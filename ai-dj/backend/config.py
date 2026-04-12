"""Central config: thresholds, playlist map, env loading."""

import os
from dotenv import load_dotenv

load_dotenv()

# Audio
AUDIO_GAIN = float(os.getenv("AUDIO_GAIN", "8.0"))


# ── Webcam ────────────────────────────────────────────────────────────────────
WEBCAM_INDEX = int(os.getenv("WEBCAM_INDEX", 0))
WEBCAM_FLIP = int(os.getenv("WEBCAM_FLIP", 1))  # 1 = mirror horizontally
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
CAPTURE_FPS = 25
BROADCAST_HZ = 4

# ── YOLO ──────────────────────────────────────────────────────────────────────
YOLO_MODEL = "yolov8n.pt"
YOLO_IMGSZ = 320
YOLO_CONF = 0.4
YOLO_EVERY_N = int(os.getenv("YOLO_EVERY_N", 3))  # inference thread runs YOLO every 3rd cycle

# ── Emotion ───────────────────────────────────────────────────────────────────
MAX_FACES = 5
EMOTION_EVERY_N = 9          # ~1 emotion run / 3 seconds at 3 yolo runs/sec

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
    "dead":    ("spotify:playlist:16gsF9eLsg6A4zo4kD0teG", "#1a1a40", 60,  "static"),
    "chill":   ("spotify:playlist:44BQqhiH8baSBRuReESa07", "#2d4a7a", 100, "slow_breathe"),
    "neutral": ("spotify:playlist:4cTjO8JzLx1vmopCfNrxTm", "#4a7a4a", 150, "static"),
    "hype":    ("spotify:playlist:0ENJ8AFAuJLEhCzYx5n6yY", "#ff6600", 220, "pulse"),
    "peak":    ("spotify:playlist:2JS5ZJS4WsMOqDt07uWaHK", "#ff0066", 254, "strobe"),
}

# Track start offsets (1-based track index, position_ms)
MOOD_TRACK_STARTS = {
    "dead": [
        (1, 0_000),
        (2, 25_000),
        (3, 33_000),
        (4, 0_000),
        (5, 2_000),
    ],
    "chill": [
        (1, 106_000),
        (2, 54_000),
        (3, 26_000),
        (4, 11_000),
        (5, 23_000),
    ],
    "neutral": [
        (1, 105_000),
        (2, 68_000),
        (3, 50_000),
        (4, 0_000),
        (5, 27_000),
    ],
    "hype": [
        (1, 0_000),
        (2, 95_000),
        (3, 17_000),
        (4, 0_000),
        (5, 16_000),
    ],
    "peak": [
        (1, 61_000),
        (2, 20_000),
        (3, 0_000),
        (4, 151_000),
        (5, 12_000),
    ],
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
SPOTIFY_TRACK_POLL_S  = float(os.getenv("SPOTIFY_TRACK_POLL_S", "3.0"))
SPOTIFY_FADE_MS       = int(os.getenv("SPOTIFY_FADE_MS", 1200))
SPOTIFY_FADE_STEPS    = int(os.getenv("SPOTIFY_FADE_STEPS", 6))

# ── Hue ───────────────────────────────────────────────────────────────────────
HUE_BRIDGE_IP = os.getenv("HUE_BRIDGE_IP", "")
HUE_USERNAME  = os.getenv("HUE_USERNAME", "")
