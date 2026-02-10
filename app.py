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

# Custom CSS - DraftKings Carousel Style
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Dark theme background */
    .main {
        background: #0d1117;
        color: white;
    }
    
    .main .block-container {
        padding: 1.5rem;
        max-width: 1400px;
    }
    
    /* Typography */
    * {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    h1, h2, h3 {
        color: white;
        font-weight: 600;
    }
    
    h1 {
        font-size: 1.75rem;
        margin-bottom: 1.5rem;
    }
    
    h2 {
        font-size: 1.3rem;
        margin: 1.5rem 0 1rem 0;
    }
    
    /* Input section */
    .input-section {
        background: #161b22;
        padding: 1.25rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid #30363d;
    }
    
    .stTextInput input {
        background: #0d1117;
        border: 1px solid #30363d;
        color: white;
        border-radius: 8px;
        padding: 0.875rem;
        font-size: 1rem;
    }
    
    .stTextInput input:focus {
        border-color: #58a6ff;
    }
    
    /* Buttons */
    .stButton>button {
        background: #238636;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        background: #2ea043;
        transform: translateY(-1px);
    }
    
    /* Settings button */
    button[kind="secondary"] {
        background: transparent !important;
        border: 1px solid #30363d !important;
        color: white !important;
    }
    
    /* Carousel container - ALWAYS horizontal scroll */
    .carousel-container {
        overflow-x: auto;
        overflow-y: hidden;
        display: flex;
        gap: 1.25rem;
        padding: 1rem 0 1.5rem 0;
        scroll-snap-type: x mandatory;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: thin;
        scrollbar-color: #30363d #161b22;
    }
    
    .carousel-container::-webkit-scrollbar {
        height: 8px;
    }
    
    .carousel-container::-webkit-scrollbar-track {
        background: #161b22;
        border-radius: 4px;
    }
    
    .carousel-container::-webkit-scrollbar-thumb {
        background: #30363d;
        border-radius: 4px;
    }
    
    .carousel-container::-webkit-scrollbar-thumb:hover {
        background: #484f58;
    }
    
    /* Parlay cards - DraftKings style */
    .parlay-card {
        min-width: 380px;
        max-width: 380px;
        background: #161b22;
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid #30363d;
        scroll-snap-align: start;
        flex-shrink: 0;
        transition: all 0.2s;
        position: relative;
    }
    
    .parlay-card:hover {
        border-color: #58a6ff;
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    }
    
    /* Card header */
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .card-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: white;
    }
    
    /* Odds badge */
    .odds-badge {
        background: #238636;
        padding: 0.4rem 0.9rem;
        border-radius: 6px;
        font-size: 1rem;
        font-weight: 700;
        color: white;
    }
    
    /* Leg items - compact */
    .leg-item {
        background: #0d1117;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #30363d;
    }
    
    .leg-item strong {
        color: white;
        font-size: 0.9rem;
        display: block;
        margin-bottom: 0.25rem;
    }
    
    .leg-item small {
        color: #8b949e;
        font-size: 0.8rem;
    }
    
    /* Locked leg */
    .locked-leg {
        border-left-color: #f85149;
    }
    
    /* Removed leg */
    .removed-leg {
        opacity: 0.4;
        border-left-color: #6e7681;
    }
    
    /* Social proof */
    .social-proof {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 1rem 0;
        color: #f85149;
        font-size: 0.9rem;
    }
    
    /* Payout section */
    .payout-section {
        background: #0d1117;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
        text-align: center;
    }
    
    .payout-odds {
        font-size: 1.5rem;
        font-weight: 700;
        color: #3fb950;
        margin-bottom: 0.25rem;
    }
    
    .payout-text {
        color: #8b949e;
        font-size: 0.85rem;
    }
    
    /* Slide-out bet slip */
    .bet-slip-overlay {
        position: fixed;
        top: 0;
        right: -400px;
        width: 380px;
        height: 100vh;
        background: #0d1117;
        border-left: 1px solid #30363d;
        box-shadow: -4px 0 24px rgba(0,0,0,0.6);
        transition: right 0.3s ease;
        z-index: 1000;
        overflow-y: auto;
        padding: 1.5rem;
    }
    
    .bet-slip-overlay.open {
        right: 0;
    }
    
    /* Collapse settings by default */
    .settings-collapsed {
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.3s ease;
    }
    
    .settings-expanded {
        max-height: 500px;
        transition: max-height 0.3s ease;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background: #0d1117;
        border: 1px solid #30363d;
        color: white;
        border-radius: 8px;
    }
    
    /* Sliders */
    .stSlider {
        padding: 0.75rem 0;
    }
    
    /* Number input */
    .stNumberInput input {
        background: #0d1117;
        border: 1px solid #30363d;
        color: white;
        border-radius: 8px;
    }
    
    /* Text colors */
    p, span, label, div {
        color: #c9d1d9;
    }
    
    .caption {
        color: #8b949e;
        font-size: 0.8rem;
    }
    
    /* Hide sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .parlay-card {
            min-width: 320px;
            max-width: 320px;
        }
        
        .bet-slip-overlay {
            width: 100%;
            right: -100%;
        }
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
<h1 style='color: white; margin: 0 0 0.5rem 0;'>Parlay Builder</h1>
<p style='color: #8b949e; margin: 0 0 1.5rem 0;'>AI-powered same-game parlay generator</p>
""", unsafe_allow_html=True)

# Load games on first run
if not st.session_state.events:
    with st.spinner("Loading NBA games..."):
        load_events()

# Settings toggle state
if 'settings_open' not in st.session_state:
    st.session_state.settings_open = False

# Input and Settings Section
st.markdown("<div class='input-section'>", unsafe_allow_html=True)

# Top row: Game selector and settings button
col_game, col_settings = st.columns([3, 1])

with col_game:
    if st.session_state.events:
        game_options = ["Auto-detect from description"] + [
            f"{e['teams']['away']['abbreviation']} @ {e['teams']['home']['abbreviation']}" 
            for e in st.session_state.events
        ]
        
        selected_game_idx = st.selectbox(
            "Select Game",
            range(len(game_options)),
            format_func=lambda x: game_options[x],
            key="game_selector"
        )
        
        if selected_game_idx == 0:
            st.session_state.selected_game = None
        else:
            st.session_state.selected_game = st.session_state.events[selected_game_idx - 1]

with col_settings:
    if st.button("⚙️ Filters" if not st.session_state.settings_open else "✕ Close", key="settings_toggle", use_container_width=True):
        st.session_state.settings_open = not st.session_state.settings_open
        st.rerun()

# Expandable settings
if st.session_state.settings_open:
    st.markdown("---")
    col_legs, col_odds = st.columns(2)
    
    with col_legs:
        st.markdown("<p style='font-size: 0.85rem; margin-bottom: 0.5rem; color: #8b949e;'>Number of Legs</p>", unsafe_allow_html=True)
        num_legs = st.slider(
            "legs",
            min_value=2,
            max_value=6,
            value=st.session_state.num_legs_filter,
            label_visibility="collapsed",
            key="num_legs_slider"
        )
        st.session_state.num_legs_filter = num_legs
    
    with col_odds:
        st.markdown("<p style='font-size: 0.85rem; margin-bottom: 0.5rem; color: #8b949e;'>Odds Range</p>", unsafe_allow_html=True)
        odds_range = st.slider(
            "odds",
            min_value=1.2,
            max_value=100.0,
            value=st.session_state.odds_range_filter,
            step=0.5,
            label_visibility="collapsed",
            key="odds_range_slider"
        )
        st.session_state.odds_range_filter = odds_range
    
    # Locked/Removed info
    if st.session_state.locked_legs or st.session_state.removed_legs:
        st.markdown("---")
        col_status, col_clear = st.columns([2, 1])
        with col_status:
            if st.session_state.locked_legs:
                st.markdown(f"<p style='color: #f85149; margin: 0.25rem 0;'>🔒 {len(st.session_state.locked_legs)} locked</p>", unsafe_allow_html=True)
            if st.session_state.removed_legs:
                st.markdown(f"<p style='color: #8b949e; margin: 0.25rem 0;'>❌ {len(st.session_state.removed_legs)} removed</p>", unsafe_allow_html=True)
        with col_clear:
            if st.button("Clear All", key="clear_all", use_container_width=True):
                st.session_state.locked_legs = []
                st.session_state.removed_legs = []
                st.rerun()

st.markdown("---")

# Input form
col_input, col_submit, col_regen = st.columns([5, 1.5, 1.5])

with col_input:
    user_input = st.text_input(
        "input",
        placeholder="Describe your parlay (e.g., 'Knicks win big, Brunson 30+ points')",
        key='user_input',
        label_visibility="collapsed"
    )

with col_submit:
    submit = st.button("Generate", use_container_width=True, key="gen_btn")

with col_regen:
    if st.session_state.recommendations:
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

st.markdown("</div>", unsafe_allow_html=True)

# Process input
if submit and user_input:
    st.session_state.chat_history.append({
        'role': 'user',
        'content': user_input
    })
    
    parsed = parse_narrative(user_input, force_event=st.session_state.selected_game)
    
    if not parsed:
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': "❌ Couldn't identify the game. Please select a game or mention a team name."
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
    
    st.rerun()

# Error messages
assistant_messages = [msg for msg in st.session_state.chat_history if msg['role'] == 'assistant']
if assistant_messages:
    for msg in assistant_messages:
        st.error(msg['content'])

# Parlay Carousel
if st.session_state.recommendations:
    st.markdown(f"<h2>Recommended Parlays ({len(st.session_state.recommendations)})</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8b949e; margin-bottom: 1rem;'>← Scroll to see all options →</p>", unsafe_allow_html=True)
    
    # Carousel container
    st.markdown("<div class='carousel-container'>", unsafe_allow_html=True)
    
    for parlay in st.session_state.recommendations:
        st.markdown("<div class='parlay-card'>", unsafe_allow_html=True)
        
        # Card header with title and badge
        st.markdown(f"""
        <div class='card-header'>
            <div class='card-title'>Parlay #{parlay['id']}</div>
            <div class='odds-badge'>{parlay['odds_american']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Legs with lock/remove
        for idx, leg in enumerate(parlay['legs']):
            is_locked = any(l['id'] == leg['id'] for l in st.session_state.locked_legs)
            is_removed = any(l['id'] == leg['id'] for l in st.session_state.removed_legs)
            
            leg_class = 'locked-leg' if is_locked else ('removed-leg' if is_removed else 'leg-item')
            
            cols = st.columns([7, 0.8, 0.8])
            
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
        
        # Social proof (mock data)
        import random
        people_count = random.randint(50, 500)
        st.markdown(f"""
        <div class='social-proof'>
            🔥 {people_count} people placed this bet
        </div>
        """, unsafe_allow_html=True)
        
        # Payout section
        st.markdown(f"""
        <div class='payout-section'>
            <div class='payout-odds'>{parlay['odds_american']}</div>
            <div class='payout-text'>$10 pays ${10 + calculate_payout(parlay['odds_american'], 10):.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add to slip button
        if st.button("+ Add to Bet Slip", key=f"add_{parlay['id']}", use_container_width=True):
            st.session_state.selected_parlay = parlay
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close parlay-card
    
    st.markdown("</div>", unsafe_allow_html=True)  # Close carousel

# Bet Slip - Conditional slide-out
if st.session_state.selected_parlay:
    st.markdown("""
    <div style='position: fixed; top: 0; right: 0; width: 380px; height: 100vh; background: #161b22; border-left: 1px solid #30363d; box-shadow: -4px 0 24px rgba(0,0,0,0.6); z-index: 1000; overflow-y: auto; padding: 1.5rem;'>
        <h3 style='color: white; margin-top: 0;'>Bet Slip</h3>
    """, unsafe_allow_html=True)
    
    parlay = st.session_state.selected_parlay
    
    # Header
    col_legs, col_close = st.columns([2, 1])
    with col_legs:
        st.markdown(f"<p style='color: #3fb950; margin: 0; font-weight: 600;'>{len(parlay['legs'])} Legs Multi</p>", unsafe_allow_html=True)
    with col_close:
        if st.button("✕", key="close_slip"):
            st.session_state.selected_parlay = None
            st.rerun()
    
    st.markdown("<hr style='border-color: #30363d; margin: 0.75rem 0;'>", unsafe_allow_html=True)
    
    # Legs
    for leg in parlay['legs']:
        st.markdown(f"""
        <div style='background: #0d1117; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #3fb950;'>
            <strong style='color: white; font-size: 0.9rem;'>{leg['display']}</strong><br>
            <small style='color: #8b949e; font-size: 0.8rem;'>{leg['market']} • {leg['price']}</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border-color: #30363d; margin: 0.75rem 0;'>", unsafe_allow_html=True)
    
    # Bet amount
    bet_amount = st.number_input("Stake Amount ($)", min_value=1.0, value=10.0, step=1.0, key="bet_amount_slip")
    
    # Payout
    profit = calculate_payout(parlay['odds_american'], bet_amount)
    total_payout = bet_amount + profit
    
    st.markdown(f"""
    <div style='background: #0d1117; padding: 1rem; border-radius: 8px; margin: 0.75rem 0; text-align: center;'>
        <div style='color: #8b949e; font-size: 0.85rem; margin-bottom: 0.5rem;'>@ {parlay['odds_american']}</div>
        <div style='color: #3fb950; font-size: 1.75rem; font-weight: 700;'>${total_payout:.2f}</div>
        <div style='color: #8b949e; font-size: 0.85rem; margin-top: 0.5rem;'>Potential Payout</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Place bet button
    if st.button("Place Bet", use_container_width=True, key="place_bet_slip"):
        st.success("Bet placed! (Demo mode)")
    
    st.markdown("</div>", unsafe_allow_html=True)
