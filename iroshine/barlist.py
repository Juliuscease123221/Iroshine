"""
iroshine.barlist — BarList, the main visual object.

A BarList is a *view* bound to a variable name in your solution. Declare one
for every list you want to see (inputs, `stack`, the returned `result`, ...)
and give it whatever look you want. Lists you don't declare are still tracked
(so provenance works) but aren't drawn.
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple

from manim import (
    DOWN, LEFT, RIGHT, UP, BLACK, Circle, DashedLine, Line, ManimColor, MarkupText,
    Rectangle, RoundedRectangle, Text, VGroup, interpolate_color,
)

from .style import Axis, BarStyle, Gradient, Labels, Panel


@dataclass
class BarList:
    name: str
    position: Tuple[float, float] = (0.0, 0.0)      # center of the panel (Manim units, frame ≈ 14.2 × 8)
    size: Tuple[float, float] = (8.0, 2.4)
    orientation: str = "up"                         # "up": vertical bars in a row · "right": horizontal bars stacked bottom→top
    y_range: Tuple[Optional[float], Optional[float]] = (None, None)   # bars grow from y_range[0]; None = auto
    capacity: Optional[int] = None                  # number of slots; None = longest the list ever gets
    bar: BarStyle = field(default_factory=BarStyle)
    labels: Labels = field(default_factory=Labels)
    panel: Optional[Panel] = field(default_factory=Panel)
    axis: Axis = field(default_factory=Axis)
    title: Optional[str] = None                     # text shown instead of the variable name
    indexes: Optional[str] = None                   # this list holds *indices* into another list (e.g. a
    index_labels: bool = False                      # (indexes view) label each bar with the index it holds,
                                                    # not the value it points at
                                                    #   monotonic stack of positions): draw each bar as that
                                                    #   element, and fly it in from there
    padding: float = 0.18

    # ─────────────────────────────────────────── set up by the Stage ──
    def prepare(self, values_seen, max_len):
        nums = [v for v in values_seen if isinstance(v, (int, float))] or [0, 1]
        self.ranked = sorted(set(nums))
        lo, hi = self.y_range
        self.lo = lo if lo is not None else min(0, min(nums))
        self.hi = hi if hi is not None else max(nums)
        if self.hi <= self.lo:
            self.hi = self.lo + 1
        self.cap = self.capacity or max(1, max_len)

        cx, cy = self.position
        w, h = self.size
        p, L, A = self.padding, self.labels, self.axis
        left = L.name_margin if (L.name and L.name_position == "left") else 0
        g = A.ground
        if self.orientation == "up":
            self.a0 = cx - w / 2 + p + left                              # slot axis start/end (x)
            self.a1 = cx + w / 2 - p - (0.5 if A.ticks else 0)
            self.base = cy - h / 2 + p + g + (0.24 if L.indices else 0)  # value axis start/end (y)
            self.top = cy + h / 2 - p - (0.3 if L.values else 0)
        elif self.orientation == "right":
            self.a0 = cy - h / 2 + p                                     # slots run up the panel (y)
            self.a1 = cy + h / 2 - p
            self.base = cx - w / 2 + p + left + g + (0.38 if L.indices else 0)
            self.top = cx + w / 2 - p - (0.62 if L.values else 0)
        else:
            raise ValueError(f"orientation must be 'up' or 'right', not {self.orientation!r}")
        # Band layout, the same model as D3's scaleBand:
        #   step = range / (n - inner + 2·outer),  band = step · (1 - inner)
        B = self.bar
        self.inner = min(0.95, max(0.0, B.gap if B.gap is not None else 1 - B.width))
        self.outer = max(0.0, B.outer_gap if B.outer_gap is not None else self.inner / 2)
        self.slot = (self.a1 - self.a0) / max(1e-9, self.cap - self.inner + 2 * self.outer)
        self.band = self.slot * (1 - self.inner)
        self.start = self.a0 + self.slot * self.outer

    # ─────────────────────────────────────────────────── geometry ──
    def length(self, v):
        t = (v - self.lo) / (self.hi - self.lo) if isinstance(v, (int, float)) else 0
        t = min(1.0, max(0.0, t))
        return max(self.bar.min_length, t * (self.top - self.base))

    def value_pos(self, v):
        """Coordinate along the value axis for value v (no minimum length)."""
        t = min(1.0, max(0.0, (v - self.lo) / (self.hi - self.lo)))
        return self.base + t * (self.top - self.base)

    def slot_center(self, i):
        return self.start + self.slot * i + self.band / 2

    def anchor(self, i):
        """Point where bar i's base sits."""
        s = self.slot_center(i)
        return (s, self.base) if self.orientation == "up" else (self.base, s)

    def slot_offset(self, i, j):
        """Vector that moves something from slot i to slot j."""
        d = (j - i) * self.slot
        return [d, 0, 0] if self.orientation == "up" else [0, d, 0]

    def color_for(self, v, i, origin=None):
        f = self.bar.fill
        if isinstance(f, Gradient):
            n = max(1, self.cap - 1)
            if f.by == "value":
                t = (v - self.lo) / (self.hi - self.lo)
            elif f.by == "rank":
                r = self.ranked.index(v) if v in self.ranked else 0
                t = r / max(1, len(self.ranked) - 1)
            elif f.by == "origin":
                t = (i if origin is None else origin) / n
            else:                                    # "index"
                t = i / n
            return f.at(t)
        if callable(f):
            return ManimColor(f(v, i))
        return ManimColor(f)

    # ─────────────────────────────────────────────────── drawing ──
    def make_bar(self, i, v, color=None, origin=None):
        """A VGroup(body, label) for value v in slot i. body[...] holds the shapes to recolor.

        origin: the slot this element started in (keeps by="origin" colors attached to it).
        """
        B, up = self.bar, self.orientation == "up"
        origin = i if origin is None else origin
        color = ManimColor(color) if color is not None else self.color_for(v, i, origin)
        thick, L = self.band, self.length(v)
        if self.inner == 0 and B.seam > 0:           # touching bars: overlap a hair to hide AA seams
            from manim import config
            thick += B.seam * config.frame_height / config.pixel_height
        ax, ay = self.anchor(i)
        if up:
            cx, cy, W, H = ax, ay + L / 2, thick, L
            tip = (ax, ay + L)
        else:
            cx, cy, W, H = ax + L / 2, ay, L, thick
            tip = (ax + L, ay)

        def shape(scale=1.0):
            if B.shape == "lollipop":
                r = thick * 0.42 * scale
                stem = Rectangle(width=W if not up else thick * 0.16 * scale,
                                 height=H if up else thick * 0.16 * scale).move_to([cx, cy, 0])
                head = Circle(radius=r).move_to([tip[0], tip[1], 0])
                return VGroup(stem, head)
            if B.shape == "pill":
                rad = min(W, H) / 2.05
            else:
                rad = min(B.corner_radius, W / 2.1, H / 2.1)
            w = W * scale if up else W + (scale - 1) * thick
            h = H + (scale - 1) * thick if up else H * scale
            r = Rectangle(width=w, height=h) if rad <= 1e-4 else RoundedRectangle(width=w, height=h, corner_radius=rad)
            return VGroup(r.move_to([cx, cy, 0]))

        body = VGroup()
        if B.glow > 0:
            for k, s in enumerate((1.7, 1.4, 1.15)):
                halo = shape(s)
                halo.set_fill(color, opacity=B.glow * (0.10 + 0.07 * k)).set_stroke(width=0)
                body.add(halo)
        core = shape()
        self._paint(core, color)
        core.set_stroke(ManimColor(B.stroke) if B.stroke else color, width=B.stroke_width if B.stroke else 0)
        body.add(core)

        label = VGroup()
        if self.labels.values:
            label = Text(str(v), font=self.labels.font, font_size=self.labels.font_size,
                         color=ManimColor(self.labels.color))
            label.next_to(core, UP if up else RIGHT, buff=0.08)
        bar = VGroup(body, label)
        bar.value, bar.slot_index, bar.origin, bar.hue = v, i, origin, color
        return bar

    def _paint(self, core, color):
        """Flat fill, or a base-to-tip gradient when BarStyle.shade > 0."""
        B = self.bar
        if B.shade > 0:
            dark = interpolate_color(color, BLACK, B.shade)
            for part in core:
                part.set_fill([dark, color], opacity=B.opacity)
                part.set_sheen_direction(UP if self.orientation == "up" else RIGHT)
        else:
            core.set_fill(color, opacity=B.opacity)

    def paint(self, bar, color):
        """Recolor an existing bar (keeps shading)."""
        self._paint(bar[0][-1], ManimColor(color))
        bar.hue = ManimColor(color)
        return bar

    def build_static(self):
        """Panel, name, baseline or ground, index labels, ticks."""
        g = VGroup()
        cx, cy = self.position
        w, h = self.size
        up = self.orientation == "up"
        if self.panel:
            P = self.panel
            box = (Rectangle(width=w, height=h) if P.corner_radius <= 0
                   else RoundedRectangle(width=w, height=h, corner_radius=P.corner_radius)).move_to([cx, cy, 0])
            if P.fill is None:
                box.set_fill(opacity=0)
            elif isinstance(P.fill, (list, tuple)):
                box.set_fill([ManimColor(c) for c in P.fill], opacity=P.opacity).set_sheen_direction(UP)
            else:
                box.set_fill(ManimColor(P.fill), opacity=P.opacity)
            box.set_stroke(ManimColor(P.stroke) if P.stroke else None, width=P.stroke_width if P.stroke else 0)
            g.add(box)

        A = self.axis
        if A.ground > 0:
            if up:
                slab = Rectangle(width=self.a1 - self.a0 + 0.2, height=A.ground)
                slab.move_to([(self.a0 + self.a1) / 2, self.base - A.ground / 2, 0])
            else:
                slab = Rectangle(width=A.ground, height=self.a1 - self.a0 + 0.2)
                slab.move_to([self.base - A.ground / 2, (self.a0 + self.a1) / 2, 0])
            slab.set_fill(ManimColor(A.ground_color), opacity=1)
            slab.set_stroke(ManimColor(A.ground_stroke) if A.ground_stroke else None,
                            width=2 if A.ground_stroke else 0)
            g.add(slab)
        elif A.baseline:
            a, b = ([self.a0 - 0.1, self.base, 0], [self.a1 + 0.1, self.base, 0]) if up else \
                   ([self.base, self.a0 - 0.1, 0], [self.base, self.a1 + 0.1, 0])
            g.add(Line(a, b, color=ManimColor(A.color), stroke_width=A.width))

        L = self.labels
        if L.name:
            name = (self.title or self.name)
            name = name.upper() if L.uppercase else name
            spacing = 1400 if L.uppercase else 0         # Pango letter spacing (1/1024 pt)
            t = MarkupText(f'<span letter_spacing="{spacing}">{name}</span>', font=L.name_font,
                           weight=L.name_weight, font_size=L.name_size, color=ManimColor(L.color))
            if L.name_position == "left":
                if t.width > L.name_margin - 0.2:
                    t.scale_to_fit_width(L.name_margin - 0.2)
                t.move_to([cx - w / 2 + self.padding + 0.1, cy, 0], aligned_edge=LEFT)
            else:
                t.move_to([cx - w / 2, cy + h / 2, 0], aligned_edge=DOWN + LEFT).shift(0.12 * UP)
            g.add(t)

        for tv in A.ticks:
            d = self.base + self.length(tv)
            a, b = ([self.a0, d, 0], [self.a1, d, 0]) if up else ([d, self.a0, 0], [d, self.a1, 0])
            g.add(DashedLine(a, b, color=ManimColor(A.color), stroke_width=1, dash_length=0.06))
            lab = Text(str(tv), font=L.font, font_size=L.font_size * 0.65, color=ManimColor(L.muted))
            lab.next_to(b, RIGHT if up else UP, buff=0.08)
            g.add(lab)
        if L.indices:
            for i in range(self.cap):
                ax, ay = self.anchor(i)
                t = Text(str(i), font=L.font, font_size=L.font_size * 0.72, color=ManimColor(L.muted))
                t.move_to([ax, ay - A.ground - 0.18, 0] if up else [ax - A.ground - 0.2, ay, 0])
                g.add(t)
        return g
