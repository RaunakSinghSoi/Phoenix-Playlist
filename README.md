# PhoenixPlaylist

A full-stack web application that recognizes songs, classifies them by mood using natural language processing and genre-based audio profiling, and automatically generates themed Spotify playlists. User history and playlist data are persisted in a local SQLite database.

---

## Features

- Song lookup via the iTunes Search API (no authentication required)
- Mood classification combining VADER sentiment analysis on song titles with a genre-derived energy and valence model
- Auto-generates four mood-based playlist categories: Happy, Sad, Energetic, Chill
- Spotify OAuth 2.0 integration to push generated playlists directly to a user's account
- SQLite database tracking users, playlists, and individual tracks across sessions
- Playlist history dashboard with per-mood statistics

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask 3 |
| Database | SQLite3 with raw SQL |
| NLP | NLTK VADER sentiment analyzer |
| External APIs | iTunes Search API, Spotify Web API |
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
│   ├── itunes_client.py        # iTunes Search API wrapper
│   ├── spotify_client.py       # Spotify API and OAuth wrapper
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

**users**: id, spotify_id, email, display_name, created_at
**playlists**: id, user_id, playlist_name, mood_category, spotify_uri, spotify_url, track_count, created_at
**tracks**: id, playlist_id, track_name, artist, spotify_uri, mood_score, energy, valence, genre, album_image_url, created_at

Foreign keys cascade on delete. Indexes on user_id, mood_category, and playlist_id for fast lookups.

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

### 2. Get Spotify credentials (only needed if you want playlist push)

1. Create an app at [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Add `http://127.0.0.1:5000/callback` as a Redirect URI
3. Enable Web API under "APIs used"
4. Copy your Client ID and Client Secret into `.env`

### 3. Run

```bash
cp .env.example .env
# Fill in SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET if you want push
python -m backend.app
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

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
| GET | `/api/history` | Retrieve current user's saved playlists |
| GET | `/api/history/stats` | Per-mood playlist and track counts |
| GET | `/api/health` | Health check |

---

## Mood Classification

The classifier scores each track across all four moods using a weighted combination of three signals:

1. **VADER compound score** on the track title (-1 to +1)
2. **Energy** derived from genre (0 to 1)
3. **Valence** derived from genre (0 to 1)

| Mood | Primary signals |
|---|---|
| Happy | High valence, positive VADER score, moderate energy |
| Sad | Negative VADER score, low valence, low energy |
| Energetic | High energy, positive or neutral sentiment |
| Chill | Low energy, neutral sentiment, mid valence |

Each track is assigned to the highest-scoring mood with a confidence percentage.

---

## License

MIT
