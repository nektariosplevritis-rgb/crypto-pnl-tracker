# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="Crypto PnL & Volatility Tracker",
    page_icon="Chart increasing",
    layout="wide"
)

st.title("Crypto PnL & Volatility Tracker")
st.markdown("Upload your trades CSV → get instant performance metrics and volatility analysis")

# --------------------------------------------------
# CSV Upload
# --------------------------------------------------
st.sidebar.header("Instructions")
st.sidebar.markdown("""
- CSV must have columns: `date`, `symbol`, `entry_price`, `exit_price`, `quantity`  
- Date format: YYYY-MM-DD  
- Example row: `2025-01-15,BTC,62000,64500,0.15`
""")

uploaded_file = st.file_uploader("Upload your trades (CSV)", type=["csv"])

if uploaded_file is None:
    st.info("Upload a CSV file to see your PnL, equity curve and volatility")
    st.stop()

# --------------------------------------------------
# Load & clean data
# --------------------------------------------------
try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Error reading CSV: {e}")
    st.stop()

required_cols = ["date", "symbol", "entry_price", "exit_price", "quantity"]
if not all(col in df.columns for col in required_cols):
    st.error(f"Missing columns. Required: {required_cols}")
    st.stop()

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

# --------------------------------------------------
# Calculations
# --------------------------------------------------
df["pnl"] = (df["exit_price"] - df["entry_price"]) * df["quantity"]
df["cumulative_pnl"] = df["pnl"].cumsum()
df["win"] = df["pnl"] > 0

total_pnl = df["pnl"].sum()
win_rate = df["win"].mean() * 100
num_trades = len(df)
total_volume = (df["entry_price"] * df["quantity"]).sum()

# Rolling 30-day volatility (annualized)
df["daily_return"] = df["pnl"] / (df["entry_price"] * df["quantity"])
rolling_vol = df["daily_return"].rolling(window=30, min_periods=1).std() * np.sqrt(365) * 100

# Max drawdown
peak = df["cumulative_pnl"].cummax()
drawdown = df["cumulative_pnl"] - peak
max_drawdown = drawdown.min()

# --------------------------------------------------
# Display metrics
# --------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total PnL", f"${total_pnl:,.2f}")
with col2:
    st.metric("Win Rate", f"{win_rate:.1f}%")
with col3:
    st.metric("Total Trades", num_trades)
with col4:
    st.metric("Max Drawdown", f"${max_drawdown:,.2f}")
with col5:
    st.metric("Current 30d Vol", f"{rolling_vol.iloc[-1]:.1f}%" if not rolling_vol.empty else "N/A")

# --------------------------------------------------
# Charts
# --------------------------------------------------
st.subheader("Equity Curve")
fig_eq = px.line(df, x="date", y="cumulative_pnl", title="Cumulative PnL")
fig_eq.update_layout(yaxis_title="Cumulative PnL ($)", xaxis_title="Date")
st.plotly_chart(fig_eq, use_container_width=True)

st.subheader("Rolling 30-Day Volatility (Annualized)")
fig_vol = go.Figure()
fig_vol.add_trace(go.Scatter(x=df["date"], y=rolling_vol, mode='lines', name='30d Vol %'))
fig_vol.update_layout(title="Rolling Volatility", yaxis_title="Annualized Volatility (%)")
st.plotly_chart(fig_vol, use_container_width=True)

# --------------------------------------------------
# Raw table
# --------------------------------------------------
st.subheader("Trade History")
df_display = df.copy()
df_display["date"] = df_display["date"].dt.strftime("%Y-%m-%d")
st.dataframe(df_display, use_container_width=True)

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown("---")
st.caption("Built by Nektarios Plevritis – Junior Quant Dev | Open for remote crypto/fintech roles")
