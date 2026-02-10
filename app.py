import streamlit as st
import requests
import json
from datetime import datetime

# Page config
st.set_page_config(page_title="Parlay Builder", page_icon="🎰", layout="wide")

# API Configuration
API_KEY = '10019992-c9b1-46b5-be2c-9e760b1c2041'
API_URL = 'https://odds.oddsblaze.com'

# Session state
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
if 'num_legs_filter' not in st.session_state:
    st.session_state.num_legs_filter = (3, 5)
if 'odds_range_filter' not in st.session_state:
    st.session_state.odds_range_filter = (1.5, 50.0)

def load_events():
    """Load NBA events from API"""
    try:
        url = f"{API_URL}/nba/odds"
        headers = {'X-API-Key': API_KEY}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.events = data.get('events', [])
        else:
            st.error(f"Failed to load games: {response.status_code}")
    except Exception as e:
        st.error(f"Error loading games: {str(e)}")

def parse_narrative(narrative, force_event=None):
    """Parse user narrative to identify game and constraints"""
    if force_event:
        return {
            'event': force_event,
            'narrative': narrative
        }
    
    # Simple team name matching
    narrative_lower = narrative.lower()
    for event in st.session_state.events:
        away = event['teams']['away']['name'].lower()
        home = event['teams']['home']['name'].lower()
        
        if away in narrative_lower or home in narrative_lower:
            return {
                'event': event,
                'narrative': narrative
            }
    
    return None

def generate_parlays(parsed_data, num_parlays=10, locked_legs=[], removed_legs=[], num_legs_range=(3, 5), odds_range=(1.5, 50.0)):
    """Generate parlay combinations"""
    event = parsed_data['event']
    
    try:
        # Get markets
        url = f"{API_URL}/nba/odds/{event['id']}"
        headers = {'X-API-Key': API_KEY}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        markets = data.get('markets', [])
        
        # Build available legs
        all_legs = []
        removed_ids = [leg['id'] for leg in removed_legs]
        
        for market in markets:
            for selection in market.get('selections', []):
                leg_id = f"{market['key']}_{selection['name']}"
                
                if leg_id in removed_ids:
                    continue
                
                all_legs.append({
                    'id': leg_id,
                    'display': selection['name'],
                    'market': market['name'],
                    'price': selection['price'],
                    'odds': selection.get('american_odds', '+100')
                })
        
        # Generate parlays
        import random
        parlays = []
        locked_leg_ids = [leg['id'] for leg in locked_legs]
        
        for i in range(num_parlays):
            num_legs = random.randint(num_legs_range[0], num_legs_range[1])
            
            # Start with locked legs
            parlay_legs = locked_legs.copy()
            
            # Add random legs
            available = [leg for leg in all_legs if leg['id'] not in locked_leg_ids]
            needed = num_legs - len(parlay_legs)
            
            if needed > 0 and available:
                selected = random.sample(available, min(needed, len(available)))
                parlay_legs.extend(selected)
            
            if len(parlay_legs) >= 2:
                # Calculate odds
                total_odds = 1.0
                for leg in parlay_legs:
                    american = leg['odds']
                    if american.startswith('+'):
                        decimal = 1 + (int(american[1:]) / 100)
                    else:
                        decimal = 1 + (100 / int(american[1:]))
                    total_odds *= decimal
                
                # Convert back to American
                if total_odds >= 2.0:
                    american_odds = f"+{int((total_odds - 1) * 100)}"
                else:
                    american_odds = f"-{int(100 / (total_odds - 1))}"
                
                parlays.append({
                    'id': i,
                    'legs': parlay_legs,
                    'odds_american': american_odds,
                    'implied_probability': round(100 / total_odds, 1)
                })
        
        return parlays
    
    except Exception as e:
        st.error(f"Error generating parlays: {str(e)}")
        return []

def calculate_payout(odds_str, amount):
    """Calculate payout from American odds"""
    try:
        if odds_str.startswith('+'):
            return amount * (int(odds_str[1:]) / 100)
        else:
            return amount * (100 / abs(int(odds_str[1:])))
    except:
        return 0

# Load games
if not st.session_state.events:
    with st.spinner("Loading games..."):
        load_events()

# Header
st.title("Parlay Builder")

