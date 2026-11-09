import sqlite3

import pytest

from backend import database as db


@pytest.fixture
def database(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "playlist-test.db"))
    db.init_db()
    return db


def test_creates_and_reuses_local_user(database):
    first_id = database.get_or_create_local_user()
    second_id = database.get_or_create_local_user()
    assert first_id == second_id
    user = database.get_user_by_spotify_id("local_default")
    assert user["id"] == first_id


def test_playlist_tracks_and_statistics(database):
    user_id = database.get_or_create_local_user()
    playlist_id = database.save_playlist(user_id, "Road Trip", "happy", 2)
    tracks = [
        {"track": {"name": "Song A", "artist": "Artist A", "genre": "Pop"},
         "mood": {"compound_score": 0.65},
         "audio_features": {"energy": 0.7, "valence": 0.8}},
        {"track": {"name": "Song B", "artist": "Artist B", "genre": "Rock"},
         "mood": {"compound_score": 0.3},
         "audio_features": {"energy": 0.6, "valence": 0.7}},
    ]
    database.save_tracks(playlist_id, tracks)
    playlists = database.get_user_playlists(user_id)
    assert len(playlists) == 1
    assert playlists[0]["playlist_name"] == "Road Trip"
    saved_tracks = database.get_playlist_tracks(playlist_id)
    assert [t["track_name"] for t in saved_tracks] == ["Song A", "Song B"]
    assert saved_tracks[0]["mood_score"] == pytest.approx(0.65)
    assert saved_tracks[1]["energy"] == pytest.approx(0.6)
    assert database.get_mood_stats(user_id) == [
        {"mood_category": "happy", "playlist_count": 1, "total_tracks": 2}
    ]


def test_foreign_keys_cascade_when_playlist_deleted(database):
    user_id = database.get_or_create_local_user()
    playlist_id = database.save_playlist(user_id, "Temporary", "chill", 1)
    database.save_tracks(playlist_id, [{"track": {"name": "Track"}}])

    with database.get_connection() as conn:
        conn.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))

    assert database.get_playlist_tracks(playlist_id) == []


def test_invalid_mood_is_rejected_by_database(database):
    user_id = database.get_or_create_local_user()
    with pytest.raises(sqlite3.IntegrityError):
        database.save_playlist(user_id, "Wrong", "invalid", 0)
