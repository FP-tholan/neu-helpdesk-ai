from flask import Blueprint, jsonify, session, request

from database.db import SessionLocal
from models.user import User
from models.ticket import Ticket
from services.management_service import (
    get_management_dashboard,
    get_unassigned_tickets,
    assign_ticket_to_technician,
    reassign_ticket_to_technician,
    update_technician_duty_status,
    list_team_technicians,       
    create_team_technician,
    list_team_tickets
)


management_bp = Blueprint(
    "management",
    __name__
)


@management_bp.get("/dashboard")
def management_dashboard():

    user_id = session.get("user_id")
    role = session.get("role")

    if user_id is None:
        return jsonify({
            "success": False,
            "error": "UNAUTHORIZED"
        }), 401

    if role != "TEAM_LEAD":
        return jsonify({
            "success": False,
            "error": "FORBIDDEN"
        }), 403

    db = SessionLocal()

    try:
        user = db.query(User).filter(
            User.id == user_id
        ).first()

        if user is None:
            return jsonify({
                "success": False,
                "error": "USER_NOT_FOUND"
            }), 404

        team_id = user.team_id

        if team_id is None:
            return jsonify({
                "success": False,
                "error": "TEAM_NOT_FOUND"
            }), 404

        result = get_management_dashboard(
            db,
            team_id
        )

        if result is None:
            return jsonify({
                "success": False,
                "error": "TEAM_NOT_FOUND"
            }), 404

        return jsonify({
            "success": True,
            "data": result
        }), 200

    finally:
        db.close()


@management_bp.get("/tickets/unassigned")
def management_unassigned_tickets():

    user_id = session.get("user_id")
    role = session.get("role")

    if user_id is None:
        return jsonify({
            "success": False,
            "error": "UNAUTHORIZED"
        }), 401

    if role != "TEAM_LEAD":
        return jsonify({
            "success": False,
            "error": "FORBIDDEN"
        }), 403

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:
            return jsonify({
                "success": False,
                "error": "USER_NOT_FOUND"
            }), 404

        if user.team_id is None:
            return jsonify({
                "success": False,
                "error": "TEAM_NOT_FOUND"
            }), 404

        tickets = get_unassigned_tickets(
            db,
            user.team_id
        )

        return jsonify({
            "success": True,
            "data": tickets
        }), 200

    finally:
        db.close()


@management_bp.post("/tickets/<ticket_id>/assign")
def management_assign_ticket(ticket_id):

    user_id = session.get("user_id")
    role = session.get("role")

    if user_id is None:
        return jsonify({
            "success": False,
            "error": "UNAUTHORIZED"
        }), 401

    if role != "TEAM_LEAD":
        return jsonify({
            "success": False,
            "error": "FORBIDDEN"
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "INVALID_REQUEST"
        }), 400

    technician_id = data.get("technician_id")

    if not technician_id:
        return jsonify({
            "success": False,
            "error": "MISSING_TECHNICIAN_ID"
        }), 400

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:
            return jsonify({
                "success": False,
                "error": "USER_NOT_FOUND"
            }), 404

        if user.role != "TEAM_LEAD":
            return jsonify({
                "success": False,
                "error": "FORBIDDEN"
            }), 403

        if user.team_id is None:
            return jsonify({
                "success": False,
                "error": "TEAM_NOT_FOUND"
            }), 404

        ticket = (
            db.query(Ticket)
            .filter(Ticket.id == ticket_id)
            .first()
        )

        if ticket is None:
            return jsonify({
                "success": False,
                "error": "TICKET_NOT_FOUND"
            }), 404

        if ticket.assigned_team_id != user.team_id:
            return jsonify({
                "success": False,
                "error": "FORBIDDEN"
            }), 403

        result = assign_ticket_to_technician(
            db,
            ticket_id,
            technician_id,
            user_id
        )

        if not result["success"]:
            error_status = {
                "TICKET_NOT_FOUND": 404,
                "TECHNICIAN_NOT_FOUND": 404,
                "INVALID_TECHNICIAN": 400,
                "TECHNICIAN_NOT_IN_TICKET_TEAM": 400,
                "TICKET_NOT_ASSIGNABLE": 400,
                "TICKET_ALREADY_ASSIGNED": 400
            }

            return jsonify(result), error_status.get(
                result["error"],
                400
            )

        return jsonify(result), 200

    finally:
        db.close()


