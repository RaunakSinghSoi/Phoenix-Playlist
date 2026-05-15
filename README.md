# 🔥 PhoenixPlaylist

> Recognize songs, analyze their mood with AI, and auto-generate Spotify playlists — all from a single web app.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)
![Spotify](https://img.shields.io/badge/Spotify_API-green?logo=spotify)
![Shazam](https://img.shields.io/badge/Shazam_API-blue?logo=shazam)
![VADER](https://img.shields.io/badge/VADER_NLP-NLTK-yellow)

---

## What it does

PhoenixPlaylist combines three APIs and an NLP mood engine to automatically sort songs into themed playlists:

| Feature | How |
|---|---|
| Song recognition | Shazam API (via RapidAPI) — search by title/artist |
| Mood classification | VADER sentiment analysis on lyrics + Spotify audio features (energy, valence, tempo) |
| Playlist generation | Groups tracks into **Happy**, **Sad**, **Energetic**, **Chill** |
| Spotify push | Creates a real Spotify playlist in your account via OAuth |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask 3 |
| Mood AI | NLTK VADER Sentiment Analyzer |
| Song Data | Shazam API (RapidAPI), Spotify Web API |
| Frontend | Vanilla HTML/CSS/JS (served by Flask) |
| Auth | Spotify OAuth 2.0 Authorization Code Flow |

---

## Project Structure

```
PhoenixPlaylist/
├── backend/
│   ├── app.py              # Flask app + all API routes
│   ├── config.py           # Environment variable loading
│   ├── shazam_client.py    # Shazam API wrapper
│   ├── spotify_client.py   # Spotify API + OAuth wrapper
│   └── playlist_manager.py # Orchestrates recognition + mood + Spotify
├── frontend/
│   ├── templates/
│   │   └── index.html      # Single-page UI (Jinja2)
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── models/
│   └── mood_analyzer.py    # VADER + audio feature mood classifier
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/RaunakSinghSoi/PhoenixPlaylist.git
cd PhoenixPlaylist
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Get API keys

**Shazam (RapidAPI)**
1. Sign up at [rapidapi.com](https://rapidapi.com/apidojo/api/shazam)
2. Subscribe to the Shazam API (free tier available)
3. Copy your `X-RapidAPI-Key`

**Spotify**
1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Add `http://localhost:5000/callback` to Redirect URIs
4. Copy your Client ID and Client Secret

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your actual keys
```

### 4. Run

```bash
python -m backend.app
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web UI |
| `GET` | `/auth/spotify` | Start Spotify OAuth flow |
| `GET` | `/callback` | Spotify OAuth callback |
| `POST` | `/api/recognize` | Recognize + classify a single track |
| `POST` | `/api/playlist/generate` | Batch classify songs into mood buckets |
| `POST` | `/api/playlist/push` | Push a mood playlist to Spotify |
| `GET` | `/api/health` | Health check |

### Example: Recognize a track

```bash
curl -X POST http://localhost:5000/api/recognize \
  -H "Content-Type: application/json" \
  -d '{"query": "Blinding Lights The Weeknd"}'
```

```json
{
  "shazam": { "title": "Blinding Lights", "artist": "The Weeknd", ... },
  "spotify": { "uri": "spotify:track:...", "popularity": 95, ... },
  "audio_features": { "energy": 0.73, "valence": 0.33, "tempo": 171.0 },
  "mood": { "mood": "energetic", "label": "Energetic & Pumped", "confidence": 0.62 }
}
```

---

## Mood Classification Logic

The `MoodAnalyzer` (`models/mood_analyzer.py`) scores each track across four moods using a weighted combination of:

- **VADER compound score** — sentiment polarity of the lyrics (`-1` to `+1`)
- **Spotify energy** — perceptual measure of intensity and activity (`0`–`1`)
- **Spotify valence** — musical positiveness (`0`–`1`)

| Mood | Signals |
|---|---|
| Happy | High valence, positive compound, moderate energy |
| Sad | Negative compound, low valence, low energy |
| Energetic | High energy, positive/neutral sentiment |
| Chill | Low energy, neutral sentiment, mid valence |

---

## License

MIT
