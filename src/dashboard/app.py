import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Retail Setu Command Center",
    page_icon="🌉",
    layout="wide"
)

DATA_DIR = "data"

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False

# --------------------------------------------------
# SAFE LOAD FUNCTION
# --------------------------------------------------
def safe_load(path):
    try:
        return pd.read_csv(path)
    except:
        return pd.DataFrame()

# --------------------------------------------------
# LOAD ALL DATA
# --------------------------------------------------
df_daily = safe_load(f"{DATA_DIR}/gold_daily_sales.csv")
df_forecast = safe_load(f"{DATA_DIR}/gold_sales_forecast.csv")
df_monthly = safe_load(f"{DATA_DIR}/gold_monthly_sales.csv")
df_top = safe_load(f"{DATA_DIR}/gold_top_products.csv")
df_inventory = safe_load(f"{DATA_DIR}/gold_inventory_health.csv")
df_turnover = safe_load(f"{DATA_DIR}/gold_inventory_turnover.csv")
df_seasonal = safe_load(f"{DATA_DIR}/gold_seasonal_trend.csv")
df_customer_metrics = safe_load(f"{DATA_DIR}/gold_customer_metrics.csv")
df_basket = safe_load(f"{DATA_DIR}/gold_market_basket.csv")
df_recent = safe_load(f"{DATA_DIR}/silver_pos_transactions.csv")
df_customers = safe_load(f"{DATA_DIR}/dim_customers_scd2.csv")

# --------------------------------------------------
# HEADER
# --------------------------------------------------
col1, col2 = st.columns([3,1])
with col1:
    st.title("🌉 Retail Setu AI Command Center")
    st.caption(f"Supply Chain Intelligence | {datetime.now().strftime('%H:%M:%S')}")

with col2:
    st.session_state.auto_refresh = st.toggle("🔄 Live Mode", value=st.session_state.auto_refresh)

# --------------------------------------------------
# AUTO REFRESH (Stable Version)
# --------------------------------------------------
if st.session_state.auto_refresh:
    st_autorefresh(interval=3000, key="datarefresh")

st.markdown("---")

# --------------------------------------------------
# KPI METRICS
# --------------------------------------------------
if not df_daily.empty:

    total_rev = df_daily["Total_Revenue"].sum()
    avg_daily = df_daily["Total_Revenue"].mean()
    critical = len(df_inventory[df_inventory["status"] == "CRITICAL"]) if not df_inventory.empty else 0

    m1, m2, m3 = st.columns(3)
    m1.metric("💰 Total Revenue", f"₹{total_rev:,.0f}")
    m2.metric("📈 Avg Daily Revenue", f"₹{avg_daily:,.0f}")
    m3.metric("🚨 Critical Stock Items", critical)

st.markdown("---")

# --------------------------------------------------
# REVENUE + AI FORECAST
# --------------------------------------------------
st.subheader("📊 Revenue & AI Forecast")

if not df_daily.empty:

    df_daily["Date"] = pd.to_datetime(df_daily["Date"])
    df_daily = df_daily.sort_values("Date")

    fig = px.line(
        df_daily,
        x="Date",
        y="Total_Revenue",
        title="Historical Revenue"
    )

    if not df_forecast.empty and "Date" in df_forecast.columns:

        df_forecast["Date"] = pd.to_datetime(df_forecast["Date"])
        df_forecast = df_forecast.sort_values("Date")

        forecast_col = None
        for col in df_forecast.columns:
            if "revenue" in col.lower():
                forecast_col = col
                break

        if forecast_col:
            fig.add_scatter(
                x=df_forecast["Date"],
                y=df_forecast[forecast_col],
                mode="lines+markers",
                name="Forecast",
                line=dict(dash="dash")
            )

    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# ADVANCED ANALYTICS TABS
# --------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📈 Commercial", "🚚 Operations", "👤 Customer"])

# ------------------ COMMERCIAL ------------------
with tab1:

    col1, col2 = st.columns(2)

    with col1:
        if not df_monthly.empty:
            fig_m = px.bar(df_monthly, x="month", y=df_monthly.columns[-1], title="Monthly Revenue")
            st.plotly_chart(fig_m, use_container_width=True)

    with col2:
        if not df_top.empty:
            fig_top = px.bar(df_top.head(10), x="product_name", y="quantity", title="Top Products")
            st.plotly_chart(fig_top, use_container_width=True)

# ------------------ OPERATIONS ------------------
with tab2:

    if not df_turnover.empty:
        st.metric("Inventory Turnover Ratio", f"{df_turnover['value'].iloc[0]:.2f}")

    if not df_seasonal.empty:
        fig_s = px.line(df_seasonal, x="Month", y="Total_Quantity_Sold", title="Seasonal Demand Trend")
        st.plotly_chart(fig_s, use_container_width=True)

    if not df_inventory.empty:
        st.subheader("Inventory Health")
        st.dataframe(df_inventory.head(10), use_container_width=True)

# ------------------ CUSTOMER ------------------
with tab3:

    if not df_customer_metrics.empty:

        col1, col2 = st.columns(2)

        with col1:
            counts = df_customer_metrics["customer_type"].value_counts().reset_index()
            counts.columns = ["Type", "Count"]
            fig_pie = px.pie(counts, names="Type", values="Count", title="New vs Returning")
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            top_clv = df_customer_metrics.sort_values("total_spent", ascending=False).head(10)
            fig_clv = px.bar(top_clv, x="customer_id", y="total_spent", title="Top CLV Customers")
            st.plotly_chart(fig_clv, use_container_width=True)

    if not df_basket.empty:
        st.subheader("Market Basket Insights")
        st.dataframe(df_basket.head(10), use_container_width=True)

st.markdown("---")

# --------------------------------------------------
# LIVE TRANSACTIONS & SCD
# --------------------------------------------------
tab_live, tab_scd = st.tabs(["⚡ Live Transactions", "🕰️ Customer History (SCD2)"])

with tab_live:
    if not df_recent.empty:
        st.dataframe(df_recent.tail(10), use_container_width=True)
    else:
        st.info("Waiting for transactions...")

with tab_scd:
    if not df_customers.empty:
        st.dataframe(df_customers, use_container_width=True)
    else:
        st.info("No customer history yet.")
