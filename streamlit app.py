import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from collections import Counter

# Page config
st.set_page_config(page_title="Crypto PnL & Volatility Tracker", layout="wide")

# Title
st.title("🚀 Crypto PnL & Volatility Tracker")

# Sidebar for instructions
st.sidebar.header("How to Use")
st.sidebar.info("""
1. Upload CSV with columns: `date` (YYYY-MM-DD), `symbol`, `entry_price`, `exit_price`, `quantity`
2. Or add trades manually below
3. View metrics, equity curve, and volatility plot
""")
