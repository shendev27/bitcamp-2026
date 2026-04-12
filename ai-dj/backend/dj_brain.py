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
        loudness: float,
    ) -> dict:
        """
        Process latest CV data and return the full state dict.

        Parameters
        ----------
        people_count : number of detected persons
        emotions     : list of per-face emotion dicts (from emotion.py)
        motion       : normalised motion score 0–1
        """
        hype = self._calc_hype(people_count, emotions, motion, loudness)
        new_mood, mood_check_s = self._update_mood(hype)
        dom_emotion = dominant_emotion(emotions)
        breakdown = emotion_breakdown(emotions)

        return {
            "people_count": people_count,
            "dominant_emotion": dom_emotion,
            "emotion_breakdown": breakdown,
            "motion": round(motion, 3),
            "loudness": round(loudness, 3),
            "hype": round(hype, 1),
            "mood": new_mood,
            "mood_check_s": round(mood_check_s, 1),
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

    def _calc_hype(self, people_count: int, emotions: list[dict], motion: float, loudness: float) -> float:
        if people_count <= 0:
            if not hasattr(self, "_no_people_hype"):
                self._no_people_hype = 6.0
            drift = random.uniform(-0.6, 0.6)
            self._no_people_hype = max(3.0, min(10.0, self._no_people_hype + drift))
            return self._no_people_hype

        avg_happy = 0.0
        if emotions:
            avg_happy = sum(
                e.get("happy", 0) + e.get("surprise", 0) for e in emotions
            ) / len(emotions)

        # Motion: scale up so less movement yields more hype.
        motion_scaled = min(1.0, motion * 10.0)
        # Loudness: 20% -> 0, 80% -> 1 (linear).
        loudness_scaled = min(1.0, max(0.0, (loudness - 0.2) / 0.6))
        # People: max at 4 people.
        people_factor = min(people_count / 4.0, 1.0)

        hype = 100 * (
            0.60 * motion_scaled
            + 0.30 * loudness_scaled
            + 0.05 * avg_happy
            + 0.05 * people_factor
        )
        return max(0.0, min(100.0, hype))

    def _band_for_hype(self, hype: float) -> str:
        for name, (lo, hi) in MOOD_BANDS.items():
            if lo <= hype < hi:
                return name
        return "peak"

    def _update_mood(self, hype: float) -> tuple[str, float]:
        now = time.time()
        target = self._band_for_hype(hype)

        if not hasattr(self, "_next_check_at"):
            self._next_check_at = now + 10.0
        if not hasattr(self, "_jump_candidate"):
            self._jump_candidate = None
            self._jump_since = 0.0

        # Jump override: 3-level jump sustained for 1.5s.
        if abs(self._band_index(target) - self._band_index(self._mood)) >= 3:
            if self._jump_candidate != target:
                self._jump_candidate = target
                self._jump_since = now
            elif now - self._jump_since >= 1.5:
                old = self._mood
                self._mood = target
                self._last_action_reason = self._build_reason(old, self._mood, hype)
                self._last_commentary = random.choice(COMMENTARY[self._mood])
                self._next_check_at = now + 10.0
                self._jump_candidate = None
        else:
            self._jump_candidate = None

        # Regular 10s mood check cadence.
        if now >= self._next_check_at:
            if target != self._mood:
                old = self._mood
                self._mood = target
                self._last_action_reason = self._build_reason(old, self._mood, hype)
                self._last_commentary = random.choice(COMMENTARY[self._mood])
            self._next_check_at = now + 10.0

        mood_check_s = max(0.0, self._next_check_at - now)
        return self._mood, mood_check_s

    def _band_index(self, mood: str) -> int:
        order = ["dead", "chill", "neutral", "hype", "peak"]
        return order.index(mood) if mood in order else 0

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
