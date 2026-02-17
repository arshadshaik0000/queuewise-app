"""Deterministic queue business rules.

These functions enforce fairness constraints.  They NEVER modify the
database — they only validate and raise RuleViolation on failure.

Each rule includes a rule_code for machine-readable error identification.
"""

import re
from typing import List

from app.models.queue import Queue, QueueStatus
from app.models.queue_entry import EntryStatus, QueueEntry
from app.rules.exceptions import RuleViolation


def validate_user_name(user_name: str):
    """Rule 8: User name must be a real name -- letters only, min 2 chars.

    Rejects:
      - Pure numbers ("42", "1")
      - Single characters ("a")
      - Names with digits or special characters ("John3", "A@B")
    """
    name = user_name.strip()
    if len(name) < 2:
        raise RuleViolation(
            "Name must be at least 2 characters long.",
            rule_code="INVALID_NAME",
        )
    if not re.match(r"^[A-Za-z][A-Za-z \-']*[A-Za-z]$", name):
        raise RuleViolation(
            f"'{user_name}' is not a valid name. "
            "Use letters only (spaces, hyphens, and apostrophes allowed).",
            rule_code="INVALID_NAME",
        )


def validate_no_duplicate_waiting(queue_id: int, user_name: str, entries: List[QueueEntry]):
    """Rule 1: A user cannot join the same queue twice while WAITING."""
    for entry in entries:
        if entry.user_name == user_name and entry.status == EntryStatus.WAITING:
            raise RuleViolation(
                f"User '{user_name}' is already waiting in this queue.",
                rule_code="DUPLICATE_JOIN",
            )


def validate_serve_order(entries: List[QueueEntry]):
    """Rule 2: Only the first WAITING person in the queue can be served.

    Returns the entry to be served so the caller doesn't need to
    re-scan the list.
    """
    first_waiting = None
    for entry in entries:
        if entry.status == EntryStatus.WAITING:
            first_waiting = entry
            break

    if first_waiting is None:
        raise RuleViolation(
            "No one is waiting in this queue.",
            rule_code="EMPTY_QUEUE",
        )

    return first_waiting


def validate_not_already_served(entry: QueueEntry):
    """Rule 3: A served user cannot be served again."""
    if entry.status == EntryStatus.SERVED:
        raise RuleViolation(
            f"User '{entry.user_name}' has already been served.",
            rule_code="ALREADY_SERVED",
        )


def validate_can_skip(entry: QueueEntry):
    """Rule 4: Only a WAITING user can be skipped."""
    if entry.status != EntryStatus.WAITING:
        raise RuleViolation(
            f"User '{entry.user_name}' cannot be skipped "
            f"(current status: {entry.status.value}).",
            rule_code="NOT_WAITING",
        )


def can_skip_entry(entries: List[QueueEntry]):
    """Rule 5: Only the FIRST waiting user in the queue can be skipped.

    Mirrors serve_order logic but for skipping -- ensures
    position ordering integrity by preventing arbitrary skips.
    Skipped users cannot be served later (terminal status).

    Returns the entry to be skipped.
    """
    first_waiting = None
    for entry in entries:
        if entry.status == EntryStatus.WAITING:
            first_waiting = entry
            break

    if first_waiting is None:
        raise RuleViolation(
            "No one is waiting in this queue to skip.",
            rule_code="EMPTY_QUEUE",
        )

    return first_waiting


def validate_queue_active_for_join(queue: Queue):
    """Rule 6: Joining is blocked when a queue is PAUSED.

    Serve and Skip remain allowed even when paused --
    only new joins are restricted.
    """
    if queue.status == QueueStatus.PAUSED:
        raise RuleViolation(
            "This queue is currently paused. New joins are not accepted.",
            rule_code="QUEUE_PAUSED",
        )


def validate_preview_safety(entries: List[QueueEntry]):
    """Rule 7: Preview is only meaningful if someone is waiting.

    This prevents generating meaningless preview data for empty queues.
    Returns the list of waiting entries for the caller to use.
    """
    waiting = [e for e in entries if e.status == EntryStatus.WAITING]
    if not waiting:
        raise RuleViolation(
            "No one is waiting -- nothing to preview.",
            rule_code="EMPTY_QUEUE",
        )
    return waiting
