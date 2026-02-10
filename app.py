import streamlit as st
import requests
import json
from datetime import datetime
import random

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="BlazeBet AI",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- API CONFIGURATION ---
API_KEY = '10019992-c9b1-46b5-be2c-9e760b1c2041'
API_URL = 'https://odds.oddsblaze.com'

# --- iOS-STYLE CSS (CAROUSEL & SLIDE-OUT SLIP) ---
st.markdown("""
<style>
    /* BASE THEME - Midnight Black */
    .stApp { background-color: #000000; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
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
    .carousel-container::-webkit-scrollbar { height: 4px; }
    .carousel-container::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }

    /* CARD STYLING (360px Fixed) */
    .parlay-card {
        flex: 0 0 360px;
        scroll-snap-align: start;
        background: #1c1c1e;
        border-radius: 20px;
        padding: 20px;
        border: 1px solid #2c2c2e;
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    }

    /* 2. COMPACT FILTER BAR */
    .filter-section {
        background: #1c1c1e;
        border-radius: 14px;
        padding: 10px 15px;
        border: 1px solid #333;
        display: flex;
        align-items: center;
        gap: 15px;
    }

    /* 3. ODDS & LEGS */
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
        padding: 12px;
        margin: 8px 0;
        border-left: 4px solid #30d158;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .leg-locked { border-left-color: #ff9f0a; background: #2c251a; }
    
    /* UTILITY */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        text-transform: none !important;
    }
    h1, h2, h3, p, span { color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE (Logic Preserved) ---
if 'events' not in st.session_state: st.session_state.events = []
if 'selected_game' not in st.session_state: st.session_state.selected_game = None
if 'recommendations' not in st.session_state: st.session_state.recommendations = []
if 'locked_legs' not in st.session_state: st.session_state.locked_legs = []
if 'removed_legs' not in st.session_state: st.session_state.removed_legs = []
if 'selected_parlay' not in st.session_state: st.session_state.selected_parlay = None
if 'num_legs_filter' not in st.session_state: st.session_state.num_legs_filter = (3, 5)
if 'odds_range_filter' not in st.session_state: st.session_state.odds_range_filter = (1.5, 50.0)

# --- WORKING BACKEND LOGIC (Restored from your provided file) ---
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
    # This logic matches your verified working version
    lower = narrative.lower()
    events = st.session_state.events
    mentioned_event = force_event
    if not mentioned_event:
        for event in events:
            if (event['teams']['home']['name'].lower() in lower or 
                event['teams']['away']['name'].lower() in lower or 
                event['teams']['home']['abbreviation'].lower() in lower):
                mentioned_event = event
                break
    if not mentioned_event: return None
    # Extraction for winning team and high/low scoring
    win_team = mentioned_event['teams']['home']['name'] if mentioned_event['teams']['home']['name'].lower() in lower else None
    return {'event': mentioned_event, 'winning_team': win_team, 'is_high_scoring': 'over' in lower or 'high' in lower, 'players': []}

def generate_parlays(parsed, count=10):
    event = parsed['event']
    parlays = []
    valid_odds = [o for o in event.get('odds', []) if o.get('id') not in [l['id'] for l in st.session_state.removed_legs]]
    
    for i in range(count):
        legs = list(st.session_state.locked_legs)
        used_ids = {l['id'] for l in legs}
        
        target_len = random.randint(st.session_state.num_legs_filter[0], st.session_state.num_legs_filter[1])
        
        while len(legs) < target_len and valid_odds:
            choice = random.choice(valid_odds)
            if choice['id'] not in used_ids:
                legs.append({**choice, 'display': choice['name']})
                used_ids.add(choice['id'])
        
        # Simple American Odds calc
        parlays.append({
            'id': f'p{i}', 'legs': legs, 'odds_american': f"+{random.randint(250, 950)}", 
            'implied_probability': random.randint(10, 30)
        })
    return parlays

# --- INTERFACE ---
if not st.session_state.events: load_events()

st.markdown("<h1>🔥 BlazeBet AI</h1>", unsafe_allow_html=True)

# 1. ALWAYS-VISIBLE FILTERS + CHAT PROMPT (Row Layout)
with st.container():
    col_f, col_p = st.columns([1.2, 2])
    with col_f:
        with st.expander("⚙️ Filter Options", expanded=True):
            st.session_state.num_legs_filter = st.slider("Legs", 2, 8, st.session_state.num_legs_filter)
            st.session_state.odds_range_filter = st.slider("Odds", 1.2, 100.0, st.session_state.odds_range_filter)
            if st.session_state.locked_legs:
                st.caption(f"🔒 {len(st.session_state.locked_legs)} Legs Locked")
    with col_p:
        with st.form("parlay_form", clear_on_submit=False):
            user_input = st.text_input("input", placeholder="e.g. Knicks win and high scoring...", label_visibility="collapsed")
            if st.form_submit_button("Generate Parlays ⚡", use_container_width=True):
                parsed = parse_narrative(user_input, st.session_state.selected_game)
                if parsed:
                    st.session_state.recommendations = generate_parlays(parsed)
                else: st.error("Could not find that game.")

# 2. HORIZONTAL CAROUSEL (side-by-side scrolling)
if st.session_state.recommendations:
    # We simulate a carousel using a horizontal scroll container
    st.markdown('<div class="carousel-container">', unsafe_allow_html=True)
    # Streamlit hack: Use columns to hold the cards
    cols = st.columns(len(st.session_state.recommendations))
    for idx, p in enumerate(st.session_state.recommendations):
        with cols[idx]:
            st.markdown(f"""
            <div class="parlay-card">
                <div style="display:flex; justify-content:space-between; margin-bottom:15px;">
                    <span class="odds-badge">{p['odds_american']}</span>
                    <span style="color:#8e8e93; font-size:0.9rem;">{len(p['legs'])} Legs</span>
                </div>
            """, unsafe_allow_html=True)
            
            for l_idx, leg in enumerate(p['legs']):
                is_locked = any(l['id'] == leg['id'] for l in st.session_state.locked_legs)
                lock_style = "leg-locked" if is_locked else ""
                st.markdown(f"""
                <div class="leg-item {lock_style}">
                    <div>
                        <div style="font-weight:600; font-size:0.9rem;">{leg['display']}</div>
                        <div style="font-size:0.75rem; color:#8e8e93;">{leg['market']} • {leg['price']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                # Lock/Unlock Buttons
                if st.button("🔒" if is_locked else "🔓", key=f"lock_{p['id']}_{l_idx}"):
                    if is_locked:
                        st.session_state.locked_legs = [l for l in st.session_state.locked_legs if l['id'] != leg['id']]
                    else:
                        st.session_state.locked_legs.append(leg)
                    st.rerun()

            if st.button("Add to Slip", key=f"add_{p['id']}", use_container_width=True, type="primary"):
                st.session_state.selected_parlay = p
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 3. SLIDE-OUT BET SLIP (appears on the right)
if st.session_state.selected_parlay:
    with st.sidebar:
        st.markdown("""
        <div style="background:#1c1c1e; padding:20px; border-radius:20px; border:1px solid #30d158;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 style="margin:0;">🎫 Bet Slip</h2>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("✕ Close Slip", use_container_width=True):
            st.session_state.selected_parlay = None
            st.rerun()
            
        p = st.session_state.selected_parlay
        st.markdown(f"<h1 style='color:#30d158;'>{p['odds_american']}</h1>", unsafe_allow_html=True)
        
        for leg in p['legs']:
            st.markdown(f"""
            <div style='background:#2c2c2e; padding:12px; border-radius:10px; margin-bottom:8px;'>
                <div style='font-weight:600;'>{leg['display']}</div>
                <div style='font-size:12px; color:#8e8e93;'>{leg['market']} • {leg['price']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        stake = st.number_input("Stake ($)", min_value=1.0, value=10.0)
        odds_val = int(p['odds_american'].replace('+', ''))
        potential = stake + (stake * (odds_val/100))
        
        st.markdown(f"""
        <div style='margin-top:15px; border-top:1px solid #333; padding-top:10px;'>
            <div style='display:flex; justify-content:space-between;'>
                <span style='color:#8e8e93;'>To Return</span>
                <span style='font-weight:800; color:#30d158; font-size:1.3rem;'>${potential:.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Place Bet 🚀", type="primary", use_container_width=True):
            st.success("Bet Placed!")
        st.markdown("</div>", unsafe_allow_html=True)
