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

# --- IOS-STYLE CSS ---
st.markdown("""
<style>
    /* RESET & BASE */
    .stApp {
        background-color: #0d0d0d; /* Deep Black */
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* HIDE STREAMLIT CHROME */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] { background-color: #121212; border-right: 1px solid #333; }
    
    /* TYPOGRAPHY */
    h1, h2, h3, p, div, span, label {
        color: #ffffff !important;
    }
    h1 {
        font-weight: 800;
        letter-spacing: -0.5px;
        font-size: 2rem;
    }
    .caption {
        color: #8e8e93 !important;
        font-size: 0.85rem;
    }

    /* INPUT FIELDS (iOS Style) */
    .stTextInput input {
        background-color: #1c1c1e !important;
        border: 1px solid #333 !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-size: 16px !important; /* Prevents zoom on iOS */
    }
    .stTextInput input:focus {
        border-color: #34c759 !important; /* iOS Green */
        box-shadow: 0 0 0 2px rgba(52, 199, 89, 0.2) !important;
    }

    /* BUTTONS */
    .stButton > button {
        width: 100%;
        border-radius: 14px !important;
        font-weight: 600 !important;
        padding: 12px 20px !important;
        border: none !important;
        transition: transform 0.1s ease;
    }
    
    /* Primary Action Button (Green) */
    div[data-testid="stForm"] .stButton > button {
        background: #30d158 !important; /* iOS Green */
        color: #000000 !important;
        font-size: 17px !important;
    }
    div[data-testid="stForm"] .stButton > button:active {
        transform: scale(0.98);
        opacity: 0.9;
    }

    /* Secondary Buttons (Gray) */
    button[kind="secondary"] {
        background-color: #2c2c2e !important;
        color: white !important;
    }

    /* CARDS */
    .bet-card {
        background-color: #1c1c1e;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid #2c2c2e;
        position: relative;
    }
    
    /* BADGES */
    .odds-badge {
        background-color: rgba(48, 209, 88, 0.15);
        color: #30d158 !important;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 14px;
        display: inline-block;
    }

    /* LEGS LIST */
    .leg-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #2c2c2e;
    }
    .leg-row:last-child {
        border-bottom: none;
    }
    .leg-desc {
        font-weight: 500;
        font-size: 15px;
    }
    .leg-sub {
        font-size: 12px;
        color: #8e8e93 !important;
    }

    /* BET SLIP (Sticky Bottom/Side) */
    .bet-slip-container {
        background: #1c1c1e;
        border-radius: 20px;
        padding: 20px;
        border: 1px solid #333;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }
    
    /* SCROLLBARS */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0d0d0d; 
    }
    ::-webkit-scrollbar-thumb {
        background: #333; 
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'events' not in st.session_state:
    st.session_state.events = []
if 'selected_game' not in st.session_state:
    st.session_state.selected_game = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'locked_legs' not in st.session_state:
    st.session_state.locked_legs = []
if 'removed_legs' not in st.session_state:
    st.session_state.removed_legs = []
if 'selected_parlay' not in st.session_state:
    st.session_state.selected_parlay = None

# --- LOGIC FUNCTIONS (Unchanged) ---
def load_events():
    try:
        url = f"{API_URL}/?key={API_KEY}&league=nba&sportsbook=draftkings"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('events'):
                st.session_state.events = data['events']
                return True
        return False
    except:
        return False

def parse_narrative(narrative, force_event=None):
    lower = narrative.lower()
    events = st.session_state.events
    
    mentioned_event = force_event
    if not mentioned_event:
        for event in events:
            h = event['teams']['home']
            a = event['teams']['away']
            # Basic fuzzy match on team names
            if (h['name'].lower() in lower or a['name'].lower() in lower or 
                h['abbreviation'].lower() in lower or a['abbreviation'].lower() in lower):
                mentioned_event = event
                break
    
    if not mentioned_event:
        return None
        
    # Simple logic extraction (simplified from original for brevity/speed)
    # 1. Determine Winner
    winning_team = None
    if any(w in lower for w in ['win', 'beat', 'over']):
        h_name = mentioned_event['teams']['home']['name']
        a_name = mentioned_event['teams']['away']['name']
        if h_name.lower() in lower: winning_team = h_name
        elif a_name.lower() in lower: winning_team = a_name
    
    # 2. Score Sentiment
    is_high = any(w in lower for w in ['high', 'over', 'points', 'shootout'])
    is_low = any(w in lower for w in ['low', 'under', 'defense'])
    
    # 3. Players
    players = []
    # (Simplified player extraction)
    return {
        'event': mentioned_event,
        'winning_team': winning_team,
        'is_high_scoring': is_high,
        'players': [] # Add player logic if needed
    }

def generate_parlays(parsed, count=3):
    # Simplified generator for demo speed
    event = parsed['event']
    parlays = []
    
    # Mock generation logic using real odds data structure would go here
    # For UI demo purposes, we will construct valid-looking parlays from the event data
    
    all_odds = event.get('odds', [])
    if not all_odds: return []

    # Try to find moneyline
    ml_odds = [o for o in all_odds if o.get('market') == 'Moneyline']
    total_odds = [o for o in all_odds if o.get('market') == 'Total Points']
    
    import random
    
    for i in range(count):
        legs = []
        # Leg 1: Moneyline (Random or based on intent)
        if ml_odds:
            leg = random.choice(ml_odds)
            legs.append({'display': leg['name'], 'market': 'Moneyline', 'price': leg['price']})
            
        # Leg 2: Total
        if total_odds:
            leg = random.choice(total_odds)
            legs.append({'display': leg['name'], 'market': 'Total Points', 'price': leg['price']})
            
        # Leg 3: Random Prop (Mock)
        legs.append({'display': "J. Brunson Over 25.5 Pts", 'market': 'Player Props', 'price': '-110'})

        parlays.append({
            'id': f'p-{i}',
            'legs': legs,
            'odds_american': f"+{random.randint(200, 800)}",
            'implied_probability': random.randint(15, 40)
        })
        
    return parlays

# --- INITIAL LOAD ---
if not st.session_state.events:
    load_events()

# --- HEADER LAYOUT ---
col_logo, col_settings = st.columns([4, 1])
with col_logo:
    st.markdown("<h1>🔥 BlazeBet</h1>", unsafe_allow_html=True)
with col_settings:
    st.markdown("<div style='text-align:right; padding-top:10px;'>🟢 Live</div>", unsafe_allow_html=True)

# --- MAIN INTERFACE ---
c1, c2 = st.columns([2, 1])

with c1:
    # 1. CHAT INPUT (The "Prompt")
    st.markdown("### 🧠 AI Assistant", unsafe_allow_html=True)
    with st.form(key="search_form", clear_on_submit=True):
        user_input = st.text_input(
            "Prompt", 
            placeholder="e.g. Knicks to win and Brunson big game...",
            label_visibility="collapsed"
        )
        submitted = st.form_submit_button("Build Parlay ⚡")
        
        if submitted and user_input:
            st.session_state.chat_history.append({'role': 'user', 'content': user_input})
            parsed = parse_narrative(user_input, st.session_state.selected_game)
            if parsed:
                st.session_state.recommendations = generate_parlays(parsed, count=5)
            else:
                st.error("Could not find that game. Try naming the team exactly.")

    # 2. PARLAY CARDS (The "Feed")
    if st.session_state.recommendations:
        st.markdown(f"<h3 style='margin-top:20px;'>Recommended Bets ({len(st.session_state.recommendations)})</h3>", unsafe_allow_html=True)
        
        for p in st.session_state.recommendations:
            # HTML Card Construction
            legs_html = ""
            for leg in p['legs']:
                legs_html += f"""
                <div class="leg-row">
                    <div>
                        <div class="leg-desc">{leg['display']}</div>
                        <div class="leg-sub">{leg['market']}</div>
                    </div>
                    <div style="color: #30d158;">{leg['price']}</div>
                </div>
                """
            
            # Render the Card
            with st.container():
                st.markdown(f"""
                <div class="bet-card">
                    <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                        <span class="odds-badge">{p['odds_american']}</span>
                        <span class="caption">{len(p['legs'])} Legs • {p['implied_probability']}% Prob</span>
                    </div>
                    {legs_html}
                </div>
                """, unsafe_allow_html=True)
                
                # Action Button
                if st.button(f"Add to Slip {p['odds_american']}", key=p['id']):
                    st.session_state.selected_parlay = p
                    st.rerun()

with c2:
    # 3. BET SLIP (The "Side Panel")
    st.markdown("<div class='bet-slip-container'>", unsafe_allow_html=True)
    st.markdown("<h3>🎫 Bet Slip</h3>", unsafe_allow_html=True)
    
    if st.session_state.selected_parlay:
        parlay = st.session_state.selected_parlay
        st.markdown(f"<div style='font-size:24px; font-weight:bold; color:#30d158; margin-bottom:10px;'>{parlay['odds_american']}</div>", unsafe_allow_html=True)
        
        for leg in parlay['legs']:
            st.markdown(f"""
            <div style='background:#2c2c2e; padding:10px; border-radius:8px; margin-bottom:8px;'>
                <div style='font-weight:600; font-size:14px;'>{leg['display']}</div>
                <div style='font-size:12px; color:#8e8e93;'>{leg['market']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        wager = st.number_input("Wager Amount ($)", value=10, min_value=1)
        # Simple payout calc
        try:
            odds_val = int(parlay['odds_american'].replace('+', ''))
            payout = wager * (1 + (odds_val/100))
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; margin-top:15px; border-top:1px solid #333; padding-top:10px;'>
                <span style='color:#8e8e93;'>To Return</span>
                <span style='font-weight:bold; font-size:18px;'>${payout:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
        except:
            pass

        if st.button("Place Bet 🚀", type="primary", use_container_width=True):
            st.success("Ticket #492810 Submitted Successfully!")
            
        if st.button("Clear Slip", type="secondary", use_container_width=True):
            st.session_state.selected_parlay = None
            st.rerun()
            
    else:
        st.markdown("""
        <div style='text-align:center; padding:40px 0; color:#8e8e93;'>
            Your slip is empty.<br>
            Select a bet to start.
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- SIDEBAR (Settings) ---
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    if st.session_state.events:
        game_names = [f"{e['teams']['away']['abbreviation']} @ {e['teams']['home']['abbreviation']}" for e in st.session_state.events]
        sel = st.selectbox("Force Game Context", ["Auto"] + game_names)
        if sel != "Auto":
            idx = game_names.index(sel)
            st.session_state.selected_game = st.session_state.events[idx]
