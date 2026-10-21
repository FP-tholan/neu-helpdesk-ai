import uuid
from datetime import datetime

from models.ticket import Ticket
from models.ticket_history import TicketHistory
from models.user import User
from models.room import Room
from models.building import Building
from models.team import Team
from models.dispatch_rule import DispatchRule


ALLOWED_PRIORITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}

ALLOWED_CATEGORIES = {
    "PROJECTOR", "COMPUTER", "WIFI", "MICROPHONE",
    "AIR_CONDITIONER", "ELECTRICITY", "FURNITURE",
    "CLEANING", "OTHER",
}


# =============================================================
# DISPATCH
# =============================================================

def resolve_team_for_ticket(db, category, building_id):
    """
    Dispatch theo bảng dispatch_rules:
    - match category nếu rule có category
    - match building nếu rule có building
    - NULL match all
    - sắp xếp theo priority ASC, lấy rule đầu
    """
    rules = (
        db.query(DispatchRule)
        .order_by(DispatchRule.priority.asc())
        .all()
    )

    for rule in rules:
        if rule.category is not None and rule.category != category:
            continue
        if rule.building_id is not None and rule.building_id != building_id:
            continue
        return rule.team_id

    return None


# =============================================================
# CREATE TICKET
# =============================================================

def create_user_ticket(
    db, user_id, title, building_name, room_code,
    category, priority, description
):
    if not title or not title.strip():
        return {"success": False, "error": "TITLE_REQUIRED"}

    if not description or not description.strip():
        return {"success": False, "error": "DESCRIPTION_REQUIRED"}

    if category not in ALLOWED_CATEGORIES:
        return {"success": False, "error": "INVALID_CATEGORY"}

    if priority not in ALLOWED_PRIORITIES:
        return {"success": False, "error": "INVALID_PRIORITY"}

    building = db.query(Building).filter(Building.name == building_name).first()
    if building is None:
        return {"success": False, "error": "BUILDING_NOT_FOUND"}

    room = (
        db.query(Room)
        .filter(Room.code == room_code, Room.building_id == building.id)
        .first()
    )
    if room is None:
        return {"success": False, "error": "ROOM_NOT_FOUND"}

    team_id = resolve_team_for_ticket(db, category, building.id)
    if team_id is None:
        return {"success": False, "error": "DISPATCH_FAILED"}

    team = db.query(Team).filter(Team.id == team_id).first()
    if team is None:
        return {"success": False, "error": "TEAM_NOT_FOUND"}

    today = datetime.utcnow().strftime("%Y%m%d")
    prefix = f"TCK-{today}-"
    latest = (
        db.query(Ticket)
        .filter(Ticket.id.like(f"{prefix}%"))
        .order_by(Ticket.id.desc())
        .first()
    )
    next_number = 1
    if latest:
        try:
            next_number = int(latest.id.split("-")[-1]) + 1
        except ValueError:
            next_number = 1
    ticket_id = f"{prefix}{next_number:03d}"

    # Trạng thái khởi tạo: NEW
    ticket = Ticket(
        id=ticket_id,
        title=title.strip(),
        reporter_id=user_id,
        room_id=room.id,
        description=description.strip(),
        category=category,
        priority=priority,
        status="NEW",
        assigned_team_id=team.id,
        assigned_to=None,
    )
    db.add(ticket)

    # History 1: tạo ticket
    db.add(TicketHistory(
        id=f"HIS-{uuid.uuid4()}",
        ticket_id=ticket.id,
        from_status=None,
        to_status="NEW",
        note="Ticket được tạo.",
        updated_by=user_id,
    ))

    # Dispatch ngay: NEW → ASSIGNED
    ticket.status = "ASSIGNED"
    db.add(TicketHistory(
        id=f"HIS-{uuid.uuid4()}",
        ticket_id=ticket.id,
        from_status="NEW",
        to_status="ASSIGNED",
        note=f"Hệ thống tự động gán về Team {team.name}.",
        updated_by=user_id,
    ))

    db.commit()

    return {
        "success": True,
        "data": {
            "id": ticket.id,
            "title": ticket.title,
            "category": ticket.category,
            "priority": ticket.priority,
            "status": ticket.status,
            "room": {"id": room.id, "code": room.code, "name": room.name},
            "building": {"id": building.id, "code": building.code, "name": building.name},
            "assigned_team": {"id": team.id, "code": team.code, "name": team.name},
        },
    }


# =============================================================
# GET DETAIL
# =============================================================

