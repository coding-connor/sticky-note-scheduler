from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import and_, or_, text
from sqlalchemy.orm import Session

from app.models.event import Event, RecurrenceRule, Weekday
from app.schemas.event import EventCreate


def get_time_overlap_conditions(
    start_datetime: datetime,
    end_datetime: datetime,
):
    """Returns SQLAlchemy filter conditions for checking time overlaps.

    Args:
        start_datetime: Start time to check
        end_datetime: End time to check

    Returns:
        SQLAlchemy OR condition containing all overlap cases
    """

    # Convert datetime to minutes since midnight for comparison
    def to_minutes(dt: datetime) -> int:
        return dt.hour * 60 + dt.minute

    start_minutes = to_minutes(start_datetime)
    end_minutes = to_minutes(end_datetime)

    # Base time expressions
    time_base = (
        "(CAST(STRFTIME('%H', event.start_datetime) AS INTEGER) * 60 + "
        "CAST(STRFTIME('%M', event.start_datetime) AS INTEGER))"
    )
    end_time_base = (
        "(CAST(STRFTIME('%H', event.end_datetime) AS INTEGER) * 60 + "
        "CAST(STRFTIME('%M', event.end_datetime) AS INTEGER))"
    )

    return or_(
        # Case 1: Event starts during our event
        text(f"{time_base} >= {start_minutes} AND {time_base} < {end_minutes}"),
        # Case 2: Event ends during our event
        text(f"{end_time_base} > {start_minutes} AND {end_time_base} <= {end_minutes}"),
        # Case 3: Event completely surrounds our event
        text(f"{time_base} <= {start_minutes} AND {end_time_base} >= {end_minutes}"),
    )


def check_anchor_x_anchor_conflict(
    db: Session,
    start_datetime: datetime,
    end_datetime: datetime,
) -> bool:
    """Check if a new event's anchor datetime conflicts with any existing events' anchor datetimes.

    Checks three overlap conditions:
    1. An existing event starts during our event
    2. An existing event ends during our event
    3. An existing event completely surrounds our event

    Args:
        db: Database session
        start_datetime: Start time of new event
        end_datetime: End time of new event

    Returns:
        bool: True if there's a conflict, False otherwise
    """
    existing_events = (
        db.query(Event)
        .filter(
            or_(
                # Case 1: Event starts during our event
                and_(
                    Event.start_datetime >= start_datetime,
                    Event.start_datetime < end_datetime,
                ),
                # Case 2: Event ends during our event
                and_(
                    Event.end_datetime > start_datetime,
                    Event.end_datetime <= end_datetime,
                ),
                # Case 3: Event completely surrounds our event
                and_(
                    Event.start_datetime <= start_datetime,
                    Event.end_datetime >= end_datetime,
                ),
            )
        )
        .all()
    )

    return len(existing_events) > 0


def check_anchor_x_recurrence_conflict(
    db: Session,
    start_datetime: datetime,
    end_datetime: datetime,
) -> bool:
    """Check if a new event's anchor datetime conflicts with recurring events."""
    # Get the weekday of the start datetime
    weekday = Weekday[start_datetime.strftime("%A").upper()]

    # Find recurring events that happen on this weekday
    existing_events = (
        db.query(Event)
        .join(RecurrenceRule)
        .filter(
            Event.recurrence_rule_id.isnot(None),
            text(f"recurrence_rule.days_of_week LIKE '%{weekday.value}%'"),
            get_time_overlap_conditions(start_datetime, end_datetime),
        )
        .all()
    )

    return len(existing_events) > 0


def check_recurrence_x_anchor_conflict(
    db: Session,
    start_datetime: datetime,
    end_datetime: datetime,
    days_of_week: List[Weekday],
) -> bool:
    """Check if a new recurring event conflicts with existing anchor events."""
    # Convert weekdays to their string values for SQL comparison
    weekday_values = [day.value for day in days_of_week]

    # Find non-recurring events that happen on any of our weekdays
    existing_events = (
        db.query(Event)
        .filter(
            Event.recurrence_rule_id.is_(None),
            or_(*[text(f"UPPER(strftime('%A', event.start_datetime)) = '{day}'") for day in weekday_values]),
            get_time_overlap_conditions(start_datetime, end_datetime),
        )
        .all()
    )

    return len(existing_events) > 0


