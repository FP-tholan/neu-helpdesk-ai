from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from database.db import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    building_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("buildings.id"),
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )