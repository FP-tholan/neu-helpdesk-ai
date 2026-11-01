from database.db import SessionLocal
from models.team import Team


def seed_teams():
    db = SessionLocal()

    try:
        teams = [
            Team(
                id="T_IT",
                code="IT",
                name="Công nghệ thông tin",
                description="Đội phụ trách các sự cố và hệ thống công nghệ thông tin",
            ),
            Team(
                id="T_PSA",
                code="PSA",
                name="Team PSA",
                description="Đội PSA phụ trách cơ sở vật chất khu vực A1, A2",
            ),
            Team(
                id="T_QTTB",
                code="QTTB",
                name="Quản trị thiết bị",
                description="Đội quản trị thiết bị phụ trách xử lý sự cố thiết bị và cơ sở vật chất",
            ),
            Team(
                id="T_ADMIN",
                code="ADMIN",
                name="Quản trị hệ thống",
                description="Đội phụ trách quản trị hệ thống",
            ),
        ]

        for team in teams:
            existing_team = (
                db.query(Team)
                .filter(Team.id == team.id)
                .first()
            )

            if existing_team:
                print(f"Team already exists: {team.id}")
                continue

            db.add(team)

        db.commit()
        print("Teams seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_teams()