"""
Reranker dùng LLM: cho điểm relevance từng doc, sort lại.
Fallback: nếu LLM fail → giữ nguyên thứ tự retriever.
"""
import logging

from src import llm
from src.schemas import Document, RankedDocument, RerankRequest, RerankResult

logger = logging.getLogger(__name__)

_SYSTEM = """Bạn là Reranker. Cho điểm mức độ liên quan của từng tài liệu với câu hỏi.
CHỈ trả về JSON:
{"ranking": [{"index": <int>, "score": <0.0-1.0>}, ...]}
- index là vị trí tài liệu trong danh sách (bắt đầu 0).
- score từ 0 (không liên quan) đến 1 (rất liên quan).
- Trả về TẤT CẢ tài liệu, sắp xếp theo score giảm dần."""


class LLMReranker:
    def rerank(self, request: RerankRequest, request_id: str = "-") -> RerankResult:
        docs = request.documents
        if not docs:
            return RerankResult(documents=[])

        doc_block = "\n\n".join(
            f"[{i}] {d.content[:500]}" for i, d in enumerate(docs)
        )
        user_msg = (
            f"Câu hỏi: {request.query}\n\n"
            f"Tài liệu:\n{doc_block}\n\n"
            f"Trả về JSON ranking cho {len(docs)} tài liệu."
        )

        try:
            result = llm.chat_json(
                [
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.0,
                request_id=request_id,
            )
            ranking = result.get("ranking", [])
            if not isinstance(ranking, list):
                raise ValueError("Invalid ranking format")

            ranked: list[RankedDocument] = []
            for item in ranking[: request.top_k]:
                idx = item.get("index")
                if not isinstance(idx, int) or idx < 0 or idx >= len(docs):
                    continue
                try:
                    score = float(item.get("score", 0.5))
                except (TypeError, ValueError):
                    score = 0.5
                ranked.append(RankedDocument(
                    document=docs[idx],
                    score=max(0.0, min(1.0, score)),
                    rank=len(ranked) + 1,
                ))

            if not ranked:
                raise ValueError("Empty ranking")

            return RerankResult(documents=ranked)

        except Exception as e:
            logger.warning("Reranker LLM failed (%s), fallback to retriever order", e)
            return RerankResult(documents=[
                RankedDocument(
                    document=d,
                    score=1.0 - i * 0.05,
                    rank=i + 1,
                )
                for i, d in enumerate(docs[: request.top_k])
            ])