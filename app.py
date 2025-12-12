import streamlit as st
import subprocess
import sys

# Force install yfinance if it's missing
try:
    import yfinance
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance"])
    import yfinance as yf
import openai
import pandas as pd
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="FinSmart Live", page_icon="📡", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .news-card { background-color: #1E1E1E; padding: 20px; border-radius: 8px; border-left: 5px solid #333; margin-bottom: 25px; }
    .headline { font-size: 22px; font-weight: 700; color: #fff; margin-bottom: 8px; }
    .source { font-size: 12px; color: #aaa; text-transform: uppercase; }
    .ticker-badge { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 14px; margin-right: 10px; }
    .up { background: rgba(0, 200, 5, 0.2); color: #00FF41; border: 1px solid #00C805; }
    .down { background: rgba(255, 43, 43, 0.2); color: #FF2B2B; border: 1px solid #FF2B2B; }
    .impact-box { background: #2D2D2D; padding: 15px; border-radius: 6px; margin-top: 15px; border-left: 3px solid #00A8FF; }
    .impact-title { color: #00A8FF; font-weight: bold; font-size: 14px; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: SETTINGS & KEYS ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    
    # 1. OpenAI Key Input (Crucial for the "Intelligence")
    api_key = st.text_input("Enter OpenAI API Key:", type="password", help="Needed to generate the 'Why/How' summaries.")
    if api_key:
        openai.api_key = api_key
    
    st.divider()
    
    # 2. User Preferences
    expertise = st.select_slider("Knowledge Level", options=["Beginner", "Expert"], value="Beginner")
    
    # 3. Watchlist
    st.subheader("👀 Watchlist")
    default_tickers = ["AAPL", "NVDA", "TSLA", "BTC-USD", "EURUSD=X"]
    tickers = st.multiselect("Select Assets:", default_tickers, default=["AAPL", "BTC-USD"])
    
    st.info("💡 'BTC-USD' is Bitcoin. 'EURUSD=X' is Euro/Dollar.")

# --- FUNCTION: FETCH LIVE DATA (YFINANCE) ---
def get_live_data(ticker_list):
    """
    Fetches real-time price changes and news for selected tickers.
    """
    data = []
    
    # 1. Get Price Changes
    for t in ticker_list:
        stock = yf.Ticker(t)
        
        # Get Price Change
        try:
            hist = stock.history(period="2d")
            if len(hist) >= 2:
                close_today = hist['Close'].iloc[-1]
                close_yesterday = hist['Close'].iloc[-2]
                change_pct = ((close_today - close_yesterday) / close_yesterday) * 100
                price_display = f"{change_pct:+.2f}%"
                direction = "up" if change_pct > 0 else "down"
            else:
                price_display = "0.00%"
                direction = "up"
        except:
            price_display = "N/A"
            direction = "up"

        # 2. Get Real News
        # yfinance news returns a list of dicts: {'title':..., 'link':..., 'publisher':...}
        news_list = stock.news
        
        if news_list:
            # We take the latest story for this ticker
            latest = news_list[0] 
            data.append({
                "ticker": t,
                "price_change": price_display,
                "direction": direction,
                "headline": latest['title'],
                "source": latest['publisher'],
                "link": latest['link'],
                "published": datetime.fromtimestamp(latest['providerPublishTime']).strftime('%H:%M'),
                "raw_text": latest['title'] # In a real app, we'd scrape the full link content
            })
    return data

# --- FUNCTION: GENERATE AI INSIGHT ---
def analyze_news(headline, ticker, level):
    """
    Sends the headline to OpenAI to generate the 'Why' and 'How'.
    """
    if not api_key:
        return None # User hasn't entered a key

    prompt = f"""
    Analyze this financial news headline for {ticker}: "{headline}"
    
    I need a structured explanation for a {level} audience.
    Return ONLY a JSON-like format with exactly these two keys:
    WHY: (Explain why this event happened in 1 sentence)
    HOW: (Explain how this impacts the specific stock or the user's wallet in 1 sentence)
    
    Do not use technical jargon if level is Beginner. Use trading terms if level is Expert.
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo", # Use gpt-4o if you have access
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating insight: {e}"

# --- MAIN APP UI ---
st.title("FinSmart Live 📡")

if not tickers:
    st.warning("Please select tickers in the sidebar.")
else:
    # Fetch Data
    with st.spinner(f"Fetching live data for {', '.join(tickers)}..."):
        news_items = get_live_data(tickers)

    # Display Data
    for item in news_items:
        
        # Ticker Badge Logic
        css_class = item['direction'] # 'up' or 'down'
        
        with st.container():
            st.markdown(f"""
            <div class="news-card">
                <div class="source">{item['source']} • {item['published']}</div>
                <div class="headline">{item['headline']}</div>
                <div style="margin-top:10px;">
                    <span class="ticker-badge {css_class}">{item['ticker']} {item['price_change']}</span>
                    <a href="{item['link']}" style="color: #00A8FF; text-decoration: none; font-size: 14px;">Read Full Story ↗</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # THE AI BUTTON
            # We don't auto-generate for everything to save your API costs/latency.
            # User clicks "Analyze" to run the LLM.
            
            col1, col2 = st.columns([0.2, 0.8])
            with col1:
                analyze_btn = st.button(f"⚡ Analyze Impact", key=f"btn_{item['ticker']}")
            
            if analyze_btn:
                if not api_key:
                    st.error("Please enter an OpenAI API Key in the sidebar first!")
                else:
                    with st.spinner("AI is analyzing market implications..."):
                        insight = analyze_news(item['headline'], item['ticker'], expertise)
                        
                        # Parsing the output simply for display (Robust JSON parsing recommended for prod)
                        st.markdown(f"""
                        <div class="impact-box">
                            <div class="impact-title">🤖 FinSmart Analysis ({expertise} Mode)</div>
                            <div style="color: #ddd; margin-top: 5px; white-space: pre-wrap;">{insight}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
        st.divider()

