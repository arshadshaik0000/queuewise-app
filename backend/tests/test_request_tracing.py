"""Tests for request tracing middleware.

Covers:
  1. X-Request-ID header is present in every response.
  2. Request ID is a valid UUID.
  3. Client-supplied X-Request-ID is propagated.
"""

import uuid


def test_response_has_request_id_header(client, db):
    """Every response must include an X-Request-ID header."""
    resp = client.post("/queues", json={"name": "Test"})
    assert resp.status_code == 201
    assert "X-Request-ID" in resp.headers
    assert len(resp.headers["X-Request-ID"]) > 0


def test_request_id_is_valid_uuid(client, db):
    """The generated request ID should be a valid UUID."""
    resp = client.post("/queues", json={"name": "Test"})
    request_id = resp.headers.get("X-Request-ID", "")

    # Should not raise ValueError
    parsed = uuid.UUID(request_id)
    assert str(parsed) == request_id


def test_client_request_id_is_propagated(client, db):
    """If the client sends X-Request-ID, the server should echo it back."""
    custom_id = "client-trace-12345"

    resp = client.post(
        "/queues",
        json={"name": "Test"},
        headers={"X-Request-ID": custom_id},
    )

    assert resp.headers["X-Request-ID"] == custom_id


def test_different_requests_get_different_ids(client, db):
    """Each request should receive a unique request ID."""
    r1 = client.post("/queues", json={"name": "Q1"})
    r2 = client.post("/queues", json={"name": "Q2"})

    id1 = r1.headers["X-Request-ID"]
    id2 = r2.headers["X-Request-ID"]

    assert id1 != id2


def test_request_id_on_get_endpoints(client, db):
    """GET endpoints should also include X-Request-ID."""
    client.post("/queues", json={"name": "Test"})

    resp = client.get("/queues")
    assert "X-Request-ID" in resp.headers