@management_bp.post("/tickets/<ticket_id>/reassign")
def management_reassign_ticket(ticket_id):
    user_id = session.get("user_id")
    role = session.get("role")

    if user_id is None:
        return jsonify({
            "success": False,
            "error": "UNAUTHORIZED"
        }), 401

    if role != "TEAM_LEAD":
        return jsonify({
            "success": False,
            "error": "FORBIDDEN"
        }), 403

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "error": "INVALID_REQUEST"
        }), 400

    new_technician_id = data.get("technician_id")

    if not new_technician_id:
        return jsonify({
            "success": False,
            "error": "MISSING_TECHNICIAN_ID"
        }), 400

    db = SessionLocal()

    try:
        result = reassign_ticket_to_technician(
            db=db,
            ticket_id=ticket_id,
            new_technician_id=new_technician_id,
            manager_id=user_id
        )

        if not result["success"]:
            error_status = {
                "TICKET_NOT_FOUND": 404,
                "TECHNICIAN_NOT_FOUND": 404,
                "TICKET_NOT_ASSIGNED": 400,
                "SAME_TECHNICIAN": 400,
                "INVALID_TECHNICIAN": 400,
                "TECHNICIAN_NOT_IN_TICKET_TEAM": 400
            }

            return jsonify(result), error_status.get(
                result["error"],
                400
            )

        return jsonify(result), 200

    finally:
        db.close()


@management_bp.patch("/technicians/<technician_id>/duty")
def management_update_technician_duty(technician_id):
    user_id = session.get("user_id")
    role = session.get("role")

    # 1. Kiểm tra đăng nhập
    if user_id is None:
        return jsonify({
            "success": False,
            "error": "UNAUTHORIZED"
        }), 401

    # 2. Kiểm tra quyền
    if role != "TEAM_LEAD":
        return jsonify({
            "success": False,
            "error": "FORBIDDEN"
        }), 403

    # 3. Kiểm tra dữ liệu gửi lên
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "INVALID_REQUEST"
        }), 400

    if "is_on_duty" not in data:
        return jsonify({
            "success": False,
            "error": "MISSING_DUTY_STATUS"
        }), 400

    is_on_duty = data["is_on_duty"]

    if not isinstance(is_on_duty, bool):
        return jsonify({
            "success": False,
            "error": "INVALID_DUTY_STATUS"
        }), 400

    db = SessionLocal()

    try:
        # 4. Xác minh tài khoản người quản lý
        manager = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if manager is None:
            return jsonify({
                "success": False,
                "error": "USER_NOT_FOUND"
            }), 404

        # 5. Team Lead chỉ quản lý KTV trong team của mình.
        # Admin có thể quản lý KTV thuộc team khác.
        if role == "TEAM_LEAD":
            technician = (
                db.query(User)
                .filter(User.id == technician_id)
                .first()
            )

            if technician is None:
                return jsonify({
                    "success": False,
                    "error": "TECHNICIAN_NOT_FOUND"
                }), 404

            if technician.team_id != manager.team_id:
                return jsonify({
                    "success": False,
                    "error": "TECHNICIAN_NOT_IN_TEAM"
                }), 403

        # 6. Cập nhật trạng thái
        result = update_technician_duty_status(
            db,
            technician_id,
            is_on_duty
        )

        if not result["success"]:
            error_status = {
                "TECHNICIAN_NOT_FOUND": 404,
                "INVALID_TECHNICIAN": 400,
                "INVALID_DUTY_STATUS": 400
            }

            return jsonify(result), error_status.get(
                result["error"],
                400
            )

        return jsonify(result), 200

    finally:
        db.close()
@management_bp.get("/technicians")
def management_list_technicians():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"success": False, "error": "UNAUTHORIZED"}), 401
    if session.get("role") != "TEAM_LEAD":
        return jsonify({"success": False, "error": "FORBIDDEN"}), 403

    db = SessionLocal()
    try:
        manager = db.query(User).filter(User.id == user_id).first()
        if manager is None:
            return jsonify({"success": False, "error": "USER_NOT_FOUND"}), 404
        if manager.team_id is None:
            return jsonify({"success": False, "error": "TEAM_NOT_FOUND"}), 404

        techs = list_team_technicians(db, manager.team_id)
        return jsonify({"success": True, "data": techs}), 200
    finally:
        db.close()


@management_bp.post("/technicians")
def management_create_technician():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"success": False, "error": "UNAUTHORIZED"}), 401
    if session.get("role") != "TEAM_LEAD":
        return jsonify({"success": False, "error": "FORBIDDEN"}), 403

    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip()

    if not all([username, email, password, name]):
        return jsonify({"success": False, "error": "MISSING_FIELDS"}), 400
    if len(password) < 6:
        return jsonify({"success": False, "error": "WEAK_PASSWORD"}), 400

    db = SessionLocal()
    try:
        manager = db.query(User).filter(User.id == user_id).first()
        if manager is None:
            return jsonify({"success": False, "error": "USER_NOT_FOUND"}), 404
        if manager.team_id is None:
            return jsonify({"success": False, "error": "TEAM_NOT_FOUND"}), 404

        if db.query(User).filter(User.email == email).first():
            return jsonify({"success": False, "error": "EMAIL_EXISTS"}), 409
        if db.query(User).filter(User.username == username).first():
            return jsonify({"success": False, "error": "USERNAME_EXISTS"}), 409

        tech = create_team_technician(
            db, manager.team_id, username, email, password, name
        )

        return jsonify({
            "success": True,
            "data": {
                "id": tech.id,
                "name": tech.name,
                "email": tech.email,
                "team_id": tech.team_id,
                "role": tech.role,
                "is_on_duty": tech.is_on_duty,
            },
        }), 201
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
@management_bp.get("/tickets")
def management_list_tickets():
    user_id = session.get("user_id")
    role = session.get("role")

    if user_id is None:
        return jsonify({"success": False, "error": "UNAUTHORIZED"}), 401
    if role != "TEAM_LEAD":
        return jsonify({"success": False, "error": "FORBIDDEN"}), 403

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return jsonify({"success": False, "error": "USER_NOT_FOUND"}), 404
        if user.team_id is None:
            return jsonify({"success": False, "error": "TEAM_NOT_FOUND"}), 404

        tickets = list_team_tickets(db, user.team_id)
        return jsonify({"success": True, "data": tickets}), 200
    finally:
        db.close()
