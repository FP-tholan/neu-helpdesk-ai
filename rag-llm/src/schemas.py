"""
Pydantic schemas khớp CHÍNH XÁC docs/04-schema-contract.md.
Bất kỳ field mới → phải có [CONTRACT] tag trước khi merge.
"""
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, field_validator


# ═══════════════════════════════════════════════════════════
# COMMON
# ═══════════════════════════════════════════════════════════

class Query(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    session_id: str = Field(..., min_length=1)
    user_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RouteDecision(BaseModel):
    route: Literal["agent", "rag", "ood"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: Optional[str] = None


# ═══════════════════════════════════════════════════════════
# RETRIEVER
# ═══════════════════════════════════════════════════════════

class RetrievalRequest(BaseModel):
    query: str
    top_k: int = Field(5, ge=1, le=50)


class Document(BaseModel):
    id: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalResult(BaseModel):
    documents: list[Document] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════
# RERANKER
# ═══════════════════════════════════════════════════════════

class RerankRequest(BaseModel):
    query: str
    documents: list[Document]
    top_k: int = Field(3, ge=1, le=20)


class RankedDocument(BaseModel):
    document: Document
    score: float = Field(..., ge=0.0, le=1.0)
    rank: int = Field(..., ge=1)


class RerankResult(BaseModel):
    documents: list[RankedDocument] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# MEMORY
# ═══════════════════════════════════════════════════════════

class MemoryRequest(BaseModel):
    query: str
    session_id: str
    top_k: int = Field(5, ge=1, le=50)


class Memory(BaseModel):
    id: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryResult(BaseModel):
    memories: list[Memory] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════
# RESPONSE
# ═══════════════════════════════════════════════════════════

class Source(BaseModel):
    document_id: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class Response(BaseModel):
    answer: str
    sources: list[Source] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)