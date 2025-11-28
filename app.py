# app.py
import streamlit as st
import pandas as pd
import numpy as np

# Page setup
st.set_page_config(page_title="Crypto PnL Tracker", layout="wide")
st.title("Crypto PnL & Volatility Tracker")
st.caption("Upload your CSV trades to see performance metrics")

# --- File Upload ---
uploaded_file = st.file_uploader(
    "CSV: date, symbol, entry_price, exit_price, quantity", type="csv"
)

if uploaded_file is None:
    st.info("Upload a CSV file to get started")
    st.stop()

# --- Load CSV ---
try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Error reading CSV: {e}")
    st.stop()

# Required columns
required_cols = ["date", "symbol", "entry_price", "exit_price", "quantity"]
if not all(col in df.columns for col in required_cols):
    st.error(f"Missing columns. Required: {required_cols}")
    st.stop()

# --- Data Prep ---
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.sort_values("date").reset_index(drop=True)

# --- PnL Calculation ---
pnl_list = []
for idx, row in df.iterrows():
    profit = (row["exit_price"] - row["entry_price"]) * row["quantity"]
    pnl_list.append(profit)

df["pnl"] = pnl_list

# Cumulative profit
cum_profit = []
total = 0
for p in pnl_list:
    total += p
    cum_profit.append(total)
df["cum_profit"] = cum_profit

# Metrics
total_profit = sum(pnl_list)
win_rate = sum(p > 0 for p in pnl_list) / len(pnl_list) * 100
total_trades = len(df)

# --- Display Metrics ---
c1, c2, c3 = st.columns(3)
c1.metric("Total Profit", f"${total_profit:,.2f}")
c2.metric("Win Rate", f"{win_rate:.1f}%")
c3.metric("Total Trades", total_trades)

# --- Charts ---
st.subheader("Equity Curve")
st.line_chart(df.set_index("date")["cum_profit"])

st.subheader("Daily PnL")
st.bar_chart(df.set_index("date")["pnl"])

# --- Trade Table ---
st.subheader("Trade History")
st.dataframe(df[["date", "symbol", "entry_price", "exit_price", "quantity", "pnl"]].round(2))
