from flask import Blueprint, jsonify, request,session

from database.db import SessionLocal
from services.technician_service import (
    get_technician_dashboard,
    get_technician_ticket_detail,
    accept_technician_ticket,
    update_technician_progress,
    resolve_technician_ticket,
    escalate_technician_ticket
)


technician_bp = Blueprint(
    "technician",
    __name__
)


@technician_bp.route("/dashboard", methods=["GET"])
def technician_dashboard():

    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({
            "success": False,
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Bạn chưa đăng nhập"
            }
        }), 401

    role = session.get("role")

    if role != "TECHNICIAN":
        return jsonify({
            "success": False,
            "error": {
                "code": "FORBIDDEN",
                "message": "Bạn không có quyền truy cập"
            }
        }), 403

    db = SessionLocal()

    try:
        result = get_technician_dashboard(
            db,
            user_id
        )

        if result is None:
            return jsonify({
                "success": False,
                "error": {
                    "code": "TECHNICIAN_NOT_FOUND",
                    "message": "Không tìm thấy thông tin kỹ thuật viên"
                }
            }), 404

        return jsonify({
            "success": True,
            "data": result
        }), 200

    finally:
        db.close()


@technician_bp.route("/tickets/<ticket_id>", methods=["GET"])
def get_technician_ticket_detail_api(ticket_id):

    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({
            "success": False,
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Bạn chưa đăng nhập"
            }
        }), 401

    if session.get("role") != "TECHNICIAN":
        return jsonify({
            "success": False,
            "error": {
                "code": "FORBIDDEN",
                "message": "Bạn không có quyền truy cập"
            }
        }), 403

    db = SessionLocal()

    try:
        result = get_technician_ticket_detail(
            db,
            user_id,
            ticket_id
        )

        if result is None:
            return jsonify({
                "success": False,
                "error": {
                    "code": "TICKET_NOT_FOUND",
                    "message": "Không tìm thấy ticket hoặc bạn không có quyền truy cập"
                }
            }), 404

        return jsonify({
            "success": True,
            "data": result
        }), 200

    finally:
        db.close()


@technician_bp.route("/tickets/<ticket_id>/accept", methods=["POST"])
def accept_ticket(ticket_id):

    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({
            "success": False,
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Bạn chưa đăng nhập"
            }
        }), 401

    if session.get("role") != "TECHNICIAN":
        return jsonify({
            "success": False,
            "error": {
                "code": "FORBIDDEN",
                "message": "Bạn không có quyền truy cập"
            }
        }), 403

    db = SessionLocal()

    try:
        result = accept_technician_ticket(
            db,
            user_id,
            ticket_id
        )

        if result is None:
            return jsonify({
                "success": False,
                "error": {
                    "code": "TICKET_NOT_FOUND",
                    "message": "Không tìm thấy ticket"
                }
            }), 404

        if not result["success"]:
            messages = {
                "TICKET_NOT_ASSIGNED_TO_TEAM":
                    "Ticket không thuộc Team của bạn",

                "TICKET_NOT_ASSIGNABLE":
                    "Ticket không ở trạng thái có thể nhận xử lý",

                "TICKET_ALREADY_ASSIGNED":
                    "Ticket đã được kỹ thuật viên khác nhận"
            }

            return jsonify({
                "success": False,
                "error": {
                    "code": result["error"],
                    "message": messages.get(
                        result["error"],
                        "Không thể nhận xử lý ticket"
                    )
                }
            }), 400

        return jsonify({
            "success": True,
            "data": result
        }), 200

    finally:
        db.close()


@technician_bp.route("/tickets/<ticket_id>/progress", methods=["POST"])
def update_ticket_progress(ticket_id):

    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({
            "success": False,
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Bạn chưa đăng nhập"
            }
        }), 401

    if session.get("role") != "TECHNICIAN":
        return jsonify({
            "success": False,
            "error": {
                "code": "FORBIDDEN",
                "message": "Bạn không có quyền truy cập"
            }
        }), 403

    data = request.get_json(silent=True) or {}

    note = data.get("note")

    db = SessionLocal()

    try:
        result = update_technician_progress(
            db,
            user_id,
            ticket_id,
            note
        )

        if result is None:
            return jsonify({
                "success": False,
                "error": {
                    "code": "TICKET_NOT_FOUND",
                    "message": "Không tìm thấy ticket"
                }
            }), 404

        if not result["success"]:

            messages = {
                "TICKET_NOT_ASSIGNED_TO_TEAM":
                    "Ticket không thuộc Team của bạn",

                "TICKET_NOT_ASSIGNED_TO_TECHNICIAN":
                    "Ticket chưa được giao cho bạn",

                "TICKET_NOT_IN_PROGRESS":
                    "Ticket chưa ở trạng thái IN_PROGRESS",

                "NOTE_REQUIRED":
                    "Nội dung cập nhật không được để trống"
            }

            return jsonify({
                "success": False,
                "error": {
                    "code": result["error"],
                    "message": messages.get(
                        result["error"],
                        "Không thể cập nhật tiến độ"
                    )
                }
            }), 400

        return jsonify({
            "success": True,
            "data": result
        }), 200

    finally:
        db.close()


