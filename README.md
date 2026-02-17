<p align="center">
  <img src=".github/assets/banner.svg" alt="QueueWise Banner" width="800"/>
</p>

<p align="center">
  <a href="#-getting-started"><img src="https://img.shields.io/badge/GETTING_STARTED-667eea?style=for-the-badge&logo=rocket&logoColor=white" alt="Getting Started"/></a>
  <a href="#-how-it-works"><img src="https://img.shields.io/badge/ARCHITECTURE-764ba2?style=for-the-badge&logo=buffer&logoColor=white" alt="Architecture"/></a>
  <a href="#-api-reference"><img src="https://img.shields.io/badge/API_REFERENCE-f093fb?style=for-the-badge&logo=fastapi&logoColor=white" alt="API Reference"/></a>
  <a href="#-running-tests"><img src="https://img.shields.io/badge/TESTS-4ade80?style=for-the-badge&logo=pytest&logoColor=white" alt="Tests"/></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-3776ab?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/flask-3.0-000000?logo=flask&logoColor=white" alt="Flask"/>
  <img src="https://img.shields.io/badge/react-18-61dafb?logo=react&logoColor=black" alt="React"/>
  <img src="https://img.shields.io/badge/typescript-5.0-3178c6?logo=typescript&logoColor=white" alt="TypeScript"/>
  <img src="https://img.shields.io/badge/tests-67_passed-4ade80?logo=checkmarx&logoColor=white" alt="Tests"/>
  <img src="https://img.shields.io/badge/API-v1-667eea" alt="API Version"/>
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&pause=1000&color=667EEA&center=true&vCenter=true&width=700&lines=Smart+queue+management+for+clinics%2C+salons+%26+service+centers;AI-powered+wait+time+explanations;Dry-run+mode+%E2%80%93+preview+before+committing;8+deterministic+rules+keep+the+queue+fair;67+tests+%E2%80%93+every+feature+verified" alt="Typing SVG" />
</p>

---

## ✨ What Can It Do?

<table>
<tr>
<td width="50%">

### 🏥 For Patients / Customers
- Join a queue with your name
- See your position and estimated wait time
- Get AI-generated messages like:
  > *"Arshad, there are 2 people ahead of you. Estimated wait: ~6 minutes."*

</td>
<td width="50%">

### 👨‍⚕️ For Operators
- Serve or skip the next person
- Pause the queue (lunch break? 🍔)
- Preview actions before committing
- See full event history for accountability

</td>
</tr>
</table>

<details>
<summary><strong>📋 Full Feature List (click to expand)</strong></summary>
<br>

| Feature | Description | Endpoint |
|:--------|:------------|:---------|
| 🎫 **Queue CRUD** | Create and list queues | `POST /queues`, `GET /queues` |
| ➕ **Join** | Add yourself to a queue | `POST /queues/:id/join` |
| ⚡ **Serve** | Serve the next person in line | `PATCH /queues/:id/serve` |
| ⏭️ **Skip** | Skip the first waiting person | `PATCH /queues/:id/skip` |
| 🔍 **Preview** | See what would happen next (read-only) | `GET /queues/:id/preview` |
| ⏸️ **Pause / ▶️ Resume** | Temporarily block new joins | `PATCH /queues/:id/pause` |
| 🧪 **Dry-Run** | Test any action without side effects | `?dry_run=true` on any action |
| 🤖 **AI Explanations** | Friendly wait-time messages | Built into responses |
| 📜 **Event Timeline** | Full history of every action | `GET /queues/:id/events` |
| 🔗 **Request Tracing** | Unique ID per request for debugging | `X-Request-ID` header |
| 📌 **API Versioning** | Track which API version you're using | `X-API-Version: v1` |
| 🛡️ **Name Validation** | Rejects numbers and special characters | Rule 8 |

</details>

---

## 🚀 Getting Started

> **Prerequisites:** Python 3.9+ · Node.js 18+ · npm

<details open>
<summary><strong>📦 Step 1 — Clone</strong></summary>

```bash
git clone <your-repo-url>
cd queuewise-app
```

</details>

<details open>
<summary><strong>🔧 Step 2 — Start the Backend</strong></summary>

```bash
cd backend
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

> 💡 First run auto-creates the database. No configuration needed!

**Backend runs at** → `http://127.0.0.1:5000`

</details>

<details open>
<summary><strong>🎨 Step 3 — Start the Frontend</strong></summary>

Open a **new terminal tab**:

```bash
cd frontend
npm install
npm run dev
```

**Frontend runs at** → `http://localhost:5173`

</details>

<details open>
<summary><strong>🎉 Step 4 — Use it!</strong></summary>

