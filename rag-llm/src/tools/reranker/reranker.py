from src.agent.schemas import ToolResult, ToolStatus
from src.agent.tools import Tool
from src.rag.reranker import LLMReranker
from src.schemas import Document, RerankRequest


def build_reranker_tool(reranker: LLMReranker) -> Tool:
    def _run(args: dict) -> ToolResult:
        try:
            docs_raw = args.get("documents", [])
            docs = [Document(**d) for d in docs_raw]
            res = reranker.rerank(RerankRequest(
                query=args["query"],
                documents=docs,
                top_k=args.get("top_k", 3),
            ))
            return ToolResult(
                status=ToolStatus.SUCCESS,
                data={"documents": [r.model_dump() for r in res.documents]},
            )
        except Exception as e:
            return ToolResult(status=ToolStatus.ERROR, error=str(e))

    return Tool(
        name="reranker",
        description="Xếp hạng lại danh sách tài liệu theo độ liên quan.",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "minLength": 1},
                "documents": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "content": {"type": "string"},
                            "metadata": {"type": "object"},
                        },
                        "required": ["id", "content"],
                    },
                },
                "top_k": {"type": "integer", "minimum": 1, "maximum": 20, "default": 3},
            },
            "required": ["query", "documents"],
        },
        func=_run,
    )