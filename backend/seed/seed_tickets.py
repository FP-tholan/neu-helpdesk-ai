from datetime import datetime

from database.db import SessionLocal
from models.ticket import Ticket
from models.user import User
from models.room import Room
from models.team import Team


def seed_tickets():
    db = SessionLocal()

    try:
        tickets = [
            Ticket(
                id="TCK-20260914-001",
                title="Máy tính phòng A2.602 không kết nối được Wifi",
                reporter_id="USR_STUDENT_01",
                room_id="ROOM_A2_602",
                description="Máy tính phòng A2.602 không kết nối được Wifi toàn trường",
                category="IT",
                priority="MEDIUM",
                status="CLOSED",
                assigned_team_id="T_IT",
                assigned_to=None,
                created_at=datetime.fromisoformat(
                    "2026-09-14T08:00:00"
                ),
                updated_at=datetime.fromisoformat(
                    "2026-09-14T10:30:00"
                ),
            ),

            Ticket(
                id="TCK-20260915-002",
                title="Điều hòa phòng A2.602 chảy nước",
                reporter_id="USR_LECTURER_01",
                room_id="ROOM_A2_602",
                description="Điều hòa phòng A2.602 chảy nước",
                category="Infrastructure",
                priority="HIGH",
                status="IN_PROGRESS",
                assigned_team_id="T_PSA",
                assigned_to=None,
                created_at=datetime.fromisoformat(
                    "2026-09-15T07:30:00"
                ),
                updated_at=datetime.fromisoformat(
                    "2026-09-15T09:15:00"
                ),
            ),

            Ticket(
                id="TCK-20260915-003",
                title="Máy chiếu phòng B102 không hoạt động",
                reporter_id="USR_STUDENT_01",
                room_id="ROOM_B_102",
                description="Máy chiếu phòng B102 không hoạt động",
                category="Equipment",
                priority="HIGH",
                status="WAITING_CONFIRM",
                assigned_team_id="T_QTTB",
                assigned_to=None,
                created_at=datetime.fromisoformat(
                    "2026-09-15T08:10:00"
                ),
                updated_at=datetime.fromisoformat(
                    "2026-09-15T08:30:00"
                ),
            ),

            Ticket(
                id="TCK-20260915-004",
                title="Mùi hôi lạ từ khu vực hành lang",
                reporter_id="USR_STUDENT_01",
                room_id="ROOM_B_401",
                description="Mùi hôi lạ từ khu vực hành lang",
                category="Unmapped",
                priority="LOW",
                status="NEW",
                assigned_team_id="T_ADMIN",
                assigned_to=None,
                created_at=datetime.fromisoformat(
                    "2026-09-15T09:00:00"
                ),
                updated_at=datetime.fromisoformat(
                    "2026-09-15T09:00:00"
                ),
            ),
        ]

        for ticket in tickets:
            existing_ticket = (
                db.query(Ticket)
                .filter(Ticket.id == ticket.id)
                .first()
            )

            if existing_ticket:
                print(f"Ticket already exists: {ticket.id}")
                continue

            db.add(ticket)

        db.commit()
        print("Tickets seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_tickets()