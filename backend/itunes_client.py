import requests

SEARCH_URL = "https://itunes.apple.com/search"


class ITunesClient:
    """
    Lightweight client for the public iTunes Search API.
    No authentication, no API key, no quota — completely free.
    """

    def search_track(self, query: str) -> dict | None:
        params = {"term": query, "entity": "song", "limit": 1}
        try:
            resp = requests.get(SEARCH_URL, params=params, timeout=10)
            resp.raise_for_status()
            results = resp.json().get("results", [])
            if not results:
                return None
            r = results[0]

            # Upgrade album art from 100x100 to 600x600
            artwork = r.get("artworkUrl100", "")
            if artwork:
                artwork = artwork.replace("100x100bb", "600x600bb")

            return {
                "id":           str(r.get("trackId", "")),
                "uri":          "",                              # filled in later if Spotify search succeeds
                "name":         r.get("trackName", ""),
                "artist":       r.get("artistName", ""),
                "album":        r.get("collectionName", ""),
                "genre":        r.get("primaryGenreName", ""),
                "popularity":   0,
                "preview_url":  r.get("previewUrl", ""),
                "album_image":  artwork,
                "external_url": r.get("trackViewUrl", ""),
                "release_date": r.get("releaseDate", ""),
            }
        except requests.RequestException as e:
            raise RuntimeError(f"iTunes Search error: {e}") from e
