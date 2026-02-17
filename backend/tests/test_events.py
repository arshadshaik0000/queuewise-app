"""Tests for GET /queues/<id>/events — observability timeline."""

import pytest


def test_events_returns_data_after_actions(client, db):
    """After join + serve, events endpoint should return matching entries."""
    res = client.post("/queues", json={"name": "Events Q"})
    qid = res.get_json()["id"]
    client.post(f"/queues/{qid}/join", json={"user_name": "Alice"})
    client.patch(f"/queues/{qid}/serve")

    res = client.get(f"/queues/{qid}/events")
    assert res.status_code == 200
    events = res.get_json()
    assert len(events) >= 2  # at least JOIN + SERVE

    actions = [e["action"] for e in events]
    assert "JOIN" in actions
    assert "SERVE" in actions


def test_events_has_request_id(client, db):
    """Each event should include a request_id for tracing."""
    res = client.post("/queues", json={"name": "Events Q"})
    qid = res.get_json()["id"]
    client.post(f"/queues/{qid}/join", json={"user_name": "Alice"})

    events = client.get(f"/queues/{qid}/events").get_json()
    for event in events:
        assert "request_id" in event


def test_events_ordered_newest_first(client, db):
    """Events should be returned with newest first."""
    res = client.post("/queues", json={"name": "Events Q"})
    qid = res.get_json()["id"]
    client.post(f"/queues/{qid}/join", json={"user_name": "Alice"})
    client.post(f"/queues/{qid}/join", json={"user_name": "Bob"})

    events = client.get(f"/queues/{qid}/events").get_json()
    # Newest first → last action's event is at index 0
    assert events[0]["action"] == "JOIN"  # Bob's join is newest


def test_events_empty_queue(client, db):
    """Events on a queue with no actions should return empty list."""
    res = client.post("/queues", json={"name": "Empty Events Q"})
    qid = res.get_json()["id"]

    res = client.get(f"/queues/{qid}/events")
    assert res.status_code == 200
    assert res.get_json() == []


def test_events_nonexistent_queue(client, db):
    """Events for a nonexistent queue should return 404."""
    res = client.get("/queues/999/events")
    assert res.status_code == 404
