import logging
from typing import Any

from src.config import settings
from src.rag.vector_store import BaseVectorStore
from src.schemas import Document, RetrievalRequest, RetrievalResult

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self, store: BaseVectorStore):
        self.store = store

    def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        try:
            raw = self.store.search(request.query, top_k=request.top_k)
            docs = [
                Document(
                    id=r["id"],
                    content=r["content"],
                    metadata={**r.get("metadata", {}), "score": r.get("score", 0.0)},
                )
                for r in raw
            ]
            return RetrievalResult(
                documents=docs,
                metadata={"count": len(docs), "retriever": type(self.store).__name__},
            )
        except Exception as e:
            logger.exception("Retriever error")
            return RetrievalResult(
                documents=[],
                metadata={"error": str(e), "count": 0},
            )