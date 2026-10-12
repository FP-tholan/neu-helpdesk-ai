from models.user import User
from models.ticket import Ticket


def get_user_info(db, user_id):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        return None

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email
    }


def get_ticket_stats(db, user_id):
    tickets = (
        db.query(Ticket)
        .filter(Ticket.reporter_id == user_id)
        .all()
    )

    stats = {
        "open": 0,
        "in_progress": 0,
        "resolved": 0,
        "closed": 0
    }

    for ticket in tickets:
        status = ticket.status.lower()

        if status == "assigned":
            stats["open"] += 1
        elif status in stats:
            stats[status] += 1

    return stats


def get_recent_tickets(db, user_id):
    tickets = (
        db.query(Ticket)
        .filter(Ticket.reporter_id == user_id)
        .order_by(Ticket.created_at.desc())
        .all()
    )

    return [
        {
            "id": ticket.id,
            "title": ticket.title,
            "category": ticket.category,
            "status": ticket.status,
            "created_at": ticket.created_at
        }
        for ticket in tickets
    ]


def get_user_dashboard(db, user_id):
    user_info = get_user_info(db, user_id)

    if user_info is None:
        return None

    return {
        "user_info": user_info,
        "ticket_stats": get_ticket_stats(db, user_id),
        "recent_tickets": get_recent_tickets(db, user_id)
    }