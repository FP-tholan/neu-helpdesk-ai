"""
Logic dùng chung cho auto-dispatch, priority decay, AI priority.
"""
import os
import uuid
from datetime import datetime

import requests

from models.ticket import Ticket
from models.user import User
from services.system_setting_service import PRIORITY_ORDER

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://127.0.0.1:8000")
AI_TIMEOUT = int(os.getenv("AI_PRIORITY_TIMEOUT", "5"))

_OPEN_STATUSES = {"NEW", "ASSIGNED", "IN_PROGRESS", "RE_PROCESS"}

# (số giờ, số cấp tăng priority)
_DECAY_STEPS = [
    (3, 0),
    (6, 1),
    (12, 2),
    (10**9, 3),
]


# ═══════════════════════════════════════════════════════════
# PRIORITY DECAY (chỉ hiển thị, không ghi DB)
# ═══════════════════════════════════════════════════════════

def get_effective_priority(ticket: Ticket, now: datetime | None = None) -> str:
    if ticket.status not in _OPEN_STATUSES:
        return ticket.priority
    if ticket.priority not in PRIORITY_ORDER:
        return ticket.priority

    ref = ticket.updated_at or ticket.created_at
    if ref is None:
        return ticket.priority
    if now is None:
        now = datetime.utcnow()

    hours = (now - ref).total_seconds() / 3600.0
    boost = 0
    for threshold, step in _DECAY_STEPS:
        if hours < threshold:
            boost = step
            break

    idx = PRIORITY_ORDER.index(ticket.priority)
    return PRIORITY_ORDER[min(idx + boost, len(PRIORITY_ORDER) - 1)]


def priority_rank(priority: str) -> int:
    """CRITICAL=0 (cao nhất), LOW=3 (thấp nhất)."""
    if priority not in PRIORITY_ORDER:
        return 999
    return len(PRIORITY_ORDER) - 1 - PRIORITY_ORDER.index(priority)


def sort_tickets_by_effective_priority(tickets: list, now=None):
    now = now or datetime.utcnow()
    return sorted(
        tickets,
        key=lambda t: (
            -priority_rank(get_effective_priority(t, now)),
            t.created_at or now,
        ),
    )


# ═══════════════════════════════════════════════════════════
# WORKLOAD — tìm KTV ít việc nhất
# ═══════════════════════════════════════════════════════════

def get_technician_workload_count(db, tech_id: str) -> int:
    return (
        db.query(Ticket)
        .filter(
            Ticket.assigned_to == tech_id,
            Ticket.status.in_(["ASSIGNED", "IN_PROGRESS", "RE_PROCESS"]),
        )
        .count()
    )


def find_best_technician(db, team_id: str) -> User | None:
    techs = (
        db.query(User)
        .filter(
            User.role == "TECHNICIAN",
            User.team_id == team_id,
            User.is_locked == False,   # noqa: E712
        )
        .all()
    )
    if not techs:
        return None

    on_duty = [t for t in techs if t.is_on_duty]
    candidates = on_duty or techs

    best, best_load = None, None
    for t in candidates:
        load = get_technician_workload_count(db, t.id)
        if best_load is None or load < best_load:
            best_load = load
            best = t
    return best


# ═══════════════════════════════════════════════════════════
# AI PRIORITY (chỉ dùng mode Auto)
# Trả None nếu AI service down / lỗi / timeout
# ═══════════════════════════════════════════════════════════

def ai_determine_priority(
    title: str, description: str, metadata: dict | None = None,
) -> str | None:
    query_text = f"{title}. {description}".strip()
    if not query_text:
        return None
    try:
        resp = requests.post(
            f"{AI_SERVICE_URL}/ai/query",
            json={
                "query": query_text,
                "session_id": f"priority_{uuid.uuid4().hex[:8]}",
                "user_id": None,
                "metadata": metadata or {},
            },
            timeout=AI_TIMEOUT,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not data.get("success"):
            return None
        prio = data.get("data", {}).get("metadata", {}).get("priority")
        return prio if prio in PRIORITY_ORDER else None
    except Exception:
        return None