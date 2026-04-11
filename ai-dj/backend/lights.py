"""Philips Hue light control with MockLightController fallback."""

import time


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert '#rrggbb' string to (r, g, b) 0–255."""
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_xy(r: int, g: int, b: int) -> tuple[float, float]:
    """Convert sRGB to Philips Hue CIE xy using the Wide-gamut D65 matrix."""
    r_, g_, b_ = r / 255.0, g / 255.0, b / 255.0
    # Gamma correction
    r_ = pow((r_ + 0.055) / 1.055, 2.4) if r_ > 0.04045 else r_ / 12.92
    g_ = pow((g_ + 0.055) / 1.055, 2.4) if g_ > 0.04045 else g_ / 12.92
    b_ = pow((b_ + 0.055) / 1.055, 2.4) if b_ > 0.04045 else b_ / 12.92
    X = r_ * 0.664511 + g_ * 0.154324 + b_ * 0.162028
    Y = r_ * 0.283881 + g_ * 0.668433 + b_ * 0.047685
    Z = r_ * 0.000088 + g_ * 0.072310 + b_ * 0.986039
    denom = X + Y + Z or 1e-9
    return round(X / denom, 4), round(Y / denom, 4)


def lerp_hex(a: str, b: str, t: float) -> str:
    """Linear interpolate between two hex colors."""
    ar, ag, ab_ = hex_to_rgb(a)
    br, bg, bb = hex_to_rgb(b)
    r = int(ar + (br - ar) * t)
    g = int(ag + (bg - ag) * t)
    bv = int(ab_ + (bb - ab_) * t)
    return f"#{r:02x}{g:02x}{bv:02x}"


class LightController:
    """Abstract interface for light control."""

    def set_state(self, hex_color: str, brightness: int, effect: str):
        raise NotImplementedError


class MockLightController(LightController):
    """Prints light state to console instead of hitting real hardware."""

    def set_state(self, hex_color: str, brightness: int, effect: str):
        """Log light state update."""
        print(f"[MOCK LIGHTS] color={hex_color}  brightness={brightness}  effect={effect}")


class HueLightController(LightController):
    """Controls Philips Hue lights via phue."""

    def __init__(self, bridge_ip: str, username: str = ""):
        from phue import Bridge
        self._bridge = Bridge(bridge_ip, username=username or None)
        self._bridge.connect()
        self._lights = self._bridge.lights

    def set_state(self, hex_color: str, brightness: int, effect: str):
        """Push color + brightness to all Hue lights."""
        r, g, b = hex_to_rgb(hex_color)
        x, y = rgb_to_xy(r, g, b)
        hue_effect = "none"
        alert = "none"
        if effect == "strobe":
            alert = "lselect"
        elif effect == "pulse":
            hue_effect = "colorloop"

        for light in self._lights:
            try:
                light.on = True
                light.brightness = max(1, min(254, brightness))
                light.xy = [x, y]
                light.effect = hue_effect
                light.alert = alert
            except Exception as exc:
                print(f"[HUE] Failed to set light {light.name}: {exc}")


def make_controller() -> LightController:
    """Factory: returns HueLightController if HUE_BRIDGE_IP is set, else Mock."""
    from config import HUE_BRIDGE_IP, HUE_USERNAME
    if HUE_BRIDGE_IP:
        try:
            ctrl = HueLightController(HUE_BRIDGE_IP, HUE_USERNAME)
            print(f"[LIGHTS] Connected to Hue bridge at {HUE_BRIDGE_IP}")
            return ctrl
        except Exception as exc:
            print(f"[LIGHTS] Hue init failed ({exc}), falling back to mock.")
    print("[LIGHTS] No HUE_BRIDGE_IP set — using MockLightController.")
    return MockLightController()
