from flask import Blueprint, jsonify, request, session

from database.db import SessionLocal
from models.user import User
from models.ticket import Ticket
from models.team import Team
from models.room import Room
from models.building import Building
from models.ticket_history import TicketHistory
import uuid


admin_bp = Blueprint("admin", __name__)


def require_admin():
    if session.get("user_id") is None:
        return jsonify({"success": False, "error": "UNAUTHORIZED"}), 401
    if session.get("role") != "ADMIN":
        return jsonify({"success": False, "error": "FORBIDDEN"}), 403
    return None


@admin_bp.get("/tickets")
def admin_list_tickets():
    err = require_admin()
    if err:
        return err

    db = SessionLocal()
    try:
        tickets = (
            db.query(Ticket)
            .order_by(Ticket.created_at.desc())
            .all()
        )
        items = []
        for t in tickets:
            room = db.query(Room).filter(Room.id == t.room_id).first()
            building = None
            if room:
                building = db.query(Building).filter(Building.id == room.building_id).first()
            team = db.query(Team).filter(Team.id == t.assigned_team_id).first()
            items.append({
                "id": t.id,
                "title": t.title,
                "category": t.category,
                "priority": t.priority,
                "status": t.status,
                "assigned_team": {"id": team.id, "code": team.code, "name": team.name} if team else None,
                "assigned_to": t.assigned_to,
                "location": {
                    "building": {"id": building.id, "name": building.name} if building else None,
                    "room": {"id": room.id, "code": room.code, "name": room.name} if room else None,
                },
                "created_at": t.created_at,
            })
        return jsonify({"success": True, "data": items}), 200
    finally:
        db.close()


@admin_bp.patch("/tickets/<ticket_id>")
def admin_update_ticket(ticket_id):
    err = require_admin()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    db = SessionLocal()
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if ticket is None:
            return jsonify({"success": False, "error": "TICKET_NOT_FOUND"}), 404

        changed = []

        if "priority" in data and data["priority"] != ticket.priority:
            old = ticket.priority
            ticket.priority = data["priority"]
            changed.append(f"priority: {old} → {data['priority']}")

        if "status" in data and data["status"] != ticket.status:
            old = ticket.status
            ticket.status = data["status"]
            changed.append(f"status: {old} → {data['status']}")

        if "assigned_team_id" in data and data["assigned_team_id"] != ticket.assigned_team_id:
            old = ticket.assigned_team_id
            ticket.assigned_team_id = data["assigned_team_id"]
            changed.append(f"team: {old} → {data['assigned_team_id']}")

        if changed:
            db.add(TicketHistory(
                id=f"HIS-{uuid.uuid4()}",
                ticket_id=ticket.id,
                from_status=ticket.status,
                to_status=ticket.status,
                note="Admin cập nhật: " + "; ".join(changed),
                updated_by=session.get("user_id"),
            ))
            db.commit()

        return jsonify({"success": True, "data": {"id": ticket.id, "changes": changed}}), 200
    finally:
        db.close()


@admin_bp.get("/statistics")
def admin_statistics():
    err = require_admin()
    if err:
        return err

    db = SessionLocal()
    try:
        tickets = db.query(Ticket).all()
        by_status = {}
        by_category = {}
        by_team = {}
        for t in tickets:
            by_status[t.status] = by_status.get(t.status, 0) + 1
            by_category[t.category] = by_category.get(t.category, 0) + 1
            by_team[t.assigned_team_id] = by_team.get(t.assigned_team_id, 0) + 1

        return jsonify({
            "success": True,
            "data": {
                "total": len(tickets),
                "by_status": by_status,
                "by_category": by_category,
                "by_team": by_team,
            },
        }), 200
    finally:
        db.close()