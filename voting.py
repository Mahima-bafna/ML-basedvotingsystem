import joblib
import pandas as pd
from admin_login_report import view_login_report
from login_events import (
    initialize_login_events,
    record_login_event,
    get_recent_activity,

)


import hashlib
import secrets
import hmac
import sqlite3
from getpass import getpass

from database import create_tables, connect_db


# =====================================
# PASSWORD SECURITY
# =====================================

def hash_password(password):
    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        600_000
    )

    return salt.hex() + ":" + password_hash.hex()


def verify_password(password, stored_hash):
    try:
        salt_hex, hash_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)

        attempted_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            600_000
        )

        return hmac.compare_digest(
            attempted_hash.hex(),
            hash_hex
        )

    except (ValueError, TypeError):
        return False


# =====================================
# VOTER REGISTRATION
# =====================================

def register_voter():
    print("\n--- Voter Registration ---")

    voter_id = input("Create a voter ID: ").strip()

    if not voter_id:
        print("Voter ID cannot be empty.")
        return

    password = getpass("Create a password: ")

    if len(password) < 12:
        print("Password must contain at least 12 characters.")
        return

    confirm = getpass("Confirm password: ")

    if not hmac.compare_digest(password, confirm):
        print("Passwords do not match.")
        return

    connection = connect_db()

    try:
        connection.execute(
            """
            INSERT INTO voters (voter_id, password_hash)
            VALUES (?, ?)
            """,
            (voter_id, hash_password(password))
        )

        connection.commit()
        print("Registration successful!")

    except sqlite3.IntegrityError:
        print("That voter ID is already registered.")

    finally:
        connection.close()


# =====================================
# VOTER LOGIN
# =====================================


def voter_login():
    print("\n--- Voter Login ---")

    voter_id = input("Enter your voter ID: ").strip()
    password = getpass("Enter your password: ")

    connection = connect_db()

    try:
        result = connection.execute(
            """
            SELECT id, password_hash
            FROM voters
            WHERE voter_id = ?
            """,
            (voter_id,),
        ).fetchone()

        # Never log or save the password.
        if result and verify_password(password, result[1]):
            record_login_event(result[0], True)
            print("Voter login successful!")

            # Advisory ML check; it does not control authentication.
            try:
                activity = get_recent_activity(result[0])

                if activity is not None:
                    saved_data = joblib.load("fraud_model.joblib")
                    model = saved_data["model"]
                    features = saved_data["features"]

                    input_data = pd.DataFrame(
                        [activity], columns=features
                    )
                    prediction = int(model.predict(input_data)[0])

                    if prediction == 1:
                        print(
                            "ADVISORY: Login activity flagged "
                            "for admin review."
                        )
                    else:
                        print(
                            "ML check: Activity was not flagged."
                        )

                    print(
                        "This model is experimental and does not "
                        "prove fraud."
                    )

            except (FileNotFoundError, KeyError, ValueError) as error:
                print(
                    "ML advisory check unavailable; "
                    "login can continue."
                )
                print("Check the model file and feature names.")

            return result[0]

        # Use the account ID only if the supplied voter ID exists.
        if result:
            record_login_event(result[0], False)
        else:
            record_login_event(None, False)

        print("Invalid voter ID or password.")
        return None

    finally:
        connection.close()


# =====================================
# ADMIN LOGIN
# =====================================

def admin_login():
    print("\n--- Administrator Login ---")

    username = input("Admin username: ").strip()
    password = getpass("Admin password: ")

    connection = connect_db()

    try:
        result = connection.execute(
            """
            SELECT id, password_hash
            FROM admins
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        if result and verify_password(password, result[1]):
            print("Administrator login successful!")
            return result[0]

        print("Invalid administrator username or password.")
        return None

    finally:
        connection.close()


# =====================================
# CAST VOTE
# =====================================

def cast_vote(database_voter_id):
    connection = connect_db()

    try:
        cursor = connection.cursor()

        already_voted = cursor.execute(
            "SELECT 1 FROM votes WHERE voter_id = ?",
            (database_voter_id,)
        ).fetchone()

        if already_voted:
            print("You have already voted.")
            return

        candidates = cursor.execute(
            "SELECT id, name FROM candidates ORDER BY id"
        ).fetchall()

        if not candidates:
            print("No candidates are available.")
            return

        print("\n--- Candidates ---")

        for candidate_id, name in candidates:
            print(f"{candidate_id}. {name}")

        try:
            choice = int(input("Enter candidate number: "))
        except ValueError:
            print("Enter a valid candidate number.")
            return

        valid_ids = [candidate[0] for candidate in candidates]

        if choice not in valid_ids:
            print("Invalid candidate selection.")
            return

        cursor.execute(
            """
            INSERT INTO votes (voter_id, candidate_id)
            VALUES (?, ?)
            """,
            (database_voter_id, choice)
        )

        connection.commit()
        print("Vote recorded successfully!")

    except sqlite3.IntegrityError:
        connection.rollback()
        print("A vote has already been recorded for this account.")

    finally:
        connection.close()


# =====================================
# ADMIN-ONLY ELECTION RESULTS
# =====================================

def view_results(admin_session):
    # Check authorization before querying vote totals.
    if admin_session is None:
        print("Access denied. Administrator login is required.")
        return

    connection = connect_db()

    try:
        results = connection.execute("""
            SELECT candidates.name, COUNT(votes.id)
            FROM candidates
            LEFT JOIN votes
                ON candidates.id = votes.candidate_id
            GROUP BY candidates.id, candidates.name
            ORDER BY candidates.id
        """).fetchall()

        print("\n--- Protected Election Results ---")

        for name, total in results:
            print(f"{name}: {total} vote(s)")

    finally:
        connection.close()


# =====================================
# MAIN MENU
# =====================================

def show_menu():
    print("\n" + "=" * 40)
    print("       ONLINE VOTING SYSTEM")
    print("=" * 40)
    print("1. Voter Registration")
    print("2. Voter Login")
    print("3. Cast Vote")
    print("4. Admin Login")
    print("5. View Election Results (Admin only)")
    print("6. Logout")
    print("7. View Login Activity Report (Admin Only)")
    print("0. Exit")



def main():
    create_tables()
    initialize_login_events()

    logged_in_voter = None
    logged_in_admin = None

    while True:
        show_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            register_voter()

        elif choice == "2":
            logged_in_voter = voter_login()

        elif choice == "3":
            if logged_in_voter is None:
                print("Please log in as a voter first.")
            else:
                cast_vote(logged_in_voter)

        elif choice == "4":
            logged_in_admin = admin_login()

        elif choice == "5":
            if logged_in_admin is None:
                print("Please log in as an administrator first.")
            else:
                view_results(logged_in_admin)

        elif choice == "7":
            if logged_in_admin is None:
                print("Please log in as an administrator first.")
            else:
                view_login_report()

        elif choice == "6":
            logged_in_voter = None
            logged_in_admin = None
            print("You have been logged out.")

        elif choice == "0":
            logged_in_voter = None
            logged_in_admin = None
            print("Thank you for using the voting system!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
