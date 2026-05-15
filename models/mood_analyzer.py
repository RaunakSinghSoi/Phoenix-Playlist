import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from dataclasses import dataclass

# Download VADER lexicon on first use
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon", quiet=True)


@dataclass
class MoodResult:
    mood: str
    confidence: float
    compound_score: float
    energy: float
    valence: float
    label: str

    def to_dict(self) -> dict:
        return {
            "mood": self.mood,
            "confidence": round(self.confidence, 3),
            "compound_score": round(self.compound_score, 3),
            "energy": round(self.energy, 3),
            "valence": round(self.valence, 3),
            "label": self.label,
        }


class MoodAnalyzer:
    """
    Combines VADER sentiment scores from lyrics with Spotify audio features
    (energy, valence, tempo) to classify tracks into one of four moods:
    happy, sad, energetic, chill.
    """

    MOOD_LABELS = {
        "happy": "Happy & Upbeat",
        "sad": "Sad & Melancholic",
        "energetic": "Energetic & Pumped",
        "chill": "Chill & Relaxed",
    }

    def __init__(self):
        self._sia = SentimentIntensityAnalyzer()

    def analyze(self, lyrics: str, audio_features: dict | None = None) -> MoodResult:
        sentiment = self._sia.polarity_scores(lyrics) if lyrics.strip() else {
            "compound": 0.0, "pos": 0.0, "neg": 0.0, "neu": 1.0
        }
        compound = sentiment["compound"]

        energy = audio_features.get("energy", 0.5) if audio_features else 0.5
        valence = audio_features.get("valence", 0.5) if audio_features else 0.5

        mood, confidence = self._classify(compound, energy, valence)
        return MoodResult(
            mood=mood,
            confidence=confidence,
            compound_score=compound,
            energy=energy,
            valence=valence,
            label=self.MOOD_LABELS[mood],
        )

    def _classify(self, compound: float, energy: float, valence: float) -> tuple[str, float]:
        scores = {
            "happy": self._happy_score(compound, energy, valence),
            "sad": self._sad_score(compound, energy, valence),
            "energetic": self._energetic_score(compound, energy, valence),
            "chill": self._chill_score(compound, energy, valence),
        }
        mood = max(scores, key=scores.get)
        total = sum(scores.values()) or 1
        confidence = scores[mood] / total
        return mood, confidence

    def _happy_score(self, compound, energy, valence):
        score = 0.0
        if compound > 0.2:
            score += compound
        if valence > 0.6:
            score += valence
        if 0.4 < energy < 0.85:
            score += 0.3
        return max(score, 0.0)

    def _sad_score(self, compound, energy, valence):
        score = 0.0
        if compound < -0.1:
            score += abs(compound)
        if valence < 0.4:
            score += (0.4 - valence)
        if energy < 0.5:
            score += 0.2
        return max(score, 0.0)

    def _energetic_score(self, compound, energy, valence):
        score = 0.0
        if energy > 0.7:
            score += energy
        if compound > 0.0:
            score += compound * 0.5
        if valence > 0.5:
            score += 0.2
        return max(score, 0.0)

    def _chill_score(self, compound, energy, valence):
        score = 0.0
        if energy < 0.45:
            score += (0.45 - energy) + 0.5
        if -0.2 <= compound <= 0.3:
            score += 0.3
        if 0.3 <= valence <= 0.65:
            score += 0.2
        return max(score, 0.0)

    def batch_analyze(self, tracks: list[dict]) -> list[dict]:
        """Analyze a list of track dicts, each with 'lyrics' and 'audio_features' keys."""
        results = []
        for track in tracks:
            result = self.analyze(
                track.get("lyrics", ""),
                track.get("audio_features"),
            )
            results.append({**track, "mood_result": result.to_dict()})
        return results
