import logging
import re

from src import llm
from src.config import settings
from src.schemas import MemoryRequest, Query, RouteDecision
from src.router.prompt import ROUTER_SYSTEM
from src.tools.memory import memory as mem_store

logger = logging.getLogger(__name__)

_VALID_ROUTES = {"agent", "rag", "ood"}

# ─── Regex patterns ───

_LOCATION_RE = re.compile(
    r"(phòng\s+\w+"
    r"|tòa(?:\s+nhà)?\s+\w+"
    r"|tầng\s+\d+"
    r"|\b[A-Z]\d+(?:[.\s]\d+)?\b"
    r"|\b[A-Z]\.\d+\b)",
    re.IGNORECASE,
)

_ISSUE_RE = re.compile(
    r"(hỏng|hư|bị lỗi|không (?:lên|hoạt động|chạy|kết nối|mở|mát|nhận|chạy)"
    r"|chập chờn|treo|đơ|rè|ồn|yếu|ngắt kết nối|báo lỗi)",
    re.IGNORECASE,
)

_HOWTO_RE = re.compile(
    r"(làm sao|làm thế nào|cách nào|cách tự|hướng dẫn|quy trình|chính sách"
    r"|bao lâu|thế nào|tự xử lý|tự khắc phục|khởi động lại|restart|reset|thay pin)",
    re.IGNORECASE,
)

_SEVERE_RE = re.compile(
    r"(cháy|khét|khói|ngập|điện giật|nổ|bốc lửa|sập|rò điện)",
    re.IGNORECASE,
)

_EXPLICIT_TICKET_RE = re.compile(
    r"(tạo ticket|tạo phiếu|báo cáo (?:sự cố|lỗi)|gửi yêu cầu|tôi muốn báo)",
    re.IGNORECASE,
)

_MEMORY_RECALL_RE = re.compile(
    r"(tôi (?:mới|vừa) hỏi gì"
    r"|tôi (?:đã )?hỏi gì"
    r"|vừa nói gì"
    r"|câu (?:trước|vừa rồi|nãy) (?:là gì|nói gì)"
    r"|nhớ (?:không|lại)"
    r"|lúc nãy tôi nói gì"
    r"|ở trên (?:tôi |đã )?nói gì"
    r"|nội dung (?:câu )?trước)",
    re.IGNORECASE,
)

_OOD_KEYWORDS = re.compile(
    r"(thời tiết|bóng đá|tin tức|chứng khoán|python|javascript"
    r"|viết code|lập trình|dịch (?:bài|đoạn)|toán cao cấp|đố vui)",
    re.IGNORECASE,
)


def _looks_like_followup(text: str, session_id: str) -> bool:
    """Follow-up = message ngắn + có location + memory vừa hỏi phòng nào."""
    if len(text.split()) > 10:
        return False
    if not _LOCATION_RE.search(text):
        return False
    try:
        mem = mem_store.read(MemoryRequest(
            query=text, session_id=session_id, top_k=5,
        ))
        for m in mem.memories:
            content_lower = m.content.lower()
            if (
                "phòng nào" in content_lower
                or "vị trí nào" in content_lower
                or "ở đâu" in content_lower
                or "phòng gì" in content_lower
            ):
                return True
    except Exception:
        pass
    return False


def _heuristic_route(text: str) -> RouteDecision:
    # 1. OOD
    if _OOD_KEYWORDS.search(text):
        return RouteDecision(route="ood", confidence=0.9, reason="Heuristic: ngoài phạm vi")

    # 2. Memory recall → agent (để đọc memory)
    if _MEMORY_RECALL_RE.search(text):
        return RouteDecision(
            route="agent", confidence=0.95,
            reason="Heuristic: hỏi lại hội thoại",
        )

    # 3. Sự cố nghiêm trọng → agent
    if _SEVERE_RE.search(text):
        return RouteDecision(
            route="agent", confidence=0.95,
            reason="Heuristic: sự cố nghiêm trọng",
        )

    # 4. Explicit ticket request → agent
    if _EXPLICIT_TICKET_RE.search(text):
        return RouteDecision(
            route="agent", confidence=0.95,
            reason="Heuristic: user yêu cầu tạo ticket",
        )

    has_location = bool(_LOCATION_RE.search(text))
    has_issue = bool(_ISSUE_RE.search(text))

    # 5. Vị trí + sự cố → agent
    if has_location and has_issue:
        return RouteDecision(
            route="agent", confidence=0.9,
            reason="Heuristic: báo sự cố tại vị trí cụ thể",
        )

    # 6. Hỏi how-to không có vị trí → rag
    if _HOWTO_RE.search(text) and not has_location:
        return RouteDecision(
            route="rag", confidence=0.85,
            reason="Heuristic: hỏi cách xử lý",
        )

    # 7. Có issue không location → agent (sẽ hỏi lại)
    if has_issue:
        return RouteDecision(
            route="agent", confidence=0.8,
            reason="Heuristic: có từ chỉ sự cố, cần làm rõ vị trí",
        )

    # 8. Fallback
    return RouteDecision(route="rag", confidence=0.6, reason="Heuristic: fallback rag")


def route(query: Query, request_id: str = "-") -> RouteDecision:
    # ── Fast-path: memory recall / follow-up (không cần LLM) ──
    if _MEMORY_RECALL_RE.search(query.query):
        return RouteDecision(
            route="agent", confidence=0.95,
            reason="Fast-path: user hỏi lại hội thoại",
        )

    if _looks_like_followup(query.query, query.session_id):
        return RouteDecision(
            route="agent", confidence=0.95,
            reason="Fast-path: user trả lời câu hỏi clarification",
        )

    try:
        result = llm.chat_json(
            [
                {"role": "system", "content": ROUTER_SYSTEM},
                {"role": "user", "content": query.query},
            ],
            temperature=0.0,
            request_id=request_id,
        )
        raw_route = str(result.get("route", "")).lower().strip()
        if raw_route not in _VALID_ROUTES:
            raise ValueError(f"Invalid route from LLM: {raw_route}")

        try:
            confidence = float(result.get("confidence", 0.5))
        except (TypeError, ValueError):
            confidence = 0.5

        # Double-check: LLM nói rag nhưng heuristic nói agent confidence cao → ưu tiên agent
        if raw_route == "rag":
            heuristic = _heuristic_route(query.query)
            if heuristic.route == "agent" and heuristic.confidence >= 0.85:
                logger.info(
                    "Router override rag→agent [%s]: %s",
                    request_id, heuristic.reason,
                )
                return RouteDecision(
                    route="agent",
                    confidence=heuristic.confidence,
                    reason=f"Override: {heuristic.reason}",
                )

        return RouteDecision(
            route=raw_route,  # type: ignore
            confidence=max(0.0, min(1.0, confidence)),
            reason=result.get("reason"),
        )
    except Exception as e:
        logger.warning("Router LLM failed (%s), fallback heuristic", e)
        return _heuristic_route(query.query)