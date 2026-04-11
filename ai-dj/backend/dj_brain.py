"""Hype scoring, mood state machine, action mapping, DJ commentary."""

import random
import time

from config import (
    PEOPLE_NORM, HYSTERESIS_SEC, MOOD_BANDS, ACTION_MAP, COMMENTARY,
)
from emotion import dominant_emotion, emotion_breakdown


class DJBrain:
    """Aggregates CV signals into hype score, mood state, and action triggers."""

    def __init__(self):
        self._mood: str = "dead"
        self._candidate_mood: str = "dead"
        self._candidate_since: float = time.time()
        self._last_commentary: str = COMMENTARY["dead"][0]
        self._last_action_reason: str = ""

    # ── public API ─────────────────────────────────────────────────────────────

    def update(
        self,
        people_count: int,
        emotions: list[dict],
        motion: float,
    ) -> dict:
        """
        Process latest CV data and return the full state dict.

        Parameters
        ----------
        people_count : number of detected persons
        emotions     : list of per-face emotion dicts (from emotion.py)
        motion       : normalised motion score 0–1
        """
        hype = self._calc_hype(people_count, emotions, motion)
        new_mood = self._update_mood(hype)
        dom_emotion = dominant_emotion(emotions)
        breakdown = emotion_breakdown(emotions)

        return {
            "people_count": people_count,
            "dominant_emotion": dom_emotion,
            "emotion_breakdown": breakdown,
            "motion": round(motion, 3),
            "hype": round(hype, 1),
            "mood": new_mood,
            "action_reason": self._last_action_reason,
            "commentary": self._last_commentary,
        }

    @property
    def mood(self) -> str:
        return self._mood

    def get_action(self) -> tuple:
        """Return (playlist_uri, hex_color, brightness, effect) for current mood."""
        return ACTION_MAP[self._mood]

    # ── internals ──────────────────────────────────────────────────────────────

    def _calc_hype(self, people_count: int, emotions: list[dict], motion: float) -> float:
        avg_happy = 0.0
        avg_sad = 0.0
        if emotions:
            avg_happy = sum(
                e.get("happy", 0) + e.get("surprise", 0) for e in emotions
            ) / len(emotions)
            avg_sad = sum(
                e.get("sad", 0) + e.get("angry", 0) + e.get("fear", 0) for e in emotions
            ) / len(emotions)

        people_factor = min(people_count / PEOPLE_NORM, 1.0)
        hype = 100 * (0.45 * motion + 0.35 * avg_happy + 0.20 * people_factor) - 25 * avg_sad
        return max(0.0, min(100.0, hype))

    def _band_for_hype(self, hype: float) -> str:
        for name, (lo, hi) in MOOD_BANDS.items():
            if lo <= hype < hi:
                return name
        return "peak"

    def _update_mood(self, hype: float) -> str:
        target = self._band_for_hype(hype)

        if target == self._mood:
            self._candidate_mood = target
            self._candidate_since = time.time()
            return self._mood

        if target != self._candidate_mood:
            self._candidate_mood = target
            self._candidate_since = time.time()

        if time.time() - self._candidate_since >= HYSTERESIS_SEC:
            if self._candidate_mood != self._mood:
                old = self._mood
                self._mood = self._candidate_mood
                self._last_action_reason = self._build_reason(old, self._mood, hype)
                self._last_commentary = random.choice(COMMENTARY[self._mood])

        return self._mood

    def _build_reason(self, old: str, new: str, hype: float) -> str:
        arrows = {"dead": 0, "chill": 1, "neutral": 2, "hype": 3, "peak": 4}
        direction = "up" if arrows.get(new, 0) > arrows.get(old, 0) else "down"
        return f"Hype {hype:.0f} → mood {old}→{new} (energy going {direction})"


# ── Standalone smoke test ─────────────────────────────────────────────────────
if __name__ == "__main__":
    brain = DJBrain()
    tests = [
        (0,  [],                               0.0),
        (3,  [{"happy": 0.8, "neutral": 0.2}], 0.3),
        (8,  [{"happy": 0.9}] * 4,            0.7),
        (10, [{"happy": 1.0}] * 5,            0.9),
        (1,  [{"sad": 0.7}],                  0.05),
    ]
    for people, emotions, motion in tests:
        state = brain.update(people, emotions, motion)
        print(f"people={people} motion={motion:.2f}  →  "
              f"hype={state['hype']:.1f}  mood={state['mood']}  "
              f"commentary={state['commentary'][:40]!r}")
