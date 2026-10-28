
import pandas as pd
import random

# Make the experiment reproducible.
random.seed(42)

records = []

for _ in range(1000):
    failed_attempts = random.randint(0, 12)
    attempts_per_minute = random.randint(1, 20)
    unique_accounts = random.randint(1, 8)
    unusual_hour = random.randint(0, 1)

    # Synthetic training label for our classroom project.
    # These rules create example labels; they are not
    # a real-world definition of fraud.
    suspicious_score = 0

    if failed_attempts >= 5:
        suspicious_score += 1

    if attempts_per_minute >= 10:
        suspicious_score += 1

    if unique_accounts >= 4:
        suspicious_score += 1

    if unusual_hour == 1:
        suspicious_score += 1

    # Label 1 means suspicious; 0 means normal.
    is_suspicious = int(suspicious_score >= 2)

    records.append({
        "failed_attempts": failed_attempts,
        "attempts_per_minute": attempts_per_minute,
        "unique_accounts": unique_accounts,
        "unusual_hour": unusual_hour,
        "is_suspicious": is_suspicious
    })

df = pd.DataFrame(records)

df.to_csv("fraud_dataset.csv", index=False)

print("Dataset created successfully!")
print("Number of records:", len(df))
print("\nFirst five records:")
print(df.head())

print("\nClass distribution:")
print(df["is_suspicious"].value_counts().sort_index())
