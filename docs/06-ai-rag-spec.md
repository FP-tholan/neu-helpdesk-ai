# NEU HelpDesk AI — AI/RAG Specification

**Owner:** [RAG-LLM]
**Collaborators:** BE, QA
**Model:** Qwen2.5:3B
**Contract:** `docs/04-schema-contract.md`

---

# 1. Critical Requirement

> **Team AI phải stick theo `docs/04-schema-contract.md`.**

Không tự ý thiết kế một schema khác.

AI module public interfaces:

```text
Router
Agent
RAG
Retriever
Reranker
Memory
```

---

# 2. AI Architecture

```text
                    Query
                      │
                      ▼
                   Router
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
        Agent         RAG         OOD
          │           │
          │           │
     ┌────┼────┐      │
     ▼    ▼    ▼      ▼
 Retriever Reranker Memory
     │      │
     └──┬───┘
        ▼
     Response
```

---

# 3. Model

Target:

```text
Qwen2.5:3B
```

Lý do:

* phù hợp giới hạn ~6GB VRAM;
* đủ cho intent classification;
* structured extraction;
* conversational response;
* lightweight RAG.

Không giao cho LLM những task deterministic.

---

# 4. Router

Router quyết định:

```text
agent
rag
ood
```

### Agent

Dùng cho:

* report issue;
* track ticket;
* multi-step task;
* workflow cần tool.

### RAG

Dùng cho:

* FAQ;
* troubleshooting;
* policy;
* knowledge base.

### OOD

Dùng khi query không thuộc phạm vi HelpDesk.

---

# 5. Agent

Agent nhận:

```text
Query
```

Agent có thể sử dụng:

```text
Retriever
Reranker
Memory
```

Agent không được:

```text
write database
write memory
change ticket
assign team
```

Agent chỉ trả:

```text
Response
```

---

# 6. Retriever

Retriever chịu trách nhiệm:

```text
Query
 ↓
Candidate Documents
```

Không rerank.

Input/output phải đúng:

```text
RetrievalRequest
RetrievalResult
```

---

# 7. Reranker

Reranker chịu trách nhiệm:

```text
Candidate Documents
 ↓
Ranked Documents
```

Không retrieval.

Input/output:

```text
RerankRequest
RerankResult
```

---

# 8. Memory

Memory public interface chỉ có read.

```text
MemoryRequest
 ↓
MemoryResult
```

Agent không trực tiếp write Memory.

---

# 9. RAG

RAG pipeline:

```text
Query
 ↓
Retriever
 ↓
Candidate Documents
 ↓
Reranker
 ↓
Top Documents
 ↓
Qwen2.5:3B
 ↓
Response
```

Nếu không cần reranking:

```text
Query
 ↓
Retriever
 ↓
Qwen
 ↓
Response
```

---

# 10. Knowledge Base

Demo có thể dùng:

```text
data/knowledge_base/
├── projector.md
├── air_conditioner.md
├── microphone.md
├── electricity.md
└── helpdesk_policy.md
```

Nội dung:

```text
Problem
Symptoms
Possible causes
Troubleshooting
When to contact technician
Policy
```

---

# 11. NEU Context

AI nhận context thông qua:

```text
Query.metadata
```

Example:

```json
{
  "source": "chatbot",
  "room_id": "R002",
  "room_code": "B203",
  "building_id": "B002",
  "user_role": "student"
}
```

Không được thay đổi:

```text
Query
```

thành:

```text
HelpdeskQuery
```

trong public contract.

Nếu cần context mới:

```json
{
  "metadata": {
    "new_context": "..."
  }
}
```

---

# 12. Ticket Understanding

AI có thể phân tích:

```text
Máy chiếu phòng B203 không hoạt động.
```

và đưa thông tin vào:

```text
Response.metadata
```

nếu workflow cần.

Ví dụ:

```json
{
  "answer": "Tôi xác định đây là sự cố máy chiếu tại phòng B203.",
  "sources": [],
  "metadata": {
    "intent": "report_issue",
    "category": "projector",
    "room_code": "B203",
    "priority": "medium",
    "recommended_team_id": "TEAM_BCD"
  }
}
```

**Lưu ý:** Đây vẫn là `Response` đúng contract. Không tạo một public output type mới nếu chưa có contract change.

