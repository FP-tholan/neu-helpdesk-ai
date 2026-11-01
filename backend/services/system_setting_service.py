from database.db import SessionLocal
from models.system_setting import SystemSetting

DISPATCH_MODE_KEY = "dispatch_mode"
DEFAULT_DISPATCH_MODE = 1     # 1=Manual, 2=Auto

PRIORITY_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def get_setting(db, key, default=None):
    row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    return row.value if row else default


def set_setting(db, key, value, description=None):
    row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if row is None:
        db.add(SystemSetting(key=key, value=value, description=description))
    else:
        row.value = value
        if description:
            row.description = description
    db.commit()


def get_dispatch_mode(db) -> int:
    raw = get_setting(db, DISPATCH_MODE_KEY, str(DEFAULT_DISPATCH_MODE))
    try:
        mode = int(raw)
    except (TypeError, ValueError):
        return DEFAULT_DISPATCH_MODE
    return mode if mode in (1, 2) else DEFAULT_DISPATCH_MODE


def set_dispatch_mode(db, mode: int) -> None:
    if mode not in (1, 2):
        raise ValueError("Dispatch mode phải là 1 (Manual) hoặc 2 (Auto).")
    set_setting(
        db, DISPATCH_MODE_KEY, str(mode),
        "Dispatch mode: 1=Manual, 2=Auto",
    )