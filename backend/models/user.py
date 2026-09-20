from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from database.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    team_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)