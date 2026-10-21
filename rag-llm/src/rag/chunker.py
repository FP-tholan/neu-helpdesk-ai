import uuid
from typing import List

from src.rag.loader import Document


class BaseChunker:
    def chunk(self, documents: List[Document]) -> List[Document]:
        raise NotImplementedError


class ParagraphChunker(BaseChunker):
    """Chunk theo `## ` heading. Fallback char-split nếu đoạn quá dài."""

    def __init__(self, max_chunk_size: int = 800, overlap: int = 100):
        if max_chunk_size <= 0:
            raise ValueError("max_chunk_size must be > 0")
        if not (0 <= overlap < max_chunk_size):
            raise ValueError("overlap must be in [0, max_chunk_size)")
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk(self, documents: List[Document]) -> List[Document]:
        out: List[Document] = []
        for doc in documents:
            sections = self._split_sections(doc.content)
            for sec in sections:
                if not sec.strip():
                    continue
                if len(sec) <= self.max_chunk_size:
                    self._emit(out, doc, sec.strip())
                else:
                    self._char_split(out, doc, sec.strip())
        return out

    @staticmethod
    def _split_sections(text: str) -> list[str]:
        """Split theo heading `## `, giữ heading với nội dung."""
        blocks: list[str] = []
        current: list[str] = []
        for line in text.splitlines():
            if line.startswith("## ") and current:
                blocks.append("\n".join(current).strip())
                current = [line]
            else:
                current.append(line)
        if current:
            blocks.append("\n".join(current).strip())
        return blocks

    def _emit(self, out: List[Document], src: Document, text: str) -> None:
        meta = dict(src.metadata)
        meta["chunk_id"] = f"{meta.get('document_id', 'doc')}_{uuid.uuid4().hex[:8]}"
        out.append(Document(content=text, metadata=meta))

    def _char_split(self, out: List[Document], src: Document, text: str) -> None:
        start = 0
        while start < len(text):
            end = start + self.max_chunk_size
            self._emit(out, src, text[start:end])
            start += self.max_chunk_size - self.overlap