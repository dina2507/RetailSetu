import pandas as pd
import os

# Define Paths
DATA_DIR = "data"
SILVER_POS_PATH = f"{DATA_DIR}/silver_pos_transactions.csv"
SILVER_INV_PATH = f"{DATA_DIR}/silver_warehouse.csv"
DIM_PROD_PATH = f"{DATA_DIR}/dim_products.csv"

# Output Paths (Gold Layer)
GOLD_DAILY_SALES = f"{DATA_DIR}/gold_daily_sales.csv"
GOLD_TOP_PRODUCTS = f"{DATA_DIR}/gold_top_products.csv"
GOLD_INV_HEALTH = f"{DATA_DIR}/gold_inventory_health.csv"

def generate_gold_layer():
    print("STARTING: Silver -> Gold Transformation (KPI Calculation)...")
    
    # Check if files exist
    if not os.path.exists(SILVER_POS_PATH):
        print("ERROR: Silver data not found. Run 'process_silver_layer.py' first.")
        return

    # Load Data
    df_sales = pd.read_csv(SILVER_POS_PATH)
    df_inv = pd.read_csv(SILVER_INV_PATH)
    df_prod = pd.read_csv(DIM_PROD_PATH)

    # Ensure Date format
    df_sales['timestamp'] = pd.to_datetime(df_sales['timestamp'])
    df_sales['date'] = df_sales['timestamp'].dt.date

    # --- KPI 1: Daily Revenue (For Line Chart) ---
    daily_revenue = df_sales.groupby('date')['total_amount'].sum().reset_index()
    daily_revenue.columns = ['Date', 'Total_Revenue']
    daily_revenue.to_csv(GOLD_DAILY_SALES, index=False)
    print(f"💰 Generated Daily Revenue KPI: {GOLD_DAILY_SALES}")

    # --- KPI 2: Top Selling Products (For Bar Chart) ---
    top_products = df_sales.groupby('product_id')['quantity'].sum().reset_index()
    # Merge with Product Names so the chart looks nice
    top_products = top_products.merge(df_prod[['product_id', 'product_name']], on='product_id', how='left')
    top_products = top_products.sort_values(by='quantity', ascending=False).head(10)
    top_products.to_csv(GOLD_TOP_PRODUCTS, index=False)
    print(f"🏆 Generated Top Products KPI: {GOLD_TOP_PRODUCTS}")

    # --- KPI 3: Inventory Health (For "Low Stock" Alerts) ---
    # Merge Inventory with Product Info
    inv_health = df_inv.merge(df_prod[['product_id', 'product_name', 'category']], on='product_id', how='left')
    # Flag items with low stock (< 20 units)
    inv_health['status'] = inv_health['stock_level'].apply(lambda x: 'CRITICAL' if x < 20 else 'Healthy')
    inv_health.to_csv(GOLD_INV_HEALTH, index=False)
    print(f"📦 Generated Inventory Health KPI: {GOLD_INV_HEALTH}")

    print("🎉 SUCCESS: Gold Layer (Analytics Ready) Created.")

if __name__ == "__main__":
    generate_gold_layer()