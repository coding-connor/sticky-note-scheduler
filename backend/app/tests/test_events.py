from datetime import datetime, timedelta

from app.models.event import Weekday


def test_create_event(client):
    """Test creating a single event without recurrence."""
    event_data = {
        "name": "Team Meeting",
        "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
    }

    response = client.post("/api/events/", json=event_data)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == event_data["name"]
    assert "id" in data
    assert data["recurrence"] is None


def test_create_recurring_event(client):
    """Test creating an event with weekly recurrence."""
    event_data = {
        "name": "Weekly Standup",
        "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
        "days_of_week": [Weekday.MONDAY.value, Weekday.WEDNESDAY.value],
    }

    response = client.post("/api/events/", json=event_data)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == event_data["name"]
    assert "id" in data
    assert data["recurrence"] is not None
    assert data["recurrence"]["days_of_week"] == event_data["days_of_week"]


def test_get_event(client):
    """Test getting a single event."""
    # First create an event
    event_data = {
        "name": "Team Meeting",
        "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
    }
    create_response = client.post("/api/events/", json=event_data)
    event_id = create_response.json()["id"]

    # Then get it
    response = client.get(f"/api/events/{event_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == event_data["name"]


def test_get_event_not_found(client):
    """Test getting a non-existent event."""
    test_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/events/{test_uuid}")
    assert response.status_code == 404


def test_get_events(client):
    """Test getting a list of events."""
    # Create a few events
    events = [
        {
            "name": f"Event {i}",
            "start_time": (datetime.now() + timedelta(days=i)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=i, hours=1)).isoformat(),
        }
        for i in range(3)
    ]

    for event in events:
        client.post("/api/events/", json=event)

    response = client.get("/api/events/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(event["name"].startswith("Event") for event in data)
