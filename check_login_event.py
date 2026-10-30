
from database import connect_db

conn = connect_db()

try:
    tables = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
    """).fetchall()

    print("Database tables:")
    for table in tables:
        print("-", table[0])

    print("\nLogin-event table structure:")
    try:
        columns = conn.execute(
            "PRAGMA table_info(login_events)"
        ).fetchall()

        for column in columns:
            print(column)

        count = conn.execute(
            "SELECT COUNT(*) FROM login_events"
        ).fetchone()[0]

        print("\nTotal login events:", count)

        rows = conn.execute("""
            SELECT id, voter_id, success, event_time
            FROM login_events
            ORDER BY id DESC
            LIMIT 5
        """).fetchall()

        print("Recent events:", rows)

    except Exception as error:
        print("Could not inspect login_events:", error)

finally:
    conn.close()

