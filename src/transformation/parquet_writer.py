import pandas as pd
import os


DATA_PATH = "data"
PARQUET_BASE_PATH = os.path.join(DATA_PATH, "gold_parquet")


def write_fact_sales_parquet():
    sales_path = os.path.join(DATA_PATH, "fact_sales.csv")

    if not os.path.exists(sales_path):
        raise FileNotFoundError("fact_sales.csv not found")

    df = pd.read_csv(sales_path)

    output_path = os.path.join(PARQUET_BASE_PATH, "fact_sales")

    df.to_parquet(
        output_path,
        engine="pyarrow",
        partition_cols=["sale_year", "sale_month"],
        index=False
    )

    print("✅ fact_sales written to Parquet with partitioning.")


def write_fact_inventory_parquet():
    inventory_path = os.path.join(DATA_PATH, "fact_inventory.csv")

    if not os.path.exists(inventory_path):
        raise FileNotFoundError("fact_inventory.csv not found")

    df = pd.read_csv(inventory_path)

    output_path = os.path.join(PARQUET_BASE_PATH, "fact_inventory")

    df.to_parquet(
        output_path,
        engine="pyarrow",
        partition_cols=["inventory_year", "inventory_month"],
        index=False
    )

    print("✅ fact_inventory written to Parquet with partitioning.")


if __name__ == "__main__":
    write_fact_sales_parquet()
    write_fact_inventory_parquet()