1. Open `http://localhost:5173` in your browser
2. Click **Create Queue** → give it a name like "Clinic Reception"
3. **Join** the queue with your name
4. Try **Serve**, **Skip**, **Preview**, and **Pause**!

</details>

---

## 🏗️ How It Works

<p align="center">
  <img src=".github/assets/architecture.svg" alt="Architecture Diagram" width="800"/>
</p>

<details>
<summary><strong>🔰 Explain this to me like I'm a beginner (click to expand)</strong></summary>
<br>

Think of QueueWise like a restaurant kitchen:

| Layer | Restaurant Analogy | What It Does |
|:------|:-------------------|:-------------|
| **Routes** | 🚪 Front door | Takes the customer's order (HTTP request) |
| **Schemas** | 📝 Order form | Checks the order makes sense (validates input) |
| **Services** | 👨‍🍳 Head chef | Coordinates everything: checks rules, prepares food |
| **Rules** | 📖 Health code | Says what's allowed and what's not (no raw chicken!) |
| **Repository** | 🗄️ Pantry | Gets and stores ingredients (database access) |
| **AI Explainer** | 🎙️ Waiter | Explains what's happening in friendly language |
| **Models** | 📦 Ingredient labels | Defines what things look like (Queue, Entry, Event) |

**The key insight:** The waiter (AI) can describe the food, but **cannot** change the recipe or enter the kitchen. This means AI bugs can never break your queue!

</details>

<details>
<summary><strong>⚙️ What each layer can and cannot do</strong></summary>
<br>

| Layer | ✅ Can Do | ❌ Cannot Do |
|:------|:---------|:------------|
| **Routes** | Parse HTTP, return responses | Contain business logic |
| **Schemas** | Validate input shapes | Access database or rules |
| **Services** | Coordinate rules + DB + AI | Query database directly |
| **Rules** | Validate, raise errors | Write to DB, call AI |
| **Repository** | Read/write database | Make business decisions |
| **AI** | Generate friendly text | Modify any data, ever |

</details>

---

## 🛡️ Business Rules

<p align="center">
  <img src=".github/assets/rules.svg" alt="Business Rules" width="800"/>
</p>

<details>
<summary><strong>📖 Detailed Rule Breakdown</strong></summary>
<br>

| # | Rule | What It Prevents | Code |
|:-:|:-----|:-----------------|:-----|
| 1 | **No duplicate joins** | Same person joining twice | `DUPLICATE_JOIN` |
| 2 | **Serve in order** | Cutting the line | `EMPTY_QUEUE` |
| 3 | **No re-serving** | Serving someone twice | `ALREADY_SERVED` |
| 4 | **Skip only waiting** | Skipping served/skipped people | `NOT_WAITING` |
| 5 | **Skip first only** | Skipping someone in the middle | `EMPTY_QUEUE` |
| 6 | **Paused = no joins** | Joining during a break | `QUEUE_PAUSED` |
| 7 | **Preview needs people** | Previewing an empty queue | `EMPTY_QUEUE` |
| 8 | **Valid names only** | Numbers or symbols as names | `INVALID_NAME` |

> ⚠️ **Terminal statuses:** `SERVED` and `SKIPPED` are **permanent**. If you accidentally serve someone, they must rejoin (new position at end). This prevents confusing state changes.

</details>

---

## 🔌 API Reference

<details open>
<summary><strong>Queue Management</strong></summary>

| Method | Endpoint | Description |
|:------:|:---------|:------------|
| `GET` | `/queues` | List all queues with entry counts |
| `POST` | `/queues` | Create a new queue → `{ "name": "Clinic Reception" }` |

</details>

<details>
<summary><strong>Queue Actions (click to expand)</strong></summary>
<br>

| Method | Endpoint | Description | Dry Run? |
|:------:|:---------|:------------|:--------:|
| `POST` | `/queues/:id/join` | Join the queue | ✅ |
| `PATCH` | `/queues/:id/serve` | Serve next person | ✅ |
| `PATCH` | `/queues/:id/skip` | Skip first waiting | ✅ |
| `PATCH` | `/queues/:id/skip/:entryId` | Skip specific person | ❌ |

**Dry-run mode:** Add `?dry_run=true` to any action. Rules execute, but nothing changes. Like a "what if?" button.

</details>

<details>
<summary><strong>Queue State & Observability (click to expand)</strong></summary>
<br>

| Method | Endpoint | Description |
|:------:|:---------|:------------|
| `GET` | `/queues/:id/status` | Full status + AI explanations |
| `GET` | `/queues/:id/summary` | Counts + wait estimates |
| `GET` | `/queues/:id/preview` | Read-only next-action simulation |
| `PATCH` | `/queues/:id/pause` | Pause queue (blocks joins) |
| `PATCH` | `/queues/:id/resume` | Resume paused queue |
| `GET` | `/queues/:id/events?limit=N` | Event timeline (max 100) |

