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

# --- API CONFIGURATION (EXACTLY AS PROVIDED) ---
API_KEY = '10019992-c9b1-46b5-be2c-9e760b1c2041'
API_URL = 'https://odds.oddsblaze.com'

# --- PREMIUM iOS/DARK CSS ---
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
        font-size: 16px !important;
    }
    .stTextInput input:focus {
        border-color: #30d158 !important; /* iOS Green */
        box-shadow: 0 0 0 2px rgba(48, 209, 88, 0.2) !important;
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
        background: #30d158 !important;
        color: #000000 !important;
        font-size: 17px !important;
    }
    div[data-testid="stForm"] .stButton > button:hover {
        background: #2db84c !important;
        transform: scale(1.02);
    }

    /* Secondary/Utility Buttons */
    button[kind="secondary"] {
        background-color: #2c2c2e !important;
        color: white !important;
        border: 1px solid #3a3a3c !important;
    }

    /* CARDS */
    .bet-card {
        background-color: #1c1c1e;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid #2c2c2e;
        transition: transform 0.2s;
    }
    .bet-card:hover {
        transform: translateY(-2px);
        border-color: #3a3a3c;
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

    /* BET SLIP */
    .bet-slip-container {
        background: #1c1c1e;
        border-radius: 20px;
        padding: 20px;
        border: 1px solid #333;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        position: sticky;
        top: 20px;
    }

    /* LEG ACTIONS */
    .leg-actions button {
        padding: 4px 8px !important;
        font-size: 12px !important;
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
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
if 'bet_amount' not in st.session_state:
    st.session_state.bet_amount = 10.0
if 'num_legs_filter' not in st.session_state:
    st.session_state.num_legs_filter = (3, 5)
if 'odds_range_filter' not in st.session_state:
    st.session_state.odds_range_filter = (1.2, 100.0)

# --- BACKEND LOGIC (EXACTLY AS PROVIDED) ---
def load_events():
    """Load NBA games from OddsBlaze API"""
    try:
        url = f"{API_URL}/?key={API_KEY}&league=nba&sportsbook=draftkings"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            st.error(f"API Error: {response.status_code}")
            return False
        
        data = response.json()
        
        if not data.get('events') or len(data['events']) == 0:
            # Silent fail for UI purposes, or show subtle error
            return False
        
        st.session_state.events = data['events']
        return True
        
    except Exception as e:
        st.error(f"Error loading games: {str(e)}")
        return False

def parse_narrative(narrative, force_event=None):
    """Parse user narrative to understand betting intent"""
    lower = narrative.lower()
    events = st.session_state.events
    
    if force_event:
        mentioned_event = force_event
    else:
        mentioned_event = None
        for event in events:
            home_name = event['teams']['home']['name'].lower()
            away_name = event['teams']['away']['name'].lower()
            home_abbrev = event['teams']['home']['abbreviation'].lower()
            away_abbrev = event['teams']['away']['abbreviation'].lower()
            
            home_words = home_name.split()
            away_words = away_name.split()
            
            if (home_name in lower or away_name in lower or 
                home_abbrev in lower or away_abbrev in lower or
                any(word in lower for word in home_words if len(word) > 3) or
                any(word in lower for word in away_words if len(word) > 3)):
                mentioned_event = event
                break
    
    if not mentioned_event:
        return None
    
    winning_team = None
    win_words = ['win', 'beat', 'dominate', 'destroy', 'crush']
    has_win = any(word in lower for word in win_words)
    
    if has_win:
        home_name = mentioned_event['teams']['home']['name']
        away_name = mentioned_event['teams']['away']['name']
        home_name_lower = home_name.lower()
        away_name_lower = away_name.lower()
        
        home_mentioned = home_name_lower in lower
        away_mentioned = away_name_lower in lower
        
        if home_mentioned and not away_mentioned:
            winning_team = home_name
        elif away_mentioned and not home_mentioned:
            winning_team = away_name
            
    is_high_scoring = any(word in lower for word in ['high scoring', 'lots of points', 'shootout', 'offensive', 'over'])
    is_low_scoring = any(word in lower for word in ['low scoring', 'defensive', 'grind', 'under'])
    is_blowout = any(word in lower for word in ['blowout', 'dominate', 'destroy', 'crush'])
    
    players = []
    for odd in mentioned_event.get('odds', []):
        if odd.get('player') and isinstance(odd.get('player'), str):
            try:
                player_name = odd['player'].lower()
                player_parts = player_name.split()
                if any(part in lower for part in player_parts) or player_name in lower:
                    has_positive = any(word in lower for word in ['score', 'big game', 'lots', 'great'])
                    players.append({
                        'name': odd['player'],
                        'sentiment': 'positive' if has_positive else 'neutral'
                    })
            except:
                continue
    
    unique_players = {p['name']: p for p in players}.values()
    
    return {
        'event': mentioned_event,
        'winning_team': winning_team,
        'is_high_scoring': is_high_scoring,
        'is_low_scoring': is_low_scoring,
        'is_blowout': is_blowout,
        'players': list(unique_players)
    }

def generate_parlays(parsed_data, count=10, locked_legs=None, removed_legs=None, num_legs_range=(3, 5), odds_range=(1.2, 100.0)):
    """Generate parlay combinations based on parsed narrative"""
    try:
        event = parsed_data['event']
        winning_team = parsed_data['winning_team']
        is_high_scoring = parsed_data['is_high_scoring']
        players = parsed_data['players']
        is_blowout = parsed_data['is_blowout']
        
        locked_legs = locked_legs or []
        removed_legs = removed_legs or []
        removed_ids = {leg['id'] for leg in removed_legs}
        
        parlays = []
        all_odds = event.get('odds', [])
        
        valid_odds = [o for o in all_odds 
                     if o.get('id') and o.get('market') and o.get('name') and o.get('price')
                     and o['id'] not in removed_ids]
        
        min_legs, max_legs = num_legs_range
        min_odds, max_odds = odds_range
        
        import random
        
        for i in range(count * 5): 
            legs = list(locked_legs)
            used_ids = {leg['id'] for leg in locked_legs}
            
            target_legs = random.randint(min_legs, max_legs)
            
            if winning_team and len(legs) < target_legs:
                ml = next((o for o in valid_odds if o.get('market') == 'Moneyline' and o.get('name') == winning_team), None)
                if ml and ml['id'] not in used_ids:
                    legs.append({**ml, 'display': ml['name']})
                    used_ids.add(ml['id'])
            
            if (is_high_scoring) and len(legs) < target_legs:
                totals = [o for o in valid_odds if o.get('market') == 'Total Points' and 'Over' in o.get('name', '')]
                if totals and totals[0]['id'] not in used_ids:
                    legs.append({**totals[0], 'display': totals[0]['name']})
                    used_ids.add(totals[0]['id'])
            
            for player in players:
                if len(legs) >= target_legs: break
                player_odds = [o for o in valid_odds if o.get('player') == player['name']]
                for odd in player_odds:
                    if odd['id'] not in used_ids:
                        legs.append({**odd, 'display': odd['name']})
                        used_ids.add(odd['id'])
                        break

            # Fill random
            available = [o for o in valid_odds if o['id'] not in used_ids and o.get('market') != 'Moneyline']
            while len(legs) < target_legs and available:
                odd = random.choice(available)
                legs.append({**odd, 'display': odd['name']})
                used_ids.add(odd['id'])
                available = [o for o in available if o['id'] != odd['id']]
            
            if min_legs <= len(legs) <= max_legs:
                decimal_odds = 1
                for leg in legs:
                    price = leg.get('price', '+100')
                    try:
                        if price.startswith('+'):
                            decimal_odds *= (int(price[1:]) / 100) + 1
                        else:
                            decimal_odds *= (100 / int(price[1:])) + 1
                    except: continue
                
                if not (min_odds <= decimal_odds <= max_odds):
                    continue
                
                american_odds = f"+{int((decimal_odds - 1) * 100)}" if decimal_odds >= 2 else f"-{int(100 / (decimal_odds - 1))}"
                implied_prob = round(1 / decimal_odds * 100, 1)
                
                parlays.append({
                    'id': f'parlay-{i}',
                    'legs': legs,
                    'event_id': event['id'],
                    'odds_american': american_odds,
                    'implied_probability': implied_prob,
                    'decimal_odds': decimal_odds
                })
                
                if len(parlays) >= count:
                    break
        
        return parlays
    except Exception as e:
        return []

def calculate_payout(odds_str, amount):
    try:
        if odds_str.startswith('+'):
            return amount * (int(odds_str[1:]) / 100)
        else:
            return amount * (100 / int(odds_str[1:]))
    except:
        return 0

# --- APP LAYOUT ---

# Load Data
if not st.session_state.events:
    load_events()

# Top Bar
col_logo, col_status = st.columns([4, 1])
with col_logo:
    st.markdown("<h1>🔥 BlazeBet</h1>", unsafe_allow_html=True)
with col_status:
    if st.session_state.events:
        st.markdown("<div style='text-align:right; color:#30d158; padding-top:15px; font-weight:600;'>● Live Feed</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:right; color:#ff453a; padding-top:15px; font-weight:600;'>● Offline</div>", unsafe_allow_html=True)

# Main Grid
c1, c2 = st.columns([2, 1])

with c1:
    # 1. Chat Interface
    st.markdown("### 🧠 AI Assistant")
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input(
            "Prompt", 
            placeholder="e.g. Knicks win big, Brunson 30+ points...",
            label_visibility="collapsed"
        )
        submit = st.form_submit_button("Generate Parlay ⚡")
        
        if submit and user_input:
            st.session_state.chat_history.append({'role': 'user', 'content': user_input})
            
            # CALLING THE WORKING LOGIC
            parsed = parse_narrative(user_input, force_event=st.session_state.selected_game)
            
            if not parsed:
                st.error("❌ Could not identify the game. Mention the team name clearly.")
            else:
                parlays = generate_parlays(
                    parsed, 
                    10,
                    locked_legs=st.session_state.locked_legs,
                    removed_legs=st.session_state.removed_legs,
                    num_legs_range=st.session_state.num_legs_filter,
                    odds_range=st.session_state.odds_range_filter
                )
                st.session_state.recommendations = parlays
                st.rerun()

    # 2. Results Feed
    if st.session_state.recommendations:
        st.markdown(f"<h3 style='margin-top:20px;'>Recommended Bets ({len(st.session_state.recommendations)})</h3>", unsafe_allow_html=True)
        
        for parlay in st.session_state.recommendations:
            # Generate HTML for legs
            legs_html = ""
            for leg in parlay['legs']:
                legs_html += f"""
                <div class="leg-row">
                    <div>
                        <div class="leg-desc">{leg['display']}</div>
                        <div class="leg-sub">{leg['market']}</div>
                    </div>
                    <div style="color: #30d158; font-weight:600;">{leg['price']}</div>
                </div>
                """
            
            # Card Container
            with st.container():
                st.markdown(f"""
                <div class="bet-card">
                    <div style="display:flex; justify-content:space-between; margin-bottom:12px; align-items:center;">
                        <span class="odds-badge">{parlay['odds_american']}</span>
                        <span class="caption">{len(parlay['legs'])} Legs • {parlay['implied_probability']}% Prob</span>
                    </div>
                    {legs_html}
                </div>
                """, unsafe_allow_html=True)
                
                # Selection Logic
                col_btn, col_acts = st.columns([1, 4])
                with col_btn:
                    if st.button(f"Select", key=f"btn_{parlay['id']}"):
                        st.session_state.selected_parlay = parlay
                        st.rerun()

with c2:
    # 3. Sticky Bet Slip
    st.markdown("<div class='bet-slip-container'>", unsafe_allow_html=True)
    st.markdown("<h3>🎫 Bet Slip</h3>", unsafe_allow_html=True)
    
    if st.session_state.selected_parlay:
        parlay = st.session_state.selected_parlay
        
        st.markdown(f"""
        <div style="margin-bottom:15px; border-bottom:1px solid #333; padding-bottom:10px;">
            <div style="font-size:2rem; font-weight:800; color:#30d158;">{parlay['odds_american']}</div>
            <div class="caption">Combined Odds</div>
        </div>
        """, unsafe_allow_html=True)

        for leg in parlay['legs']:
            st.markdown(f"""
            <div style="background:#2c2c2e; padding:10px; border-radius:8px; margin-bottom:8px;">
                <div style="font-weight:600;">{leg['display']}</div>
                <div style="font-size:12px; color:#8e8e93;">{leg['market']} • {leg['price']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        wager = st.number_input("Wager", value=10.0, step=5.0, min_value=1.0)
        profit = calculate_payout(parlay['odds_american'], wager)
        total_ret = wager + profit
        
        st.markdown(f"""
        <div style="margin-top:15px; background:#2c2c2e; padding:15px; border-radius:12px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                <span style="color:#8e8e93">Wager</span>
                <span>${wager:.2f}</span>
            </div>
            <div style="display:flex; justify-content:space-between; font-weight:bold;">
                <span style="color:#30d158">To Return</span>
                <span style="color:#30d158; font-size:1.2rem;">${total_ret:.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Place Bet 🚀", type="primary"):
            st.balloons()
            st.success("Bet Placed Successfully!")
            
        if st.button("Clear Slip", type="secondary"):
            st.session_state.selected_parlay = None
            st.rerun()
            
    else:
        st.markdown("""
        <div style="text-align:center; padding:40px 0; color:#636366;">
            Your slip is empty.<br>
            Select a recommended parlay to populate.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # Logic from original file to filter games
    if st.session_state.events:
        game_options = ["Auto-detect"] + [
            f"{e['teams']['away']['abbreviation']} @ {e['teams']['home']['abbreviation']}" 
            for e in st.session_state.events
        ]
        
        sel_idx = st.selectbox("Force Game Context", range(len(game_options)), format_func=lambda x: game_options[x])
        
        if sel_idx == 0:
            st.session_state.selected_game = None
        else:
            st.session_state.selected_game = st.session_state.events[sel_idx - 1]
    
    st.markdown("---")
    st.caption("Filters")
    legs_sel = st.slider("Legs", 2, 6, (3, 5))
    st.session_state.num_legs_filter = legs_sel
    
    if st.button("Reload Data"):
        st.session_state.events = []
        load_events()
        st.rerun()
