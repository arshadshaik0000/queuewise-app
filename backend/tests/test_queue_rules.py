"""Tests for queue business rules and API endpoints.

Covers:
  1. Successful join
  2. Duplicate join blocked
  3. Successful serve
  4. Cannot serve out of order
  5. Skip functionality
  6. List queues
  7. Per-user wait explanations
"""

import json


# -- Helper ------------------------------------------------------------------

def _create_queue(client, name="Test Queue"):
    """Create a queue and return the JSON response."""
    resp = client.post("/queues", json={"name": name})
    assert resp.status_code == 201
    return resp.get_json()


def _join_queue(client, queue_id, user_name):
    """Attempt to join a queue and return the response."""
    return client.post(f"/queues/{queue_id}/join", json={"user_name": user_name})


def _serve_next(client, queue_id):
    """Attempt to serve the next person and return the response."""
    return client.patch(f"/queues/{queue_id}/serve")


def _skip_user(client, queue_id, entry_id):
    """Attempt to skip a user and return the response."""
    return client.patch(f"/queues/{queue_id}/skip/{entry_id}")


# -- Original Tests ----------------------------------------------------------

def test_successful_join(client, db):
    """A user should be able to join an existing queue."""
    queue = _create_queue(client)
    resp = _join_queue(client, queue["id"], "Alice")

    assert resp.status_code == 201
    data = resp.get_json()
    assert data["user_name"] == "Alice"
    assert data["position"] == 1
    assert data["status"] == "WAITING"


def test_duplicate_join_blocked(client, db):
    """The same user cannot join a queue twice while still WAITING."""
    queue = _create_queue(client)
    _join_queue(client, queue["id"], "Alice")

    # Second join with the same name should be rejected
    resp = _join_queue(client, queue["id"], "Alice")

    assert resp.status_code == 409
    data = resp.get_json()
    assert "error" in data
    assert "already waiting" in data["error"].lower()


def test_successful_serve(client, db):
    """The first waiting person in a queue can be served."""
    queue = _create_queue(client)
    _join_queue(client, queue["id"], "Alice")

    resp = _serve_next(client, queue["id"])

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["user_name"] == "Alice"
    assert data["status"] == "SERVED"


def test_cannot_serve_out_of_order(client, db):
    """Serving must follow queue order — only the first person gets served."""
    queue = _create_queue(client)
    _join_queue(client, queue["id"], "Alice")
    _join_queue(client, queue["id"], "Bob")

    # Serve first -> should be Alice
    resp1 = _serve_next(client, queue["id"])
    assert resp1.status_code == 200
    assert resp1.get_json()["user_name"] == "Alice"

    # Serve second -> should be Bob (not anyone else)
    resp2 = _serve_next(client, queue["id"])
    assert resp2.status_code == 200
    assert resp2.get_json()["user_name"] == "Bob"

    # No one left to serve
    resp3 = _serve_next(client, queue["id"])
    assert resp3.status_code == 409
    assert "error" in resp3.get_json()


def test_queue_status_endpoint(client, db):
    """GET /queues/<id>/status returns entries and an AI explanation."""
    queue = _create_queue(client, "Clinic A")
    _join_queue(client, queue["id"], "Alice")
    _join_queue(client, queue["id"], "Bob")

    resp = client.get(f"/queues/{queue['id']}/status")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["queue_name"] == "Clinic A"
    assert len(data["entries"]) == 2
    assert "explanation" in data
    # AI explanation should mention who's next
    assert "Alice" in data["explanation"]


# -- New Enhancement Tests ---------------------------------------------------

def test_skip_user(client, db):
    """A WAITING user can be skipped, and their status becomes SKIPPED."""
    queue = _create_queue(client)
    join_resp = _join_queue(client, queue["id"], "Alice")
    entry_id = join_resp.get_json()["entry_id"]

    resp = _skip_user(client, queue["id"], entry_id)

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["user_name"] == "Alice"
    assert data["status"] == "SKIPPED"


def test_skip_already_served_blocked(client, db):
    """A SERVED user cannot be skipped."""
    queue = _create_queue(client)
    join_resp = _join_queue(client, queue["id"], "Alice")
    entry_id = join_resp.get_json()["entry_id"]

    # Serve Alice first
    _serve_next(client, queue["id"])

    # Try to skip — should fail
    resp = _skip_user(client, queue["id"], entry_id)
    assert resp.status_code == 409
    assert "error" in resp.get_json()


def test_skip_advances_queue(client, db):
    """After skipping the first person, serve should pick the next WAITING person."""
    queue = _create_queue(client)
    join1 = _join_queue(client, queue["id"], "Alice")
    _join_queue(client, queue["id"], "Bob")

    # Skip Alice
    _skip_user(client, queue["id"], join1.get_json()["entry_id"])

    # Serve next — should be Bob (Alice was skipped)
    resp = _serve_next(client, queue["id"])
    assert resp.status_code == 200
    assert resp.get_json()["user_name"] == "Bob"


def test_list_queues(client, db):
    """GET /queues returns all queues with waiting counts."""
    _create_queue(client, "Clinic A")
    _create_queue(client, "Salon B")
    _join_queue(client, 1, "Alice")

    resp = client.get("/queues")

    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 2
    # Most recent queue first
    assert data[0]["name"] == "Salon B"
    assert data[1]["name"] == "Clinic A"
    assert data[1]["waiting_count"] == 1


def test_per_user_wait_explanations(client, db):
    """Status response includes per-user wait explanations for WAITING entries."""
    queue = _create_queue(client, "Clinic A")
    _join_queue(client, queue["id"], "Alice")
    _join_queue(client, queue["id"], "Bob")

    resp = client.get(f"/queues/{queue['id']}/status")
    data = resp.get_json()

    assert "wait_explanations" in data
    assert "Alice" in data["wait_explanations"]
    assert "Bob" in data["wait_explanations"]
    # Alice is first, so she should be told she's next
    assert "next" in data["wait_explanations"]["Alice"].lower()
    # Bob has 1 person ahead
    assert "1" in data["wait_explanations"]["Bob"]


def test_rejoin_after_skip(client, db):
    """A user who was skipped can rejoin the queue."""
    queue = _create_queue(client)
    join_resp = _join_queue(client, queue["id"], "Alice")
    entry_id = join_resp.get_json()["entry_id"]

    # Skip Alice
    _skip_user(client, queue["id"], entry_id)

    # Alice can rejoin since she's no longer WAITING
    resp = _join_queue(client, queue["id"], "Alice")
    assert resp.status_code == 201
    assert resp.get_json()["user_name"] == "Alice"
