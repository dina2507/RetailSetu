import pandas as pd
import random
from faker import Faker
import json
import os
from datetime import datetime, timedelta

# Initialize Faker (Indian Locale for realism)
fake = Faker('en_IN')

# Configuration
NUM_CUSTOMERS = 100
NUM_PRODUCTS = 20
NUM_STORES = 5
NUM_TRANSACTIONS = 500
DATA_DIR = "data"

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

print("🚀 Starting Data Generation for Retail Setu...")

# --- 1. GENERATE PRODUCTS (Dimension Table) ---
products = []
categories = ['Electronics', 'Clothing', 'Home', 'Grocery']
for i in range(1, NUM_PRODUCTS + 1):
    products.append({
        "product_id": f"P{i:03d}",
        "product_name": fake.word().title(),
        "category": random.choice(categories),
        "price": round(random.uniform(100, 5000), 2),
        "supplier": fake.company()
    })

df_products = pd.DataFrame(products)
df_products.to_csv(f"{DATA_DIR}/dim_products.csv", index=False)
print(f"✅ Generated {NUM_PRODUCTS} Products.")

# --- 2. GENERATE POS TRANSACTIONS (The "Silo A") ---
transactions = []
payment_modes = ['UPI', 'Credit Card', 'Cash', 'Debit Card']

for _ in range(NUM_TRANSACTIONS):
    prod = random.choice(products)
    qty = random.randint(1, 5)
    
    # Intentionally creating "Messy Data" for Member 2 to clean:
    # 1. 2% chance of negative price (Error)
    # 2. 2% chance of a future date (Error)
    price = prod['price']
    if random.random() < 0.02: 
        price = price * -1  
    
    date_event = fake.date_time_between(start_date="-30d", end_date="now")
    if random.random() < 0.02:
        date_event = fake.date_time_between(start_date="+1d", end_date="+5d")

    transactions.append({
        "transaction_id": fake.uuid4(),
        "store_id": f"S{random.randint(1, NUM_STORES):03d}",
        "product_id": prod['product_id'],
        "quantity": qty,
        "total_amount": round(price * qty, 2),
        "payment_mode": random.choice(payment_modes),
        "timestamp": date_event,
        "customer_id": f"C{random.randint(1, NUM_CUSTOMERS):03d}"
    })

df_pos = pd.DataFrame(transactions)
df_pos.to_csv(f"{DATA_DIR}/silo_pos_transactions.csv", index=False)
print(f"✅ Generated {NUM_TRANSACTIONS} POS Transactions (with some errors!).")

# --- 3. GENERATE WAREHOUSE STOCK (The "Silo B") ---
inventory = []
warehouses = ['Mumbai_WH', 'Delhi_WH', 'Bangalore_WH']

for prod in products:
    for wh in warehouses:
        inventory.append({
            "warehouse_id": wh,
            "product_id": prod['product_id'],
            "stock_level": random.randint(0, 200),  # Some will be 0 (Stock-out!)
            "last_restocked": fake.date_this_year()
        })

df_inv = pd.DataFrame(inventory)
df_inv.to_csv(f"{DATA_DIR}/silo_warehouse.csv", index=False)
print(f"✅ Generated Warehouse Inventory.")

# --- 4. GENERATE WEB LOGS (The "Silo C" - JSON Format) ---
web_logs = []
actions = ['view_product', 'add_to_cart', 'checkout', 'login']

for _ in range(300):
    web_logs.append({
        "session_id": fake.uuid4(),
        "user_id": f"C{random.randint(1, NUM_CUSTOMERS):03d}",
        "action": random.choice(actions),
        "product_id": f"P{random.randint(1, NUM_PRODUCTS):03d}",
        "timestamp": str(fake.date_time_between(start_date="-7d", end_date="now")),
        "device": random.choice(['Android', 'iOS', 'Desktop'])
    })

with open(f"{DATA_DIR}/silo_web_logs.json", "w") as f:
    json.dump(web_logs, f, indent=4)
print(f"✅ Generated Web Logs (JSON).")

print("\n🎉 MISSION COMPLETE: Data Silos Created in 'data/' folder.")