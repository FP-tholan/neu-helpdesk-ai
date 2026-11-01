from datetime import datetime
from models.user import User
from models.team import Team
from models.ticket import Ticket
from models.room import Room
from models.building import Building
from models.ticket_history import TicketHistory

import uuid
from sqlalchemy import func
from services.auto_dispatch_service import (
    get_effective_priority,
    sort_tickets_by_effective_priority,
)
from services.system_setting_service import (
    PRIORITY_ORDER,
    get_dispatch_mode,
    set_dispatch_mode,
)


def get_management_team(db, team_id):
    team = (
        db.query(Team)
        .filter(Team.id == team_id)
        .first()
    )

    if team is None:
        return None

    return {
        "id": team.id,
        "code": team.code,
        "name": team.name
    }


def get_management_technicians(db, team_id):
    technicians = (
        db.query(User)
        .filter(
            User.role == "TECHNICIAN",
            User.team_id == team_id
        )
        .order_by(User.name.asc())
        .all()
    )

    result = []

    for technician in technicians:
        result.append({
            "id": technician.id,
            "name": technician.name,
            "email": technician.email,
            "is_on_duty": technician.is_on_duty
        })

    return result


def get_technician_workload(db, technician_id):
    tickets = (
        db.query(Ticket)
        .filter(
            Ticket.assigned_to == technician_id,
            Ticket.status.in_(["ASSIGNED", "IN_PROGRESS", "RE_PROCESS"]),
        )
        .all()
    )

    assigned = sum(1 for t in tickets if t.status == "ASSIGNED")
    in_progress = sum(1 for t in tickets if t.status in ("IN_PROGRESS", "RE_PROCESS"))

    return {
        "assigned": assigned,
        "in_progress": in_progress,
        "total_open": assigned + in_progress,
    }

def get_technician_rating_stats(db, technician_id):
    row = (
        db.query(
            func.avg(Ticket.rating).label("avg"),
            func.count(Ticket.rating).label("count"),
        )
        .filter(
            Ticket.assigned_to == technician_id,
            Ticket.status == "CLOSED",
            Ticket.rating.isnot(None),
        )
        .one()
    )
    avg = float(row.avg) if row.avg is not None else None
    return {
        "average": round(avg, 1) if avg is not None else None,
        "count": int(row.count or 0),
    }
def get_management_dashboard(db, team_id):
    team = get_management_team(db, team_id)

    if team is None:
        return None

    technicians = get_management_technicians(
        db,
        team_id
    )

    for technician in technicians:
        technician["workload"] = get_technician_workload(db, technician["id"])
        rs = get_technician_rating_stats(db, technician["id"])
        technician["rating"] = rs["average"]
        technician["rating_count"] = rs["count"]

    unassigned_tickets = (
        db.query(Ticket)
        .filter(
            Ticket.assigned_team_id == team_id,
            Ticket.assigned_to.is_(None),
            Ticket.status == "ASSIGNED"
        )
        .count()
    )

    active_techs = sum(
    1 for technician in technicians
    if technician["is_on_duty"]
)

    return {
    "team": team,
    "stats": {
        "total_techs": len(technicians),
        "active_techs": active_techs,
        "unassigned_tickets": unassigned_tickets
    },
    "technicians": technicians
}


def get_unassigned_tickets(db, team_id):
    tickets = (
        db.query(Ticket)
        .filter(
            Ticket.assigned_team_id == team_id,
            Ticket.assigned_to.is_(None),
            Ticket.status == "ASSIGNED"
        )
        .all()
    )
    tickets = sort_tickets_by_effective_priority(tickets)

    result = []
    for ticket in tickets:
        room = db.query(Room).filter(Room.id == ticket.room_id).first()
        building = (
            db.query(Building).filter(Building.id == room.building_id).first()
            if room else None
        )
        result.append({
            "id": ticket.id,
            "title": ticket.title,
            "category": ticket.category,
            "priority": ticket.priority,
            "effective_priority": get_effective_priority(ticket),
            "status": ticket.status,
            "created_at": ticket.created_at,
            "location": {
                "building": (
                    {"id": building.id, "code": building.code, "name": building.name}
                    if building else None
                ),
                "room": (
                    {"id": room.id, "code": room.code, "name": room.name}
                    if room else None
                ),
            },
        })
    return result


