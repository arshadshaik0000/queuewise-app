"""Service layer — orchestrates rules, repository, and AI.

Each method:
  1. Fetches data via the repository.
  2. Validates business rules.
  3. Persists changes via the repository (unless dry_run=True).
  4. Generates AI explanations for the response.

DRY-RUN MODE:
  When dry_run=True, rules execute normally but repository writes
  are skipped. The response includes {"dry_run": true, "result": ...}.
"""

from app.ai.explainer import explain_queue_status, explain_rule_failure, explain_wait_time
from app.logging_utils import log_event
from app.models.queue import QueueStatus
from app.models.queue_entry import EntryStatus
from app.repositories import queue_repository as repo
from app.rules import queue_rules as rules
from app.rules.exceptions import RuleViolation


def list_queues() -> list:
    """Return all queues with entry counts."""
    queues = repo.list_all_queues()
    result = []
    for q in queues:
        entries = repo.get_entries(q.id)
        waiting = sum(1 for e in entries if e.status == EntryStatus.WAITING)
        result.append({
            "id": q.id,
            "name": q.name,
            "status": q.status.value,
            "waiting_count": waiting,
            "total_count": len(entries),
            "created_at": q.created_at.isoformat() if q.created_at else None,
        })
    return result


def create_queue(name: str) -> dict:
    """Create a new queue."""
    queue = repo.create_queue(name)
    return {"id": queue.id, "name": queue.name}


def join_queue(queue_id: int, user_name: str, dry_run: bool = False) -> dict:
    """Add a user to the queue after validating rules."""
    queue = repo.get_queue(queue_id)
    if queue is None:
        raise RuleViolation("Queue not found.", rule_code="QUEUE_NOT_FOUND")

    # Rule 8: Validate user name is a real name
    try:
        rules.validate_user_name(user_name)
    except RuleViolation as e:
        log_event(queue_id, "JOIN_ATTEMPT", "BLOCKED", {"reason": e.reason, "rule_code": e.rule_code})
        if dry_run:
            return {"dry_run": True, "result": "would_fail", "reason": e.reason, "rule_code": e.rule_code}
        raise

    # Rule 6: Queue must be ACTIVE for joins
    try:
        rules.validate_queue_active_for_join(queue)
    except RuleViolation as e:
        log_event(queue_id, "JOIN_ATTEMPT", "BLOCKED", {"reason": e.reason, "rule_code": e.rule_code})
        if dry_run:
            return {"dry_run": True, "result": "would_fail", "reason": e.reason, "rule_code": e.rule_code}
        raise

    entries = repo.get_entries(queue_id)

    # Rule 1: No duplicate waiting entries
    try:
        rules.validate_no_duplicate_waiting(queue_id, user_name, entries)
    except RuleViolation as e:
        log_event(queue_id, "JOIN_ATTEMPT", "BLOCKED", {"reason": e.reason, "rule_code": e.rule_code})
        if dry_run:
            return {"dry_run": True, "result": "would_fail", "reason": e.reason, "rule_code": e.rule_code}
        raise

    if dry_run:
        position = repo.next_position(queue_id)
        explanation = explain_wait_time(entries, user_name)
        return {
            "dry_run": True,
            "result": "would_succeed",
            "user_name": user_name,
            "position": position,
            "explanation": explanation,
        }

    position = repo.next_position(queue_id)
    entry = repo.add_entry(queue_id, user_name, position)

    log_event(queue_id, "JOIN", "SUCCESS", {"user_name": user_name, "position": position})

    return {
        "entry_id": entry.id,
        "user_name": entry.user_name,
        "position": entry.position,
        "status": entry.status.value,
    }


def serve_next(queue_id: int, dry_run: bool = False) -> dict:
    """Serve the next person in the queue."""
    queue = repo.get_queue(queue_id)
    if queue is None:
        raise RuleViolation("Queue not found.", rule_code="QUEUE_NOT_FOUND")

    entries = repo.get_entries(queue_id)

    try:
        entry = rules.validate_serve_order(entries)
    except RuleViolation as e:
        log_event(queue_id, "SERVE", "BLOCKED", {"reason": e.reason, "rule_code": e.rule_code})
        if dry_run:
            return {"dry_run": True, "result": "would_fail", "reason": e.reason, "rule_code": e.rule_code}
        raise

    try:
        rules.validate_not_already_served(entry)
    except RuleViolation as e:
        log_event(queue_id, "SERVE", "BLOCKED", {"reason": e.reason, "rule_code": e.rule_code})
        if dry_run:
            return {"dry_run": True, "result": "would_fail", "reason": e.reason, "rule_code": e.rule_code}
        raise

    if dry_run:
        return {"dry_run": True, "result": "would_succeed", "user_name": entry.user_name}

    repo.mark_served(entry)
    log_event(queue_id, "SERVE", "SUCCESS", {"user_name": entry.user_name})

    return {
        "entry_id": entry.id,
        "user_name": entry.user_name,
        "status": entry.status.value,
    }


def skip_user(queue_id: int, entry_id: int) -> dict:
    """Skip a specific user in the queue (by entry ID)."""
    queue = repo.get_queue(queue_id)
    if queue is None:
        raise RuleViolation("Queue not found.", rule_code="QUEUE_NOT_FOUND")

    entry = repo.get_entry(entry_id)
    if entry is None or entry.queue_id != queue_id:
        raise RuleViolation("Entry not found in this queue.", rule_code="ENTRY_NOT_FOUND")

    try:
        rules.validate_can_skip(entry)
    except RuleViolation as e:
        log_event(queue_id, "SKIP", "BLOCKED", {"reason": e.reason, "rule_code": e.rule_code})
        raise

    repo.mark_skipped(entry)
    log_event(queue_id, "SKIP", "SUCCESS", {"user_name": entry.user_name})

    return {
        "entry_id": entry.id,
        "user_name": entry.user_name,
        "status": entry.status.value,
    }


