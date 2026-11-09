# Phoenix Playlist

Phoenix Playlist is a local web application for finding songs and organizing them into mood-based playlists. It searches the iTunes catalogue, uses song-title sentiment and genre-based estimates to group tracks, and saves playlists in SQLite for later browsing. I built it with Python, Flask, SQL, HTML, CSS, and JavaScript.

## What it does

- Finds songs through the iTunes Search API using a title or artist query.
- Groups matched tracks into happy, sad, energetic, and chill playlists.
- Uses NLTK VADER for title sentiment and a set of genre-based energy and valence estimates.
- Saves playlists and their tracks in a local SQLite database.
- Displays saved playlist history, track details, and counts by mood.
- Keeps an optional Spotify OAuth integration for future playlist export. Spotify export is not part of the main user flow.

Song identification here means a text search, not audio fingerprint recognition. The mood categories are rule-based estimates, not measurements of a song's actual emotional character or audio signal.

## Stack

- Python 3.11 and Flask 3
- SQLite and raw SQL
- NLTK VADER
- iTunes Search API
- HTML, CSS, and vanilla JavaScript
- Optional Spotify OAuth integration

## Project layout

```text
backend/
  app.py               Flask routes and JSON API
  config.py            Environment configuration
  database.py          SQLite schema and queries
  itunes_client.py     Song search
  playlist_manager.py  Song lookup, grouping, and playlist operations
  spotify_client.py    Optional Spotify integration
frontend/
  templates/index.html
  static/css/style.css
  static/js/app.js
models/
  mood_analyzer.py     Mood rules and genre feature estimates
requirements.txt
.env.example
```

## Run locally

Python 3.11 is recommended.

```bash
git clone https://github.com/RaunakSinghSoi/Phoenix-Playlist.git
cd Phoenix-Playlist
python -m venv .venv
```

Activate the environment with `source .venv/bin/activate` on macOS/Linux, or `.venv\Scripts\activate` in Windows PowerShell. Then install dependencies and start the app:

```bash
pip install -r requirements.txt
python -m backend.app
```

Open http://127.0.0.1:5000. An internet connection is needed to search iTunes. NLTK may download its VADER lexicon the first time it runs. The main search-and-save workflow does not need Spotify credentials.

For optional Spotify integration, copy `.env.example` to `.env` and set your own client ID, client secret, and redirect URI. Set `FLASK_SECRET_KEY` to a long random value if using sessions across restarts. Never commit your `.env` file.

## How it works

1. A search request reaches Flask at `POST /api/recognize`.
2. `ITunesClient` retrieves a matching track, including its title, artist, and genre.
3. `MoodAnalyzer` scores the title with VADER and estimates energy and valence from its genre.
4. `PlaylistManager` sorts tracks into one of four mood groups.
5. The user can save a playlist to SQLite and later view its history and tracks.

The database has related `users`, `playlists`, and `tracks` tables, using foreign keys and indexes. The default local user is intended for single-user development, not multi-user deployment.

## API

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/` | Web interface |
| POST | `/api/recognize` | Search for and classify one song |
| POST | `/api/playlist/generate` | Group a list of song queries by mood |
| POST | `/api/playlist/save` | Store a selected playlist |
| GET | `/api/history` | List saved playlists |
| GET | `/api/history/<id>/tracks` | Get tracks for a saved playlist |
| GET | `/api/history/stats` | Get playlist counts by mood |
| GET | `/api/health` | Basic health check |

Example request:

```bash
curl -X POST http://127.0.0.1:5000/api/recognize \
  -H "Content-Type: application/json" \
  -d '{"query": "Headlines Drake"}'
```

## Current limitations

- iTunes returns the top matching result; ambiguous song searches can select the wrong recording.
- Title sentiment and genre proxies are approximate and do not analyze the audio itself.
- The local user and database setup are for personal use. Authentication and access controls need more work before hosting for multiple users.
- The app has no automated test suite yet, and the optional Spotify export workflow depends on Spotify permissions and API availability.

## Next steps

See [ROADMAP.md](ROADMAP.md) for planned engineering work, including tests, playlist editing, stronger API error handling, data export, and frontend improvements.

## License

MIT. See [LICENSE](LICENSE).