@technician_bp.route("/tickets/<ticket_id>/resolve", methods=["POST"])
def resolve_ticket(ticket_id):

    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({
            "success": False,
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Bạn chưa đăng nhập"
            }
        }), 401

    if session.get("role") != "TECHNICIAN":
        return jsonify({
            "success": False,
            "error": {
                "code": "FORBIDDEN",
                "message": "Bạn không có quyền truy cập"
            }
        }), 403

    data = request.get_json(silent=True) or {}

    cause = data.get("cause")
    solution = data.get("solution")

    db = SessionLocal()

    try:
        result = resolve_technician_ticket(
            db,
            user_id,
            ticket_id,
            cause,
            solution
        )

        if result is None:
            return jsonify({
                "success": False,
                "error": {
                    "code": "TICKET_NOT_FOUND",
                    "message": "Không tìm thấy ticket"
                }
            }), 404

        if not result["success"]:

            messages = {
                "FORBIDDEN":
                    "Bạn không có quyền thực hiện thao tác này",

                "TICKET_NOT_ASSIGNED_TO_TEAM":
                    "Ticket không thuộc Team của bạn",

                "TICKET_NOT_ASSIGNED_TO_TECHNICIAN":
                    "Ticket chưa được giao cho bạn",

                "TICKET_NOT_IN_PROGRESS":
                    "Ticket chưa ở trạng thái IN_PROGRESS",

                "CAUSE_REQUIRED":
                    "Nguyên nhân sự cố không được để trống",

                "SOLUTION_REQUIRED":
                    "Giải pháp khắc phục không được để trống"
            }

            return jsonify({
                "success": False,
                "error": {
                    "code": result["error"],
                    "message": messages.get(
                        result["error"],
                        "Không thể Resolve ticket"
                    )
                }
            }), 400

        return jsonify({
            "success": True,
            "data": result
        }), 200

    finally:
        db.close()


@technician_bp.route("/tickets/<ticket_id>/escalate", methods=["POST"])
def escalate_ticket(ticket_id):

    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({
            "success": False,
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Bạn chưa đăng nhập"
            }
        }), 401

    if session.get("role") != "TECHNICIAN":
        return jsonify({
            "success": False,
            "error": {
                "code": "FORBIDDEN",
                "message": "Bạn không có quyền truy cập"
            }
        }), 403

    data = request.get_json(silent=True) or {}

    new_team_id = data.get("new_team_id")
    reason = data.get("reason")

    db = SessionLocal()

    try:
        result = escalate_technician_ticket(
            db,
            user_id,
            ticket_id,
            new_team_id,
            reason
        )

        if result is None:
            return jsonify({
                "success": False,
                "error": {
                    "code": "TICKET_NOT_FOUND",
                    "message": "Không tìm thấy ticket"
                }
            }), 404

        if not result["success"]:

            messages = {
                "TECHNICIAN_NOT_FOUND":
                    "Không tìm thấy kỹ thuật viên",

                "TICKET_NOT_ASSIGNED_TO_TEAM":
                    "Ticket không thuộc Team của bạn",

                "TICKET_NOT_ASSIGNED_TO_TECHNICIAN":
                    "Ticket chưa được giao cho bạn",

                "TICKET_NOT_IN_PROGRESS":
                    "Ticket chưa ở trạng thái IN_PROGRESS",

                "TEAM_NOT_FOUND":
                    "Không tìm thấy Team cần chuyển",

                "SAME_TEAM":
                    "Team mới phải khác Team hiện tại",

                "REASON_REQUIRED":
                    "Lý do chuyển Team không được để trống"
            }

            return jsonify({
                "success": False,
                "error": {
                    "code": result["error"],
                    "message": messages.get(
                        result["error"],
                        "Không thể chuyển Team"
                    )
                }
            }), 400

        return jsonify({
            "success": True,
            "data": result
        }), 200

    finally:
        db.close()


