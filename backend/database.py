import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "phoenixplaylist.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                spotify_id  TEXT    NOT NULL UNIQUE,
                email       TEXT,
                display_name TEXT,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS playlists (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                playlist_name   TEXT    NOT NULL,
                mood_category   TEXT    NOT NULL CHECK(mood_category IN ('happy','sad','energetic','chill')),
                spotify_uri     TEXT,
                spotify_url     TEXT,
                track_count     INTEGER DEFAULT 0,
                created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS tracks (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id     INTEGER NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
                track_name      TEXT    NOT NULL,
                artist          TEXT,
                spotify_uri     TEXT,
                mood_score      REAL,
                energy          REAL,
                valence         REAL,
                genre           TEXT,
                album_image_url TEXT,
                created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_playlists_user    ON playlists(user_id);
            CREATE INDEX IF NOT EXISTS idx_playlists_mood    ON playlists(mood_category);
            CREATE INDEX IF NOT EXISTS idx_tracks_playlist   ON tracks(playlist_id);
        """)


# ── Users ──────────────────────────────────────────────────────────────────────

def upsert_user(spotify_id: str, email: str = "", display_name: str = "") -> int:
    """Insert or update a user, return their internal DB id. Race-safe."""
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO users (spotify_id, email, display_name)
               VALUES (?, ?, ?)
               ON CONFLICT(spotify_id) DO UPDATE SET
                 email        = excluded.email,
                 display_name = excluded.display_name""",
            (spotify_id, email, display_name),
        )
        row = conn.execute(
            "SELECT id FROM users WHERE spotify_id = ?", (spotify_id,)
        ).fetchone()
        return row["id"]


def get_user_by_spotify_id(spotify_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE spotify_id = ?", (spotify_id,)
        ).fetchone()
        return dict(row) if row else None


def get_or_create_local_user() -> int:
    """Return the id of the default local user, creating it if necessary."""
    return upsert_user(
        spotify_id="local_default",
        email="",
        display_name="Local User",
    )


# ── Playlists ──────────────────────────────────────────────────────────────────

def save_playlist(
    user_id: int,
    playlist_name: str,
    mood_category: str,
    track_count: int,
    spotify_uri: str = "",
    spotify_url: str = "",
) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO playlists
               (user_id, playlist_name, mood_category, spotify_uri, spotify_url, track_count)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, playlist_name, mood_category, spotify_uri, spotify_url, track_count),
        )
        return cur.lastrowid


def get_user_playlists(user_id: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT * FROM playlists WHERE user_id = ?
               ORDER BY created_at DESC LIMIT 50""",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]


# ── Tracks ─────────────────────────────────────────────────────────────────────

def save_tracks(playlist_id: int, tracks: list[dict]):
    """Bulk-insert track records linked to a playlist."""
    rows = []
    for t in tracks:
        track = t.get("track") or {}
        mood  = t.get("mood") or {}
        af    = t.get("audio_features") or {}
        rows.append((
            playlist_id,
            track.get("name", "Unknown"),
            track.get("artist", ""),
            track.get("uri", ""),
            mood.get("compound_score", 0.0),
            af.get("energy", 0.0),
            af.get("valence", 0.0),
            track.get("genre", ""),
            track.get("album_image", ""),
        ))
    with get_connection() as conn:
        conn.executemany(
            """INSERT INTO tracks
               (playlist_id, track_name, artist, spotify_uri,
                mood_score, energy, valence, genre, album_image_url)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )


def get_playlist_tracks(playlist_id: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM tracks WHERE playlist_id = ? ORDER BY id",
            (playlist_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_mood_stats(user_id: int) -> list[dict]:
    """Aggregate playlist counts per mood for a user."""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT mood_category, COUNT(*) as playlist_count,
                      SUM(track_count) as total_tracks
               FROM playlists WHERE user_id = ?
               GROUP BY mood_category""",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
