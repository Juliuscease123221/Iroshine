"""
iroshine.gradient — multi-stop gradients with positioned stops.

The model follows CSS gradients (the most widely used system for this):

    Gradient("#cfe8b8", "#8ad0e0", "#e2483a")                       # evenly spaced
    Gradient(("#cfe8b8", 0.0), ("#8ad0e0", 0.2), ("#e2483a", 1.0))  # stop = (color, position)
    Gradient({0.0: "#cfe8b8", 0.2: "#8ad0e0", 1.0: "#e2483a"})       # same thing as a dict
    Gradient("#cfe8b8", ("#8ad0e0", "20%"), "#e2483a")               # mix; positions can be "20%"

Rules (the same as CSS):
  · positions run 0 → 1 (or "0%" → "100%")
  · a stop with no position is spaced evenly between its positioned neighbours;
    the first defaults to 0 and the last to 1
  · positions never go backwards (a smaller one is raised to the previous one)
  · two stops at the same position make a hard edge, e.g. ("#fff", .5), ("#000", .5)

Colors are hex strings ("#rrggbb"), Manim colors, or (r, g, b) tuples of 0–255.

Colors are blended in OKLab by default. That's the perceptual space modern CSS
recommends: blending two colors in plain sRGB passes through a grey,
desaturated middle, and OKLab doesn't. You can pick space="oklch" (keeps
saturation, travels around the hue wheel), "srgb" (old-school), or
"linear" (physically mixed light).

    steps=5   posterize into 5 flat bands (a screen-print look)
    by=...    what drives the gradient on a BarList: "rank" | "value" | "index" | "origin"
"""

import math
from typing import Sequence

import numpy as np
from manim import ManimColor


# ─────────────────────────────────────────────── color-space conversions ──
def _srgb_to_linear(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _linear_to_srgb(c):
    c = np.clip(np.asarray(c, float), 0, 1)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * c ** (1 / 2.4) - 0.055)


_M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                [0.2119034982, 0.6806995451, 0.1073969566],
                [0.0883024619, 0.2817188376, 0.6299787005]])
_M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                [1.9779984951, -2.4285922050, 0.4505937099],
                [0.0259040371, 0.7827717662, -0.8086757660]])


def _linear_to_oklab(rgb):
    lms = np.cbrt(_M1 @ rgb)
    return _M2 @ lms


def _oklab_to_linear(lab):
    lms = np.linalg.solve(_M2, lab) ** 3
    return np.linalg.solve(_M1, lms)


def _to(space, rgb):
    """sRGB (0–1) → working space."""
    if space == "srgb":
        return np.asarray(rgb, float)
    lin = _srgb_to_linear(rgb)
    if space == "linear":
        return lin
    lab = _linear_to_oklab(lin)
    if space == "oklab":
        return lab
    L, a, b = lab                                         # oklch
    return np.array([L, math.hypot(a, b), math.atan2(b, a)])


def _from(space, v):
    if space == "srgb":
        return np.clip(v, 0, 1)
    if space == "linear":
        return _linear_to_srgb(v)
    if space == "oklch":
        L, C, h = v
        v = np.array([L, C * math.cos(h), C * math.sin(h)])
    return _linear_to_srgb(_oklab_to_linear(v))


def _parse_color(c):
    if isinstance(c, (tuple, list)) and len(c) in (3, 4) and all(isinstance(x, (int, float)) for x in c):
        return np.array(c[:3], float) / (255.0 if max(c[:3]) > 1 else 1.0)
    return np.array(ManimColor(c).to_rgb(), float)


def _parse_pos(p):
    if p is None:
        return None
    if isinstance(p, str) and p.strip().endswith("%"):
        return float(p.strip()[:-1]) / 100
    return float(p)


def _is_pos(x):
    return isinstance(x, (int, float)) or (isinstance(x, str) and x.strip().endswith("%"))


