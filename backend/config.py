import os
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = "shazam.p.rapidapi.com"

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:5000/callback")

FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "phoenix-playlist-secret-key-change-in-prod")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

MOOD_THRESHOLDS = {
    "happy": {"compound": 0.3, "energy_min": 0.5},
    "sad": {"compound": -0.3, "energy_max": 0.5},
    "energetic": {"compound": 0.1, "energy_min": 0.7},
    "chill": {"compound": -0.1, "energy_max": 0.45},
}
