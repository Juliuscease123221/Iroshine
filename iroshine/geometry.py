"""
iroshine.geometry — PointSet and Polyline, for problems about points in the plane
(convex hull, closest pair, line sweeps, polygons…).

PointSet("trees")          binds to a list of [x, y] pairs and draws them as dots.
                           Sorting the list recolors the dots by their new order, so you can
                           see the sweep order. `focus="p"` rings whichever point `p` is.
Polyline("hull", on=...)   binds to a list used as a stack of points and draws it as a path:
                           append grows a new segment, pop pulls the last one back. `probe="p"`
                           draws a dashed feeler from the path's end to the candidate point `p`.
                           On finish, the path closes and fills.
"""

from dataclasses import dataclass
from typing import Any, Optional, Tuple

import numpy as np
from manim import (Circle, Create, DashedLine, Dot, FadeIn, FadeOut, LaggedStart, Line, ManimColor,
                   Polygon, VGroup, rate_functions, there_and_back)


def _pt(v):
    return (float(v[0]), float(v[1]))


@dataclass
class PointSet:
    name: str
    position: Tuple[float, float] = (0.0, 0.0)
    size: Tuple[float, float] = (10.0, 6.0)
    x_range: Optional[Tuple[float, float]] = None     # None = fit the data
    y_range: Optional[Tuple[float, float]] = None
    margin: float = 0.06
    radius: float = 0.09
    fill: Any = "#ffffff"                              # a color, or a Gradient (by the list's current order)
    stroke: Optional[str] = None
    stroke_width: float = 1.5
    focus: Optional[str] = None                        # variable holding the current point
    focus_color: str = "#ffffff"
    flash_reads: bool = False
    grid: bool = False                                 # faint dotted graph lines behind the points
    grid_step: float = 1.0                             # in data units
    grid_color: str = "#000000"
    grid_opacity: float = 0.12
    grid_major: int = 0                                # every Nth line a bit stronger (0 = all the same)
    grid_width: float = 1.2

    # ---------------------------------------------------------------- setup
    def build(self, values):
        pts = [_pt(v) for v in values]
        xs, ys = [p[0] for p in pts] or [0, 1], [p[1] for p in pts] or [0, 1]
        self.xr = self.x_range or (min(xs), max(xs))
        self.yr = self.y_range or (min(ys), max(ys))
        w, h = self.size
        spanx = (self.xr[1] - self.xr[0]) or 1
        spany = (self.yr[1] - self.yr[0]) or 1
        self.k = min(w * (1 - 2 * self.margin) / spanx, h * (1 - 2 * self.margin) / spany)   # equal aspect
        self.order = list(pts)
        self.initial = list(pts)
        self.dots = {}
        g = VGroup()
        for i, p in enumerate(pts):
            d = Dot(self.to_scene(p), radius=self.radius)
            self._style(d, i)
            self.dots[p] = d
            g.add(d)
        self.grid_mob = self._grid() if self.grid else None
        self.ring = Circle(radius=self.radius * 2.2).set_fill(opacity=0) \
            .set_stroke(ManimColor(self.focus_color), width=2.5, opacity=0)
        self.ring_on = False
        return g

    def _grid(self):
        """Dotted lines at every grid_step, filling the plot box."""
        import math
        cx, cy = self.position
        w, h = self.size
        mx, my = (self.xr[0] + self.xr[1]) / 2, (self.yr[0] + self.yr[1]) / 2
        x0, x1 = mx - w / 2 / self.k, mx + w / 2 / self.k        # the box, in data units
        y0, y1 = my - h / 2 / self.k, my + h / 2 / self.k
        st = self.grid_step
        g = VGroup()

        def line(a, b, major):
            op = min(1.0, self.grid_opacity * (2.0 if major else 1.0))
            d = DashedLine(a, b, dash_length=0.012, dashed_ratio=0.45, stroke_width=self.grid_width,
                           color=ManimColor(self.grid_color))
            d.set_stroke(opacity=op)
            g.add(d)
        for i in range(math.ceil(x0 / st), math.floor(x1 / st) + 1):
            x = i * st
            line(self.to_scene((x, y0)), self.to_scene((x, y1)), self.grid_major and i % self.grid_major == 0)
        for j in range(math.ceil(y0 / st), math.floor(y1 / st) + 1):
            y = j * st
            line(self.to_scene((x0, y)), self.to_scene((x1, y)), self.grid_major and j % self.grid_major == 0)
        return g

    def to_scene(self, p):
        cx, cy = self.position
        mx, my = (self.xr[0] + self.xr[1]) / 2, (self.yr[0] + self.yr[1]) / 2
        return np.array([cx + (p[0] - mx) * self.k, cy + (p[1] - my) * self.k, 0.0])

    def color(self, i):
        from .gradient import Gradient
        if isinstance(self.fill, Gradient):
            return self.fill.at(i / max(1, len(self.order) - 1))
        return ManimColor(self.fill)

    def _style(self, d, i):
        d.set_fill(self.color(i), opacity=1)
        d.set_stroke(ManimColor(self.stroke) if self.stroke else None,
                     width=self.stroke_width if self.stroke else 0)

    # --------------------------------------------------------------- events
    def handle(self, scene, e):
        t = e["type"]
        if t == "replace":                                   # e.g. trees.sort(): recolor in the new order
            self.order = [_pt(v) for v in e["values"]]
            anims = [self.dots[p].animate.set_fill(self.color(i)) for i, p in enumerate(self.order)
                     if p in self.dots]
            for i, p in enumerate(self.order):
                scene.note(deg=2 + i % 12, instrument=scene.S.sound_cfg.soft_instrument, offset=i * 0.05, gain=-14)
            if anims:
                scene.play(LaggedStart(*anims, lag_ratio=0.12), run_time=1.6 / scene.S.timing.speed)
        elif t == "read" and self.flash_reads:
            p = _pt(e["value"]) if isinstance(e.get("value"), (list, tuple)) else None
            if p in self.dots:
                scene.play(self.dots[p].animate(rate_func=there_and_back).scale(1.6),
                           run_time=0.2 / scene.S.timing.speed)

    def restore(self):
        """Animations back to the opening state: original colors, no focus ring (for loops)."""
        self.order = list(self.initial)
        anims = [self.dots[p].animate.set_fill(self.color(i)) for i, p in enumerate(self.initial)]
        if self.ring_on:
            anims.append(self.ring.animate.set_stroke(opacity=0))
            self.ring_on = False
        return anims

    def focus_on(self, value):
        """Animation that moves the focus ring to point `value`."""
        p = _pt(value)
        if p not in self.dots:
            return []
        target = self.to_scene(p)
        if not self.ring_on:
            self.ring.move_to(target)
            self.ring_on = True
            return [self.ring.animate.set_stroke(opacity=0.9)]
        return [self.ring.animate(rate_func=rate_functions.ease_in_out_cubic).move_to(target)]


