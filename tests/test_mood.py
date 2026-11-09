import pytest

from models.mood_analyzer import MoodAnalyzer, MoodResult, estimate_features_from_genre


def test_genre_proxies_are_deterministic():
    assert estimate_features_from_genre("Hip-Hop/Rap") == {
        "energy": 0.7, "valence": 0.5
    }
    assert estimate_features_from_genre(None) == {
        "energy": 0.5, "valence": 0.5
    }


def test_analyzer_returns_mood_and_bounded_confidence():
    result = MoodAnalyzer().analyze(text="Wonderful Day", genre="Dance")
    assert result.mood in {"happy", "sad", "energetic", "chill"}
    assert 0 <= result.confidence <= 1
    assert 0 <= result.energy <= 1
    assert 0 <= result.valence <= 1
    assert result.label


def test_supplied_audio_features_override_genre_estimate():
    result = MoodAnalyzer().analyze(
        text="Calm", genre="Dance", audio_features={"energy": 0.1, "valence": 0.2}
    )
    assert result.energy == pytest.approx(0.1)
    assert result.valence == pytest.approx(0.2)


def test_mood_result_serializes_rounded_values():
    result = MoodResult(
        mood="happy", confidence=0.123456,
        compound_score=0.56789, energy=0.78, valence=0.91, label="Happy"
    )
    assert result.to_dict()["confidence"] == pytest.approx(0.123)
    assert result.to_dict()["compound_score"] == pytest.approx(0.568)
