from models.user import User
from models.team import Team
from models.ticket import Ticket
from models.ticket_history import TicketHistory
from models.room import Room
from models.building import Building
from datetime import datetime
import uuid

def get_technician_info(db, technician_id):
    technician = (
        db.query(User)
        .filter(
            User.id == technician_id,
            User.role == "TECHNICIAN"
        )
        .first()
    )

    if technician is None:
        return None

    team = (
        db.query(Team)
        .filter(Team.id == technician.team_id)
        .first()
    )

    return {
        "id": technician.id,
        "name": technician.name,
        "email": technician.email,
        "team": {
            "id": team.id,
            "code": team.code,
            "name": team.name
        } if team else None
    }


def get_workload_stats(db, technician_id):
    technician = (
        db.query(User)
        .filter(
            User.id == technician_id,
            User.role == "TECHNICIAN"
        )
        .first()
    )

    if technician is None:
        return None

    tickets = (
        db.query(Ticket)
        .filter(
            (Ticket.assigned_team_id == technician.team_id)
            | (Ticket.assigned_to == technician_id)
        )
        .all()
    )

    stats = {
        "assigned": 0,
        "in_progress": 0,
        "waiting_confirm": 0,
        "re_process": 0
    }

    for ticket in tickets:
        if ticket.status == "ASSIGNED":
            stats["assigned"] += 1

        elif ticket.status == "IN_PROGRESS":
            stats["in_progress"] += 1

        elif ticket.status == "WAITING_CONFIRM":
            stats["waiting_confirm"] += 1

        elif ticket.status == "RE_PROCESS":
            stats["re_process"] += 1

    return stats


def get_technician_ticket_queue(db, technician_id):
    technician = (
        db.query(User)
        .filter(
            User.id == technician_id,
            User.role == "TECHNICIAN"
        )
        .first()
    )

    if technician is None:
        return None

    tickets = (
        db.query(Ticket)
        .filter(
            (Ticket.assigned_team_id == technician.team_id)
            | (Ticket.assigned_to == technician_id)
        )
        .order_by(Ticket.created_at.desc())
        .all()
    )

    result = []

    for ticket in tickets:

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

        result.append({
            "id": ticket.id,
            "title": ticket.title,

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

            "priority": ticket.priority,
            "status": ticket.status,
            "assigned_to": ticket.assigned_to, 
            "created_at": ticket.created_at
        })

    return result


def get_technician_dashboard(db, technician_id):
    tech_info = get_technician_info(
        db,
        technician_id
    )

    if tech_info is None:
        return None

    workload_stats = get_workload_stats(
        db,
        technician_id
    )

    ticket_queue = get_technician_ticket_queue(
        db,
        technician_id
    )

    return {
        "tech_info": tech_info,
        "workload_stats": workload_stats,
        "ticket_queue": ticket_queue
    }


