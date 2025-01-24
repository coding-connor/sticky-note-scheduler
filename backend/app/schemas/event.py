from datetime import datetime, time
from typing import List, Optional
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, model_validator, validator

from app.models.event import Weekday


class RecurrenceRuleBase(BaseModel):
    days_of_week: List[Weekday]

    @validator("days_of_week")
    def validate_days_of_week(cls, v):
        if not v:
            raise ValueError("At least one day of week must be specified")
        if len(set(v)) != len(v):
            raise ValueError("Days of week must be unique")
        return v


class RecurrenceRuleCreate(RecurrenceRuleBase):
    pass


class RecurrenceRuleRead(RecurrenceRuleBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


class EventBase(BaseModel):
    name: str
    start_datetime: datetime
    end_datetime: datetime
    timezone: str = "America/New_York"

    @validator("name")
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @validator("end_datetime")
    def validate_end_time(cls, end_datetime, values):
        # Convert to local time for validation
        local_tz = ZoneInfo(values.get("timezone", "America/New_York"))
        local_end = end_datetime.astimezone(local_tz)

        # Check if end time is after 9 PM
        if local_end.time() > time(21, 0):
            raise ValueError("Events cannot end after 9:00 PM local time")

        return end_datetime

    @model_validator(mode="after")
    def validate_times(self):
        if self.end_datetime <= self.start_datetime:
            raise ValueError("Event must end after it starts")
        return self


class EventCreate(EventBase):
    days_of_week: Optional[List[Weekday]] = None

    @validator("days_of_week")
    def validate_days_of_week(cls, v):
        if v is not None and not v:
            raise ValueError("Days of week cannot be empty when provided")
        return v


class EventRead(EventBase):
    id: UUID
    recurrence_rule: Optional[RecurrenceRuleRead] = None
    model_config = ConfigDict(from_attributes=True)
