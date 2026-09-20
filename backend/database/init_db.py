from database.db import Base, engine
from models.user import User


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")


if __name__ == "__main__":
    init_db()