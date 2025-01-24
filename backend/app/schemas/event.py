from datetime import datetime, time
from typing import List, Optional
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, model_validator, validator

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
    name: str = Field(
        ...,
        description="Name of the event",
        example="Team Meeting",
    )
    start_datetime: datetime = Field(
        ...,
        description="Start time of the event (assumed to be in UTC)",
        example="2024-03-20T14:00:00.000",
    )
    end_datetime: datetime = Field(
        ...,
        description="End time of the event (assumed to be in UTC)",
        example="2024-03-20T15:00:00.000",
    )
    timezone: str = Field(
        ...,
        description="User's local timezone (e.g. 'America/New_York')",
        example="America/Los_Angeles",
    )

    @validator("name")
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @validator("timezone")
    def validate_timezone(cls, v):
        try:
            ZoneInfo(v)
        except Exception:
            raise ValueError("Invalid timezone. Must be a valid IANA timezone identifier")
        return v

    @model_validator(mode="after")
    def validate_end_time(self):
        # By this point, end_datetime is already a datetime object
        try:
            local_tz = ZoneInfo(self.timezone)
            local_end = self.end_datetime.astimezone(local_tz)

            # Check if end time is after 9 PM in user's timezone
            if local_end.time() > time(21, 0):
                raise ValueError(f"Events cannot end after 9:00 PM in {self.timezone}")
        except Exception as e:
            raise ValueError(f"Error validating end time: {str(e)}")

        return self

    @model_validator(mode="after")
    def validate_times(self):
        if self.end_datetime <= self.start_datetime:
            raise ValueError("Event must end after it starts")
        return self


class EventCreate(EventBase):
    days_of_week: Optional[List[Weekday]] = Field(
        default=None,
        description="Optional list of days for recurring events",
        example=["MONDAY", "WEDNESDAY"],
    )

    @validator("days_of_week")
    def validate_days_of_week(cls, v):
        if v is not None and not v:
            raise ValueError("Days of week cannot be empty when provided")
        return v


class EventRead(EventBase):
    id: UUID
    recurrence_rule: Optional[RecurrenceRuleRead] = None
    model_config = ConfigDict(from_attributes=True)
