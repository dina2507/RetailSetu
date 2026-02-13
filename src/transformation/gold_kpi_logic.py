import pandas as pd
import os

# Define Paths
DATA_DIR = "data"
SILVER_POS_PATH = f"{DATA_DIR}/silver_pos_transactions.csv"
SILVER_INV_PATH = f"{DATA_DIR}/silver_warehouse.csv"
DIM_PROD_PATH = f"{DATA_DIR}/dim_products.csv"

# Output Paths (Gold Layer)
GOLD_DAILY_SALES = f"{DATA_DIR}/gold_daily_sales.csv"
GOLD_MONTHLY_SALES = f"{DATA_DIR}/gold_monthly_sales.csv"
GOLD_TOP_PRODUCTS = f"{DATA_DIR}/gold_top_products.csv"
GOLD_INV_HEALTH = f"{DATA_DIR}/gold_inventory_health.csv"
GOLD_CITY_SALES = f"{DATA_DIR}/gold_city_sales.csv"
GOLD_CUSTOMER_METRICS = f"{DATA_DIR}/gold_customer_metrics.csv"
GOLD_MARKET_BASKET = f"{DATA_DIR}/gold_market_basket.csv"


def generate_gold_layer():
    print("STARTING: Silver -> Gold Transformation (KPI Calculation)...")

    if not os.path.exists(SILVER_POS_PATH):
        print("ERROR: Silver POS data not found.")
        return

    df_sales = pd.read_csv(SILVER_POS_PATH)
    df_inv = pd.read_csv(SILVER_INV_PATH)
    df_prod = pd.read_csv(DIM_PROD_PATH)

    df_sales['timestamp'] = pd.to_datetime(df_sales['timestamp'])
    df_sales['date'] = df_sales['timestamp'].dt.date
    df_sales['year'] = df_sales['timestamp'].dt.year
    df_sales['month'] = df_sales['timestamp'].dt.month

    # ------------------------
    # 1️⃣ Daily Revenue
    # ------------------------
    daily_revenue = df_sales.groupby('date')['total_amount'].sum().reset_index()
    daily_revenue.columns = ['Date', 'Total_Revenue']
    daily_revenue.to_csv(GOLD_DAILY_SALES, index=False)

    # ------------------------
    # 2️⃣ Monthly Revenue
    # ------------------------
    monthly_revenue = df_sales.groupby(['year', 'month'])['total_amount'].sum().reset_index()
    monthly_revenue.to_csv(GOLD_MONTHLY_SALES, index=False)

    # ------------------------
    # 3️⃣ Top Products
    # ------------------------
    top_products = df_sales.groupby('product_id')['quantity'].sum().reset_index()
    top_products = top_products.merge(
        df_prod[['product_id', 'product_name']],
        on='product_id',
        how='left'
    )
    top_products = top_products.sort_values(by='quantity', ascending=False)
    top_products.to_csv(GOLD_TOP_PRODUCTS, index=False)

    # ------------------------
    # 4️⃣ City-wise Sales
    # ------------------------
    if 'store_id' in df_sales.columns:
        city_sales = df_sales.groupby('store_id')['total_amount'].sum().reset_index()
        city_sales.to_csv(GOLD_CITY_SALES, index=False)

    # ------------------------
    # 5️⃣ Inventory Health
    # ------------------------
    inv_health = df_inv.merge(
        df_prod[['product_id', 'product_name', 'category']],
        on='product_id',
        how='left'
    )
    inv_health['status'] = inv_health['stock_level'].apply(
        lambda x: 'CRITICAL' if x < 20 else 'Healthy'
    )
    inv_health.to_csv(GOLD_INV_HEALTH, index=False)

    # ------------------------
    # 6️⃣ Customer Metrics (New vs Returning + CLV)
    # ------------------------
    customer_metrics = df_sales.groupby('customer_id').agg(
        total_spent=('total_amount', 'sum'),
        total_orders=('transaction_id', 'nunique')
    ).reset_index()

    customer_metrics['customer_type'] = customer_metrics['total_orders'].apply(
        lambda x: 'Returning' if x > 1 else 'New'
    )

    customer_metrics.to_csv(GOLD_CUSTOMER_METRICS, index=False)

    # ------------------------
    # 7️⃣ Market Basket (Simple Pair Frequency)
    # ------------------------
    basket = df_sales.groupby(['transaction_id'])['product_id'].apply(list)

    pair_counts = {}

    for products in basket:
        unique_products = list(set(products))
        for i in range(len(unique_products)):
            for j in range(i + 1, len(unique_products)):
                pair = tuple(sorted([unique_products[i], unique_products[j]]))
                pair_counts[pair] = pair_counts.get(pair, 0) + 1

    market_basket_df = pd.DataFrame(
        [(k[0], k[1], v) for k, v in pair_counts.items()],
        columns=['product_1', 'product_2', 'frequency']
    )

    market_basket_df = market_basket_df.sort_values(by='frequency', ascending=False)
    market_basket_df.to_csv(GOLD_MARKET_BASKET, index=False)

    print("SUCCESS: Extended Gold KPIs generated.")
    
    # ------------------------
    # 8️⃣ Inventory Turnover Ratio
    # ------------------------
    # Simplified turnover = Total quantity sold / Average stock level

    total_sold = df_sales['quantity'].sum()
    avg_stock = df_inv['stock_level'].mean()

    turnover_ratio = total_sold / avg_stock if avg_stock != 0 else 0

    turnover_df = pd.DataFrame({
        "metric": ["Inventory Turnover Ratio"],
        "value": [turnover_ratio]
    })

    turnover_df.to_csv(f"{DATA_DIR}/gold_inventory_turnover.csv", index=False)
    
    # ------------------------
    # 9️⃣ Seasonal Demand Trend
    # ------------------------
    seasonal_trend = df_sales.groupby('month')['quantity'].sum().reset_index()
    seasonal_trend.columns = ['Month', 'Total_Quantity_Sold']

    seasonal_trend.to_csv(f"{DATA_DIR}/gold_seasonal_trend.csv", index=False)


if __name__ == "__main__":
    generate_gold_layer()
    