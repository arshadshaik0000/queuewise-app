"""Tests for Rule 8: validate_user_name — name format validation."""

import pytest


def _create_queue(client):
    res = client.post("/queues", json={"name": "Validation Q"})
    return res.get_json()["id"]


# --- Valid names ---

def test_valid_simple_name(client, db):
    """A normal two-letter+ name should be accepted."""
    qid = _create_queue(client)
    res = client.post(f"/queues/{qid}/join", json={"user_name": "Arshad"})
    assert res.status_code == 201


def test_valid_name_with_space(client, db):
    """Names with spaces like 'Mary Jane' should pass."""
    qid = _create_queue(client)
    res = client.post(f"/queues/{qid}/join", json={"user_name": "Mary Jane"})
    assert res.status_code == 201


def test_valid_name_with_hyphen(client, db):
    """Hyphenated names like 'Jean-Pierre' should pass."""
    qid = _create_queue(client)
    res = client.post(f"/queues/{qid}/join", json={"user_name": "Jean-Pierre"})
    assert res.status_code == 201


def test_valid_name_with_apostrophe(client, db):
    """Names with apostrophes like O'Brien should pass."""
    qid = _create_queue(client)
    res = client.post(f"/queues/{qid}/join", json={"user_name": "O'Brien"})
    assert res.status_code == 201


# --- Invalid names ---

def test_reject_single_character(client, db):
    """Single character names should be rejected."""
    qid = _create_queue(client)
    res = client.post(f"/queues/{qid}/join", json={"user_name": "A"})
    # min=2 in schema → 400 from Marshmallow before Rule 8 even runs
    assert res.status_code == 400


def test_reject_pure_number(client, db):
    """Pure numbers like '42' should be rejected with INVALID_NAME."""
    qid = _create_queue(client)
    res = client.post(f"/queues/{qid}/join", json={"user_name": "42"})
    assert res.status_code == 409
    assert res.get_json()["rule_code"] == "INVALID_NAME"


def test_reject_number_string(client, db):
    """Number-like strings like '1' are caught by schema (too short) or rule."""
    qid = _create_queue(client)
    res = client.post(f"/queues/{qid}/join", json={"user_name": "1"})
    # min=2 in schema → 400
    assert res.status_code == 400


def test_reject_name_with_digits(client, db):
    """Names containing digits like 'User1' should be rejected."""
    qid = _create_queue(client)
    res = client.post(f"/queues/{qid}/join", json={"user_name": "User1"})
    assert res.status_code == 409
    assert res.get_json()["rule_code"] == "INVALID_NAME"


def test_reject_special_characters(client, db):
    """Names with special characters like 'A@B' should be rejected."""
    qid = _create_queue(client)
    res = client.post(f"/queues/{qid}/join", json={"user_name": "A@B"})
    assert res.status_code == 409
    assert res.get_json()["rule_code"] == "INVALID_NAME"


def test_reject_empty_string(client, db):
    """Empty string should be rejected by schema validation."""
    qid = _create_queue(client)
    res = client.post(f"/queues/{qid}/join", json={"user_name": ""})
    assert res.status_code == 400
