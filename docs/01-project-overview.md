# NEU HelpDesk AI — Project Overview

**Owner:** [ALL]
**Primary owner:** BA
**Version:** v0

---

## 1. Problem

Sinh viên/giảng viên cần một kênh tập trung để:

* báo cáo sự cố cơ sở vật chất;
* biết đơn vị nào đang xử lý;
* theo dõi tiến độ;
* phản hồi kết quả xử lý.

Nhà trường có nhiều đội kỹ thuật, mỗi đội phụ trách một hoặc nhiều tòa nhà.

Ví dụ:

```text
Team PSA → quản lý A1, A2
Team QTTB → quản lý B, C, D
Team IT → quản lý toàn bộ hệ thống cáp, wifi, ...
```

---

# 2. Solution

NEU HelpDesk AI cung cấp website có chatbot.

Người dùng có thể nhập tự nhiên:

> "Phòng B203 máy chiếu không lên."

AI phân tích câu hỏi và trả structured response.

Backend sử dụng thông tin đó để xử lý nghiệp vụ.

---

# 3. Actors

## Student / Lecturer

Có thể:

* chat với chatbot;
* tạo ticket;
* xem ticket của mình;
* xem lịch sử xử lý;
* accept/reject kết quả.

## Technician

Có thể:

* xem ticket của team;
* tiếp nhận;
* cập nhật trạng thái;
* thêm ghi chú;
* đánh dấu resolved.

## Admin

Có thể:

* xem toàn bộ ticket;
* thay đổi assignment;
* điều chỉnh priority;
* điều chỉnh status;
* quản lý team;
* xem thống kê.

---

# 4. Main Architecture

```text
Frontend
   │
   ▼
Backend
   │
   ├── Database
   │
   └── RAG-LLM
          │
          ├── Router
          ├── Agent
          ├── RAG
          ├── Retriever
          ├── Reranker
          └── Memory
```

---

# 5. AI Architecture

```text
User Query
    │
    ▼
  Router
    │
    ├── agent ──→ Agent
    │
    ├── rag ────→ RAG
    │
    └── ood ────→ Out-of-domain handling
```

Agent/RAG sử dụng chung:

```text
Response
```

và các tools theo Communication Schema.

---

# 6. Demo Scenario

Input:

```text
Máy chiếu phòng B203 không hoạt động trong giờ học.
```

Expected flow:

```text
User
 ↓
Chatbot
 ↓
Router
 ↓
Agent
 ↓
Structured understanding
 ↓
Backend
 ↓
Create Ticket
 ↓
B203 → Building B
 ↓
TEAM_BCD
 ↓
Technician
 ↓
Resolved
 ↓
Student Accept
 ↓
Closed
```

---

# 7. Demo Scope

### In Scope

* Chatbot
* Report issue
* AI analysis
* Ticket creation
* Team dispatch
* Technician dashboard
* Student tracking
* Accept / Reject
* Admin observation
* Basic RAG
* Seed data

### Out of Scope

* Real SSO
* Real QR deployment
* Real GPS
* Real timetable integration
* Production notification
* Complex duplicate detection
* Large-scale multi-agent
* Complex escalation engine
* Annual asset lifecycle analytics

---

# 8. Hardware Constraint

Host GPU:

```text
~6 GB VRAM
```

Model target:

```text
Qwen2.5:3B
```

Design principle:

> Không yêu cầu LLM thực hiện các task có thể giải quyết deterministic bằng Backend.

---

# 9. Technology Principle

```text
LLM
→ language understanding

RAG
→ knowledge retrieval

Backend
→ business logic

Database
→ persistent truth

Frontend
→ presentation
```

---
