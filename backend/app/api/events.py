from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.event import EventCreate, EventRead
from app.services import event as event_service

router = APIRouter(prefix="/events", tags=["events"])


@router.post(
    "/",
    response_model=EventRead,
    responses={
        409: {"description": "Time slot conflict with existing event"},
    },
)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
) -> EventRead:
    """Create a new event.

    The event can be a single occurrence or recurring weekly on specified days.
    Duration is specified in minutes.
    """
    return event_service.create_event(db=db, event=event)


@router.get("/", response_model=List[EventRead])
def get_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[EventRead]:
    """Get a list of events with pagination."""
    return event_service.get_events(db=db, skip=skip, limit=limit)
