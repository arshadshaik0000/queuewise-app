"""Tests for the derived-data summary endpoint.

Covers:
  1. Summary returns correct counts.
  2. Summary includes AI-generated explanation.
  3. Summary with mixed statuses (waiting, served, skipped).
  4. Summary for empty queue.
"""


def _create_queue(client, name="Test Queue"):
    resp = client.post("/queues", json={"name": name})
    assert resp.status_code == 201
    return resp.get_json()


def _join(client, qid, name):
    return client.post(f"/queues/{qid}/join", json={"user_name": name})


def test_summary_counts(client, db):
    """GET /queues/<id>/summary returns correct waiting/served/skipped counts."""
    q = _create_queue(client)
    _join(client, q["id"], "Alice")
    _join(client, q["id"], "Bob")
    _join(client, q["id"], "Charlie")

    # Serve Alice
    client.patch(f"/queues/{q['id']}/serve")
    # Skip Bob (he's now first WAITING)
    client.patch(f"/queues/{q['id']}/skip")

    resp = client.get(f"/queues/{q['id']}/summary")
    assert resp.status_code == 200
    data = resp.get_json()

    assert data["queue_name"] == "Test Queue"
    assert data["waiting_count"] == 1    # Charlie
    assert data["served_count"] == 1     # Alice
    assert data["skipped_count"] == 1    # Bob


def test_summary_has_explanation(client, db):
    """Summary includes an AI-generated explanation string."""
    q = _create_queue(client)
    _join(client, q["id"], "Alice")

    resp = client.get(f"/queues/{q['id']}/summary")
    data = resp.get_json()

    assert "explanation" in data
    assert len(data["explanation"]) > 0
    assert "Alice" in data["explanation"]


def test_summary_has_estimated_wait(client, db):
    """Summary includes estimated wait for the last waiting person."""
    q = _create_queue(client)
    _join(client, q["id"], "Alice")
    _join(client, q["id"], "Bob")

    resp = client.get(f"/queues/{q['id']}/summary")
    data = resp.get_json()

    assert "estimated_wait" in data
    assert len(data["estimated_wait"]) > 0


def test_summary_empty_queue(client, db):
    """Summary for an empty queue returns zero counts."""
    q = _create_queue(client)

    resp = client.get(f"/queues/{q['id']}/summary")
    data = resp.get_json()

    assert data["waiting_count"] == 0
    assert data["served_count"] == 0
    assert data["skipped_count"] == 0
    assert "empty" in data["explanation"].lower()


def test_summary_nonexistent_queue(client, db):
    """Summary for a nonexistent queue returns 404."""
    resp = client.get("/queues/999/summary")
    assert resp.status_code == 404
