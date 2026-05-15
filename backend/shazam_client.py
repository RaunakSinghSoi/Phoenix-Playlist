import requests
from backend.config import RAPIDAPI_KEY, RAPIDAPI_HOST


class ShazamClient:
    BASE_URL = "https://shazam.p.rapidapi.com"
    HEADERS = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }

    def search_song(self, query: str) -> dict | None:
        """Search for a song by text query and return top result metadata."""
        url = f"{self.BASE_URL}/search"
        params = {"term": query, "locale": "en-US", "offset": "0", "limit": "1"}
        try:
            response = requests.get(url, headers=self.HEADERS, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            hits = data.get("tracks", {}).get("hits", [])
            if not hits:
                return None
            track = hits[0]["track"]
            return {
                "title": track.get("title", ""),
                "artist": track.get("subtitle", ""),
                "genre": track.get("genres", {}).get("primary", "Unknown"),
                "shazam_id": track.get("key", ""),
                "image_url": track.get("images", {}).get("coverart", ""),
                "lyrics_snippet": self._extract_lyrics_snippet(track),
            }
        except requests.RequestException as e:
            raise RuntimeError(f"Shazam API error: {e}") from e

    def get_track_details(self, shazam_id: str) -> dict | None:
        """Fetch full track details from Shazam by track key."""
        url = f"{self.BASE_URL}/songs/get-details"
        params = {"key": shazam_id, "locale": "en-US"}
        try:
            response = requests.get(url, headers=self.HEADERS, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            sections = data.get("sections", [])
            lyrics_lines = []
            for section in sections:
                if section.get("type") == "LYRICS":
                    lyrics_lines = section.get("text", [])
                    break
            return {
                "title": data.get("title", ""),
                "artist": data.get("subtitle", ""),
                "genre": data.get("genres", {}).get("primary", "Unknown"),
                "shazam_id": data.get("key", ""),
                "image_url": data.get("images", {}).get("coverart", ""),
                "lyrics": " ".join(lyrics_lines),
            }
        except requests.RequestException as e:
            raise RuntimeError(f"Shazam API error: {e}") from e

    def _extract_lyrics_snippet(self, track: dict) -> str:
        sections = track.get("sections", [])
        for section in sections:
            if section.get("type") == "LYRICS":
                return " ".join(section.get("text", [])[:4])
        return ""