Backend phải validate các giá trị này trước khi dùng.

---

# 13. AI Confidence

Nếu AI cần confidence:

```json
{
  "metadata": {
    "confidence": {
      "intent": 0.96,
      "category": 0.94,
      "priority": 0.82
    }
  }
}
```

Confidence:

```text
0.0 ≤ confidence ≤ 1.0
```

---

# 14. Clarification

AI có thể yêu cầu clarification thông qua `Response`.

Ví dụ:

```json
{
  "answer": "Sự cố xảy ra ở phòng nào?",
  "sources": [],
  "metadata": {
    "intent": "report_issue",
    "needs_clarification": true,
    "clarification_type": "room"
  }
}
```

Frontend không cần biết AI implementation.

Frontend chỉ render `answer` và metadata cần thiết theo API contract.

---

# 15. Team Recommendation

AI có thể recommend:

```text
TEAM_BCD
```

nhưng:

```text
AI recommendation
        ↓
Backend validation
        ↓
Database
        ↓
Actual assignment
```

Không được coi:

```text
AI → TEAM_BCD
```

là assignment chính thức.

---

# 16. Prompt Rules

Qwen phải được yêu cầu:

```text
1. Không hallucinate database ID.
2. Không tự tạo ticket.
3. Không tự assign ticket.
4. Không tự thay đổi status.
5. Không truy cập database.
6. Tuân thủ output contract.
7. Không trả field ngoài contract nếu không cần.
8. Confidence nằm trong [0,1].
9. Nếu thiếu thông tin → clarification.
10. Nếu không thuộc domain → OOD.
```

---

# 17. Error Handling

AI module phải xử lý:

```text
Model unavailable
Timeout
Invalid output
Malformed response
Low confidence
Empty response
```

Không để exception nội bộ leak ra frontend.

---

# 18. AI Evaluation

Các metric cơ bản:

### Router

```text
Accuracy
Macro-F1
OOD detection
```

### Retriever

```text
Recall@K
Hit@K
```

### Reranker

```text
MRR
NDCG@K
```

### RAG

```text
Answer correctness
Faithfulness
Citation/source relevance
```

### End-to-end

```text
Successful ticket understanding
Correct room extraction
Correct category
Correct routing recommendation
```

---

# 19. AI Directory Contract

```text
rag-llm/
│
├── src/
│   ├── router/                 # Router implementation
│   │
│   ├── agent/                  # Agent implementation
│   │
│   ├── rag/                    # RAG implementation
│   │
│   ├── tools/
│   │   ├── retriever/          # Retriever implementation
│   │   ├── reranker/           # Reranker implementation
│   │   └── memory/             # Memory implementation
│   │
│   └── main.py                 # AI service entry point
│
├── eval/                       # AI evaluation
├── assets/                     # Diagrams/assets
└── requirements.txt
```

---

# 20. Module Ownership

| Module    | Owner | Public Interface                     |
| --------- | ----- | ------------------------------------ |
| Router    | RAG   | `Query → RouteDecision`              |
| Agent     | RAG   | `Query → Response`                   |
| RAG       | RAG   | `Query → Response`                   |
| Retriever | RAG   | `RetrievalRequest → RetrievalResult` |
| Reranker  | RAG   | `RerankRequest → RerankResult`       |
| Memory    | RAG   | `MemoryRequest → MemoryResult`       |

---

# 21. Final AI Contract

```text
Router

    Query
      ↓
RouteDecision


Agent

    Query
      ↓
Response

    RetrievalRequest
      ↓
RetrievalResult

    RerankRequest
      ↓
RerankResult

    MemoryRequest
      ↓
MemoryResult


RAG

    Query
      ↓
Response

    RetrievalRequest
      ↓
RetrievalResult

    RerankRequest
      ↓
RerankResult


Retriever

    RetrievalRequest
      ↓
RetrievalResult


Reranker

    RerankRequest
      ↓
RerankResult


Memory

    MemoryRequest
      ↓
MemoryResult
```

---

# 22. Contract Version

```text
Contract Version: v0
Status: ACTIVE
```

Mọi thay đổi public interface phải:

```text
[CONTRACT]
```

và được thống nhất trước khi merge.
