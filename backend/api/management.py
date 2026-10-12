from flask import Blueprint, jsonify, session, request

from database.db import SessionLocal
from models.user import User
from models.ticket import Ticket
from services.management_service import (
    get_management_dashboard,
    get_unassigned_tickets,
    assign_ticket_to_technician,
    reassign_ticket_to_technician,
    update_technician_duty_status
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