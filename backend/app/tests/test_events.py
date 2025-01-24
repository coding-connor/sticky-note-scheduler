from datetime import datetime, timedelta

import pytest
from fastapi import status
from pydantic import ValidationError

from app.schemas.event import EventCreate


def test_create_event(client):
    """Test creating a single event without recurrence."""
    event_data = {
        "name": "Team Meeting",
        "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "duration": 60,
    }

    response = client.post("/api/events/", json=event_data)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == event_data["name"]
    assert "id" in data
    assert "end_time" in data
    assert data["recurrence"] is None


def test_create_recurring_event(client):
    """Test creating an event with weekly recurrence."""
    event_data = {
        "name": "Weekly Standup",
        "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "duration": 30,
        "days_of_week": ["MONDAY", "WEDNESDAY"],
    }

    response = client.post("/api/events/", json=event_data)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == event_data["name"]
    assert "id" in data
    assert data["recurrence"] is not None
    assert data["recurrence"]["days_of_week"] == event_data["days_of_week"]


def test_event_time_conflict(client):
    """Test that overlapping events are rejected."""
    # Create first event
    base_time = datetime.now() + timedelta(days=1, hours=10)
    event1_data = {
        "name": "First Meeting",
        "start_time": base_time.isoformat(),
        "duration": 60,
    }
    response = client.post("/api/events/", json=event1_data)
    assert response.status_code == status.HTTP_200_OK

    # Try to create overlapping event
    start_time = base_time + timedelta(minutes=30)
    event2_data = {
        "name": "Second Meeting",
        "start_time": start_time.isoformat(),
        "duration": 60,
    }
    response = client.post("/api/events/", json=event2_data)
    assert response.status_code == status.HTTP_409_CONFLICT


def test_recurring_event_conflict(client):
    """Test that recurring events check for conflicts on specific days."""
    # Create recurring event
    start_time = datetime.now() + timedelta(days=1, hours=10)
    event1_data = {
        "name": "Weekly Meeting",
        "start_time": start_time.isoformat(),
        "duration": 60,
        "days_of_week": ["MONDAY", "WEDNESDAY"],
    }
    response = client.post("/api/events/", json=event1_data)
    assert response.status_code == status.HTTP_200_OK

    # Try to create conflicting event on same day/time
    event2_data = {
        "name": "Another Meeting",
        "start_time": start_time.isoformat(),
        "duration": 30,
        "days_of_week": ["WEDNESDAY", "FRIDAY"],
    }
    response = client.post("/api/events/", json=event2_data)
    assert response.status_code == status.HTTP_409_CONFLICT


def test_event_validation():
    """Test event validation rules."""
    base_time = datetime.now()

    # Test empty name
    with pytest.raises(ValidationError, match="Name cannot be empty"):
        EventCreate(
            name="   ",
            start_time=base_time,
            duration=30,
        )

    # Test negative duration
    with pytest.raises(ValidationError, match="Duration must be positive"):
        EventCreate(
            name="Test Event",
            start_time=base_time,
            duration=-30,
        )

    # Test zero duration
    with pytest.raises(ValidationError, match="Duration must be positive"):
        EventCreate(
            name="Test Event",
            start_time=base_time,
            duration=0,
        )

    # Test empty days_of_week list
    with pytest.raises(ValidationError) as exc:
        EventCreate(
            name="Test Event",
            start_time=base_time,
            duration=30,
            days_of_week=[],
        )
    assert "Days of week cannot be empty when provided" in str(exc.value)

    # Test invalid weekday
    with pytest.raises(ValidationError):
        EventCreate(
            name="Test Event",
            start_time=base_time,
            duration=30,
            days_of_week=["INVALID_DAY"],
        )

    # Test duplicate weekdays
    with pytest.raises(ValidationError) as exc:
        EventCreate(
            name="Test Event",
            start_time=base_time,
            duration=30,
            days_of_week=["MONDAY", "MONDAY"],
        )
    assert "Days of week must be unique" in str(exc.value)


def test_get_events(client):
    """Test getting a list of events."""
    # Create a few events
    events = [
        {
            "name": f"Event {i}",
            "start_time": (datetime.now() + timedelta(days=i)).isoformat(),
            "duration": 30,
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
    assert all(isinstance(event["start_time"], str) for event in data)
    assert all(isinstance(event["end_time"], str) for event in data)
