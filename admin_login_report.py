
from database import connect_db


def view_login_report():
    conn = connect_db()

    try:
        total = conn.execute(
            "SELECT COUNT(*) FROM login_events"
        ).fetchone()[0]

        successful = conn.execute(
            "SELECT COUNT(*) FROM login_events WHERE success = 1"
        ).fetchone()[0]

        failed = conn.execute(
            "SELECT COUNT(*) FROM login_events WHERE success = 0"
        ).fetchone()[0]

        print("\n--- Login Activity Report ---")
        print("Total attempts:", total)
        print("Successful attempts:", successful)
        print("Failed attempts:", failed)

        rows = conn.execute("""
            SELECT voter_id, success, event_time
            FROM login_events
            ORDER BY id DESC
            LIMIT 20
        """).fetchall()

        print("\n--- Recent Login Events ---")

        for voter_id, success, event_time in rows:
            status = "SUCCESS" if success else "FAILED"
            print(
                f"Account ID: {voter_id} | "
                f"Status: {status} | "
                f"Time: {event_time}"
            )

    finally:
        conn.close()


if __name__ == "__main__":
    view_login_report()

