# QueueWise — Design Tradeoffs & Decisions

This document explains the key design decisions, their tradeoffs, and known limitations.

---

## 1. SQLite as the Default Database

**Decision:** Use SQLite for development and single-instance deployment.

**Why:** Zero setup, file-based, perfect for clinics and salons running a single queue terminal. No external database server needed.

**Tradeoff:** No concurrent write support beyond a single process. If you need multi-process or distributed deployment, swap to PostgreSQL via the `DATABASE_URL` env var. The repository layer is database-agnostic — only the connection string changes.

**Weakness:** Schema migrations require deleting the database file (`queuewise.db`) and restarting. For production, use Alembic or Flask-Migrate.

---

## 2. ~3 Minutes Per Person Wait Estimate

**Decision:** AI wait estimates use a hardcoded `~3 minutes per person` heuristic.

**Why:** Simple, deterministic, and reasonable for clinic/salon contexts. Avoids the complexity of ML-based estimation with insufficient training data.

**Tradeoff:** Inaccurate for queues with variable service times (e.g., a dental clinic vs. a barber). A future improvement could track actual service durations and compute rolling averages.

**Weakness:** The estimate is cosmetic — it never influences queue ordering or business rules. If it's wrong, the only impact is a slightly misleading message.

---

## 3. Terminal Statuses (SERVED, SKIPPED)

**Decision:** Once an entry is marked SERVED or SKIPPED, it cannot be changed back to WAITING.

**Why:** Prevents inconsistent state transitions. If a served user could be "unserved," the position ordering would become unpredictable, and audit trails would be unreliable.

**Tradeoff:** If an operator accidentally serves or skips someone, the only recovery is for the user to rejoin the queue (getting a new position at the end).

**Alternative considered:** Soft-delete with an "undo" window. Rejected because it adds complexity and creates ambiguous states during the undo window.

---

## 4. No Authentication

**Decision:** No user authentication or authorization.

**Why:** QueueWise is designed for walk-in service centers where a single operator manages the queue on a shared terminal. Adding auth would create friction for a use case that doesn't need it.

**Tradeoff:** Anyone with network access can join, serve, or skip. For public-facing deployments, add an API key or session-based auth at the route layer.

**Weakness:** In a multi-queue environment without auth, one operator could interfere with another's queue. Mitigated by queue IDs in all endpoints.

---

## 5. AI as Read-Only Layer

**Decision:** AI functions can only generate text — they cannot modify state, raise exceptions, or influence queue ordering.

**Why:** Separates correctness from presentation. Queue ordering depends on deterministic rules in pure Python. AI failures (e.g., bad text generation) cannot break the system.

**Tradeoff:** AI cannot optimize queue ordering (e.g., priority-based serving). All optimization must be added through the rules layer with human review.

**See:** [agents.md](agents.md) for full AI governance constraints.

---

## 6. Dry-Run Mode (Simulated Actions)

**Decision:** All mutating actions (join, serve, skip) support `?dry_run=true`, which runs rules but skips database writes.

**Why:** Enables safe previewing and testing without side effects. Operators can check if an action would succeed before committing.

**Tradeoff:** Dry-run results can become stale — between the preview and the actual action, another operator could change the queue state. There's no locking mechanism.

---

## 7. Event Persistence via log_event()

**Decision:** Events are persisted synchronously inside `log_event()`, but wrapped in a try/except that silently ignores failures.

**Why:** Event logging is observability infrastructure — it should never block or break the main action flow. A failed event write is less harmful than a failed serve.

**Tradeoff:** Events could theoretically be lost if the database is temporarily unavailable. For mission-critical audit trails, use an async event queue (e.g., Celery + Redis) instead.

---

## 8. Client-Side Validation as a UX Layer

**Decision:** Frontend validates names with the same regex as Rule 8, but the backend remains the source of truth.

**Why:** Client-side validation gives instant feedback. Backend validation prevents bypass. The two are intentionally duplicated.

**Tradeoff:** If the name regex changes on the backend, the frontend must be updated separately. No shared validation schema.

---

## 9. Polling Instead of WebSockets

**Decision:** Frontend polls `/status`, `/summary`, and `/events` every 3 seconds.

**Why:** Simple, stateless, works through any proxy/CDN. No WebSocket infrastructure needed.

**Tradeoff:** 3-second delay for real-time updates. Unnecessary HTTP traffic when no changes occur. For high-frequency updates, switch to Server-Sent Events (SSE) or WebSockets.

---

## 10. No Pagination on Queue Entries

**Decision:** `/queues/<id>/status` returns all entries in a single response.

**Why:** Queue sizes in clinic/salon contexts are typically < 50 entries. Pagination adds complexity without benefit for the target use case.

**Tradeoff:** For large-scale deployments (hundreds of entries), this will cause slow responses. Add `?page=1&per_page=20` params to the repository and route layers if needed.