def assign_ticket_to_technician(
    db,
    ticket_id,
    technician_id,
    manager_id
):
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if ticket is None:
        return {
            "success": False,
            "error": "TICKET_NOT_FOUND"
        }

    technician = (
        db.query(User)
        .filter(User.id == technician_id)
        .first()
    )

    if technician is None:
        return {
            "success": False,
            "error": "TECHNICIAN_NOT_FOUND"
        }

    if technician.role != "TECHNICIAN":
        return {
            "success": False,
            "error": "INVALID_TECHNICIAN"
        }

    if technician.team_id != ticket.assigned_team_id:
        return {
            "success": False,
            "error": "TECHNICIAN_NOT_IN_TICKET_TEAM"
        }

    if ticket.status != "ASSIGNED":
        return {
            "success": False,
            "error": "TICKET_NOT_ASSIGNABLE"
        }

    if ticket.assigned_to is not None:
        return {
            "success": False,
            "error": "TICKET_ALREADY_ASSIGNED"
        }

    old_status = ticket.status

    ticket.assigned_to = technician_id

    history = TicketHistory(
        id=f"HIS-{uuid.uuid4()}",
        ticket_id=ticket.id,
        from_status=old_status,
        to_status=old_status,
        note=f"Ticket được phân công cho kỹ thuật viên {technician.name}.",
        updated_by=manager_id
    )

    db.add(history)
    db.commit()

    return {
        "success": True,
        "data": {
            "ticket_id": ticket.id,
            "assigned_to": technician.id,
            "technician_name": technician.name,
            "status": ticket.status
        }
    }


def reassign_ticket_to_technician(
    db,
    ticket_id,
    new_technician_id,
    manager_id
):
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if ticket is None:
        return {
            "success": False,
            "error": "TICKET_NOT_FOUND"
        }

    new_technician = (
        db.query(User)
        .filter(User.id == new_technician_id)
        .first()
    )

    if new_technician is None:
        return {
            "success": False,
            "error": "TECHNICIAN_NOT_FOUND"
        }

    if new_technician.role != "TECHNICIAN":
        return {
            "success": False,
            "error": "INVALID_TECHNICIAN"
        }

    if new_technician.team_id != ticket.assigned_team_id:
        return {
            "success": False,
            "error": "TECHNICIAN_NOT_IN_TICKET_TEAM"
        }

    if ticket.assigned_to is None:
        return {
            "success": False,
            "error": "TICKET_NOT_ASSIGNED"
        }

    if ticket.assigned_to == new_technician_id:
        return {
            "success": False,
            "error": "SAME_TECHNICIAN"
        }

    old_technician_id = ticket.assigned_to

    old_technician = (
        db.query(User)
        .filter(User.id == old_technician_id)
        .first()
    )

    ticket.assigned_to = new_technician_id

    history = TicketHistory(
        id=f"HIS-{uuid.uuid4()}",
        ticket_id=ticket.id,
        from_status=ticket.status,
        to_status=ticket.status,
        note=(
            f"Ticket được chuyển từ "
            f"{old_technician.name if old_technician else old_technician_id} "
            f"sang {new_technician.name}."
        ),
        updated_by=manager_id
    )

    db.add(history)
    db.commit()

    return {
        "success": True,
        "data": {
            "ticket_id": ticket.id,
            "old_assigned_to": old_technician_id,
            "assigned_to": new_technician.id,
            "technician_name": new_technician.name,
            "status": ticket.status
        }
    }


def update_technician_duty_status(
    db,
    technician_id,
    is_on_duty
):
    technician = (
        db.query(User)
        .filter(User.id == technician_id)
        .first()
    )

    if technician is None:
        return {
            "success": False,
            "error": "TECHNICIAN_NOT_FOUND"
        }

    if technician.role != "TECHNICIAN":
        return {
            "success": False,
            "error": "INVALID_TECHNICIAN"
        }

    if not isinstance(is_on_duty, bool):
        return {
            "success": False,
            "error": "INVALID_DUTY_STATUS"
        }

    technician.is_on_duty = is_on_duty

    db.commit()

    return {
        "success": True,
        "data": {
            "technician_id": technician.id,
            "technician_name": technician.name,
            "is_on_duty": technician.is_on_duty
        }
    }
def list_team_technicians(db, team_id):
    techs = (
        db.query(User)
        .filter(User.role == "TECHNICIAN", User.team_id == team_id)
        .order_by(User.name.asc())
        .all()
    )
    result = []
    for t in techs:
        rs = get_technician_rating_stats(db, t.id)
        result.append({
            "id": t.id,
            "name": t.name,
            "email": t.email,
            "team_id": t.team_id,
            "is_on_duty": t.is_on_duty,
            "rating": rs["average"],
            "rating_count": rs["count"],
        })
    return result


def create_team_technician(db, team_id, username, email, password, name):
    import uuid
    from werkzeug.security import generate_password_hash

    tech = User(
        id=f"USR_TECH_{uuid.uuid4().hex[:8].upper()}",
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        name=name,
        role="TECHNICIAN",
        team_id=team_id,
        is_locked=False,
        is_on_duty=True,
    )
    db.add(tech)
    db.commit()
    return tech

def _status_rank(status: str) -> int:
    """WAITING_CONFIRM=0 (ưu tiên xử lý), active=1, đóng/hủy=2."""
    if status == "WAITING_CONFIRM":
        return 0
    if status in ("NEW", "ASSIGNED", "IN_PROGRESS", "RE_PROCESS"):
        return 1
    if status in ("CLOSED", "CANCELLED"):
        return 2
    return 3
