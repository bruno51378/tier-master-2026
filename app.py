import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. THE COMPLETE MASTER DATABASE
portfolio = {
    "Ticker": ["NVDA", "MSFT", "AMZN", "SOFI", "HOOD", "ANET", "META", "PLTR", "TSM", "AAPL", "V", "MU", "VRT", "CRWD", "CLS", "HWM", "CDNS", "ARM", "CVX", "AMD", "UAL", "FTNT", "WDC", "EXPE", "RKLB", "LMT", "JPM", "FANG", "IREN", "ORCL", "PINS", "BAC", "CELH", "HIMS", "MRK", "WMT", "MSTR", "LRCX", "STX", "PANW", "CMG", "PGR"],
    "Tier": ["S", "S", "A", "B+", "A", "S", "S", "S", "S", "A", "S", "S", "S", "S", "S", "S", "S", "A", "B", "A", "A", "A", "S", "A", "B", "B", "S", "S", "B+", "B", "C", "B", "B", "B", "A", "A", "F", "S", "S", "S", "A", "A"],
    "Strike": [175.0, 395.0, 195.0, 18.5, 70.0, 145.0, 630.0, 125.0, 345.0, 250.0, 315.0, 380.0, 210.0, 385.0, 265.0, 230.0, 275.0, 112.0, 172.0, 195.0, 98.0, 74.0, 265.0, 212.0, 62.0, 625.0, 295.0, 165.0, 38.0, 145.0, 14.5, 48.5, 41.0, 14.5, 112.0, 118.0, 75.0, 215.0, 385.0, 142.0, 32.0, 198.0],
    "Exit": [265.0, 510.0, 285.0, 32.0, 115.0, 185.0, 800.0, 255.0, 475.0, 306.0, 405.0, 523.0, 310.0, 555.0, 355.0, 320.0, 395.0, 160.0, 215.0, 267.0, 145.0, 115.0, 340.0, 315.0, 95.0, 710.0, 365.0, 215.0, 75.0, 210.0, 30.0, 65.0, 68.0, 38.0, 143.0, 147.0, 400.0, 325.0, 550.0, 225.0, 55.0, 285.0]
}
df_master = pd.DataFrame(portfolio)

# 2. APP LAYOUT & SEARCHABLE WATCHLIST
st.set_page_config(page_title="Tier Master 2026", layout="wide")
st.sidebar.title("🔍 Controls")

# The Search Box: Pre-loaded with S-Tier favorites, but searchable for any ticker
watchlist = st.sidebar.multiselect(
    "Edit Watchlist / Search Tickers:",
    options=df_master["Ticker"].tolist(),
    default=["NVDA", "MSFT", "META", "SOFI"] 
)

# Option to add a brand new ticker not in the database
custom_ticker = st.sidebar.text_input("Search a NEW ticker (e.g. TSLA):").upper()
if custom_ticker and custom_ticker not in watchlist:
    watchlist.append(custom_ticker)

st.title("📈 Tier Master: Live Watchlist")

# 3. DISPLAY LOOP
for ticker in watchlist:
    try:
        # Get data from master list if available, otherwise default to "New Search"
        if ticker in df_master["Ticker"].values:
            tier = df_master[df_master["Ticker"] == ticker]["Tier"].iloc[0]
            strike = df_master[df_master["Ticker"] == ticker]["Strike"].iloc[0]
            exit_p = df_master[df_master["Ticker"] == ticker]["Exit"].iloc[0]
        else:
            tier, strike, exit_p = "New Search", 0.0, 0.0

        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")['Close'].iloc[-1]
        signal = "🟢 BUY" if price <= strike and strike > 0 else "🟡 WAIT"
        
        with st.expander(f"**{ticker}** | Price: ${price:.2f} | {signal}"):
            st.write(f"Tier: **{tier}** | Strike: **${strike}** | Exit: **${exit_p}**")
            # Pull news
            news = stock.news[:2]
            for n in news:
                st.markdown(f"* [{n['title']}]({n['link']})")
                
    except:
        st.error(f"Error loading {ticker}")
