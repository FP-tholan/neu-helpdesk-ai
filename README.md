# NEU HelpDesk AI

> Website hỗ trợ sinh viên/giảng viên báo cáo, theo dõi và phản hồi các vấn đề về cơ sở vật chất của nhà trường thông qua chatbot AI.

---

## 1. Project Overview

NEU HelpDesk AI là hệ thống HelpDesk dành cho cơ sở vật chất.

Sinh viên/giảng viên có thể sử dụng chatbot để:

* báo cáo sự cố cơ sở vật chất;
* hỏi cách tự xử lý các lỗi đơn giản;
* theo dõi ticket;
* xác nhận tình trạng sau khi kỹ thuật xử lý.

Các đội kỹ thuật của nhà trường chịu trách nhiệm theo từng tòa/khu vực.

Ví dụ:

```text
Team PSA → quản lý A1, A2
Team QTTB → quản lý B, C, D
Team IT → quản lý toàn bộ hệ thống cáp, wifi, ...
```

Admin có thể quan sát và điều chỉnh toàn bộ hệ thống.

---

## 2. Main Workflow

```text
Student / Lecturer
        │
        ▼
     Chatbot
        │
        ▼
      Router
        │
        ├──────────────┐
        ▼              ▼
      Agent           RAG
        │              │
        │              └── FAQ / Troubleshooting
        │
        └── Ticket-related processing
                │
                ▼
             Backend
                │
                ▼
             Ticket
                │
                ▼
        Responsible Team
                │
                ▼
          Technician
                │
                ▼
        Update Ticket
                │
                ▼
            Student
                │
          ┌─────┴─────┐
          ▼           ▼
        Accept      Reject
          │           │
          ▼           ▼
        Closed     Re-process
```

---

## 3. System Architecture

```text
┌────────────────────────────────────────────┐
│                  FRONTEND                  │
│                                            │
│ Chatbot │ Ticket Tracking │ Dashboard     │
└─────────────────────┬──────────────────────┘
                      │
                      │ REST / JSON
                      ▼
┌────────────────────────────────────────────┐
│                  BACKEND                   │
│                                            │
│ Ticket │ Team │ User │ Permission │ DB    │
└─────────────────────┬──────────────────────┘
                      │
                      │ Internal AI Interface
                      ▼
┌────────────────────────────────────────────┐
│                RAG-LLM MODULE              │
│                                            │
│ Router │ Agent │ RAG │ Retriever           │
│ Reranker │ Memory │ Qwen2.5:3B             │
└────────────────────────────────────────────┘
```

### Core principle

> **AI hiểu ngôn ngữ. Backend điều hành nghiệp vụ. Database là source of truth.**

AI không được trực tiếp:

* sửa database;
* assign ticket;
* thay đổi ticket status;
* bypass permission;
* thực hiện business action.

AI chỉ trả recommendation/response theo contract.

---

# 4. Repository Structure

```text
neu-helpdesk-ai/
│
├── README.md                              # [ALL]
│
├── docs/
│   ├── 01-project-overview.md             # [ALL]
│   ├── 02-business-spec.md                # [BA]
│   ├── 03-database-design.md              # [BA + BE]
│   ├── 04-schema-contract.md              # [ALL] ⭐
│   ├── 05-api-spec.md                     # [BE + FE]
│   └── 06-ai-rag-spec.md                  # [RAG-LLM]
│
├── backend/                               # [BE]
│   ├── main.py
│   ├── api/
│   ├── models/
│   ├── services/
│   └── database/
│
├── rag-llm/                               # [RAG-LLM]
│   ├── src/
│   │   ├── agent/
│   │   ├── rag/
│   │   ├── router/
│   │   ├── tools/
│   │   │   ├── retriever/
│   │   │   ├── reranker/
│   │   │   └── memory/
│   │   └── main.py
│   ├── eval/
│   ├── assets/
│   └── requirements.txt
│
├── frontend/                              # [FE]
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── services/
│   │   └── types/
│   └── package.json
│
├── tests/                                 # [QA]
│   ├── backend/
│   ├── rag-llm/
│   └── e2e/
│
└── data/
    ├── users.json                         # [BA]
    ├── buildings.json                     # [BA]
    ├── rooms.json                         # [BA]
    ├── teams.json                         # [BA]
    ├── tickets.json                       # [BA + BE]
    └── knowledge_base/                    # [RAG-LLM]
```

---

# 5. Team Responsibilities

