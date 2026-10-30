
import pandas as pd
import random

random.seed(42)

data = []

for _ in range(1000):
    failed_attempts = random.randint(0, 12)
    attempts_per_minute = random.randint(1, 20)
    unusual_hour = random.randint(0, 1)

    # Demonstration labels based on simple rules.
    suspicious = (
        failed_attempts >= 5
        or (
            attempts_per_minute >= 10
            and unusual_hour == 1
        )
    )

    data.append({
        "failed_attempts": failed_attempts,
        "attempts_per_minute": attempts_per_minute,
        "unusual_hour": unusual_hour,
        "is_suspicious": int(suspicious)
    })

df = pd.DataFrame(data)

df.to_csv("fraud_dataset.csv", index=False)

print("Fraud detection dataset created successfully!")
print(df.head())
print("\nDataset shape:", df.shape)
print("\nClass distribution:")
print(df["is_suspicious"].value_counts())
