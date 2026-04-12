"""FastAPI app: /video_feed MJPEG + /ws JSON state at ~5 Hz."""

import asyncio
import random
import time
import threading
from contextlib import asynccontextmanager
import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from config import BROADCAST_HZ, ACTION_MAP, COMMENTARY
from vision import VisionProcessor
from audio_meter import AudioMeter
from dj_brain import DJBrain
from lights import make_controller, lerp_hex
from spotify_ctrl import SpotifyController

vision = VisionProcessor()
brain = DJBrain()
lights = make_controller()
spotify = SpotifyController()
audio_meter = AudioMeter()

_latest_state: dict = {}
_current_hex: str = ACTION_MAP["dead"][1]
_manual_mood: str | None = None
_manual_until: float = 0.0
_manual_commentary: str = ""


@asynccontextmanager
async def lifespan(app: FastAPI):
    def _start_vision():
        try:
            vision.start()
            print("[STARTUP] Vision thread started.")
        except Exception as exc:
            print(f"[STARTUP] Vision start failed: {exc}")

    threading.Thread(target=_start_vision, daemon=True).start()
    threading.Thread(target=audio_meter.start, daemon=True).start()
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, spotify.connect)
    asyncio.create_task(_brain_loop())
    yield
    vision.stop()
    audio_meter.stop()


app = FastAPI(title="Vibe Check", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/debug/mood/{mood}")
async def debug_set_mood(mood: str, seconds: int = 10):
    """Temporary mood override for UI testing — also triggers a song change."""
    global _manual_mood, _manual_until, _manual_commentary
    if mood not in ACTION_MAP:
        return {"ok": False, "error": "unknown mood"}
    seconds = max(5, min(300, int(seconds)))
    _manual_mood = mood
    _manual_until = time.time() + seconds
    _manual_commentary = random.choice(COMMENTARY[mood])
    # Run blocking Spotify call in a thread so we don't stall the event loop.
    # immediate=True bypasses the fade-thread guard so button presses always fire.
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, lambda: spotify.play_mood(mood, immediate=True))
    return {"ok": True, "mood": mood, "until": _manual_until}


async def _brain_loop():
    """Read vision results, update brain, push lights/spotify, cache state."""
    global _latest_state, _current_hex, _manual_mood, _manual_until
    prev_mood = brain.mood
    interval = 1.0 / BROADCAST_HZ

    while True:
        t0 = time.time()

        boxes, emotions, motion = vision.get_state()
        loudness = audio_meter.get_level()
        state = brain.update(len(boxes), emotions, motion, loudness)
        mood = state["mood"]
        now = time.time()
        if _manual_mood and now < _manual_until:
            mood = _manual_mood
            state["mood"] = mood
            state["action_reason"] = f"Manual override -> {mood}"
            state["commentary"] = _manual_commentary   # picked once at override start
        elif _manual_mood and now >= _manual_until:
            _manual_mood = None

        target_hex = ACTION_MAP[mood][1]
        _current_hex = lerp_hex(_current_hex, target_hex, 0.15)
        brightness, effect = ACTION_MAP[mood][2], ACTION_MAP[mood][3]
        lights.set_state(_current_hex, brightness, effect)

        if mood != prev_mood:
            spotify.play_mood(mood)
            prev_mood = mood

        track = spotify.current_track()
        _latest_state = {"ts": int(time.time()), **state, "track": track}

        elapsed = time.time() - t0
        await asyncio.sleep(max(0, interval - elapsed))


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
