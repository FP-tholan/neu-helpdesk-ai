"""
AgentExecutor:
  - max_iterations
  - request deadline
  - duplicate tool-call detection
  - collect sources từ tool results
  - deterministic metadata extraction + post-process answer
  - recover category from memory for follow-up turns
  - strip prompt leakage from Qwen output
"""
import json
import logging
import re
import time
import uuid
from typing import Any, Optional

from src.agent.agent import NativeAgent
from src.agent.prompt import AGENT_SYSTEM_PROMPT
from src.agent.schemas import AgentState, ToolStatus

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════

_CATEGORY_LABEL = {
    "PROJECTOR": "máy chiếu",
    "COMPUTER": "máy tính",
    "WIFI": "mạng/wifi",
    "MICROPHONE": "âm thanh/micro",
    "AIR_CONDITIONER": "điều hòa",
    "ELECTRICITY": "điện/nước",
    "FURNITURE": "bàn ghế",
    "CLEANING": "vệ sinh",
    "OTHER": "cơ sở vật chất",
}

_TEAM_BY_CATEGORY_FIXED = {
    "COMPUTER": "T_IT",
    "WIFI": "T_IT",
    "PROJECTOR": "T_QTTB",
    "MICROPHONE": "T_QTTB",
    "AIR_CONDITIONER": "T_QTTB",
    "ELECTRICITY": "T_PSA",
    "FURNITURE": "T_PSA",
    "CLEANING": "T_PSA",
    "OTHER": "T_ADMIN",
}

_HALLUCINATED_TEAMS = [
    r"\bHVAC\b",
    r"\bHVAC Team\b",
    r"Đội HVAC",
    r"Facility Team",
    r"Facilities Team",
    r"Maintenance Team",
    r"Operations Team",
    r"IT Support Team",
    r"Support Team",
    r"Technician Team",
    r"Đội bảo trì",
    r"Đội Facilities",
]

# Prompt leakage patterns — Qwen 3B hay copy nguyên dòng instruction từ system prompt
_LEAK_PREFIX_RE = re.compile(
    r"^(?:Điều kiện|Trả lời MẪU|KỊCH BẢN [A-Z]|Ví dụ\s*→|»|Điều kiện\s*:)"
    r"[^.]*\.\s*",
    re.MULTILINE,
)

_ROOM_PATTERNS = [
    re.compile(r"(?:phòng|room)\s+([A-Z]\d+(?:[.\s]\d+)?)", re.IGNORECASE),
    re.compile(r"\b([A-Z]\d+(?:\.\d+)?)\b", re.IGNORECASE),
    re.compile(r"\b([A-Z]\.\d+)\b", re.IGNORECASE),
]


# ═══════════════════════════════════════════════════════════
# CATEGORY DETECTION (reusable)
# ═══════════════════════════════════════════════════════════

def _detect_category(text_lower: str) -> str | None:
    """Detect category từ lowercase text."""
    if re.search(r"(máy chiếu|projector)", text_lower):
        return "PROJECTOR"
    if re.search(r"(wifi|wi-fi|mạng không dây|mất mạng|mạng\b)", text_lower):
        return "WIFI"
    if re.search(r"(máy tính|computer|laptop|phần mềm|virus)", text_lower):
        return "COMPUTER"
    if re.search(r"(micro|âm thanh|loa)", text_lower):
        return "MICROPHONE"
    if re.search(r"(điều hòa|điều hoà|máy lạnh|điện lạnh)", text_lower):
        return "AIR_CONDITIONER"
    if re.search(r"(điện|ổ cắm|bóng đèn|nước|vòi|ống nước)", text_lower):
        return "ELECTRICITY"
    if re.search(r"(bàn|ghế|tủ|kệ)", text_lower):
        return "FURNITURE"
    if re.search(r"(vệ sinh|rác|bẩn|hôi|dơ)", text_lower):
        return "CLEANING"
    if re.search(r"(hỏng|sự cố|báo cáo|không lên|không mở|bị lỗi)", text_lower):
        return "OTHER"
    return None


