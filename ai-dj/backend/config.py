"""Central config: thresholds, playlist map, env loading."""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Webcam ────────────────────────────────────────────────────────────────────
WEBCAM_INDEX = int(os.getenv("WEBCAM_INDEX", 0))
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
CAPTURE_FPS = 10
BROADCAST_HZ = 5

# ── YOLO ──────────────────────────────────────────────────────────────────────
YOLO_MODEL = "yolov8n.pt"
YOLO_IMGSZ = 480
YOLO_CONF = 0.4

# ── Emotion ───────────────────────────────────────────────────────────────────
MAX_FACES = 5
EMOTION_EVERY_N = 3          # run DeepFace every Nth frame per slot

# ── DJ Brain ──────────────────────────────────────────────────────────────────
PEOPLE_NORM = 8.0            # crowd size that = "full"
HYSTERESIS_SEC = 2.0         # seconds in new band before mood switch

MOOD_BANDS = {
    "dead":    (0,   20),
    "chill":   (20,  45),
    "neutral": (45,  65),
    "hype":    (65,  85),
    "peak":    (85,  101),
}

# ── Action Map  state → (playlist_uri, hex_color, brightness 0-254, effect) ──
ACTION_MAP = {
    "dead":    ("spotify:playlist:REPLACE_WITH_LOFI_URI",       "#1a1a40", 60,  "static"),
    "chill":   ("spotify:playlist:REPLACE_WITH_CHILLHOP_URI",   "#2d4a7a", 100, "slow_breathe"),
    "neutral": ("spotify:playlist:REPLACE_WITH_INDIEPOP_URI",   "#4a7a4a", 150, "static"),
    "hype":    ("spotify:playlist:REPLACE_WITH_EDM_URI",        "#ff6600", 220, "pulse"),
    "peak":    ("spotify:playlist:REPLACE_WITH_FESTIVAL_URI",   "#ff0066", 254, "strobe"),
}

# ── DJ Commentary (no LLM — simple templates) ─────────────────────────────────
COMMENTARY = {
    "dead": [
        "Crowd's dead. Bringing it down with some lo-fi.",
        "Almost empty in here. Keeping it mellow.",
        "Nobody's feeling it yet. Chill vibes only.",
    ],
    "chill": [
        "Easy energy tonight. Riding the chill wave.",
        "Low-key crowd. Keeping it smooth.",
        "Vibes are relaxed. Chillhop incoming.",
    ],
    "neutral": [
        "Steady pulse out there. Holding the groove.",
        "Crowd's warming up. Indie pop keeps the flow.",
        "Middle of the road — let's build from here.",
    ],
    "hype": [
        "Y'all are popping off — turning it up!",
        "Energy's rising! EDM time, let's go!",
        "Crowd's getting lit — cranking the BPM!",
    ],
    "peak": [
        "PEAK HOUR. Festival mode ACTIVATED.",
        "The crowd is absolutely losing it. BIG ROOM!",
        "This is what we live for — maximum power!",
    ],
}

# ── Spotify ───────────────────────────────────────────────────────────────────
SPOTIPY_CLIENT_ID     = os.getenv("SPOTIPY_CLIENT_ID", "")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET", "")
SPOTIPY_REDIRECT_URI  = os.getenv("SPOTIPY_REDIRECT_URI", "http://localhost:8888/callback")
SPOTIFY_SCOPES        = "user-modify-playback-state user-read-playback-state"

# ── Hue ───────────────────────────────────────────────────────────────────────
HUE_BRIDGE_IP = os.getenv("HUE_BRIDGE_IP", "")
HUE_USERNAME  = os.getenv("HUE_USERNAME", "")