# Input section
with st.container():
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.session_state.events:
            game_options = ["Auto-detect"] + [
                f"{e['teams']['away']['abbreviation']} @ {e['teams']['home']['abbreviation']}" 
                for e in st.session_state.events
            ]
            
            selected_idx = st.selectbox("Game", range(len(game_options)), format_func=lambda x: game_options[x])
            
            if selected_idx == 0:
                st.session_state.selected_game = None
            else:
                st.session_state.selected_game = st.session_state.events[selected_idx - 1]
    
    with col2:
        st.slider("Legs", 2, 10, st.session_state.num_legs_filter, key="legs_slider")
        st.session_state.num_legs_filter = st.session_state.legs_slider

# Input
user_input = st.text_input("Describe your parlay", placeholder="e.g., 'Knicks win, Brunson 30+ points'")

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Generate", use_container_width=True):
        if user_input:
            parsed = parse_narrative(user_input, st.session_state.selected_game)
            if parsed:
                parlays = generate_parlays(parsed, 10, st.session_state.locked_legs, st.session_state.removed_legs, st.session_state.num_legs_filter)
                st.session_state.recommendations = parlays
                st.rerun()
with col2:
    if st.session_state.recommendations and st.button("🔄 Regenerate", use_container_width=True):
        if user_input:
            parsed = parse_narrative(user_input, st.session_state.selected_game)
            if parsed:
                parlays = generate_parlays(parsed, 10, st.session_state.locked_legs, st.session_state.removed_legs, st.session_state.num_legs_filter)
                st.session_state.recommendations = parlays
                st.rerun()

# Show parlays
if st.session_state.recommendations:
    st.write("---")
    
    for i in range(0, len(st.session_state.recommendations), 2):
        cols = st.columns(2)
        
        for col_idx in range(2):
            parlay_idx = i + col_idx
            if parlay_idx < len(st.session_state.recommendations):
                parlay = st.session_state.recommendations[parlay_idx]
                
                with cols[col_idx]:
                    with st.container():
                        st.subheader(f"#{parlay['id']} - {parlay['odds_american']}")
                        
                        for leg_idx, leg in enumerate(parlay['legs']):
                            is_locked = any(l['id'] == leg['id'] for l in st.session_state.locked_legs)
                            is_removed = any(l['id'] == leg['id'] for l in st.session_state.removed_legs)
                            
                            leg_cols = st.columns([3, 1, 1])
                            
                            with leg_cols[0]:
                                icon = "🔒 " if is_locked else ("❌ " if is_removed else "")
                                st.write(f"{icon}{leg['display']}")
                                st.caption(f"{leg['market']} • {leg['price']}")
                            
                            with leg_cols[1]:
                                if st.button("🔒" if is_locked else "🔓", key=f"l{parlay['id']}{leg_idx}"):
                                    if is_locked:
                                        st.session_state.locked_legs = [l for l in st.session_state.locked_legs if l['id'] != leg['id']]
                                    else:
                                        st.session_state.locked_legs.append(leg)
                                        st.session_state.removed_legs = [l for l in st.session_state.removed_legs if l['id'] != leg['id']]
                                    st.rerun()
                            
                            with leg_cols[2]:
                                if st.button("❌" if not is_removed else "↩️", key=f"r{parlay['id']}{leg_idx}"):
                                    if is_removed:
                                        st.session_state.removed_legs = [l for l in st.session_state.removed_legs if l['id'] != leg['id']]
                                    else:
                                        st.session_state.removed_legs.append(leg)
                                        st.session_state.locked_legs = [l for l in st.session_state.locked_legs if l['id'] != leg['id']]
                                    st.rerun()
                        
                        payout = 10 + calculate_payout(parlay['odds_american'], 10)
                        st.success(f"$10 → ${payout:.2f}")
                        
                        if st.button("Add to Slip", key=f"add{parlay['id']}", use_container_width=True):
                            st.session_state.selected_parlay = parlay
                            st.rerun()
                        
                        st.write("---")

# Bet slip
if st.session_state.selected_parlay:
    with st.sidebar:
        st.header("Bet Slip")
        
        parlay = st.session_state.selected_parlay
        
        if st.button("✕ Close"):
            st.session_state.selected_parlay = None
            st.rerun()
        
        st.write(f"**{len(parlay['legs'])} Legs**")
        
        for leg in parlay['legs']:
            st.write(f"• {leg['display']}")
            st.caption(f"{leg['market']} • {leg['price']}")
        
        st.write("---")
        
        stake = st.number_input("Stake ($)", 1.0, value=10.0, step=1.0)
        profit = calculate_payout(parlay['odds_american'], stake)
        total = stake + profit
        
        st.metric("Payout", f"${total:.2f}", f"{parlay['odds_american']}")
        
        if st.button("Place Bet", use_container_width=True):
            st.success("Bet placed!")