@dataclass
class Polyline:
    name: str                                          # a list of points used as a stack (append / pop)
    on: str                                            # the PointSet whose coordinates it uses
    color: str = "#ffffff"
    width: float = 5.0
    vertex_radius: float = 0.12
    vertex_color: Optional[str] = None                 # None = the line color
    probe: Optional[str] = None                        # variable holding the candidate point
    probe_color: str = "#ffffff"
    probe_opacity: float = 0.55
    fill: Optional[str] = None                         # fill the closed shape at the end
    fill_opacity: float = 0.35
    buildup: bool = True                               # the closing sweep over the posts plays a rising run of notes
    push_time: float = 0.45
    pop_time: float = 0.35
    ghost: bool = False                                # show the final shape faintly from the start (the promise)
    ghost_opacity: float = 0.3
    ghost_dash: float = 0.07
    loop: bool = False                                 # at the very end, return to the opening frame

    def setup(self, scene):
        self.ps = next(p for p in scene.S.pointsets if p.name == self.on)
        self.vertices, self.segments, self.posts = [], [], []
        self.feeler = None
        self.poly = None
        self.ghost_mob = None
        if self.ghost:
            stack = []                                 # replay the pushes and pops to find the final path
            for e in scene.S.events:
                if e.get("list") != self.name:
                    continue
                if e["type"] == "push":
                    stack.append(_pt(e["value"]))
                elif e["type"] == "pop" and stack:
                    stack.pop()
            self._final = stack

    def show_ghost(self, scene):
        """Draw the faint dashed final shape (called once the points exist)."""
        if not self.ghost:
            return
        pts = []
        for p in self._final:
            if not pts or pts[-1] != p:
                pts.append(p)
        if len(pts) > 1 and pts[0] == pts[-1]:
            pts = pts[:-1]
        if len(pts) < 2:
            return
        from manim import DashedVMobject
        shape = Polygon(*[self.ps.to_scene(p) for p in pts]).set_fill(opacity=0) \
            .set_stroke(ManimColor(self.color), width=self.width * 0.55, opacity=self.ghost_opacity)
        self.ghost_mob = DashedVMobject(shape, num_dashes=max(12, int(shape.get_arc_length() / self.ghost_dash / 2)),
                                        dashed_ratio=0.5)
        scene.add(self.ghost_mob)
        scene.bring_to_back(self.ghost_mob)
        for m in scene.S._backdrop:
            scene.bring_to_back(m)

    def handle(self, scene, e):
        t, sp = e["type"], scene.S.timing.speed
        if t in ("create", "replace"):
            return
        if t == "push":
            p = _pt(e["value"])
            a = self.ps.to_scene(p)
            post = Dot(a, radius=self.vertex_radius).set_fill(ManimColor(self.vertex_color or self.color), opacity=1)
            anims = [FadeIn(post, scale=0.3, rate_func=rate_functions.ease_out_back)]
            seg = None
            if self.vertices:
                b = self.ps.to_scene(self.vertices[-1])
                seg = Line(b, a, color=ManimColor(self.color), stroke_width=self.width)
                scene.add(seg)
                anims.insert(0, Create(seg, rate_func=rate_functions.ease_in_out_cubic))
            anims += self._feeler_off()
            self.vertices.append(p); self.segments.append(seg); self.posts.append(post)
            scene.note(deg=2 + len(self.vertices) % 12, gain=-4)
            scene.play(*anims, run_time=self.push_time / sp)
            scene.bring_to_front(*[x for x in self.posts])
        elif t == "pop" and self.vertices:
            self.vertices.pop()
            seg, post = self.segments.pop(), self.posts.pop()
            anims = [FadeOut(post, scale=0.3)]
            if seg is not None:
                anims.append(seg.animate(rate_func=rate_functions.ease_in_cubic)
                             .put_start_and_end_on(seg.get_start(), seg.get_start() + 1e-4 * (seg.get_end() - seg.get_start())))
            scene.note(deg=len(self.vertices) % 12, instrument=scene.S.sound_cfg.soft_instrument, gain=-6)
            scene.play(*anims, run_time=self.pop_time / sp)
            if seg is not None:
                scene.remove(seg)

    def _feeler_off(self):
        if self.feeler is None:
            return []
        f, self.feeler = self.feeler, None
        return [FadeOut(f)]

    def probe_to(self, scene, value):
        """Dashed feeler from the end of the path to the candidate point."""
        if not self.vertices:
            return []
        a = self.ps.to_scene(self.vertices[-1])
        b = self.ps.to_scene(_pt(value))
        if np.linalg.norm(b - a) < 1e-6:
            return self._feeler_off()
        new = DashedLine(a, b, dash_length=0.08, color=ManimColor(self.probe_color),
                         stroke_width=self.width * 0.45).set_opacity(self.probe_opacity)
        if self.feeler is None:
            self.feeler = new
            return [Create(new, rate_func=rate_functions.ease_out_cubic)]
        old = self.feeler
        return [old.animate(rate_func=rate_functions.ease_in_out_cubic).become(new)]

    def finish(self, scene):
        anims = self._feeler_off()
        pts = []
        for p in self.vertices:
            if not pts or pts[-1] != p:
                pts.append(p)
        if len(pts) > 1 and pts[0] == pts[-1]:
            pts = pts[:-1]
        if self.fill and len(pts) >= 3:
            poly = Polygon(*[self.ps.to_scene(p) for p in pts]).set_fill(ManimColor(self.fill), opacity=self.fill_opacity)
            poly.set_stroke(width=0)
            self.poly = poly
            scene.add(poly)
            scene.bring_to_back(poly)
            for m in scene.S._backdrop:
                scene.bring_to_back(m)
            anims.append(FadeIn(poly))
        lag = 0.12
        anims.append(LaggedStart(*[post.animate(rate_func=there_and_back).scale(1.7) for post in self.posts],
                                 lag_ratio=lag))
        n = len(self.posts)
        if self.buildup and n and scene.synth:
            # the stage plays the closing over 1.6 s; each post's pulse starts k·lag·d in, and peaks halfway
            T = 1.6 / scene.S.timing.speed
            d = T / (1 + lag * (n - 1))
            top = 2 * len(scene.synth.steps)
            cfg = scene.S.sound_cfg
            for k in range(n):
                f = k / max(1, n - 1)                  # 0 → 1 around the fence
                scene.note(deg=round(2 + f * (top - 3)), instrument=cfg.instrument,
                           offset=k * lag * d + d / 2, gain=-14 + 10 * f)       # rising, and getting louder
        return anims

    def unwind(self, scene):
        """Animations back to the opening frame: the path lifts away, leaving only the ghost."""
        if not self.loop:
            return []
        anims = self._feeler_off()
        anims += [FadeOut(m) for m in self.segments + self.posts if m is not None]
        if self.poly is not None:
            anims.append(FadeOut(self.poly))
        anims += self.ps.restore()
        self.vertices, self.segments, self.posts, self.poly = [], [], [], None
        return anims


