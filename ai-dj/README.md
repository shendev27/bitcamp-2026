# PASS THE AUX — Real-time Crowd-Reactive DJ System

Webcam → YOLO person detection → DeepFace emotions → hype score → auto Spotify playlist switch + Hue lights + live dashboard.

## Architecture

```
Webcam → VisionProcessor (thread) → EmotionCache → DJBrain → Spotify / Lights
                                                          ↓
                                                 FastAPI /ws  →  React UI
                                                 FastAPI /video_feed (MJPEG)
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- A webcam
- (Optional) Active Spotify Premium account + Spotify app
- (Optional) Philips Hue bridge

## Setup

### 1. Backend

```bash
cd ai-dj/backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> **Note:** DeepFace downloads ~500 MB of face models on first run. This is normal — wait for the download to complete before expecting emotion labels.

Copy `.env.example` to `.env` and fill in values:

```bash
cp .env.example .env
```

### 2. Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SPOTIPY_CLIENT_ID` | Spotify only | From Spotify Developer Dashboard |
| `SPOTIPY_CLIENT_SECRET` | Spotify only | From Spotify Developer Dashboard |
| `SPOTIPY_REDIRECT_URI` | Spotify only | Must match app settings (default: `http://localhost:8888/callback`) |
| `HUE_BRIDGE_IP` | Hue only | Leave blank for mock lights (prints to console) |
| `HUE_USERNAME` | Hue only | Hue API username (see Hue setup below) |
| `WEBCAM_INDEX` | No | Webcam device index (default: `0`) |

### 3. Spotify App Setup

1. Go to [https://developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Create an app
3. Add `http://localhost:8888/callback` as a Redirect URI
4. Copy Client ID and Client Secret to `.env`
5. Open Spotify on any device and start playing something (so there's an active device)
6. On first run, a browser window will open for OAuth. Complete the login.
7. Replace the `REPLACE_WITH_*_URI` playlist constants in `config.py` with your own Spotify playlist URIs (right-click playlist → Share → Copy Spotify URI)

### 4. Philips Hue Setup (optional)

```bash
# Find your bridge IP
python -c "from phue import PhueRegistrationException; from phue import Bridge; b = Bridge('YOUR_BRIDGE_IP'); b.connect()"
```

Press the button on your Hue bridge when prompted, then copy the username printed to `.env`.

Leave `HUE_BRIDGE_IP` blank to use `MockLightController` (prints color/brightness to console).

### 5. Frontend

```bash
cd ai-dj/frontend
npm install
```

## Running

### Backend
```bash
cd ai-dj/backend
source .venv/bin/activate
uvicorn main:app --reload
```

### Frontend (separate terminal)
```bash
cd ai-dj/frontend
npm run dev
```

Open `http://localhost:5173` in a browser.

## Troubleshooting

**No webcam / wrong camera**
- Set `WEBCAM_INDEX=1` (or 2, 3…) in `.env` to try other cameras
- On macOS/Linux, run `ls /dev/video*` to list devices

**DeepFace first-run model download**
- Wait 2–5 minutes on first start — it downloads VGG-Face and other model weights
- If it hangs, check your internet connection; models are cached in `~/.deepface/`

**"No active Spotify device" warning**
- Open Spotify (app or web player) and play any track to create an active session
- The backend will continue without Spotify — music just won't change

**Backend crashes on startup**
- Check Python version: `python --version` (need 3.10+)
- Ensure all packages installed: `pip install -r requirements.txt`

**Frontend shows "CONNECTING…"**
- Make sure the backend is running: `uvicorn main:app --reload`
- Check CORS — both must run on localhost

**Hue lights not responding**
- Verify bridge IP with: `python -c "from phue import Bridge; b = Bridge('IP'); b.connect()"`
- Press bridge button before connecting for the first time
