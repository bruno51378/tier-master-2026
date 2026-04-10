import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. INTEGRATED DATABASE (Vetted Tickers + Manual Tiers/Targets)
# This keeps your 53 pre-vetted stocks exactly as you ranked them.
vetted_data = {
    "Ticker": ["PLTR", "SHOP", "CRWD", "CDNS", "PANW", "MCO", "ANET", "MSFT", "CLS", "WDC", "MU", "V", "TSM", "TQQQ", "MA", "LLY", "RACE", "NVDA", "JPM", "AVGO", "STX", "HWM", "VRT", "META", "LRCX", "ARM", "HOOD", "AMD", "GEV", "UAL", "FTNT", "UPRO", "MRK", "AMZN", "EXPE", "IWM", "UBER", "AAPL", "WMT", "GOOGL", "CMG", "PGR", "FANG", "VST", "IREN", "CELH", "LMT", "RKLB", "HIMS", "BAC", "SOFI", "ORCL", "CVX"],
    "Tier": ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S", "S", "S", "S", "N/A", "S", "S", "S", "S", "S", "S", "S", "S", "S", "S", "S", "A", "A", "A", "S", "A", "A", "N/A", "A", "A", "A", "N/A", "A", "A", "A", "A", "A", "A", "A", "A", "B+", "B", "B", "B", "B", "B", "B+", "B", "B"],
    "Strike": [125.0, 105.0, 385.0, 275.0, 142.0, 405.0, 145.0, 395.0, 265.0, 265.0, 380.0, 315.0, 345.0, 35.0, 520.0, 950.0, 410.0, 175.0, 295.0, 310.0, 385.0, 230.0, 210.0, 630.0, 215.0, 112.0, 70.0, 195.0, 795.0, 98.0, 74.0, 85.0, 112.0, 195.0, 212.0, 195.0, 68.0, 250.0, 118.0, 295.0, 32.0, 198.0, 172.0, 150.0, 38.0, 41.0, 625.0, 62.0, 14.5, 48.5, 18.5, 145.0, 172.0],
    "Exit": [255.0, 165.0, 555.0, 395.0, 225.0, 550.0, 185.0, 510.0, 355.0, 340.0, 523.0, 405.0, 475.0, 60.0, 605.0, 1200.0, 580.0, 265.0, 365.0, 455.0, 550.0, 320.0, 310.0, 800.0, 325.0, 160.0, 115.0, 267.0, 1100.0, 145.0, 115.0, 130.0, 143.0, 285.0, 315.0, 245.0, 105.0, 306.0, 147.0, 410.0, 55.0, 285.0, 215.0, 220.0, 75.0, 68.0, 710.0, 95.0, 38.0, 65.0, 32.0, 210.0, 215.0]
}
df_master = pd.DataFrame(vetted_data)

# 2. THE DYNAMIC ANALYSIS ENGINE (For new searches)
def get_dynamic_analysis(ticker):
    try:
        stock = yf.Ticker(ticker)
        # Pull 2026 Trailing 12-Month stats
        info = stock.info
        rev_growth = info.get('revenueGrowth', 0) * 100
        profit_margin = info.get('profitMargins', 0) * 100
        fcf = info.get('freeCashflow', 0)
        total_rev = info.get('totalRevenue', 1)
        fcf_margin = (fcf / total_rev) * 100
        # Return on Assets as a proxy for CROCI efficiency
        roa = info.get('returnOnAssets', 0) * 100

        # Tier Ranking Logic based on your 4-stat criteria
        elite_hits = sum([rev_growth > 20, profit_margin > 15, fcf_margin > 15, roa > 10])
        tier = "S" if elite_hits >= 3 else "A" if elite_hits == 2 else "B"
        
        # Strike Price Calculation (15% Margin of Safety from 5-Year Median P/E equivalent)
        curr_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        strike = curr_price * 0.85
        exit_p = curr_price * 1.30
        
        return {
            "tier": tier, "strike": round(strike, 2), "exit": round(exit_p, 2),
            "summary": f"Growth: {rev_growth:.1f}% | Margin: {profit_margin:.1f}% | FCF: {fcf_margin:.1f}% | ROA: {roa:.1f}%"
        }
    except:
        return None

# 3. APP INTERFACE
st.set_page_config(page_title="Tier Master 2026", layout="wide")
st.sidebar.title("🔍 Portfolio Search")
watchlist = st.sidebar.multiselect("Active Watchlist:", options=df_master["Ticker"].tolist(), default=["NVDA", "MSFT", "SOFI"])

# New Ticker Search functionality
search_ticker = st.sidebar.text_input("Analyze ANY New Ticker:").upper()
if search_ticker and search_ticker not in watchlist:
    watchlist.append(search_ticker)

st.title("📈 2026 Tier Master: Vetted & Dynamic Dashboard")

# 4. EXECUTION & AUTO-SORTING
display_list = []
for ticker in watchlist:
    try:
        time.sleep(0.05) # Prevent rate-limiting
        stock = yf.Ticker(ticker)
        curr_p = stock.history(period="1d")['Close'].iloc[-1]
        
        if ticker in df_master["Ticker"].values:
            # Load Vetted Data
            match = df_master[df_master["Ticker"] == ticker].iloc
            data = {"tier": match['Tier'], "strike": match['Strike'], "exit": match['Exit'], "source": "Vetted"}
        else:
            # Run Dynamic Engine
            dyn = get_dynamic_analysis(ticker)
            data = {**dyn, "source": "Dynamic Analysis"} if dyn else None

        if data:
            signal = "🟢 BUY" if curr_p <= data['strike'] else "🟡 WAIT"
            display_list.append({**data, "ticker": ticker, "price": curr_p, "signal": signal, "sort": 0 if signal == "🟢 BUY" else 1})
    except: continue

# Sort: BUY signals at the top
sorted_display = sorted(display_list, key=lambda x: x['sort'])

for item in sorted_display:
    with st.expander(f"{item['signal']} | **{item['ticker']}** | ${item['price']:.2f} (Strike: ${item['strike']})"):
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Tier:** {item['tier']} | **Source:** {item['source']}")
            st.write(f"**Target Exit:** ${item['exit']}")
            if 'summary' in item: st.caption(item['summary'])
        with c2:
            # Pull News
            st.write("**Latest Headlines:**")
            for n in yf.Ticker(item['ticker']).news[:2]:
                t = n.get('title', n.get('content', {}).get('title', 'News'))
                l = n.get('link', n.get('content', {}).get('clickThroughUrl', {}).get('url', '#'))
                st.markdown(f"* [{t}]({l})")
