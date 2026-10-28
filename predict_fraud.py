
import joblib
import pandas as pd


# =====================================
# 1. LOAD THE TRAINED MODEL
# =====================================

try:
    saved_data = joblib.load("fraud_model.joblib")
    model = saved_data["model"]
    features = saved_data["features"]

except FileNotFoundError:
    print("Model file not found.")
    print("Run: python train_model.py")
    raise SystemExit(1)


# =====================================
# 2. GET LOGIN ACTIVITY
# =====================================

def get_activity():
    print("\n--- Login Activity Details ---")

    try:
        failed_attempts = int(
            input("Failed attempts: ")
        )

        attempts_per_minute = int(
            input("Attempts per minute: ")
        )

        unique_accounts = int(
            input("Unique accounts attempted: ")
        )

        unusual_hour = int(
            input("Unusual hour? Enter 1 for yes, 0 for no: ")
        )

    except ValueError:
        print("Please enter numbers only.")
        return None

    if not 0 <= failed_attempts <= 12:
        print("Failed attempts must be between 0 and 12.")
        return None

    if not 1 <= attempts_per_minute <= 20:
        print("Attempts per minute must be between 1 and 20.")
        return None

    if not 1 <= unique_accounts <= 8:
        print("Unique accounts must be between 1 and 8.")
        return None

    if unusual_hour not in (0, 1):
        print("Unusual hour must be 0 or 1.")
        return None

    return {
        "failed_attempts": failed_attempts,
        "attempts_per_minute": attempts_per_minute,
        "unique_accounts": unique_accounts,
        "unusual_hour": unusual_hour
    }


# =====================================
# 3. PREDICT AND DISPLAY
# =====================================

def predict_activity(activity):
    input_data = pd.DataFrame(
        [activity],
        columns=features
    )

    prediction = int(model.predict(input_data)[0])

    probabilities = model.predict_proba(input_data)[0]
    suspicious_index = list(model.classes_).index(1)
    suspicious_probability = probabilities[suspicious_index]

    print("\n--- ML Prediction ---")

    if prediction == 1:
        print("FLAG FOR ADMIN REVIEW")
    else:
        print("Not flagged by the model")

    print(
        "Model's suspicious-class score:",
        f"{suspicious_probability:.1%}"
    )

    print(
        "\nReminder: this is a classroom model trained "
        "on synthetic labels, not proof of fraud."
    )


# =====================================
# 4. MAIN PROGRAM
# =====================================

if __name__ == "__main__":
    activity = get_activity()

    if activity is not None:
        predict_activity(activity)
