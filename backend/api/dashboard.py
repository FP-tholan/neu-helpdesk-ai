from flask import Blueprint, jsonify, session

from database.db import SessionLocal
from services.dashboard_service import get_user_dashboard


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard", methods=["GET"])
def get_dashboard():

    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({
            "success": False,
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Bạn chưa đăng nhập"
            }
        }), 401

    if session.get("role") != "USER":
        return jsonify({
            "success": False,
            "error": {
                "code": "FORBIDDEN",
                "message": "Bạn không có quyền truy cập"
            }
        }), 403

    db = SessionLocal()

    try:
        dashboard = get_user_dashboard(db, user_id)

        if dashboard is None:
            session.clear()

            return jsonify({
                "success": False,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Phiên đăng nhập không hợp lệ"
                }
            }), 401

        return jsonify({
            "success": True,
            "data": dashboard
        }), 200

    finally:
        db.close()