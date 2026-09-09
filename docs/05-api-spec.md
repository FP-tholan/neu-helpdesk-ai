# NEU HelpDesk AI — API Specification

**Owner:** [BE]
**Consumers:** FE, RAG-LLM, QA
**Version:** v0

---

# 1. API Rules

Frontend chỉ gọi Backend.

```text
FE → BE
```

Không:

```text
FE → Database
FE → Qwen
FE → Retriever
```

Backend gọi AI module qua AI interface.

---

# 2. Common Error

```json
{
  "success": false,
  "error": {
    "code": "TICKET_NOT_FOUND",
    "message": "Ticket does not exist."
  }
}
```

---

# 3. AI Analyze

## Endpoint

```http
POST /ai/query
```

## Input

Backend tạo:

```text
Query
```

theo:

```text
docs/04-schema-contract.md
```

Example:

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

## Output

AI trả:

```text
RouteDecision
```

hoặc:

```text
Response
```

tùy route.

---

# 4. Create Ticket

```http
POST /tickets
```

## Input

```json
{
  "reporter_id": "U001",
  "room_id": "R002",
  "description": "Máy chiếu phòng B203 không hoạt động.",
  "category": "projector",
  "priority": "medium"
}
```

## Output

```json
{
  "success": true,
  "ticket": {
    "id": "T001",
    "reporter_id": "U001",
    "room_id": "R002",
    "description": "Máy chiếu phòng B203 không hoạt động.",
    "category": "projector",
    "priority": "medium",
    "status": "assigned",
    "assigned_team_id": "TEAM_BCD",
    "created_at": "2026-09-09T09:30:00+07:00",
    "updated_at": "2026-09-09T09:30:00+07:00"
  }
}
```

Backend tự quyết định:

```text
assigned_team_id
status
timestamps
```

---

# 5. Get Ticket

```http
GET /tickets/{ticket_id}
```

Output:

```json
{
  "success": true,
  "ticket": {
    "id": "T001",
    "status": "in_progress",
    "assigned_team_id": "TEAM_BCD",
    "updated_at": "2026-09-09T10:00:00+07:00"
  }
}
```

---

# 6. Update Status

```http
PATCH /tickets/{ticket_id}/status
```

## Input

```json
{
  "status": "in_progress",
  "note": "Đã tiếp nhận và đang kiểm tra."
}
```

## Output

```json
{
  "success": true,
  "ticket": {
    "id": "T001",
    "status": "in_progress",
    "updated_at": "2026-09-09T10:00:00+07:00"
  }
}
```

---

# 7. Accept Ticket

```http
POST /tickets/{ticket_id}/accept
```

## Input

```json
{
  "comment": "Máy chiếu đã hoạt động bình thường."
}
```

## Output

```json
{
  "success": true,
  "ticket_id": "T001",
  "status": "closed"
}
```

---

# 8. Reject Ticket

```http
POST /tickets/{ticket_id}/reject
```

## Input

```json
{
  "reason": "Máy chiếu vẫn chưa hoạt động."
}
```

## Output

```json
{
  "success": true,
  "ticket_id": "T001",
  "status": "rejected"
}
```

Backend xử lý workflow tiếp theo theo business rule.

---

# 9. Team Tickets

```http
GET /teams/{team_id}/tickets
```

Technician chỉ được xem ticket của team mình.

Admin có thể xem tất cả.

---

# 10. Admin

```http
GET   /admin/tickets
PATCH /admin/tickets/{ticket_id}
GET   /admin/statistics
```

Admin có thể:

* xem toàn bộ;
* đổi team;
* đổi priority;
* điều chỉnh status.

---

# 11. API Ownership

### BE

Owner:

* endpoint;
* validation;
* permission;
* business logic;
* persistence.

### FE

Consumer.

### RAG

Chỉ chịu trách nhiệm AI interface.

### QA

Verify request/response.

---