def get_technician_ticket_detail(db, technician_id, ticket_id):

    technician = (
        db.query(User)
        .filter(
            User.id == technician_id,
            User.role == "TECHNICIAN"
        )
        .first()
    )

    if technician is None:
        return None

    ticket = (
        db.query(Ticket)
        .filter(
            Ticket.id == ticket_id,
            (
                (Ticket.assigned_team_id == technician.team_id)
                |
                (Ticket.assigned_to == technician_id)
            )
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
        .filter(
            TicketHistory.ticket_id == ticket.id
        )
        .order_by(
            TicketHistory.created_at.asc()
        )
        .all()
    )

    return {
        "ticket_summary": {
            "id": ticket.id,
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

            "description": ticket.description,
            "priority": ticket.priority,
            "status": ticket.status,
            "created_at": ticket.created_at
        },

        "internal_notes": [],

        "resolution_details": None,

        "activity_log": [
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


def accept_technician_ticket(db, technician_id, ticket_id):
    technician = (
        db.query(User)
        .filter(
            User.id == technician_id,
            User.role == "TECHNICIAN"
        )
        .first()
    )

    if technician is None:
        return None

    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if ticket is None:
        return None

    # 1. Ticket phải thuộc Team của Technician
    if ticket.assigned_team_id != technician.team_id:
        return {
            "success": False,
            "error": "TICKET_NOT_ASSIGNED_TO_TEAM"
        }

    # 2. Ticket phải đang chờ nhận
    if ticket.status not in ("ASSIGNED", "RE_PROCESS"):
        return {"success": False, "error": "TICKET_NOT_ASSIGNABLE"}

    # 3. Nếu đã có KTV KHÁC đứng tên xử lý → chặn
    if ticket.assigned_to is not None and ticket.assigned_to != technician_id:
        return {
            "success": False,
            "error": "TICKET_ALREADY_ASSIGNED"
        }

    old_status = ticket.status

    ticket.assigned_to = technician_id
    ticket.status = "IN_PROGRESS"

    history = TicketHistory(
        id=f"HIS-{uuid.uuid4()}",
        ticket_id=ticket.id,
        from_status=old_status,
        to_status="IN_PROGRESS",
        note="Technician nhận xử lý ticket.",
        updated_by=technician_id
    )

    db.add(history)
    db.commit()

    return {
        "success": True,
        "ticket_id": ticket.id,
        "assigned_to": ticket.assigned_to,
        "old_status": old_status,
        "new_status": ticket.status
    }


def update_technician_progress(
    db,
    technician_id,
    ticket_id,
    note
):
    technician = (
        db.query(User)
        .filter(
            User.id == technician_id,
            User.role == "TECHNICIAN"
        )
        .first()
    )

    if technician is None:
        return None

    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if ticket is None:
        return None

    # Ticket phải thuộc Team của Technician
    if ticket.assigned_team_id != technician.team_id:
        return {
            "success": False,
            "error": "TICKET_NOT_ASSIGNED_TO_TEAM"
        }

    # Technician phải là người đang xử lý ticket
    if ticket.assigned_to != technician_id:
        return {
            "success": False,
            "error": "TICKET_NOT_ASSIGNED_TO_TECHNICIAN"
        }

    # Chỉ cho cập nhật khi đang xử lý
    if ticket.status not in ("IN_PROGRESS", "RE_PROCESS"):
        return {"success": False, "error": "TICKET_NOT_IN_PROGRESS"}

    # Bắt buộc có nội dung cập nhật
    if not note or not note.strip():
        return {
            "success": False,
            "error": "NOTE_REQUIRED"
        }

    history = TicketHistory(
        id=f"HIS-{uuid.uuid4()}",
        ticket_id=ticket.id,
        from_status=ticket.status,
        to_status=ticket.status,
        note=note.strip(),
        updated_by=technician_id
    )

    db.add(history)
    db.commit()

    return {
        "success": True,
        "ticket_id": ticket.id,
        "status": ticket.status,
        "note": note.strip()
    }


def resolve_technician_ticket(
    db,
    technician_id,
    ticket_id,
    cause,
    solution
):
    technician = (
        db.query(User)
        .filter(User.id == technician_id)
        .first()
    )

    if technician is None:
        return None

    if technician.role != "TECHNICIAN":
        return {
            "success": False,
            "error": "FORBIDDEN"
        }

    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if ticket is None:
        return None

    if ticket.assigned_team_id != technician.team_id:
        return {
            "success": False,
            "error": "TICKET_NOT_ASSIGNED_TO_TEAM"
        }

    if ticket.assigned_to != technician_id:
        return {
            "success": False,
            "error": "TICKET_NOT_ASSIGNED_TO_TECHNICIAN"
        }

    if ticket.status != "IN_PROGRESS":
        return {
            "success": False,
            "error": "TICKET_NOT_IN_PROGRESS"
        }

    if not cause or not cause.strip():
        return {
            "success": False,
            "error": "CAUSE_REQUIRED"
        }

    if not solution or not solution.strip():
        return {
            "success": False,
            "error": "SOLUTION_REQUIRED"
        }

    old_status = ticket.status

    ticket.status = "WAITING_CONFIRM"

    note = (
        f"Nguyên nhân: {cause.strip()}\n"
        f"Giải pháp: {solution.strip()}"
    )

    history = TicketHistory(
        id=f"HIS-{uuid.uuid4()}",
        ticket_id=ticket.id,
        from_status=old_status,
        to_status="WAITING_CONFIRM",
        note=note,
        updated_by=technician_id
    )

    db.add(history)
    db.commit()

    return {
        "success": True,
        "ticket_id": ticket.id,
        "old_status": old_status,
        "new_status": ticket.status,
        "cause": cause.strip(),
        "solution": solution.strip()
    }


def escalate_technician_ticket(
    db,
    technician_id,
    ticket_id,
    new_team_id,
    reason
):
    technician = (
        db.query(User)
        .filter(
            User.id == technician_id,
            User.role == "TECHNICIAN"
        )
        .first()
    )

    if technician is None:
        return {
            "success": False,
            "error": "TECHNICIAN_NOT_FOUND"
        }

    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if ticket is None:
        return None

    # Ticket phải thuộc team hiện tại của Technician
    if ticket.assigned_team_id != technician.team_id:
        return {
            "success": False,
            "error": "TICKET_NOT_ASSIGNED_TO_TEAM"
        }

    # Ticket phải được chính Technician xử lý
    if ticket.assigned_to != technician_id:
        return {
            "success": False,
            "error": "TICKET_NOT_ASSIGNED_TO_TECHNICIAN"
        }

    # Chỉ ticket đang xử lý mới được Escalate
    if ticket.status != "IN_PROGRESS":
        return {
            "success": False,
            "error": "TICKET_NOT_IN_PROGRESS"
        }

    # Kiểm tra lý do
    if not reason or not reason.strip():
        return {
            "success": False,
            "error": "REASON_REQUIRED"
        }

    # Kiểm tra Team mới
    new_team = (
        db.query(Team)
        .filter(Team.id == new_team_id)
        .first()
    )

    if new_team is None:
        return {
            "success": False,
            "error": "TEAM_NOT_FOUND"
        }

    # Không được chuyển sang chính Team hiện tại
    if new_team_id == ticket.assigned_team_id:
        return {
            "success": False,
            "error": "SAME_TEAM"
        }

    old_team_id = ticket.assigned_team_id
    old_status = ticket.status

    # Chuyển Team
    ticket.assigned_team_id = new_team_id

    # Team mới chưa có Technician cụ thể
    ticket.assigned_to = None

    # Ticket quay về hàng đợi của Team mới
    ticket.status = "ASSIGNED"

    history = TicketHistory(
        id=f"HIS-{uuid.uuid4()}",
        ticket_id=ticket.id,
        from_status=old_status,
        to_status="ASSIGNED",
        note=(
            f"Escalate từ Team {old_team_id} "
            f"sang Team {new_team_id}.\n"
            f"Lý do: {reason.strip()}"
        ),
        updated_by=technician_id
    )

    db.add(history)
    db.commit()

    return {
        "success": True,
        "ticket_id": ticket.id,
        "old_team": old_team_id,
        "new_team": new_team_id,
        "old_status": old_status,
        "new_status": "ASSIGNED",
        "reason": reason.strip()
    }