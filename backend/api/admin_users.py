from flask import Blueprint, jsonify, request, session
from database.db import SessionLocal
from models.user import User

admin_users_bp = Blueprint("admin_users", __name__)


def require_system_admin():
    """Chỉ cho phép Admin hệ thống quản lý tài khoản."""
    if session.get("user_id") is None:
        return jsonify({
            "success": False,
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Bạn chưa đăng nhập"
            }
        }), 401

    if session.get("role") != "ADMIN":
        return jsonify({
            "success": False,
            "error": {
                "code": "FORBIDDEN",
                "message": "Bạn không có quyền quản lý tài khoản"
            }
        }), 403

    return None


@admin_users_bp.get("")
def list_users():
    """Lấy danh sách tài khoản, hỗ trợ tìm kiếm và lọc."""
    err = require_system_admin()
    if err:
        return err

    # Lấy các điều kiện từ query parameters
    search = request.args.get("search", "").strip()
    role = request.args.get("role", "").strip().upper()
    is_locked = request.args.get("is_locked", "").strip().lower()

    db = SessionLocal()

    try:
        query = db.query(User)

        # 1. Tìm theo tên hoặc email
        if search:
            keyword = f"%{search}%"

            query = query.filter(
                (User.name.ilike(keyword)) |
                (User.email.ilike(keyword))
            )

        # 2. Lọc theo role
        if role:
            allowed_roles = {
                "USER",
                "TECHNICIAN",
                "TEAM_LEAD",
                "ADMIN"
            }

            if role not in allowed_roles:
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "INVALID_ROLE",
                        "message": "Role không hợp lệ"
                    }
                }), 400

            query = query.filter(User.role == role)

        # 3. Lọc theo trạng thái khóa
        if is_locked:
            if is_locked not in {"true", "false"}:
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "INVALID_LOCK_STATUS",
                        "message": "is_locked chỉ nhận true hoặc false"
                    }
                }), 400

            query = query.filter(
                User.is_locked == (is_locked == "true")
            )

        users = query.order_by(User.name.asc()).all()

        data = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "team_id": user.team_id,
                "is_locked": user.is_locked,
                "is_on_duty": user.is_on_duty,
            }
            for user in users
        ]

        return jsonify({
            "success": True,
            "data": data
        }), 200

    finally:
        db.close()


@admin_users_bp.patch("/<user_id>/lock")
def lock_user(user_id):
    err = require_system_admin()
    if err:
        return err

    current_user_id = session.get("user_id")

    # Không cho Admin tự khóa tài khoản của mình
    if user_id == current_user_id:
        return jsonify({
            "success": False,
            "error": {
                "code": "CANNOT_LOCK_SELF",
                "message": "Bạn không thể tự khóa tài khoản của mình"
            }
        }), 400

    db = SessionLocal()

    try:
        user = db.query(User).filter(User.id == user_id).first()

        if user is None:
            return jsonify({
                "success": False,
                "error": {
                    "code": "USER_NOT_FOUND",
                    "message": "Không tìm thấy tài khoản"
                }
            }), 404

        if user.is_locked:
            return jsonify({
                "success": True,
                "message": "Tài khoản đã bị khóa",
                "data": {
                    "id": user.id,
                    "is_locked": user.is_locked
                }
            }), 200

        user.is_locked = True
        db.commit()

        return jsonify({
            "success": True,
            "message": "Khóa tài khoản thành công",
            "data": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "is_locked": user.is_locked
            }
        }), 200

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


@admin_users_bp.patch("/<user_id>/unlock")
def unlock_user(user_id):
    err = require_system_admin()
    if err:
        return err

    db = SessionLocal()

    try:
        user = db.query(User).filter(User.id == user_id).first()

        if user is None:
            return jsonify({
                "success": False,
                "error": {
                    "code": "USER_NOT_FOUND",
                    "message": "Không tìm thấy tài khoản"
                }
            }), 404

        if not user.is_locked:
            return jsonify({
                "success": True,
                "message": "Tài khoản hiện không bị khóa",
                "data": {
                    "id": user.id,
                    "is_locked": user.is_locked
                }
            }), 200

        user.is_locked = False
        db.commit()

        return jsonify({
            "success": True,
            "message": "Mở khóa tài khoản thành công",
            "data": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "is_locked": user.is_locked
            }
        }), 200

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()