from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.db import Base


class DispatchRule(Base):
    __tablename__ = "dispatch_rules"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    building_id: Mapped[str | None] = mapped_column(
        String(50), ForeignKey("buildings.id"), nullable=True
    )
    team_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("teams.id"), nullable=False
    )