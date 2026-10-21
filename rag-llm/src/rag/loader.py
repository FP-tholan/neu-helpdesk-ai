import hashlib
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from src.config import settings


@dataclass
class Document:
    content: str
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if "document_id" not in self.metadata:
            self.metadata["document_id"] = str(uuid.uuid4())
        if "content_hash" not in self.metadata:
            self.metadata["content_hash"] = hashlib.sha256(
                self.content.encode("utf-8")
            ).hexdigest()


class BaseLoader:
    def load(self, file_path: str, extra_metadata: dict | None = None) -> list[Document]:
        raise NotImplementedError


class MarkdownLoader(BaseLoader):
    def load(self, file_path: str, extra_metadata: dict | None = None) -> list[Document]:
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(file_path)

        content = p.read_text(encoding="utf-8").strip()
        if not content:
            return []

        meta = {
            "source": p.name,
            "extension": p.suffix,
            "ingested_at": datetime.utcnow().isoformat(),
        }
        if extra_metadata:
            meta.update(extra_metadata)

        return [Document(content=content, metadata=meta)]


class KnowledgeBaseLoader:
    """Load toàn bộ KB từ thư mục."""

    def __init__(self, kb_dir: Path | None = None):
        self.kb_dir = kb_dir or settings.kb_path

    def load_all(self) -> list[Document]:
        docs: list[Document] = []
        if not self.kb_dir.exists():
            return docs
        loader = MarkdownLoader()
        for f in sorted(self.kb_dir.glob("*.md")):
            try:
                docs.extend(loader.load(str(f)))
            except Exception:
                continue
        return docs