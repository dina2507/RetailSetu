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
    initial_sidebar_state="collapsed" # Sidebar is gone!
)

# --- CUSTOM CSS (THE FUTURISTIC LOOK) ---
st.markdown("""
    <style>
        /* Remove top padding to make header look like a nav bar */
        .block-container {
            padding-top: 1rem; 
            padding-bottom: 0rem;
        }
        /* Style metrics */
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

# --- LOAD DATA ---
DATA_DIR = "data"

def load_data():
    try:
        # 1. Gold Data
        if os.path.exists(f"{DATA_DIR}/gold_sales_forecast.csv"):
            daily_sales = pd.read_csv(f"{DATA_DIR}/gold_sales_forecast.csv")
        else:
            daily_sales = pd.read_csv(f"{DATA_DIR}/gold_daily_sales.csv")
            if 'Type' not in daily_sales.columns: daily_sales['Type'] = 'Historical'

        top_products = pd.read_csv(f"{DATA_DIR}/gold_top_products.csv")
        inventory = pd.read_csv(f"{DATA_DIR}/gold_inventory_health.csv")
        
        # 2. Raw Transactions (Last 8 rows)
        recent_txns = pd.read_csv(f"{DATA_DIR}/silver_pos_transactions.csv").tail(8).sort_values(by='timestamp', ascending=False)
        
        return daily_sales, top_products, inventory, recent_txns
    except FileNotFoundError:
        return None, None, None, None

df_sales, df_top_products, df_inventory, df_recent = load_data()

# --- 🛰️ FLOATING HEADER LAYOUT ---
# We use columns to create a "Navbar" feel
c_title, c_spacer, c_controls = st.columns([3, 1, 1.5])

with c_title:
    st.title("🌉 Retail Setu AI")
    st.caption(f"🚀 Supply Chain Command Center | System Time: {datetime.now().strftime('%H:%M:%S')}")

with c_controls:
    # This is the "Floating Window" effect - a styled container at the top right
    with st.container(border=True):
        c_toggle, c_status = st.columns([1.5, 1])
        with c_toggle:
            st.write("**Live Data Feed**")
            st.session_state.auto_refresh = st.toggle("Connect", value=st.session_state.auto_refresh)
        with c_status:
            if st.session_state.auto_refresh:
                st.success("ONLINE")
            else:
                st.warning("PAUSED")

st.markdown("---")

# --- MAIN DASHBOARD ---
if df_sales is not None:
    # --- 1. METRICS ROW ---
    df_history = df_sales[df_sales.get('Type', 'Historical') == 'Historical']
    total_rev = df_history['Total_Revenue'].sum()
    avg_daily = df_history['Total_Revenue'].mean()
    critical_items = len(df_inventory[df_inventory['status'] == 'CRITICAL'])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 Total Revenue", f"₹{total_rev:,.0f}", delta="▲ Live Updates")
    m2.metric("📦 Avg. Daily Sales", f"₹{avg_daily:,.0f}")
    m3.metric("🚨 Critical Stock", f"{critical_items} SKUs", delta="-URGENT", delta_color="inverse")
    m4.metric("🤖 AI Model", "Active", delta="v2.1")

    # --- 2. LIVE FEED (Visual Proof) ---
    with st.expander("⚡ View Live Transaction Stream (Real-Time)", expanded=False):
        st.dataframe(
            df_recent[['transaction_id', 'timestamp', 'product_id', 'total_amount', 'payment_mode']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "total_amount": st.column_config.NumberColumn("Amount", format="₹%.2f"),
                "timestamp": st.column_config.DatetimeColumn("Time", format="h:mm:ss a")
            }
        )

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
    st.info("🚀 System initializing... Please wait for the pipeline to generate data.")

# --- AUTO-REFRESH LOGIC ---
if st.session_state.auto_refresh:
    time.sleep(3)
    st.rerun()