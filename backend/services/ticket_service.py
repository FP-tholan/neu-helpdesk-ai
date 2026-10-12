from models.ticket import Ticket
from models.ticket_history import TicketHistory
from models.user import User
from models.room import Room
from models.building import Building
from models.team import Team
from datetime import datetime


def get_user_ticket_detail(db, user_id, ticket_id):
    ticket = (
        db.query(Ticket)
        .filter(
            Ticket.id == ticket_id,
            Ticket.reporter_id == user_id
        )
        .first()
    )

    if ticket is None:
        return None

    reporter = (
        db.query(User)
        .filter(User.id == ticket.reporter_id)
        .first()
    )

    room = (
        db.query(Room)
        .filter(Room.id == ticket.room_id)
        .first()
    )

    building = None

    if room is not None:
        building = (
            db.query(Building)
            .filter(Building.id == room.building_id)
            .first()
        )

    assigned_team = (
        db.query(Team)
        .filter(Team.id == ticket.assigned_team_id)
        .first()
    )

    assigned_tech = None

    if ticket.assigned_to is not None:
        assigned_tech = (
            db.query(User)
            .filter(User.id == ticket.assigned_to)
            .first()
        )

    histories = (
        db.query(TicketHistory)
        .filter(TicketHistory.ticket_id == ticket.id)
        .order_by(TicketHistory.created_at.asc())
        .all()
    )

    return {
        "ticket_header": {
           "id": ticket.id,
           "title": ticket.title,
           "priority": ticket.priority,
           "status": ticket.status
        },
        
        "ticket_info": {
            "reporter": {
                "id": reporter.id,
                "name": reporter.name,
                "email": reporter.email
            } if reporter else None,

            "location": {
                "building": {
                    "id": building.id,
                    "code": building.code,
                    "name": building.name
                } if building else None,

                "room": {
                    "id": room.id,
                    "code": room.code,
                    "name": room.name
                } if room else None
            },

            "category": ticket.category,

            "assigned_team": {
                "id": assigned_team.id,
                "code": assigned_team.code,
                "name": assigned_team.name
            } if assigned_team else None,

            "assigned_tech": {
                "id": assigned_tech.id,
                "name": assigned_tech.name,
                "email": assigned_tech.email
            } if assigned_tech else None
        },

        "ticket_description": {
            "description": ticket.description,
            "attachments": []
        },

        "ticket_history": [
            {
                "time": history.created_at,
                "old_status": history.from_status,
                "new_status": history.to_status,
                "note": history.note,
                "updated_by": history.updated_by
            }
            for history in histories
        ]
    }


def close_user_ticket(db, user_id, ticket_id):
    ticket = (
        db.query(Ticket)
        .filter(
            Ticket.id == ticket_id,
            Ticket.reporter_id == user_id
        )
        .first()
    )

    if ticket is None:
        return None

    if ticket.status != "RESOLVED":
        return {
            "success": False,
            "error": "TICKET_NOT_RESOLVED"
        }

    old_status = ticket.status

    ticket.status = "CLOSED"

    history = TicketHistory(
        id=f"HIS-{ticket_id}-CLOSE",
        ticket_id=ticket.id,
        from_status=old_status,
        to_status="CLOSED",
        note="User xác nhận hoàn thành.",
        updated_by=user_id
    )

    db.add(history)
    db.commit()

    return {
        "success": True,
        "ticket_id": ticket.id,
        "old_status": old_status,
        "new_status": ticket.status
    }


def reopen_user_ticket(db, user_id, ticket_id, note):
    ticket = (
        db.query(Ticket)
        .filter(
            Ticket.id == ticket_id,
            Ticket.reporter_id == user_id
        )
        .first()
    )

    if ticket is None:
        return None

    if ticket.status != "RESOLVED":
        return {
            "success": False,
            "error": "TICKET_NOT_RESOLVED"
        }

    if not note or not note.strip():
        return {
            "success": False,
            "error": "NOTE_REQUIRED"
        }

    old_status = ticket.status

    ticket.status = "IN_PROGRESS"

    history = TicketHistory(
        id=f"HIS-{ticket_id}-REOPEN",
        ticket_id=ticket.id,
        from_status=old_status,
        to_status="IN_PROGRESS",
        note=note.strip(),
        updated_by=user_id
    )

    db.add(history)
    db.commit()

    return {
        "success": True,
        "ticket_id": ticket.id,
        "old_status": old_status,
        "new_status": ticket.status
    }


