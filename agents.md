# QueueWise — AI Extension Constraints

## Purpose

This document defines strict governance rules for AI usage within
the QueueWise system. These rules ensure that AI remains a
**read-only explanation layer** and never influences correctness,
ordering, or business outcomes.

---

## Core Principles

### 1. AI Must Not Implement Queue Ordering Logic

- Queue ordering is determined **exclusively** by deterministic rules
  in `app/rules/queue_rules.py`.
- AI-generated responses (explanations, summaries, wait estimates)
  must **never** influence which user gets served, skipped, or joined.
- The `position` field is computed by `app/repositories/queue_repository.py`
  and is **immutable** to AI.

### 2. AI Cannot Modify Rules Engine Files

- All files under `app/rules/` are **off-limits** to AI-generated
  modifications.
- Business validation functions must be written and reviewed by humans.
- The `RuleViolation` exception is the **sole** mechanism for blocking
  invalid actions. AI must not create alternative blocking paths.

### 3. AI Explanations Must Be Read-Only

- All AI functions live in `app/ai/explainer.py`.
- These functions:
  - Receive **read-only snapshots** of queue state.
  - Return **string text** only.
  - **Never** write to the database.
  - **Never** raise exceptions that control flow.
  - **Never** return data structures used for routing decisions.

### 4. All New Features Must Extend Services or Rules Layers Only

New capabilities must follow the strict layered architecture:

```
routes → schemas → services → rules → repositories → models → database
                       ↓
                  ai/explainer (read-only)
```

| Layer          | What It Can Do                        | What It Cannot Do                 |
|---------------|---------------------------------------|-----------------------------------|
| **Routes**     | Parse HTTP, delegate to services      | Contain business logic            |
| **Schemas**    | Validate input, serialize output      | Access database or rules          |
| **Services**   | Orchestrate rules + repo + AI         | Directly query the database       |
| **Rules**      | Validate, raise RuleViolation         | Write to database, call AI        |
| **Repository** | Read/write database                   | Validate business rules           |
| **AI**         | Generate text explanations            | Modify state, influence ordering  |

---

## Business Rules Registry

All rules live in `app/rules/queue_rules.py`. Each returns nothing (passes
silently) or raises `RuleViolation` with a machine-readable `rule_code`.

| # | Function | rule_code | Purpose |
|---|----------|-----------|---------|
| 1 | `validate_no_duplicate_waiting()` | `DUPLICATE_JOIN` | Block duplicate waiting entries |
| 2 | `validate_serve_order()` | `EMPTY_QUEUE` | Only first WAITING can be served |
| 3 | `validate_not_already_served()` | `ALREADY_SERVED` | Cannot re-serve a served user |
| 4 | `validate_can_skip()` | `NOT_WAITING` | Only WAITING entries can be skipped |
| 5 | `can_skip_entry()` | `EMPTY_QUEUE` | Skip targets first WAITING only |
| 6 | `validate_queue_active_for_join()` | `QUEUE_PAUSED` | Paused queues block joins |
| 7 | `validate_preview_safety()` | `EMPTY_QUEUE` | Preview requires waiting entries |
| 8 | `validate_user_name()` | `INVALID_NAME` | Names must be 2+ letters, no numbers |

---

## Feature Inventory

| Feature | Read-Only? | Modifies DB? | AI Involved? |
|---------|-----------|-------------|-------------|
| Queue CRUD | No | Yes | No |
| Join / Serve / Skip | No | Yes | Explanation text only |
| Dry-Run Mode | Yes | No | Explanation text only |
| Preview Endpoint | Yes | No | Wait projection text |
| Pause / Resume | No | Yes (status) | No |
| Event Timeline | Yes | No (read) | No |
| Request Tracing | Yes | No | No |
| API Versioning | Yes | No | No |

---

## Enforcement Checklist

Before merging any AI-related change, verify:

- [ ] AI functions are in `app/ai/explainer.py` only.
- [ ] No AI code modifies `db.session`.
- [ ] No AI code raises `RuleViolation`.
- [ ] Queue ordering depends solely on `position` column and `EntryStatus`.
- [ ] New service methods follow the fetch → validate → persist → explain pattern.
- [ ] Dry-run mode works correctly (rules execute, DB writes skipped).
- [ ] All new validation logic is in `app/rules/`, not in routes or AI.
- [ ] Structured logs include `request_id` from tracing middleware.
- [ ] New rules include a `rule_code` for machine-readable error handling.
- [ ] Event timeline captures the action via `log_event()`.

---

## Change-Resilience

The architecture preserves change-resilience through:

1. **Separation of concerns** — Each layer has a single responsibility.
   Changing AI explanations cannot break queue ordering.
2. **Deterministic rules** — Business logic is pure Python with no
   external dependencies, side effects, or randomness.
3. **Dry-run capability** — Any action can be previewed without
   modifying state, enabling safe testing and validation.
4. **Request tracing** — Every request gets a unique ID for
   end-to-end observability without touching business logic.
5. **Terminal statuses** — SKIPPED and SERVED are terminal. Once set,
   they cannot be reversed, preventing inconsistent state transitions.
6. **Rule metadata** — Machine-readable `rule_code` on all violations
   decouples error handling from message strings.
7. **Non-critical observability** — Event persistence fails silently;
   logging never blocks business actions.
