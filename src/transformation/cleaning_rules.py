import pandas as pd
import numpy as np

def clean_pos_data(df):
    """
    Cleans the Raw POS Data (Bronze -> Silver).
    1. Removes duplicates.
    2. Fixes negative amounts (Data Contract).
    3. Standardizes dates.
    """
    print("🧹 Starting POS Data Cleaning...")
    
    # 1. Drop Duplicates
    initial_count = len(df)
    df = df.drop_duplicates(subset=['transaction_id'])
    print(f"   - Removed {initial_count - len(df)} duplicate rows.")

    # 2. DATA CONTRACT: Remove Negative Amounts (The "Quarantine" Logic)
    # In a real system, we'd save these to a 'quarantine_table' instead of dropping.
    invalid_rows = df[df['total_amount'] < 0]
    if not invalid_rows.empty:
        print(f"   - ⚠️ FOUND {len(invalid_rows)} INVALID ROWS (Negative Price). Removing them...")
        df = df[df['total_amount'] >= 0]
    
    # 3. Standardize Dates
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    print("✅ POS Data Cleaned Successfully.")
    return df

def clean_inventory_data(df):
    """
    Cleans Warehouse Data.
    1. Fills missing stock levels with 0.
    """
    print("🧹 Starting Inventory Cleaning...")
    df['stock_level'] = df['stock_level'].fillna(0).astype(int)
    print("✅ Inventory Data Cleaned.")
    return df