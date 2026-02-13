import pandas as pd
import os

# Base data directory
DATA_PATH = "data"


def build_fact_sales():
    """
    Builds fact_sales table from silver_pos_transactions.csv
    Grain: One row per product per transaction
    """
    pos_path = os.path.join(DATA_PATH, "silver_pos_transactions.csv")

    if not os.path.exists(pos_path):
        raise FileNotFoundError("silver_pos_transactions.csv not found in data/")

    df = pd.read_csv(pos_path)

    # Convert timestamp
    df["sale_timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Create date breakdown columns
    df["sale_date"] = df["sale_timestamp"].dt.date
    df["sale_year"] = df["sale_timestamp"].dt.year
    df["sale_month"] = df["sale_timestamp"].dt.month

    # Select fact columns
    fact_sales = df[
        [
            "transaction_id",
            "store_id",
            "product_id",
            "customer_id",
            "quantity",
            "total_amount",
            "payment_mode",
            "sale_timestamp",
            "sale_date",
            "sale_year",
            "sale_month",
        ]
    ]

    output_path = os.path.join(DATA_PATH, "fact_sales.csv")
    fact_sales.to_csv(output_path, index=False)

    print("✅ fact_sales created successfully.")


def build_fact_inventory():
    """
    Builds fact_inventory table from silver_inventory.csv
    Grain: One row per store per product snapshot
    """
    inventory_path = os.path.join(DATA_PATH, "silver_inventory.csv")

    if not os.path.exists(inventory_path):
        raise FileNotFoundError("silver_inventory.csv not found in data/")

    df = pd.read_csv(inventory_path)

    # Convert restock date
    df["inventory_date"] = pd.to_datetime(df["last_restocked"], errors="coerce").dt.date
    df["inventory_year"] = pd.to_datetime(df["last_restocked"], errors="coerce").dt.year
    df["inventory_month"] = pd.to_datetime(df["last_restocked"], errors="coerce").dt.month

    fact_inventory = df[
        [
            "store_id",
            "product_id",
            "stock_level",
            "last_restocked",
            "inventory_date",
            "inventory_year",
            "inventory_month",
        ]
    ]

    output_path = os.path.join(DATA_PATH, "fact_inventory.csv")
    fact_inventory.to_csv(output_path, index=False)

    print("✅ fact_inventory created successfully.")


if __name__ == "__main__":
    build_fact_sales()
    build_fact_inventory()