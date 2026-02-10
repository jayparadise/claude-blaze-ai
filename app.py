import streamlit as st
import requests
import json
from datetime import datetime
import random

# Page configuration
st.set_page_config(
    page_title="AI Parlay Builder",
    page_icon="🎰",
    layout="wide"
)

# API Configuration
API_KEY = '10019992-c9b1-46b5-be2c-9e760b1c2041'
API_URL = 'https://odds.oddsblaze.com'

# --- CUSTOM CSS: iOS Style & Horizontal Carousel ---
st.markdown("""
<style>
    /* 1. Global iOS Theme */
    .stApp {
        background-color: #F2F2F7; /* Apple System Gray 6 */
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    #MainMenu, header, footer {visibility: hidden;}
    .block-container { padding-top: 2rem; padding-bottom: 5rem; }

    /* 2. Horizontal Carousel Logic */
    /* This invisible marker triggers the CSS on the following horizontal block */
    .carousel-marker { display: none; }
    
    /* Target the horizontal block immediately following the marker */
    .carousel-marker + div[data-testid="stHorizontalBlock"] {
        display: flex;
        flex-wrap: nowrap; /* Force single row */
        overflow-x: auto; /* Enable scrolling */
        gap: 16px; /* Gap between cards */
        padding-bottom: 20px; /* Space for scrollbar */
        padding-right: 20px;
        mask-image: linear-gradient(to right, black 95%, transparent 100%);
        -webkit-mask-image: linear-gradient(to right, black 95%, transparent 100%);
        align-items: stretch;
    }
    
    /* Target the columns (cards) inside the carousel */
    .carousel-marker + div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        flex: 0 0 auto !important; /* Prevent shrinking */
        width: 320px !important; /* Fixed width for standard mobile card feel */
        min-width: 320px !important;
        max-width: 320px !important;
    }

    /* 3. Card Styling */
    .parlay-card {
        background: white;
        border-radius: 20px;
        padding: 1.2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        border: 1px solid rgba(0,0,0,0.04);
        height: 100%;
        display: flex;
        flex-direction: column;
        position: relative;
    }

    /* 4. Buttons (Pill Shape) */
    .stButton > button {
        border-radius: 20px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        transition: transform 0.1s ease;
    }
    /* Primary Action Button */
    div[data-testid="stForm"] .stButton > button {
        background-color: #34C759 !important; /* iOS Green */
        color: white !important;
        height: 45px;
    }
    
    /* 5. Bet Slip (Floating Side Panel) */
    .bet-slip {
        background: white;
        border-radius: 24px;
        padding: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.12);
        border: 1px solid #E5E5EA;
        position: sticky;
        top: 2rem;
        animation: slideIn 0.3s ease-out;
    }
    @keyframes slideIn {
        from { transform: translateX(20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    /* 6. Typography & Elements */
    h1, h2, h3 { color: #000; letter-spacing: -0.5px; }
    .odds-badge {
        background-color: #34C759;
        color: white;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 800;
        font-size: 1.1rem;
    }
    .leg-item {
        background-color: #F9F9F9;
        border-radius: 12px;
        padding: 10px;
        margin: 8px 0;
        border-left: 4px solid #007AFF;
    }
    .locked-leg { border-left-color: #FF9500; background-color: #FFF8E1; }
    .removed-leg { border-left-color: #FF3B30; opacity: 0.5; }
    
    /* Inputs */
    .stTextInput input, .stNumberInput input {
        border-radius: 12px;
        border: 1px solid #E5E5EA;
        padding: 10px;
    }
    .caption { color: #8E8E93; font-size: 0.8rem; }
    hr { margin: 10px 0; border-color: #E5E5EA; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
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
            st.error("No games available")
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
    
    # Use forced event if provided (from game selector)
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
        
        if home_name.lower() in lower:
            winning_team = home_name
        elif away_name.lower() in lower:
            winning_team = away_name
            
    is_high_scoring = any(word in lower for word in ['high scoring', 'lots of points', 'shootout', 'offensive', 'over'])
    is_low_scoring = any(word in lower for word in ['low scoring', 'defensive', 'grind', 'under'])
    is_blowout = any(word in lower for word in ['blowout', 'dominate'])
    
    players = []
    for odd in mentioned_event.get('odds', []):
        if odd.get('player') and isinstance(odd.get('player'), str):
            try:
                player_name = odd['player'].lower()
                if player_name in lower or any(p in lower for p in player_name.split()):
                    has_positive = any(word in lower for word in ['score', 'big game', 'lots', 'great'])
                    players.append({
                        'name': odd['player'],
                        'sentiment': 'positive' if has_positive else 'neutral'
                    })
            except: continue
    
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
        is_low_scoring = parsed_data['is_low_scoring']
        is_blowout = parsed_data['is_blowout']
        players = parsed_data['players']
        
        locked_legs = locked_legs or []
        removed_legs = removed_legs or []
        removed_ids = {leg['id'] for leg in removed_legs}
        
        parlays = []
        all_odds = event.get('odds', [])
        valid_odds = [o for o in all_odds if o.get('id') and o.get('market') and o.get('price') and o['id'] not in removed_ids]
        
        min_legs, max_legs = num_legs_range
        min_odds, max_odds = odds_range
        
        for i in range(count * 3):
            legs = list(locked_legs)
            used_ids = {leg['id'] for leg in locked_legs}
            target_legs = random.randint(min_legs, max_legs)
            
            # Logic to build legs
            if winning_team:
                ml = next((o for o in valid_odds if o.get('market') == 'Moneyline' and o.get('name') == winning_team), None)
                if ml and ml['id'] not in used_ids:
                    legs.append({**ml, 'display': ml['name']})
                    used_ids.add(ml['id'])
            
            if is_high_scoring or is_low_scoring:
                side = 'Over' if is_high_scoring else 'Under'
                totals = [o for o in valid_odds if o.get('market') == 'Total Points' and side in o.get('name', '')]
                if totals and totals[0]['id'] not in used_ids:
                    legs.append({**totals[0], 'display': totals[0]['name']})
                    used_ids.add(totals[0]['id'])
            
            for player in players:
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
                
            if len(legs) >= 2:
                # Mock Odds for demo visualization (replace with real calculation if available)
                parlays.append({
                    'id': f'parlay-{i}',
                    'legs': legs,
                    'event_id': event['id'],
                    'odds_american': f"+{random.randint(150, 900)}",
                    'implied_probability': random.randint(10, 45)
                })
                if len(parlays) >= count: break
        return parlays
    except: return []

def calculate_payout(odds_str, amount):
    try:
        if odds_str.startswith('+'): return amount * (int(odds_str[1:]) / 100)
        else: return amount * (100 / int(odds_str[1:]))
    except: return 0

# Header
st.markdown("<h1 style='margin-bottom: 5px;'>🔥 BlazeBet AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #8E8E93; margin-top: 0;'>Build your perfect same-game parlay</p>", unsafe_allow_html=True)

if not st.session_state.events:
    load_events()

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    # 1. Chat Input
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input("input", placeholder="Describe your parlay (e.g. Knicks win big...)", label_visibility="collapsed")
        submit = st.form_submit_button("Generate Parlays ⚡", use_container_width=True)
        
        if submit and user_input:
            st.session_state.chat_history.append({'role': 'user', 'content': user_input})
            parsed = parse_narrative(user_input, force_event=st.session_state.selected_game)
            if parsed:
                st.session_state.recommendations = generate_parlays(parsed, 10, locked_legs=st.session_state.locked_legs, removed_legs=st.session_state.removed_legs)
                st.rerun()
            else:
                st.error("Could not find a matching game.")

    # 2. Horizontal Carousel of Cards
    if st.session_state.recommendations:
        col_title, col_regen = st.columns([3, 1])
        with col_title: st.markdown(f"### Top Picks ({len(st.session_state.recommendations)})")
        with col_regen: 
            if st.button("🔄 Regenerate", use_container_width=True): st.rerun()

        # START CAROUSEL MARKER
        st.markdown('<div class="carousel-marker"></div>', unsafe_allow_html=True)
        
        cols = st.columns(len(st.session_state.recommendations))
        for idx, parlay in enumerate(st.session_state.recommendations):
            with cols[idx]:
                # Start Card Wrapper
                st.markdown("<div class='parlay-card'>", unsafe_allow_html=True)
                
                # Header
                st.markdown(f"""
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;'>
                    <span class='odds-badge'>{parlay['odds_american']}</span>
                    <span class='caption'>{len(parlay['legs'])} Legs</span>
                </div>
                <hr>
                """, unsafe_allow_html=True)
                
                # Legs Loop
                for i, leg in enumerate(parlay['legs']):
                    is_locked = any(l['id'] == leg['id'] for l in st.session_state.locked_legs)
                    is_removed = any(l['id'] == leg['id'] for l in st.session_state.removed_legs)
                    leg_class = 'locked-leg' if is_locked else ('removed-leg' if is_removed else 'leg-item')
                    
                    st.markdown(f"""
                    <div class='{leg_class}'>
                        <div style='font-weight:600; font-size:0.9rem;'>{leg['display']}</div>
                        <div style='font-size:0.8rem; color:#8E8E93;'>{leg['market']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Mini Action Buttons
                    b_cols = st.columns([1, 1])
                    with b_cols[0]:
                        if st.button("🔒" if is_locked else "🔓", key=f"lock_{parlay['id']}_{i}"):
                            if is_locked: st.session_state.locked_legs = [l for l in st.session_state.locked_legs if l['id'] != leg['id']]
                            else: st.session_state.locked_legs.append(leg)
                            st.rerun()
                    with b_cols[1]:
                        if st.button("❌", key=f"rem_{parlay['id']}_{i}"):
                            st.session_state.removed_legs.append(leg)
                            st.rerun()

                st.markdown("<div style='margin-top:auto;'></div>", unsafe_allow_html=True)
                if st.button("Add to Slip", key=f"add_{parlay['id']}", use_container_width=True):
                    st.session_state.selected_parlay = parlay
                    st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True) # End Card

with col2:
    # 3. Floating Bet Slip (Hidden until selected)
    if st.session_state.selected_parlay:
        st.markdown("<div class='bet-slip'>", unsafe_allow_html=True)
        
        # Header
        h_cols = st.columns([3, 1])
        with h_cols[0]: st.markdown("<h3 style='margin:0;'>🎫 Slip</h3>", unsafe_allow_html=True)
        with h_cols[1]: 
            if st.button("✕", key="close_slip"): 
                st.session_state.selected_parlay = None
                st.rerun()
        
        parlay = st.session_state.selected_parlay
        st.markdown(f"<h1 style='color:#34C759; margin:10px 0;'>{parlay['odds_american']}</h1>", unsafe_allow_html=True)
        
        for leg in parlay['legs']:
            st.markdown(f"""
            <div style='padding:8px 0; border-bottom:1px solid #E5E5EA;'>
                <div style='font-weight:600;'>{leg['display']}</div>
                <div style='font-size:0.8rem; color:#8E8E93;'>{leg['market']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        stake = st.number_input("Wager ($)", value=10.0, step=5.0)
        payout = calculate_payout(parlay['odds_american'], stake)
        
        st.markdown(f"""
        <div style='background:#F2F2F7; padding:15px; border-radius:12px; margin-top:15px;'>
            <div style='display:flex; justify-content:space-between; margin-bottom:5px; color:#8E8E93;'><span>Wager</span><span>${stake:.2f}</span></div>
            <div style='display:flex; justify-content:space-between; font-weight:bold; font-size:1.1rem;'><span>Win</span><span style='color:#34C759'>${payout:.2f}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Place Bet 🚀", type="primary", use_container_width=True):
            st.balloons()
            
        st.markdown("</div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Settings")
    if st.session_state.events:
        game_options = ["Auto-detect"] + [f"{e['teams']['away']['abbreviation']} @ {e['teams']['home']['abbreviation']}" for e in st.session_state.events]
        selected_idx = st.selectbox("Game", range(len(game_options)), format_func=lambda x: game_options[x])
        st.session_state.selected_game = st.session_state.events[selected_idx - 1] if selected_idx > 0 else None
    
    st.markdown("---")
    st.session_state.num_legs_filter = st.slider("Legs", 2, 6, (3, 5))
    st.session_state.odds_range_filter = st.slider("Odds", 1.2, 100.0, (1.2, 50.0))
    
    if st.button("Clear Locks"):
        st.session_state.locked_legs = []
        st.session_state.removed_legs = []
        st.rerun()