def get_user_ticket_detail(db, user_id, ticket_id):
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id, Ticket.reporter_id == user_id)
        .first()
    )
    if ticket is None:
        return None

    reporter = db.query(User).filter(User.id == ticket.reporter_id).first()
    room = db.query(Room).filter(Room.id == ticket.room_id).first()
    building = None
    if room is not None:
        building = db.query(Building).filter(Building.id == room.building_id).first()

    assigned_team = db.query(Team).filter(Team.id == ticket.assigned_team_id).first()

    assigned_tech = None
    if ticket.assigned_to is not None:
        assigned_tech = db.query(User).filter(User.id == ticket.assigned_to).first()

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
            "status": ticket.status,
        },
        "ticket_info": {
            "reporter": {"id": reporter.id, "name": reporter.name, "email": reporter.email} if reporter else None,
            "location": {
                "building": {"id": building.id, "code": building.code, "name": building.name} if building else None,
                "room": {"id": room.id, "code": room.code, "name": room.name} if room else None,
            },
            "category": ticket.category,
            "assigned_team": {"id": assigned_team.id, "code": assigned_team.code, "name": assigned_team.name} if assigned_team else None,
            "assigned_tech": {"id": assigned_tech.id, "name": assigned_tech.name, "email": assigned_tech.email} if assigned_tech else None,
        },
        "ticket_description": {"description": ticket.description, "attachments": []},
        "ticket_history": [
            {
                "time": h.created_at,
                "old_status": h.from_status,
                "new_status": h.to_status,
                "note": h.note,
                "updated_by": h.updated_by,
            }
            for h in histories
        ],
    }


# =============================================================
# ACCEPT / REJECT
# =============================================================

def accept_user_ticket(db, user_id, ticket_id, rating=None, rating_comment=None):
    """
    User accept ticket ở WAITING_CONFIRM → CLOSED.
    Có thể kèm rating (1-5) + comment tuỳ chọn.
    """
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id, Ticket.reporter_id == user_id)
        .first()
    )
    if ticket is None:
        return None

    if ticket.status != "WAITING_CONFIRM":
        return {"success": False, "error": "TICKET_NOT_WAITING_CONFIRM"}

    if rating is not None:
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return {"success": False, "error": "INVALID_RATING"}

    if rating_comment is not None:
        if not isinstance(rating_comment, str):
            return {"success": False, "error": "INVALID_COMMENT"}
        if len(rating_comment) > 500:
            return {"success": False, "error": "COMMENT_TOO_LONG"}

    old = ticket.status
    ticket.status = "CLOSED"

    if rating is not None:
        ticket.rating = rating
        ticket.rating_comment = (rating_comment or "").strip() or None
        ticket.rated_at = datetime.utcnow()

    note = "Người báo xác nhận sự cố đã xử lý xong."
    if rating is not None:
        note += f" Đánh giá: {rating}/5 sao."
        if ticket.rating_comment:
            note += f" Nhận xét: {ticket.rating_comment}"

    db.add(TicketHistory(
        id=f"HIS-{uuid.uuid4()}",
        ticket_id=ticket.id,
        from_status=old,
        to_status="CLOSED",
        note=note,
        updated_by=user_id,
    ))
    db.commit()

    return {
        "success": True,
        "data": {
            "ticket_id": ticket.id,
            "old_status": old,
            "new_status": ticket.status,
            "rating": ticket.rating,
        },
    }


def reject_user_ticket(db, user_id, ticket_id, reason):
    """
    User reject: WAITING_CONFIRM → RE_PROCESS, priority lên HIGH.
    """
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id, Ticket.reporter_id == user_id)
        .first()
    )
    if ticket is None:
        return None

    if ticket.status != "WAITING_CONFIRM":
        return {"success": False, "error": "TICKET_NOT_WAITING_CONFIRM"}

    if not reason or not reason.strip():
        return {"success": False, "error": "REASON_REQUIRED"}

    old = ticket.status
    ticket.status = "RE_PROCESS"
    ticket.priority = "HIGH"
    ticket.assigned_to = None

    db.add(TicketHistory(
        id=f"HIS-{uuid.uuid4()}",
        ticket_id=ticket.id,
        from_status=old,
        to_status="RE_PROCESS",
        note=f"Người báo từ chối nghiệm thu. Lý do: {reason.strip()}",
        updated_by=user_id,
    ))
    db.commit()

    return {
        "success": True,
        "data": {
            "ticket_id": ticket.id,
            "old_status": old,
            "new_status": ticket.status,
            "new_priority": ticket.priority,
        },
    }