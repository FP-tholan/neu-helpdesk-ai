from src.agent.schemas import ToolResult, ToolStatus
from src.agent.tools import Tool
from src.rag.retriever import Retriever
from src.schemas import RetrievalRequest


def build_retriever_tool(retriever: Retriever) -> Tool:
    def _run(args: dict) -> ToolResult:
        try:
            res = retriever.retrieve(
                RetrievalRequest(
                    query=args["query"],
                    top_k=args.get("top_k", 5),
                )
            )
            if not res.documents:
                return ToolResult(
                    status=ToolStatus.NO_RESULT,
                    error="Không tìm thấy tài liệu phù hợp.",
                )
            return ToolResult(
                status=ToolStatus.SUCCESS,
                data={
                    "documents": [d.model_dump() for d in res.documents],
                    "metadata": res.metadata,
                },
            )
        except Exception as e:
            return ToolResult(status=ToolStatus.ERROR, error=str(e))

    return Tool(
        name="knowledge_retriever",
        description=(
            "Tra cứu tài liệu cơ sở vật chất (FAQ, hướng dẫn, chính sách). "
            "Gọi khi cần thông tin thực tế."
        ),
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Câu hỏi cần tra cứu.",
                    "minLength": 1,
                    "maxLength": 500,
                },
                "top_k": {
                    "type": "integer",
                    "description": "Số tài liệu cần lấy.",
                    "minimum": 1,
                    "maximum": 20,
                    "default": 5,
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        func=_run,
    )