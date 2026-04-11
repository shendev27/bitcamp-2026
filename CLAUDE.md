# AI DJ — Claude Code Guide

Real-time crowd-reactive DJ. Webcam → CV → mood/hype → Spotify + Hue + UI.

## Stack (do not substitute)
- Backend: Python 3.10+, FastAPI, Uvicorn, WebSockets, OpenCV, Ultralytics YOLOv8n, DeepFace, Spotipy, phue
- Frontend: Vite + React + Tailwind, Framer Motion, Recharts
- Transport: WS `/ws` @ ~5 Hz, MJPEG `/video_feed`

## Layout
backend/   main.py vision.py emotion.py dj_brain.py spotify_ctrl.py lights.py config.py
frontend/  src/{App.jsx, components/, hooks/useWS.js, theme.js}

## Run
- Backend: `cd backend && uvicorn main:app --reload`
- Frontend: `cd frontend && npm run dev`
- Env: copy `.env.example` → `.env`. Mock lights auto-enable if `HUE_BRIDGE_IP` unset.

## Core Contracts

**WS state JSON** (single source of truth, do not rename keys):
`ts, people_count, dominant_emotion, emotion_breakdown, motion, hype, mood, track, action_reason, commentary`

**Hype formula** (`dj_brain.py`, keep simple, do not "improve"):
hype = 100*(0.45motion + 0.35avg_happy + 0.20people_factor) - 25avg_sad
people_factor = min(count/8, 1.0). Clamp 0–100.

**Mood bands** (with 2s hysteresis before switching):
dead <20 | chill 20–45 | neutral 45–65 | hype 65–85 | peak >85

**Action map**: state → (playlist_uri, hex, brightness, effect). Lives in `config.py`. Spotify call only on state change (debounced); lights lerp every tick.

## Performance Rules (non-negotiable)
- YOLOv8n only, `imgsz=480`, frame resized to 640x480
- DeepFace on ≤5 largest crops, every other frame
- CV in background thread; WS loop reads latest state, never blocks
- No new models, no training, no LLM calls

## Style
- Minimal comments, docstrings on public funcs only
- No new deps without updating `requirements.txt` / `package.json`
- No DB, no auth, no Docker, no tests beyond smoke checks
- Frontend: dark `#0a0a0f` bg, glassmorphism (`bg-white/5 backdrop-blur border-white/10`), mood-driven gradient via `theme.js`

## Gotchas
- DeepFace downloads models on first run — warn user in README
- Spotify needs an active device; warn + continue, don't crash
- `enforce_detection=False` on DeepFace or it throws on empty crops
- YOLO class 0 = person, filter others out
- Don't block the event loop with cv2.VideoCapture — thread it

## When Editing
- Touching `dj_brain.py`? Don't change the JSON contract or formula weights without being told.
- Touching `config.py`? Playlist URIs are placeholders — leave the comment.
- Adding a feature? Check "Non-Goals" in the original spec first. If it's there, don't.

## Build Order (if starting fresh)
1. config + requirements + .env.example
2. vision.py (standalone webcam+YOLO test)
3. emotion.py
4. dj_brain.py (print test with fake inputs)
5. lights.py (mock first)
6. spotify_ctrl.py
7. main.py (WS + MJPEG)
8. frontend scaffold + useWS + StatsCards
9. VideoPanel + DJPanel + theme reactivity
10. Polish