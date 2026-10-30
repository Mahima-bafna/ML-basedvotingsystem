
from database import connect_db
from login_events import (
    initialize_login_events,
    record_login_event,
)

initialize_login_events()

# Insert a test event with no voter ID.
record_login_event(None, False)

conn = connect_db()

try:
    count = conn.execute(
        "SELECT COUNT(*) FROM login_events"
    ).fetchone()[0]

    print("Total login events:", count)

    latest = conn.execute("""
        SELECT id, voter_id, success, event_time
        FROM login_events
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    print("Latest event:", latest)
finally:
    conn.close()
