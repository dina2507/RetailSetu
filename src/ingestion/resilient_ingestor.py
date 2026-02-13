import pandas as pd
import time
import os
import logging
from datetime import datetime

# Configuration
SOURCE_FILE = "data/silo_pos_transactions.csv"
EXPECTED_SCHEMA = [
    'transaction_id',
    'store_id',
    'product_id',
    'quantity',
    'total_amount',
    'payment_mode',
    'timestamp',
    'customer_id'
]

LOG_FILE = "logs/ingestion.log"

# Setup Logging
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def ingest_data_safely(retries=3):
    """
    Reads data with:
    - Automatic Retries
    - Schema Validation
    - Logging
    """

    attempt = 0

    while attempt < retries:
        try:
            logging.info(f"Attempting ingestion (Try {attempt+1}/{retries})")

            if not os.path.exists(SOURCE_FILE):
                raise FileNotFoundError("Source file not found!")

            df = pd.read_csv(SOURCE_FILE)

            current_cols = list(df.columns)

            # Schema Evolution Detection
            new_cols = set(current_cols) - set(EXPECTED_SCHEMA)
            missing_cols = set(EXPECTED_SCHEMA) - set(current_cols)

            if new_cols:
                logging.warning(f"Schema Evolution Detected. New columns: {new_cols}")

            if missing_cols:
                logging.error(f"Missing required columns: {missing_cols}")
                for col in missing_cols:
                    df[col] = None
                logging.info("Filled missing columns with NULLs.")

            # Basic Data Validation
            if (df['total_amount'] < 0).any():
                logging.warning("Negative total_amount values detected.")

            df["ingestion_timestamp"] = datetime.now()

            logging.info(f"Ingestion Successful: {len(df)} records loaded.")

            return df

        except Exception as e:
            logging.error(f"Ingestion failed: {e}")
            attempt += 1
            time.sleep(2)

    logging.critical("Final Failure: Could not ingest after retries.")
    return None


if __name__ == "__main__":
    df = ingest_data_safely()
    if df is not None:
        print("Ingestion completed successfully.")
    else:
        print("Ingestion failed.")
