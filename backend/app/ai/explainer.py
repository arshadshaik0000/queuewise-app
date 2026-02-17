"""AI explanation layer.

Generates human-readable messages about queue state.
This module NEVER modifies queue ordering or validates actions —
it only produces text for display.
"""

from typing import List

from app.models.queue_entry import EntryStatus, QueueEntry


def explain_wait_time(entries: List[QueueEntry], user_name: str) -> str:
    """Generate a friendly wait-time explanation for a specific user."""
    waiting = [e for e in entries if e.status == EntryStatus.WAITING]

    # Find the user's position among waiting entries
    user_position = None
    for i, entry in enumerate(waiting):
        if entry.user_name == user_name:
            user_position = i
            break

    if user_position is None:
        return f"{user_name} is not currently waiting in this queue."

    if user_position == 0:
        return f"{user_name}, you're next! Please be ready."

    people_ahead = user_position
    # Rough estimate: ~3 minutes per person (a reasonable clinic/salon default)
    estimated_minutes = people_ahead * 3

    return (
        f"{user_name}, there {'is' if people_ahead == 1 else 'are'} "
        f"{people_ahead} {'person' if people_ahead == 1 else 'people'} "
        f"ahead of you. Estimated wait: ~{estimated_minutes} minutes."
    )


def explain_queue_status(entries: List[QueueEntry]) -> str:
    """Generate an overall summary of the queue."""
    waiting = [e for e in entries if e.status == EntryStatus.WAITING]
    served = [e for e in entries if e.status == EntryStatus.SERVED]

    if not waiting and not served:
        return "This queue is empty. Be the first to join!"

    if not waiting:
        return (
            f"All {len(served)} {'person has' if len(served) == 1 else 'people have'} "
            f"been served. The queue is now clear."
        )

    next_up = waiting[0].user_name
    return (
        f"{len(waiting)} {'person' if len(waiting) == 1 else 'people'} waiting. "
        f"{len(served)} already served. "
        f"Next up: {next_up}."
    )


def explain_rule_failure(reason: str) -> str:
    """Convert a rule violation reason into a friendlier message."""
    return f"Sorry, that action isn't allowed: {reason}"
