"""DeepFace emotion analysis on face crops from YOLO boxes."""

import cv2
import numpy as np
from deepface import DeepFace

from config import MAX_FACES, EMOTION_EVERY_N

# Emotion keys returned by DeepFace
_EMOTION_KEYS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]


def analyze_emotions(raw_frame: np.ndarray, boxes: list[tuple]) -> list[dict]:
    """
    Run DeepFace on the largest face crops from YOLO boxes.

    Parameters
    ----------
    raw_frame : BGR numpy array
    boxes     : list of (x1, y1, x2, y2, conf)

    Returns
    -------
    List of emotion dicts (one per face), each with keys matching _EMOTION_KEYS,
    values are probabilities 0–1.  Returns [] if no faces.
    """
    if not boxes or raw_frame is None:
        return []

    # Sort by area, take top MAX_FACES
    sorted_boxes = sorted(boxes, key=lambda b: (b[2]-b[0])*(b[3]-b[1]), reverse=True)
    selected = sorted_boxes[:MAX_FACES]

    results = []
    h, w = raw_frame.shape[:2]
    for (x1, y1, x2, y2, _conf) in selected:
        # Clamp crop
        x1c, y1c = max(0, x1), max(0, y1)
        x2c, y2c = min(w, x2), min(h, y2)
        if x2c <= x1c or y2c <= y1c:
            continue
        crop = raw_frame[y1c:y2c, x1c:x2c]
        if crop.size == 0:
            continue
        try:
            analysis = DeepFace.analyze(
                crop,
                actions=["emotion"],
                enforce_detection=False,
                silent=True,
            )
            # analyze returns list or dict
            rec = analysis[0] if isinstance(analysis, list) else analysis
            raw_pct: dict = rec.get("emotion", {})
            total = sum(raw_pct.values()) or 1.0
            normed = {k: raw_pct.get(k, 0) / total for k in _EMOTION_KEYS}
            results.append(normed)
        except Exception:
            pass

    return results


def dominant_emotion(emotions: list[dict]) -> str:
    """Return the single dominant emotion label across all detected faces."""
    if not emotions:
        return "neutral"
    combined = {k: 0.0 for k in _EMOTION_KEYS}
    for face in emotions:
        for k, v in face.items():
            combined[k] = combined.get(k, 0) + v
    return max(combined, key=combined.get)


def emotion_breakdown(emotions: list[dict]) -> dict:
    """Aggregate per-emotion average across all faces, rounded to 2dp."""
    if not emotions:
        return {k: 0.0 for k in _EMOTION_KEYS}
    combined = {k: 0.0 for k in _EMOTION_KEYS}
    for face in emotions:
        for k, v in face.items():
            combined[k] = combined.get(k, 0) + v
    n = len(emotions)
    return {k: round(v / n, 2) for k, v in combined.items()}


class EmotionCache:
    """
    Per-slot emotion cache: only re-runs DeepFace every EMOTION_EVERY_N frames.
    Slots are indexed by box order (largest face = slot 0).
    """

    def __init__(self):
        self._cache: dict[int, dict] = {}
        self._counters: dict[int, int] = {}

    def update(self, raw_frame: np.ndarray, boxes: list[tuple]) -> list[dict]:
        """Return cached (or freshly computed) emotions for current boxes."""
        if not boxes:
            self._cache.clear()
            self._counters.clear()
            return []

        sorted_boxes = sorted(boxes, key=lambda b: (b[2]-b[0])*(b[3]-b[1]), reverse=True)
        selected = sorted_boxes[:MAX_FACES]

        emotions = []
        h, w = raw_frame.shape[:2]
        for idx, (x1, y1, x2, y2, _conf) in enumerate(selected):
            counter = self._counters.get(idx, 0)
            if counter == 0 or idx not in self._cache:
                x1c, y1c = max(0, x1), max(0, y1)
                x2c, y2c = min(w, x2), min(h, y2)
                crop = raw_frame[y1c:y2c, x1c:x2c]
                if crop.size == 0:
                    self._counters[idx] = (counter + 1) % EMOTION_EVERY_N
                    continue
                try:
                    analysis = DeepFace.analyze(
                        crop, actions=["emotion"],
                        enforce_detection=False, silent=True,
                    )
                    rec = analysis[0] if isinstance(analysis, list) else analysis
                    raw_pct: dict = rec.get("emotion", {})
                    total = sum(raw_pct.values()) or 1.0
                    normed = {k: raw_pct.get(k, 0) / total for k in _EMOTION_KEYS}
                    self._cache[idx] = normed
                except Exception:
                    pass
            self._counters[idx] = (counter + 1) % EMOTION_EVERY_N
            if idx in self._cache:
                emotions.append(self._cache[idx])

        # Prune stale slots
        active = set(range(len(selected)))
        for k in list(self._cache.keys()):
            if k not in active:
                del self._cache[k]
                self._counters.pop(k, None)

        return emotions
