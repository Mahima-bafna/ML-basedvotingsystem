
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report
)

# =====================================
# 1. LOAD THE DATASET
# =====================================

df = pd.read_csv("fraud_dataset.csv")

print("Dataset loaded successfully!")
print("Dataset shape:", df.shape)

# =====================================
# 2. SEPARATE FEATURES AND LABEL
# =====================================

features = [
    "failed_attempts",
    "attempts_per_minute",
    "unique_accounts",
    "unusual_hour"
]

X = df[features]
y = df["is_suspicious"]

# X = input information
# y = expected answer (0 or 1)

# =====================================
# 3. SPLIT TRAINING AND TEST DATA
# =====================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))

# =====================================
# 4. CREATE AND TRAIN THE MODEL
# =====================================

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

print("\nModel training completed!")

# =====================================
# 5. EVALUATE THE MODEL
# =====================================

predictions = model.predict(X_test)

print("\nAccuracy:",
      round(accuracy_score(y_test, predictions), 3))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions, labels=[0, 1]))

print("\nClassification Report:")
print(classification_report(
    y_test,
    predictions,
    labels=[0, 1],
    target_names=["Normal", "Suspicious"],
    zero_division=0
))

# =====================================
# 6. SAVE THE TRAINED MODEL
# =====================================

joblib.dump(
    {
        "model": model,
        "features": features
    },
    "fraud_model.joblib"
)

print("\nModel saved as fraud_model.joblib")
print("Lesson 7 completed successfully!")
