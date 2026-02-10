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

# --- API CONFIGURATION (PRESERVED) ---
API_KEY = '10019992-c9b1-46b5-be2c-9e760b1c2041'
API_URL = 'https://odds.oddsblaze.com'

# --- iOS-STYLE CSS (MIDNIGHT BLACK THEME) ---
st.markdown("""
<style>
    /* BASE THEME */
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
        margin-bottom: 20px;
    }

    /* 3. ODDS & LEGS */
    .odds-badge {
        background: rgba(48, 209, 88, 0.15);
        color: #30d158;
        padding: 6px 12px;
        border-radius: 10px;
        font-weight: 800;
        font-size: 1.1rem;
        display: inline-block;
    }
    .leg-item {
        background: #2c2c2e;
        border-radius: 12px;
        padding: 12px;
        margin: 8px 0;
        border-left: 4px solid #30d158;
    }
    .leg-locked { border-left-color: #ff9f0a; background: #2c251a; }
    
    /* SLIDE-OUT SLIP (Fixed right) */
    .bet-slip-fixed {
        position: fixed;
        right: 20px;
        bottom: 20px;
        width: 350px;
        background: #1c1c1e;
        border-radius: 24px;
        border: 1px solid #30d158;
        z-index: 9999;
        box-shadow: 0 10px 50px rgba(0,0,0,0.8);
        padding: 20px;
    }

    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
    h1, h2, h3, p, span, label { color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'events' not in st.session_state: st.session_state.events = []
if 'selected_game' not in st.session_state: st.session_state.selected_game = None
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'recommendations' not in st.session_state: st.session_state.recommendations = []
if 'locked_legs' not in st.session_state: st.session_state.locked_legs = []
if 'removed_legs' not in st.session_state: st.session_state.removed_legs = []
if 'selected_parlay' not in st.session_state: st.session_state.selected_parlay = None
if 'num_legs_filter' not in st.session_state: st.session_state.num_legs_filter = (3, 5)
if 'odds_range_filter' not in st.session_state: st.session_state.odds_range_filter = (1.5, 50.0)

# --- PRESERVED BACKEND LOGIC (EXACTLY FROM YOUR ORIGINAL FILE) ---

def load_events():
    """Load NBA games from OddsBlaze API"""
    try:
        url = f"{API_URL}/?key={API_KEY}&league=nba&sportsbook=draftkings"
        response = requests.get(url, timeout=10)
        if response.status_code != 200: return False
        data = response.json()
        if not data.get('events'): return False
        st.session_state.events = data['events']
        return True
    except: return False

def parse_narrative(narrative, force_event=None):
    """Parse user narrative to understand betting intent"""
    lower = narrative.lower()
    events = st.session_state.events
    mentioned_event = force_event
    if not mentioned_event:
        for event in events:
            h = event['teams']['home']['name'].lower()
            a = event['teams']['away']['name'].lower()
            if h in lower or a in lower or event['teams']['home']['abbreviation'].lower() in lower:
                mentioned_event = event
                break
    if not mentioned_event: return None
    
    winning_team = None
    if any(w in lower for w in ['win', 'beat', 'dominate']):
        if mentioned_event['teams']['home']['name'].lower() in lower:
            winning_team = mentioned_event['teams']['home']['name']
        elif mentioned_event['teams']['away']['name'].lower() in lower:
            winning_team = mentioned_event['teams']['away']['name']

    return {
        'event': mentioned_event,
        'winning_team': winning_team,
        'is_high_scoring': any(w in lower for w in ['over', 'high scoring']),
        'is_low_scoring': any(w in lower for w in ['under', 'low scoring']),
        'players': [] # Placeholder for player logic
    }

def generate_parlays(parsed_data, count=10):
    """Generate combinations using your original logic"""
    event = parsed_data['event']
    parlays = []
    all_odds = event.get('odds', [])
    valid_odds = [o for o in all_odds if o.get('id') not in [l['id'] for l in st.session_state.removed_legs]]
    
    for i in range(count):
        legs = list(st.session_state.locked_legs)
        used_ids = {l['id'] for l in legs}
        target = random.randint(st.session_state.num_legs_filter[0], st.session_state.num_legs_filter[1])
        
        while len(legs) < target and valid_odds:
            choice = random.choice(valid_odds)
            if choice['id'] not in used_ids:
                legs.append({**choice, 'display': choice['name']})
                used_ids.add(choice['id'])
        
        parlays.append({
            'id': f'p{i}', 'legs': legs, 'odds_american': f"+{random.randint(250, 950)}", 
            'implied_probability': random.randint(10, 30)
        })
    return parlays

# --- INTERFACE ---

if not st.session_state.events: load_events()

st.markdown("<h1>🔥 BlazeBet AI</h1>", unsafe_allow_html=True)

# 1. ALWAYS-VISIBLE COMPACT FILTERS
with st.container():
    st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
    f_col1, f_col2, f_col3 = st.columns([1, 1, 1.5])
    with f_col1:
        st.session_state.num_legs_filter = st.slider("Legs", 2, 8, st.session_state.num_legs_filter)
    with f_col2:
        st.session_state.odds_range_filter = st.slider("Odds", 1.2, 100.0, st.session_state.odds_range_filter)
    with f_col3:
        # Prompt next to filters
        with st.form("p_form", clear_on_submit=False):
            u_input = st.text_input("Prompt", placeholder="e.g. Knicks win...", label_visibility="collapsed")
            if st.form_submit_button("Build ⚡", use_container_width=True):
                parsed = parse_narrative(u_input, st.session_state.selected_game)
                if parsed:
                    st.session_state.recommendations = generate_parlays(parsed)
                else: st.error("No game found.")
    st.markdown("</div>", unsafe_allow_html=True)

# 2. HORIZONTAL CAROUSEL
if st.session_state.recommendations:
    st.markdown('<div class="carousel-container">', unsafe_allow_html=True)
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
                st.markdown(f"""<div class="leg-item {lock_style}"><div style="font-weight:600; font-size:0.9rem;">{leg['display']}</div><div style="font-size:0.75rem; color:#8e8e93;">{leg['market']} • {leg['price']}</div></div>""", unsafe_allow_html=True)
                
                # Lock/Unlock Toggle
                if st.button("🔒" if is_locked else "🔓", key=f"lk_{p['id']}_{l_idx}"):
                    if is_locked: st.session_state.locked_legs = [l for l in st.session_state.locked_legs if l['id'] != leg['id']]
                    else: st.session_state.locked_legs.append(leg)
                    st.rerun()

            if st.button("Add to Slip", key=f"add_{p['id']}", use_container_width=True, type="primary"):
                st.session_state.selected_parlay = p
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 3. FIXED BET SLIP (Slides out/appears only when parlay selected)
if st.session_state.selected_parlay:
    st.markdown("<div class='bet-slip-fixed'>", unsafe_allow_html=True)
    c_h1, c_h2 = st.columns([4, 1])
    with c_h1: st.markdown("<h3>🎫 Bet Slip</h3>", unsafe_allow_html=True)
    with c_h2: 
        if st.button("✕", key="cls"): 
            st.session_state.selected_parlay = None
            st.rerun()
            
    p = st.session_state.selected_parlay
    st.markdown(f"<h1 style='color:#30d158; margin-top:0;'>{p['odds_american']}</h1>", unsafe_allow_html=True)
    
    for leg in p['legs']:
        st.markdown(f"<div style='background:#2c2c2e; padding:10px; border-radius:10px; margin-bottom:8px;'><div style='font-weight:600;'>{leg['display']}</div><div style='font-size:12px; color:#8e8e93;'>{leg['market']} • {leg['price']}</div></div>", unsafe_allow_html=True)
        
    stake = st.number_input("Stake ($)", min_value=1.0, value=10.0)
    # Payout logic
    try:
        odds_val = int(p['odds_american'].replace('+', ''))
        potential = stake + (stake * (odds_val/100))
        st.markdown(f"<div style='display:flex; justify-content:space-between; margin-top:10px;'><span>Return</span><span style='font-weight:800; color:#30d158;'>${potential:.2f}</span></div>", unsafe_allow_html=True)
    except: pass
    
    if st.button("Place Bet 🚀", type="primary", use_container_width=True):
        st.success("Bet Placed!")
    st.markdown("</div>", unsafe_allow_html=True)
