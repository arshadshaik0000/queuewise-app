"""Seed script: reset the database and populate with realistic data."""

import uuid
from datetime import datetime, timezone, timedelta

from app import create_app
from app.database import db
from app.models.queue import Queue, QueueStatus
from app.models.queue_entry import QueueEntry, EntryStatus
from app.models.queue_event import QueueEvent

app = create_app()

with app.app_context():
    # ── Drop everything and recreate ──────────────────────────────────
    db.drop_all()
    db.create_all()
    print("✓ Database reset — all tables recreated.")

    now = datetime.now(timezone.utc)

    # ── Queues ────────────────────────────────────────────────────────
    queues_data = [
        {"name": "City Hospital – Emergency Room", "status": QueueStatus.ACTIVE,
         "created_at": now - timedelta(days=14)},
        {"name": "DMV – License Renewal", "status": QueueStatus.ACTIVE,
         "created_at": now - timedelta(days=30)},
        {"name": "Starbucks – Downtown Drive-Thru", "status": QueueStatus.ACTIVE,
         "created_at": now - timedelta(days=7)},
        {"name": "Apple Store – Genius Bar", "status": QueueStatus.ACTIVE,
         "created_at": now - timedelta(days=21)},
        {"name": "University Library – Book Returns", "status": QueueStatus.PAUSED,
         "created_at": now - timedelta(days=45)},
        {"name": "Bank of America – Teller Service", "status": QueueStatus.ACTIVE,
         "created_at": now - timedelta(days=10)},
        {"name": "Tesla Service Center – Vehicle Pickup", "status": QueueStatus.ACTIVE,
         "created_at": now - timedelta(days=5)},
        {"name": "Costco – Pharmacy Pickup", "status": QueueStatus.PAUSED,
         "created_at": now - timedelta(days=60)},
    ]

    queues = []
    for qd in queues_data:
        q = Queue(name=qd["name"], status=qd["status"], created_at=qd["created_at"])
        db.session.add(q)
        queues.append(q)
    db.session.flush()  # assign IDs
    print(f"✓ Created {len(queues)} queues.")

    # ── Queue Entries ─────────────────────────────────────────────────
    entries_data = {
        0: [  # City Hospital – ER
            ("James Rodriguez", EntryStatus.SERVED, now - timedelta(hours=6)),
            ("Maria Chen", EntryStatus.SERVED, now - timedelta(hours=5, minutes=30)),
            ("Aisha Patel", EntryStatus.SERVED, now - timedelta(hours=4)),
            ("David Kim", EntryStatus.WAITING, now - timedelta(hours=2)),
            ("Fatima Al-Hassan", EntryStatus.WAITING, now - timedelta(hours=1, minutes=45)),
            ("Robert Johnson", EntryStatus.WAITING, now - timedelta(hours=1)),
            ("Emily Nguyen", EntryStatus.WAITING, now - timedelta(minutes=30)),
        ],
        1: [  # DMV – License Renewal
            ("Michael Thompson", EntryStatus.SERVED, now - timedelta(hours=3)),
            ("Sarah Williams", EntryStatus.SERVED, now - timedelta(hours=2, minutes=45)),
            ("Carlos Gutierrez", EntryStatus.SKIPPED, now - timedelta(hours=2, minutes=30)),
            ("Jennifer Lee", EntryStatus.SERVED, now - timedelta(hours=2)),
            ("Anthony Davis", EntryStatus.WAITING, now - timedelta(hours=1, minutes=30)),
            ("Priya Sharma", EntryStatus.WAITING, now - timedelta(hours=1)),
            ("Kevin O'Brien", EntryStatus.WAITING, now - timedelta(minutes=45)),
            ("Rachel Martinez", EntryStatus.WAITING, now - timedelta(minutes=20)),
            ("Daniel Park", EntryStatus.WAITING, now - timedelta(minutes=10)),
        ],
        2: [  # Starbucks – Drive-Thru
            ("Olivia Brown", EntryStatus.SERVED, now - timedelta(minutes=25)),
            ("Liam Wilson", EntryStatus.SERVED, now - timedelta(minutes=20)),
            ("Sophia Garcia", EntryStatus.WAITING, now - timedelta(minutes=12)),
            ("Noah Anderson", EntryStatus.WAITING, now - timedelta(minutes=8)),
            ("Emma Taylor", EntryStatus.WAITING, now - timedelta(minutes=3)),
        ],
        3: [  # Apple Store – Genius Bar
            ("Benjamin Clark", EntryStatus.SERVED, now - timedelta(hours=4)),
            ("Isabella Moore", EntryStatus.SERVED, now - timedelta(hours=3, minutes=15)),
            ("Alexander Wright", EntryStatus.SKIPPED, now - timedelta(hours=2, minutes=45)),
            ("Charlotte Harris", EntryStatus.WAITING, now - timedelta(hours=1, minutes=30)),
            ("Ethan Robinson", EntryStatus.WAITING, now - timedelta(hours=1)),
            ("Amelia Young", EntryStatus.WAITING, now - timedelta(minutes=40)),
        ],
        4: [  # University Library (PAUSED)
            ("Lucas Foster", EntryStatus.SERVED, now - timedelta(days=1, hours=5)),
            ("Mia Stewart", EntryStatus.SERVED, now - timedelta(days=1, hours=4)),
            ("Jack Turner", EntryStatus.WAITING, now - timedelta(days=1, hours=2)),
        ],
        5: [  # Bank of America – Teller Service
            ("Grace Phillips", EntryStatus.SERVED, now - timedelta(hours=2)),
            ("Henry Campbell", EntryStatus.SERVED, now - timedelta(hours=1, minutes=40)),
            ("Lily Morgan", EntryStatus.WAITING, now - timedelta(hours=1)),
            ("Samuel Perez", EntryStatus.WAITING, now - timedelta(minutes=35)),
            ("Chloe Rivera", EntryStatus.WAITING, now - timedelta(minutes=15)),
        ],
        6: [  # Tesla Service Center
            ("Owen Mitchell", EntryStatus.SERVED, now - timedelta(hours=5)),
            ("Zoe Carter", EntryStatus.WAITING, now - timedelta(hours=3)),
            ("William Brooks", EntryStatus.WAITING, now - timedelta(hours=1, minutes=20)),
        ],
        7: [  # Costco Pharmacy (PAUSED)
            ("Ella Murphy", EntryStatus.SERVED, now - timedelta(days=2, hours=3)),
            ("Logan Hughes", EntryStatus.SERVED, now - timedelta(days=2, hours=2)),
            ("Aria Jenkins", EntryStatus.SKIPPED, now - timedelta(days=2, hours=1)),
            ("Mason Powell", EntryStatus.WAITING, now - timedelta(days=2)),
        ],
    }

    total_entries = 0
    for q_idx, entries in entries_data.items():
        for pos, (name, status, joined_at) in enumerate(entries, start=1):
            entry = QueueEntry(
                queue_id=queues[q_idx].id,
                user_name=name,
                position=pos,
                status=status,
                joined_at=joined_at,
            )
            db.session.add(entry)
            total_entries += 1
    db.session.flush()
    print(f"✓ Created {total_entries} queue entries.")

    # ── Queue Events ──────────────────────────────────────────────────
    action_map = {
        EntryStatus.SERVED: ("SERVE", "SUCCESS"),
        EntryStatus.SKIPPED: ("SKIP", "SUCCESS"),
        EntryStatus.WAITING: ("JOIN", "SUCCESS"),
    }

    events = []
    for q_idx, entries in entries_data.items():
        queue_id = queues[q_idx].id
        for name, status, joined_at in entries:
            # JOIN event for every entry
            events.append(QueueEvent(
                queue_id=queue_id,
                action="JOIN",
                result="SUCCESS",
                detail=f"{name} joined the queue",
                request_id=str(uuid.uuid4())[:8],
                created_at=joined_at,
            ))
            # Additional event if served or skipped
            if status == EntryStatus.SERVED:
                events.append(QueueEvent(
                    queue_id=queue_id,
                    action="SERVE",
                    result="SUCCESS",
                    detail=f"{name} was served",
                    request_id=str(uuid.uuid4())[:8],
                    created_at=joined_at + timedelta(minutes=15),
                ))
            elif status == EntryStatus.SKIPPED:
                events.append(QueueEvent(
                    queue_id=queue_id,
                    action="SKIP",
                    result="SUCCESS",
                    detail=f"{name} was skipped — did not respond",
                    request_id=str(uuid.uuid4())[:8],
                    created_at=joined_at + timedelta(minutes=10),
                ))

    db.session.add_all(events)
    db.session.commit()
    print(f"✓ Created {len(events)} queue events.")
    print("\n🎉 Database seeded successfully!")
