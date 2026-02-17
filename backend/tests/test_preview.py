"""Tests for GET /queues/<id>/preview — read-only simulation."""

import pytest


def _setup_queue(client, db, n_users=3):
    """Helper: create a queue and add n users."""
    names = ["Alice", "Bob", "Charlie", "Dana", "Eve"]
    res = client.post("/queues", json={"name": "Preview Q"})
    qid = res.get_json()["id"]
    for i in range(n_users):
        client.post(f"/queues/{qid}/join", json={"user_name": names[i]})
    return qid


def test_preview_shows_next_serve_and_skip(client, db):
    """Preview should report who gets served/skipped next."""
    qid = _setup_queue(client, db)
    res = client.get(f"/queues/{qid}/preview")
    assert res.status_code == 200
    data = res.get_json()
    assert data["next_if_served"] == "Alice"
    assert data["skip_target"] == "Alice"
    assert data["next_if_skipped"] == "Bob"


def test_preview_is_read_only(client, db):
    """Preview must NOT modify any entries."""
    qid = _setup_queue(client, db, n_users=2)

    # Preview twice — should always report same state
    r1 = client.get(f"/queues/{qid}/preview")
    r2 = client.get(f"/queues/{qid}/preview")
    assert r1.get_json() == r2.get_json()

    # Queue status should show all entries still WAITING
    status = client.get(f"/queues/{qid}/status").get_json()
    waiting = [e for e in status["entries"] if e["status"] == "WAITING"]
    assert len(waiting) == 2


def test_preview_projected_wait(client, db):
    """Preview should include a projected wait change string."""
    qid = _setup_queue(client, db)
    res = client.get(f"/queues/{qid}/preview")
    data = res.get_json()
    assert "projected_wait_change" in data
    assert len(data["projected_wait_change"]) > 0


def test_preview_empty_queue_fails(client, db):
    """Preview on an empty queue should return 404 with rule_code."""
    res = client.post("/queues", json={"name": "Empty Q"})
    qid = res.get_json()["id"]
    res = client.get(f"/queues/{qid}/preview")
    assert res.status_code == 404
    assert res.get_json()["rule_code"] == "EMPTY_QUEUE"


def test_preview_nonexistent_queue(client, db):
    """Preview on a non-existent queue should return 404."""
    res = client.get("/queues/999/preview")
    assert res.status_code == 404
