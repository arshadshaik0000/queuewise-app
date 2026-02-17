"""Repository layer — database access only.

No business logic lives here.  Every function either reads from
or writes to the database via SQLAlchemy.
"""

from typing import List, Optional

from app.database import db
from app.models.queue import Queue, QueueStatus
from app.models.queue_entry import EntryStatus, QueueEntry
from app.models.queue_event import QueueEvent


def list_all_queues() -> List[Queue]:
    """Return all queues ordered by creation time."""
    return Queue.query.order_by(Queue.created_at.desc()).all()


def create_queue(name: str) -> Queue:
    """Insert a new queue and return it."""
    queue = Queue(name=name)
    db.session.add(queue)
    db.session.commit()
    return queue


def get_queue(queue_id: int) -> Optional[Queue]:
    """Find a queue by primary key."""
    return db.session.get(Queue, queue_id)


def get_entries(queue_id: int) -> List[QueueEntry]:
    """Return all entries for a queue, ordered by position."""
    return (
        QueueEntry.query
        .filter_by(queue_id=queue_id)
        .order_by(QueueEntry.position)
        .all()
    )


def next_position(queue_id: int) -> int:
    """Calculate the next available position number."""
    last = (
        QueueEntry.query
        .filter_by(queue_id=queue_id)
        .order_by(QueueEntry.position.desc())
        .first()
    )
    return (last.position + 1) if last else 1


def add_entry(queue_id: int, user_name: str, position: int) -> QueueEntry:
    """Insert a new entry into the queue."""
    entry = QueueEntry(
        queue_id=queue_id,
        user_name=user_name,
        position=position,
    )
    db.session.add(entry)
    db.session.commit()
    return entry


def get_entry(entry_id: int) -> Optional[QueueEntry]:
    """Find an entry by primary key."""
    return db.session.get(QueueEntry, entry_id)


def mark_served(entry: QueueEntry) -> QueueEntry:
    """Update an entry's status to SERVED."""
    entry.status = EntryStatus.SERVED
    db.session.commit()
    return entry


def mark_skipped(entry: QueueEntry) -> QueueEntry:
    """Update an entry's status to SKIPPED."""
    entry.status = EntryStatus.SKIPPED
    db.session.commit()
    return entry


# --- Queue state management ---

def set_queue_status(queue: Queue, status: QueueStatus) -> Queue:
    """Update a queue's operational status (ACTIVE/PAUSED)."""
    queue.status = status
    db.session.commit()
    return queue


# --- Event log ---

def add_event(queue_id: int, action: str, result: str,
              detail: str = "", request_id: str = "") -> QueueEvent:
    """Insert a structured event log entry."""
    event = QueueEvent(
        queue_id=queue_id,
        action=action,
        result=result,
        detail=detail,
        request_id=request_id,
    )
    db.session.add(event)
    db.session.commit()
    return event


def get_events(queue_id: int, limit: int = 50) -> List[QueueEvent]:
    """Return recent events for a queue, newest first."""
    return (
        QueueEvent.query
        .filter_by(queue_id=queue_id)
        .order_by(QueueEvent.created_at.desc())
        .limit(limit)
        .all()
    )
