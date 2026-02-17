"""Thin route handlers for queue operations.

Routes are responsible ONLY for:
  - Parsing/validating request data via schemas.
  - Extracting dry_run query param.
  - Delegating to the service layer.
  - Returning HTTP responses with rule_code when blocked.

No business logic lives here.
"""

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from app.ai.explainer import explain_rule_failure
from app.rules.exceptions import RuleViolation
from app.schemas.queue_schema import (
    CreateQueueSchema,
    JoinQueueSchema,
    QueueStatusSchema,
    QueueSummarySchema,
    PreviewSchema,
)
from app.services import queue_service as service

queue_bp = Blueprint("queues", __name__)

# Reusable schema instances
_create_schema = CreateQueueSchema()
_join_schema = JoinQueueSchema()
_status_schema = QueueStatusSchema()
_summary_schema = QueueSummarySchema()
_preview_schema = PreviewSchema()


def _is_dry_run() -> bool:
    """Extract ?dry_run=true from query params."""
    return request.args.get("dry_run", "").lower() == "true"


def _rule_error(e: RuleViolation, status_code: int = 409):
    """Build error response with rule_code for machine-readable feedback."""
    return jsonify({
        "error": explain_rule_failure(e.reason),
        "rule_code": e.rule_code,
    }), status_code


@queue_bp.route("/queues", methods=["GET"])
def list_queues():
    """GET /queues — List all queues with entry counts."""
    result = service.list_queues()
    return jsonify(result), 200


@queue_bp.route("/queues", methods=["POST"])
def create_queue():
    """POST /queues — Create a new queue."""
    try:
        data = _create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    result = service.create_queue(data["name"])
    return jsonify(result), 201


@queue_bp.route("/queues/<int:queue_id>/join", methods=["POST"])
def join_queue(queue_id: int):
    """POST /queues/<id>/join — Supports ?dry_run=true."""
    try:
        data = _join_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    dry_run = _is_dry_run()
    try:
        result = service.join_queue(queue_id, data["user_name"], dry_run=dry_run)
    except RuleViolation as e:
        return _rule_error(e)

    return jsonify(result), 200 if dry_run else 201


@queue_bp.route("/queues/<int:queue_id>/serve", methods=["PATCH"])
def serve_next(queue_id: int):
    """PATCH /queues/<id>/serve — Supports ?dry_run=true."""
    dry_run = _is_dry_run()
    try:
        result = service.serve_next(queue_id, dry_run=dry_run)
    except RuleViolation as e:
        return _rule_error(e)

    return jsonify(result), 200


@queue_bp.route("/queues/<int:queue_id>/skip/<int:entry_id>", methods=["PATCH"])
def skip_user(queue_id: int, entry_id: int):
    """PATCH /queues/<id>/skip/<entry_id> — Skip a specific user by ID."""
    try:
        result = service.skip_user(queue_id, entry_id)
    except RuleViolation as e:
        return _rule_error(e)

    return jsonify(result), 200


@queue_bp.route("/queues/<int:queue_id>/skip", methods=["PATCH"])
def skip_next(queue_id: int):
    """PATCH /queues/<id>/skip — Skip the first waiting person. Supports ?dry_run=true."""
    dry_run = _is_dry_run()
    try:
        result = service.skip_next(queue_id, dry_run=dry_run)
    except RuleViolation as e:
        return _rule_error(e)

    return jsonify(result), 200


@queue_bp.route("/queues/<int:queue_id>/status", methods=["GET"])
def get_status(queue_id: int):
    """GET /queues/<id>/status — Full queue status with AI explanation."""
    try:
        result = service.get_status(queue_id)
    except RuleViolation as e:
        return _rule_error(e, 404)

    return jsonify(_status_schema.dump(result)), 200


@queue_bp.route("/queues/<int:queue_id>/summary", methods=["GET"])
def get_summary(queue_id: int):
    """GET /queues/<id>/summary — Derived-data summary."""
    try:
        result = service.get_summary(queue_id)
    except RuleViolation as e:
        return _rule_error(e, 404)

    return jsonify(_summary_schema.dump(result)), 200


@queue_bp.route("/queues/<int:queue_id>/preview", methods=["GET"])
def preview(queue_id: int):
    """GET /queues/<id>/preview — Read-only simulation of next action."""
    try:
        result = service.preview_next_action(queue_id)
    except RuleViolation as e:
        return _rule_error(e, 404)

    return jsonify(_preview_schema.dump(result)), 200


@queue_bp.route("/queues/<int:queue_id>/pause", methods=["PATCH"])
def pause_queue(queue_id: int):
    """PATCH /queues/<id>/pause — Pause a queue (blocks new joins)."""
    try:
        result = service.pause_queue(queue_id)
    except RuleViolation as e:
        return _rule_error(e)

    return jsonify(result), 200


@queue_bp.route("/queues/<int:queue_id>/resume", methods=["PATCH"])
def resume_queue(queue_id: int):
    """PATCH /queues/<id>/resume — Resume a paused queue."""
    try:
        result = service.resume_queue(queue_id)
    except RuleViolation as e:
        return _rule_error(e)

    return jsonify(result), 200


@queue_bp.route("/queues/<int:queue_id>/events", methods=["GET"])
def get_events(queue_id: int):
    """GET /queues/<id>/events — Event timeline for observability."""
    try:
        limit = request.args.get("limit", 50, type=int)
        result = service.get_events(queue_id, limit=min(limit, 100))
    except RuleViolation as e:
        return _rule_error(e, 404)

    return jsonify(result), 200
