"""Tests for rule_code in blocked responses."""

import pytest


def test_duplicate_join_has_rule_code(client, db):
    """Duplicate join should return rule_code=DUPLICATE_JOIN."""
    res = client.post("/queues", json={"name": "Rule Q"})
    qid = res.get_json()["id"]
    client.post(f"/queues/{qid}/join", json={"user_name": "Alice"})

    res = client.post(f"/queues/{qid}/join", json={"user_name": "Alice"})
    assert res.status_code == 409
    data = res.get_json()
    assert "rule_code" in data
    assert data["rule_code"] == "DUPLICATE_JOIN"


def test_empty_serve_has_rule_code(client, db):
    """Serving an empty queue should return rule_code=EMPTY_QUEUE."""
    res = client.post("/queues", json={"name": "Rule Q"})
    qid = res.get_json()["id"]

    res = client.patch(f"/queues/{qid}/serve")
    assert res.status_code == 409
    assert res.get_json()["rule_code"] == "EMPTY_QUEUE"


def test_skip_empty_has_rule_code(client, db):
    """Skipping on an empty queue should return rule_code=EMPTY_QUEUE."""
    res = client.post("/queues", json={"name": "Rule Q"})
    qid = res.get_json()["id"]

    res = client.patch(f"/queues/{qid}/skip")
    assert res.status_code == 409
    assert res.get_json()["rule_code"] == "EMPTY_QUEUE"


def test_dry_run_failure_has_rule_code(client, db):
    """Dry-run failures should also include rule_code."""
    res = client.post("/queues", json={"name": "Rule Q"})
    qid = res.get_json()["id"]
    client.post(f"/queues/{qid}/join", json={"user_name": "Alice"})

    res = client.post(f"/queues/{qid}/join?dry_run=true", json={"user_name": "Alice"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["dry_run"] is True
    assert data["result"] == "would_fail"
    assert data["rule_code"] == "DUPLICATE_JOIN"


def test_rule_code_not_present_on_success(client, db):
    """Successful actions should not include rule_code."""
    res = client.post("/queues", json={"name": "Rule Q"})
    qid = res.get_json()["id"]

    res = client.post(f"/queues/{qid}/join", json={"user_name": "Alice"})
    assert res.status_code == 201
    data = res.get_json()
    assert "rule_code" not in data
