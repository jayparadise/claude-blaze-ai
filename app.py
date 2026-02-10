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

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 8px;
        font-weight: 600;
    }
    .parlay-card {
        background: rgba(30, 41, 59, 0.6);
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid rgba(148, 163, 184, 0.2);
        margin-bottom: 1rem;
    }
    .odds-badge {
        background: rgba(34, 197, 94, 0.2);
        padding: 0.4rem 1rem;
        border-radius: 6px;
        font-size: 1.1rem;
        font-weight: 700;
        color: #4ade80;
        display: inline-block;
    }
    .leg-item {
        background: #1e293b;
        padding: 0.75rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    .locked-leg {
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'events' not in st.session_state:
    st.session_state.events = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'locked_legs' not in st.session_state:
    st.session_state.locked_legs = []
if 'selected_parlay' not in st.session_state:
    st.session_state.selected_parlay = None
if 'bet_amount' not in st.session_state:
    st.session_state.bet_amount = 10.0

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
        
        games_list = [f"{e['teams']['away']['name']} @ {e['teams']['home']['name']}" 
                     for e in data['events']]
        
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': f"✅ Loaded {len(data['events'])} NBA game(s)!\n\n📊 Available: {', '.join(games_list)}\n\nDescribe your parlay idea!"
        })
        
        return True
        
    except Exception as e:
        st.error(f"Error loading games: {str(e)}")
        return False

def parse_narrative(narrative):
    """Parse user narrative to understand betting intent"""
    lower = narrative.lower()
    events = st.session_state.events
    
    # Find mentioned event
    mentioned_event = None
    for event in events:
        home_name = event['teams']['home']['name'].lower()
        away_name = event['teams']['away']['name'].lower()
        home_abbrev = event['teams']['home']['abbreviation'].lower()
        away_abbrev = event['teams']['away']['abbreviation'].lower()
        
        # Split team names into words to match partial names (e.g., "Knicks" from "New York Knicks")
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

def generate_parlays(parsed_data, count=10):
    """Generate parlay combinations based on parsed narrative"""
    try:
        event = parsed_data['event']
        winning_team = parsed_data['winning_team']
        is_high_scoring = parsed_data['is_high_scoring']
        is_low_scoring = parsed_data['is_low_scoring']
        is_blowout = parsed_data['is_blowout']
        players = parsed_data['players']
        
        parlays = []
        all_odds = event.get('odds', [])
        
        # Filter out invalid odds early
        valid_odds = [o for o in all_odds if o.get('id') and o.get('market') and o.get('name') and o.get('price')]
        
        for i in range(count):
            legs = []
            used_ids = set()
            
            # Add moneyline if team mentioned
            if winning_team:
                ml = next((o for o in valid_odds if o.get('market') == 'Moneyline' and o.get('name') == winning_team), None)
                if ml and ml['id'] not in used_ids:
                    legs.append({**ml, 'display': ml['name']})
                    used_ids.add(ml['id'])
            
            # Add spread if blowout
            if is_blowout and winning_team and len(legs) < 5:
                spreads = [o for o in valid_odds if o.get('market') == 'Point Spread' and winning_team in o.get('name', '')]
                # Find large spreads
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
            if (is_high_scoring or is_low_scoring) and len(legs) < 5:
                side = 'Over' if is_high_scoring else 'Under'
                totals = [o for o in valid_odds if o.get('market') == 'Total Points' and side in o.get('name', '')]
                if totals and totals[0]['id'] not in used_ids:
                    legs.append({**totals[0], 'display': totals[0]['name']})
                    used_ids.add(totals[0]['id'])
            
            # Add player props
            for player in players:
                if len(legs) >= 5:
                    break
                player_odds = [o for o in valid_odds if o.get('player') == player['name']]
                for odd in player_odds:
                    if odd['id'] not in used_ids:
                        legs.append({**odd, 'display': odd['name']})
                        used_ids.add(odd['id'])
                        break
            
            # Fill remaining legs randomly
            available = [o for o in valid_odds if o['id'] not in used_ids and o.get('market') != 'Moneyline']
            while len(legs) < 4 and available:
                import random
                odd = random.choice(available)
                legs.append({**odd, 'display': odd['name']})
                used_ids.add(odd['id'])
                available = [o for o in available if o['id'] != odd['id']]
            
            if len(legs) >= 3:
                try:
                    # Calculate combined odds
                    decimal_odds = 1
                    for leg in legs:
                        price = leg.get('price', '+100')
                        if price.startswith('+'):
                            decimal_odds *= (int(price[1:]) / 100) + 1
                        else:
                            decimal_odds *= (100 / int(price[1:])) + 1
                    
                    american_odds = f"+{int((decimal_odds - 1) * 100)}" if decimal_odds >= 2 else f"-{int(100 / (decimal_odds - 1))}"
                    implied_prob = round(1 / decimal_odds * 100, 1)
                    
                    parlays.append({
                        'id': f'parlay-{i}',
                        'legs': legs,
                        'event_id': event['id'],
                        'odds_american': american_odds,
                        'implied_probability': implied_prob
                    })
                except (ValueError, ZeroDivisionError, TypeError) as e:
                    # Skip this parlay if odds calculation fails
                    continue
        
        return parlays
    
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
st.title("🎰 AI Parlay Builder")
st.markdown("**Powered by DraftKings • Real-time odds from OddsBlaze API**")

