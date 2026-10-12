from database.db import SessionLocal
from models.room import Room
from models.building import Building

def seed_rooms():
    db = SessionLocal()

    try:
        rooms = [
            Room(
                id="ROOM_A2_101",
                code="A2.101",
                building_id="BLD_A2",
                name="Phòng A2.101",
            ),
            Room(
                id="ROOM_A2_202",
                code="A2.202",
                building_id="BLD_A2",
                name="Phòng A2.202",
            ),
            Room(
                id="ROOM_A2_602",
                code="A2.602",
                building_id="BLD_A2",
                name="Phòng A2.602",
            ),
            Room(
                id="ROOM_A2_304",
                code="A2.304",
                building_id="BLD_A2",
                name="Phòng A2.304",
            ),
            Room(
                id="ROOM_B_102",
                code="B.102",
                building_id="BLD_B",
                name="Phòng B.102",
            ),
            Room(
                id="ROOM_B_401",
                code="B.401",
                building_id="BLD_B",
                name="Phòng B.401",
            ),
        ]

        for room in rooms:
            existing_room = (
                db.query(Room)
                .filter(Room.id == room.id)
                .first()
            )

            if existing_room:
                print(f"Room already exists: {room.id}")
                continue

            db.add(room)

        db.commit()
        print("Rooms seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_rooms()