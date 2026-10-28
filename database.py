
import sqlite3

DB_NAME = "voting.db"


def connect_db():
    connection = sqlite3.connect(DB_NAME)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables():
    connection = connect_db()

    try:
        cursor = connection.cursor()

        # Preserve the existing voters table and its data.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                voter_id TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)

        # Preserve the existing candidates table and its data.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)

        # Preserve existing recorded votes.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                voter_id INTEGER NOT NULL UNIQUE,
                candidate_id INTEGER NOT NULL,
                FOREIGN KEY (voter_id) REFERENCES voters(id),
                FOREIGN KEY (candidate_id) REFERENCES candidates(id)
            )
        """)

        # New table for administrator accounts.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    create_tables()
    print("Database initialized. Existing data was preserved.")
