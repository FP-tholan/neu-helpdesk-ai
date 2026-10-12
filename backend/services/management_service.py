from models.user import User
from models.team import Team
from models.ticket import Ticket
from models.room import Room
from models.building import Building
from models.ticket_history import TicketHistory
import uuid


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
            Ticket.status.in_(["ASSIGNED", "IN_PROGRESS"])
        )
        .all()
    )

    assigned = 0
    in_progress = 0

    for ticket in tickets:
        if ticket.status == "ASSIGNED":
            assigned += 1

        elif ticket.status == "IN_PROGRESS":
            in_progress += 1

    return {
        "assigned": assigned,
        "in_progress": in_progress,
        "total_open": assigned + in_progress
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
        technician["workload"] = get_technician_workload(
            db,
            technician["id"]
        )

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
        to_status="ASSIGNED",
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