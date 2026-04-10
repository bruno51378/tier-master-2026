import streamlit as st
import yfinance as yf
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

# 1. LIVE REFRESH (Every 30 seconds)
st_autorefresh(interval=30000, key="price_refresh")

# 2. MASTER VETTED DATABASE
vetted_data = {
    "Ticker": ["PLTR", "SHOP", "CRWD", "CDNS", "PANW", "MCO", "ANET", "MSFT", "CLS", "WDC", "MU", "V", "TSM", "MA", "LLY", "NVDA", "JPM", "AVGO", "STX", "HWM", "VRT", "META", "LRCX", "ARM", "HOOD", "AMD", "UAL", "FTNT", "AMZN", "UBER", "AAPL", "WMT", "GOOGL", "CMG", "PGR", "FANG", "VST", "SOFI", "ORCL", "CVX"],
    "Tier": ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S", "S", "S", "S", "S", "S", "S", "S", "S", "S", "S", "S", "S", "S", "A", "A", "A", "A", "A", "A", "A", "A", "A", "A", "A", "A", "A", "A", "B+", "B", "B"],
    "Strike": [125.0, 105.0, 385.0, 275.0, 142.0, 405.0, 145.0, 395.0, 265.0, 265.0, 380.0, 315.0, 345.0, 520.0, 950.0, 175.0, 295.0, 310.0, 385.0, 230.0, 210.0, 630.0, 215.0, 112.0, 70.0, 195.0, 98.0, 74.0, 195.0, 68.0, 250.0, 118.0, 295.0, 32.0, 198.0, 172.0, 150.0, 18.5, 145.0, 172.0],
    "Exit": [255.0, 165.0, 555.0, 395.0, 225.0, 550.0, 185.0, 510.0, 355.0, 340.0, 523.0, 405.0, 475.0, 605.0, 1200.0, 265.0, 365.0, 455.0, 550.0, 320.0, 310.0, 800.0, 325.0, 160.0, 115.0, 267.0, 145.0, 115.0, 285.0, 105.0, 306.0, 147.0, 410.0, 55.0, 285.0, 215.0, 220.0, 32.0, 210.0, 215.0]
}
df_master = pd.DataFrame(vetted_data)

# 3. ANALYST ENGINE (4-Stat Logic)
def auto_analyze(ticker):
    try:
        stock = yf.Ticker(ticker)
        inf = stock.info
        # Criteria: Growth, Profit, FCF, and Efficiency
        growth = inf.get('revenueGrowth', 0) * 100
        margin = inf.get('profitMargins', 0) * 100
        fcf = (inf.get('freeCashflow', 0) / inf.get('totalRevenue', 1)) * 100
        roa = inf.get('returnOnAssets', 0) * 100 # Proxy for CROCI
        
        # Tier logic
        score = sum([growth > 20, margin > 15, fcf > 15, roa > 10])
        tier = "S" if score >= 3 else "A" if score >= 2 else "B"
        
        curr = inf.get('currentPrice', 0)
        return {"tier": tier, "strike": round(curr * 0.85, 2), "exit": round(curr * 1.3, 2), "stats": f"Growth: {growth:.1f}% | FCF: {fcf:.1f}%"}
    except: return None

# 4. APP INTERFACE
st.set_page_config(page_title="Tier Master 2026", layout="wide")
st.sidebar.header("🔍 Watchlist")
watchlist = st.sidebar.multiselect("Select Tickers:", options=df_master["Ticker"].tolist(), default=["NVDA", "MSFT", "SOFI"])

search = st.sidebar.text_input("Analyze New Ticker:").upper()
if search and search not in watchlist: watchlist.append(search)

st.title("📈 Tier Master: Live Strategy Dashboard")
st.caption(f"Prices auto-update every 30s. Last update: {time.strftime('%H:%M:%S')}")

# 5. EXECUTION & SORTING
active_list = []
for t in watchlist:
    stock = yf.Ticker(t)
    price = stock.history(period="1d")['Close'].iloc[-1]
    
    if t in df_master["Ticker"].values:
        row = df_master[df_master["Ticker"] == t].iloc[0]
        data = {"tier": row['Tier'], "strike": row['Strike'], "exit": row['Exit'], "stats": "Vetted"}
    else:
        data = auto_analyze(t)

    if data:
        signal = "🟢 BUY" if price <= data['strike'] else "🟡 WAIT"
        active_list.append({**data, "ticker": t, "price": price, "signal": signal, "sort": 0 if signal == "🟢 BUY" else 1})

# SORT & DISPLAY
for item in sorted(active_list, key=lambda x: x['sort']):
    with st.expander(f"**{item['signal']}** | {item['ticker']} | ${item['price']:.2f} (Strike: ${item['strike']})"):
        st.write(f"**Tier:** {item['tier']} | **Target Exit:** ${item['exit']}")
        st.caption(item['stats'])
