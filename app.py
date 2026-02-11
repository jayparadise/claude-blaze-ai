import streamlit as st
import requests
import json
import random
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="BlazeBuilder – SGP Parlay Builder",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── API Configuration ───────────────────────────────────────────────
API_KEY = '10019992-c9b1-46b5-be2c-9e760b1c2041'
ODDS_API_URL = 'https://odds.oddsblaze.com/'           # Odds endpoint
SGP_API_TPL  = 'https://{sportsbook}.sgp.oddsblaze.com/'  # SGP endpoint
# ACTIVE_API = 'https://active.markets.oddsblaze.com/'  # Available if needed
DEFAULT_SPORTSBOOK = 'draftkings'
DEFAULT_LEAGUE = 'nba'

# ─── Custom CSS – Dark Sports-Dashboard Theme ────────────────────────
st.markdown("""
<style>
/* ── Import Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,500;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Root Variables ── */
:root {
    --bg-primary: #0B0E14;
    --bg-card: #141820;
    --bg-card-hover: #1A1F2B;
    --bg-input: #1A1F2B;
    --border: #252B37;
    --border-accent: #2D3548;
    --text-primary: #F0F2F5;
    --text-secondary: #8A92A6;
    --text-muted: #555D70;
    --accent-green: #00E676;
    --accent-green-dim: rgba(0,230,118,0.12);
    --accent-blue: #448AFF;
    --accent-blue-dim: rgba(68,138,255,0.12);
    --accent-orange: #FF9100;
    --accent-orange-dim: rgba(255,145,0,0.12);
    --accent-red: #FF5252;
    --accent-red-dim: rgba(255,82,82,0.12);
    --radius-sm: 8px;
    --radius-md: 14px;
    --radius-lg: 20px;
    --shadow-card: 0 4px 24px rgba(0,0,0,0.35);
    --shadow-glow-green: 0 0 20px rgba(0,230,118,0.15);
}

/* ── Global Reset ── */
.stApp {
    background-color: var(--bg-primary) !important;
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text-primary);
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden !important; }
.block-container { padding: 1.5rem 2rem 5rem 2rem; max-width: 1400px; }

/* ── Typography ── */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
    letter-spacing: -0.03em;
}
h1 { font-weight: 700 !important; font-size: 1.75rem !important; }
h2 { font-weight: 600 !important; font-size: 1.25rem !important; }
h3 { font-weight: 600 !important; font-size: 1.05rem !important; }
p, label, span { color: var(--text-secondary) !important; }

/* ── Header Bar ── */
.app-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}
.app-header .logo {
    font-size: 1.65rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.04em;
}
.app-header .logo span { color: var(--accent-green); }
.app-header .subtitle {
    font-size: 0.82rem;
    color: var(--text-muted);
    margin-left: auto;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Inputs ── */
.stTextInput input, .stNumberInput input, .stSelectbox > div > div {
    background-color: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-size: 0.95rem !important;
    padding: 10px 14px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--accent-green) !important;
    box-shadow: 0 0 0 2px var(--accent-green-dim) !important;
}
.stTextInput input::placeholder { color: var(--text-muted) !important; }

/* ── Buttons ── */
.stButton > button {
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    border: 1px solid var(--border) !important;
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
    padding: 8px 20px !important;
    transition: all 0.15s ease !important;
    font-size: 0.88rem !important;
}
.stButton > button:hover {
    background-color: var(--bg-card-hover) !important;
    border-color: var(--accent-green) !important;
    color: var(--accent-green) !important;
}
.stButton > button:active { transform: scale(0.97); }

/* Generate button override */
div[data-testid="stForm"] .stButton > button {
    background: linear-gradient(135deg, #00C853, #00E676) !important;
    color: #0B0E14 !important;
    border: none !important;
    font-size: 1rem !important;
    padding: 12px 24px !important;
    border-radius: var(--radius-md) !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em;
    box-shadow: var(--shadow-glow-green);
}
div[data-testid="stForm"] .stButton > button:hover {
    color: #0B0E14 !important;
    box-shadow: 0 0 30px rgba(0,230,118,0.3);
}

/* ── Parlay Card ── */
.parlay-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px;
    margin-bottom: 16px;
    transition: all 0.2s ease;
    box-shadow: var(--shadow-card);
}
.parlay-card:hover {
    border-color: var(--accent-green);
    box-shadow: var(--shadow-card), var(--shadow-glow-green);
}
.parlay-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
}

/* ── Odds Badge ── */
.odds-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, #00C853, #00E676);
    color: #0B0E14;
    padding: 6px 16px;
    border-radius: 100px;
    font-weight: 800;
    font-size: 1.05rem;
    font-family: 'JetBrains Mono', monospace;
    box-shadow: 0 2px 12px rgba(0,230,118,0.25);
    letter-spacing: -0.02em;
}
.odds-badge-pending {
    background: var(--bg-input);
    color: var(--text-muted);
    border: 1px dashed var(--border);
    box-shadow: none;
}

/* ── Meta Chips ── */
.meta-chip {
    display: inline-block;
    background: var(--bg-input);
    color: var(--text-secondary);
    padding: 3px 10px;
    border-radius: 100px;
    font-size: 0.75rem;
    font-weight: 500;
    margin-right: 6px;
    border: 1px solid var(--border);
}

/* ── Leg Item ── */
.leg-item {
    background: var(--bg-input);
    border-radius: var(--radius-sm);
    padding: 10px 14px;
    margin-bottom: 6px;
    border-left: 3px solid var(--accent-blue);
    transition: all 0.15s ease;
}
.leg-item:hover { background: var(--bg-card-hover); }
.leg-item .leg-name {
    color: var(--text-primary);
    font-weight: 600;
    font-size: 0.88rem;
}
.leg-item .leg-meta {
    color: var(--text-muted);
    font-size: 0.78rem;
    margin-top: 2px;
    font-family: 'JetBrains Mono', monospace;
}
.locked-leg { border-left-color: var(--accent-orange); background: var(--accent-orange-dim); }
.removed-leg { border-left-color: var(--accent-red); opacity: 0.45; }

/* ── Bet Slip ── */
.bet-slip {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 22px;
    box-shadow: var(--shadow-card);
    position: sticky;
    top: 1.5rem;
}
.bet-slip-empty {
    text-align: center;
    padding: 3rem 1rem;
    color: var(--text-muted);
}
.bet-slip-empty .icon { font-size: 2rem; margin-bottom: 8px; }

/* ── Divider ── */
.divider {
    height: 1px;
    background: var(--border);
    margin: 14px 0;
    border: none;
}

/* ── Payout Row ── */
.payout-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
}
.payout-row .label { color: var(--text-muted); font-size: 0.85rem; }
.payout-row .value {
    color: var(--text-primary);
    font-weight: 700;
    font-size: 1rem;
    font-family: 'JetBrains Mono', monospace;
}
.payout-row .value.green { color: var(--accent-green); }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: var(--bg-card) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: var(--text-primary) !important; }
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label { color: var(--text-secondary) !important; }

/* Slider track overrides */
.stSlider [data-baseweb="slider"] div { background-color: var(--border) !important; }

/* ── Status Messages ── */
.sgp-status {
    font-size: 0.78rem;
    font-family: 'JetBrains Mono', monospace;
    padding: 4px 10px;
    border-radius: 6px;
    display: inline-block;
}
.sgp-status.success { background: var(--accent-green-dim); color: var(--accent-green); }
.sgp-status.error { background: var(--accent-red-dim); color: var(--accent-red); }
.sgp-status.pending { background: var(--accent-blue-dim); color: var(--accent-blue); }

/* ── Game Selector Cards ── */
.game-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: 100px;
    font-size: 0.82rem;
    color: var(--text-secondary);
    font-weight: 500;
    white-space: nowrap;
}
.game-pill.active {
    border-color: var(--accent-green);
    color: var(--accent-green);
    background: var(--accent-green-dim);
}

/* ── Scrollbar Styling ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* ── Expander ── */
.streamlit-expanderHeader { 
    background: var(--bg-input) !important; 
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
}

/* ── Columns gap fix ── */
[data-testid="stHorizontalBlock"] { gap: 12px; }

/* ── Mobile ── */
@media (max-width: 768px) {
    .block-container { padding: 1rem 1rem 4rem 1rem; }
    .parlay-card { padding: 14px; }
    .bet-slip { position: relative; }
}
</style>
""", unsafe_allow_html=True)

