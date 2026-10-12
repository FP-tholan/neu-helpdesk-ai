from flask import Blueprint, jsonify, request, session

from database.db import SessionLocal
from services.ticket_service import (
    get_user_ticket_detail,
    close_user_ticket,
    reopen_user_ticket,
    create_user_ticket
)


ticket_bp = Blueprint("tickets", __name__)


def require_reporter_user():
    user_id = session.get("user_id")

    if user_id is None:
        return None, (
            jsonify({
                "success": False,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Bạn chưa đăng nhập"
                }
            }),
            401
        )

    if session.get("role") != "USER":
        return None, (
            jsonify({
                "success": False,
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Bạn không có quyền truy cập"
                }
            }),
            403
        )

    return user_id, None


@ticket_bp.route("", methods=["POST"])
def create_ticket():
    user_id, auth_error = require_reporter_user()

    if auth_error is not None:
        return auth_error

    data = request.get_json(silent=True) or {}

    title = data.get("title")
    building_name = data.get("building")
    room_code = data.get("room")
    category = data.get("category")
    priority = data.get("priority")
    description = data.get("description")

    db = SessionLocal()

    try:
        result = create_user_ticket(
            db,
            user_id,
            title,
            building_name,
            room_code,
            category,
            priority,
            description
        )

        if not result["success"]:
            error_messages = {
                "TITLE_REQUIRED": "Vui lòng nhập tiêu đề ticket",
                "DESCRIPTION_REQUIRED": "Vui lòng nhập mô tả sự cố",
                "BUILDING_NOT_FOUND": "Không tìm thấy tòa nhà",
                "ROOM_NOT_FOUND": "Không tìm thấy phòng",
                "INVALID_CATEGORY": "Loại sự cố không hợp lệ",
                "TEAM_NOT_FOUND": "Không tìm thấy team xử lý",
                "INVALID_PRIORITY": "Mức độ ưu tiên không hợp lệ"
            }

            return jsonify({
                "success": False,
                "error": {
                    "code": result["error"],
                    "message": error_messages.get(
                        result["error"],
                        "Dữ liệu không hợp lệ"
                    )
                }
            }), 400

        return jsonify({
            "success": True,
            "data": result["ticket"]
        }), 201

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

@ticket_bp.route("/<ticket_id>", methods=["GET"])
def get_ticket_detail(ticket_id):
    user_id, auth_error = require_reporter_user()

    if auth_error is not None:
        return auth_error

    db = SessionLocal()

    try:
        result = get_user_ticket_detail(
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

        return jsonify({
            "success": True,
            "data": result
        }), 200

    finally:
        db.close()


@ticket_bp.route("/<ticket_id>/close", methods=["POST"])
def close_ticket(ticket_id):
    user_id, auth_error = require_reporter_user()

    if auth_error is not None:
        return auth_error

    db = SessionLocal()

    try:
        result = close_user_ticket(
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
            return jsonify({
                "success": False,
                "error": {
                    "code": result["error"],
                    "message": "Ticket chưa ở trạng thái RESOLVED"
                }
            }), 400

        return jsonify({
            "success": True,
            "data": result
        }), 200

    finally:
        db.close()


@ticket_bp.route("/<ticket_id>/reopen", methods=["POST"])
def reopen_ticket(ticket_id):
    user_id, auth_error = require_reporter_user()

    if auth_error is not None:
        return auth_error

    data = request.get_json(silent=True) or {}

    note = data.get("note")

    db = SessionLocal()

    try:
        result = reopen_user_ticket(
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
            if result["error"] == "NOTE_REQUIRED":
                message = "Vui lòng nhập lý do yêu cầu xử lý tiếp"
            else:
                message = "Ticket chưa ở trạng thái RESOLVED"

            return jsonify({
                "success": False,
                "error": {
                    "code": result["error"],
                    "message": message
                }
            }), 400

        return jsonify({
            "success": True,
            "data": result
        }), 200

    finally:
        db.close()