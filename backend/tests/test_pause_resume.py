"""Tests for queue pause/resume — join blocked when paused."""

import pytest


def _create_queue(client, db, name="Pause Q"):
    res = client.post("/queues", json={"name": name})
    return res.get_json()["id"]


def test_pause_blocks_join(client, db):
    """A paused queue should reject join attempts with QUEUE_PAUSED."""
    qid = _create_queue(client, db)
    client.patch(f"/queues/{qid}/pause")

    res = client.post(f"/queues/{qid}/join", json={"user_name": "Alice"})
    assert res.status_code == 409
    assert res.get_json()["rule_code"] == "QUEUE_PAUSED"


def test_pause_allows_serve(client, db):
    """Serve should still work on a paused queue."""
    qid = _create_queue(client, db)
    client.post(f"/queues/{qid}/join", json={"user_name": "Alice"})
    client.patch(f"/queues/{qid}/pause")

    res = client.patch(f"/queues/{qid}/serve")
    assert res.status_code == 200
    assert res.get_json()["user_name"] == "Alice"


def test_pause_allows_skip(client, db):
    """Skip should still work on a paused queue."""
    qid = _create_queue(client, db)
    client.post(f"/queues/{qid}/join", json={"user_name": "Alice"})
    client.patch(f"/queues/{qid}/pause")

    res = client.patch(f"/queues/{qid}/skip")
    assert res.status_code == 200
    assert res.get_json()["user_name"] == "Alice"


def test_resume_allows_join(client, db):
    """After resuming, joins should work normally again."""
    qid = _create_queue(client, db)
    client.patch(f"/queues/{qid}/pause")
    client.patch(f"/queues/{qid}/resume")

    res = client.post(f"/queues/{qid}/join", json={"user_name": "Bob"})
    assert res.status_code == 201


def test_double_pause_fails(client, db):
    """Pausing an already paused queue should error."""
    qid = _create_queue(client, db)
    client.patch(f"/queues/{qid}/pause")

    res = client.patch(f"/queues/{qid}/pause")
    assert res.status_code == 409
    assert res.get_json()["rule_code"] == "ALREADY_PAUSED"


def test_double_resume_fails(client, db):
    """Resuming an active queue should error."""
    qid = _create_queue(client, db)

    res = client.patch(f"/queues/{qid}/resume")
    assert res.status_code == 409
    assert res.get_json()["rule_code"] == "ALREADY_ACTIVE"


def test_queue_list_shows_status(client, db):
    """GET /queues should include queue status field."""
    qid = _create_queue(client, db)
    client.patch(f"/queues/{qid}/pause")

    res = client.get("/queues")
    queues = res.get_json()
    paused_q = [q for q in queues if q["id"] == qid][0]
    assert paused_q["status"] == "PAUSED"
