from database.db import SessionLocal
from models.user import User


db = SessionLocal()

try:
    users = db.query(User).all()

    for user in users:
        print(
            f"ID: {user.id} | "
            f"Email: {user.email} | "
            f"Role: {user.role} | "
            f"Locked: {user.is_locked}"
        )

finally:
    db.close()