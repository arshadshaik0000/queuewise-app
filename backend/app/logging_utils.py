"""Structured logging, request tracing, and API versioning.

Provides:
  1. Request tracing — UUID request_id per request on flask.g + X-Request-ID header.
  2. Structured JSON logging — log_event() with request_id from g context.
  3. Event persistence — persist_event() writes to QueueEvent table.
  4. API versioning — X-API-Version header on every response.

None of these modify business logic or routes.
"""

import logging
import json
import uuid
from typing import Optional

from flask import Flask, g, request as flask_request

logger = logging.getLogger("queuewise")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

# Current API version — single source of truth
API_VERSION = "v1"


def _get_request_id() -> str:
    """Get the current request_id from Flask g context, or generate one."""
    try:
        return g.request_id
    except AttributeError:
        return str(uuid.uuid4())[:8]


def log_event(queue_id: int, action: str, result: str, extra: Optional[dict] = None):
    """Emit a structured log entry AND persist to event table."""
    request_id = _get_request_id()
    record = {
        "request_id": request_id,
        "queue_id": queue_id,
        "action": action,
        "result": result,
    }
    if extra:
        record.update(extra)

    logger.info(json.dumps(record))

    # Persist to database for the /events endpoint
    _persist_event(queue_id, action, result, extra, request_id)


def _persist_event(queue_id: int, action: str, result: str,
                   extra: Optional[dict], request_id: str):
    """Write event to QueueEvent table. Fails silently if out of app context."""
    try:
        from app.repositories import queue_repository as repo
        detail = json.dumps(extra) if extra else ""
        repo.add_event(queue_id, action, result, detail, request_id)
    except Exception:
        pass  # Event logging is non-critical — never break the main flow


def register_request_tracing(app: Flask):
    """Register before/after-request hooks for request tracing and API versioning.

    - Generates UUID request_id per request → flask.g
    - Returns X-Request-ID header in every response
    - Returns X-API-Version header in every response
    """

    @app.before_request
    def _attach_request_id():
        incoming_id = flask_request.headers.get("X-Request-ID")
        g.request_id = incoming_id or str(uuid.uuid4())

    @app.after_request
    def _add_response_headers(response):
        response.headers["X-Request-ID"] = getattr(g, "request_id", "unknown")
        response.headers["X-API-Version"] = API_VERSION
        return response