def _recover_category_from_memory(session_id: str) -> str | None:
    """
    Recover category từ lượt trước trong memory.

    Dùng khi user chỉ trả lời mã phòng (VD: "phòng B102")
    → category=None trong query hiện tại → phải lấy từ memory.

    Chỉ đọc phần "User:" của memory (bỏ "AI: ...") để tránh
    phụ thuộc vào answer LLM có thể đã bị post-process.
    """
    if not session_id:
        return None
    try:
        from src.schemas import MemoryRequest
        from src.tools.memory import memory as mem_store

        mem = mem_store.read(MemoryRequest(
            query="", session_id=session_id, top_k=10,
        ))

        # Mới nhất trước
        for m in reversed(mem.memories):
            content = m.content
            # Chỉ lấy phần user (bỏ "\nAI: ...")
            user_part = content.split("\nAI:")[0]
            user_part = user_part.replace("User:", "").strip().lower()

            cat = _detect_category(user_part)
            if cat:
                return cat
        return None
    except Exception as e:
        logger.warning("recover category from memory failed: %s", e)
        return None


# ═══════════════════════════════════════════════════════════
# METADATA EXTRACTION (deterministic)
# ═══════════════════════════════════════════════════════════

def _extract_ticket_metadata(
    answer: str,
    user_query: str,
    session_id: str = "",
) -> dict:
    """
    Suy ra metadata từ user_query (KHÔNG tin answer của LLM).
    Nếu category None trong query hiện tại (VD follow-up "phòng B102"),
    recover category từ memory của session.
    """
    text = user_query.lower()

    # ── Category từ query hiện tại ──
    category = _detect_category(text)

    # ── Recover category từ memory nếu chưa có ──
    if category is None and session_id:
        category = _recover_category_from_memory(session_id)

    # ── Priority ──
    priority = "MEDIUM"
    if re.search(r"(cháy|khét|khói|ngập|điện giật|nổ|bốc lửa|sập|rò điện)", text):
        priority = "CRITICAL"
    elif re.search(r"(đang học|đang thi|khẩn|gấp|ngay|trong giờ)", text):
        priority = "HIGH"
    elif re.search(r"(nhẹ|không gấp|khi nào cũng được)", text):
        priority = "LOW"

    # ── Room code ──
    room_code = None
    for pat in _ROOM_PATTERNS:
        m = pat.search(user_query)
        if m:
            code = m.group(1).upper().strip()
            code = re.sub(r"\s+", ".", code)
            room_code = code
            break

    # ── Memory recall intent ──
    is_recall = bool(re.search(
        r"(tôi (?:mới|vừa|đã) hỏi gì"
        r"|câu (?:trước|vừa rồi|nãy)"
        r"|vừa nói gì"
        r"|nhớ (?:không|lại)"
        r"|nội dung (?:câu )?trước)",
        text,
    ))

    if is_recall:
        return {
            "intent": "recall",
            "category": None,
            "priority": None,
            "room_code": None,
            "needs_clarification": False,
            "clarification_type": None,
            "recommended_action": None,
        }

    # ── Kịch bản A: có category + CHƯA có room → hỏi lại phòng ──
    if category and not room_code:
        return {
            "intent": "report_issue",
            "category": category,
            "priority": priority,
            "room_code": None,
            "needs_clarification": True,
            "clarification_type": "room",
            "recommended_action": "ask_room",
        }

    # ── Kịch bản B: có category + có room → tạo ticket ──
    if category and room_code:
        return {
            "intent": "report_issue",
            "category": category,
            "priority": priority,
            "room_code": room_code,
            "needs_clarification": False,
            "clarification_type": None,
            "recommended_action": "create_ticket",
        }

    # ── Fallback ──
    return {
        "intent": "general",
        "category": category,
        "priority": priority,
        "room_code": room_code,
        "needs_clarification": False,
        "clarification_type": None,
        "recommended_action": None,
    }


# ═══════════════════════════════════════════════════════════
# POST-PROCESS ANSWER
# ═══════════════════════════════════════════════════════════

