from datetime import datetime

from database.db import SessionLocal
from models.ticket_history import TicketHistory
from models.ticket import Ticket
from models.user import User


def seed_ticket_history():
    db = SessionLocal()

    try:
        histories = [
            # Ticket 001
            TicketHistory(
                id="HIS-001-01",
                ticket_id="TCK-20260914-001",
                from_status=None,
                to_status="NEW",
                note="Ticket được tạo.",
                updated_by="USR_STUDENT_01",
                created_at=datetime.fromisoformat(
                    "2026-09-14T08:00:00"
                ),
            ),
            TicketHistory(
                id="HIS-001-02",
                ticket_id="TCK-20260914-001",
                from_status="NEW",
                to_status="IN_PROGRESS",
                note="Đã tiếp nhận và bắt đầu xử lý.",
                updated_by="USR_TECH_01",
                created_at=datetime.fromisoformat(
                    "2026-09-14T08:30:00"
                ),
            ),
            TicketHistory(
                id="HIS-001-03",
                ticket_id="TCK-20260914-001",
                from_status="IN_PROGRESS",
                to_status="WAITING_CONFIRM",
                note="Đã xử lý xong, chờ người báo lỗi xác nhận.",
                updated_by="USR_TECH_01",
                created_at=datetime.fromisoformat(
                    "2026-09-14T10:00:00"
                ),
            ),
            TicketHistory(
                id="HIS-001-04",
                ticket_id="TCK-20260914-001",
                from_status="WAITING_CONFIRM",
                to_status="CLOSED",
                note="Người báo lỗi xác nhận đã hoàn thành.",
                updated_by="USR_STUDENT_01",
                created_at=datetime.fromisoformat(
                    "2026-09-14T10:30:00"
                ),
            ),

            # Ticket 002
            TicketHistory(
                id="HIS-002-01",
                ticket_id="TCK-20260915-002",
                from_status=None,
                to_status="NEW",
                note="Ticket được tạo.",
                updated_by="USR_LECTURER_01",
                created_at=datetime.fromisoformat(
                    "2026-09-15T07:30:00"
                ),
            ),
            TicketHistory(
                id="HIS-002-02",
                ticket_id="TCK-20260915-002",
                from_status="NEW",
                to_status="IN_PROGRESS",
                note="Đã tiếp nhận và đang kiểm tra điều hòa.",
                updated_by="USR_TECH_01",
                created_at=datetime.fromisoformat(
                    "2026-09-15T09:15:00"
                ),
            ),

            # Ticket 003
            TicketHistory(
                id="HIS-003-01",
                ticket_id="TCK-20260915-003",
                from_status=None,
                to_status="NEW",
                note="Ticket được tạo.",
                updated_by="USR_STUDENT_01",
                created_at=datetime.fromisoformat(
                    "2026-09-15T08:10:00"
                ),
            ),
            TicketHistory(
                id="HIS-003-02",
                ticket_id="TCK-20260915-003",
                from_status="NEW",
                to_status="IN_PROGRESS",
                note="Đã tiếp nhận và kiểm tra máy chiếu.",
                updated_by="USR_TECH_01",
                created_at=datetime.fromisoformat(
                    "2026-09-15T08:20:00"
                ),
            ),
            TicketHistory(
                id="HIS-003-03",
                ticket_id="TCK-20260915-003",
                from_status="IN_PROGRESS",
                to_status="WAITING_CONFIRM",
                note="Máy chiếu đã hoạt động trở lại.",
                updated_by="USR_TECH_01",
                created_at=datetime.fromisoformat(
                    "2026-09-15T08:30:00"
                ),
            ),

            # Ticket 004
            TicketHistory(
                id="HIS-004-01",
                ticket_id="TCK-20260915-004",
                from_status=None,
                to_status="NEW",
                note="Ticket được tạo.",
                updated_by="USR_STUDENT_01",
                created_at=datetime.fromisoformat(
                    "2026-09-15T09:00:00"
                ),
            ),
            TicketHistory(
                id="HIS-005-01",
                ticket_id="TCK-20260910-005",
                from_status=None,
                to_status="NEW",
                note="Ticket được tạo.",
                updated_by="USR_STUDENT_01",
                created_at=datetime.fromisoformat("2026-09-10T09:00:00"),
            ),
            TicketHistory(
                id="HIS-005-02",
                ticket_id="TCK-20260910-005",
                from_status="WAITING_CONFIRM",
                to_status="CLOSED",
                note="Người báo xác nhận. Đánh giá: 4/5 sao.",
                updated_by="USR_STUDENT_01",
                created_at=datetime.fromisoformat("2026-09-10T11:00:00"),
            ),

            TicketHistory(
                id="HIS-006-01",
                ticket_id="TCK-20260911-006",
                from_status=None,
                to_status="NEW",
                note="Ticket được tạo.",
                updated_by="USR_LECTURER_01",
                created_at=datetime.fromisoformat("2026-09-11T14:00:00"),
            ),
            TicketHistory(
                id="HIS-006-02",
                ticket_id="TCK-20260911-006",
                from_status="WAITING_CONFIRM",
                to_status="CLOSED",
                note="Người báo xác nhận. Đánh giá: 5/5 sao.",
                updated_by="USR_LECTURER_01",
                created_at=datetime.fromisoformat("2026-09-11T16:00:00"),
            ),

            TicketHistory(
                id="HIS-007-01",
                ticket_id="TCK-20260912-007",
                from_status=None,
                to_status="NEW",
                note="Ticket được tạo.",
                updated_by="USR_STUDENT_01",
                created_at=datetime.fromisoformat("2026-09-12T08:00:00"),
            ),
            TicketHistory(
                id="HIS-007-02",
                ticket_id="TCK-20260912-007",
                from_status="WAITING_CONFIRM",
                to_status="CLOSED",
                note="Người báo xác nhận. Đánh giá: 3/5 sao.",
                updated_by="USR_STUDENT_01",
                created_at=datetime.fromisoformat("2026-09-12T09:30:00"),
            ),
        ]

        for history in histories:
            existing_history = (
                db.query(TicketHistory)
                .filter(TicketHistory.id == history.id)
                .first()
            )

            if existing_history:
                print(f"History already exists: {history.id}")
                continue

            db.add(history)

        db.commit()
        print("Ticket history seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_ticket_history()