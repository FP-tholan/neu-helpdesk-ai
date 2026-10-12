from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from database.db import Base


class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )