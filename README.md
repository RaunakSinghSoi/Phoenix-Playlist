# PhoenixPlaylist

A full-stack web application that recognizes songs, classifies them by mood using NLP and audio analysis, and automatically generates themed Spotify playlists. User history and playlist data are persisted in a local SQLite database.

---

## Features

- Song lookup via the Shazam API (RapidAPI)
- Mood classification combining VADER sentiment analysis on lyrics with Spotify audio features (energy, valence, tempo)
- Auto-generates four mood-based playlist categories: Happy, Sad, Energetic, Chill
- Spotify OAuth 2.0 integration to push generated playlists directly to a user's account
- SQLite database tracking users, playlists, and individual tracks across sessions
- Playlist history dashboard with per-mood statistics

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask 3 |
| Database | SQLite3 (built-in), raw SQL |
| Mood Analysis | NLTK VADER, Spotify audio features |
| External APIs | Shazam API (RapidAPI), Spotify Web API |
| Auth | Spotify OAuth 2.0 Authorization Code Flow |
| Frontend | HTML, CSS, Vanilla JavaScript |

---

## Project Structure

```
PhoenixPlaylist/
├── backend/
│   ├── app.py                  # Flask application and all API routes
│   ├── config.py               # Environment variable loading
│   ├── database.py             # SQLite schema, connections, and queries
│   ├── shazam_client.py        # Shazam API wrapper
│   ├── spotify_client.py       # Spotify API and OAuth wrapper
│   └── playlist_manager.py     # Core logic orchestrating recognition, mood, and Spotify
├── frontend/
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── models/
│   └── mood_analyzer.py        # VADER + audio feature mood classifier
├── .env.example
├── requirements.txt
└── README.md
```

---

## Database Schema

**users**
| Column | Type | Notes |
|---|---|---|
| id | INTEGER | Primary key |
| spotify_id | TEXT | Unique Spotify user ID |
| email | TEXT | |
| display_name | TEXT | |
| created_at | TEXT | UTC datetime |

**playlists**
| Column | Type | Notes |
|---|---|---|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key -> users |
| playlist_name | TEXT | |
| mood_category | TEXT | happy / sad / energetic / chill |
| spotify_uri | TEXT | Spotify playlist ID |
| spotify_url | TEXT | Direct Spotify link |
| track_count | INTEGER | |
| created_at | TEXT | UTC datetime |

**tracks**
| Column | Type | Notes |
|---|---|---|
| id | INTEGER | Primary key |
| playlist_id | INTEGER | Foreign key -> playlists |
| track_name | TEXT | |
| artist | TEXT | |
| spotify_uri | TEXT | |
| mood_score | REAL | VADER compound score |
| energy | REAL | Spotify audio feature |
| valence | REAL | Spotify audio feature |
| genre | TEXT | |
| album_image_url | TEXT | |

---

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/RaunakSinghSoi/Phoenix-Playlist.git
cd Phoenix-Playlist
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Obtain API credentials

**Shazam (RapidAPI)**
1. Create an account at [rapidapi.com](https://rapidapi.com)
2. Subscribe to the Shazam API
3. Copy your `X-RapidAPI-Key`

**Spotify**
1. Create an app at [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Under app settings, add `http://localhost:5000/callback` as a Redirect URI
3. Copy your Client ID and Client Secret

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```
RAPIDAPI_KEY=your_key_here
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:5000/callback
FLASK_SECRET_KEY=any_random_string
```

### 4. Run

```bash
python -m backend.app
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Web UI |
| GET | `/auth/spotify` | Initiate Spotify OAuth flow |
| GET | `/callback` | Spotify OAuth redirect handler |
| POST | `/api/recognize` | Recognize and classify a single track |
| POST | `/api/playlist/generate` | Batch classify songs into mood buckets |
| POST | `/api/playlist/push` | Create a Spotify playlist from a mood bucket |
| GET | `/api/history` | Retrieve the current user's saved playlists |
| GET | `/api/history/<id>/tracks` | Retrieve tracks for a specific playlist |
| GET | `/api/history/stats` | Per-mood playlist and track counts |
| GET | `/api/health` | Health check |

### Example request

```bash
curl -X POST http://localhost:5000/api/recognize \
  -H "Content-Type: application/json" \
  -d '{"query": "Blinding Lights The Weeknd"}'
```

```json
{
  "shazam": { "title": "Blinding Lights", "artist": "The Weeknd", "genre": "Pop" },
  "spotify": { "uri": "spotify:track:...", "popularity": 95 },
  "audio_features": { "energy": 0.73, "valence": 0.33, "tempo": 171.0 },
  "mood": { "mood": "energetic", "label": "Energetic & Pumped", "confidence": 0.62 }
}
```

---

## Mood Classification

The classifier in `models/mood_analyzer.py` scores each track across all four moods using a weighted combination of signals, then assigns the highest-scoring category.

| Mood | Primary signals |
|---|---|
| Happy | High valence, positive VADER compound, moderate energy |
| Sad | Negative compound, low valence, low energy |
| Energetic | High energy, neutral or positive sentiment |
| Chill | Low energy, neutral sentiment, mid valence |

---

## License

MIT
