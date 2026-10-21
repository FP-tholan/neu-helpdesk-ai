"""
In-memory store với session isolation + size cap.
Public interface: read() (cho Agent), append() (nội bộ service gọi).
"""
import threading
import uuid
from collections import defaultdict
from typing import Any

from src.config import settings
from src.schemas import Memory, MemoryRequest, MemoryResult

_lock = threading.RLock()
_STORE: dict[str, list[Memory]] = defaultdict(list)


def append(session_id: str, content: str, metadata: dict[str, Any] | None = None) -> None:
    if not session_id or not content:
        return
    with _lock:
        buf = _STORE[session_id]
        buf.append(Memory(
            id=f"mem_{uuid.uuid4().hex[:8]}",
            content=content,
            metadata=metadata or {},
        ))
        cap = settings.memory_max_per_session
        if len(buf) > cap:
            del buf[: len(buf) - cap]


def read(request: MemoryRequest) -> MemoryResult:
    with _lock:
        buf = list(_STORE.get(request.session_id, []))
    recent = buf[-request.top_k :]
    return MemoryResult(memories=recent, metadata={"count": len(recent)})


def clear(session_id: str) -> None:
    with _lock:
        _STORE.pop(session_id, None)


def count(session_id: str) -> int:
    with _lock:
        return len(_STORE.get(session_id, []))