def _resolve_team(category: str | None, room_code: str | None) -> str:
    """Trả team đúng dựa trên category + room."""
    if not category:
        return "bộ phận kỹ thuật phụ trách"

    if category in ("PROJECTOR", "MICROPHONE", "AIR_CONDITIONER"):
        rc = (room_code or "").upper()
        if rc.startswith(("A1", "A2")):
            return "T_PSA"
        if rc.startswith(("B", "C", "D")):
            return "T_QTTB"
        return _TEAM_BY_CATEGORY_FIXED[category]

    return _TEAM_BY_CATEGORY_FIXED.get(category, "bộ phận kỹ thuật phụ trách")


def _strip_prompt_leakage(answer: str) -> str:
    """Loại bỏ prefix instruction Qwen có thể echo từ system prompt."""
    prev = None
    while prev != answer:
        prev = answer
        answer = _LEAK_PREFIX_RE.sub("", answer).strip()
    return answer


def _post_process_answer(answer: str, meta: dict) -> str:
    """
    Post-process answer dựa trên metadata (deterministic).

    Thứ tự ưu tiên:
      1. Clarification template (nếu thiếu room)
      2. Create ticket template (nếu đủ info) — kể cả CRITICAL
      3. Fallback: strip prompt leakage + sanitize team name
    """
    category = meta.get("category")
    room_code = meta.get("room_code")
    needs_clarification = meta.get("needs_clarification")
    clarification_type = meta.get("clarification_type")
    priority = meta.get("priority")

    # ── 1. Clarification ──
    if needs_clarification and clarification_type == "room":
        label = _CATEGORY_LABEL.get(category, "sự cố")
        return (
            f"Tôi đã ghi nhận sự cố {label} bạn mô tả. "
            f"Bạn vui lòng cho biết sự cố xảy ra ở phòng nào ạ? "
            f"(VD: A2.101, B.102, A1.202)"
        )

    # ── 2. Create ticket template (đủ info) ──
    correct_team = _resolve_team(category, room_code)

    if category and room_code:
        label = _CATEGORY_LABEL.get(category, "sự cố")

        if priority == "CRITICAL":
            return (
                f"CẢNH BÁO: Đây là sự cố nghiêm trọng. Vui lòng gọi bảo vệ ngay "
                f"(số nội bộ 113). Đồng thời, bấm nút 'Tạo ticket' bên dưới "
                f"để đội {correct_team} xử lý khẩn cấp."
            )

        return (
            f"Tôi đã ghi nhận sự cố {label} tại phòng {room_code}. "
            f"Vui lòng bấm nút 'Tạo ticket' bên dưới để đội {correct_team} "
            f"tiếp nhận và xử lý."
        )

    # ── 3. Fallback: strip leakage + sanitize team ──
    answer = _strip_prompt_leakage(answer)

    for pattern in _HALLUCINATED_TEAMS:
        answer = re.sub(pattern, correct_team, answer, flags=re.IGNORECASE)

    if not answer or len(answer.strip()) < 10:
        # Nếu Qwen trả rỗng sau khi strip → fallback template
        return (
            "Tôi đã ghi nhận yêu cầu của bạn. "
            "Bạn vui lòng cung cấp thêm chi tiết để tôi hỗ trợ tốt hơn."
        )

    return answer


# ═══════════════════════════════════════════════════════════
# AGENT EXECUTOR
# ═══════════════════════════════════════════════════════════

