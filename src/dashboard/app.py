import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Retail Setu Command Center",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem; 
            padding-bottom: 0rem;
        }
        [data-testid="stMetricValue"] {
            font-size: 26px;
            font-weight: bold;
            color: #00CC96;
        }
        /* Floating Control Deck Styling */
        div.css-1r6slb0.e1tzin5v2 {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        }
        /* Button Styling */
        div.stButton > button:first-child {
            background-color: #00CC96; 
            color: white;
            border-radius: 20px;
            border: none;
        }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False

# --- LOAD DATA (CRASH-PROOF VERSION) ---
DATA_DIR = "data"

def load_data():
    try:
        # 1. Gold Data (Forecast & Sales) - Safe Load
        if os.path.exists(f"{DATA_DIR}/gold_sales_forecast.csv"):
            try:
                daily_sales = pd.read_csv(f"{DATA_DIR}/gold_sales_forecast.csv")
            except pd.errors.EmptyDataError:
                daily_sales = None
        else:
            if os.path.exists(f"{DATA_DIR}/gold_daily_sales.csv"):
                try:
                    daily_sales = pd.read_csv(f"{DATA_DIR}/gold_daily_sales.csv")
                    if 'Type' not in daily_sales.columns: daily_sales['Type'] = 'Historical'
                except pd.errors.EmptyDataError:
                    daily_sales = None
            else:
                daily_sales = None

        # 2. Other Gold Files - Safe Load
        try:
            top_products = pd.read_csv(f"{DATA_DIR}/gold_top_products.csv")
        except (FileNotFoundError, pd.errors.EmptyDataError):
            top_products = pd.DataFrame()

        try:
            inventory = pd.read_csv(f"{DATA_DIR}/gold_inventory_health.csv")
        except (FileNotFoundError, pd.errors.EmptyDataError):
            inventory = pd.DataFrame()
        
        # 3. Raw Transactions (Live Feed) - CRASH FIX HERE
        try:
            recent_txns = pd.read_csv(f"{DATA_DIR}/silver_pos_transactions.csv")
            # Check if file has data before sorting
            if not recent_txns.empty:
                recent_txns = recent_txns.tail(8).sort_values(by='timestamp', ascending=False)
            else:
                recent_txns = pd.DataFrame()
        except (FileNotFoundError, pd.errors.EmptyDataError):
            recent_txns = pd.DataFrame() 
        
        # 4. Customer History (SCD)
        try:
            customer_history = pd.read_csv(f"{DATA_DIR}/dim_customers_scd2.csv")
        except (FileNotFoundError, pd.errors.EmptyDataError):
            customer_history = None

        return daily_sales, top_products, inventory, recent_txns, customer_history

    except Exception as e:
        return None, None, None, None, None

df_sales, df_top_products, df_inventory, df_recent, df_customers = load_data()

# --- 🛰️ FLOATING HEADER LAYOUT ---
c_title, c_spacer, c_controls = st.columns([3, 1, 1.5])

with c_title:
    st.title("🌉 Retail Setu AI")
    st.caption(f"🚀 Supply Chain Command Center | System Time: {datetime.now().strftime('%H:%M:%S')}")

with c_controls:
    with st.container(border=True):
        c_toggle, c_status = st.columns([1.5, 1])
        with c_toggle:
            st.write("") # <--- SPACER TO PUSH BUTTON DOWN
            st.write("**Live Data Feed**")
            st.session_state.auto_refresh = st.toggle("Connect", value=st.session_state.auto_refresh)
        with c_status:
            st.write("") # <--- SPACER TO ALIGN TEXT
            if st.session_state.auto_refresh:
                st.success("ONLINE")
            else:
                st.warning("PAUSED")

st.markdown("---")

# --- MAIN DASHBOARD ---
if df_sales is not None and not df_sales.empty:
    # --- 1. METRICS ROW ---
    df_history = df_sales[df_sales.get('Type', 'Historical') == 'Historical']
    total_rev = df_history['Total_Revenue'].sum()
    avg_daily = df_history['Total_Revenue'].mean()
    
    # Safety check for inventory
    if not df_inventory.empty:
        critical_items = len(df_inventory[df_inventory['status'] == 'CRITICAL'])
    else:
        critical_items = 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 Total Revenue", f"₹{total_rev:,.0f}", delta="▲ Live Updates")
    m2.metric("📦 Avg. Daily Sales", f"₹{avg_daily:,.0f}")
    m3.metric("🚨 Critical Stock", f"{critical_items} SKUs", delta="-URGENT", delta_color="inverse")
    m4.metric("🤖 AI Model", "Active", delta="v2.1")

    # --- 2. AI EXECUTIVE SUMMARY ---
    with st.expander("🧠 View AI Executive Summary (Analysis)", expanded=True):
        if critical_items > 5:
            st.error(f"**CRITICAL ALERT:** {critical_items} products below safety threshold. Recommended Action: Initiate emergency restocking.", icon="🤖")
        elif critical_items > 0:
            st.warning(f"**WARNING:** {critical_items} products are running low. Supply chain velocity is stable otherwise.", icon="🤖")
        else:
            st.success("**OPTIMAL:** Supply chain efficiency at 98%. No bottlenecks detected.", icon="🤖")

    # --- 3. CHARTS ROW ---
    c1, c2 = st.columns([2, 1]) 
    with c1:
        st.subheader("📈 Revenue Trends & AI Forecast")
        if 'Type' in df_sales.columns and df_sales['Type'].nunique() > 1:
            color_map = {'Historical': '#1f77b4', 'Forecast': '#ff7f0e'} 
            fig_sales = px.line(df_sales, x='Date', y='Total_Revenue', color='Type', color_discrete_map=color_map, markers=True)
            fig_sales.update_layout(legend=dict(orientation="h", y=1.1, x=0))
        else:
            fig_sales = px.area(df_sales, x='Date', y='Total_Revenue', color_discrete_sequence=["#00CC96"])
        st.plotly_chart(fig_sales, use_container_width=True)

    with c2:
        st.subheader("📦 Inventory Risks")
        if not df_inventory.empty:
            st.dataframe(
                df_inventory[['product_name', 'stock_level', 'status']], 
                use_container_width=True, 
                height=300,
                column_config={
                     "status": st.column_config.TextColumn("Risk", help="AI Risk Level"),
                     "stock_level": st.column_config.ProgressColumn("Stock", format="%d", min_value=0, max_value=200)
                }
            )
        else:
            st.info("Inventory data initializing...")

    st.divider()

    # --- 4. TABS: LIVE FEED & SCD ---
    tab_live, tab_scd = st.tabs(["⚡ Live Transaction Feed", "🕰️ Customer History (SCD Type 2)"])
    
    with tab_live:
        if not df_recent.empty:
            st.dataframe(
                df_recent[['transaction_id', 'timestamp', 'product_id', 'total_amount', 'payment_mode']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "total_amount": st.column_config.NumberColumn("Amount", format="₹%.2f"),
                    "timestamp": st.column_config.DatetimeColumn("Time", format="h:mm:ss a")
                }
            )
        else:
            st.write("Waiting for first transaction...")

    with tab_scd:
        st.markdown("**Feature Demonstration:** Slowly Changing Dimension (Type 2) for tracking customer movements.")
        if df_customers is not None and not df_customers.empty:
            st.dataframe(df_customers, use_container_width=True)
        else:
            st.info("Waiting for customer updates to generate history...")

else:
    st.info("🚀 System initializing... Please wait for the pipeline to generate data.")

# --- AUTO-REFRESH LOGIC ---
if st.session_state.auto_refresh:
    time.sleep(3)
    st.rerun()