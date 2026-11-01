from database.db import SessionLocal
from models.system_setting import SystemSetting


def seed_settings():
    db = SessionLocal()
    try:
        if not db.query(SystemSetting).filter(
            SystemSetting.key == "dispatch_mode"
        ).first():
            db.add(SystemSetting(
                key="dispatch_mode",
                value="1",
                description="Dispatch mode: 1=Manual, 2=Auto",
            ))
            db.commit()
            print("Default dispatch_mode = 1 (Manual).")
        else:
            print("dispatch_mode already exists.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_settings()