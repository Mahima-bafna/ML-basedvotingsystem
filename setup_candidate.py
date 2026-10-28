
from database import create_tables, connect_db


def setup_candidates():
    create_tables()

    connection = connect_db()

    candidates = [
        ("Candidate A",),
        ("Candidate B",),
        ("Candidate C",)
    ]

    connection.executemany(
        "INSERT OR IGNORE INTO candidates (name) VALUES (?)",
        candidates
    )

    connection.commit()
    connection.close()

    print("Candidates added successfully!")


if __name__ == "__main__":
    setup_candidates()
