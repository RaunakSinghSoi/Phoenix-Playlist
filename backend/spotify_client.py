import base64
import requests
from flask import session
from backend.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE = "https://api.spotify.com/v1"

SCOPES = "playlist-modify-public playlist-modify-private user-read-private"


class SpotifyClient:

    # ── OAuth helpers ──────────────────────────────────────────────────────────

    def get_auth_url(self) -> str:
        params = (
            f"?client_id={SPOTIFY_CLIENT_ID}"
            f"&response_type=code"
            f"&redirect_uri={SPOTIFY_REDIRECT_URI}"
            f"&scope={SCOPES.replace(' ', '%20')}"
        )
        return AUTH_URL + params

    def exchange_code(self, code: str) -> dict:
        credentials = base64.b64encode(
            f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
        ).decode()
        headers = {"Authorization": f"Basic {credentials}"}
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": SPOTIFY_REDIRECT_URI,
        }
        response = requests.post(TOKEN_URL, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        return response.json()

    def refresh_token(self, refresh_token: str) -> dict:
        credentials = base64.b64encode(
            f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
        ).decode()
        headers = {"Authorization": f"Basic {credentials}"}
        payload = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        response = requests.post(TOKEN_URL, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        return response.json()

    # ── API helpers ────────────────────────────────────────────────────────────

    def _headers(self) -> dict:
        token = session.get("spotify_token")
        if not token:
            raise PermissionError("Not authenticated with Spotify.")
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def get_current_user(self) -> dict:
        response = requests.get(f"{API_BASE}/me", headers=self._headers(), timeout=10)
        response.raise_for_status()
        return response.json()

    def search_track(self, title: str, artist: str) -> str | None:
        """Return the Spotify URI for the best-matching track, or None."""
        query = f"track:{title} artist:{artist}"
        params = {"q": query, "type": "track", "limit": 1}
        response = requests.get(
            f"{API_BASE}/search", headers=self._headers(), params=params, timeout=10
        )
        response.raise_for_status()
        items = response.json().get("tracks", {}).get("items", [])
        if not items:
            return None
        track = items[0]
        return {
            "uri": track["uri"],
            "id": track["id"],
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "popularity": track.get("popularity", 0),
            "preview_url": track.get("preview_url"),
            "album_image": (
                track["album"]["images"][0]["url"] if track["album"]["images"] else ""
            ),
        }

    def get_audio_features(self, track_id: str) -> dict | None:
        response = requests.get(
            f"{API_BASE}/audio-features/{track_id}",
            headers=self._headers(),
            timeout=10,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    def create_playlist(self, user_id: str, name: str, description: str = "") -> dict:
        payload = {"name": name, "description": description, "public": True}
        response = requests.post(
            f"{API_BASE}/users/{user_id}/playlists",
            headers=self._headers(),
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def add_tracks_to_playlist(self, playlist_id: str, uris: list[str]) -> dict:
        """Add up to 100 tracks to a playlist."""
        payload = {"uris": uris[:100]}
        response = requests.post(
            f"{API_BASE}/playlists/{playlist_id}/tracks",
            headers=self._headers(),
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
