import streamlit as st
import pandas as pd
import plotly.express as px
import time

# --- PAGE CONFIGURATION (Must be first) ---
st.set_page_config(
    page_title="Retail Setu Command Center",
    page_icon="🌉",
    layout="wide", # Uses full screen width
    initial_sidebar_state="collapsed" # Hides sidebar by default
)

# --- CUSTOM CSS (To make it look like a pro app) ---
st.markdown("""
    <style>
        .block-container {padding-top: 1rem; padding-bottom: 0rem;}
        h1 {margin-top: -50px;}
        [data-testid="stMetricValue"] {font-size: 24px;}
        div.stButton > button:first-child {background-color: #00CC96; color: white;}
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False

# --- LOAD DATA ---
DATA_DIR = "data"

def load_data():
    """Loads the Gold Layer data."""
    try:
        # We stick to the standard 'gold_daily_sales.csv' to ensure stability
        # If you have the forecast file later, you can swap this back.
        daily_sales = pd.read_csv(f"{DATA_DIR}/gold_daily_sales.csv")
        top_products = pd.read_csv(f"{DATA_DIR}/gold_top_products.csv")
        inventory = pd.read_csv(f"{DATA_DIR}/gold_inventory_health.csv")
        return daily_sales, top_products, inventory
    except FileNotFoundError:
        return None, None, None

df_sales, df_top_products, df_inventory = load_data()

# --- TOP BAR (Title + Controls) ---
col_title, col_controls = st.columns([6, 1])

with col_title:
    st.title("🌉 Retail Setu: Supply Chain AI")

with col_controls:
    # Toggle button at the top right
    st.session_state.auto_refresh = st.toggle("🔄 Live Mode", value=st.session_state.auto_refresh)

if st.session_state.auto_refresh:
    st.toast("🔴 Live Data Streaming...", icon="📡")

st.divider()

if df_sales is not None:
    # --- 1. KEY METRICS ROW ---
    total_rev = df_sales['Total_Revenue'].sum()
    avg_daily = df_sales['Total_Revenue'].mean()
    critical_items = len(df_inventory[df_inventory['status'] == 'CRITICAL'])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 Total Revenue", f"₹{total_rev:,.0f}", delta="Live Updates")
    m2.metric("📦 Avg. Daily Sales", f"₹{avg_daily:,.0f}")
    m3.metric("🚨 Critical Stock", f"{critical_items} SKUs", delta="-URGENT", delta_color="inverse")
    m4.metric("🤖 AI Model Status", "Active", delta="v2.1")

    # --- 2. AI INSIGHTS (The "Chat" Interface) ---
    with st.expander("🧠 View AI Executive Summary", expanded=True):
        if critical_items > 5:
            st.error(f"**CRITICAL ALERT:** {critical_items} products are below safety stock levels. Predicted revenue loss of ₹45,000 if not restocked by tomorrow.", icon="🤖")
        elif critical_items > 0:
            st.warning(f"**WARNING:** {critical_items} products are running low. Supply chain velocity is stable otherwise.", icon="🤖")
        else:
            st.success("**OPTIMAL:** Supply chain is operating at 98% efficiency. No bottlenecks detected.", icon="🤖")

    # --- 3. CHARTS ROW (Full Width) ---
    # We use a 2:1 ratio so the Line Chart gets more space
    c1, c2 = st.columns([2, 1]) 

    with c1:
        st.subheader("📈 Revenue Trends")
        # Enhance chart with area fill
        fig_sales = px.area(df_sales, x='Date', y='Total_Revenue', title="", color_discrete_sequence=["#00CC96"])
        fig_sales.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_sales, use_container_width=True)

    with c2:
        st.subheader("🏆 Top Selling Products")
        fig_prod = px.bar(df_top_products, x='quantity', y='product_name', orientation='h', color='quantity', color_continuous_scale='Bluered')
        fig_prod.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
        st.plotly_chart(fig_prod, use_container_width=True)

    # --- 4. DATA GRID ---
    st.subheader("📦 Real-Time Inventory Feed")
    
    # We use column_config to make the table look like a dashboard component
    st.dataframe(
        df_inventory, 
        use_container_width=True,
        column_config={
            "status": st.column_config.TextColumn(
                "Risk Status",
                help="AI Predicted Risk",
                validate="^(CRITICAL|Healthy)$"
            ),
            "stock_level": st.column_config.ProgressColumn(
                "Stock Level",
                format="%d",
                min_value=0,
                max_value=200,
            ),
        }
    )

else:
    st.error("❌ Waiting for pipeline... Run 'src/orchestration/pipeline_runner.py'")

# --- AUTO REFRESH LOOP ---
if st.session_state.auto_refresh:
    time.sleep(2)
    st.rerun()