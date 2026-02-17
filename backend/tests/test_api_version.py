"""Tests for X-API-Version header in all responses."""

import pytest


def test_api_version_header_on_get(client, db):
    """GET /queues should include X-API-Version header."""
    res = client.get("/queues")
    assert "X-API-Version" in res.headers
    assert res.headers["X-API-Version"] == "v1"


def test_api_version_header_on_post(client, db):
    """POST /queues should include X-API-Version header."""
    res = client.post("/queues", json={"name": "Version Q"})
    assert res.headers["X-API-Version"] == "v1"


def test_api_version_header_on_error(client, db):
    """Error responses should also include X-API-Version header."""
    res = client.patch("/queues/999/serve")
    assert "X-API-Version" in res.headers
    assert res.headers["X-API-Version"] == "v1"
