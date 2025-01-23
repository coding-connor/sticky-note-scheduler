from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.event import Weekday


class RecurrenceBase(BaseModel):
    days_of_week: List[Weekday]


class RecurrenceCreate(RecurrenceBase):
    pass


class RecurrenceRead(RecurrenceBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


class EventBase(BaseModel):
    name: str
    start_time: datetime
    end_time: datetime


class EventCreate(EventBase):
    days_of_week: Optional[List[Weekday]] = None


class EventRead(EventBase):
    id: UUID
    recurrence: Optional[RecurrenceRead] = None
    model_config = ConfigDict(from_attributes=True)
