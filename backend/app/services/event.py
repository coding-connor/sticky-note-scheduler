from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.event import Event, Recurrence
from app.schemas.event import EventCreate


def create_event(db: Session, event: EventCreate) -> Event:
    """Create a new event, optionally with recurrence."""
    db_event = Event(
        name=event.name,
        start_time=event.start_time,
        end_time=event.end_time,
    )

    if event.days_of_week:
        # Create recurrence if days are specified
        db_recurrence = Recurrence(days_of_week=event.days_of_week)
        db_event.recurrence = db_recurrence

    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def get_event(db: Session, event_id: UUID) -> Optional[Event]:
    """Get a single event by ID."""
    return db.query(Event).filter(Event.id == event_id).first()


def get_events(db: Session, skip: int = 0, limit: int = 100) -> List[Event]:
    """Get a list of events with pagination."""
    return db.query(Event).offset(skip).limit(limit).all()
