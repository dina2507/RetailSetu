import pandas as pd
import os
import time
from cleaning_rules import clean_pos_data, clean_inventory_data

# Configuration
DATA_DIR = "data"
SILVER_POS_FILE = f"{DATA_DIR}/silver_pos_transactions.csv"
SILVER_INV_FILE = f"{DATA_DIR}/silver_inventory.csv"

def read_csv_with_retry(filepath, retries=5, delay=1):
    """
    Reads a CSV with automatic retries (Resilience Requirement).
    Fixes 'PermissionError' if the file is being written to at the same time.
    """
    for attempt in range(retries):
        try:
            return pd.read_csv(filepath)
        except (PermissionError, FileNotFoundError, pd.errors.EmptyDataError):
            if attempt < retries - 1:
                time.sleep(delay)  # Wait and try again
    return pd.DataFrame() # Return empty if failed after all retries

def run_silver_transformation():
    print("STARTING: Bronze -> Silver Transformation Pipeline...")

    # --- 1. Process POS Data (With Retries) ---
    df_pos = read_csv_with_retry(f"{DATA_DIR}/silo_pos_transactions.csv")
    
    if not df_pos.empty:
        df_clean_pos = clean_pos_data(df_pos)
        df_clean_pos.to_csv(SILVER_POS_FILE, index=False)
        print(f"💾 Saved Silver Data: {SILVER_POS_FILE}")
    else:
        print("⚠️ Skipping POS processing (File empty or locked).")

    # --- 2. Process Inventory Data (With Retries) ---
    df_inv = read_csv_with_retry(f"{DATA_DIR}/silo_warehouse.csv")
    
    if not df_inv.empty:
        df_clean_inv = clean_inventory_data(df_inv)
        df_clean_inv.to_csv(SILVER_INV_FILE, index=False)
        print(f"💾 Saved Silver Data: {SILVER_INV_FILE}")
    else:
        print("⚠️ Skipping Inventory processing.")

if __name__ == "__main__":
    run_silver_transformation()