# ── Settings (mode) ──────────────────────────────────────
@management_bp.get("/settings")
def management_get_settings():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"success": False, "error": "UNAUTHORIZED"}), 401
    if session.get("role") != "TEAM_LEAD":
        return jsonify({"success": False, "error": "FORBIDDEN"}), 403

    db = SessionLocal()
    try:
        from services.management_service import get_team_lead_settings
        return jsonify({"success": True, "data": get_team_lead_settings(db)}), 200
    finally:
        db.close()


@management_bp.put("/settings")
def management_update_settings():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"success": False, "error": "UNAUTHORIZED"}), 401
    if session.get("role") != "TEAM_LEAD":
        return jsonify({"success": False, "error": "FORBIDDEN"}), 403

    data = request.get_json(silent=True) or {}
    mode = data.get("dispatch_mode")
    if mode not in (1, 2):
        return jsonify({"success": False, "error": "INVALID_MODE"}), 400

    db = SessionLocal()
    try:
        from services.management_service import update_team_lead_settings
        result = update_team_lead_settings(db, mode)
        return jsonify(result), (200 if result["success"] else 400)
    finally:
        db.close()


# ── Verify / Reject / Priority ───────────────────────────
@management_bp.post("/tickets/<ticket_id>/verify")
def management_verify_ticket(ticket_id):
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"success": False, "error": "UNAUTHORIZED"}), 401
    if session.get("role") != "TEAM_LEAD":
        return jsonify({"success": False, "error": "FORBIDDEN"}), 403

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None or user.team_id is None:
            return jsonify({"success": False, "error": "TEAM_NOT_FOUND"}), 404

        from services.management_service import team_lead_verify_ticket
        result = team_lead_verify_ticket(db, user.team_id, ticket_id, user_id)
        status_map = {
            "TICKET_NOT_FOUND": 404,
            "FORBIDDEN": 403,
            "TICKET_NOT_WAITING_CONFIRM": 400,
        }
        return jsonify(result), (200 if result["success"] else status_map.get(result["error"], 400))
    finally:
        db.close()


@management_bp.post("/tickets/<ticket_id>/reject")
def management_reject_ticket(ticket_id):
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"success": False, "error": "UNAUTHORIZED"}), 401
    if session.get("role") != "TEAM_LEAD":
        return jsonify({"success": False, "error": "FORBIDDEN"}), 403

    data = request.get_json(silent=True) or {}
    reason = data.get("reason")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None or user.team_id is None:
            return jsonify({"success": False, "error": "TEAM_NOT_FOUND"}), 404

        from services.management_service import team_lead_reject_ticket
        result = team_lead_reject_ticket(db, user.team_id, ticket_id, user_id, reason)
        status_map = {
            "TICKET_NOT_FOUND": 404,
            "FORBIDDEN": 403,
            "TICKET_NOT_WAITING_CONFIRM": 400,
            "REASON_REQUIRED": 400,
        }
        return jsonify(result), (200 if result["success"] else status_map.get(result["error"], 400))
    finally:
        db.close()


@management_bp.patch("/tickets/<ticket_id>/priority")
def management_set_priority(ticket_id):
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"success": False, "error": "UNAUTHORIZED"}), 401
    if session.get("role") != "TEAM_LEAD":
        return jsonify({"success": False, "error": "FORBIDDEN"}), 403

    data = request.get_json(silent=True) or {}
    priority = (data.get("priority") or "").upper()

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None or user.team_id is None:
            return jsonify({"success": False, "error": "TEAM_NOT_FOUND"}), 404

        from services.management_service import team_lead_set_priority
        result = team_lead_set_priority(
            db, user.team_id, ticket_id, user_id, priority,
        )
        status_map = {
            "TICKET_NOT_FOUND": 404,
            "FORBIDDEN": 403,
            "INVALID_PRIORITY": 400,
        }
        return jsonify(result), (200 if result["success"] else status_map.get(result["error"], 400))
    finally:
        db.close()        