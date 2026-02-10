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

# Custom CSS - FanDuel inspired
st.markdown("""
<style>
    /* Main background */
    .main {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Buttons */
    .stButton>button {
        background: #1E88E5;
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 4px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        background: #1565C0;
        box-shadow: 0 2px 8px rgba(30, 136, 229, 0.3);
    }
    
    /* Lock button */
    .lock-btn {
        background: #FFA726;
        color: white;
        border: none;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        font-size: 0.8rem;
        cursor: pointer;
        margin-left: 0.5rem;
    }
    
    /* Remove button */
    .remove-btn {
        background: #EF5350;
        color: white;
        border: none;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        font-size: 0.8rem;
        cursor: pointer;
        margin-left: 0.3rem;
    }
    
    /* Parlay card */
    .parlay-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        border: 2px solid #e0e0e0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.2s;
    }
    
    .parlay-card:hover {
        border-color: #1E88E5;
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.15);
    }
    
    /* Odds badge */
    .odds-badge {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 1.2rem;
        font-weight: 700;
        color: white;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3);
    }
    
    /* Leg item */
    .leg-item {
        background: #f5f5f5;
        padding: 0.75rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border-left: 3px solid #1E88E5;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Locked leg */
    .locked-leg {
        background: #FFF3E0;
        border-left: 3px solid #FFA726;
    }
    
    /* Removed leg */
    .removed-leg {
        background: #FFEBEE;
        border-left: 3px solid #EF5350;
        opacity: 0.6;
    }
    
    /* Chat messages */
    .chat-user {
        background: #E3F2FD;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #1E88E5;
    }
    
    .chat-assistant {
        background: white;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #212121;
    }
    
    /* Info boxes */
    .stAlert {
        background: white;
        border-left: 4px solid #1E88E5;
    }
    
    /* Sliders */
    .stSlider {
        padding: 0.5rem 0;
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
<div style='background: linear-gradient(90deg, #1E88E5 0%, #1565C0 100%); 
            padding: 1.5rem; 
            border-radius: 8px; 
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 12px rgba(30, 136, 229, 0.2);'>
    <h1 style='color: white; margin: 0; font-size: 2rem;'>🎰 AI Parlay Builder</h1>
    <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
        Powered by DraftKings • Real-time odds from OddsBlaze API
    </p>
</div>
""", unsafe_allow_html=True)

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
                st.markdown(f"""
                <div class='chat-user'>
                    <strong>You:</strong> {msg['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='chat-assistant'>
                    {msg['content']}
                </div>
                """, unsafe_allow_html=True)
    
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
                parlays = generate_parlays(
                    parsed, 
                    10,
                    locked_legs=st.session_state.locked_legs,
                    removed_legs=st.session_state.removed_legs,
                    num_legs_range=st.session_state.num_legs_filter,
                    odds_range=st.session_state.odds_range_filter
                )
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
        
        # Regenerate button
        col_regen1, col_regen2 = st.columns([3, 1])
        with col_regen2:
            if st.button("🔄 Regenerate", use_container_width=True):
                # Get the last parsed data from chat
                if st.session_state.chat_history:
                    # Re-parse the last user message
                    for msg in reversed(st.session_state.chat_history):
                        if msg['role'] == 'user':
                            parsed = parse_narrative(msg['content'])
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
        
        for parlay in st.session_state.recommendations:
            with st.container():
                st.markdown("<div class='parlay-card'>", unsafe_allow_html=True)
                
                col_odds, col_info, col_select = st.columns([1, 2, 1])
                
                with col_odds:
                    st.markdown(f"<div class='odds-badge'>{parlay['odds_american']}</div>", unsafe_allow_html=True)
                    st.caption(f"{len(parlay['legs'])} legs • {parlay['implied_probability']}% prob")
                
                with col_select:
                    if st.button(f"Add to Slip", key=f"select_{parlay['id']}", use_container_width=True):
                        st.session_state.selected_parlay = parlay
                        st.rerun()
                
                # Display legs with lock/remove buttons
                for idx, leg in enumerate(parlay['legs']):
                    leg_col1, leg_col2 = st.columns([4, 1])
                    
                    with leg_col1:
                        is_locked = any(l['id'] == leg['id'] for l in st.session_state.locked_legs)
                        is_removed = any(l['id'] == leg['id'] for l in st.session_state.removed_legs)
                        
                        leg_class = 'locked-leg' if is_locked else ('removed-leg' if is_removed else 'leg-item')
                        
                        st.markdown(f"""
                        <div class='{leg_class}'>
                            <strong>{leg['display']}</strong><br>
                            <small>{leg['market']} • {leg['price']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with leg_col2:
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            lock_emoji = "🔓" if not is_locked else "🔒"
                            if st.button(lock_emoji, key=f"lock_{parlay['id']}_{idx}", help="Lock this leg"):
                                if is_locked:
                                    st.session_state.locked_legs = [l for l in st.session_state.locked_legs if l['id'] != leg['id']]
                                else:
                                    if not any(l['id'] == leg['id'] for l in st.session_state.locked_legs):
                                        st.session_state.locked_legs.append(leg)
                                    # Also remove from removed if it was there
                                    st.session_state.removed_legs = [l for l in st.session_state.removed_legs if l['id'] != leg['id']]
                                st.rerun()
                        
                        with btn_col2:
                            remove_emoji = "❌" if not is_removed else "↩️"
                            if st.button(remove_emoji, key=f"remove_{parlay['id']}_{idx}", help="Remove this leg"):
                                if is_removed:
                                    st.session_state.removed_legs = [l for l in st.session_state.removed_legs if l['id'] != leg['id']]
                                else:
                                    if not any(l['id'] == leg['id'] for l in st.session_state.removed_legs):
                                        st.session_state.removed_legs.append(leg)
                                    # Also remove from locked if it was there
                                    st.session_state.locked_legs = [l for l in st.session_state.locked_legs if l['id'] != leg['id']]
                                st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
                st.divider()

with col2:
    st.markdown("""
    <div style='background: white; 
                border-radius: 8px; 
                padding: 1rem; 
                border: 2px solid #1E88E5;
                box-shadow: 0 4px 12px rgba(30, 136, 229, 0.15);'>
        <h3 style='color: #1E88E5; margin-top: 0;'>🎫 Bet Slip</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.selected_parlay:
        parlay = st.session_state.selected_parlay
        
        st.markdown("### Selected Parlay")
        
        for leg in parlay['legs']:
            is_locked = any(l['id'] == leg['id'] for l in st.session_state.locked_legs)
            leg_class = 'locked-leg' if is_locked else 'leg-item'
            
            st.markdown(f"""
            <div class='{leg_class}'>
                <strong>{leg['display']}</strong><br>
                <small>{leg['market']} • {leg['price']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Odds display
        st.markdown(f"""
        <div style='background: #E8F5E9; padding: 1rem; border-radius: 6px; margin: 1rem 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <span style='color: #555;'>DraftKings Odds:</span>
                <span style='font-size: 1.5rem; font-weight: 700; color: #4CAF50;'>{parlay['odds_american']}</span>
            </div>
            <div style='text-align: right; color: #666; font-size: 0.85rem; margin-top: 0.25rem;'>
                {parlay['implied_probability']}% implied probability
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Bet amount
        bet_amount = st.number_input("Bet Amount ($)", min_value=1.0, value=10.0, step=1.0)
        
        # Payout calculation
        profit = calculate_payout(parlay['odds_american'], bet_amount)
        total_payout = bet_amount + profit
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); 
                    padding: 1rem; 
                    border-radius: 6px; 
                    color: white;
                    margin: 1rem 0;'>
            <div style='font-size: 0.9rem; opacity: 0.9;'>Potential Payout</div>
            <div style='font-size: 2rem; font-weight: 700; margin: 0.25rem 0;'>${total_payout:.2f}</div>
            <div style='font-size: 0.85rem; opacity: 0.9;'>Profit: ${profit:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎰 Place Bet on DraftKings", use_container_width=True):
            st.balloons()
            st.success("Bet placed! (Demo mode)")
        
        if st.button("Clear Selection", use_container_width=True):
            st.session_state.selected_parlay = None
            st.rerun()
    else:
        st.markdown("""
        <div style='background: #f5f5f5; 
                    padding: 2rem; 
                    border-radius: 8px; 
                    text-align: center;
                    color: #666;
                    border: 2px dashed #e0e0e0;'>
            <p>Select a parlay from the recommendations to see details here</p>
        </div>
        """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    st.subheader("🎯 Parlay Filters")
    
    # Number of legs filter
    st.markdown("**Number of Legs**")
    num_legs = st.slider(
        "Select range",
        min_value=2,
        max_value=6,
        value=(3, 5),
        help="Filter parlays by number of legs",
        key="num_legs_slider"
    )
    st.session_state.num_legs_filter = num_legs
    
    # Odds range filter
    st.markdown("**Total Odds Range**")
    odds_range = st.slider(
        "Select decimal odds range",
        min_value=1.2,
        max_value=100.0,
        value=(1.5, 50.0),
        step=0.5,
        help="Filter parlays by total odds",
        key="odds_range_slider"
    )
    st.session_state.odds_range_filter = odds_range
    
    st.divider()
    
    # Locked/Removed legs info
    if st.session_state.locked_legs:
        st.success(f"🔒 {len(st.session_state.locked_legs)} locked leg(s)")
    if st.session_state.removed_legs:
        st.error(f"❌ {len(st.session_state.removed_legs)} removed leg(s)")
    
    if st.session_state.locked_legs or st.session_state.removed_legs:
        if st.button("Clear All Locks/Removes", use_container_width=True):
            st.session_state.locked_legs = []
            st.session_state.removed_legs = []
            st.rerun()
    
    st.divider()
    
    st.header("ℹ️ About")
    st.markdown("""
    This AI Parlay Builder helps you create same-game parlays using natural language.
    
    **How to use:**
    1. Describe your betting thesis
    2. Adjust filters if needed
    3. Lock/remove legs to refine
    4. Regenerate for new options
    
    **Example queries:**
    - "Knicks will win in a blowout"
    - "High scoring game, Brunson goes off"
    - "Pacers win and Haliburton has a big game"
    """)
    
    st.divider()
    
    if st.button("🔄 Reload Games", use_container_width=True):
        st.session_state.events = []
        st.session_state.chat_history = []
        st.session_state.recommendations = []
        st.session_state.locked_legs = []
        st.session_state.removed_legs = []
        load_events()
        st.rerun()
    
    st.caption(f"Games loaded: {len(st.session_state.events)}")
