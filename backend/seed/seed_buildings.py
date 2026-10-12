from database.db import SessionLocal
from models.building import Building


def seed_buildings():
    db = SessionLocal()

    try:
        buildings = [
            Building(
                id="BLD_A1",
                code="A1",
                name="Tòa nhà A1",
            ),
            Building(
                id="BLD_A2",
                code="A2",
                name="Tòa nhà A2",
            ),
            Building(
                id="BLD_B",
                code="B",
                name="Tòa nhà B",
            ),
        ]

        for building in buildings:
            existing_building = (
                db.query(Building)
                .filter(Building.id == building.id)
                .first()
            )

            if existing_building:
                print(f"Building already exists: {building.id}")
                continue

            db.add(building)

        db.commit()
        print("Buildings seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_buildings()