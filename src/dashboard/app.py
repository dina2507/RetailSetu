import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Retail Setu Intelligence", page_icon="📊", layout="wide")

# --- INITIALIZE SESSION STATE ---
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False

# --- SIDEBAR AUTO-REFRESH TOGGLE ---
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.session_state.auto_refresh = st.toggle("🔄 Auto-Refresh (Every 2s)", value=st.session_state.auto_refresh)
    
    if st.session_state.auto_refresh:
        st.info("🟢 Auto-Refresh is ON")
    else:
        st.info("🔴 Auto-Refresh is OFF")

# --- LOAD DATA ---
DATA_DIR = "data"

def load_data():
    """Loads the Gold Layer data for the dashboard."""
    try:
        daily_sales = pd.read_csv(f"{DATA_DIR}/gold_daily_sales.csv")
        top_products = pd.read_csv(f"{DATA_DIR}/gold_top_products.csv")
        inventory = pd.read_csv(f"{DATA_DIR}/gold_inventory_health.csv")
        return daily_sales, top_products, inventory
    except FileNotFoundError:
        st.error("❌ Data not found! Please run 'src/transformation/gold_kpi_logic.py' first.")
        return None, None, None

df_sales, df_top_products, df_inventory = load_data()

# --- HEADER ---
st.title("🌉 Retail Setu: Supply Chain Command Center")
st.markdown("### Real-time visibility into Stores, Inventory, and Logistics")
st.divider()

if df_sales is not None:
    # --- KPI METRICS (Top Row) ---
    total_revenue = df_sales['Total_Revenue'].sum()
    avg_daily_sales = df_sales['Total_Revenue'].mean()
    critical_stock_items = len(df_inventory[df_inventory['status'] == 'CRITICAL'])

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Revenue (Last 30 Days)", f"₹{total_revenue:,.2f}")
    col2.metric("📉 Avg. Daily Sales", f"₹{avg_daily_sales:,.2f}")
    col3.metric("🚨 Critical Stock Items", f"{critical_stock_items} SKUs", delta="-High Risk", delta_color="inverse")

    st.divider()

    # --- CHARTS ROW 1 ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📈 Revenue Trend")
        fig_sales = px.line(df_sales, x='Date', y='Total_Revenue', markers=True, title="Daily Sales Performance")
        st.plotly_chart(fig_sales, use_container_width=True)

    with col_right:
        st.subheader("🏆 Top Selling Products")
        fig_prod = px.bar(df_top_products, x='quantity', y='product_name', orientation='h', title="Units Sold", color='quantity')
        st.plotly_chart(fig_prod, use_container_width=True)

    # --- INVENTORY TABLE ---
    st.subheader("📦 Inventory Health Monitor")
    
    # Filter for Critical items
    critical_df = df_inventory[df_inventory['status'] == 'CRITICAL']
    
    tab1, tab2 = st.tabs(["🚨 Critical Alerts (Low Stock)", "✅ Full Inventory"])
    
    with tab1:
        st.dataframe(critical_df.style.applymap(lambda x: 'background-color: #ffcccc', subset=['stock_level']))
    
    with tab2:
        st.dataframe(df_inventory)

else:
    st.warning("Waiting for data pipelines to run...")

# --- AUTO-REFRESH LOGIC (AT END) ---
if st.session_state.auto_refresh:
    time.sleep(2)
    st.rerun()