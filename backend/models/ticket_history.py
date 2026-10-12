from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.db import Base


class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    ticket_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("tickets.id"),
        nullable=False
    )

    from_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    to_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    updated_by: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("users.id"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )