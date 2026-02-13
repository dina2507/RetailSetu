import pandas as pd
import os
from cleaning_rules import clean_pos_data, clean_inventory_data

# Define Paths
DATA_DIR = "data"
RAW_POS_PATH = f"{DATA_DIR}/silo_pos_transactions.csv"
RAW_INV_PATH = f"{DATA_DIR}/silo_warehouse.csv"

SILVER_POS_PATH = f"{DATA_DIR}/silver_pos_transactions.csv"
SILVER_INV_PATH = f"{DATA_DIR}/silver_warehouse.csv"

def run_silver_transformation():
    print("STARTING: Bronze -> Silver Transformation Pipeline...")

    # --- 1. Process POS Transactions ---
    if os.path.exists(RAW_POS_PATH):
        print(f"Reading Raw Data: {RAW_POS_PATH}")
        df_pos = pd.read_csv(RAW_POS_PATH)
        
        # Apply the logic you wrote
        df_clean_pos = clean_pos_data(df_pos)
        
        # Save to Silver Layer
        df_clean_pos.to_csv(SILVER_POS_PATH, index=False)
        print(f"💾 Saved Silver Data: {SILVER_POS_PATH}")
    else:
        print(f"⚠️ ERROR: Could not find {RAW_POS_PATH}. Did Member 1 run the generator?")

    # --- 2. Process Inventory ---
    if os.path.exists(RAW_INV_PATH):
        print(f"Reading Raw Data: {RAW_INV_PATH}")
        df_inv = pd.read_csv(RAW_INV_PATH)
        
        # Apply the logic
        df_clean_inv = clean_inventory_data(df_inv)
        
        # Save to Silver Layer
        df_clean_inv.to_csv(SILVER_INV_PATH, index=False)
        print(f"💾 Saved Silver Data: {SILVER_INV_PATH}")

    print("🎉 SUCCESS: Silver Layer Created.")

if __name__ == "__main__":
    run_silver_transformation()