"""Tests for skip functionality — only the first WAITING user can be skipped.

Covers:
  1. Skip-next picks the first WAITING person.
  2. Skipping preserves queue order for remaining entries.
  3. Skipped users cannot be served later.
  4. Skipped users can rejoin.
  5. Empty-queue skip returns 409.
"""


def _create_queue(client, name="Test Queue"):
    resp = client.post("/queues", json={"name": name})
    assert resp.status_code == 201
    return resp.get_json()


def _join(client, qid, name):
    return client.post(f"/queues/{qid}/join", json={"user_name": name})


def test_skip_next_targets_first_waiting(client, db):
    """PATCH /queues/<id>/skip should skip the first WAITING user."""
    q = _create_queue(client)
    _join(client, q["id"], "Alice")
    _join(client, q["id"], "Bob")

    resp = client.patch(f"/queues/{q['id']}/skip")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["user_name"] == "Alice"
    assert data["status"] == "SKIPPED"


def test_skip_preserves_queue_order(client, db):
    """After skipping the first person, serve picks the next WAITING user."""
    q = _create_queue(client)
    _join(client, q["id"], "Alice")
    _join(client, q["id"], "Bob")
    _join(client, q["id"], "Charlie")

    # Skip Alice
    client.patch(f"/queues/{q['id']}/skip")

    # Serve should pick Bob (not Charlie)
    resp = client.patch(f"/queues/{q['id']}/serve")
    assert resp.status_code == 200
    assert resp.get_json()["user_name"] == "Bob"

    # Next serve should pick Charlie
    resp = client.patch(f"/queues/{q['id']}/serve")
    assert resp.status_code == 200
    assert resp.get_json()["user_name"] == "Charlie"


def test_skipped_user_cannot_be_served(client, db):
    """A skipped user's status is terminal — they cannot be served."""
    q = _create_queue(client)
    _join(client, q["id"], "Alice")

    # Skip Alice
    client.patch(f"/queues/{q['id']}/skip")

    # No one left to serve
    resp = client.patch(f"/queues/{q['id']}/serve")
    assert resp.status_code == 409


def test_skipped_user_can_rejoin(client, db):
    """A skipped user can rejoin since they're no longer WAITING."""
    q = _create_queue(client)
    _join(client, q["id"], "Alice")

    client.patch(f"/queues/{q['id']}/skip")

    resp = _join(client, q["id"], "Alice")
    assert resp.status_code == 201
    assert resp.get_json()["user_name"] == "Alice"


def test_skip_empty_queue_fails(client, db):
    """Skipping with no WAITING users returns 409."""
    q = _create_queue(client)

    resp = client.patch(f"/queues/{q['id']}/skip")
    assert resp.status_code == 409
    assert "error" in resp.get_json()


def test_skip_skips_first_not_arbitrary(client, db):
    """Ensures skip always targets position order, never arbitrary entries."""
    q = _create_queue(client)
    _join(client, q["id"], "Alice")
    _join(client, q["id"], "Bob")
    _join(client, q["id"], "Charlie")

    # First skip → Alice
    r1 = client.patch(f"/queues/{q['id']}/skip")
    assert r1.get_json()["user_name"] == "Alice"

    # Second skip → Bob
    r2 = client.patch(f"/queues/{q['id']}/skip")
    assert r2.get_json()["user_name"] == "Bob"

    # Third skip → Charlie
    r3 = client.patch(f"/queues/{q['id']}/skip")
    assert r3.get_json()["user_name"] == "Charlie"

    # No one left
    r4 = client.patch(f"/queues/{q['id']}/skip")
    assert r4.status_code == 409
