# Module Communication Schema

**Owner:** [ALL]
**Criticality:** ⭐ HIGH
**Version:** `v0`

> Đây là contract bắt buộc giữa các module AI.

Team RAG-LLM phải **stick chính xác schema này**.

---

# 1. Common Types

## Query

```text
Query
├── query: string
├── session_id: string
├── user_id: string | null
└── metadata: object
```

### Example

```json
{
  "query": "Máy chiếu phòng B203 không hoạt động.",
  "session_id": "session_001",
  "user_id": "U001",
  "metadata": {
    "source": "chatbot",
    "room_id": "R002",
    "room_code": "B203",
    "building_id": "B002",
    "user_role": "student"
  }
}
```

`metadata` là nơi chứa context đặc thù của NEU.

Không thêm field trực tiếp vào `Query`.

---

# 2. Router

## Input

```text
Query
```

## Output

```text
RouteDecision
├── route: "agent" | "rag" | "ood"
├── confidence: float
└── reason: string | null
```

Example:

```json
{
  "route": "rag",
  "confidence": 0.91,
  "reason": "Query có thể được trả lời từ knowledge base"
}
```

---

# 3. Agent

## Input

```text
Query
```

Agent có thể gọi:

```text
Retriever
Reranker
Memory
```

---

# 4. Retriever

## Input

```text
RetrievalRequest
├── query: string
└── top_k: integer
```

## Output

```text
RetrievalResult
├── documents: Document[]
└── metadata: object
```

### Document

```text
Document
├── id: string
├── content: string
└── metadata: object
```

### Requirement

Retriever:

```text
Query + top_k
      ↓
Candidate Documents
```

Retriever **không rerank**.

---

# 5. Reranker

## Input

```text
RerankRequest
├── query: string
├── documents: Document[]
└── top_k: integer
```

## Output

```text
RerankResult
└── documents: RankedDocument[]
```

### RankedDocument

```text
RankedDocument
├── document: Document
├── score: float
└── rank: integer
```

### Requirement

Reranker:

```text
Query + Candidate Documents
            ↓
      Ranked Documents
```

Reranker **không retrieval**.

---

# 6. Memory

## Input

```text
MemoryRequest
├── query: string
├── session_id: string
└── top_k: integer
```

## Output

```text
MemoryResult
├── memories: Memory[]
└── metadata: object
```

### Memory

```text
Memory
├── id: string
├── content: string
└── metadata: object
```

Agent chỉ có:

```text
Query → Read Memory
```

Agent không:

```text
Agent → Write Memory
```

---

# 7. RAG

## Input

```text
Query
```

RAG có thể gọi:

```text
Retriever
Reranker
```

## Output

```text
Response
├── answer: string
├── sources: Source[]
└── metadata: object
```

---

# 8. Agent Output

```text
Response
├── answer: string
├── sources: Source[]
└── metadata: object
```

---

# 9. Source

```text
Source
├── document_id: string
├── content: string
└── metadata: object
```

Example:

```json
{
  "answer": "Theo tài liệu...",
  "sources": [
    {
      "document_id": "doc_001",
      "content": "Trong ngày...",
      "metadata": {}
    }
  ],
  "metadata": {
    "route": "rag"
  }
}
```

---

# 10. Interface Summary

| Module    | Input              | Output            |
| --------- | ------------------ | ----------------- |
| Router    | `Query`            | `RouteDecision`   |
| Agent     | `Query`            | `Response`        |
| RAG       | `Query`            | `Response`        |
| Retriever | `RetrievalRequest` | `RetrievalResult` |
| Reranker  | `RerankRequest`    | `RerankResult`    |
| Memory    | `MemoryRequest`    | `MemoryResult`    |

---

# 11. Implementation Rules

1. Không thay đổi field nếu chưa thống nhất.
2. Có thể thay đổi implementation nội bộ.
3. Output phải đúng schema.
4. Field mới phải thông báo leader.
5. Chỉ sử dụng public interface.
6. Retriever không rerank.
7. Reranker không retrieval.
8. Agent chỉ read Memory.
9. AI không trực tiếp modify database.
10. NEU-specific context đặt trong `Query.metadata`.

---

# 12. Contract Flow

```text
Query
 │
 ▼
Router
 │
 ├── agent → Agent → Response
 │              │
 │              ├── Retriever
 │              ├── Reranker
 │              └── Memory
 │
 ├── rag → RAG → Response
 │           │
 │           ├── Retriever
 │           └── Reranker
 │
 └── ood
```

---

