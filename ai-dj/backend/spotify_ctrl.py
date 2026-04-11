"""Spotipy wrapper: OAuth auth, playlist switching, playback info."""

import random
import threading
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from config import (
    SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,
    SPOTIPY_REDIRECT_URI, SPOTIFY_SCOPES,
    SPOTIFY_FADE_MS, SPOTIFY_FADE_STEPS,
    ACTION_MAP, MOOD_TRACK_STARTS,
)

_BLANK_TRACK = {
    "name": "-",
    "artist": "-",
    "art_url": "",
    "start_ms": None,
    "start_track_index": None,
}


class SpotifyController:
    """Wraps Spotipy for the actions needed by the DJ Brain."""

    def __init__(self):
        self._sp: spotipy.Spotify | None = None
        self._active = False
        self._fade_lock = threading.Lock()
        self._fade_thread: threading.Thread | None = None
        self._last_start_ms: int | None = None
        self._last_track_index: int | None = None

    def connect(self):
        """Authenticate via Authorization Code Flow.  Stores token cache in .cache."""
        if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET:
            print("[SPOTIFY] Missing credentials - Spotify disabled.")
            return

        auth = SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope=SPOTIFY_SCOPES,
            open_browser=True,
        )
        self._sp = spotipy.Spotify(auth_manager=auth)

        # Verify an active device exists
        try:
            devices = self._sp.devices().get("devices", [])
            active = [d for d in devices if d["is_active"]]
            if active:
                print(f"[SPOTIFY] Active device: {active[0]['name']}")
                self._active = True
            else:
                all_names = [d["name"] for d in devices]
                if all_names:
                    print(f"[SPOTIFY] No active device. Available: {all_names}. "
                          "Start playing on one of them.")
                else:
                    print("[SPOTIFY] No devices found. Open Spotify on any device and start playing.")
                self._active = False
        except Exception as exc:
            print(f"[SPOTIFY] Device check failed: {exc}")

    def play_mood(self, mood: str):
        """Start playback for a mood using configured playlist and offsets."""
        if mood not in ACTION_MAP:
            return
        playlist_uri = ACTION_MAP[mood][0]
        choices = MOOD_TRACK_STARTS.get(mood) or []
        if choices:
            track_index, start_ms = random.choice(choices)
            self.play_playlist(playlist_uri, track_index=track_index, position_ms=start_ms)
        else:
            self.play_playlist(playlist_uri)

    def play_playlist(self, playlist_uri: str, track_index: int | None = None, position_ms: int | None = None):
        """Switch playback to the given playlist URI (context)."""
        if not self._sp or "REPLACE_WITH" in playlist_uri:
            return
        position_ms = int(position_ms or 0)
        if SPOTIFY_FADE_MS <= 0 or SPOTIFY_FADE_STEPS < 2:
            self._start_playback(playlist_uri, track_index, position_ms)
            return
        if self._fade_thread and self._fade_thread.is_alive():
            return
        self._fade_thread = threading.Thread(
            target=self._fade_switch, args=(playlist_uri, track_index, position_ms), daemon=True
        )
        self._fade_thread.start()

    def current_track(self) -> dict:
        """Return current track info as dict with name/artist/art_url keys."""
        if not self._sp:
            return _BLANK_TRACK
        try:
            pb = self._sp.current_playback()
            if not pb or not pb.get("item"):
                return _BLANK_TRACK
            item = pb["item"]
            art = item["album"]["images"][0]["url"] if item["album"]["images"] else ""
            artists = ", ".join(a["name"] for a in item["artists"])
            return {
                "name": item["name"],
                "artist": artists,
                "art_url": art,
                "start_ms": self._last_start_ms,
                "start_track_index": self._last_track_index,
            }
        except Exception:
            return _BLANK_TRACK

    @property
    def is_active(self) -> bool:
        return self._active

    # internals

    def _start_playback(self, playlist_uri: str, track_index: int | None, position_ms: int):
        try:
            kwargs: dict = {"context_uri": playlist_uri}
            if track_index is not None:
                track_pos = max(0, int(track_index) - 1)
                kwargs["offset"] = {"position": track_pos}
            if position_ms > 0:
                kwargs["position_ms"] = max(0, int(position_ms))
            self._sp.start_playback(**kwargs)
            self._active = True
            self._last_start_ms = kwargs.get("position_ms", 0)
            self._last_track_index = track_index
        except spotipy.SpotifyException as exc:
            if "NO_ACTIVE_DEVICE" in str(exc):
                print("[SPOTIFY] No active device - cannot switch playlist.")
                self._active = False
            else:
                print(f"[SPOTIFY] Playback error: {exc}")

    def _get_volume(self) -> int:
        try:
            pb = self._sp.current_playback()
            if pb and pb.get("device") and pb["device"].get("volume_percent") is not None:
                return int(pb["device"]["volume_percent"])
        except Exception:
            pass
        return 60

    def _set_volume(self, volume: int):
        try:
            self._sp.volume(max(0, min(100, int(volume))))
        except Exception:
            pass

    def _fade_switch(self, playlist_uri: str, track_index: int | None, position_ms: int):
        if not self._sp:
            return
        if not self._fade_lock.acquire(blocking=False):
            return
        try:
            start_vol = self._get_volume()
            steps = max(2, SPOTIFY_FADE_STEPS)
            step_delay = (SPOTIFY_FADE_MS / steps) / 1000.0

            for i in range(steps):
                v = start_vol * (1 - (i + 1) / steps)
                self._set_volume(v)
                time.sleep(step_delay)

            self._start_playback(playlist_uri, track_index, position_ms)

            for i in range(steps):
                v = start_vol * ((i + 1) / steps)
                self._set_volume(v)
                time.sleep(step_delay)
        finally:
            self._fade_lock.release()