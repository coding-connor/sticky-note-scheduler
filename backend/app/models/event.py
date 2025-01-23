import json
from datetime import datetime
from enum import IntEnum
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Weekday(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class WeekdayList(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(
        self,
        value: List[Weekday] | None,
        dialect,
    ) -> str | None:
        if value is None:
            return None
        return json.dumps([day.value for day in value])

    def process_result_value(
        self,
        value: str | None,
        dialect,
    ) -> List[Weekday] | None:
        if value is None:
            return None
        return [Weekday(day) for day in json.loads(value)]


class Recurrence(Base):
    __tablename__ = "recurrence"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    days_of_week: Mapped[List[Weekday]] = mapped_column(
        WeekdayList,
        nullable=False,
    )

    # Relationship
    event: Mapped["Event"] = relationship(
        "Event",
        back_populates="recurrence",
        uselist=False,
    )


class Event(Base):
    __tablename__ = "event"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_time: Mapped[datetime] = mapped_column(nullable=False)
    end_time: Mapped[datetime] = mapped_column(nullable=False)

    # Foreign key and relationship
    recurrence_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("recurrence.id"),
        nullable=True,
    )
    recurrence: Mapped[Recurrence | None] = relationship(
        "Recurrence",
        back_populates="event",
    )
