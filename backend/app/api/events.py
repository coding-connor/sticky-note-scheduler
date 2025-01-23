from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.event import EventCreate, EventRead
from app.services import event as event_service

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventRead)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
) -> EventRead:
    """Create a new event."""
    return event_service.create_event(db=db, event=event)


@router.get("/{event_id}", response_model=EventRead)
def get_event(
    event_id: UUID,
    db: Session = Depends(get_db),
) -> EventRead:
    """Get a single event by ID."""
    db_event = event_service.get_event(db=db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event


@router.get("/", response_model=List[EventRead])
def get_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[EventRead]:
    """Get a list of events with pagination."""
    return event_service.get_events(db=db, skip=skip, limit=limit)
