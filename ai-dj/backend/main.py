"""FastAPI app: /video_feed MJPEG + /ws JSON state at ~5 Hz."""

import asyncio
import time
from contextlib import asynccontextmanager
import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from config import BROADCAST_HZ, ACTION_MAP
from vision import VisionProcessor
from emotion import EmotionCache
from dj_brain import DJBrain
from lights import make_controller, lerp_hex
from spotify_ctrl import SpotifyController

# ── Shared state ──────────────────────────────────────────────────────────────
vision = VisionProcessor()
emotion_cache = EmotionCache()
brain = DJBrain()
lights = make_controller()
spotify = SpotifyController()

_latest_state: dict = {}
_annotated_frame: np.ndarray | None = None
_current_hex: str = ACTION_MAP["dead"][1]


# ── Lifecycle ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    vision.start()
    spotify.connect()
    asyncio.create_task(_brain_loop())
    yield
    vision.stop()


app = FastAPI(title="PASS THE AUX", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Core loop (runs as background task) ───────────────────────────────────────
async def _brain_loop():
    """Process CV data, update brain, push lights/spotify, cache state."""
    global _latest_state, _annotated_frame, _current_hex
    prev_mood = brain.mood
    interval = 1.0 / BROADCAST_HZ

    while True:
        t0 = time.time()

        raw = vision.get_raw_frame()
        boxes, motion = vision.get_detections()

        emotions = []
        if raw is not None and boxes:
            emotions = await asyncio.get_event_loop().run_in_executor(
                None, emotion_cache.update, raw, boxes
            )

        state = brain.update(len(boxes), emotions, motion)
        mood = state["mood"]

        # Build emotion label overlays
        labels = []
        if raw is not None:
            sorted_boxes = sorted(boxes, key=lambda b: (b[2]-b[0])*(b[3]-b[1]), reverse=True)
            for i, (x1, y1, x2, y2, _c) in enumerate(sorted_boxes[:5]):
                if i < len(emotions):
                    label = max(emotions[i], key=emotions[i].get)
                else:
                    label = ""
                labels.append((x1, y1, x2, y2, label))

        # Draw annotated frame
        base_frame = vision.get_frame()
        if base_frame is not None and labels:
            annotated = vision.draw_emotion_labels(base_frame, labels)
        else:
            annotated = base_frame
        _annotated_frame = annotated

        # Lerp light color toward target
        target_hex = ACTION_MAP[mood][1]
        _current_hex = lerp_hex(_current_hex, target_hex, 0.15)
        brightness, effect = ACTION_MAP[mood][2], ACTION_MAP[mood][3]
        lights.set_state(_current_hex, brightness, effect)

        # Spotify: only on mood change
        if mood != prev_mood:
            playlist_uri = ACTION_MAP[mood][0]
            spotify.play_playlist(playlist_uri)
            prev_mood = mood

        track = spotify.current_track()
        _latest_state = {
            "ts": int(time.time()),
            **state,
            "track": track,
        }

        elapsed = time.time() - t0
        await asyncio.sleep(max(0, interval - elapsed))


# ── WebSocket endpoint ────────────────────────────────────────────────────────
@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    """Push state JSON to connected clients at ~5 Hz."""
    await websocket.accept()
    try:
        while True:
            if _latest_state:
                await websocket.send_json(_latest_state)
            await asyncio.sleep(1.0 / BROADCAST_HZ)
    except WebSocketDisconnect:
        pass


# ── MJPEG video feed ──────────────────────────────────────────────────────────
def _frame_generator():
    while True:
        frame = _annotated_frame
        if frame is None:
            time.sleep(0.05)
            continue
        ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if ok:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
            )
        time.sleep(1.0 / BROADCAST_HZ)


@app.get("/video_feed")
def video_feed():
    """MJPEG stream with bounding boxes and emotion labels."""
    return StreamingResponse(
        _frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
