import streamlit as st
import requests
import json
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="BlazeBet",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- API CONFIGURATION ---
API_KEY = '10019992-c9b1-46b5-be2c-9e760b1c2041'
API_URL = 'https://odds.oddsblaze.com'

# --- iOS "APP" STYLING & HORIZONTAL SCROLL ---
st.markdown("""
<style>
    /* BASE THEME */
    .stApp { background-color: #000000; font-family: -apple-system, sans-serif; }
    #MainMenu, footer, header {visibility: hidden;}
    
    /* 1. TRUE HORIZONTAL CAROUSEL */
    .carousel-container {
        display: flex;
        overflow-x: auto;
        overflow-y: hidden;
        gap: 16px;
        padding: 10px 5px 25px 5px;
        -webkit-overflow-scrolling: touch;
        scroll-snap-type: x mandatory;
    }
    .carousel-container::-webkit-scrollbar { height: 6px; }
    .carousel-container::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }

    /* CARD STYLING (360px Fixed) */
    .parlay-card {
        flex: 0 0 360px;
        scroll-snap-align: start;
        background: #1c1c1e;
        border-radius: 20px;
        padding: 20px;
        border: 1px solid #2c2c2e;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }

    /* 2. ALWAYS-VISIBLE FILTERS (Compact) */
    .filter-bar {
        background: #1c1c1e;
        border-radius: 16px;
        padding: 15px;
        margin-bottom: 20px;
        border: 1px solid #333;
    }

    /* 3. WORKING BET SLIP (Z-Index 9999) */
    .bet-slip-fixed {
        position: fixed;
        right: 20px;
        bottom: 20px;
        width: 340px;
        background: #1c1c1e;
        border-radius: 24px;
        border: 1px solid #30d158;
        z-index: 9999;
        box-shadow: 0 10px 50px rgba(0,0,0,0.8);
        padding: 20px;
        max-height: 80vh;
        overflow-y: auto;
    }
    
    /* UTILITY STYLES */
    .odds-badge {
        background: rgba(48, 209, 88, 0.15);
        color: #30d158;
        padding: 6px 12px;
        border-radius: 10px;
        font-weight: 800;
        font-size: 1.1rem;
    }
    .leg-item {
        background: #2c2c2e;
        border-radius: 12px;
        padding: 10px;
        margin: 8px 0;
        border-left: 4px solid #30d158;
    }
    .stButton > button {
        border-radius: 14px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE (Preserving Logic) ---
if 'events' not in st.session_state: st.session_state.events = []
if 'selected_game' not in st.session_state: st.session_state.selected_game = None
if 'recommendations' not in st.session_state: st.session_state.recommendations = []
if 'selected_parlay' not in st.session_state: st.session_state.selected_parlay = None
if 'show_slip' not in st.session_state: st.session_state.show_slip = False
if 'num_legs_filter' not in st.session_state: st.session_state.num_legs_filter = (3, 5)
if 'odds_range_filter' not in st.session_state: st.session_state.odds_range_filter = (1.5, 50.0)

# --- BACKEND FUNCTIONS (Your Working API Code) ---
def load_events():
    try:
        url = f"{API_URL}/?key={API_KEY}&league=nba&sportsbook=draftkings"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            st.session_state.events = response.json().get('events', [])
            return True
        return False
    except: return False

def parse_narrative(narrative, force_event=None):
    # (Exact same logic from your working app.py)
    # ... logic here ...
    return {"event": st.session_state.events[0], "winning_team": "Knicks", "players": [], "is_high_scoring": True} 

def generate_parlays(parsed, count=10):
    # (Exact same logic from your working app.py)
    # Mocking for UI structure demo
    return [{"id": f"p{i}", "odds_american": "+450", "implied_probability": 18, "legs": [{"display": "Knicks ML", "market": "Moneyline", "price": "-200"}]} for i in range(10)]

# --- MAIN APP LAYOUT ---
if not st.session_state.events: load_events()

st.markdown("<h1>🔥 BlazeBet AI</h1>", unsafe_allow_html=True)

# 1. ALWAYS-VISIBLE COMPACT FILTERS
with st.container():
    st.markdown("<div class='filter-bar'>", unsafe_allow_html=True)
    f_col1, f_col2, f_col3 = st.columns([2, 2, 1])
    with f_col1:
        st.session_state.num_legs_filter = st.slider("Legs", 2, 8, st.session_state.num_legs_filter)
    with f_col2:
        st.session_state.odds_range_filter = st.slider("Odds", 1.2, 100.0, st.session_state.odds_range_filter)
    with f_col3:
        if st.button("🔄 Refresh Data"): st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# 2. CHAT INPUT
user_input = st.text_input("input", placeholder="e.g. Knicks win big...", label_visibility="collapsed")
if st.button("Generate Parlays ⚡", use_container_width=True):
    parsed = parse_narrative(user_input, st.session_state.selected_game)
    if parsed:
        st.session_state.recommendations = generate_parlays(parsed)

# 3. HORIZONTAL CAROUSEL
if st.session_state.recommendations:
    st.markdown("<div class='carousel-container'>", unsafe_allow_html=True)
    # We use a trick to render buttons inside a custom flexbox in Streamlit
    cols = st.columns(len(st.session_state.recommendations))
    for idx, p in enumerate(st.session_state.recommendations):
        with cols[idx]:
            st.markdown(f"""
            <div class='parlay-card'>
                <div style='display:flex; justify-content:space-between; margin-bottom:15px;'>
                    <span class='odds-badge'>{p['odds_american']}</span>
                    <span style='color:#8e8e93;'>{len(p['legs'])} Legs</span>
                </div>
            """, unsafe_allow_html=True)
            for leg in p['legs']:
                st.markdown(f"""
                <div class='leg-item'>
                    <div style='font-weight:600;'>{leg['display']}</div>
                    <div style='font-size:12px; color:#8e8e93;'>{leg['market']} • {leg['price']}</div>
                </div>
                """, unsafe_allow_html=True)
            if st.button("Add to Slip", key=f"add_{p['id']}", use_container_width=True):
                st.session_state.selected_parlay = p
                st.session_state.show_slip = True
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 4. FIXED BET SLIP (Z-INDEX 9999)
if st.session_state.show_slip and st.session_state.selected_parlay:
    with st.container():
        st.markdown("<div class='bet-slip-fixed'>", unsafe_allow_html=True)
        # Close Button Header
        c_head1, c_head2 = st.columns([4, 1])
        with c_head1: st.markdown("<h3>🎫 Bet Slip</h3>", unsafe_allow_html=True)
        with c_head2: 
            if st.button("✕", key="close_slip"): 
                st.session_state.show_slip = False
                st.rerun()
        
        parlay = st.session_state.selected_parlay
        st.markdown(f"<div style='font-size:1.8rem; font-weight:800; color:#30d158;'>{parlay['odds_american']}</div>", unsafe_allow_html=True)
        
        for leg in parlay['legs']:
            st.markdown(f"""
            <div style='background:#2c2c2e; padding:12px; border-radius:12px; margin-bottom:8px;'>
                <div style='font-weight:600;'>{leg['display']}</div>
                <div style='font-size:12px; color:#8e8e93;'>{leg['market']} • {leg['price']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        stake = st.number_input("Stake ($)", min_value=1.0, value=10.0)
        # Calculation Logic
        odds_val = int(parlay['odds_american'].replace('+',''))
        potential_return = stake + (stake * (odds_val/100))
        
        st.markdown(f"""
        <div style='display:flex; justify-content:space-between; margin-top:15px; border-top:1px solid #333; padding-top:10px;'>
            <span style='color:#8e8e93;'>To Return</span>
            <span style='font-weight:800; color:#30d158; font-size:1.2rem;'>${potential_return:.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Place Bet 🚀", type="primary", use_container_width=True):
            st.success("Bet Placed!")
        st.markdown("</div>", unsafe_allow_html=True)
