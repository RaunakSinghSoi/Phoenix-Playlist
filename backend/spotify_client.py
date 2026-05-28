import base64
import requests
from flask import session
from backend.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

AUTH_URL  = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE  = "https://api.spotify.com/v1"

SCOPES = "playlist-modify-public playlist-modify-private user-read-private user-read-email"


class SpotifyClient:

    # ── Client Credentials (no user login needed) ──────────────────────────────

    def _app_token(self) -> str:
        """Fetch a short-lived app-level token for search and audio features."""
        credentials = base64.b64encode(
            f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
        ).decode()
        resp = requests.post(
            TOKEN_URL,
            headers={"Authorization": f"Basic {credentials}"},
            data={"grant_type": "client_credentials"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    def _app_headers(self) -> dict:
        return {"Authorization": f"Bearer {self._app_token()}"}

    # ── OAuth (user login, needed for playlist creation) ───────────────────────

    def get_auth_url(self) -> str:
        scope = SCOPES.replace(" ", "%20")
        return (
            f"{AUTH_URL}?client_id={SPOTIFY_CLIENT_ID}"
            f"&response_type=code"
            f"&redirect_uri={SPOTIFY_REDIRECT_URI}"
            f"&scope={scope}"
        )

    def exchange_code(self, code: str) -> dict:
        credentials = base64.b64encode(
            f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
        ).decode()
        resp = requests.post(
            TOKEN_URL,
            headers={"Authorization": f"Basic {credentials}"},
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": SPOTIFY_REDIRECT_URI,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def _user_headers(self) -> dict:
        token = session.get("spotify_token")
        if not token:
            raise PermissionError("Not authenticated with Spotify.")
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # ── Search (uses app token — works without user login) ─────────────────────

    def search_track(self, query: str) -> dict | None:
        """
        Search Spotify by free-text query (title, artist, or both).
        Returns a track dict or None.
        """
        params = {"q": query, "type": "track", "limit": 1}
        resp = requests.get(
            f"{API_BASE}/search",
            headers=self._app_headers(),
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        items = resp.json().get("tracks", {}).get("items", [])
        if not items:
            return None
        t = items[0]
        return {
            "id":          t["id"],
            "uri":         t["uri"],
            "name":        t["name"],
            "artist":      t["artists"][0]["name"],
            "album":       t["album"]["name"],
            "popularity":  t.get("popularity", 0),
            "preview_url": t.get("preview_url"),
            "album_image": t["album"]["images"][0]["url"] if t["album"]["images"] else "",
            "external_url": t["external_urls"].get("spotify", ""),
        }

    def get_audio_features(self, track_id: str) -> dict | None:
        resp = requests.get(
            f"{API_BASE}/audio-features/{track_id}",
            headers=self._app_headers(),
            timeout=10,
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    # ── User info (requires user login) ───────────────────────────────────────

    def get_current_user(self) -> dict:
        resp = requests.get(f"{API_BASE}/me", headers=self._user_headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()

    # ── Playlist management (requires user login) ─────────────────────────────

    def create_playlist(self, user_id: str, name: str, description: str = "") -> dict:
        resp = requests.post(
            f"{API_BASE}/users/{user_id}/playlists",
            headers=self._user_headers(),
            json={"name": name, "description": description, "public": True},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def add_tracks_to_playlist(self, playlist_id: str, uris: list[str]) -> dict:
        resp = requests.post(
            f"{API_BASE}/playlists/{playlist_id}/tracks",
            headers=self._user_headers(),
            json={"uris": uris[:100]},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
