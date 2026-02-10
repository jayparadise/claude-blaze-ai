import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Parlay Builder",
    page_icon="🎰",
    layout="wide"
)

# API Configuration
API_KEY = '10019992-c9b1-46b5-be2c-9e760b1c2041'
API_URL = 'https://odds.oddsblaze.com'

# Custom CSS - Bet Builder Style (Light theme with mobile support)
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container - light cream background */
    .main {
        background: #f5f3ed;
        padding: 0;
    }
    
    .main .block-container {
        padding: 1rem;
        max-width: 100%;
    }
    
    /* Typography */
    * {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    h1, h2, h3 {
        color: #1a1a1a;
        font-weight: 600;
    }
    
    h1 {
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    h2 {
        font-size: 1.2rem;
        margin: 1rem 0 0.75rem 0;
    }
    
    h3 {
        font-size: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Text colors */
    p, span, label, div {
        color: #4a4a4a;
    }
    
    /* Input fields */
    .stTextInput input {
        background: white;
        border: 1px solid #d4d4d4;
        color: #1a1a1a;
        border-radius: 8px;
        padding: 0.75rem;
        font-size: 0.95rem;
    }
    
    /* Buttons - yellow/green accent */
    .stButton>button {
        background: #c3f53c;
        color: #1a1a1a;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton>button:hover {
        background: #b5e634;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Secondary buttons */
    button[kind="secondary"] {
        background: white !important;
        border: 1px solid #d4d4d4 !important;
        color: #1a1a1a !important;
    }
    
    /* Parlay cards - white with shadow */
    .parlay-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e8e8e8;
        transition: all 0.2s;
    }
    
    .parlay-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    /* Odds badge - yellow/green */
    .odds-badge {
        background: #c3f53c;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 1.1rem;
        font-weight: 700;
        color: #1a1a1a;
        display: inline-block;
    }
    
    /* Leg items */
    .leg-item {
        background: #fafaf8;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #d4d4d4;
    }
    
    .leg-item strong {
        color: #1a1a1a;
        font-size: 0.9rem;
    }
    
    .leg-item small {
        color: #6b6b6b;
        font-size: 0.8rem;
    }
    
    /* Locked leg */
    .locked-leg {
        background: #fff8e1;
        border-left: 3px solid #ffa726;
    }
    
    /* Removed leg */
    .removed-leg {
        background: #ffebee;
        border-left: 3px solid #e53935;
        opacity: 0.6;
    }
    
    /* Bet slip */
    .bet-slip {
        background: #2d2d2d;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        position: sticky;
        top: 1rem;
    }
    
    .bet-slip h3 {
        color: white;
        margin-top: 0;
    }
    
    .bet-slip .leg-item {
        background: #3a3a3a;
        border-left-color: #c3f53c;
    }
    
    .bet-slip .leg-item strong {
        color: white;
    }
    
    .bet-slip .leg-item small {
        color: #b0b0b0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid #e8e8e8;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background: white;
        border: 1px solid #d4d4d4;
        border-radius: 8px;
    }
    
    /* Sliders */
    .stSlider {
        padding: 0.5rem 0;
    }
    
    /* Number input */
    .stNumberInput input {
        background: white;
        border: 1px solid #d4d4d4;
        color: #1a1a1a;
        border-radius: 8px;
    }
    
    /* Dividers */
    hr {
        margin: 1rem 0;
        border-color: #e8e8e8;
    }
    
    /* Mobile styles */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.5rem;
        }
        
        [data-testid="column"] {
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }
        
        .bet-slip {
            position: relative;
            margin-top: 1rem;
        }
        
        /* Carousel container */
        .carousel-container {
            overflow-x: auto;
            scroll-snap-type: x mandatory;
            display: flex;
            gap: 1rem;
            padding: 0.5rem 0;
            -webkit-overflow-scrolling: touch;
        }
        
        .carousel-container::-webkit-scrollbar {
            height: 4px;
        }
        
        .carousel-container::-webkit-scrollbar-track {
            background: #e8e8e8;
            border-radius: 4px;
        }
        
        .carousel-container::-webkit-scrollbar-thumb {
            background: #c3f53c;
            border-radius: 4px;
        }
        
        .parlay-card {
            min-width: 85%;
            scroll-snap-align: start;
            flex-shrink: 0;
        }
    }
    
    /* Compact spacing */
    .element-container {
        margin-bottom: 0.5rem;
    }
    
    /* Caption text */
    .caption {
        color: #6b6b6b;
        font-size: 0.8rem;
    }
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
        
        # Don't add confirmation message to chat
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
        # Find mentioned event from narrative
        mentioned_event = None
        for event in events:
            home_name = event['teams']['home']['name'].lower()
            away_name = event['teams']['away']['name'].lower()
            home_abbrev = event['teams']['home']['abbreviation'].lower()
            away_abbrev = event['teams']['away']['abbreviation'].lower()
            
            # Split team names into words to match partial names
            home_words = home_name.split()
            away_words = away_name.split()
            
            # Check full names, abbreviations, and individual words
            if (home_name in lower or away_name in lower or 
                home_abbrev in lower or away_abbrev in lower or
                any(word in lower for word in home_words if len(word) > 3) or
                any(word in lower for word in away_words if len(word) > 3)):
                mentioned_event = event
                break
    
    if not mentioned_event:
        return None
    
    # Determine winning team
    winning_team = None
    win_words = ['win', 'beat', 'dominate', 'destroy', 'crush']
    has_win = any(word in lower for word in win_words)
    
    if has_win:
        home_name = mentioned_event['teams']['home']['name']
        away_name = mentioned_event['teams']['away']['name']
        home_name_lower = home_name.lower()
        away_name_lower = away_name.lower()
        home_abbrev = mentioned_event['teams']['home']['abbreviation'].lower()
        away_abbrev = mentioned_event['teams']['away']['abbreviation'].lower()
        
        # Split into words to check partial matches
        home_words = home_name_lower.split()
        away_words = away_name_lower.split()
        
        # Check if home team is mentioned (full name, abbreviation, or any significant word)
        home_mentioned = (home_name_lower in lower or 
                         home_abbrev in lower or 
                         any(word in lower for word in home_words if len(word) > 3))
        
        # Check if away team is mentioned
        away_mentioned = (away_name_lower in lower or 
                         away_abbrev in lower or 
                         any(word in lower for word in away_words if len(word) > 3))
        
        if home_mentioned and not away_mentioned:
            winning_team = home_name
        elif away_mentioned and not home_mentioned:
            winning_team = away_name
        elif home_mentioned and away_mentioned:
            # If both mentioned, the one closer to a win word wins
            # Simple heuristic: first one mentioned
            for word in lower.split():
                if word in [w.lower() for w in home_words if len(w) > 3] + [home_abbrev]:
                    winning_team = home_name
                    break
                elif word in [w.lower() for w in away_words if len(w) > 3] + [away_abbrev]:
                    winning_team = away_name
                    break
    
    # Identify sentiment
    is_high_scoring = any(word in lower for word in ['high scoring', 'lots of points', 'shootout', 'offensive'])
    is_low_scoring = any(word in lower for word in ['low scoring', 'defensive', 'grind'])
    is_blowout = any(word in lower for word in ['blowout', 'dominate', 'destroy', 'crush'])
    
    # Find player mentions
    players = []
    for odd in mentioned_event.get('odds', []):
        # Make sure the odd has a player field and it's not None
        if odd.get('player') and isinstance(odd.get('player'), str):
            try:
                player_name = odd['player'].lower()
                # Check if any part of the player name is mentioned
                player_parts = player_name.split()
                if any(part in lower for part in player_parts) or player_name in lower:
                    has_positive = any(word in lower for word in ['score', 'big game', 'lots', 'great'])
                    players.append({
                        'name': odd['player'],
                        'sentiment': 'positive' if has_positive else 'neutral'
                    })
            except (AttributeError, TypeError):
                # Skip if there's any issue with the player name
                continue
    
    # Remove duplicates
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
        
        # Filter out invalid odds and removed legs
        valid_odds = [o for o in all_odds 
                     if o.get('id') and o.get('market') and o.get('name') and o.get('price')
                     and o['id'] not in removed_ids]
        
        min_legs, max_legs = num_legs_range
        min_odds, max_odds = odds_range
        
        for i in range(count * 3):  # Generate extra, filter later
            legs = list(locked_legs)  # Start with locked legs
            used_ids = {leg['id'] for leg in locked_legs}
            
            target_legs = min_legs if len(locked_legs) == 0 else max(min_legs, len(locked_legs) + 1)
            if target_legs > max_legs:
                target_legs = max_legs
            
            # Add moneyline if team mentioned and not locked/removed
            if winning_team and len(legs) < target_legs:
                ml = next((o for o in valid_odds if o.get('market') == 'Moneyline' and o.get('name') == winning_team), None)
                if ml and ml['id'] not in used_ids:
                    legs.append({**ml, 'display': ml['name']})
                    used_ids.add(ml['id'])
            
            # Add spread if blowout
            if is_blowout and winning_team and len(legs) < target_legs:
                spreads = [o for o in valid_odds if o.get('market') == 'Point Spread' and winning_team in o.get('name', '')]
                for spread in spreads:
                    if spread.get('selection') and isinstance(spread['selection'], dict) and 'line' in spread['selection']:
                        try:
                            line = float(spread['selection']['line'])
                            if abs(line) >= 7 and spread['id'] not in used_ids:
                                legs.append({**spread, 'display': spread['name']})
                                used_ids.add(spread['id'])
                                break
                        except (ValueError, TypeError):
                            continue
            
            # Add total
            if (is_high_scoring or is_low_scoring) and len(legs) < target_legs:
                side = 'Over' if is_high_scoring else 'Under'
                totals = [o for o in valid_odds if o.get('market') == 'Total Points' and side in o.get('name', '')]
                if totals and totals[0]['id'] not in used_ids:
                    legs.append({**totals[0], 'display': totals[0]['name']})
                    used_ids.add(totals[0]['id'])
            
            # Add player props
            for player in players:
                if len(legs) >= target_legs:
                    break
                player_odds = [o for o in valid_odds if o.get('player') == player['name']]
                for odd in player_odds:
                    if odd['id'] not in used_ids:
                        legs.append({**odd, 'display': odd['name']})
                        used_ids.add(odd['id'])
                        break
            
            # Fill remaining legs randomly
            available = [o for o in valid_odds if o['id'] not in used_ids and o.get('market') != 'Moneyline']
            while len(legs) < target_legs and available:
                import random
                odd = random.choice(available)
                legs.append({**odd, 'display': odd['name']})
                used_ids.add(odd['id'])
                available = [o for o in available if o['id'] != odd['id']]
            
            if min_legs <= len(legs) <= max_legs:
                try:
                    # Calculate combined odds
                    decimal_odds = 1
                    for leg in legs:
                        price = leg.get('price', '+100')
                        if price.startswith('+'):
                            decimal_odds *= (int(price[1:]) / 100) + 1
                        else:
                            decimal_odds *= (100 / int(price[1:])) + 1
                    
                    # Filter by odds range
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
                        
                except (ValueError, ZeroDivisionError, TypeError) as e:
                    continue
        
        return parlays[:count]
    
    except Exception as e:
        st.error(f"Error generating parlays: {str(e)}")
        return []

def calculate_payout(odds_str, amount):
    """Calculate potential payout from American odds"""
    try:
        if odds_str.startswith('+'):
            return amount * (int(odds_str[1:]) / 100)
        else:
            return amount * (100 / int(odds_str[1:]))
    except:
        return 0

# Header
st.markdown("""
<div style='margin-bottom: 1.5rem;'>
    <h1 style='color: #1a1a1a; margin: 0; font-size: 1.75rem; font-weight: 700;'>Parlay Builder</h1>
    <p style='color: #6b6b6b; margin: 0.25rem 0 0 0; font-size: 0.9rem;'>Build your perfect same-game parlay</p>
</div>
""", unsafe_allow_html=True)

# Load games on first run
if not st.session_state.events:
    with st.spinner("Loading NBA games..."):
        load_events()

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    # Only show errors if they exist
    assistant_messages = [msg for msg in st.session_state.chat_history if msg['role'] == 'assistant']
    
    if assistant_messages:
        for msg in assistant_messages:
            st.error(msg['content'])
    
    # Input form - compact
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input(
            "input",
            placeholder="Describe your parlay (e.g., 'Knicks win big, Brunson scores lots')",
            key='user_input',
            label_visibility="collapsed"
        )
        submit = st.form_submit_button("Generate", use_container_width=True)
        
        if submit and user_input:
            # Add user message
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            
            # Parse and generate
            parsed = parse_narrative(user_input, force_event=st.session_state.selected_game)
            
            if not parsed:
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': "❌ Couldn't identify the game. Please select a game from the sidebar or mention a team name."
                })
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
                
                # No confirmation message - just show the parlays
            
            st.rerun()
    
    # Recommendations
    if st.session_state.recommendations:
        col_title, col_regen = st.columns([3, 1])
        with col_title:
            st.markdown(f"<h2>Parlays ({len(st.session_state.recommendations)})</h2>", unsafe_allow_html=True)
        with col_regen:
            if st.button("🔄 Regenerate", use_container_width=True, key="regen_btn"):
                if st.session_state.chat_history:
                    for msg in reversed(st.session_state.chat_history):
                        if msg['role'] == 'user':
                            parsed = parse_narrative(msg['content'], force_event=st.session_state.selected_game)
                            if parsed:
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
                            break
        
        # Mobile: Show swipe hint
        st.markdown("""
        <p class='caption' style='margin: 0.5rem 0; display: none;'>
            <span style='display: inline-block;'>← Swipe to see more →</span>
        </p>
        <style>
            @media (max-width: 768px) {
                .caption span { display: inline-block !important; }
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Start carousel container
        st.markdown("<div class='carousel-container'>", unsafe_allow_html=True)
        
        for parlay in st.session_state.recommendations:
            st.markdown("<div class='parlay-card'>", unsafe_allow_html=True)
            
            # Header row
            col_odds, col_info, col_select = st.columns([1.5, 2, 1.5])
            
            with col_odds:
                st.markdown(f"<div class='odds-badge'>{parlay['odds_american']}</div>", unsafe_allow_html=True)
                st.markdown(f"<p class='caption' style='margin-top: 0.25rem;'>{len(parlay['legs'])} legs • {parlay['implied_probability']}%</p>", unsafe_allow_html=True)
            
            with col_select:
                if st.button("+ Add", key=f"select_{parlay['id']}", use_container_width=True):
                    st.session_state.selected_parlay = parlay
                    st.rerun()
            
            st.markdown("<hr style='margin: 0.75rem 0;'>", unsafe_allow_html=True)
            
            # Display legs
            for idx, leg in enumerate(parlay['legs']):
                is_locked = any(l['id'] == leg['id'] for l in st.session_state.locked_legs)
                is_removed = any(l['id'] == leg['id'] for l in st.session_state.removed_legs)
                
                leg_class = 'locked-leg' if is_locked else ('removed-leg' if is_removed else 'leg-item')
                
                cols = st.columns([6, 0.7, 0.7])
                
                with cols[0]:
                    st.markdown(f"""
                    <div class='{leg_class}'>
                        <strong>{leg['display']}</strong><br>
                        <small>{leg['market']} • {leg['price']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[1]:
                    lock_emoji = "🔒" if is_locked else "🔓"
                    if st.button(lock_emoji, key=f"lock_{parlay['id']}_{idx}", help="Lock"):
                        if is_locked:
                            st.session_state.locked_legs = [l for l in st.session_state.locked_legs if l['id'] != leg['id']]
                        else:
                            if not any(l['id'] == leg['id'] for l in st.session_state.locked_legs):
                                st.session_state.locked_legs.append(leg)
                            st.session_state.removed_legs = [l for l in st.session_state.removed_legs if l['id'] != leg['id']]
                        st.rerun()
                
                with cols[2]:
                    remove_emoji = "❌" if not is_removed else "↩️"
                    if st.button(remove_emoji, key=f"remove_{parlay['id']}_{idx}", help="Remove"):
                        if is_removed:
                            st.session_state.removed_legs = [l for l in st.session_state.removed_legs if l['id'] != leg['id']]
                        else:
                            if not any(l['id'] == leg['id'] for l in st.session_state.removed_legs):
                                st.session_state.removed_legs.append(leg)
                            st.session_state.locked_legs = [l for l in st.session_state.locked_legs if l['id'] != leg['id']]
                        st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)  # Close parlay-card
        
        # Close carousel container
        st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='bet-slip'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top: 0; color: white;'>Bet Slip</h3>", unsafe_allow_html=True)
    
    if st.session_state.selected_parlay:
        parlay = st.session_state.selected_parlay
        
        # Display number of legs and clear all
        col_legs, col_clear = st.columns([2, 1])
        with col_legs:
            st.markdown(f"<p style='color: #c3f53c; margin: 0; font-weight: 600;'>{len(parlay['legs'])} Legs Multi</p>", unsafe_allow_html=True)
        with col_clear:
            st.markdown(f"<p style='color: #888; margin: 0; font-size: 0.85rem; cursor: pointer;'>Clear All</p>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 0.75rem 0; border-color: #444;'>", unsafe_allow_html=True)
        
        # Legs
        for leg in parlay['legs']:
            st.markdown(f"""
            <div style='background: #3a3a3a; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0;'>
                <strong style='color: white; font-size: 0.9rem;'>{leg['display']}</strong><br>
                <small style='color: #b0b0b0; font-size: 0.8rem;'>{leg['market']} • {leg['price']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 0.75rem 0; border-color: #444;'>", unsafe_allow_html=True)
        
        # Bet amount input
        col_amount_label, col_amount_value = st.columns([1, 2])
        with col_amount_label:
            st.markdown("<p style='color: white; margin: 0.5rem 0; font-size: 0.9rem;'>Stake:</p>", unsafe_allow_html=True)
        with col_amount_value:
            bet_amount = st.number_input("stake", min_value=1.0, value=10.0, step=1.0, label_visibility="collapsed")
        
        # Odds and payout
        profit = calculate_payout(parlay['odds_american'], bet_amount)
        total_payout = bet_amount + profit
        
        st.markdown(f"""
        <div style='display: flex; justify-content: space-between; margin: 0.75rem 0;'>
            <span style='color: #b0b0b0; font-size: 0.9rem;'>@ {parlay['odds_american']}</span>
            <span style='color: white; font-weight: 600; font-size: 0.9rem;'>return: ${total_payout:.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 0.75rem 0; border-color: #444;'>", unsafe_allow_html=True)
        
        # Place bet button
        if st.button("Place Multi", use_container_width=True, key="place_bet"):
            st.success("Bet placed!")
        
        if st.button("Clear", use_container_width=True, key="clear_bet"):
            st.session_state.selected_parlay = None
            st.rerun()
    else:
        st.markdown("""
        <div style='text-align: center; padding: 3rem 1rem; color: #888;'>
            <p style='margin: 0; font-size: 0.95rem;'>Add selections to get started</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='margin-bottom: 1rem; color: #1a1a1a;'>Settings</h2>", unsafe_allow_html=True)
    
    # Game Selector
    if st.session_state.events:
        st.markdown("<h3 style='font-size: 0.95rem; margin-bottom: 0.5rem; color: #1a1a1a;'>Select Game</h3>", unsafe_allow_html=True)
        game_options = ["Auto-detect"] + [
            f"{e['teams']['away']['abbreviation']} @ {e['teams']['home']['abbreviation']}" 
            for e in st.session_state.events
        ]
        
        selected_game_idx = st.selectbox(
            "Game",
            range(len(game_options)),
            format_func=lambda x: game_options[x],
            label_visibility="collapsed"
        )
        
        if selected_game_idx == 0:
            st.session_state.selected_game = None
        else:
            st.session_state.selected_game = st.session_state.events[selected_game_idx - 1]
        
        st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='font-size: 0.95rem; margin-bottom: 0.75rem; color: #1a1a1a;'>Filters</h3>", unsafe_allow_html=True)
    
    # Number of legs filter
    st.markdown("<p style='font-size: 0.85rem; margin-bottom: 0.25rem; color: #6b6b6b;'>Number of Legs</p>", unsafe_allow_html=True)
    num_legs = st.slider(
        "legs",
        min_value=2,
        max_value=6,
        value=(3, 5),
        label_visibility="collapsed"
    )
    st.session_state.num_legs_filter = num_legs
    
    # Odds range filter
    st.markdown("<p style='font-size: 0.85rem; margin-bottom: 0.25rem; margin-top: 0.75rem; color: #6b6b6b;'>Odds Range</p>", unsafe_allow_html=True)
    odds_range = st.slider(
        "odds",
        min_value=1.2,
        max_value=100.0,
        value=(1.5, 50.0),
        step=0.5,
        label_visibility="collapsed"
    )
    st.session_state.odds_range_filter = odds_range
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Locked/Removed legs info
    if st.session_state.locked_legs:
        st.markdown(f"<p style='color: #f59e0b; font-size: 0.9rem; margin: 0.5rem 0;'>🔒 {len(st.session_state.locked_legs)} locked</p>", unsafe_allow_html=True)
    if st.session_state.removed_legs:
        st.markdown(f"<p style='color: #e53935; font-size: 0.9rem; margin: 0.5rem 0;'>❌ {len(st.session_state.removed_legs)} removed</p>", unsafe_allow_html=True)
    
    if st.session_state.locked_legs or st.session_state.removed_legs:
        if st.button("Clear All", use_container_width=True, key="clear_locks"):
            st.session_state.locked_legs = []
            st.session_state.removed_legs = []
            st.rerun()
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    if st.button("Reload Games", use_container_width=True):
        st.session_state.events = []
        st.session_state.selected_game = None
        st.session_state.chat_history = []
        st.session_state.recommendations = []
        st.session_state.locked_legs = []
        st.session_state.removed_legs = []
        load_events()
        st.rerun()
