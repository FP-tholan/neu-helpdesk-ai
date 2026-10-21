from datetime import datetime

from database.db import SessionLocal
from models.ticket import Ticket


def seed_tickets():
    db = SessionLocal()
    try:
        tickets = [
            # === Ticket 001: CLOSED + có rating (cho dashboard có dữ liệu) ===
            Ticket(
                id="TCK-20260914-001",
                title="Máy tính phòng A2.602 không kết nối được Wifi",
                reporter_id="USR_STUDENT_01",
                room_id="ROOM_A2_602",
                description="Máy tính phòng A2.602 không kết nối được Wifi toàn trường",
                category="COMPUTER",
                priority="MEDIUM",
                status="CLOSED",
                assigned_team_id="T_IT",
                assigned_to="USR_TECH_IT_01",
                created_at=datetime.fromisoformat("2026-09-14T08:00:00"),
                updated_at=datetime.fromisoformat("2026-09-14T10:30:00"),
                rating=5,
                rating_comment="Xử lý nhanh, KTV thân thiện.",
                rated_at=datetime.fromisoformat("2026-09-14T10:30:00"),
            ),
            Ticket(
                id="TCK-20260915-002",
                title="Điều hòa phòng A2.602 chảy nước",
                reporter_id="USR_LECTURER_01",
                room_id="ROOM_A2_602",
                description="Điều hòa phòng A2.602 chảy nước",
                category="AIR_CONDITIONER",
                priority="HIGH",
                status="IN_PROGRESS",
                assigned_team_id="T_PSA",
                assigned_to="USR_TECH_PSA_01",
                created_at=datetime.fromisoformat("2026-09-15T07:30:00"),
                updated_at=datetime.fromisoformat("2026-09-15T09:15:00"),
            ),
            Ticket(
                id="TCK-20260915-003",
                title="Máy chiếu phòng B.102 không hoạt động",
                reporter_id="USR_STUDENT_01",
                room_id="ROOM_B_102",
                description="Máy chiếu phòng B.102 không hoạt động",
                category="PROJECTOR",
                priority="HIGH",
                status="WAITING_CONFIRM",
                assigned_team_id="T_QTTB",
                assigned_to="USR_TECH_01",
                created_at=datetime.fromisoformat("2026-09-15T08:10:00"),
                updated_at=datetime.fromisoformat("2026-09-15T08:30:00"),
            ),

            # === 3 ticket CLOSED bổ sung để dashboard Team Lead có rating đa dạng ===
            Ticket(
                id="TCK-20260910-005",
                title="Ổ cắm điện phòng A2.101 bị hỏng",
                reporter_id="USR_STUDENT_01",
                room_id="ROOM_A2_101",
                description="Ổ cắm điện góc trái phòng A2.101 không có điện",
                category="ELECTRICITY",
                priority="MEDIUM",
                status="CLOSED",
                assigned_team_id="T_PSA",
                assigned_to="USR_TECH_PSA_01",
                created_at=datetime.fromisoformat("2026-09-10T09:00:00"),
                updated_at=datetime.fromisoformat("2026-09-10T11:00:00"),
                rating=4,
                rating_comment="KTV nhiệt tình, chỉ hơi chậm.",
                rated_at=datetime.fromisoformat("2026-09-10T11:00:00"),
            ),
            Ticket(
                id="TCK-20260911-006",
                title="Điều hòa phòng B.401 kêu to",
                reporter_id="USR_LECTURER_01",
                room_id="ROOM_B_401",
                description="Điều hòa phòng B.401 hoạt động nhưng kêu rất to",
                category="AIR_CONDITIONER",
                priority="MEDIUM",
                status="CLOSED",
                assigned_team_id="T_QTTB",
                assigned_to="USR_TECH_01",
                created_at=datetime.fromisoformat("2026-09-11T14:00:00"),
                updated_at=datetime.fromisoformat("2026-09-11T16:00:00"),
                rating=5,
                rating_comment="Rất hài lòng.",
                rated_at=datetime.fromisoformat("2026-09-11T16:00:00"),
            ),
            Ticket(
                id="TCK-20260912-007",
                title="Bàn ghế phòng A2.202 lung lay",
                reporter_id="USR_STUDENT_01",
                room_id="ROOM_A2_202",
                description="Bàn ghế dãy giữa phòng A2.202 bị lung lay",
                category="FURNITURE",
                priority="LOW",
                status="CLOSED",
                assigned_team_id="T_PSA",
                assigned_to="USR_TECH_PSA_01",
                created_at=datetime.fromisoformat("2026-09-12T08:00:00"),
                updated_at=datetime.fromisoformat("2026-09-12T09:30:00"),
                rating=3,
                rating_comment="Đã sửa nhưng chưa chắc chắn lắm.",
                rated_at=datetime.fromisoformat("2026-09-12T09:30:00"),
            ),
        ]
        for t in tickets:
            if db.query(Ticket).filter(Ticket.id == t.id).first():
                print(f"Skip: {t.id}")
                continue
            db.add(t)
        db.commit()
        print("Tickets seeded.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_tickets()