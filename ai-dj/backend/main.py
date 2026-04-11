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
from dj_brain import DJBrain
from lights import make_controller, lerp_hex
from spotify_ctrl import SpotifyController

# ── Shared state ──────────────────────────────────────────────────────────────
vision = VisionProcessor()
brain = DJBrain()
lights = make_controller()
spotify = SpotifyController()

_latest_state: dict = {}
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


# ── Core loop ─────────────────────────────────────────────────────────────────
async def _brain_loop():
    """Read latest vision results, update brain, push lights/spotify, cache state."""
    global _latest_state, _current_hex
    prev_mood = brain.mood
    interval = 1.0 / BROADCAST_HZ

    while True:
        t0 = time.time()

        boxes, emotions, motion = vision.get_state()
        state = brain.update(len(boxes), emotions, motion)
        mood = state["mood"]

        # Lerp light color toward target
        target_hex = ACTION_MAP[mood][1]
        _current_hex = lerp_hex(_current_hex, target_hex, 0.15)
        brightness, effect = ACTION_MAP[mood][2], ACTION_MAP[mood][3]
        lights.set_state(_current_hex, brightness, effect)

        # Spotify: only on mood change
        if mood != prev_mood:
            spotify.play_playlist(ACTION_MAP[mood][0])
            prev_mood = mood

        track = spotify.current_track()
        _latest_state = {"ts": int(time.time()), **state, "track": track}

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
    """Stream annotated frames as fast as the vision thread produces them."""
    while True:
        frame = vision.get_frame()
        if frame is None:
            time.sleep(0.02)
            continue
        ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
        if ok:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
            )


@app.get("/video_feed")
def video_feed():
    """MJPEG stream with YOLO boxes and emotion labels."""
    return StreamingResponse(
        _frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