# ──────────────────────────────────────────────────────────── Gradient ──
class Gradient:
    """A multi-stop color ramp with optional stop positions. See the module docstring."""

    def __init__(self, *stops, by="rank", space="oklab", steps=None):
        if len(stops) == 1 and isinstance(stops[0], dict):
            stops = tuple((c, p) for p, c in sorted(stops[0].items()))
        if len(stops) == 1 and isinstance(stops[0], (list, tuple)) and stops[0] and \
                isinstance(stops[0][0], (list, tuple, str)) and not _is_pos(stops[0][0]):
            stops = tuple(stops[0])                       # Gradient([...]) also works
        if not stops:
            raise ValueError("a Gradient needs at least one color")
        self.by, self.space, self.steps = by, space, steps

        colors, positions = [], []
        for s in stops:
            if isinstance(s, (tuple, list)) and len(s) == 2 and (_is_pos(s[1]) or _is_pos(s[0])):
                color, pos = (s[0], s[1]) if _is_pos(s[1]) else (s[1], s[0])   # (color, pos) or (pos, color)
            else:
                color, pos = s, None
            colors.append(_parse_color(color))
            positions.append(_parse_pos(pos))

        # CSS rules: default ends, fix going-backwards, spread unpositioned stops
        if positions[0] is None:
            positions[0] = 0.0
        if positions[-1] is None:
            positions[-1] = 1.0 if len(positions) > 1 else 0.0
        for i in range(1, len(positions)):
            if positions[i] is not None:
                prev = max(p for p in positions[:i] if p is not None)
                positions[i] = max(positions[i], prev)
        i = 0
        while i < len(positions):
            if positions[i] is None:
                j = i
                while positions[j] is None:
                    j += 1
                a, b = positions[i - 1], positions[j]
                for k in range(i, j):
                    positions[k] = a + (b - a) * (k - i + 1) / (j - i + 1)
                i = j
            i += 1

        self.stops = list(zip(positions, colors))       # [(pos, rgb 0–1), ...]
        self._work = [(p, _to(space, c)) for p, c in self.stops]
        self.colors = [ManimColor(c) for _, c in self.stops]   # handy for Panel / legacy code

    # ------------------------------------------------------------------
    def at(self, t):
        """Color at position t (0–1) as a ManimColor."""
        t = min(1.0, max(0.0, float(t)))
        if self.steps and self.steps > 1:
            t = min(self.steps - 1, math.floor(t * self.steps)) / (self.steps - 1)
        st = self._work
        if t <= st[0][0]:
            return self._out(st[0][1])
        if t >= st[-1][0]:
            return self._out(st[-1][1])
        for (p0, c0), (p1, c1) in zip(st, st[1:]):
            if p0 <= t <= p1:
                if p1 == p0:                              # hard stop
                    return self._out(c1)
                u = (t - p0) / (p1 - p0)
                return self._out(self._mix(c0, c1, u))
        return self._out(st[-1][1])

    def _mix(self, a, b, u):
        if self.space == "oklch":
            dh = (b[2] - a[2] + math.pi) % (2 * math.pi) - math.pi     # shorter way round the hue wheel
            if a[1] < 1e-4:
                a = np.array([a[0], a[1], b[2]])                         # grey has no hue: borrow it
            elif b[1] < 1e-4:
                dh = 0
            return np.array([a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] + dh * u])
        return a + (b - a) * u

    def _out(self, v):
        r, g, b = (int(round(float(x) * 255)) for x in np.clip(_from(self.space, v), 0, 1))
        return ManimColor(f"#{r:02x}{g:02x}{b:02x}")

    def sample(self, n=32):
        """n evenly spaced colors (e.g. for a background)."""
        return [self.at(i / max(1, n - 1)) for i in range(n)]

    def reversed(self):
        g = Gradient(*[(c, 1 - p) for p, c in reversed(self.stops)],
                     by=self.by, space=self.space, steps=self.steps)
        return g

    def __repr__(self):
        stops = ", ".join(f"({ManimColor(c).to_hex()}, {p:g})" for p, c in self.stops)
        return f"Gradient({stops}, by={self.by!r}, space={self.space!r})"
