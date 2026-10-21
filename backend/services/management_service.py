from models.user import User
from models.team import Team
from models.ticket import Ticket
from models.room import Room
from models.building import Building
from models.ticket_history import TicketHistory
import uuid
from sqlalchemy import func



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
        .order_by(Ticket.created_at.desc())
        .all()
    )

    result = []

    for ticket in tickets:

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

        result.append({
            "id": ticket.id,
            "title": ticket.title,
            "category": ticket.category,
            "priority": ticket.priority,
            "status": ticket.status,
            "created_at": ticket.created_at,

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
            }
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

def list_team_tickets(db, team_id):
    tickets = (
        db.query(Ticket)
        .filter(Ticket.assigned_team_id == team_id)
        .order_by(Ticket.created_at.desc())
        .all()
    )
    result = []
    for t in tickets:
        room = db.query(Room).filter(Room.id == t.room_id).first()
        building = None
        if room is not None:
            building = db.query(Building).filter(Building.id == room.building_id).first()

        tech = None
        if t.assigned_to is not None:
            tech = db.query(User).filter(User.id == t.assigned_to).first()

        result.append({
            "id": t.id,
            "title": t.title,
            "category": t.category,
            "priority": t.priority,
            "status": t.status,
            "assigned_to": {"id": tech.id, "name": tech.name} if tech else None,
            "location": {
                "building": {"id": building.id, "name": building.name} if building else None,
                "room": {"id": room.id, "code": room.code, "name": room.name} if room else None,
            },
            "created_at": t.created_at,
        })
    return result
