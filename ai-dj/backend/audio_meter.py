"""Microphone loudness meter (RMS) for hype weighting."""

from __future__ import annotations

import threading

import numpy as np

try:
    import sounddevice as sd
except Exception:  # pragma: no cover - optional dep
    sd = None  # type: ignore


class AudioMeter:
    """Continuously measures mic loudness and exposes a 0–1 level."""

    def __init__(self, *, samplerate: int = 16000, blocksize: int = 1024):
        self._samplerate = samplerate
        self._blocksize = blocksize
        self._lock = threading.Lock()
        self._level = 0.0
        self._stream = None
        self._available = sd is not None

    def start(self):
        if not self._available:
            print("[AUDIO] sounddevice not available — loudness disabled.")
            return

        def _callback(indata, frames, time, status):
            if indata is None or len(indata) == 0:
                return
            rms = float(np.sqrt(np.mean(np.square(indata))))
            # Scale to 0–1 (very hot; DJBrain also scales loudness).
            level = min(1.0, rms * 36.0)
            with self._lock:
                self._level = (self._level * 0.8) + (level * 0.2)

        try:
            self._stream = sd.InputStream(
                samplerate=self._samplerate,
                blocksize=self._blocksize,
                channels=1,
                dtype="float32",
                callback=_callback,
            )
            self._stream.start()
            print("[AUDIO] Mic monitor started.")
        except Exception as exc:
            print(f"[AUDIO] Mic monitor failed: {exc}")
            self._stream = None

    def stop(self):
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

    def get_level(self) -> float:
        with self._lock:
            return float(self._level)
