"""Spotipy wrapper: OAuth auth, playlist switching, playback info."""

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from config import (
    SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,
    SPOTIPY_REDIRECT_URI, SPOTIFY_SCOPES,
)

_BLANK_TRACK = {"name": "—", "artist": "—", "art_url": ""}


class SpotifyController:
    """Wraps Spotipy for the actions needed by the DJ Brain."""

    def __init__(self):
        self._sp: spotipy.Spotify | None = None
        self._active = False

    def connect(self):
        """Authenticate via Authorization Code Flow.  Stores token cache in .cache."""
        if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET:
            print("[SPOTIFY] Missing credentials — Spotify disabled.")
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

    def play_playlist(self, playlist_uri: str):
        """Switch playback to the given playlist URI (context)."""
        if not self._sp or "REPLACE_WITH" in playlist_uri:
            return
        try:
            self._sp.start_playback(context_uri=playlist_uri)
            self._active = True
        except spotipy.SpotifyException as exc:
            if "NO_ACTIVE_DEVICE" in str(exc):
                print("[SPOTIFY] No active device — cannot switch playlist.")
                self._active = False
            else:
                print(f"[SPOTIFY] Playback error: {exc}")

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
            return {"name": item["name"], "artist": artists, "art_url": art}
        except Exception:
            return _BLANK_TRACK

    @property
    def is_active(self) -> bool:
        return self._active