@dataclass
class PointStrip:
    """A list of points shown as a row of chips (each tinted like its dot), that changes live.

        PointStrip("trees", on="trees", cursor="p")    # the input: reorders when sorted; a ring follows p
        PointStrip("hull",  on="trees", stack=True)    # a stack: pushed chips fly in from `source`, pops lift away

    Chips wrap onto new rows every `per_row`. Pairs with a PointSet (for colors) and plays alongside
    the fence animation rather than after it.
    """
    name: str                                          # the list in your solution
    on: str                                            # the PointSet whose dots give the chips their colors
    position: Tuple[float, float] = (0.0, -1.0)        # top-left corner of the strip
    width: float = 3.4
    per_row: int = 7
    chip_height: float = 0.21
    gap: float = 0.06
    row_gap: float = 0.07
    label: Optional[str] = None                        # small caption above the chips
    label_color: str = "#6f7a6c"
    label_size: float = 8
    label_spacing: int = 1400                          # tracking for the all-caps caption
    ink: str = "#2f352e"                               # coordinate text
    font: str = "IBM Plex Mono"
    border: Optional[str] = None                       # chip outline (e.g. the fence color for the stack)
    border_width: float = 2.0
    cursor: Optional[str] = None                       # variable holding the current point: a ring follows it
    cursor_color: str = "#2f352e"
    source: Optional[str] = None                       # the strip pushed points fly in from
    stack: bool = False
    loop: bool = False                                 # at the very end, return to the opening state

    # ------------------------------------------------------------ layout
    def slot(self, i):
        w = (self.width - self.gap * (self.per_row - 1)) / self.per_row
        r, c = divmod(i, self.per_row)
        x0, y0 = self.position
        top = y0 - (0.22 if self.label else 0.0)
        return np.array([x0 + c * (w + self.gap) + w / 2, top - r * (self.chip_height + self.row_gap)
                         - self.chip_height / 2, 0.0]), w

    def _chip(self, p, i, color):
        from manim import RoundedRectangle, Text
        c, w = self.slot(i)
        box = RoundedRectangle(width=w, height=self.chip_height, corner_radius=min(0.05, self.chip_height / 3))
        box.set_fill(color, opacity=1)
        box.set_stroke(ManimColor(self.border) if self.border else None, width=self.border_width if self.border else 0)
        t = Text(f"{p[0]:g},{p[1]:g}", font=self.font, color=ManimColor(self.ink))
        t.scale(self._text_scale(w))
        t.move_to(box)
        g = VGroup(box, t).move_to(c)
        g.point = p
        return g

    def _text_scale(self, w):
        if not hasattr(self, "_ts"):
            from manim import Text
            probe = Text("30,14", font=self.font)     # the widest label decides one type size for all chips
            self._ts = min(w * 0.78 / probe.width, self.chip_height * 0.52 / probe.height)
        return self._ts

    def _move(self, c, i, color, arc=0.0):
        """One animation that slides chip c to slot i and retints it (two separate ones would fight)."""
        from manim import MoveToTarget
        c.generate_target()
        c.target.move_to(self.slot(i)[0])
        c.target[0].set_fill(color)
        return MoveToTarget(c, path_arc=arc, rate_func=rate_functions.ease_in_out_cubic)

    def _color(self, p):
        d = self.ps.dots.get(_pt(p))
        return d.get_fill_color() if d is not None else ManimColor("#ffffff")

    # ------------------------------------------------------------ story hooks (an observer)
    def setup(self, scene):
        self.ps = next(p for p in scene.S.pointsets if p.name == self.on)
        self.src = next((o for o in scene.S.observers if isinstance(o, PointStrip) and o.name == self.source), None)
        first = next((e for e in scene.S.events if e.get("list") == self.name and e["type"] == "create"), None)
        self.initial = [_pt(v) for v in (first["values"] if first else [])]
        self.chips = []
        self.ring = None

    def start(self, scene, instant):
        from manim import Text
        mobs = []
        if self.label:
            from manim import MarkupText
            cap = MarkupText(f'<span letter_spacing="{self.label_spacing}">{self.label}</span>', font=self.font,
                             font_size=self.label_size, color=ManimColor(self.label_color))
            cap.move_to([self.position[0], self.position[1] - 0.06, 0], aligned_edge=[-1, 0, 0])
            mobs.append(cap)
        self.chips = [self._chip(p, i, self._color(p)) for i, p in enumerate(self.initial)]
        mobs += self.chips
        scene.add(*mobs)

    def _queue(self, scene, *anims):
        scene._companions = getattr(scene, "_companions", []) + list(anims)

    def observe(self, scene, e):
        t = e["type"]
        if e.get("list") == self.name:
            if t == "replace":                       # e.g. sorted: chips slide to their new places
                order = [_pt(v) for v in e["values"]]
                by = {c.point: c for c in self.chips}
                n = max(1, len(order) - 1)
                anims = []
                for i, p in enumerate(order):
                    c = by.get(p)
                    if c is None:
                        continue
                    anims.append(self._move(c, i, self.ps.color(i), arc=0.6 if i % 2 else -0.6))
                self.chips = [by[p] for p in order if p in by]
                self._queue(scene, *anims)
            elif t == "push":
                p = _pt(e["value"])
                chip = self._chip(p, len(self.chips), self._color(p))
                self.chips.append(chip)
                origin = next((c for c in (self.src.chips if self.src else []) if c.point == p), None)
                if origin is not None:
                    mover = origin.copy()
                    scene.add(mover)
                    self._queue(scene, ReplacementTransformLite(mover, chip))
                else:
                    self._queue(scene, FadeIn(chip, scale=0.6, rate_func=rate_functions.ease_out_back))
            elif t == "pop" and self.chips:
                chip = self.chips.pop()
                self._queue(scene, FadeOut(chip, shift=0.12 * np.array([0, 1, 0]), scale=0.8))
        elif t == "var" and e["name"] == self.cursor and isinstance(e.get("value"), (list, tuple)):
            p = _pt(e["value"])
            c = next((c for c in self.chips if c.point == p), None)
            if c is None:
                return
            from manim import RoundedRectangle
            target = RoundedRectangle(width=c.width + 0.07, height=c.height + 0.07, corner_radius=0.07) \
                .move_to(c).set_fill(opacity=0).set_stroke(ManimColor(self.cursor_color), width=2.5)
            if self.ring is None:
                self.ring = target.set_stroke(opacity=0)
                scene.add(self.ring)
                self._queue(scene, self.ring.animate.set_stroke(opacity=1))
            else:
                self._queue(scene, self.ring.animate(rate_func=rate_functions.ease_in_out_cubic).move_to(c))

    def end(self, scene):
        if self.ring is not None:
            self._queue(scene, self.ring.animate.set_stroke(opacity=0))
        if self.stack and self.chips:                 # pulse along with the fence posts' closing sweep
            self._queue(scene, LaggedStart(*[c.animate(rate_func=there_and_back).scale(1.18) for c in self.chips],
                                           lag_ratio=0.12))

    def unwind(self, scene):
        if not self.loop:
            return []
        anims = []
        if self.stack:
            anims += [FadeOut(c) for c in self.chips]
            self.chips = []
        else:
            by = {c.point: c for c in self.chips}
            for i, p in enumerate(self.initial):
                c = by.get(p)
                if c is not None:
                    anims.append(self._move(c, i, self.ps.color(i)))
            self.chips = [by[p] for p in self.initial if p in by]
        return anims


def ReplacementTransformLite(a, b):
    from manim import ReplacementTransform
    return ReplacementTransform(a, b, path_arc=-0.5, rate_func=rate_functions.ease_in_out_cubic)
