import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from dataclasses import dataclass

# Download VADER lexicon on first use
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon", quiet=True)


# Genre-to-(energy, valence) profile mapping used when Spotify audio
# features are unavailable. Values are rough proxies on the same 0..1 scale
# Spotify uses, calibrated against typical examples per genre.
GENRE_PROFILES: dict[str, tuple[float, float]] = {
    "dance":             (0.85, 0.75),
    "electronic":        (0.80, 0.60),
    "edm":               (0.90, 0.75),
    "house":             (0.85, 0.70),
    "techno":            (0.85, 0.50),
    "trance":            (0.85, 0.60),
    "disco":             (0.75, 0.80),
    "pop":               (0.70, 0.70),
    "k-pop":             (0.75, 0.75),
    "latin":             (0.75, 0.75),
    "reggaeton":         (0.75, 0.70),
    "reggae":            (0.55, 0.75),
    "soul":              (0.55, 0.65),
    "funk":              (0.70, 0.75),
    "r&b":               (0.55, 0.55),
    "hip-hop":           (0.70, 0.50),
    "rap":               (0.70, 0.45),
    "trap":              (0.75, 0.45),
    "rock":              (0.70, 0.50),
    "alternative":       (0.60, 0.45),
    "indie":             (0.50, 0.50),
    "punk":              (0.85, 0.50),
    "metal":             (0.90, 0.40),
    "country":           (0.50, 0.55),
    "folk":              (0.35, 0.50),
    "singer/songwriter": (0.40, 0.45),
    "blues":             (0.40, 0.35),
    "jazz":              (0.40, 0.55),
    "classical":         (0.35, 0.60),
    "ambient":           (0.25, 0.50),
    "new age":           (0.25, 0.55),
    "world":             (0.55, 0.60),
    "instrumental":      (0.40, 0.55),
    "soundtrack":        (0.50, 0.50),
}


def estimate_features_from_genre(genre: str | None) -> dict:
    """Map a genre string to approximate energy/valence values."""
    if not genre:
        return {"energy": 0.5, "valence": 0.5}
    g = genre.lower()
    for keyword, (energy, valence) in GENRE_PROFILES.items():
        if keyword in g:
            return {"energy": energy, "valence": valence}
    return {"energy": 0.5, "valence": 0.5}


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
            "mood":           self.mood,
            "confidence":     round(self.confidence, 3),
            "compound_score": round(self.compound_score, 3),
            "energy":         round(self.energy, 3),
            "valence":        round(self.valence, 3),
            "label":          self.label,
        }


class MoodAnalyzer:
    """
    Combines VADER sentiment scores from text (lyrics or song title)
    with energy/valence features (real or genre-estimated) to classify
    tracks into one of four moods: happy, sad, energetic, chill.
    """

    MOOD_LABELS = {
        "happy":     "Happy & Upbeat",
        "sad":       "Sad & Melancholic",
        "energetic": "Energetic & Pumped",
        "chill":     "Chill & Relaxed",
    }

    def __init__(self):
        self._sia = SentimentIntensityAnalyzer()

    def analyze(
        self,
        text: str = "",
        audio_features: dict | None = None,
        genre: str | None = None,
    ) -> MoodResult:
        # VADER sentiment on whatever text is available (lyrics or title)
        if text.strip():
            sentiment = self._sia.polarity_scores(text)
        else:
            sentiment = {"compound": 0.0, "pos": 0.0, "neg": 0.0, "neu": 1.0}
        compound = sentiment["compound"]

        # Pull energy/valence from Spotify if present, otherwise estimate from genre
        if audio_features:
            energy  = audio_features.get("energy", 0.5)
            valence = audio_features.get("valence", 0.5)
        else:
            est = estimate_features_from_genre(genre)
            energy, valence = est["energy"], est["valence"]

        mood, confidence = self._classify(compound, energy, valence)
        return MoodResult(
            mood=mood,
            confidence=confidence,
            compound_score=compound,
            energy=energy,
            valence=valence,
            label=self.MOOD_LABELS[mood],
        )

    def _classify(self, compound, energy, valence):
        scores = {
            "happy":     self._happy_score(compound, energy, valence),
            "sad":       self._sad_score(compound, energy, valence),
            "energetic": self._energetic_score(compound, energy, valence),
            "chill":     self._chill_score(compound, energy, valence),
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
