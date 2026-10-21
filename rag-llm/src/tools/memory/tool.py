from src.agent.schemas import ToolResult, ToolStatus
from src.agent.tools import Tool
from src.schemas import MemoryRequest
from src.tools.memory import memory as mem_store


def build_memory_tool(default_session_id: str = "") -> Tool:
    def _run(args: dict) -> ToolResult:
        try:
            sid = args.get("session_id") or default_session_id
            if not sid:
                return ToolResult(status=ToolStatus.ERROR, error="Missing session_id")
            res = mem_store.read(MemoryRequest(
                query=args.get("query", ""),
                session_id=sid,
                top_k=args.get("top_k", 5),
            ))
            if not res.memories:
                return ToolResult(status=ToolStatus.NO_RESULT)
            return ToolResult(
                status=ToolStatus.SUCCESS,
                data={"memories": [m.model_dump() for m in res.memories]},
            )
        except Exception as e:
            return ToolResult(status=ToolStatus.ERROR, error=str(e))

    return Tool(
        name="memory_reader",
        description="Đọc lịch sử hội thoại của phiên hiện tại (chỉ đọc).",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "default": ""},
                "session_id": {"type": "string"},
                "top_k": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
            },
            "required": [],
        },
        func=_run,
    )