def check_recurrence_x_recurrence_conflict(
    db: Session,
    start_datetime: datetime,
    end_datetime: datetime,
    days_of_week: List[Weekday],
) -> bool:
    """Check if a new recurring event conflicts with existing recurring events."""
    # Convert weekdays to their string values for SQL comparison
    weekday_values = [day.value for day in days_of_week]

    # Find recurring events that happen on any of our weekdays
    existing_events = (
        db.query(Event)
        .join(RecurrenceRule)
        .filter(
            Event.recurrence_rule_id.isnot(None),
            or_(*[text(f"recurrence_rule.days_of_week LIKE '%{day}%'") for day in weekday_values]),
            get_time_overlap_conditions(start_datetime, end_datetime),
        )
        .all()
    )

    return len(existing_events) > 0


def check_time_conflict(
    db: Session,
    start_datetime: datetime,
    end_datetime: datetime,
    timezone: str,
    days_of_week: Optional[List[Weekday]] = None,
) -> bool:
    """Orchestrating function to check all possible conflict cases.

    Every event is composed of an anchor event (the initial event),
    and a potential recurrence rule defining future events.

    The initial event may exist outside the rule for recurring events.
    E.g. A 3-hour event Monday, then repeats every Tuesday;
    in which case there is a single Monday anchor event,
    followed by infinite Tuesday events.

    This creates 4 cases to check for conflicts:

    Checks:
    1. Anchor vs Anchor
    2. Anchor vs Recurrence
    3. Recurrence vs Anchor
    4. Recurrence vs Recurrence
    """
    # Case 1: Check anchor-to-anchor conflicts
    if check_anchor_x_anchor_conflict(db, start_datetime, end_datetime):
        return True

    # Case 2: Check anchor-to-recurrence conflicts
    if check_anchor_x_recurrence_conflict(db, start_datetime, end_datetime):
        return True

    # Case 3: Check recurrence-to-anchor conflicts
    if days_of_week and check_recurrence_x_anchor_conflict(db, start_datetime, end_datetime, days_of_week):
        return True

    # Case 4: Check recurrence-to-recurrence conflicts
    if days_of_week and check_recurrence_x_recurrence_conflict(db, start_datetime, end_datetime, days_of_week):
        return True

    return False


def get_events(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> List[Event]:
    """Get a list of events with pagination.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of events
    """
    return db.query(Event).order_by(Event.start_datetime).offset(skip).limit(limit).all()


def create_event(
    db: Session,
    event: EventCreate,
) -> Event:
    """Create a new event, optionally with recurrence.

    Args:
        db: Database session
        event: Event data including optional recurrence rule

    Returns:
        Created event

    Raises:
        HTTPException: If there's a time conflict with existing events
    """
    # Check for time conflicts
    if check_time_conflict(
        db=db,
        start_datetime=event.start_datetime,
        end_datetime=event.end_datetime,
        timezone=event.timezone,
        days_of_week=event.days_of_week,
    ):
        raise HTTPException(
            status_code=409,
            detail="This time slot conflicts with an existing event",
        )

    # Create recurrence rule if days are specified
    recurrence_rule = None
    if event.days_of_week:
        recurrence_rule = RecurrenceRule(days_of_week=event.days_of_week)
        db.add(recurrence_rule)
        db.flush()  # Get the ID without committing

    # Create the event
    db_event = Event(
        name=event.name,
        start_datetime=event.start_datetime,
        end_datetime=event.end_datetime,
        timezone=event.timezone,
        recurrence_rule_id=recurrence_rule.id if recurrence_rule else None,
    )

    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    return db_event
