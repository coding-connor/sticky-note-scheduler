from datetime import datetime, timedelta

import pytest
from fastapi import status
from pydantic import ValidationError

from app.schemas.event import EventCreate


def test_create_event(client):
    """Test creating a single event without recurrence."""
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(minutes=60)
    event_data = {
        "name": "Team Meeting",
        "start_datetime": start_time.isoformat(),
        "end_datetime": end_time.isoformat(),
        "timezone": "America/Los_Angeles",
    }

    response = client.post("/api/events/", json=event_data)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == event_data["name"]
    assert "id" in data
    assert data["start_datetime"] == event_data["start_datetime"]
    assert data["end_datetime"] == event_data["end_datetime"]
    assert data["timezone"] == event_data["timezone"]
    assert data["recurrence_rule"] is None


def test_create_recurring_event(client):
    """Test creating an event with weekly recurrence."""
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(minutes=30)
    event_data = {
        "name": "Weekly Standup",
        "start_datetime": start_time.isoformat(),
        "end_datetime": end_time.isoformat(),
        "timezone": "America/Los_Angeles",
        "days_of_week": ["MONDAY", "WEDNESDAY"],
    }

    response = client.post("/api/events/", json=event_data)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == event_data["name"]
    assert "id" in data
    assert data["start_datetime"] == event_data["start_datetime"]
    assert data["end_datetime"] == event_data["end_datetime"]
    assert data["timezone"] == event_data["timezone"]
    assert data["recurrence_rule"] is not None
    assert data["recurrence_rule"]["days_of_week"] == event_data["days_of_week"]


def test_event_time_conflict(client):
    """Test that overlapping events are rejected."""
    # Create first event
    base_time = datetime.now() + timedelta(days=1, hours=10)
    end_time = base_time + timedelta(minutes=60)
    event1_data = {
        "name": "First Meeting",
        "start_datetime": base_time.isoformat(),
        "end_datetime": end_time.isoformat(),
        "timezone": "America/Los_Angeles",
    }
    response = client.post("/api/events/", json=event1_data)
    assert response.status_code == status.HTTP_200_OK

    # Try to create overlapping event
    start_time = base_time + timedelta(minutes=30)
    end_time = start_time + timedelta(minutes=60)
    event2_data = {
        "name": "Second Meeting",
        "start_datetime": start_time.isoformat(),
        "end_datetime": end_time.isoformat(),
        "timezone": "America/Los_Angeles",
    }
    response = client.post("/api/events/", json=event2_data)
    assert response.status_code == status.HTTP_409_CONFLICT


def test_recurring_event_conflict(client):
    """Test that recurring events check for conflicts on specific days."""
    # Create recurring event
    start_time = datetime.now() + timedelta(days=1, hours=10)
    end_time = start_time + timedelta(minutes=60)
    event1_data = {
        "name": "Weekly Meeting",
        "start_datetime": start_time.isoformat(),
        "end_datetime": end_time.isoformat(),
        "timezone": "America/Los_Angeles",
        "days_of_week": ["MONDAY", "WEDNESDAY"],
    }
    response = client.post("/api/events/", json=event1_data)
    assert response.status_code == status.HTTP_200_OK

    # Try to create conflicting event on same day/time
    event2_data = {
        "name": "Another Meeting",
        "start_datetime": start_time.isoformat(),
        "end_datetime": end_time.isoformat(),
        "timezone": "America/Los_Angeles",
        "days_of_week": ["WEDNESDAY", "FRIDAY"],
    }
    response = client.post("/api/events/", json=event2_data)
    assert response.status_code == status.HTTP_409_CONFLICT


def test_event_validation(client):
    """Test event validation rules."""
    base_time = datetime.now()
    end_time = base_time + timedelta(minutes=30)

    # Test empty name
    with pytest.raises(ValidationError, match="Name cannot be empty"):
        EventCreate(
            name="   ",
            start_datetime=base_time,
            end_datetime=end_time,
            timezone="America/Los_Angeles",
        )

    # Test invalid timezone
    with pytest.raises(ValidationError, match="Invalid timezone"):
        EventCreate(
            name="Test Event",
            start_datetime=base_time,
            end_datetime=end_time,
            timezone="Invalid/Timezone",
        )

    # Test end time before start time
    with pytest.raises(ValidationError, match="Event must end after it starts"):
        EventCreate(
            name="Test Event",
            start_datetime=end_time,
            end_datetime=base_time,
            timezone="America/Los_Angeles",
        )

    # Test empty days_of_week list
    with pytest.raises(ValidationError) as exc:
        EventCreate(
            name="Test Event",
            start_datetime=base_time,
            end_datetime=end_time,
            timezone="America/Los_Angeles",
            days_of_week=[],
        )
    assert "Days of week cannot be empty when provided" in str(exc.value)

    # Test invalid weekday
    with pytest.raises(ValidationError):
        EventCreate(
            name="Test Event",
            start_datetime=base_time,
            end_datetime=end_time,
            timezone="America/Los_Angeles",
            days_of_week=["INVALID_DAY"],
        )

    # Test duplicate weekdays
    with pytest.raises(ValidationError, match="Days of week must be unique"):
        EventCreate(
            name="Test Event",
            start_datetime=base_time,
            end_datetime=end_time,
            timezone="America/Los_Angeles",
            days_of_week=["MONDAY", "MONDAY"],
        )


def test_get_events(client):
    """Test getting a list of events."""
    # Create a few events
    base_time = datetime.now()
    events = [
        {
            "name": f"Event {i}",
            "start_datetime": (base_time + timedelta(days=i)).isoformat(),
            "end_datetime": (base_time + timedelta(days=i, minutes=30)).isoformat(),
            "timezone": "America/Los_Angeles",
        }
        for i in range(3)
    ]

    for event in events:
        response = client.post("/api/events/", json=event)
        assert response.status_code == status.HTTP_200_OK

    response = client.get("/api/events/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 3  # Could be more if other tests added events
    assert all(isinstance(event["id"], str) for event in data)
    assert all(isinstance(event["name"], str) for event in data)
    assert all(isinstance(event["start_datetime"], str) for event in data)
    assert all(isinstance(event["end_datetime"], str) for event in data)
    assert all(isinstance(event["timezone"], str) for event in data)
