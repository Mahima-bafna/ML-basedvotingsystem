
import hashlib
import secrets
import sqlite3
import hmac
from getpass import getpass

from database import create_tables, connect_db


def hash_password(password):
    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        600_000
    )

    return salt.hex() + ":" + password_hash.hex()


def setup_admin():
    create_tables()

    print("\n--- Administrator Setup ---")

    username = input("Create admin username: ").strip()

    if not username:
        print("Username cannot be empty.")
        return

    connection = connect_db()

    try:
        existing = connection.execute(
            "SELECT 1 FROM admins WHERE username = ?",
            (username,)
        ).fetchone()

        if existing:
            print("That admin username already exists.")
            print("No account was changed.")
            return

        password = getpass("Create admin password: ")

        if len(password) < 12:
            print("Use a password with at least 12 characters.")
            return

        confirm = getpass("Confirm admin password: ")

        if not hmac.compare_digest(password, confirm):
            print("Passwords do not match.")
            return

        stored_hash = hash_password(password)

        connection.execute(
            """
            INSERT INTO admins (username, password_hash)
            VALUES (?, ?)
            """,
            (username, stored_hash)
        )

        connection.commit()
        print("Administrator account created successfully!")

    except sqlite3.IntegrityError:
        connection.rollback()
        print("Could not create the administrator account.")

    finally:
        connection.close()


if __name__ == "__main__":
    setup_admin()
