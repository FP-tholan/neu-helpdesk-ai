# NEU HelpDesk AI — Database Design

**Owner:** [BA + BE]
**BA:** business meaning / ERD
**BE:** implementation
**Version:** v0

---

# 1. Entity Relationship

```text
USER
 │
 ├──────────────┐
 ▼              │
TICKET          │
 │              │
 ├── ROOM       │
 │    │         │
 │    └── BUILDING
 │                 │
 │                 ▼
 └────────────── TEAM
 │
 └── TICKET_HISTORY
```

---

# 2. Building

```text
BUILDING
├── id: string
├── code: string
└── name: string
```

Example:

```json
{
  "id": "B002",
  "code": "B",
  "name": "Tòa B"
}
```

---

# 3. Room

```text
ROOM
├── id: string
├── code: string
├── building_id: string
└── name: string
```

Example:

```json
{
  "id": "R002",
  "code": "B203",
  "building_id": "B002",
  "name": "Phòng B203"
}
```

---

# 4. Team

```text
TEAM
├── id: string
├── code: string
├── name: string
└── description: string
```

Example:

```json
{
  "id": "TEAM_BCD",
  "code": "BCD",
  "name": "Đội kỹ thuật tòa B-C-D",
  "description": "Phụ trách cơ sở vật chất tòa B, C, D"
}
```

---

# 5. Team-Building Relationship

Một team có thể quản lý nhiều building.

```text
TEAM_BCD
 ├── B
 ├── C
 └── D
```

Không hard-code trong frontend.

Backend/database là source of truth.

---

# 6. User

```text
USER
├── id: string
├── username: string
├── name: string
├── role: enum
└── team_id: string | null
```

Role:

```text
student
technician
admin
```

Student:

```json
{
  "id": "U001",
  "username": "student01",
  "name": "Student 01",
  "role": "student",
  "team_id": null
}
```

Technician:

```json
{
  "id": "U101",
  "username": "tech_bcd",
  "name": "Technician BCD",
  "role": "technician",
  "team_id": "TEAM_BCD"
}
```

---

# 7. Ticket

```text
TICKET
├── id: string
├── reporter_id: string
├── room_id: string
├── description: string
├── category: enum
├── priority: enum
├── status: enum
├── assigned_team_id: string
├── assigned_to: string | null
├── created_at: datetime
└── updated_at: datetime
```

---

# 8. Category

```text
projector
air_conditioner
microphone
computer
electricity
furniture
cleaning
other
```

---

# 9. Priority

```text
low
medium
high
critical
```

---

# 10. Ticket History

```text
TICKET_HISTORY
├── id: string
├── ticket_id: string
├── from_status: string | null
├── to_status: string
├── note: string | null
├── updated_by: string
└── created_at: datetime
```

Mọi thay đổi trạng thái phải có history.

---

# 11. Dispatch Logic

Conceptual:

```text
ticket.room_id
      ↓
ROOM.building_id
      ↓
BUILDING
      ↓
TEAM
      ↓
ticket.assigned_team_id
```

Không để AI tự suy luận database relationship.

---

# 12. Seed Data

Tối thiểu:

```text
Buildings: 5–6
Rooms: 8–15
Teams: 3–5
Users: 8–15
Tickets: 10–20
```

Ticket seed phải bao phủ:

```text
open
assigned
in_progress
resolved
closed
```

---

# 13. Ownership

### BA

Chịu trách nhiệm:

* entity;
* relationship;
* field meaning;
* business constraints;
* ERD;
* seed data definition.

### BE

Chịu trách nhiệm:

* SQL/ORM;
* migrations;
* constraints;
* foreign keys;
* indexes;
* CRUD;
* seed execution.

### QA

Verify database implementation có đúng design hay không.