# Load games on first run
if not st.session_state.events:
    with st.spinner("Loading NBA games..."):
        load_events()

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Chat")
    
    # Chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                st.markdown(f"**You:** {msg['content']}")
            else:
                st.info(msg['content'])
    
    # Input
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input(
            "Describe your parlay",
            placeholder="e.g., 'Knicks will win big and Brunson scores lots of points'",
            key='user_input'
        )
        submit = st.form_submit_button("Send")
        
        if submit and user_input:
            # Add user message
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            
            # Parse and generate
            parsed = parse_narrative(user_input)
            
            if not parsed:
                games_list = [f"{e['teams']['away']['name']} @ {e['teams']['home']['name']}" 
                             for e in st.session_state.events]
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': f"❌ Couldn't identify the game.\n\nAvailable: {', '.join(games_list)}"
                })
            else:
                parlays = generate_parlays(parsed, 10)
                st.session_state.recommendations = parlays
                
                game_str = f"{parsed['event']['teams']['away']['name']} @ {parsed['event']['teams']['home']['name']}"
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': f"✅ Generated {len(parlays)} parlays for {game_str}! Check them out below."
                })
            
            st.rerun()
    
    # Recommendations
    if st.session_state.recommendations:
        st.subheader(f"🎯 Recommended Parlays ({len(st.session_state.recommendations)})")
        
        for parlay in st.session_state.recommendations:
            with st.container():
                col_odds, col_info = st.columns([1, 2])
                
                with col_odds:
                    st.markdown(f"<div class='odds-badge'>{parlay['odds_american']}</div>", unsafe_allow_html=True)
                    st.caption(f"{len(parlay['legs'])} legs • {parlay['implied_probability']}% prob")
                
                with col_info:
                    for leg in parlay['legs']:
                        st.markdown(f"**{leg['display']}** • {leg['market']} • {leg['price']}")
                
                if st.button(f"Select Parlay", key=f"select_{parlay['id']}"):
                    st.session_state.selected_parlay = parlay
                    st.rerun()
                
                st.divider()

with col2:
    st.subheader("🎫 Bet Slip")
    
    if st.session_state.selected_parlay:
        parlay = st.session_state.selected_parlay
        
        st.markdown("### Selected Parlay")
        
        for leg in parlay['legs']:
            st.markdown(f"""
            <div class='leg-item'>
                <strong>{leg['display']}</strong><br>
                <small>{leg['market']} • {leg['price']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Odds display
        st.markdown(f"**DraftKings Odds:** {parlay['odds_american']}")
        st.caption(f"{parlay['implied_probability']}% implied probability")
        
        st.divider()
        
        # Bet amount
        bet_amount = st.number_input("Bet Amount ($)", min_value=1.0, value=10.0, step=1.0)
        
        # Payout calculation
        profit = calculate_payout(parlay['odds_american'], bet_amount)
        total_payout = bet_amount + profit
        
        st.success(f"**Potential Payout:** ${total_payout:.2f}")
        st.caption(f"Profit: ${profit:.2f}")
        
        st.divider()
        
        if st.button("🎰 Place Bet on DraftKings", use_container_width=True):
            st.balloons()
            st.success("Bet placed! (Demo mode)")
        
        if st.button("Clear Selection", use_container_width=True):
            st.session_state.selected_parlay = None
            st.rerun()
    else:
        st.info("Select a parlay from the recommendations to see details here")

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This AI Parlay Builder helps you create same-game parlays using natural language.
    
    **How to use:**
    1. Describe your betting thesis
    2. AI generates 10 parlay options
    3. Select and place your bet
    
    **Example queries:**
    - "Knicks will win in a blowout"
    - "High scoring game, Brunson goes off"
    - "Pacers win and Haliburton has a big game"
    """)
    
    st.divider()
    
    if st.button("🔄 Reload Games"):
        st.session_state.events = []
        st.session_state.chat_history = []
        st.session_state.recommendations = []
        load_events()
        st.rerun()
    
    st.caption(f"Games loaded: {len(st.session_state.events)}")
