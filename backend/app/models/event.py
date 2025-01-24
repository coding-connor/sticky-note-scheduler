import json
from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Weekday(str, Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"

    @property
    def day_number(self) -> int:
        """Get the day number (0 = Monday, 6 = Sunday)."""
        return list(Weekday).index(self)


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


class RecurrenceRule(Base):
    __tablename__ = "recurrence_rule"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    days_of_week: Mapped[List[Weekday]] = mapped_column(
        WeekdayList,
        nullable=False,
    )

    # Relationship
    event: Mapped["Event"] = relationship(
        "Event",
        back_populates="recurrence_rule",
        uselist=False,
    )


class Event(Base):
    __tablename__ = "event"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), nullable=False)

    # Foreign key and relationship
    recurrence_rule_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("recurrence_rule.id"),
        nullable=True,
    )
    recurrence_rule: Mapped[RecurrenceRule | None] = relationship(
        "RecurrenceRule",
        back_populates="event",
    )
