import time  # Add this at the top

# Inside your display loop:
for i, row in df_master.iterrows():
    time.sleep(0.1)  # Add a 0.1-second delay between tickers
    # ... rest of your code ...
import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Database containing your complete list and tiers
portfolio = {
    "Ticker": ["NVDA", "MSFT", "AMZN", "SOFI", "HOOD", "ANET", "META", "PLTR", "TSM", "AAPL", "V", "MU", "VRT", "CRWD", "CLS", "HWM", "CDNS", "ARM", "CVX", "AMD", "UAL", "FTNT", "WDC", "EXPE", "RKLB", "LMT", "JPM", "FANG", "IREN", "ORCL", "PINS", "BAC", "CELH", "HIMS", "MRK", "WMT", "MSTR", "LRCX", "STX", "PANW", "CMG", "PGR"],
    "Tier": ["S", "S", "A", "B+", "A", "S", "S", "S", "S", "A", "S", "S", "S", "S", "S", "S", "S", "A", "B", "A", "A", "A", "S", "A", "B", "B", "S", "S", "B+", "B", "C", "B", "B", "B", "A", "A", "F", "S", "S", "S", "A", "A"],
    "Strike": [175.00, 395.00, 195.00, 18.50, 70.00, 145.00, 630.00, 125.00, 345.00, 250.00, 315.00, 380.00, 210.00, 385.00, 265.00, 230.00, 275.00, 112.00, 172.00, 195.00, 98.00, 74.00, 265.00, 212.00, 62.00, 625.00, 295.00, 165.00, 38.00, 145.00, 14.50, 48.50, 41.00, 14.50, 112.00, 118.00, 75.00, 215.00, 385.00, 142.00, 32.00, 198.00],
    "Exit": [265.00, 510.00, 285.00, 32.00, 115.00, 185.00, 800.00, 255.00, 475.00, 306.00, 405.00, 523.00, 310.00, 555.00, 355.00, 320.00, 395.00, 160.00, 215.00, 267.00, 145.00, 115.00, 340.00, 315.00, 95.00, 710.00, 365.00, 215.00, 75.00, 210.00, 30.00, 65.00, 68.00, 38.00, 143.00, 147.00, 400.00, 325.00, 550.00, 225.00, 55.00, 285.00]
}
df_master = pd.DataFrame(portfolio)

# 2. AI Sentiment Engine
def analyze_sentiment(news_list):
    if not news_list: return "Neutral", "gray"
    
    pos_words = ['beat', 'surge', 'buy', 'growth', 'upgrade', 'dividend', 'partnership', 'record']
    neg_words = ['miss', 'fall', 'sell', 'drop', 'downgrade', 'loss', 'debt', 'risk']
    
    score = 0
    for n in news_list:
        title = n['title'].lower()
        score += sum(1 for w in pos_words if w in title)
        score -= sum(1 for w in neg_words if w in title)
    
    if score > 0: return "Bullish", "green"
    elif score < 0: return "Bearish", "red"
    return "Neutral", "gray"

# 3. App Layout
st.set_page_config(page_title="Tier Master 2026", page_icon="📈", layout="wide")
st.title("📈 Tier Master: Real-Time Signals & AI Sentiment")

# 4. Processing and Display
for i, row in df_master.iterrows():
    try:
        stock = yf.Ticker(row['Ticker'])
        price = stock.fast_info.last_price
        news = stock.news[:3]
        sentiment, s_color = analyze_sentiment(news)
        signal = "🟢 BUY" if price <= row['Strike'] else "🟡 WAIT"
        
        with st.expander(f"**{row['Ticker']}** | Price: ${price:.2f} | **{signal}**"):
            c1, c2 = st.columns([1, 2])
            with c1:
                st.write(f"**Tier:** {row['Tier']} | **Strike:** ${row['Strike']}")
                st.write(f"**Target Exit:** ${row['Exit']}")
                st.markdown(f"Sentiment: :{s_color}[**{sentiment}**]")
            with c2:
                for art in news:
                    st.markdown(f"* [{art['title']}]({art['link']})")
    except:
        st.error(f"Error loading {row['Ticker']}")
