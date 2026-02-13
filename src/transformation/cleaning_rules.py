import pandas as pd
import numpy as np

def clean_pos_data(df):
    """
    Cleans the Raw POS Data (Bronze -> Silver).
    """
    print("🧹 Starting POS Data Cleaning...")
    
    # 1. Drop Duplicates
    initial_count = len(df)
    df = df.drop_duplicates(subset=['transaction_id'])
    print(f"   - Removed {initial_count - len(df)} duplicate rows.")

    # 2. DATA CONTRACT: Remove Negative Amounts
    invalid_rows = df[df['total_amount'] < 0]
    if not invalid_rows.empty:
        print(f"   - ⚠️ FOUND {len(invalid_rows)} INVALID ROWS (Negative Price). Removing them...")
        df = df[df['total_amount'] >= 0]
    
    # 3. Standardize Dates
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
    
    print("✅ POS Data Cleaned Successfully.")
    return df

def clean_inventory_data(df):
    """
    Cleans the Warehouse Data.
    Handles missing columns automatically to prevent crashes.
    """
    print("🧹 Starting Inventory Cleaning...")
    
    # DEBUG: Print columns so we see what exists
    print(f"   - Columns found: {list(df.columns)}")

    # 1. Fill missing stock
    if 'stock_level' in df.columns:
        df['stock_level'] = df['stock_level'].fillna(0)
    
    # 2. SMART FIX: Handle missing 'store_id'
    if 'store_id' not in df.columns:
        # Check if it is named 'warehouse_id' or 'id'
        if 'warehouse_id' in df.columns:
            print("   - 🔄 Renaming 'warehouse_id' to 'store_id'...")
            df = df.rename(columns={'warehouse_id': 'store_id'})
        elif 'id' in df.columns:
            print("   - 🔄 Renaming 'id' to 'store_id'...")
            df = df.rename(columns={'id': 'store_id'})
        else:
            print("   - ⚠️ 'store_id' not found. Creating default 'WH-001'...")
            df['store_id'] = 'WH-001'

    # 3. Ensure IDs are strings
    df['store_id'] = df['store_id'].astype(str)
    
    print("✅ Inventory Data Cleaned Successfully.")
    return df