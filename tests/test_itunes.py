import requests
import pytest

from backend.itunes_client import ITunesClient
from backend.playlist_manager import PlaylistManager


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_itunes_track_mapping(monkeypatch):
    def fake_get(url, params, timeout):
        assert "itunes.apple.com" in url
        assert params["term"] == "Song Artist"
        assert params["entity"] == "song"
        assert timeout == 10
        return FakeResponse({"results": [{
            "trackId": 42,
            "trackName": "Song",
            "artistName": "Artist",
            "collectionName": "Album",
            "primaryGenreName": "Pop",
            "artworkUrl100": "https://example.com/100x100bb.jpg",
            "previewUrl": "https://example.com/preview.m4a",
        }]})

    monkeypatch.setattr(requests, "get", fake_get)
    result = ITunesClient().search_track("Song Artist")
    assert result["id"] == "42"
    assert result["name"] == "Song"
    assert result["artist"] == "Artist"
    assert "600x600bb" in result["album_image"]


def test_no_itunes_results_returns_none(monkeypatch):
    monkeypatch.setattr(
        requests, "get",
        lambda *args, **kwargs: FakeResponse({"results": []})
    )
    assert ITunesClient().search_track("Missing track") is None


def test_itunes_network_error_is_explained(monkeypatch):
    def fail(*args, **kwargs):
        raise requests.Timeout("connection timed out")

    monkeypatch.setattr(requests, "get", fail)
    with pytest.raises(RuntimeError, match="iTunes Search error"):
        ITunesClient().search_track("Song")


def test_playlist_manager_uses_itunes_and_mood_analyzer(monkeypatch):
    manager = PlaylistManager()
    monkeypatch.setattr(manager.itunes, "search_track", lambda query: {
        "name": "Wonderful Day", "artist": "Singer", "genre": "Pop"
    })
    result = manager.recognize_and_classify("Wonderful Day Singer")
    assert result["track"]["artist"] == "Singer"
    assert result["mood"]["mood"] in {"happy", "sad", "energetic", "chill"}
    assert 0 <= result["audio_features"]["energy"] <= 1
