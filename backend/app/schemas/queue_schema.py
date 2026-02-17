"""Marshmallow schemas for request/response validation."""

from marshmallow import Schema, fields, validate


class CreateQueueSchema(Schema):
    """Validates POST /queues input."""
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=120),
    )


class JoinQueueSchema(Schema):
    """Validates POST /queues/<id>/join input."""
    user_name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=120),
    )


class QueueEntrySchema(Schema):
    """Serializes a single queue entry for responses."""
    id = fields.Integer(dump_only=True)
    user_name = fields.String()
    position = fields.Integer()
    status = fields.Method("get_status")
    joined_at = fields.DateTime()

    def get_status(self, obj):
        return obj.status.value


class QueueStatusSchema(Schema):
    """Serializes the full queue status response."""
    queue_id = fields.Integer()
    queue_name = fields.String()
    queue_status = fields.String()
    entries = fields.List(fields.Nested(QueueEntrySchema))
    explanation = fields.String()
    wait_explanations = fields.Dict(keys=fields.String(), values=fields.String())


class QueueSummarySchema(Schema):
    """Serializes the derived-data summary response."""
    queue_id = fields.Integer()
    queue_name = fields.String()
    waiting_count = fields.Integer()
    served_count = fields.Integer()
    skipped_count = fields.Integer()
    estimated_wait = fields.String()
    explanation = fields.String()


class PreviewSchema(Schema):
    """Serializes the preview response — read-only simulation."""
    next_if_served = fields.String()
    next_if_skipped = fields.String()
    skip_target = fields.String()
    projected_wait_change = fields.String()
    waiting_count = fields.Integer()
