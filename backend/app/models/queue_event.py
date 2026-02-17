"""QueueEvent model — lightweight event log for observability.

Stores structured events for each queue action (JOIN, SERVE, SKIP, etc.).
Read from the /events endpoint — never modifies business logic.
"""

from datetime import datetime, timezone

from app.database import db


class QueueEvent(db.Model):
    __tablename__ = "queue_events"

    id = db.Column(db.Integer, primary_key=True)
    queue_id = db.Column(
        db.Integer, db.ForeignKey("queues.id"), nullable=False, index=True
    )
    action = db.Column(db.String(50), nullable=False)
    result = db.Column(db.String(50), nullable=False)
    detail = db.Column(db.String(500), nullable=True)
    request_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<QueueEvent {self.action} {self.result} q={self.queue_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "queue_id": self.queue_id,
            "action": self.action,
            "result": self.result,
            "detail": self.detail,
            "request_id": self.request_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