def list_team_tickets(db, team_id):
    tickets = (
        db.query(Ticket)
        .filter(Ticket.assigned_team_id == team_id)
        .all()
    )

    # Sort 2 cấp: status trước, rồi effective_priority, rồi created_at
    from services.auto_dispatch_service import (
        get_effective_priority,
        priority_rank,
    )
    now = datetime.utcnow()
    tickets.sort(key=lambda t: (
        _status_rank(t.status),
        -priority_rank(get_effective_priority(t, now)),
        t.created_at or now,
    ))

    result = []
    for t in tickets:
        room = db.query(Room).filter(Room.id == t.room_id).first()
        building = (
            db.query(Building).filter(Building.id == room.building_id).first()
            if room else None
        )
        tech = (
            db.query(User).filter(User.id == t.assigned_to).first()
            if t.assigned_to else None
        )
        result.append({
            "id": t.id,
            "title": t.title,
            "category": t.category,
            "priority": t.priority,
            "effective_priority": get_effective_priority(t),
            "status": t.status,
            "assigned_to": {"id": tech.id, "name": tech.name} if tech else None,
            "location": {
                "building": (
                    {"id": building.id, "name": building.name}
                    if building else None
                ),
                "room": (
                    {"id": room.id, "code": room.code, "name": room.name}
                    if room else None
                ),
            },
            "created_at": t.created_at,
        })
    return result
# ═══════════════════════════════════════════════════════════
# TEAM LEAD — VERIFY / REJECT (chỉ dùng mode Manual)
# ═══════════════════════════════════════════════════════════

def team_lead_verify_ticket(db, team_id, ticket_id, manager_id):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket is None:
        return {"success": False, "error": "TICKET_NOT_FOUND"}
    if ticket.assigned_team_id != team_id:
        return {"success": False, "error": "FORBIDDEN"}
    if ticket.status != "WAITING_CONFIRM":
        return {"success": False, "error": "TICKET_NOT_WAITING_CONFIRM"}

    old = ticket.status
    ticket.status = "CLOSED"
    ticket.verified_by = manager_id
    ticket.verified_at = datetime.utcnow()

    db.add(TicketHistory(
        id=f"HIS-{uuid.uuid4()}",
        ticket_id=ticket.id,
        from_status=old,
        to_status="CLOSED",
        note="Team Lead nghiệm thu, đóng ticket.",
        updated_by=manager_id,
    ))
    db.commit()
    return {"success": True, "data": {"ticket_id": ticket.id, "new_status": "CLOSED"}}


def team_lead_reject_ticket(db, team_id, ticket_id, manager_id, reason):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket is None:
        return {"success": False, "error": "TICKET_NOT_FOUND"}
    if ticket.assigned_team_id != team_id:
        return {"success": False, "error": "FORBIDDEN"}
    if ticket.status != "WAITING_CONFIRM":
        return {"success": False, "error": "TICKET_NOT_WAITING_CONFIRM"}
    if not reason or not reason.strip():
        return {"success": False, "error": "REASON_REQUIRED"}

    old = ticket.status
    ticket.status = "RE_PROCESS"
    ticket.priority = "HIGH"
    ticket.assigned_to = None
    ticket.verified_by = manager_id
    ticket.verified_at = datetime.utcnow()

    db.add(TicketHistory(
        id=f"HIS-{uuid.uuid4()}",
        ticket_id=ticket.id,
        from_status=old,
        to_status="RE_PROCESS",
        note=f"Team Lead từ chối nghiệm thu. Lý do: {reason.strip()}",
        updated_by=manager_id,
    ))
    db.commit()
    return {"success": True, "data": {"ticket_id": ticket.id, "new_status": "RE_PROCESS"}}


def team_lead_set_priority(db, team_id, ticket_id, manager_id, priority):
    if priority not in PRIORITY_ORDER:
        return {"success": False, "error": "INVALID_PRIORITY"}
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket is None:
        return {"success": False, "error": "TICKET_NOT_FOUND"}
    if ticket.assigned_team_id != team_id:
        return {"success": False, "error": "FORBIDDEN"}

    if ticket.priority == priority:
        return {"success": True, "data": {"ticket_id": ticket.id, "priority": priority}}

    old = ticket.priority
    ticket.priority = priority
    ticket.updated_at = datetime.utcnow()   # reset bộ đếm decay

    db.add(TicketHistory(
        id=f"HIS-{uuid.uuid4()}",
        ticket_id=ticket.id,
        from_status=ticket.status,
        to_status=ticket.status,
        note=f"Team Lead đổi priority: {old} → {priority}.",
        updated_by=manager_id,
    ))
    db.commit()
    return {"success": True, "data": {"ticket_id": ticket.id, "priority": priority}}


def get_team_lead_settings(db):
    return {"dispatch_mode": get_dispatch_mode(db)}


def update_team_lead_settings(db, mode):
    try:
        set_dispatch_mode(db, mode)
    except ValueError as e:
        return {"success": False, "error": str(e)}
    return {"success": True, "data": {"dispatch_mode": mode}}