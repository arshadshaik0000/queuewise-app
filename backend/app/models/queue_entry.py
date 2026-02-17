"""QueueEntry model — represents a person's place in a queue."""

import enum
from datetime import datetime, timezone

from app.database import db


class EntryStatus(enum.Enum):
    """Possible states for a queue entry."""

    WAITING = "WAITING"
    SERVED = "SERVED"
    SKIPPED = "SKIPPED"


class QueueEntry(db.Model):
    __tablename__ = "queue_entries"

    id = db.Column(db.Integer, primary_key=True)
    queue_id = db.Column(
        db.Integer, db.ForeignKey("queues.id"), nullable=False
    )
    user_name = db.Column(db.String(120), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    status = db.Column(
        db.Enum(EntryStatus), nullable=False, default=EntryStatus.WAITING
    )
    joined_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Belongs to a queue
    queue = db.relationship("Queue", back_populates="entries")

    def __repr__(self):
        return (
            f"<QueueEntry {self.id}: {self.user_name} "
            f"pos={self.position} status={self.status.value}>"
        )