| Team        | Responsibility                                                       | Main files                               |
| ----------- | -------------------------------------------------------------------- | ---------------------------------------- |
| **BA**      | Business requirement, workflow, business rules, DB design, seed data | `docs/01`, `docs/02`, `docs/03`, `data/` |
| **BE**      | Backend, database implementation, API, ticket lifecycle, dispatch    | `backend/`, `docs/05`                    |
| **RAG-LLM** | Qwen, Router, Agent, RAG, Retriever, Reranker, Memory                | `rag-llm/`, `docs/06`                    |
| **FE**      | Website, chatbot UI, dashboard, ticket tracking                      | `frontend/`                              |
| **QA**      | Test cases, integration test, E2E test                               | `tests/`                                 |

---

# 6. Documentation Map

### `01-project-overview.md` — [ALL]

Giải thích:

* project là gì;
* users;
* architecture;
* scope;
* demo scenario.

### `02-business-spec.md` — [BA]

Giải thích:

* business workflow;
* ticket lifecycle;
* dispatch;
* permission;
* escalation;
* business rules.

### `03-database-design.md` — [BA + BE]

Giải thích:

* entities;
* relationships;
* ERD;
* database fields;
* seed data.

BA sở hữu **business meaning**.

BE sở hữu **database implementation**.

### `04-schema-contract.md` — [ALL]

> ⭐ **Shared Interface Contract**

Định nghĩa chính xác input/output giữa các module.

Đây là file quan trọng nhất khi merge code.

### `05-api-spec.md` — [BE + FE]

Định nghĩa:

* REST endpoint;
* HTTP method;
* authentication;
* request;
* response;
* errors.

### `06-ai-rag-spec.md` — [RAG-LLM]

Định nghĩa:

* AI architecture;
* Qwen;
* Router;
* Agent;
* RAG;
* Retriever;
* Reranker;
* Memory;
* prompt;
* evaluation.

---

# 7. AI Module Contract

Team RAG-LLM phải **stick theo `docs/04-schema-contract.md`**.

Không tự ý đổi:

```text
Query
RouteDecision
Response
RetrievalRequest
RetrievalResult
Document
RerankRequest
RerankResult
RankedDocument
MemoryRequest
MemoryResult
Memory
Source
```

Nếu cần thêm field:

```text
[CONTRACT] Add <field>
```

và phải thống nhất trước khi merge.

---

# 8. NEU-specific Context

AI Communication Schema dùng chung không thay đổi.

Thông tin nghiệp vụ NEU truyền qua:

```text
Query.metadata
```

Ví dụ:

```json
{
  "query": "Máy chiếu phòng B203 không hoạt động",
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

AI không cần biết database implementation của Backend.

---

# 9. Important Development Rules

## Rule 1 — Contract First

Không code integration khi chưa thống nhất interface.

```text
Contract
   ↓
Implementation
   ↓
Integration
   ↓
Testing
```

## Rule 2 — Public Interface Only

Module khác chỉ được sử dụng public interface.

Không import internal implementation của module khác.

## Rule 3 — Backend Owns Business Logic

AI có thể recommend:

```text
recommended team
recommended priority
```

nhưng Backend quyết định cuối cùng.

## Rule 4 — Database Is Source of Truth

Không lấy thông tin team/room từ hallucination của LLM.

Backend phải validate bằng database.

---

# 10. Git Workflow

Không push trực tiếp vào `main`.

```text
main
 │
 ├── feature/ai-router
 ├── feature/rag-pipeline
 ├── feature/ticket-api
 ├── feature/chatbot-ui
 └── test/e2e-ticket-flow
```

Workflow:

```text
Branch
  ↓
Implement
  ↓
Test
  ↓
Pull Request
  ↓
Review
  ↓
Merge
```

---

# 11. Definition of Done

Feature chỉ được merge khi:

```text
[ ] Đúng requirement
[ ] Đúng schema contract
[ ] Đúng API
[ ] Có error handling
[ ] Có test
[ ] Không phá interface cũ
[ ] PR được review
```

---

# 12. Golden Rule

> **Nếu interface không rõ → đọc `04-schema-contract.md`.**

> **Nếu nghiệp vụ không rõ → đọc `02-business-spec.md`.**

> **Nếu database không rõ → đọc `03-database-design.md`.**

> **Nếu API không rõ → đọc `05-api-spec.md`.**

> **Nếu AI behavior không rõ → đọc `06-ai-rag-spec.md`.**
