import pandas as pd
import time
import os

# Configuration
SOURCE_FILE = "data/silo_pos_transactions.csv"
EXPECTED_SCHEMA = ['transaction_id', 'store_id', 'product_id', 'quantity', 'total_amount', 'payment_mode', 'timestamp', 'customer_id']

def ingest_data_safely(retries=3):
    """
    Reads data with Automatic Retries and Schema Validation.
    """
    attempt = 0
    while attempt < retries:
        try:
            print(f"📥 Attempting to ingest data (Try {attempt+1}/{retries})...")
            
            # 1. Automatic Retry Logic 
            if not os.path.exists(SOURCE_FILE):
                raise FileNotFoundError("Source file not found!")
            
            df = pd.read_csv(SOURCE_FILE)
            
            # 2. Schema Evolution Handling 
            current_cols = list(df.columns)
            
            # Check if new columns appeared (Schema Evolution)
            new_cols = set(current_cols) - set(EXPECTED_SCHEMA)
            missing_cols = set(EXPECTED_SCHEMA) - set(current_cols)
            
            if new_cols:
                print(f"⚠️ SCHEMA EVOLUTION DETECTED: Found new columns {new_cols}")
                print("   -> Automatically adapting pipeline to include new fields...")
                # Logic: In a real DB, we would run 'ALTER TABLE ADD COLUMN' here.
                # For hackathon: We just acknowledge it and proceed (Pandas handles it).
            
            if missing_cols:
                print(f"🚨 CRITICAL SCHEMA ERROR: Missing columns {missing_cols}")
                # Logic: We might fill them with NULLs to prevent crash
                for col in missing_cols:
                    df[col] = None
                print("   -> Filled missing columns with NULLs to prevent crash.")

            print(f"✅ Ingestion Successful: {len(df)} records loaded.")
            return df

        except Exception as e:
            print(f"❌ Connection Failed: {e}")
            attempt += 1
            time.sleep(2)  # Wait before retry
            
    print("💀 Final Failure: Could not ingest data after retries.")
    return None

if __name__ == "__main__":
    # Test the resilient ingestion
    df = ingest_data_safely()