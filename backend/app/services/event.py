from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.event import Event, RecurrenceRule, Weekday
from app.schemas.event import EventCreate


def check_time_conflict(
    db: Session,
    start_datetime: datetime,
    end_datetime: datetime,
    days_of_week: Optional[List[Weekday]] = None,
) -> bool:
    """Check if there's a time conflict with existing one-time events."""
    # Only check non-recurring events
    query = db.query(Event).filter(
        Event.recurrence_rule_id.is_(None),
        or_(
            # Check if any existing event starts during our new event
            and_(
                Event.start_datetime >= start_datetime,
                Event.start_datetime < end_datetime,
            ),
            # Check if any existing event ends during our new event
            and_(
                Event.end_datetime > start_datetime,
                Event.end_datetime <= end_datetime,
            ),
            # Check if any existing event completely encompasses our new event
            and_(
                Event.start_datetime <= start_datetime,
                Event.end_datetime >= end_datetime,
            ),
        ),
    )

    return query.first() is not None


def create_event(db: Session, event: EventCreate) -> Event:
    """Create a new event, optionally with recurrence."""
    # Check for conflicts
    if check_time_conflict(
        db,
        event.start_datetime,
        event.end_datetime,
        event.days_of_week,
    ):
        raise HTTPException(
            status_code=409,
            detail="Time slot conflict with existing event",
        )

    db_event = Event(
        name=event.name,
        start_datetime=event.start_datetime,
        end_datetime=event.end_datetime,
        timezone=event.timezone,
    )

    if event.days_of_week:
        # Create recurrence if days are specified
        db_recurrence = RecurrenceRule(days_of_week=event.days_of_week)
        db_event.recurrence_rule = db_recurrence

    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def get_events(db: Session, skip: int = 0, limit: int = 100) -> List[Event]:
    """Get a list of events with pagination."""
    return db.query(Event).offset(skip).limit(limit).all()
