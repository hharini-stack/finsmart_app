import streamlit as st
import pandas as pd
import time
from datetime import datetime

# --- PAGE CONFIGURATION (Bloomberg Style Dark Mode) ---
st.set_page_config(
    page_title="FinSmart",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (To make it look like an App, not a script) ---
st.markdown("""
<style>
    .card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #333;
        margin-bottom: 20px;
    }
    .bullish { border-left-color: #00C805 !important; }
    .bearish { border-left-color: #FF2B2B !important; }
    .neutral { border-left-color: #FFA500 !important; }
    
    .headline { font-size: 22px; font-weight: bold; color: #FFFFFF; font-family: 'Helvetica Neue', sans-serif; }
    .source { font-size: 12px; color: #888; margin-bottom: 10px; }
    .tag { background-color: #333; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-right: 5px; }
    .impact-high { color: #FF2B2B; font-weight: bold; }
    .impact-med { color: #FFA500; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- MOCK DATA ENGINE (Simulating your Backend) ---
def get_news_data():
    return [
        {
            "id": 1,
            "headline": "Fed hikes rates by 25bps, signals pause",
            "source": "Bloomberg Markets",
            "time": "10m ago",
            "tags": ["Macro", "USD", "Fed"],
            "sentiment": "bearish",
            "impact": 95,
            "beginner_view": "The US Central Bank is making it more expensive to borrow money. This usually slows down the economy but helps stop prices from rising too fast (inflation).",
            "expert_view": "FOMC delivers 25bps hike as priced in. Dot plot suggests terminal rate is near. Expect DXY consolidation and pressure on growth stocks.",
            "el_erian_comment": "This is the 'trilemma' in action—fighting inflation without breaking growth."
        },
        {
            "id": 2,
            "headline": "Bitcoin surges past $45k on ETF rumours",
            "source": "CoinDesk",
            "time": "2h ago",
            "tags": ["Crypto", "BTC", "Regulation"],
            "sentiment": "bullish",
            "impact": 88,
            "beginner_view": "Bitcoin's price is going up because people think the government will soon let regular stock investors buy Bitcoin easily (through an ETF).",
            "expert_view": "Institutional inflows anticipated pending SEC approval. BTC breaking key resistance levels; short squeeze likely above $46k.",
            "el_erian_comment": "Speculative assets are reacting to liquidity hopes, not fundamentals."
        },
        {
            "id": 3,
            "headline": "NVIDIA revenue beats expectations by 20%",
            "source": "Financial Times",
            "time": "4h ago",
            "tags": ["Tech", "AI", "Stocks"],
            "sentiment": "bullish",
            "impact": 60,
            "beginner_view": "NVIDIA (the chip company) sold way more AI chips than anyone guessed. This is good for the company and shows the AI boom is real.",
            "expert_view": "Data center revenue up 140% YoY. Forward guidance raised. Supports the structural AI bull case despite high valuations.",
            "el_erian_comment": None # Not all stories have expert comments
        },
        {
            "id": 4,
            "headline": "Oil prices drop as production increases",
            "source": "Reuters",
            "time": "5h ago",
            "tags": ["Commodities", "Oil", "Energy"],
            "sentiment": "bearish",
            "impact": 45,
            "beginner_view": "Gas might get cheaper soon because there is more oil available in the market than people need right now.",
            "expert_view": "WTI crude testing support at $70. Supply glut concerns outweigh geopolitical risk premiums.",
            "el_erian_comment": None
        }
    ]

# --- SIDEBAR (User Profile & Watchlist) ---
with st.sidebar:
    st.header("👤 User Profile")
    
    # 1. The "Level" Slider
    expertise = st.select_slider(
        "Your Knowledge Level",
        options=["Beginner", "Intermediate", "Expert"],
        value="Beginner"
    )
    
    st.divider()
    
    # 2. The Watchlist (The Feature You Asked For)
    st.header("👀 Watchlist")
    st.caption("Filter news by your interests")
    
    all_tags = ["Macro", "Crypto", "Tech", "Stocks", "Commodities", "Fed", "AI"]
    selected_watchlist = st.multiselect(
        "Select Topics:",
        all_tags,
        default=["Macro", "Crypto", "Tech"]
    )
    
    st.divider()
    st.info(f"Viewing as: **{expertise}**\n\nFiltering for: **{', '.join(selected_watchlist)}**")

# --- MAIN FEED ---
st.title("FinSmart ⚡")
st.caption("Contextual Intelligence for Modern Markets")

# Get Data
news_items = get_news_data()

# Filter Data based on Watchlist
filtered_news = [
    item for item in news_items 
    if any(tag in selected_watchlist for tag in item["tags"])
]

if not filtered_news:
    st.warning("No news found for your watchlist. Try adding more topics!")

# Render the News Cards
for item in filtered_news:
    
    # Determine the "Why" text based on the Slider
    if expertise == "Beginner":
        explanation = item["beginner_view"]
        context_label = "💡 The Basic Concept"
    elif expertise == "Expert":
        explanation = item["expert_view"]
        context_label = "🧠 Technical Analysis"
    else: # Intermediate gets a mix or default
        explanation = item["beginner_view"] + " " + item["expert_view"]
        context_label = "📝 Deep Dive"

    # HTML Card Construction
    sentiment_class = item["sentiment"] # bullish, bearish, neutral
    
    # Visual Layout
    with st.container():
        # Using columns to create the layout
        c1, c2 = st.columns([0.85, 0.15])
        
        with c1:
            st.markdown(f"""
            <div class="card {sentiment_class}">
                <div class="source">{item['source']} • {item['time']}</div>
                <div class="headline">{item['headline']}</div>
                <div style="margin-top: 10px;">
                    {' '.join([f'<span class="tag">{t}</span>' for t in item['tags']])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # The "Context Toggle" Section (The Magic Feature)
            with st.expander(f"{context_label} (Click to Read)", expanded=True):
                st.write(explanation)
                
                # El-Erian Comment Feature
                if item["el_erian_comment"]:
                    st.markdown(f"""
                    > **Mohamed El-Erian says:** > *"{item['el_erian_comment']}"*
                    """)
        
        with c2:
            # The "Bloomberg" Data Column
            st.metric(label="Impact", value=f"{item['impact']}/100")
            if item['sentiment'] == 'bullish':
                st.markdown("🟢 **Bullish**")
            else:
                st.markdown("🔴 **Bearish**")
            
            st.button("Save", key=f"save_{item['id']}")
            st.button("Share", key=f"share_{item['id']}")

    st.divider()
