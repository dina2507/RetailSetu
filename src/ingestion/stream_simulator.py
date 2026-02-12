import pandas as pd
import time
import random
from faker import Faker
import os

fake = Faker('en_IN')

# Configuration
DATA_DIR = "data"
POS_FILE = f"{DATA_DIR}/silo_pos_transactions.csv"
STREAM_DELAY = 3  # Seconds between new orders

print("🌊 STARTING REAL-TIME TRANSACTION STREAM...")
print(f"   - Target: {POS_FILE}")
print("   - Press Ctrl+C to stop.")

def generate_single_transaction():
    """Creates one realistic transaction."""
    return {
        "transaction_id": fake.uuid4(),
        "store_id": "WEB_STORE",  # Mark as Online Order
        "product_id": f"P{random.randint(1, 20):03d}",
        "quantity": random.randint(1, 3),
        "total_amount": round(random.uniform(100, 5000), 2),
        "payment_mode": "UPI",
        "timestamp": pd.Timestamp.now().isoformat(),
        "customer_id": f"C{random.randint(1, 100):03d}"
    }

# Infinite Loop to simulate Real-Time
try:
    while True:
        # 1. Generate Data
        new_txn = generate_single_transaction()
        df_new = pd.DataFrame([new_txn])

        # 2. Append to existing CSV (Simulating a database update)
        # mode='a' means append; header=False so we don't repeat headers
        df_new.to_csv(POS_FILE, mode='a', header=not os.path.exists(POS_FILE), index=False)

        print(f"⚡ [REAL-TIME] New Order: {new_txn['transaction_id']} | ₹{new_txn['total_amount']}")
        
        # 3. Wait
        time.sleep(STREAM_DELAY)

except KeyboardInterrupt:
    print("\n🛑 Stream Stopped.")