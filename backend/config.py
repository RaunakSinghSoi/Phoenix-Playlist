import os
import secrets

from dotenv import load_dotenv

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:5000/callback")

# A temporary local key is generated when one is not configured.
# Set FLASK_SECRET_KEY explicitly to preserve sessions across restarts.
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32)
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

MOOD_THRESHOLDS = {
    "happy": {"compound": 0.3, "energy_min": 0.5},
    "sad": {"compound": -0.3, "energy_max": 0.5},
    "energetic": {"compound": 0.1, "energy_min": 0.7},
    "chill": {"compound": -0.1, "energy_max": 0.45},
}
