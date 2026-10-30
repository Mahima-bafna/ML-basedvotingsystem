
import sqlite3
from datetime import datetime, timezone

from database import connect_db


def initialize_login_events():
    """Add a login-event table without changing existing voting tables."""
    conn = connect_db()

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS login_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                voter_id INTEGER,
                success INTEGER NOT NULL CHECK (success IN (0, 1)),
                event_time TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_login_events_voter_time
            ON login_events (voter_id, event_time)
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS login_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL UNIQUE,
                prediction INTEGER NOT NULL
                    CHECK (prediction IN (0, 1)),
                assessed_at TEXT NOT NULL,
                FOREIGN KEY (event_id)
                    REFERENCES login_events(id)
            )
        """)


        conn.commit()
    finally:
        conn.close()


def record_login_event(voter_id, success):
    """
    Store an outcome only.
    voter_id should be None for an unknown account.
    """
    if success not in (True, False, 0, 1):
        raise ValueError("success must be True or False")

    timestamp = datetime.now(timezone.utc).isoformat()

    conn = connect_db()
    try:
        conn.execute(
            """
            INSERT INTO login_events (voter_id, success, event_time)
            VALUES (?, ?, ?)
            """,
            (
                voter_id,
                int(success),
                timestamp,
            ),
        )
        conn.commit()
        event_id = conn.execute(
            "SELECT last_insert_rowid()"
        ).fetchone()[0]

        return event_id

    finally:
        conn.close()


def record_ml_assessment(event_id, prediction):
    """Save the ML prediction for a login event."""

    if prediction not in (0, 1):
        raise ValueError("prediction must be 0 or 1")

    timestamp = datetime.now(timezone.utc).isoformat()

    conn = connect_db()

    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO login_assessments
            (event_id, prediction, assessed_at)
            VALUES (?, ?, ?)
            """,
            (event_id, prediction, timestamp),
        )

        conn.commit()

    finally:
        conn.close()                



def get_recent_activity(voter_id):
    """
    Calculate login activity for a known voter.
    Uses a 15-minute window and a 1-minute window.
    """

    if voter_id is None:
        return None

    conn = connect_db()

    try:
        rows = conn.execute(
            """
            SELECT success, event_time
            FROM login_events
            WHERE voter_id = ?
            ORDER BY event_time DESC
            LIMIT 100
            """,
            (voter_id,),
        ).fetchall()
    finally:
        conn.close()

    now = datetime.now(timezone.utc)

    recent_15 = []
    recent_1 = []

    for success, event_time in rows:
        try:
            event_time = datetime.fromisoformat(event_time)

            if event_time.tzinfo is None:
                event_time = event_time.replace(
                    tzinfo=timezone.utc
                )

            event_time = event_time.astimezone(timezone.utc)

        except (TypeError, ValueError):
            continue

        age_seconds = (now - event_time).total_seconds()

        if 0 <= age_seconds <= 15 * 60:
            recent_15.append((success, age_seconds))

        if 0 <= age_seconds <= 60:
            recent_1.append((success, age_seconds))

    failed_attempts = sum(
        1 for success, _ in recent_15 if success == 0
    )

    attempts_per_minute = len(recent_1)

    hour = now.hour
    unusual_hour = int(hour < 6 or hour >= 22)

    return {
        "failed_attempts": min(failed_attempts, 12),
        "attempts_per_minute": max(
            1, min(attempts_per_minute, 20)
        ),
        "unusual_hour": unusual_hour,
    }
