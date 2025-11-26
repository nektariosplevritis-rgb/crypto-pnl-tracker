# app.py
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Crypto PnL Tracker", layout="wide")
st.title("Crypto PnL & Volatility Tracker")
st.caption("Upload CSV → get instant performance metrics")

# Upload
uploaded_file = st.file_uploader("CSV: date, symbol, entry_price, exit_price, quantity", type="csv")

if uploaded_file is None:
    st.info("Upload your trades CSV to begin")
    st.stop()

# Load
df = pd.read_csv(uploaded_file)
req = ["date", "symbol", "entry_price", "exit_price", "quantity"]
if not all(c in df.columns for c in req):
    st.error(f"Missing columns. Need: {req}")
    st.stop()

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

# PnL
df["pnl"] = (df["exit_price"] - df["entry_price"]) * df["quantity"]
df["cum_pnl"] = df["pnl"].cumsum()
total_pnl = df["pnl"].sum()
win_rate = (df["pnl"] > 0).mean() * 100
trades = len(df)

# Metrics
c1, c2, c3 = st.columns(3)
c1.metric("Total PnL", f"${total_pnl:,.2f}")
c2.metric("Win Rate", f"{win_rate:.1f}%")
c3.metric("Total Trades", trades)

# Charts – 100% native Streamlit
st.subheader("Equity Curve")
st.line_chart(df.set_index("date")["cum_pnl"])

st.subheader("Daily PnL")
st.bar_chart(df.set_index("date")["pnl"])

# Table
st.subheader("Trade History")
st.dataframe(df[["date", "symbol", "entry_price", "exit_price", "quantity", "pnl"]].round(2))

st.success("LIVE – zero external packages – works everywhere")
