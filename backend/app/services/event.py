from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.models.event import Event, RecurrenceRule, Weekday


def get_time_overlap_conditions(start_datetime: datetime, end_datetime: datetime):
    """Returns SQLAlchemy filter conditions for checking time overlaps.

    Args:
        start_datetime: Start time to check
        end_datetime: End time to check

    Returns:
        SQLAlchemy OR condition containing all overlap cases
    """
    return or_(
        # Case 1: Event starts during our event
        and_(
            Event.start_datetime.time() >= start_datetime.time(),
            Event.start_datetime.time() < end_datetime.time(),
        ),
        # Case 2: Event ends during our event
        and_(
            Event.end_datetime.time() > start_datetime.time(),
            Event.end_datetime.time() <= end_datetime.time(),
        ),
        # Case 3: Event completely surrounds our event
        and_(
            Event.start_datetime.time() <= start_datetime.time(),
            Event.end_datetime.time() >= end_datetime.time(),
        ),
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


def check_recurrence_x_anchor_conflict(
    db: Session,
    start_datetime: datetime,
    end_datetime: datetime,
    days_of_week: List[Weekday],
) -> bool:
    """Check if a new event's recurrence pattern conflicts with any future events' anchor dates.

    Args:
        db: Database session
        start_datetime: Start time of new event
        end_datetime: End time of new event
        days_of_week: Days on which the new event repeats

    Returns:
        bool: True if there's a conflict, False otherwise
    """
    # Get all future events
    future_events = (
        db.query(Event)
        .filter(
            # Only get events after our start date
            Event.start_datetime >= start_datetime,
            # Convert its start date to a weekday and check if it's in the new event's recurrence pattern
            func.upper(func.strftime("%A", Event.start_datetime)).in_([day.value for day in days_of_week]),
            # Check time overlap
            get_time_overlap_conditions(start_datetime, end_datetime),
        )
        .all()
    )

    return len(future_events) > 0


def check_anchor_x_recurrence_conflict(
    db: Session,
    start_datetime: datetime,
    end_datetime: datetime,
) -> bool:
    anchor_weekday = Weekday(start_datetime.strftime("%A").upper())

    conflicts = (
        db.query(Event)
        .join(Event.recurrence_rule)
        .filter(
            Event.recurrence_rule_id.isnot(None),
            Event.start_datetime <= end_datetime,
            RecurrenceRule.days_of_week.contains([anchor_weekday]),
            get_time_overlap_conditions(start_datetime, end_datetime),
        )
        .all()
    )
    return len(conflicts) > 0


def check_recurrence_x_recurrence_conflict(
    db: Session,
    start_datetime: datetime,
    end_datetime: datetime,
    days_of_week: List[Weekday],
) -> bool:
    conflicts = (
        db.query(Event)
        .join(Event.recurrence_rule)
        .filter(
            Event.recurrence_rule_id.isnot(None),
            or_(*[RecurrenceRule.days_of_week.like(f'%"{day.value}"%') for day in days_of_week]),
            get_time_overlap_conditions(start_datetime, end_datetime),
        )
        .all()
    )
    return len(conflicts) > 0


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