def skip_next(queue_id: int, dry_run: bool = False) -> dict:
    """Skip the FIRST waiting user in the queue."""
    queue = repo.get_queue(queue_id)
    if queue is None:
        raise RuleViolation("Queue not found.", rule_code="QUEUE_NOT_FOUND")

    entries = repo.get_entries(queue_id)

    try:
        entry = rules.can_skip_entry(entries)
    except RuleViolation as e:
        log_event(queue_id, "SKIP", "BLOCKED", {"reason": e.reason, "rule_code": e.rule_code})
        if dry_run:
            return {"dry_run": True, "result": "would_fail", "reason": e.reason, "rule_code": e.rule_code}
        raise

    if dry_run:
        return {"dry_run": True, "result": "would_succeed", "user_name": entry.user_name}

    repo.mark_skipped(entry)
    log_event(queue_id, "SKIP", "SUCCESS", {"user_name": entry.user_name})

    return {
        "entry_id": entry.id,
        "user_name": entry.user_name,
        "status": entry.status.value,
    }


def get_status(queue_id: int) -> dict:
    """Return the current queue state with AI-generated explanations."""
    queue = repo.get_queue(queue_id)
    if queue is None:
        raise RuleViolation("Queue not found.", rule_code="QUEUE_NOT_FOUND")

    entries = repo.get_entries(queue_id)
    explanation = explain_queue_status(entries)

    wait_explanations = {}
    for entry in entries:
        if entry.status == EntryStatus.WAITING:
            wait_explanations[entry.user_name] = explain_wait_time(entries, entry.user_name)

    return {
        "queue_id": queue.id,
        "queue_name": queue.name,
        "queue_status": queue.status.value,
        "entries": entries,
        "explanation": explanation,
        "wait_explanations": wait_explanations,
    }


def get_summary(queue_id: int) -> dict:
    """Return a derived-data summary for a queue."""
    queue = repo.get_queue(queue_id)
    if queue is None:
        raise RuleViolation("Queue not found.", rule_code="QUEUE_NOT_FOUND")

    entries = repo.get_entries(queue_id)
    waiting = [e for e in entries if e.status == EntryStatus.WAITING]
    served = [e for e in entries if e.status == EntryStatus.SERVED]
    skipped = [e for e in entries if e.status == EntryStatus.SKIPPED]

    explanation = explain_queue_status(entries)
    estimated_wait = ""
    if waiting:
        estimated_wait = explain_wait_time(entries, waiting[-1].user_name)

    return {
        "queue_id": queue.id,
        "queue_name": queue.name,
        "waiting_count": len(waiting),
        "served_count": len(served),
        "skipped_count": len(skipped),
        "estimated_wait": estimated_wait,
        "explanation": explanation,
    }


def preview_next_action(queue_id: int) -> dict:
    """Preview what would happen if the next person is served or skipped.

    This is a read-only simulation — no database writes.
    Rules validate preview safety. AI generates projected text.
    """
    queue = repo.get_queue(queue_id)
    if queue is None:
        raise RuleViolation("Queue not found.", rule_code="QUEUE_NOT_FOUND")

    entries = repo.get_entries(queue_id)

    # Rule 7: Preview only meaningful with waiting entries
    waiting = rules.validate_preview_safety(entries)

    # Who gets served/skipped next
    next_serve = waiting[0].user_name
    next_skip_target = waiting[0].user_name
    # After skipping the first, who becomes next?
    next_after_skip = waiting[1].user_name if len(waiting) > 1 else None

    # AI-generated projected wait change
    if len(waiting) > 1:
        current_wait = (len(waiting) - 1) * 3  # ~3 min each
        new_wait = (len(waiting) - 2) * 3
        projected = f"~{current_wait - new_wait} minutes faster for remaining"
    else:
        projected = "Queue would be empty after this action"

    return {
        "next_if_served": next_serve,
        "next_if_skipped": next_after_skip or "Queue would be empty",
        "skip_target": next_skip_target,
        "projected_wait_change": projected,
        "waiting_count": len(waiting),
    }


def pause_queue(queue_id: int) -> dict:
    """Pause a queue — blocks new joins, serve/skip still allowed."""
    queue = repo.get_queue(queue_id)
    if queue is None:
        raise RuleViolation("Queue not found.", rule_code="QUEUE_NOT_FOUND")

    if queue.status == QueueStatus.PAUSED:
        raise RuleViolation("Queue is already paused.", rule_code="ALREADY_PAUSED")

    repo.set_queue_status(queue, QueueStatus.PAUSED)
    log_event(queue_id, "PAUSED", "SUCCESS", {})

    return {"queue_id": queue.id, "status": queue.status.value}


def resume_queue(queue_id: int) -> dict:
    """Resume a paused queue — accepts new joins again."""
    queue = repo.get_queue(queue_id)
    if queue is None:
        raise RuleViolation("Queue not found.", rule_code="QUEUE_NOT_FOUND")

    if queue.status == QueueStatus.ACTIVE:
        raise RuleViolation("Queue is already active.", rule_code="ALREADY_ACTIVE")

    repo.set_queue_status(queue, QueueStatus.ACTIVE)
    log_event(queue_id, "RESUMED", "SUCCESS", {})

    return {"queue_id": queue.id, "status": queue.status.value}


def get_events(queue_id: int, limit: int = 50) -> list:
    """Return recent events for a queue."""
    queue = repo.get_queue(queue_id)
    if queue is None:
        raise RuleViolation("Queue not found.", rule_code="QUEUE_NOT_FOUND")

    events = repo.get_events(queue_id, limit)
    return [e.to_dict() for e in events]