</details>

<details>
<summary><strong>Response Headers & Error Format (click to expand)</strong></summary>
<br>

**Every response includes:**

| Header | Example | Purpose |
|:-------|:--------|:--------|
| `X-Request-ID` | `a1b2c3d4-e5f6-...` | Unique trace ID for debugging |
| `X-API-Version` | `v1` | Current API version |

**Error format (when a rule blocks an action):**

```json
{
  "error": "Sorry, that action isn't allowed: User 'Arshad' is already waiting in this queue.",
  "rule_code": "DUPLICATE_JOIN"
}
```

</details>

<details>
<summary><strong>📝 Try It — cURL Examples (click to expand)</strong></summary>
<br>

```bash
# 1. Create a queue
curl -X POST http://127.0.0.1:5000/queues \
  -H "Content-Type: application/json" \
  -d '{"name": "Clinic Reception"}'
# → {"id": 1, "name": "Clinic Reception"}

# 2. Join it
curl -X POST http://127.0.0.1:5000/queues/1/join \
  -H "Content-Type: application/json" \
  -d '{"user_name": "Arshad"}'
# → {"entry_id": 1, "user_name": "Arshad", "position": 1, "status": "WAITING"}

# 3. Preview what happens next (won't change anything)
curl http://127.0.0.1:5000/queues/1/preview
# → {"next_if_served": "Arshad", "skip_target": "Arshad", ...}

# 4. Dry-run a serve (rules execute, nothing changes)
curl -X PATCH "http://127.0.0.1:5000/queues/1/serve?dry_run=true"
# → {"dry_run": true, "result": "would_succeed", "user_name": "Arshad"}

# 5. Actually serve
curl -X PATCH http://127.0.0.1:5000/queues/1/serve
# → {"entry_id": 1, "user_name": "Arshad", "status": "SERVED"}
```

</details>

---

## 🧪 Running Tests

```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
```

<details>
<summary><strong>📊 Test Coverage Breakdown (67 tests)</strong></summary>
<br>

| Test File | Tests | What It Covers |
|:----------|:-----:|:---------------|
| `test_queue_rules.py` | 11 | Core operations (join, serve, skip, status) |
| `test_name_validation.py` | 10 | Rule 8 — valid/invalid name patterns |
| `test_pause_resume.py` | 7 | Pause/resume + blocked joins |
| `test_skip_first_only.py` | 6 | Skip ordering integrity |
| `test_dry_run.py` | 5 | Dry-run mode for all actions |
| `test_preview.py` | 5 | Preview endpoint (read-only) |
| `test_summary.py` | 5 | Summary counts + explanations |
| `test_events.py` | 5 | Event timeline persistence |
| `test_rule_metadata.py` | 5 | `rule_code` in error responses |
| `test_request_tracing.py` | 5 | `X-Request-ID` header |
| `test_api_version.py` | 3 | `X-API-Version` header |

</details>

---

## 🤖 AI in QueueWise

<table>
<tr>
<td width="50%">

### ✅ What AI Does
- Generates wait-time messages
- Summarizes queue status
- Wraps errors in friendly language
- Projects wait changes in preview

</td>
<td width="50%">

### 🚫 What AI Cannot Do
- ~~Modify the database~~
- ~~Change queue ordering~~
- ~~Raise blocking exceptions~~
- ~~Influence who gets served~~

</td>
</tr>
</table>

> 🔒 **AI is sandboxed.** It receives read-only data and returns strings. A bug in AI explanations can never break queue ordering. See [agents.md](agents.md) for the full governance document.

---

## 💡 Key Concepts for Beginners

<details>
<summary><strong>🧪 What is "dry-run mode"?</strong></summary>
<br>

Add `?dry_run=true` to any action endpoint. The server checks all the rules (so you know if it would work) but **doesn't actually do anything**. It's like asking "what would happen if I pressed this button?"

```
Real action:     POST /queues/1/serve          → Actually serves the person
Dry-run:         POST /queues/1/serve?dry_run=true  → "Would succeed" but nothing changes
```

</details>

<details>
<summary><strong>🔄 What are "terminal statuses"?</strong></summary>
<br>

```mermaid
stateDiagram-v2
    [*] --> WAITING: Join queue
    WAITING --> SERVED: Serve ✅
    WAITING --> SKIPPED: Skip ⏭️
    SERVED --> [*]: Terminal (permanent)
    SKIPPED --> [*]: Terminal (permanent)
    SKIPPED --> WAITING: Rejoin (new position)
```

