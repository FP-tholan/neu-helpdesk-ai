import logging
from pathlib import Path

from src.config import settings
from src.rag.chunker import BaseChunker, ParagraphChunker
from src.rag.generator import generate
from src.rag.loader import Document, KnowledgeBaseLoader
from src.rag.reranker import LLMReranker
from src.rag.retriever import Retriever
from src.rag.vector_store import BaseVectorStore, BM25Store
from src.schemas import (
    Query,
    RerankRequest,
    Response,
    RetrievalRequest,
    Source,
)

logger = logging.getLogger(__name__)


class RAGPipeline:
    def __init__(
        self,
        store: BaseVectorStore | None = None,
        chunker: BaseChunker | None = None,
        reranker: LLMReranker | None = None,
    ):
        self.store = store or BM25Store()
        self.chunker = chunker or ParagraphChunker()
        self.reranker = reranker or LLMReranker()
        self.retriever = Retriever(self.store)

    def ingest_dir(self, kb_dir: Path | None = None) -> dict:
        loader = KnowledgeBaseLoader(kb_dir)
        docs = loader.load_all()
        if not docs:
            return {"status": "EMPTY", "count": 0}
        chunks = self.chunker.chunk(docs)
        self.store.add(chunks)
        logger.info("Ingested %s chunks (total %s)", len(chunks), self.store.count())
        return {"status": "SUCCESS", "chunks": len(chunks), "total": self.store.count()}

    def query(self, query: Query, request_id: str = "-") -> Response:
        # 1. Retrieve
        retrieval = self.retriever.retrieve(
            RetrievalRequest(query=query.query, top_k=settings.retrieval_top_k)
        )

        if not retrieval.documents:
            return Response(
                answer=(
                    "Tôi chưa có thông tin cho vấn đề này trong cơ sở tri thức. "
                    "Bạn có thể tạo ticket để kỹ thuật viên hỗ trợ."
                ),
                sources=[],
                metadata={"route": "rag", "reason": "empty_kb"},
            )

        # 2. Rerank
        reranked = self.reranker.rerank(
            RerankRequest(
                query=query.query,
                documents=retrieval.documents,
                top_k=settings.rerank_top_k,
            ),
            request_id=request_id,
        )
        top_docs = [r.document for r in reranked.documents] or retrieval.documents[:settings.rerank_top_k]

        # 3. Generate
        gen = generate(query.query, top_docs, request_id=request_id)

        sources = [
            Source(
                document_id=d.id,
                content=d.content[:300],
                metadata={
                    "source": d.metadata.get("source", ""),
                    "score": d.metadata.get("score", 0.0),
                },
            )
            for d in top_docs
        ]

        return Response(
            answer=gen["answer"],
            sources=sources,
            metadata={
                "route": "rag",
                "num_sources": len(sources),
                "num_candidates": len(retrieval.documents),
                "status": gen.get("status", "SUCCESS"),
            },
        )