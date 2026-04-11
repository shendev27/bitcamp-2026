"""Webcam capture, YOLOv8n person detection, motion scoring."""

import threading
import time
import cv2
import numpy as np
from ultralytics import YOLO

from config import (
    WEBCAM_INDEX, FRAME_WIDTH, FRAME_HEIGHT, CAPTURE_FPS,
    YOLO_MODEL, YOLO_IMGSZ, YOLO_CONF,
)


class VisionProcessor:
    """Runs webcam capture + YOLO in a background thread; exposes latest results."""

    def __init__(self):
        self._model = YOLO(YOLO_MODEL)
        self._cap = cv2.VideoCapture(WEBCAM_INDEX)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self._cap.set(cv2.CAP_PROP_FPS, CAPTURE_FPS)

        self._lock = threading.Lock()
        self._latest_frame: np.ndarray | None = None   # BGR, with drawings
        self._latest_raw: np.ndarray | None = None     # BGR, clean
        self._latest_boxes: list[tuple] = []           # (x1,y1,x2,y2, conf)
        self._latest_motion: float = 0.0
        self._prev_gray: np.ndarray | None = None
        self._running = False
        self._thread: threading.Thread | None = None

    # ── public API ────────────────────────────────────────────────────────────

    def start(self):
        """Start the background capture thread."""
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the background capture thread."""
        self._running = False

    def get_frame(self) -> np.ndarray | None:
        """Return the latest annotated BGR frame (or None if not ready)."""
        with self._lock:
            return self._latest_frame.copy() if self._latest_frame is not None else None

    def get_raw_frame(self) -> np.ndarray | None:
        """Return the latest clean BGR frame without annotations."""
        with self._lock:
            return self._latest_raw.copy() if self._latest_raw is not None else None

    def get_detections(self) -> tuple[list[tuple], float]:
        """Return (boxes, motion_score).  boxes = [(x1,y1,x2,y2,conf), ...]."""
        with self._lock:
            return list(self._latest_boxes), self._latest_motion

    # ── internal ──────────────────────────────────────────────────────────────

    def _loop(self):
        delay = 1.0 / CAPTURE_FPS
        while self._running:
            t0 = time.time()
            ok, frame = self._cap.read()
            if not ok:
                time.sleep(0.1)
                continue

            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
            raw = frame.copy()

            # YOLO inference
            results = self._model(frame, imgsz=YOLO_IMGSZ, conf=YOLO_CONF,
                                  classes=[0], verbose=False)
            boxes = []
            if results and results[0].boxes is not None:
                for box in results[0].boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    conf = float(box.conf[0])
                    boxes.append((x1, y1, x2, y2, conf))

            # Motion score
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            motion = 0.0
            if self._prev_gray is not None:
                diff = cv2.absdiff(gray, self._prev_gray).astype(np.float32)
                motion = float(np.mean(diff) / 255.0)
            self._prev_gray = gray

            # Draw bounding boxes (labels added by emotion.py overlay)
            annotated = raw.copy()
            for (x1, y1, x2, y2, conf) in boxes:
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)

            with self._lock:
                self._latest_raw = raw
                self._latest_frame = annotated
                self._latest_boxes = boxes
                self._latest_motion = motion

            elapsed = time.time() - t0
            time.sleep(max(0, delay - elapsed))

    def draw_emotion_labels(self, frame: np.ndarray, labels: list[tuple]) -> np.ndarray:
        """Overlay emotion labels on frame.  labels = [(x1,y1,x2,y2,emotion_str), ...]."""
        out = frame.copy()
        for (x1, y1, x2, y2, label) in labels:
            cv2.rectangle(out, (x1, y1), (x2, y2), (0, 200, 255), 2)
            cv2.putText(out, label, (x1, max(y1 - 8, 12)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 255), 2)
        return out


# ── Standalone test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    vp = VisionProcessor()
    vp.start()
    print("Press 'q' to quit.")
    while True:
        frame = vp.get_frame()
        boxes, motion = vp.get_detections()
        if frame is not None:
            cv2.putText(frame, f"people:{len(boxes)}  motion:{motion:.3f}",
                        (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.imshow("AI DJ — Vision Test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    vp.stop()
    cv2.destroyAllWindows()
