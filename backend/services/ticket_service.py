import logging
import threading
import uuid
from datetime import datetime

from models.ticket import Ticket
from models.ticket_history import TicketHistory
from models.user import User
from models.room import Room
from models.building import Building
from models.team import Team
from models.dispatch_rule import DispatchRule

from database.db import SessionLocal
from services.system_setting_service import get_dispatch_mode
from services.auto_dispatch_service import (
    ai_determine_priority,
    find_best_technician,
    get_effective_priority,
)

logger = logging.getLogger(__name__)

_PRIORITY_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

# Keyword-based priority — deterministic, không phụ thuộc AI
_KW_CRITICAL = (
    "cháy", "khét", "khói", "nổ", "sập",
    "điện giật", "rò điện", "ngập", "bốc lửa",
)
_KW_HIGH = ("đang học", "đang thi", "khẩn", "gấp", "ngay")
_KW_LOW  = ("nhẹ", "không gấp", "khi nào cũng được")


ALLOWED_PRIORITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}

ALLOWED_CATEGORIES = {
    "PROJECTOR", "COMPUTER", "WIFI", "MICROPHONE",
    "AIR_CONDITIONER", "ELECTRICITY", "FURNITURE",
    "CLEANING", "OTHER",
}

def _keyword_priority(title: str, description: str) -> str:
    """Priority dựa trên keyword — luôn chạy được, không cần AI."""
    text = f"{title} {description}".lower()
    if any(k in text for k in _KW_CRITICAL):
        return "CRITICAL"
    if any(k in text for k in _KW_HIGH):
        return "HIGH"
    if any(k in text for k in _KW_LOW):
        return "LOW"
    return "MEDIUM"


def _combine_priority(a: str, b: str) -> str:
    """Trả priority cao hơn — KHÔNG BAO GIỜ downgrade."""
    if a not in _PRIORITY_ORDER:
        return b if b in _PRIORITY_ORDER else "MEDIUM"
    if b not in _PRIORITY_ORDER:
        return a
    return _PRIORITY_ORDER[max(_PRIORITY_ORDER.index(a), _PRIORITY_ORDER.index(b))]


def _async_ai_priority_update(
    ticket_id: str,
    title: str,
    description: str,
    metadata: dict,
    kw_prio: str,
):
    """
    Chạy trong background thread — không block user request.
    Chỉ UPDATE priority nếu AI cho giá trị CAO HƠN keyword.
    """
    try:
        ai_prio = ai_determine_priority(title, description, metadata)
        if not ai_prio:
            return

        final_prio = _combine_priority(ai_prio, kw_prio)
        if final_prio == kw_prio:
            return  # Không cần update

        db = SessionLocal()
        try:
            ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if ticket is None or ticket.priority == final_prio:
                return

            old_prio = ticket.priority
            ticket.priority = final_prio
            db.add(TicketHistory(
                id=f"HIS-{uuid.uuid4()}",
                ticket_id=ticket.id,
                from_status=ticket.status,
                to_status=ticket.status,
                note=f"Hệ thống AI nâng priority: {old_prio} → {final_prio}.",
                updated_by="SYSTEM_AI",
            ))
            db.commit()
            logger.info(
                "AI priority boosted %s: %s → %s",
                ticket_id, old_prio, final_prio,
            )
        finally:
            db.close()
    except Exception as e:
        logger.warning("async AI priority failed for %s: %s", ticket_id, e)
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
    category, description,
):
    if not title or not title.strip():
        return {"success": False, "error": "TITLE_REQUIRED"}
    if not description or not description.strip():
        return {"success": False, "error": "DESCRIPTION_REQUIRED"}
    if category not in ALLOWED_CATEGORIES:
        return {"success": False, "error": "INVALID_CATEGORY"}

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

    # ── Priority theo mode ────────────────────────────────
    mode = get_dispatch_mode(db)
    kw_prio = _keyword_priority(title, description)

    if mode == 2:
        # Auto: keyword baseline trả NGAY, AI update ngầm sau
        priority = kw_prio
    else:
        # Manual: LUÔN LOW — Team Lead tự set sau
        priority = "LOW"

    # ── Tạo ticket ────────────────────────────────────────
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

    db.add(TicketHistory(
        id=f"HIS-{uuid.uuid4()}",
        ticket_id=ticket.id,
        from_status=None,
        to_status="NEW",
        note="Ticket được tạo.",
        updated_by=user_id,
    ))

    # ── Phân công theo mode ───────────────────────────────
    assigned_tech = None
    if mode == 2:
        assigned_tech = find_best_technician(db, team.id)

    ticket.status = "ASSIGNED"
    if assigned_tech is not None:
        ticket.assigned_to = assigned_tech.id
        note = (
            f"Hệ thống tự động gán về Team {team.name}, "
            f"KTV {assigned_tech.name} (workload thấp nhất)."
        )
    else:
        note = f"Hệ thống tự động gán về Team {team.name}."

    db.add(TicketHistory(
        id=f"HIS-{uuid.uuid4()}",
        ticket_id=ticket.id,
        from_status="NEW",
        to_status="ASSIGNED",
        note=note,
        updated_by=user_id,
    ))

    db.commit()

    # ── Mode 2: AI boost priority ngầm (không block user) ──
    if mode == 2 and kw_prio != "CRITICAL":
        threading.Thread(
            target=_async_ai_priority_update,
            args=(
                ticket.id, title, description,
                {
                    "room_code": room_code,
                    "building_id": building.id,
                    "category": category,
                },
                kw_prio,
            ),
            daemon=True,
        ).start()

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
            "assigned_tech": (
                {"id": assigned_tech.id, "name": assigned_tech.name}
                if assigned_tech else None
            ),
            "dispatch_mode": mode,
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
            "effective_priority": get_effective_priority(ticket),
            "status": ticket.status,
            "rating": ticket.rating,
            "rating_comment": ticket.rating_comment,
            "verified_by": ticket.verified_by,
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
def rate_user_ticket(db, user_id, ticket_id, rating, rating_comment=None):
    """
    User đánh giá chất lượng. KHÔNG đổi status ticket.
    Chỉ cho đánh giá khi KTV đã xử lý xong (WAITING_CONFIRM hoặc CLOSED).
    """
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id, Ticket.reporter_id == user_id)
        .first()
    )
    if ticket is None:
        return None

    if ticket.status not in ("WAITING_CONFIRM", "CLOSED"):
        return {"success": False, "error": "TICKET_NOT_RATEABLE"}

    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return {"success": False, "error": "INVALID_RATING"}

    if rating_comment is not None:
        if not isinstance(rating_comment, str):
            return {"success": False, "error": "INVALID_COMMENT"}
        if len(rating_comment) > 500:
            return {"success": False, "error": "COMMENT_TOO_LONG"}

    ticket.rating = rating
    ticket.rating_comment = (rating_comment or "").strip() or None
    ticket.rated_at = datetime.utcnow()

    db.add(TicketHistory(
        id=f"HIS-{uuid.uuid4()}",
        ticket_id=ticket.id,
        from_status=ticket.status,
        to_status=ticket.status,
        note=f"Người báo đánh giá {rating}/5 sao."
             + (f" Nhận xét: {ticket.rating_comment}" if ticket.rating_comment else ""),
        updated_by=user_id,
    ))
    db.commit()

    return {
        "success": True,
        "data": {
            "ticket_id": ticket.id,
            "rating": ticket.rating,
            "rating_comment": ticket.rating_comment,
        },
    }