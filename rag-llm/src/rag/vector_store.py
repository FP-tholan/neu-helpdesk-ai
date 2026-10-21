"""
BM25Store — mặc định, không cần GPU, deterministic.
FaissStore — optional, cho semantic retrieval (nếu Ollama embedder có sẵn).
"""
import json
import logging
import os
import pickle
import re
import shutil
from pathlib import Path
from typing import Any

from rank_bm25 import BM25Okapi

from src.rag.loader import Document

logger = logging.getLogger(__name__)

_WORD_RE = re.compile(r"\w+", re.UNICODE)

# ─── Synonym map tiếng Việt: expand query tokens để bắt trúng KB ───
_SYNONYMS: dict[str, list[str]] = {
    "khởi động lại": ["restart", "reset", "tắt bật lại", "tắt mở lại", "khởi động"],
    "restart": ["khởi động lại", "tắt bật lại"],
    "reset": ["khởi động lại"],
    "hỏng": ["hư", "lỗi", "sự cố", "không hoạt động", "không lên", "không chạy"],
    "hư": ["hỏng", "lỗi"],
    "lỗi": ["hỏng", "hư", "sự cố"],
    "máy chiếu": ["projector", "máy trình chiếu", "máy chiếu phim"],
    "projector": ["máy chiếu"],
    "máy tính": ["computer", "laptop", "pc", "máy vi tính"],
    "computer": ["máy tính"],
    "điều hòa": ["điều hoà", "máy lạnh", "air conditioner"],
    "điều hoà": ["điều hòa", "máy lạnh"],
    "máy lạnh": ["điều hòa", "điều hoà"],
    "wifi": ["wi-fi", "wlan", "mạng không dây"],
    "wi-fi": ["wifi"],
    "mạng": ["internet", "wifi", "lan"],
    "micro": ["microphone", "mic"],
    "microphone": ["micro"],
    "âm thanh": ["loa", "speaker", "sound"],
    "pin": ["ắc quy", "battery", "pin dự phòng"],
    "cáp": ["dây", "cable"],
    "nguồn": ["điện", "power", "nguồn điện"],
    "màn hình": ["screen", "display"],
    "bàn phím": ["keyboard"],
    "chuột": ["mouse"],
}

# ─── Heading keywords boost: match category chắc chắn ───
_HEADING_BOOSTS = [
    (["máy chiếu", "projector", "trình chiếu"], ["máy chiếu", "projector"], 2.5),
    (["điều hòa", "điều hoà", "máy lạnh", "điện lạnh"], ["điều hòa", "điều hoà", "điện lạnh"], 2.5),
    (["máy tính", "computer", "laptop", "pc"], ["máy tính", "computer"], 2.5),
    (["wifi", "wi-fi", "mạng", "internet", "lan"], ["wifi", "mạng"], 2.5),
    (["micro", "âm thanh", "loa", "speaker"], ["micro", "âm thanh"], 2.5),
    (["điện", "nước", "ổ cắm", "vòi"], ["điện", "nước"], 2.0),
    (["bàn", "ghế", "tủ", "kệ"], ["bàn", "ghế", "nội thất"], 1.5),
    (["vệ sinh", "rác", "bẩn"], ["vệ sinh", "làm sạch"], 1.5),
]


def _tokenize(text: str) -> list[str]:
    return _WORD_RE.findall(text.lower())


def _tokenize_with_synonyms(text: str) -> list[str]:
    """Tokenize + inject synonyms để BM25 match tốt hơn."""
    base_tokens = _tokenize(text)
    text_lower = text.lower()

    extra: list[str] = []
    for phrase, syns in _SYNONYMS.items():
        if phrase in text_lower:
            for syn in syns:
                extra.extend(_tokenize(syn))

    return base_tokens + extra


def _heading_boost(query_lower: str, doc_content: str) -> float:
    """Boost score nếu heading của chunk khớp category query."""
    first_line = doc_content.split("\n", 1)[0].lower()
    for query_kws, heading_kws, boost in _HEADING_BOOSTS:
        if any(kw in query_lower for kw in query_kws):
            if any(kw in first_line for kw in heading_kws):
                return boost
    return 0.0


class BaseVectorStore:
    def add(self, documents: list[Document]) -> None: ...
    def search(self, query: str, top_k: int) -> list[dict[str, Any]]: ...
    def count(self) -> int: ...
    def is_hash_processed(self, h: str) -> bool: ...


class BM25Store(BaseVectorStore):
    def __init__(self):
        self.docs: list[Document] = []
        self.bm25: BM25Okapi | None = None
        self.hashes: set[str] = set()

    def add(self, documents: list[Document]) -> None:
        new = [d for d in documents if d.metadata.get("content_hash") not in self.hashes]
        if not new:
            return
        self.docs.extend(new)
        for d in new:
            h = d.metadata.get("content_hash")
            if h:
                self.hashes.add(h)
        self.bm25 = BM25Okapi([_tokenize(d.content) for d in self.docs])

    def search(self, query: str, top_k: int) -> list[dict[str, Any]]:
        if not self.bm25 or not self.docs:
            return []

        # 1. Tokenize với synonym expansion
        tokens = _tokenize_with_synonyms(query)
        scores = self.bm25.get_scores(tokens)

        # 2. Heading boost
        query_lower = query.lower()
        for i, doc in enumerate(self.docs):
            boost = _heading_boost(query_lower, doc.content)
            if boost > 0:
                scores[i] += boost

        # 3. Sort & filter
        ranked = sorted(zip(self.docs, scores), key=lambda x: x[1], reverse=True)[:top_k]
        return [
            {
                "id": d.metadata.get("chunk_id", ""),
                "content": d.content,
                "metadata": d.metadata,
                "score": float(s),
            }
            for d, s in ranked
            if s > 0
        ]

    def count(self) -> int:
        return len(self.docs)

    def is_hash_processed(self, h: str) -> bool:
        return h in self.hashes