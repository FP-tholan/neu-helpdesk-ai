import os
import uuid

import requests
from flask import Blueprint, jsonify, request, session

ai_bp = Blueprint("ai", __name__)

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://127.0.0.1:8000")
# Qwen 3B cold start ~10-15s, đặt 90s để chắc chắn
AI_TIMEOUT = int(os.getenv("AI_TIMEOUT", "90"))

_warmed_up = False


def _warmup() -> None:
    """Gửi 1 request dummy khi service cold start để load model vào RAM."""
    global _warmed_up
    if _warmed_up:
        return
    try:
        requests.post(
            f"{AI_SERVICE_URL}/ai/query",
            json={
                "query": "warmup",
                "session_id": "warmup",
                "metadata": {},
            },
            timeout=AI_TIMEOUT,
        )
    except requests.RequestException:
        pass
    _warmed_up = True


def _safe_json(resp: requests.Response) -> dict:
    try:
        return resp.json()
    except ValueError:
        return {
            "success": False,
            "error": {
                "code": "AI_BAD_RESPONSE",
                "message": "AI trả về response không phải JSON.",
            },
        }


@ai_bp.post("/query")
def ai_query():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({
            "success": False,
            "error": {"code": "UNAUTHORIZED", "message": "Bạn chưa đăng nhập"},
        }), 401

    data = request.get_json(silent=True) or {}
    query_text = (data.get("query") or "").strip()
    if not query_text:
        return jsonify({
            "success": False,
            "error": {"code": "QUERY_REQUIRED", "message": "Nội dung không được rỗng"},
        }), 400

    if len(query_text) > 1000:
        return jsonify({
            "success": False,
            "error": {"code": "QUERY_TOO_LONG", "message": "Câu hỏi quá dài (tối đa 1000 ký tự)"},
        }), 400

    _warmup()  # chỉ chạy lần đầu, no-op nếu đã warm

    metadata = dict(data.get("metadata") or {})
    metadata["user_role"] = (session.get("role") or "USER").lower()

    payload = {
        "query": query_text,
        "session_id": data.get("session_id") or f"session_{user_id}",
        "user_id": user_id,
        "metadata": metadata,
    }

    try:
        resp = requests.post(
            f"{AI_SERVICE_URL}/ai/query",
            json=payload,
            timeout=AI_TIMEOUT,
            headers={"X-Request-ID": str(uuid.uuid4())},
        )
    except requests.Timeout:
        return jsonify({
            "success": False,
            "error": {
                "code": "AI_TIMEOUT",
                "message": "AI đang xử lý quá lâu. Vui lòng thử lại.",
            },
        }), 504
    except requests.RequestException as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "AI_SERVICE_UNAVAILABLE",
                "message": "Không kết nối được AI service.",
                "detail": str(e),
            },
        }), 503

    return jsonify(_safe_json(resp)), resp.status_code