class AgentExecutor:
    def __init__(self, agent: NativeAgent, max_iterations: int, timeout_sec: int):
        self.agent = agent
        self.max_iterations = max_iterations
        self.timeout_sec = timeout_sec

    def _build_messages(
        self,
        query: str,
        session_id: str,
        history: list[dict[str, str]] | None,
    ) -> list[dict[str, Any]]:
        msgs: list[dict[str, Any]] = [
            {"role": "system", "content": AGENT_SYSTEM_PROMPT}
        ]

        # Inject session memory
        try:
            from src.schemas import MemoryRequest
            from src.tools.memory import memory as mem_store

            mem = mem_store.read(MemoryRequest(
                query=query, session_id=session_id, top_k=5,
            ))
            if mem.memories:
                hist_block = ["LỊCH SỬ HỘI THOẠI (từ memory của phiên này):"]
                for m in mem.memories:
                    hist_block.append(f"---\n{m.content}")
                msgs.append({
                    "role": "system",
                    "content": "\n".join(hist_block),
                })
        except Exception as e:
            logger.warning("Memory inject failed: %s", e)

        # Caller-supplied history
        for m in history or []:
            role = m.get("role")
            if role in ("user", "assistant"):
                msgs.append({"role": role, "content": str(m.get("content", ""))})

        msgs.append({"role": "user", "content": query})
        return msgs

    def execute(
        self,
        query: str,
        session_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        history: Optional[list[dict[str, str]]] = None,
        request_id: Optional[str] = None,
    ) -> dict[str, Any]:
        req_id = request_id or str(uuid.uuid4())
        start = time.time()

        if not query or not query.strip():
            return self._err(req_id, "INVALID_QUERY")

        state = AgentState(
            user_query=query.strip(),
            request_id=req_id,
            messages=self._build_messages(query.strip(), session_id, history),
        )

        executed_signatures: set[str] = set()

        try:
            while state.iteration < self.max_iterations:
                if time.time() - start > self.timeout_sec:
                    return self._err(req_id, "TIMEOUT")

                state = self.agent.step(state)

                if state.error:
                    return self._err(req_id, "AGENT_ERROR", state.error)

                if state.final_answer:
                    # 1. Extract metadata (có session_id để recover category)
                    agent_meta = _extract_ticket_metadata(
                        state.final_answer,
                        state.user_query,
                        session_id=session_id,
                    )

                    # 2. Override answer
                    final_answer = _post_process_answer(
                        state.final_answer, agent_meta
                    )

                    # 3. Dedupe sources
                    seen = set()
                    unique_sources = []
                    for s in state.sources:
                        doc_id = s.get("document_id", "")
                        if doc_id and doc_id not in seen:
                            seen.add(doc_id)
                            unique_sources.append(s)
                    state.sources = unique_sources

                    return {
                        "answer": final_answer,
                        "sources": state.sources,
                        "metadata": {
                            "status": "SUCCESS",
                            "route": "agent",
                            "iterations": state.iteration + 1,
                            "latency_ms": int((time.time() - start) * 1000),
                            "session_id": session_id,
                            "user_id": user_id,
                            **agent_meta,
                        },
                    }

                # Execute tool calls
                last = state.messages[-1]
                tool_calls = last.get("tool_calls") or []
                for call in tool_calls:
                    call_id = call.get("id") or f"call_{uuid.uuid4().hex[:8]}"
                    func = call.get("function", {})
                    name = func.get("name", "")
                    args = func.get("arguments", {})
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except Exception:
                            args = {}

                    sig = f"{name}_{json.dumps(args, sort_keys=True, ensure_ascii=False)}"
                    if sig in executed_signatures:
                        result_content = json.dumps(
                            {"status": "ERROR", "error": "Duplicate tool call."},
                            ensure_ascii=False,
                        )
                    else:
                        res = self.agent.registry.execute(name, args)
                        executed_signatures.add(sig)

                        if res.status == ToolStatus.SUCCESS:
                            result_content = json.dumps(res.data, ensure_ascii=False)
                            docs = (res.data or {}).get("documents", [])
                            for d in docs:
                                state.sources.append({
                                    "document_id": d.get("id", ""),
                                    "content": d.get("content", ""),
                                    "metadata": d.get("metadata", {}),
                                })
                        else:
                            result_content = json.dumps({
                                "status": res.status.value,
                                "error": res.error or "Unknown",
                            }, ensure_ascii=False)

                    state.messages.append({
                        "role": "tool",
                        "name": name,
                        "content": result_content,
                        "tool_call_id": call_id,
                    })

                state.iteration += 1

            return self._err(req_id, "MAX_ITERATIONS")

        except Exception as e:
            logger.exception("Executor crash [%s]", req_id)
            return self._err(req_id, "INTERNAL_ERROR", str(e))

    @staticmethod
    def _err(req_id: str, code: str, detail: str = "") -> dict[str, Any]:
        return {
            "answer": "Xin lỗi, hệ thống đang gặp sự cố. Vui lòng thử lại sau ít phút.",
            "sources": [],
            "metadata": {
                "status": "ERROR",
                "route": "agent",
                "error_code": code,
                "error_detail": detail,
                "request_id": req_id,
            },
        }