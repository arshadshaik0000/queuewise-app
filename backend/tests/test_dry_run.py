"""Tests for dry-run mode — rules execute but no database state changes.

Covers:
  1. Dry-run join succeeds without persisting.
  2. Dry-run join fails on rule violation.
  3. Dry-run serve succeeds without persisting.
  4. Dry-run skip succeeds without persisting.
  5. Database state is unchanged after dry-run.
"""


def _create_queue(client, name="Test Queue"):
    resp = client.post("/queues", json={"name": name})
    assert resp.status_code == 201
    return resp.get_json()


def _join(client, qid, name):
    return client.post(f"/queues/{qid}/join", json={"user_name": name})


def test_dry_run_join_would_succeed(client, db):
    """Dry-run join returns would_succeed without creating an entry."""
    q = _create_queue(client)

    resp = client.post(
        f"/queues/{q['id']}/join?dry_run=true",
        json={"user_name": "Alice"},
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["dry_run"] is True
    assert data["result"] == "would_succeed"
    assert data["user_name"] == "Alice"

    # Verify no entry was actually created
    status = client.get(f"/queues/{q['id']}/status").get_json()
    assert len(status["entries"]) == 0


def test_dry_run_join_would_fail(client, db):
    """Dry-run join returns would_fail when rules would be violated."""
    q = _create_queue(client)
    _join(client, q["id"], "Alice")  # Real join

    resp = client.post(
        f"/queues/{q['id']}/join?dry_run=true",
        json={"user_name": "Alice"},
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["dry_run"] is True
    assert data["result"] == "would_fail"
    assert "already waiting" in data["reason"].lower()


def test_dry_run_serve_would_succeed(client, db):
    """Dry-run serve returns would_succeed without changing status."""
    q = _create_queue(client)
    _join(client, q["id"], "Alice")

    resp = client.patch(f"/queues/{q['id']}/serve?dry_run=true")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["dry_run"] is True
    assert data["result"] == "would_succeed"
    assert data["user_name"] == "Alice"

    # Verify Alice is still WAITING
    status = client.get(f"/queues/{q['id']}/status").get_json()
    assert status["entries"][0]["status"] == "WAITING"


def test_dry_run_skip_would_succeed(client, db):
    """Dry-run skip returns would_succeed without changing status."""
    q = _create_queue(client)
    _join(client, q["id"], "Alice")

    resp = client.patch(f"/queues/{q['id']}/skip?dry_run=true")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["dry_run"] is True
    assert data["result"] == "would_succeed"
    assert data["user_name"] == "Alice"

    # Verify Alice is still WAITING
    status = client.get(f"/queues/{q['id']}/status").get_json()
    assert status["entries"][0]["status"] == "WAITING"


def test_dry_run_no_database_mutation(client, db):
    """Multiple dry-runs should leave database completely untouched."""
    q = _create_queue(client)
    _join(client, q["id"], "Alice")
    _join(client, q["id"], "Bob")

    # Run several dry-run operations
    client.patch(f"/queues/{q['id']}/serve?dry_run=true")
    client.patch(f"/queues/{q['id']}/skip?dry_run=true")
    client.post(
        f"/queues/{q['id']}/join?dry_run=true",
        json={"user_name": "Charlie"},
    )

    # Verify state is completely unchanged
    status = client.get(f"/queues/{q['id']}/status").get_json()
    assert len(status["entries"]) == 2
    assert all(e["status"] == "WAITING" for e in status["entries"])
    assert status["entries"][0]["user_name"] == "Alice"
    assert status["entries"][1]["user_name"] == "Bob"