Once someone is **SERVED** or **SKIPPED**, that's final. The only way back to WAITING is to rejoin the queue (they go to the end of the line).

</details>

<details>
<summary><strong>🔗 What is "request tracing"?</strong></summary>
<br>

Every API call gets a unique ID (UUID). This ID appears in:
- 📤 The response header (`X-Request-ID`)
- 📝 The structured JSON logs
- 📜 The event timeline

If something goes wrong, search for that ID to find exactly what happened across all layers.

</details>

<details>
<summary><strong>🛡️ What is the "rules engine"?</strong></summary>
<br>

The rules are simple Python functions that answer one question: **"Is this action allowed?"**

- If yes → they do nothing (the action proceeds)
- If no → they raise a `RuleViolation` error with a `rule_code`

Rules **don't perform** the action — they only gatekeep it. This separation means you can test every rule independently, without needing a database.

```python
# Example: Rule 1 — No duplicate joins
def validate_no_duplicate_waiting(queue_id, user_name, entries):
    for entry in entries:
        if entry.user_name == user_name and entry.status == "WAITING":
            raise RuleViolation(
                "User already waiting in this queue.",
                rule_code="DUPLICATE_JOIN"
            )
```

</details>

---

## 📁 Project Structure

<details>
<summary><strong>🗂️ Full file tree (click to expand)</strong></summary>
<br>

```
queuewise-app/
│
├── README.md                        ← You are here!
├── agents.md                        ← AI governance rules
├── TRADEOFFS.md                     ← Design decisions explained
│
├── backend/
│   ├── run.py                       ← Entry point
│   ├── requirements.txt             ← Python dependencies
│   ├── app/
│   │   ├── __init__.py              ← App factory
│   │   ├── config.py                ← Settings (DB URL, test mode)
│   │   ├── database.py              ← SQLAlchemy setup
│   │   ├── logging_utils.py         ← Structured logging + tracing
│   │   ├── ai/
│   │   │   └── explainer.py         ← 🤖 AI text generation (read-only)
│   │   ├── models/
│   │   │   ├── queue.py             ← Queue table
│   │   │   ├── queue_entry.py       ← QueueEntry table
│   │   │   └── queue_event.py       ← QueueEvent table
│   │   ├── rules/
│   │   │   ├── exceptions.py        ← RuleViolation exception
│   │   │   └── queue_rules.py       ← 🛡️ All 8 business rules
│   │   ├── schemas/
│   │   │   └── queue_schema.py      ← Marshmallow validation
│   │   ├── repositories/
│   │   │   └── queue_repository.py  ← Database operations
│   │   ├── services/
│   │   │   └── queue_service.py     ← ⚙️ Business orchestration
│   │   └── routes/
│   │       └── queue_routes.py      ← 🛣️ HTTP endpoints
│   │
│   └── tests/                       ← 67 tests across 11 files
│
└── frontend/
    └── src/
        ├── App.tsx                  ← Main app (state + layout)
        ├── api.ts                   ← API client
        ├── types.ts                 ← TypeScript types
        └── components/
            ├── JoinForm.tsx         ← Name input + validation
            ├── ActionPanel.tsx      ← Serve / Skip / Pause buttons
            ├── QueueBoard.tsx       ← Waiting list
            ├── QueueSummary.tsx     ← Counts dashboard
            ├── ExplanationPanel.tsx ← AI explanation display
            ├── PreviewPanel.tsx     ← "What happens next?"
            ├── EventTimeline.tsx    ← Event history
            └── ErrorBoundary.tsx    ← Crash recovery
```

</details>

---

## 🔧 Configuration

| Variable | Default | Description |
|:---------|:--------|:------------|
| `DATABASE_URL` | `sqlite:///queuewise.db` | Database connection. Change for PostgreSQL |

```bash
# Switch to PostgreSQL
export DATABASE_URL="postgresql://user:pass@localhost/queuewise"
```

---

## 📝 Learn More

| Document | What's Inside |
|:---------|:--------------|
| [📋 agents.md](agents.md) | How AI is constrained — full governance rules |
| [⚖️ TRADEOFFS.md](TRADEOFFS.md) | 10 design decisions, tradeoffs, and weaknesses |

---

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=14&pause=1000&color=667EEA&center=true&vCenter=true&width=500&lines=Built+with+%E2%9D%A4%EF%B8%8F+for+clinics%2C+salons+%26+service+centers;Rules+keep+the+queue+fair.+AI+keeps+users+informed.;67+tests.+8+rules.+Zero+magic." alt="Footer typing" />
</p>

<p align="center">
  <sub>
    <strong>QueueWise</strong> — Fair queues, friendly explanations, full accountability.
  </sub>
</p>
