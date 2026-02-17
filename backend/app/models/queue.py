"""Queue model — represents a named queue that users can join.

Supports ACTIVE/PAUSED status for controlling join availability.
"""

import enum
from datetime import datetime, timezone

from app.database import db


class QueueStatus(enum.Enum):
    """Queue-level state: ACTIVE queues accept joins, PAUSED do not."""
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"


class Queue(db.Model):
    __tablename__ = "queues"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    status = db.Column(
        db.Enum(QueueStatus), nullable=False, default=QueueStatus.ACTIVE
    )
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # One queue has many entries
    entries = db.relationship(
        "QueueEntry", back_populates="queue", order_by="QueueEntry.position"
    )

    def __repr__(self):
        return f"<Queue {self.id}: {self.name} [{self.status.value}]>"
