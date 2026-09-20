from werkzeug.security import generate_password_hash

from database.db import SessionLocal
from models.user import User


def seed_users():
    db = SessionLocal()

    try:
        users = [
            User(
                username="student01",
                email="student@neu.edu.vn",
                password_hash=generate_password_hash("123456"),
                name="Student Test",
                role="USER",
                team_id=None,
                is_locked=False,
            ),
            User(
                username="lecturer01",
                email="lecturer@neu.edu.vn",
                password_hash=generate_password_hash("123456"),
                name="Lecturer Test",
                role="USER",
                team_id=None,
                is_locked=False,
            ),
            User(
                username="tech01",
                email="tech@neu.edu.vn",
                password_hash=generate_password_hash("123456"),
                name="Technician Test",
                role="TECHNICIAN",
                team_id="T_QTTB",
                is_locked=False,
            ),
            User(
                username="teamlead01",
                email="teamlead@neu.edu.vn",
                password_hash=generate_password_hash("123456"),
                name="Team Lead Test",
                role="TEAM_LEAD",
                team_id="T_QTTB",
                is_locked=False,
            ),
            User(
                username="admin01",
                email="admin@neu.edu.vn",
                password_hash=generate_password_hash("123456"),
                name="Admin Test",
                role="ADMIN",
                team_id="T_ADMIN",
                is_locked=False,
            ),
            User(
                username="locked01",
                email="locked@neu.edu.vn",
                password_hash=generate_password_hash("123456"),
                name="Locked Test",
                role="USER",
                team_id=None,
                is_locked=True,
            ),
        ]

        for user in users:
            existing_user = (
                db.query(User)
                .filter(User.email == user.email)
                .first()
            )

            if existing_user:
                print(f"User already exists: {user.email}")
                continue

            db.add(user)

        db.commit()
        print("Users seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_users()