"""Webcam capture, YOLOv8n person detection, motion scoring, and emotion analysis."""

import threading
import time
import cv2
import numpy as np
from ultralytics import YOLO
from deepface import DeepFace

from config import (
    WEBCAM_INDEX, FRAME_WIDTH, FRAME_HEIGHT, CAPTURE_FPS,
    YOLO_MODEL, YOLO_IMGSZ, YOLO_CONF, MAX_FACES, EMOTION_EVERY_N,
)

_EMOTION_KEYS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]


class VisionProcessor:
    """
    Single background thread: webcam → YOLO person detect → DeepFace emotion →
    annotated frame. Exposes latest results thread-safely.
    """

    def __init__(self):
        self._model = YOLO(YOLO_MODEL)
        self._cap: cv2.VideoCapture | None = None

        self._lock = threading.Lock()
        self._latest_frame: np.ndarray | None = None   # annotated BGR
        self._latest_boxes: list[tuple] = []           # (x1,y1,x2,y2,conf)
        self._latest_emotions: list[dict] = []         # per-face emotion dicts
        self._latest_motion: float = 0.0

        self._prev_gray: np.ndarray | None = None
        self._emotion_counters: dict[int, int] = {}
        self._emotion_cache: dict[int, dict] = {}

        self._running = False
        self._thread: threading.Thread | None = None

    # ── public API ────────────────────────────────────────────────────────────

    def start(self):
        """Open camera and start the background processing thread."""
        self._cap = cv2.VideoCapture(WEBCAM_INDEX)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self._cap.set(cv2.CAP_PROP_FPS, CAPTURE_FPS)
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the thread and release the camera."""
        self._running = False
        if self._cap:
            self._cap.release()

    def get_frame(self) -> np.ndarray | None:
        """Return the latest annotated BGR frame (YOLO boxes + emotion labels)."""
        with self._lock:
            return self._latest_frame.copy() if self._latest_frame is not None else None

    def get_state(self) -> tuple[list[tuple], list[dict], float]:
        """Return (boxes, emotions, motion_score) from the latest frame."""
        with self._lock:
            return (
                list(self._latest_boxes),
                list(self._latest_emotions),
                self._latest_motion,
            )

    # ── internal ──────────────────────────────────────────────────────────────

    def _loop(self):
        delay = 1.0 / CAPTURE_FPS
        while self._running:
            t0 = time.time()
            ok, frame = self._cap.read()
            if not ok:
                time.sleep(0.05)
                continue

            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

            # YOLO — person detection
            results = self._model(frame, imgsz=YOLO_IMGSZ, conf=YOLO_CONF,
                                  classes=[0], verbose=False)
            boxes = []
            if results and results[0].boxes is not None:
                for box in results[0].boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    conf = float(box.conf[0])
                    boxes.append((x1, y1, x2, y2, conf))

            # Sort by area, take top MAX_FACES
            sorted_boxes = sorted(boxes, key=lambda b: (b[2]-b[0])*(b[3]-b[1]), reverse=True)
            top_boxes = sorted_boxes[:MAX_FACES]

            # Motion score
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            motion = 0.0
            if self._prev_gray is not None:
                diff = cv2.absdiff(gray, self._prev_gray).astype(np.float32)
                motion = float(np.mean(diff) / 255.0)
            self._prev_gray = gray

            # DeepFace emotion — cached per slot
            emotions = self._run_emotions(frame, top_boxes)

            # Draw annotations
            annotated = self._draw(frame, top_boxes, emotions)

            with self._lock:
                self._latest_frame = annotated
                self._latest_boxes = boxes          # all boxes for people_count
                self._latest_emotions = emotions
                self._latest_motion = motion

            elapsed = time.time() - t0
            time.sleep(max(0, delay - elapsed))

    def _run_emotions(self, frame: np.ndarray, boxes: list[tuple]) -> list[dict]:
        """Run DeepFace on face crops with per-slot frame skipping."""
        h, w = frame.shape[:2]
        emotions = []
        active = set(range(len(boxes)))

        for idx, (x1, y1, x2, y2, _) in enumerate(boxes):
            counter = self._emotion_counters.get(idx, 0)
            if counter == 0 or idx not in self._emotion_cache:
                crop = frame[max(0,y1):min(h,y2), max(0,x1):min(w,x2)]
                if crop.size > 0:
                    try:
                        res = DeepFace.analyze(crop, actions=["emotion"],
                                               enforce_detection=False, silent=True)
                        rec = res[0] if isinstance(res, list) else res
                        raw = rec.get("emotion", {})
                        total = sum(raw.values()) or 1.0
                        self._emotion_cache[idx] = {k: raw.get(k, 0)/total for k in _EMOTION_KEYS}
                    except Exception:
                        pass
            self._emotion_counters[idx] = (counter + 1) % EMOTION_EVERY_N
            if idx in self._emotion_cache:
                emotions.append(self._emotion_cache[idx])

        # Prune stale slots
        for k in list(self._emotion_cache):
            if k not in active:
                del self._emotion_cache[k]
                self._emotion_counters.pop(k, None)

        return emotions

    def _draw(self, frame: np.ndarray, boxes: list[tuple], emotions: list[dict]) -> np.ndarray:
        """Draw YOLO boxes and emotion labels onto the frame."""
        out = frame.copy()
        for i, (x1, y1, x2, y2, _) in enumerate(boxes):
            has_emotion = i < len(emotions)
            color = (0, 200, 255) if has_emotion else (0, 255, 0)
            cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)
            if has_emotion:
                label = max(emotions[i], key=emotions[i].get)
                conf = emotions[i][label]
                text = f"{label} {conf:.0%}"
                cv2.putText(out, text, (x1, max(y1 - 8, 12)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
        return out


# ── Standalone test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    vp = VisionProcessor()
    vp.start()
    print("Press 'q' to quit.")
    while True:
        frame = vp.get_frame()
        boxes, emotions, motion = vp.get_state()
        if frame is not None:
            cv2.putText(frame, f"people:{len(boxes)}  motion:{motion:.3f}",
                        (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.imshow("PASS THE AUX — Vision", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    vp.stop()
    cv2.destroyAllWindows()
