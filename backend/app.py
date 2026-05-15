import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, session, redirect, render_template
from backend.config import FLASK_SECRET_KEY, DEBUG
from backend.spotify_client import SpotifyClient
from backend.playlist_manager import PlaylistManager

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "..", "frontend", "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "..", "frontend", "static"),
)
app.secret_key = FLASK_SECRET_KEY

spotify_client = SpotifyClient()
playlist_manager = PlaylistManager()


# ── Frontend ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", authenticated=bool(session.get("spotify_token")))


# ── Spotify OAuth ──────────────────────────────────────────────────────────────

@app.route("/auth/spotify")
def spotify_auth():
    return redirect(spotify_client.get_auth_url())


@app.route("/callback")
def spotify_callback():
    code = request.args.get("code")
    error = request.args.get("error")
    if error or not code:
        return jsonify({"error": error or "No code received"}), 400
    tokens = spotify_client.exchange_code(code)
    session["spotify_token"] = tokens["access_token"]
    session["spotify_refresh_token"] = tokens.get("refresh_token")
    return redirect("/")


@app.route("/auth/logout")
def logout():
    session.clear()
    return redirect("/")


# ── API: Song Recognition ──────────────────────────────────────────────────────

@app.route("/api/recognize", methods=["POST"])
def recognize():
    """Recognize a song by text query and return mood + metadata."""
    body = request.get_json(silent=True) or {}
    query = body.get("query", "").strip()
    if not query:
        return jsonify({"error": "query field is required"}), 400
    try:
        result = playlist_manager.recognize_and_classify(query)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── API: Mood Playlist Generation ─────────────────────────────────────────────

@app.route("/api/playlist/generate", methods=["POST"])
def generate_playlist():
    """
    Classify a batch of songs and group them by mood.
    Body: { "songs": ["song query 1", ...], "mood": "happy" (optional) }
    """
    body = request.get_json(silent=True) or {}
    songs = body.get("songs", [])
    mood_filter = body.get("mood")

    if not isinstance(songs, list) or not songs:
        return jsonify({"error": "songs must be a non-empty list of query strings"}), 400

    try:
        classified = playlist_manager.build_mood_playlist(songs, mood_filter)
        summary = {mood: len(tracks) for mood, tracks in classified.items()}
        return jsonify({"playlists": classified, "summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/playlist/push", methods=["POST"])
def push_playlist():
    """
    Push a mood playlist to Spotify.
    Body: { "tracks": [...], "mood": "happy" }
    Requires active Spotify session.
    """
    if not session.get("spotify_token"):
        return jsonify({"error": "Not authenticated with Spotify. Visit /auth/spotify first."}), 401

    body = request.get_json(silent=True) or {}
    tracks = body.get("tracks", [])
    mood = body.get("mood", "happy")

    if not tracks:
        return jsonify({"error": "tracks list is required"}), 400

    try:
        result = playlist_manager.push_mood_playlist_to_spotify(tracks, mood)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── API: Health ────────────────────────────────────────────────────────────────

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "authenticated": bool(session.get("spotify_token"))})


if __name__ == "__main__":
    app.run(debug=DEBUG, port=5000)
