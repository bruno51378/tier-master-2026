import streamlit as st
import yfinance as yf
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

# 1. AUTO-REFRESH (Every 30 seconds)
st_autorefresh(interval=30000, key="datarefresh")

# 2. DATABASE
portfolio = {
    "Ticker": ["NVDA", "MSFT", "AMZN", "SOFI", "HOOD", "ANET", "META", "PLTR", "TSM", "AAPL", "V", "MU", "VRT", "CRWD", "CLS", "HWM", "CDNS", "ARM", "CVX", "AMD", "UAL", "FTNT", "WDC", "EXPE", "RKLB", "LMT", "JPM", "FANG", "IREN", "ORCL", "PINS", "BAC", "CELH", "HIMS", "MRK", "WMT", "MSTR", "LRCX", "STX", "PANW", "CMG", "PGR"],
    "Tier": ["S", "S", "A", "B+", "A", "S", "S", "S", "S", "A", "S", "S", "S", "S", "S", "S", "S", "A", "B", "A", "A", "A", "S", "A", "B", "B", "S", "S", "B+", "B", "C", "B", "B", "B", "A", "A", "F", "S", "S", "S", "A", "A"],
    "Strike": [175.00, 395.00, 195.00, 18.50, 70.00, 145.00, 630.00, 125.00, 345.00, 250.00, 315.00, 380.00, 210.00, 385.00, 265.00, 230.00, 275.00, 112.00, 172.00, 195.00, 98.00, 74.00, 265.00, 212.00, 62.00, 625.00, 295.00, 165.00, 38.00, 145.00, 14.50, 48.50, 41.00, 14.50, 112.00, 118.00, 75.00, 215.00, 385.00, 142.00, 32.00, 198.00],
    "Exit": [265.00, 510.00, 285.00, 32.00, 115.00, 185.00, 800.00, 255.00, 475.00, 306.00, 405.00, 523.00, 310.00, 555.00, 355.00, 320.00, 395.00, 160.00, 215.00, 267.00, 145.00, 115.00, 340.00, 315.00, 95.00, 710.00, 365.00, 215.00, 75.00, 210.00, 30.00, 65.00, 68.00, 38.00, 143.00, 147.00, 400.00, 325.00, 550.00, 225.00, 55.00, 285.00]
}
df_master = pd.DataFrame(portfolio)

# 3. APP LAYOUT
st.set_page_config(page_title="Tier Master 2026", page_icon="📈", layout="wide")
st.title("📈 Tier Master: Live Tracker")
st.write(f"Last updated: {time.strftime('%H:%M:%S')}")

# 4. DATA PROCESSING
for i, row in df_master.iterrows():
    try:
        # Using fast_info for "LIVER" price (less delay than history)
        stock = yf.Ticker(row['Ticker'])
        price = stock.fast_info['lastPrice']
        
        signal = "🟢 BUY" if price <= row['Strike'] else "🟡 WAIT"
        color = "green" if signal == "🟢 BUY" else "white"
        
        st.markdown(f"### :{color}[{row['Ticker']}] | **${price:.2f}** | {signal}")
        st.write(f"Target Strike: ${row['Strike']} | Tier: {row['Tier']}")
        st.divider()
            
    except Exception as e:
        st.error(f"Error loading {row['Ticker']}")