# ─── Session State Initialization ─────────────────────────────────────
defaults = {
    'games': [],
    'selected_game': None,
    'chat_history': [],
    'recommendations': [],
    'locked_legs': [],
    'removed_legs': [],
    'selected_parlay': None,
    'bet_amount': 10.0,
    'num_legs_filter': (3, 5),
    'odds_range_filter': (1.5, 50.0),
    'sportsbook': DEFAULT_SPORTSBOOK,
    'league': DEFAULT_LEAGUE,
    'sgp_prices': {},  # parlay_id -> sgp price
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ═══════════════════════════════════════════════════════════════════════
# API FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def load_games():
    """Load games from OddsBlaze API."""
    try:
        sportsbook = st.session_state.sportsbook
        league = st.session_state.league
        url = f"{ODDS_API_URL}?key={API_KEY}&league={league}&sportsbook={sportsbook}"
        response = requests.get(url, timeout=15)

        if response.status_code != 200:
            st.error(f"API returned {response.status_code}. Check your API key or plan.")
            return False

        data = response.json()

        # Handle both response formats:
        # Format A (odds.oddsblaze.com): { "events": [ { ..., "odds": [...] } ] }
        # Format B (data.oddsblaze.com): { "games": [ { ..., "sportsbooks": [ { "odds": [...] } ] } ] }
        games = data.get('events') or data.get('games') or []

        if not games:
            st.warning("No games found for the selected league/sportsbook.")
            return False

        # If using Format B, flatten sportsbook odds onto each game
        for game in games:
            if 'odds' not in game and 'sportsbooks' in game:
                flat_odds = []
                for sb in game.get('sportsbooks', []):
                    if sb.get('id') == sportsbook:
                        flat_odds = sb.get('odds', [])
                        break
                game['odds'] = flat_odds

        st.session_state.games = games
        return True

    except Exception as e:
        st.error(f"Error loading games: {str(e)}")
        return False


def fetch_sgp_price(sgp_tokens, sportsbook=None):
    """
    Call the OddsBlaze SGP BlazeBuilder endpoint.
    
    POST https://{sportsbook}.sgp.oddsblaze.com/?key=API_KEY
    Body: JSON array of sgp token strings
    
    Returns dict: {"price": "+425"} or {"message": "..."} or None on error
    """
    sportsbook = sportsbook or st.session_state.sportsbook
    url = SGP_API_TPL.format(sportsbook=sportsbook) + f"?key={API_KEY}"

    try:
        response = requests.post(
            url,
            json=sgp_tokens,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"message": str(e)}


# ═══════════════════════════════════════════════════════════════════════
# NARRATIVE PARSER
# ═══════════════════════════════════════════════════════════════════════

def parse_narrative(narrative, force_event=None):
    """Parse user input to understand betting intent."""
    lower = narrative.lower()
    games = st.session_state.games

    # Resolve the target game
    if force_event:
        target = force_event
    else:
        target = None
        for game in games:
            home = game['teams']['home']
            away = game['teams']['away']
            names = [
                home['name'].lower(), away['name'].lower(),
                home.get('abbreviation', '').lower(), away.get('abbreviation', '').lower()
            ]
            words = home['name'].lower().split() + away['name'].lower().split()
            sig_words = [w for w in words if len(w) > 3]

            if any(n in lower for n in names) or any(w in lower for w in sig_words):
                target = game
                break

    if not target:
        return None

    # Determine winning team
    winning_team = None
    win_words = ['win', 'beat', 'dominate', 'destroy', 'crush', 'cover']
    if any(w in lower for w in win_words):
        home_name = target['teams']['home']['name']
        away_name = target['teams']['away']['name']
        home_match = (home_name.lower() in lower or
                      target['teams']['home'].get('abbreviation', '').lower() in lower or
                      any(w in lower for w in home_name.lower().split() if len(w) > 3))
        away_match = (away_name.lower() in lower or
                      target['teams']['away'].get('abbreviation', '').lower() in lower or
                      any(w in lower for w in away_name.lower().split() if len(w) > 3))
        if home_match and not away_match:
            winning_team = home_name
        elif away_match and not home_match:
            winning_team = away_name

    is_high = any(w in lower for w in ['high scoring', 'shootout', 'offensive', 'lots of points', 'over'])
    is_low = any(w in lower for w in ['low scoring', 'defensive', 'grind', 'under'])
    is_blowout = any(w in lower for w in ['blowout', 'dominate', 'destroy', 'crush'])

    # Player detection
    players = []
    seen_players = set()
    for odd in target.get('odds', []):
        player = odd.get('player')
        if player and isinstance(player, str) and player not in seen_players:
            parts = player.lower().split()
            if any(p in lower for p in parts):
                has_pos = any(w in lower for w in ['score', 'big game', 'lots', 'great', 'over'])
                players.append({'name': player, 'sentiment': 'positive' if has_pos else 'neutral'})
                seen_players.add(player)

    return {
        'game': target,
        'winning_team': winning_team,
        'is_high_scoring': is_high,
        'is_low_scoring': is_low,
        'is_blowout': is_blowout,
        'players': players,
    }


# ═══════════════════════════════════════════════════════════════════════
# PARLAY GENERATOR  (builds legs, then prices via SGP API)
# ═══════════════════════════════════════════════════════════════════════

def generate_parlays(parsed, count=8, locked_legs=None, removed_legs=None,
                     num_legs_range=(3, 5), odds_range=(1.5, 50.0)):
    """Generate diverse parlay combinations, then fetch real SGP prices."""
    game = parsed['game']
    winning_team = parsed['winning_team']
    is_high = parsed['is_high_scoring']
    is_low = parsed['is_low_scoring']
    is_blowout = parsed['is_blowout']
    players = parsed['players']

    locked_legs = locked_legs or []
    removed_legs = removed_legs or []
    removed_ids = {l['id'] for l in removed_legs}

    all_odds = game.get('odds', [])
    valid_odds = [o for o in all_odds
                  if o.get('id') and o.get('market') and o.get('name') and o.get('price')
                  and o['id'] not in removed_ids]

    # We need odds with sgp tokens for SGP pricing
    sgp_odds = [o for o in valid_odds if o.get('sgp')]

    # If no sgp tokens at all, fall back to all valid odds (prices will be estimated)
    use_odds = sgp_odds if sgp_odds else valid_odds
    has_sgp_tokens = len(sgp_odds) > 0

    # Group by market
    by_market = {}
    for o in use_odds:
        m = o.get('market', 'Other')
        by_market.setdefault(m, []).append(o)

    min_legs, max_legs = num_legs_range
    parlays = []
    attempts = 0
    max_attempts = count * 20

    while len(parlays) < count and attempts < max_attempts:
        attempts += 1
        target_legs = random.randint(min_legs, max_legs)
        legs = list(locked_legs)
        used_ids = {l['id'] for l in legs}

        if len(legs) > target_legs:
            continue

        # Build weighted candidate pool
        candidates = []

        # Moneyline for predicted winner
        if winning_team:
            ml = [o for o in by_market.get('Moneyline', [])
                  if winning_team.lower() in o.get('name', '').lower() and o['id'] not in used_ids]
            if ml and random.random() < 0.8:
                candidates.append(random.choice(ml))

        # Spread
        spreads = [o for o in by_market.get('Point Spread', []) if o['id'] not in used_ids]
        if spreads and random.random() < (0.7 if is_blowout else 0.35):
            candidates.append(random.choice(spreads))

        # Totals
        side = 'Over' if is_high else ('Under' if is_low else random.choice(['Over', 'Under']))
        totals = [o for o in by_market.get('Total Points', [])
                  if side in o.get('name', '') and o['id'] not in used_ids]
        if totals and random.random() < (0.7 if (is_high or is_low) else 0.3):
            candidates.append(random.choice(totals))

        # Player props for mentioned players
        for p in players:
            p_odds = [o for o in use_odds if o.get('player') == p['name'] and o['id'] not in used_ids]
            if p_odds and random.random() < 0.85:
                candidates.append(random.choice(p_odds))

        # Random props for variety
        prop_markets = [m for m in by_market if m not in ('Moneyline', 'Point Spread', 'Total Points')]
        random.shuffle(prop_markets)
        for m in prop_markets[:4]:
            opts = [o for o in by_market[m] if o['id'] not in used_ids]
            if opts and random.random() < 0.4:
                candidates.append(random.choice(opts))

        # De-dup and trim
        for c in candidates:
            if c['id'] not in used_ids and len(legs) < target_legs:
                legs.append(c)
                used_ids.add(c['id'])

        # Fill remaining
        if len(legs) < target_legs:
            pool = [o for o in use_odds if o['id'] not in used_ids]
            random.shuffle(pool)
            for o in pool:
                if len(legs) >= target_legs:
                    break
                legs.append(o)
                used_ids.add(o['id'])

        if not (min_legs <= len(legs) <= max_legs):
            continue

        # Duplicate check
        leg_set = frozenset(l['id'] for l in legs)
        if any(frozenset(p['leg_ids']) == leg_set for p in parlays):
            continue

        # Collect sgp tokens for this parlay
        sgp_tokens = [l.get('sgp') for l in legs if l.get('sgp')]

        # Fallback: calculate naive odds (will be replaced by SGP price)
        naive_dec = 1.0
        try:
            for l in legs:
                price = l.get('price', '+100')
                if isinstance(price, str):
                    if price.startswith('+'):
                        naive_dec *= (int(price[1:]) / 100) + 1
                    elif price.startswith('-'):
                        naive_dec *= (100 / abs(int(price[1:]))) + 1
                    else:
                        naive_dec *= float(price)
                else:
                    naive_dec *= float(price)
        except (ValueError, ZeroDivisionError):
            continue

        parlays.append({
            'id': f'parlay-{len(parlays)}',
            'legs': legs,
            'leg_ids': leg_set,
            'sgp_tokens': sgp_tokens,
            'has_sgp': len(sgp_tokens) == len(legs) and has_sgp_tokens,
            'naive_decimal_odds': round(naive_dec, 2),
            'sgp_price': None,       # filled in after API call
            'sgp_status': 'pending',  # pending | success | error | no_tokens
        })

    # ── Fetch SGP prices from OddsBlaze ──
    for p in parlays:
        if p['has_sgp'] and p['sgp_tokens']:
            result = fetch_sgp_price(p['sgp_tokens'])
            if result and 'price' in result:
                p['sgp_price'] = result['price']
                p['sgp_status'] = 'success'
            elif result and 'message' in result:
                p['sgp_status'] = 'error'
                p['sgp_error'] = result['message']
            else:
                p['sgp_status'] = 'error'
        else:
            p['sgp_status'] = 'no_tokens'

    return parlays


def get_display_odds(parlay):
    """Get the best available odds string for a parlay."""
    if parlay.get('sgp_price'):
        return parlay['sgp_price']
    # Fallback to naive calculation
    dec = parlay.get('naive_decimal_odds', 2.0)
    if dec >= 2:
        return f"+{int((dec - 1) * 100)}"
    elif dec > 1:
        return f"-{int(100 / (dec - 1))}"
    return "+100"


def calculate_payout(odds_str, amount):
    """Calculate profit from American odds string."""
    try:
        odds_str = str(odds_str)
        if odds_str.startswith('+'):
            return amount * (int(odds_str[1:]) / 100)
        elif odds_str.startswith('-'):
            return amount * (100 / int(odds_str[1:]))
        return 0
    except:
        return 0


# ═══════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="app-header">
    <div class="logo">🔥 Blaze<span>Builder</span></div>
    <div class="subtitle">SGP PARLAY ENGINE</div>
</div>
""", unsafe_allow_html=True)

# ── Load games on first run ──
if not st.session_state.games:
    with st.spinner("Loading games from OddsBlaze..."):
        load_games()


# ═══════════════════════════════════════════════════════════════════════
# MAIN LAYOUT
# ═══════════════════════════════════════════════════════════════════════
col_main, col_slip = st.columns([5, 2])

with col_main:
    # ── Input Form ──
    with st.form(key='parlay_form', clear_on_submit=True):
        user_input = st.text_input(
            "prompt",
            placeholder="e.g. 'Knicks win big, Brunson scores a lot, high-scoring game'",
            label_visibility="collapsed",
        )
        submit = st.form_submit_button("⚡ Generate Parlays", use_container_width=True)

        if submit and user_input:
            st.session_state.chat_history.append({'role': 'user', 'content': user_input})
            parsed = parse_narrative(user_input, force_event=st.session_state.selected_game)

            if not parsed:
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': "Couldn't identify a game. Select one from the sidebar or mention a team name."
                })
            else:
                with st.spinner("Building parlays & fetching SGP prices..."):
                    parlays = generate_parlays(
                        parsed, 8,
                        locked_legs=st.session_state.locked_legs,
                        removed_legs=st.session_state.removed_legs,
                        num_legs_range=st.session_state.num_legs_filter,
                        odds_range=st.session_state.odds_range_filter,
                    )
                st.session_state.recommendations = parlays
                st.session_state.sgp_prices = {}
            st.rerun()

    # ── Error messages ──
    for msg in st.session_state.chat_history:
        if msg['role'] == 'assistant':
            st.warning(msg['content'])

    # ── Parlay Results ──
    if st.session_state.recommendations:
        col_title, col_regen = st.columns([4, 1])
        with col_title:
            total = len(st.session_state.recommendations)
            sgp_count = sum(1 for p in st.session_state.recommendations if p.get('sgp_status') == 'success')
            st.markdown(
                f"<h2 style='margin:0;'>{total} Parlays Generated</h2>"
                f"<p style='margin:2px 0 12px 0; font-size:0.82rem;'>"
                f"<span class='sgp-status success'>{sgp_count} SGP priced</span> "
                f"<span class='sgp-status pending'>{total - sgp_count} estimated</span></p>",
                unsafe_allow_html=True
            )
        with col_regen:
            if st.button("🔄 Regenerate", use_container_width=True, key="regen_btn"):
                for msg in reversed(st.session_state.chat_history):
                    if msg['role'] == 'user':
                        parsed = parse_narrative(msg['content'], force_event=st.session_state.selected_game)
                        if parsed:
                            with st.spinner("Regenerating..."):
                                parlays = generate_parlays(
                                    parsed, 8,
                                    locked_legs=st.session_state.locked_legs,
                                    removed_legs=st.session_state.removed_legs,
                                    num_legs_range=st.session_state.num_legs_filter,
                                    odds_range=st.session_state.odds_range_filter,
                                )
                            st.session_state.recommendations = parlays
                            st.rerun()
                        break

        # ── Render each parlay card ──
        for parlay in st.session_state.recommendations:
            odds_display = get_display_odds(parlay)
            is_sgp = parlay.get('sgp_status') == 'success'
            badge_class = 'odds-badge' if is_sgp else 'odds-badge odds-badge-pending'
            source_label = 'SGP' if is_sgp else 'EST'

            st.markdown(f"<div class='parlay-card'>", unsafe_allow_html=True)

            # Card header
            header_left, header_right = st.columns([3, 1])
            with header_left:
                st.markdown(
                    f"<div style='display:flex;align-items:center;gap:10px;'>"
                    f"<div class='{badge_class}'>{odds_display}</div>"
                    f"<div>"
                    f"<span class='meta-chip'>{len(parlay['legs'])} legs</span>"
                    f"<span class='meta-chip'>{source_label}</span>"
                    f"</div></div>",
                    unsafe_allow_html=True
                )
            with header_right:
                if st.button("＋ Slip", key=f"add_{parlay['id']}", use_container_width=True):
                    st.session_state.selected_parlay = parlay
                    st.rerun()

            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

            # Legs
            for idx, leg in enumerate(parlay['legs']):
                is_locked = any(l['id'] == leg['id'] for l in st.session_state.locked_legs)
                is_removed = any(l['id'] == leg['id'] for l in st.session_state.removed_legs)
                css = 'locked-leg' if is_locked else ('removed-leg' if is_removed else '')

                leg_col, lock_col, rm_col = st.columns([8, 0.6, 0.6])
                with leg_col:
                    player_str = f" · {leg['player']}" if leg.get('player') else ""
                    st.markdown(
                        f"<div class='leg-item {css}'>"
                        f"<div class='leg-name'>{leg.get('name', '')}</div>"
                        f"<div class='leg-meta'>{leg.get('market', '')}{player_str} · {leg.get('price', '')}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                with lock_col:
                    icon = "🔒" if is_locked else "🔓"
                    if st.button(icon, key=f"lk_{parlay['id']}_{idx}"):
                        if is_locked:
                            st.session_state.locked_legs = [l for l in st.session_state.locked_legs if l['id'] != leg['id']]
                        else:
                            st.session_state.locked_legs.append(leg)
                            st.session_state.removed_legs = [l for l in st.session_state.removed_legs if l['id'] != leg['id']]
                        st.rerun()
                with rm_col:
                    icon2 = "↩️" if is_removed else "✕"
                    if st.button(icon2, key=f"rm_{parlay['id']}_{idx}"):
                        if is_removed:
                            st.session_state.removed_legs = [l for l in st.session_state.removed_legs if l['id'] != leg['id']]
                        else:
                            st.session_state.removed_legs.append(leg)
                            st.session_state.locked_legs = [l for l in st.session_state.locked_legs if l['id'] != leg['id']]
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)  # close parlay-card


# ═══════════════════════════════════════════════════════════════════════
# BET SLIP (right column)
# ═══════════════════════════════════════════════════════════════════════
with col_slip:
    st.markdown("<div class='bet-slip'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin:0 0 4px 0;'>Bet Slip</h3>", unsafe_allow_html=True)

    if st.session_state.selected_parlay:
        parlay = st.session_state.selected_parlay
        odds_display = get_display_odds(parlay)
        is_sgp = parlay.get('sgp_status') == 'success'

        st.markdown(
            f"<div style='display:flex;align-items:center;justify-content:space-between;margin:8px 0;'>"
            f"<span class='meta-chip'>{len(parlay['legs'])} legs</span>"
            f"<span class='sgp-status {'success' if is_sgp else 'pending'}'>{'SGP PRICE' if is_sgp else 'ESTIMATED'}</span>"
            f"</div>",
            unsafe_allow_html=True
        )
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        for leg in parlay['legs']:
            player_str = f" · {leg['player']}" if leg.get('player') else ""
            st.markdown(
                f"<div class='leg-item'>"
                f"<div class='leg-name'>{leg.get('name', '')}</div>"
                f"<div class='leg-meta'>{leg.get('market', '')}{player_str} · {leg.get('price', '')}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        bet_amount = st.number_input("Stake ($)", min_value=1.0, value=10.0, step=5.0,
                                     label_visibility="visible", key="slip_stake")
        profit = calculate_payout(odds_display, bet_amount)
        total = bet_amount + profit

        st.markdown(
            f"<div class='payout-row'>"
            f"<span class='label'>Odds</span>"
            f"<span class='value'>{odds_display}</span>"
            f"</div>"
            f"<div class='payout-row'>"
            f"<span class='label'>Potential Profit</span>"
            f"<span class='value green'>${profit:,.2f}</span>"
            f"</div>"
            f"<div class='payout-row'>"
            f"<span class='label'>Total Payout</span>"
            f"<span class='value green'>${total:,.2f}</span>"
            f"</div>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        if st.button("Clear Slip", use_container_width=True, key="clear_slip"):
            st.session_state.selected_parlay = None
            st.rerun()
    else:
        st.markdown("""
        <div class='bet-slip-empty'>
            <div class='icon'>📋</div>
            <p style='margin:0;font-size:0.88rem;'>Add a parlay to your slip</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    # Sportsbook selector
    sportsbooks = ['draftkings', 'fanduel', 'betmgm', 'caesars', 'bet365', 'hard_rock']
    sb_idx = st.selectbox("Sportsbook", range(len(sportsbooks)),
                          format_func=lambda i: sportsbooks[i].replace('_', ' ').title(),
                          index=sportsbooks.index(st.session_state.sportsbook)
                          if st.session_state.sportsbook in sportsbooks else 0)
    if sportsbooks[sb_idx] != st.session_state.sportsbook:
        st.session_state.sportsbook = sportsbooks[sb_idx]
        st.session_state.games = []
        st.session_state.recommendations = []
        load_games()
        st.rerun()

    # League selector
    leagues = ['nba', 'nfl', 'mlb', 'nhl', 'ncaab', 'ncaaf']
    lg_idx = st.selectbox("League", range(len(leagues)),
                          format_func=lambda i: leagues[i].upper(),
                          index=leagues.index(st.session_state.league)
                          if st.session_state.league in leagues else 0)
    if leagues[lg_idx] != st.session_state.league:
        st.session_state.league = leagues[lg_idx]
        st.session_state.games = []
        st.session_state.recommendations = []
        load_games()
        st.rerun()

    st.markdown("---")

    # Game selector
    if st.session_state.games:
        st.markdown("### 🏟️ Select Game")
        game_options = ["Auto-detect from prompt"] + [
            f"{g['teams']['away'].get('abbreviation', '?')} @ {g['teams']['home'].get('abbreviation', '?')}"
            for g in st.session_state.games
        ]
        sel = st.selectbox("Game", range(len(game_options)),
                           format_func=lambda i: game_options[i],
                           label_visibility="collapsed")
        st.session_state.selected_game = None if sel == 0 else st.session_state.games[sel - 1]

    st.markdown("---")
    st.markdown("### 🎛️ Filters")

    num_legs = st.slider("Number of Legs", 2, 10, st.session_state.num_legs_filter)
    st.session_state.num_legs_filter = num_legs

    odds_range = st.slider("Decimal Odds Range", 1.2, 100.0,
                           st.session_state.odds_range_filter, step=0.5)
    st.session_state.odds_range_filter = odds_range

    st.markdown("---")

    # Locked / removed info
    if st.session_state.locked_legs:
        st.markdown(f"🔒 **{len(st.session_state.locked_legs)}** locked legs")
    if st.session_state.removed_legs:
        st.markdown(f"🚫 **{len(st.session_state.removed_legs)}** removed legs")
    if st.session_state.locked_legs or st.session_state.removed_legs:
        if st.button("Clear Locks & Removals", use_container_width=True):
            st.session_state.locked_legs = []
            st.session_state.removed_legs = []
            st.rerun()

    st.markdown("---")
    if st.button("🔄 Reload Games", use_container_width=True):
        st.session_state.games = []
        st.session_state.selected_game = None
        st.session_state.recommendations = []
        st.session_state.locked_legs = []
        st.session_state.removed_legs = []
        load_games()
        st.rerun()

    st.markdown(
        "<p style='margin-top:2rem;font-size:0.72rem;color:#555D70;text-align:center;'>"
        "Powered by OddsBlaze SGP BlazeBuilder API</p>",
        unsafe_allow_html=True
    )
