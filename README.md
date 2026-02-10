# AI Parlay Builder - Streamlit App

Build same-game parlays using AI and natural language with real DraftKings odds.

## 🚀 Quick Deploy to Streamlit Cloud

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub repo
   - Select `main` branch and `app.py`
   - Click "Deploy"!

Your app will be live at: `https://YOUR_APP.streamlit.app`

## 🧪 Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📝 Features

- ✅ Real-time NBA odds from OddsBlaze/DraftKings
- ✅ Natural language parlay generation
- ✅ AI-powered narrative parsing
- ✅ Interactive bet slip
- ✅ Parlay odds calculation

## 🎮 Example Queries

- "Knicks will dominate and win big"
- "High scoring game, Brunson scores lots of points"
- "Pacers win in a close game"
- "Blowout win for NYK and high total"

## 🔑 API Key

The app uses OddsBlaze API. The current trial key is valid for 24 hours.

To get your own key:
1. Visit [oddsblaze.com](https://oddsblaze.com)
2. Sign up for a trial or paid plan
3. Replace `API_KEY` in `app.py` with your key

## 📄 Files

- `app.py` - Main Streamlit application
- `requirements.txt` - Python dependencies
- `README.md` - This file

## 🛠️ Tech Stack

- Streamlit (UI)
- OddsBlaze API (Odds data)
- Python requests (API calls)

## ⚠️ Note

This is for educational/demo purposes. Always gamble responsibly.
