import pytest

from backend import database as db
from backend.app import app, playlist_manager


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test-api.db"))
    db.init_db()
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def test_health_and_web_page_load(client):
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.get_json()["status"] == "ok"

    page = client.get("/")
    assert page.status_code == 200
    assert b"PhoenixPlaylist" in page.data


def test_recognize_rejects_empty_query(client):
    response = client.post("/api/recognize", json={})
    assert response.status_code == 400
    assert response.get_json()["error"]


def test_recognize_returns_track_metadata(client, monkeypatch):
    def fake_recognize(query):
        assert query == "Song Artist"
        return {"track": {"name": "Song", "artist": "Artist"}, "mood": {"mood": "happy"}}

    monkeypatch.setattr(playlist_manager, "recognize_and_classify", fake_recognize)
    response = client.post("/api/recognize", json={"query": "Song Artist"})
    assert response.status_code == 200
    assert response.get_json()["track"]["name"] == "Song"


def test_generate_rejects_empty_song_list(client):
    response = client.post("/api/playlist/generate", json={"songs": []})
    assert response.status_code == 400


def test_generate_mood_playlists(client, monkeypatch):
    def fake_build(songs, mood_filter):
        assert songs == ["First Song", "Second Song"]
        assert mood_filter is None
        return {"happy": [{"track": {"name": "First Song"}}], "chill": []}

    monkeypatch.setattr(playlist_manager, "build_mood_playlist", fake_build)
    response = client.post("/api/playlist/generate", json={
        "songs": ["First Song", "Second Song"]
    })
    assert response.status_code == 200
    body = response.get_json()
    assert body["summary"] == {"happy": 1, "chill": 0}


def test_save_and_retrieve_playlist_history(client):
    payload = {
        "mood": "happy",
        "tracks": [{
            "track": {"name": "First Song", "artist": "First Artist", "genre": "Pop"},
            "mood": {"compound_score": 0.3},
            "audio_features": {"energy": 0.6, "valence": 0.8}
        }]
    }
    saved = client.post("/api/playlist/save", json=payload)
    assert saved.status_code == 200
    playlist_id = saved.get_json()["playlist_id"]
    assert saved.get_json()["tracks_added"] == 1

    history = client.get("/api/history")
    assert history.status_code == 200
    assert history.get_json()["playlists"][0]["id"] == playlist_id

    tracks = client.get(f"/api/history/{playlist_id}/tracks")
    assert tracks.status_code == 200
    assert tracks.get_json()["tracks"][0]["track_name"] == "First Song"

    stats = client.get("/api/history/stats")
    assert stats.status_code == 200
    assert stats.get_json()["stats"][0]["total_tracks"] == 1


def test_save_without_tracks_is_bad_request(client):
    response = client.post("/api/playlist/save", json={"tracks": []})
    assert response.status_code == 400
