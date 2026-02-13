import pandas as pd
import os

DATA_PATH = "data"


def validate_scd():
    path = os.path.join(DATA_PATH, "dim_customers_scd2.csv")

    if not os.path.exists(path):
        raise FileNotFoundError("dim_customers_scd2.csv not found")

    df = pd.read_csv(path)

    print("Running SCD Type 2 Validation...\n")

    # Check 1: Only one current record per customer
    current_counts = df[df["is_current"] == True].groupby("customer_id").size()

    invalid_customers = current_counts[current_counts > 1]

    if len(invalid_customers) > 0:
        print("❌ Multiple current records found for customers:")
        print(invalid_customers)
    else:
        print("✅ One current record per customer check passed.")

    # Check 2: start_date not null
    if df["start_date"].isnull().sum() > 0:
        print("❌ Null start_date values found.")
    else:
        print("✅ No null start_date values.")

    # Check 3: end_date should be null only for current records
    invalid_end = df[(df["is_current"] == False) & (df["end_date"].isnull())]

    if len(invalid_end) > 0:
        print("❌ Non-current records missing end_date.")
    else:
        print("✅ End date logic correct.")

    print("\nSCD validation completed.")


if __name__ == "__main__":
    validate_scd()