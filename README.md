# PhoenixPlaylist

A full-stack web application that recognizes songs, classifies them by mood using natural language processing and genre-based audio profiling, and saves the resulting playlists to a local relational database. Built with Python, Flask, and SQL.

---

## Features

- Song lookup via the iTunes Search API (no authentication, no API key required)
- Mood classification combining VADER sentiment analysis on song titles with a genre-derived energy and valence model
- Auto-generates four mood-based playlist categories: Happy, Sad, Energetic, Chill
- Local playlist persistence in a SQLite relational database
- Per-mood statistics and expandable playlist history with full track-level mood metrics
- Optional Spotify OAuth 2.0 hook for future playlist export (disabled by default)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask 3 |
| Database | SQL (SQLite3 with raw queries) |
| NLP | NLTK VADER sentiment analyzer |
| External API | iTunes Search API |
| Frontend | HTML, CSS, Vanilla JavaScript |

---

## Project Structure

```
PhoenixPlaylist/
├── backend/
│   ├── app.py                  # Flask application and all API routes
│   ├── config.py               # Environment variable loading
│   ├── database.py             # SQL schema, connections, and queries
│   ├── itunes_client.py        # iTunes Search API wrapper
│   ├── spotify_client.py       # Optional Spotify OAuth wrapper
│   └── playlist_manager.py     # Core orchestration logic
├── frontend/
│   ├── templates/index.html
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── models/
│   └── mood_analyzer.py        # VADER + genre-feature mood classifier
├── .env.example
├── requirements.txt
└── README.md
```

---

## Database Schema

Three tables linked by foreign keys with cascading deletes and indexes on lookup columns.

**users**
| Column | Type | Notes |
|---|---|---|
| id | INTEGER | Primary key |
| spotify_id | TEXT | Unique identifier (or local_default) |
| email | TEXT | |
| display_name | TEXT | |
| created_at | TEXT | UTC datetime |

**playlists**
| Column | Type | Notes |
|---|---|---|
| id | INTEGER | Primary key |
| user_id | INTEGER | FK to users (CASCADE delete) |
| playlist_name | TEXT | |
| mood_category | TEXT | happy / sad / energetic / chill |
| track_count | INTEGER | |
| created_at | TEXT | UTC datetime |

**tracks**
| Column | Type | Notes |
|---|---|---|
| id | INTEGER | Primary key |
| playlist_id | INTEGER | FK to playlists (CASCADE delete) |
| track_name | TEXT | |
| artist | TEXT | |
| genre | TEXT | |
| mood_score | REAL | VADER compound score |
| energy | REAL | Estimated from genre |
| valence | REAL | Estimated from genre |
| album_image_url | TEXT | |

Race-safe inserts use SQL `ON CONFLICT` upserts. Indexes on `user_id`, `mood_category`, and `playlist_id` for fast lookups.

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/RaunakSinghSoi/Phoenix-Playlist.git
cd Phoenix-Playlist
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run

```bash
python -m backend.app
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser. No API keys or accounts required for the core flow.

### 3. Optional: enable Spotify OAuth

Copy `.env.example` to `.env` and fill in `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` from [developer.spotify.com](https://developer.spotify.com/dashboard). Add `http://127.0.0.1:5000/callback` as a Redirect URI in the Spotify app settings.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Web UI |
| POST | `/api/recognize` | Recognize and classify a single track |
| POST | `/api/playlist/generate` | Batch classify songs into mood buckets |
| POST | `/api/playlist/save` | Persist a generated playlist to the database |
| GET | `/api/history` | Retrieve current user's saved playlists |
| GET | `/api/history/<id>/tracks` | Retrieve all tracks for a saved playlist |
| GET | `/api/history/stats` | Per-mood playlist and track counts |
| GET | `/api/auth/spotify` | Optional Spotify OAuth flow |
| GET | `/api/health` | Health check |

### Example

```bash
curl -X POST http://127.0.0.1:5000/api/recognize \
  -H "Content-Type: application/json" \
  -d '{"query": "Headlines Drake"}'
```

```json
{
  "track": {
    "name": "Headlines",
    "artist": "Drake",
    "genre": "Hip-Hop/Rap",
    "album_image": "https://...",
    "preview_url": "https://..."
  },
  "audio_features": { "energy": 0.7, "valence": 0.5 },
  "mood": { "mood": "energetic", "label": "Energetic & Pumped", "confidence": 0.58 }
}
```

---

## Mood Classification

Each track is scored across all four moods using a weighted combination of three signals, then assigned to the highest-scoring category.

| Signal | Source |
|---|---|
| VADER compound score | NLTK sentiment analysis on the track title |
| Energy | Genre-derived value on a 0 to 1 scale |
| Valence | Genre-derived value on a 0 to 1 scale |

| Mood | Primary signals |
|---|---|
| Happy | High valence, positive sentiment, moderate energy |
| Sad | Negative sentiment, low valence, low energy |
| Energetic | High energy, positive or neutral sentiment |
| Chill | Low energy, neutral sentiment, mid valence |

---

## License

MIT
