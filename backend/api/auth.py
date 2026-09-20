from flask import Blueprint, jsonify, request, session

from database.db import SessionLocal
from services.auth_service import authenticate_user

from models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "error": {
                "code": "INVALID_REQUEST",
                "message": "Dữ liệu đăng nhập không hợp lệ"
            }
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "success": False,
            "error": {
                "code": "MISSING_CREDENTIALS",
                "message": "Email và mật khẩu không được để trống"
            }
        }), 400

    db = SessionLocal()

    try:
        user = authenticate_user(
            db,
            email,
            password
        )

        if user is None:
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "Tài khoản hoặc mật khẩu không chính xác"
                }
            }), 401

        session["user_id"] = user.id

        return jsonify({
            "success": True,
            "data": {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "role": user.role,
                    "team_id": user.team_id
                }
            }
        }), 200

    finally:
        db.close()


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({
            "success": False,
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Bạn chưa đăng nhập"
            }
        }), 401

    db = SessionLocal()

    try:
        user = db.query(User).filter(User.id == user_id).first()

        if user is None:
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
            "data": {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "role": user.role,
                    "team_id": user.team_id
                }
            }
        }), 200

    finally:
        db.close()


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "success": True,
        "message": "Đăng xuất thành công"
    }), 200