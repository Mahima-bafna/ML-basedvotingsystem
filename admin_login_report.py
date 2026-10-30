
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

        flagged = conn.execute(
            """
            SELECT COUNT(*)
            FROM login_assessments
            WHERE prediction = 1
            """
        ).fetchone()[0]

        print("\n--- Login Activity Report ---")
        print("Total attempts:", total)
        print("Successful attempts:", successful)
        print("Failed attempts:", failed)
        print("ML flagged attempts:", flagged)

        rows = conn.execute(
            """
            SELECT
                e.voter_id,
                e.success,
                e.event_time,
                a.prediction
            FROM login_events e
            LEFT JOIN login_assessments a
                ON e.id = a.event_id
            ORDER BY e.id DESC
            LIMIT 20
            """
        ).fetchall()

        print("\n--- Recent Login Events ---")

        for voter_id, success, event_time, prediction in rows:

            status = "SUCCESS" if success else "FAILED"

            if prediction is None:
                ml_status = "NOT ASSESSED"
            elif prediction == 1:
                ml_status = "FLAGGED"
            else:
                ml_status = "NOT FLAGGED"

            print(
                f"Account ID: {voter_id} | "
                f"Status: {status} | "
                f"ML: {ml_status} | "
                f"Time: {event_time}"
            )

    finally:
        conn.close()
