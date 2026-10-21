"""
Wrapper tập trung cho Ollama:
  - Retry exponential backoff cho lỗi network (không retry logic)
  - JSON mode
  - Timeout + request_id propagation
  - Circuit breaker đơn giản (cooldown khi fail liên tục)
"""
import json
import logging
import time
from typing import Any, Optional

import ollama
from httpx import ConnectError, ReadTimeout

from src.config import settings

logger = logging.getLogger(__name__)

_client = ollama.Client(host=settings.ollama_host, timeout=settings.ollama_timeout)

# ─── Circuit breaker (đơn giản) ───
_consecutive_failures = 0
_circuit_open_until = 0.0
_CIRCUIT_THRESHOLD = 5
_CIRCUIT_COOLDOWN = 30  # giây


class LLMError(Exception):
    pass


def _circuit_check() -> None:
    global _circuit_open_until
    if time.time() < _circuit_open_until:
        raise LLMError(f"Circuit open, retry after {_circuit_open_until - time.time():.1f}s")


def _record_failure() -> None:
    global _consecutive_failures, _circuit_open_until
    _consecutive_failures += 1
    if _consecutive_failures >= _CIRCUIT_THRESHOLD:
        _circuit_open_until = time.time() + _CIRCUIT_COOLDOWN
        logger.warning("Circuit breaker OPEN for %ss", _CIRCUIT_COOLDOWN)


def _record_success() -> None:
    global _consecutive_failures
    _consecutive_failures = 0


def _parse_json_safely(raw: str) -> dict[str, Any]:
    """Parse JSON từ output LLM, chịu được code fence ```json ... ```."""
    raw = raw.strip()
    if raw.startswith("```"):
        # bỏ code fence
        lines = raw.splitlines()
        raw = "\n".join(line for line in lines if not line.strip().startswith("```"))
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    # Thử tìm JSON object đầu tiên
    start, end = raw.find("{"), raw.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(raw[start : end + 1])
        except json.JSONDecodeError:
            pass
    return {}


def chat(
    messages: list[dict[str, Any]],
    *,
    json_mode: bool = False,
    temperature: float = 0.1,
    tools: Optional[list[dict]] = None,
    request_id: str = "-",
) -> dict[str, Any]:
    """
    Gọi Ollama với retry. Raise LLMError nếu exhaust.
    """
    _circuit_check()

    last_exc: Optional[Exception] = None
    for attempt in range(1, settings.ollama_max_retries + 1):
        try:
            kwargs: dict[str, Any] = {
                "model": settings.ollama_model,
                "messages": messages,
                "options": {"temperature": temperature},
            }
            if json_mode:
                kwargs["format"] = "json"
            if tools:
                kwargs["tools"] = tools

            resp = _client.chat(**kwargs)
            _record_success()
            return resp
        except (ReadTimeout, ConnectError) as e:
            last_exc = e
            logger.warning(
                "LLM network error (attempt %s/%s) [%s]: %s",
                attempt, settings.ollama_max_retries, request_id, e,
            )
            if attempt < settings.ollama_max_retries:
                time.sleep(2 ** (attempt - 1))
        except Exception as e:
            # Lỗi logic (VD prompt sai) → không retry
            _record_failure()
            logger.error("LLM non-retryable error [%s]: %s", request_id, e)
            raise LLMError(str(e)) from e

    _record_failure()
    raise LLMError(f"LLM exhausted retries: {last_exc}")


def chat_json(
    messages: list[dict[str, Any]],
    *,
    temperature: float = 0.0,
    request_id: str = "-",
) -> dict[str, Any]:
    resp = chat(messages, json_mode=True, temperature=temperature, request_id=request_id)
    raw = resp.get("message", {}).get("content", "")
    return _parse_json_safely(raw)


def chat_text(
    messages: list[dict[str, Any]],
    *,
    temperature: float = 0.1,
    request_id: str = "-",
) -> str:
    resp = chat(messages, temperature=temperature, request_id=request_id)
    return (resp.get("message", {}).get("content") or "").strip()


def chat_with_tools(
    messages: list[dict[str, Any]],
    tools: list[dict],
    *,
    temperature: float = 0.1,
    request_id: str = "-",
) -> dict[str, Any]:
    return chat(
        messages,
        tools=tools,
        temperature=temperature,
        request_id=request_id,
    )


def health_check() -> dict[str, Any]:
    """Dùng cho /health endpoint."""
    try:
        _client.list()
        return {"ok": True, "model": settings.ollama_model}
    except Exception as e:
        return {"ok": False, "error": str(e)}