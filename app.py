import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. UPDATED CORE ENGINE: Automated Analysis
def analyze_new_ticker(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Pulling your 4-stat criteria
        rev_growth = info.get('revenueGrowth', 0) * 100
        profit_margin = info.get('profitMargins', 0) * 100
        fcf = info.get('freeCashflow', 0)
        revenue = info.get('totalRevenue', 1)
        fcf_margin = (fcf / revenue) * 100
        croci = info.get('returnOnCapitalEmployed', 0) * 100 # Proxy for CROCI
        
        # Tier Logic (S: 3+ elite stats, A: 2+ elite stats)
        # Tech Benchmarks 2026: Growth > 25%, Margin > 20%
        elite_count = sum([rev_growth > 25, profit_margin > 20, fcf_margin > 20, croci > 15])
        tier = "S" if elite_count >= 3 else "A" if elite_count >= 2 else "B"
        
        # Valuation Math: Strike = 5-Year Median P/E * Forward EPS
        # Standard fallback if median isn't available: 15% below current price
        curr_price = info.get('currentPrice', 0)
        strike = curr_price * 0.85 
        exit_target = curr_price * 1.30
        
        return {
            "tier": tier, "strike": round(strike, 2), "exit": round(exit_target, 2),
            "stats": f"Growth: {rev_growth:.1f}% | Margin: {profit_margin:.1f}%"
        }
    except:
        return None

# 2. MASTER DATABASE (Keeps your vetted manual picks)
portfolio = {
    "Ticker": ["NVDA", "MSFT", "AMZN", "SOFI", "HOOD", "ANET", "META", "PLTR", "TSM", "AAPL", "V", "MU"],
    "Tier": ["S", "S", "A", "B+", "A", "S", "S", "S", "S", "A", "S", "S"],
    "Strike": [175.0, 395.0, 195.0, 18.5, 70.0, 145.0, 630.0, 125.0, 345.0, 250.0, 315.0, 380.0],
    "Exit": [265.0, 510.0, 285.0, 32.0, 115.0, 185.0, 800.0, 255.0, 475.0, 306.0, 405.0, 523.0]
}
df_master = pd.DataFrame(portfolio)

# 3. APP UI
st.set_page_config(page_title="Tier Master 2026", layout="wide")
st.sidebar.header("🔍 Dynamic Analyzer")
watchlist = st.sidebar.multiselect("Active Watchlist:", options=df_master["Ticker"].tolist(), default=["NVDA", "MSFT"])

new_ticker = st.sidebar.text_input("Analyze ANY Ticker:").upper()
if new_ticker and new_ticker not in watchlist:
    watchlist.append(new_ticker)

st.title("📈 Tier Master: Automated 4-Stat Analysis")

# 4. PROCESSING & DISPLAY
for ticker in watchlist:
    try:
        # Check if we use Manual Data or Auto-Calculated Data
        if ticker in df_master["Ticker"].values:
            match = df_master[df_master["Ticker"] == ticker].iloc[0]
            t_data = {"tier": match['Tier'], "strike": match['Strike'], "exit": match['Exit'], "stats": "Manual Vetted"}
        else:
            t_data = analyze_new_ticker(ticker)
            
        if t_data:
            stock = yf.Ticker(ticker)
            curr_p = stock.history(period="1d")['Close'].iloc[-1]
            signal = "🟢 BUY" if curr_p <= t_data['strike'] else "🟡 WAIT"
            
            with st.expander(f"{signal} | **{ticker}** | Price: ${curr_p:.2f}"):
                st.write(f"**Calculated Tier:** {t_data['tier']} | **Target Strike:** ${t_data['strike']}")
                st.write(f"**4-Stat Profile:** {t_data['stats']}")
                st.write(f"**Target Exit:** ${t_data['exit']}")
    except:
        continue
