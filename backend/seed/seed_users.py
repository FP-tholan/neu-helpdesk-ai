from werkzeug.security import generate_password_hash

from database.db import SessionLocal
from models.user import User


SEED_USERS = [
    dict(id="USR_STUDENT_01",  username="student01",   email="student@neu.edu.vn",   name="Nguyễn Văn An",       role="USER",       team_id=None,      is_locked=False, is_on_duty=False),
    dict(id="USR_LECTURER_01", username="lecturer01",  email="lecturer@neu.edu.vn",  name="Trần Thị Bình",        role="USER",       team_id=None,      is_locked=False, is_on_duty=False),
    dict(id="USR_TECH_01",     username="tech01",      email="tech@neu.edu.vn",      name="Lê Hoàng Long",        role="TECHNICIAN", team_id="T_QTTB",  is_locked=False, is_on_duty=True),
    dict(id="USR_TECH_02",     username="tech02",      email="tech2@neu.edu.vn",     name="Trần Văn Hưng",        role="TECHNICIAN", team_id="T_QTTB",  is_locked=False, is_on_duty=True),
    dict(id="USR_TECH_IT_01",  username="tech_it_01",  email="tech.it@neu.edu.vn",   name="Đỗ Tuấn Kiệt",         role="TECHNICIAN", team_id="T_IT",    is_locked=False, is_on_duty=True),
    dict(id="USR_TECH_PSA_01", username="tech_psa_01", email="tech.psa@neu.edu.vn",  name="Bùi Đức Anh",          role="TECHNICIAN", team_id="T_PSA",   is_locked=False, is_on_duty=True),
    dict(id="USR_LEAD_01",     username="teamlead01",  email="teamlead@neu.edu.vn",  name="Phạm Minh Đức",        role="TEAM_LEAD",  team_id="T_QTTB",  is_locked=False, is_on_duty=True),
    dict(id="USR_ADMIN_01",    username="admin01",     email="admin@neu.edu.vn",     name="Quản trị Hệ thống",    role="ADMIN",      team_id=None,      is_locked=False, is_on_duty=False),
    dict(id="USR_LOCKED_01",   username="locked01",    email="locked@neu.edu.vn",    name="Tài khoản bị khóa",    role="USER",       team_id=None,      is_locked=True,  is_on_duty=False),
]


def seed_users():
    db = SessionLocal()
    try:
        for spec in SEED_USERS:
            exists = db.query(User).filter(User.email == spec["email"]).first()
            if exists:
                print(f"Skip: {spec['email']}")
                continue
            db.add(User(
                id=spec["id"],
                username=spec["username"],
                email=spec["email"],
                password_hash=generate_password_hash("123456"),
                name=spec["name"],
                role=spec["role"],
                team_id=spec["team_id"],
                is_locked=spec["is_locked"],
                is_on_duty=spec["is_on_duty"],
            ))
        db.commit()
        print("Users seeded.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()