def create_user_ticket(
    db,
    user_id,
    title,
    building_name,
    room_code,
    category,
    priority,
    description
):
    # 1. Kiểm tra Building
    building = (
        db.query(Building)
        .filter(Building.name == building_name)
        .first()
    )

    if building is None:
        return {
            "success": False,
            "error": "BUILDING_NOT_FOUND"
        }

    # 2. Tìm Room thuộc Building
    room = (
        db.query(Room)
        .filter(
            Room.code == room_code,
            Room.building_id == building.id
        )
        .first()
    )

    if room is None:
        return {
            "success": False,
            "error": "ROOM_NOT_FOUND"
        }

    # 3. Xác định Team từ category
    category_team_mapping = {
        "Thiết bị giảng dạy / Máy chiếu": "T_QTTB",
        "Mạng & Hạ tầng CNTT": "T_IT",
        "Âm thanh & Ánh sáng": "T_PSA",
        "Điện lạnh & CSVC": "T_QTTB"
    }

    assigned_team_id = category_team_mapping.get(category)

    if assigned_team_id is None:
        return {
            "success": False,
            "error": "INVALID_CATEGORY"
        }

    # 4. Kiểm tra Team
    team = (
        db.query(Team)
        .filter(Team.id == assigned_team_id)
        .first()
    )

    if team is None:
        return {
            "success": False,
            "error": "TEAM_NOT_FOUND"
        }

    # 5. Kiểm tra các trường cơ bản
    if not title or not title.strip():
        return {
            "success": False,
            "error": "TITLE_REQUIRED"
        }

    if not description or not description.strip():
        return {
            "success": False,
            "error": "DESCRIPTION_REQUIRED"
        }

    allowed_priorities = {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL"
    }

    if priority not in allowed_priorities:
        return {
            "success": False,
            "error": "INVALID_PRIORITY"
        }

    # 6. Sinh Ticket ID
    today = datetime.utcnow().strftime("%Y%m%d")

    prefix = f"TCK-{today}-"

    latest_ticket = (
        db.query(Ticket)
        .filter(Ticket.id.like(f"{prefix}%"))
        .order_by(Ticket.id.desc())
        .first()
    )

    if latest_ticket:
        latest_number = int(
            latest_ticket.id.split("-")[-1]
        )
        next_number = latest_number + 1
    else:
        next_number = 1

    ticket_id = f"{prefix}{next_number:03d}"

    # 7. Tạo Ticket
    ticket = Ticket(
        id=ticket_id,
        title=title.strip(),
        reporter_id=user_id,
        room_id=room.id,
        description=description.strip(),
        category=category,
        priority=priority,
        status="ASSIGNED",
        assigned_team_id=team.id,
        assigned_to=None
    )

    db.add(ticket)

    # 8. Tạo lịch sử Ticket
    history = TicketHistory(
        id=f"HIS-{today}-{next_number:03d}-01",
        ticket_id=ticket.id,
        from_status=None,
        to_status="ASSIGNED",
        note="Ticket được tạo.",
        updated_by=user_id
    )

    db.add(history)

    # 9. Lưu database
    db.commit()

    return {
        "success": True,
        "ticket": {
            "id": ticket.id,
            "title": ticket.title,
            "category": ticket.category,
            "priority": ticket.priority,
            "status": ticket.status,
            "room": {
                "id": room.id,
                "code": room.code,
                "name": room.name
            },
            "building": {
                "id": building.id,
                "code": building.code,
                "name": building.name
            },
            "assigned_team": {
                "id": team.id,
                "code": team.code,
                "name": team.name
            }
        }
    }