"""
iroshine.grid — GridView, for 2-D problems (islands, BFS/DFS, flood fill, virus, paths…).

A GridView is bound to a 2-D list in your solution, the same way a BarList is bound
to a 1-D list. Two ideas drive it, and they work together:

  · state mapping:  each cell's color comes from its current value (colors={0: ..., 1: ...}),
                    and cells that are members of a set you name (marks={"seen": Mark(...)})
                    get an overlay. Change the data and the picture follows.
  · knowledge:      cells start "unknown" (dimmed). A cell lights up the moment your code
                    reads it, so the picture shows what the program knows so far.
                    forget_when="seen" makes everything unknown again whenever `seen` is
                    re-created (a new pass over the grid).

Walls(between=(-1, 0)) draws a wall on every edge between a cell whose value is -1 and
a neighbour whose value is 0 (for problems where the answer is a boundary).
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Sequence, Tuple, Union

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Animation, FadeIn, FadeOut, Line, ManimColor, Mobject,
                   Rectangle, RoundedRectangle, Square, UpdateFromAlphaFunc, VGroup, interpolate_color,
                   rate_functions, there_and_back)


@dataclass
class Mark:
    """How members of a named set are drawn on a GridView. Members must be (row, col) pairs."""
    fill: Optional[str] = None
    fill_opacity: float = 0.35
    stroke: Optional[str] = None
    stroke_width: float = 3.0
    shape: str = "cell"               # "cell" (fills the cell) | "ring" (outline) | "dot"
    inset: float = 0.12               # how far inside the cell edge (fraction of a cell)
    keep: bool = False                # when the set is re-created, keep old marks (faded) instead of clearing
    kept_opacity: float = 0.4         # how visible kept marks stay (relative)
    sound: bool = True


@dataclass
class Walls:
    """Draw walls on cell edges between two kinds of values, e.g. between=(-1, 0)."""
    between: Tuple[Any, Any] = (-1, 0)
    color: str = "#ffffff"
    width: float = 6.0
    sticky: bool = True               # once built, a wall stays even if the cells change later
    sound: bool = True


@dataclass
class GridView:
    name: str                                        # the 2-D list in your solution
    position: Tuple[float, float] = (0.0, 0.0)       # center
    size: Tuple[float, float] = (8.0, 6.0)           # the grid is fitted inside this box (square cells)
    colors: Dict[Any, str] = field(default_factory=lambda: {0: "#2b2b2b", 1: "#e8e4dc"})
    default_color: str = "#444444"                   # for values not in `colors`
    gap: float = 0.08                                # space between cells, as a fraction of a cell
    corner_radius: float = 0.0
    stroke: Optional[str] = None
    stroke_width: float = 1.5
    unknown: Optional[float] = 0.8                   # dim cells the program hasn't read yet (0–1); None = off
    unknown_color: str = "#000000"                   # what unknown cells fade toward
    forget_when: Optional[str] = None                # re-creating this set/list makes every cell unknown again
    flash: Optional[str] = "#ffffff"                 # outline that blinks on each read (the "cursor"); None = off
    flash_opacity: float = 0.9
    marks: Dict[str, Mark] = field(default_factory=dict)
    walls: Optional[Walls] = None
    rate: float = 40.0                               # grid events per second (they play as overlapping waves)
    step: float = 0.3                                # length of each cell's little animation (s)
    like: Optional[str] = None                       # a blank canvas the same shape as another GridView
                                                     #   (nothing is bound to it; Stamps draw on it)
    blank_color: str = "#111111"                     # canvas cells' color
    reads: bool = True                               # False: reading a cell shows nothing and takes no time
    set_scale: float = 1.0                           # a cell settles at this size when its value changes (e.g. 0.86:
                                                     #   it shrivels a little); applied once per cell
    set_bounce: bool = False                         # the change overshoots and settles (a little squish)
    final_hold: float = 0.0                          # a held breath (s) before the wave that makes the grid's last change
    final_instrument: Optional[str] = None           # that last change plays this instead (bigger, the peak)
    final_gain: float = 0.0
    sizes: Dict[Any, float] = field(default_factory=dict)   # cells of these values start smaller, e.g. {0: 0.3}
                                                     #   (empty spots recede as small dots)

    # ────────────────────────────────────────────────────────────── setup ──
    def build(self, grid):
        self.R, self.C = len(grid), len(grid[0]) if grid else 0
        w, h = self.size
        self.s = min(w / max(1, self.C), h / max(1, self.R))
        self.x0 = self.position[0] - self.C * self.s / 2
        self.y0 = self.position[1] + self.R * self.s / 2
        self.values = [row[:] for row in grid]
        nums = [v for row in grid for v in row if isinstance(v, (int, float))] or [0, 1]
        self._range = (min(nums), max(nums))
        self.known = [[self.unknown is None] * self.C for _ in range(self.R)]
        self.cells = [[self._cell(r, c) for c in range(self.C)] for r in range(self.R)]
        self.marks_on = {}          # (set, r, c) -> mobject
        self.kept = []              # faded marks from earlier sets
        self.walls_on = {}          # edge key -> line
        self.group = VGroup(*[m for row in self.cells for m in row])
        return self.group

    def center(self, r, c):
        return np.array([self.x0 + (c + 0.5) * self.s, self.y0 - (r + 0.5) * self.s, 0.0])

    def block(self, r0, r1, c0, c1):
        """Rectangle covering cells r0..r1 × c0..c1 (inclusive), edge to edge."""
        pad = self.s * self.gap / 2
        x0 = self.x0 + c0 * self.s + pad
        x1 = self.x0 + (c1 + 1) * self.s - pad
        y0 = self.y0 - r0 * self.s - pad
        y1 = self.y0 - (r1 + 1) * self.s + pad
        return Rectangle(width=x1 - x0, height=y0 - y1).move_to([(x0 + x1) / 2, (y0 + y1) / 2, 0])

    def color_of(self, v):
        """colors can be a dict {value: color}, a list (cycled by value), a Gradient over the
        grid's value range, or a function value -> color."""
        from .gradient import Gradient
        if v is None:
            return ManimColor(self.blank_color if self.like else self.default_color)
        cs = self.colors
        if isinstance(cs, Gradient):
            lo, hi = self._range
            return cs.at((v - lo) / (hi - lo) if hi > lo else 0)
        if isinstance(cs, (list, tuple)):
            return ManimColor(cs[int(v) % len(cs)])
        if callable(cs):
            return ManimColor(cs(v))
        return ManimColor(cs.get(v, self.default_color))

    def shown_color(self, r, c):
        col = self.color_of(self.values[r][c])
        if not self.known[r][c]:
            col = interpolate_color(col, ManimColor(self.unknown_color), self.unknown)
        return col

    def _cell(self, r, c):
        side = self.s * (1 - self.gap)
        m = (Square(side_length=side) if self.corner_radius <= 0
             else RoundedRectangle(width=side, height=side, corner_radius=self.corner_radius * side))
        m.move_to(self.center(r, c))
        k = self.sizes.get(self.values[r][c], 1.0) if self.sizes else 1.0
        if k != 1.0:
            m.scale(k)
        m.set_fill(self.shown_color(r, c), opacity=1)
        m.set_stroke(ManimColor(self.stroke) if self.stroke else None, width=self.stroke_width if self.stroke else 0)
        return m

    # ───────────────────────────────────────────────────── event routing ──
    def handles(self, e):
        if self.like:
            return False
        t = e["type"]
        if t in ("read", "set") and e.get("list") == self.name and "row" in e:
            return t == "set" or self.reads
        if t in ("sadd", "sremove", "sclear", "screate") and e.get("set") in self.marks:
            return True
        return False

    def forgets(self, e):
        return self.forget_when and e["type"] in ("screate", "create") and \
            (e.get("set") or e.get("list")) == self.forget_when

    def key(self, e):
        t = e["type"]
        if t in ("read", "set"):
            return ("cell", self.name, e["row"], e["index"])
        if t in ("sadd", "sremove"):
            r, c = e["value"][:2]
            return ("mark", e["set"], r, c)
        return ("markset", e["set"])

    # ───────────────────────────────────────────────────── animations ──
    def recolor(self, r, c, rate):
        cell, target = self.cells[r][c], self.shown_color(r, c)
        return cell.animate(rate_func=rate).set_fill(target)

    def anim(self, scene, e):
        """One little animation for event e (or None). Also returns notes to play: [(kind, value)]."""
        t, rate = e["type"], rate_functions.ease_out_cubic
        notes = []
        if t == "read":
            r, c = e["row"], e["index"]
            parts = []
            if not self.known[r][c]:
                self.known[r][c] = True
                parts.append(self.recolor(r, c, rate))
                if self.values[r][c] not in (0, None):
                    notes.append(("reveal", self.values[r][c]))
            if self.flash:
                f = Square(side_length=self.s * (1 - self.gap)).move_to(self.center(r, c))
                f.set_fill(opacity=0).set_stroke(ManimColor(self.flash), width=3, opacity=0)
                scene.add(f)                          # invisible until its turn in the wave
                parts.append(f.animate(rate_func=there_and_back).set_stroke(opacity=self.flash_opacity))
                scene._grid_trash.append(f)
            return parts, notes
        if t == "set":
            r, c, v = e["row"], e["index"], e["value"]
            old = self.values[r][c]
            self.values[r][c] = v
            self.known[r][c] = True
            if self.set_scale != 1.0 or self.set_bounce:
                cell = self.cells[r][c]
                shrunk = getattr(self, "_shrunk", set())
                self._shrunk = shrunk
                k = 1.0 if (r, c) in shrunk else self.set_scale
                shrunk.add((r, c))
                parts = [cell.animate(rate_func=rate_functions.ease_out_back if self.set_bounce else rate)
                         .set_fill(self.shown_color(r, c)).scale(k)]
            else:
                parts = [self.recolor(r, c, rate)]
            if old != v:
                notes.append(("set", v))
            if self.walls:
                parts += self._walls_around(scene, r, c, notes)
            return parts, notes
        if t == "sadd":
            r, c = e["value"][:2]
            mk = self.marks[e["set"]]
            m = self._mark(mk, r, c)
            old = self.marks_on.pop((e["set"], r, c), None)
            if old is not None:
                scene.remove(old)
            self.marks_on[(e["set"], r, c)] = m
            if mk.sound:
                notes.append(("mark", e["set"]))
            return [FadeIn(m, rate_func=rate)], notes
        if t == "sremove":
            r, c = e["value"][:2]
            m = self.marks_on.pop((e["set"], r, c), None)
            return ([FadeOut(m)] if m is not None else []), notes
        if t in ("sclear", "screate"):
            name = e["set"]
            mine = [(k, m) for k, m in self.marks_on.items() if k[0] == name]
            parts = []
            for k, m in mine:
                del self.marks_on[k]
                if self.marks[name].keep:
                    self.kept.append(m)
                    parts.append(m.animate.set_opacity(self.marks[name].kept_opacity *
                                                       self.marks[name].fill_opacity))
                else:
                    parts.append(FadeOut(m))
            return ([_Group(parts)] if parts else []), notes
        return [], notes

    def forget(self, scene):
        """Everything becomes unknown again; all marks are cleared (walls stay)."""
        for r in range(self.R):
            for c in range(self.C):
                self.known[r][c] = self.unknown is None
        parts = [self.cells[r][c].animate.set_fill(self.shown_color(r, c))
                 for r in range(self.R) for c in range(self.C)]
        old = list(self.marks_on.values()) + self.kept
        self.marks_on, self.kept = {}, []
        parts += [FadeOut(m) for m in old]
        return parts

    def _mark(self, mk, r, c):
        side = self.s * (1 - self.gap) * (1 - 2 * mk.inset)
        if mk.shape == "dot":
            from manim import Circle
            m = Circle(radius=side * 0.22)
        else:
            m = Square(side_length=side)
        m.move_to(self.center(r, c))
        if mk.shape == "ring":
            m.set_fill(opacity=0)
        else:
            m.set_fill(ManimColor(mk.fill or "#ffffff"), opacity=mk.fill_opacity if mk.shape == "cell" else 1)
        m.set_stroke(ManimColor(mk.stroke) if mk.stroke else None, width=mk.stroke_width if mk.stroke else 0)
        return m

    def _walls_around(self, scene, r, c, notes):
        a, b = self.walls.between
        out = []
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if not (0 <= nr < self.R and 0 <= nc < self.C):
                continue
            pair = (self.values[r][c], self.values[nr][nc])
            if pair not in ((a, b), (b, a)):
                continue
            k = tuple(sorted(((r, c), (nr, nc))))
            if k in self.walls_on:
                continue
            mid = (self.center(r, c) + self.center(nr, nc)) / 2
            half = self.s / 2
            if dr:                                   # neighbours above/below → horizontal wall
                p, q = mid + LEFT * half, mid + RIGHT * half
            else:
                p, q = mid + UP * half, mid + DOWN * half
            ln = Line(p, q, color=ManimColor(self.walls.color), stroke_width=self.walls.width)
            self.walls_on[k] = ln
            from manim import Create
            scene.add(ln)
            out.append(Create(ln, rate_func=rate_functions.ease_out_cubic))
            if self.walls.sound:
                notes.append(("wall", len(self.walls_on)))
        return out


class _Group(Animation):
    """Several animations started together that count as one item in a wave."""

    def __new__(cls, parts):
        from manim import AnimationGroup
        return AnimationGroup(*parts)



# ════════════════════════════════════════════════════════ boxes & stamps ══
@dataclass
class GridBoxes:
    """One outline per id, from four parallel arrays of bounds, e.g. top[c], bottom[c], left[c], right[c].

    Every time your code writes one of those arrays, the box for that index is redrawn,
    so you can watch bounding boxes grow as the scan discovers them. An id's box shows
    once it is valid (top <= bottom and left <= right).
    """
    on: str                                           # the GridView the boxes sit on
    top: str = "top"
    bottom: str = "bottom"
    left: str = "left"
    right: str = "right"
    color: Optional[str] = None                       # None = the grid's color for that id
    stroke_width: float = 3.5
    opacity: float = 0.95
    brighten: float = 0.25                            # lift the grid color a little so the outline reads

    def lists(self):
        return (self.top, self.bottom, self.left, self.right)

    def handles(self, e):
        return e["type"] == "set" and e.get("list") in self.lists() and "row" not in e

    def key(self, e):
        return ("box", self.on, e["index"])

    def anim(self, scene, e):
        g = scene.S.grids.get(self.on)
        k = e["index"]
        M = scene.mirror
        try:
            r0, r1 = M[self.top][k], M[self.bottom][k]
            c0, c1 = M[self.left][k], M[self.right][k]
        except (KeyError, IndexError, TypeError):
            return [], []
        if g is None or not (0 <= r0 <= r1 < g.R and 0 <= c0 <= c1 < g.C):
            return [], []
        boxes = scene.__dict__.setdefault("_boxes", {})
        cur = (r0, r1, c0, c1)
        old = boxes.get((self.on, k))
        if old is not None and old[0] == cur:
            return [], []
        col = ManimColor(self.color) if self.color else interpolate_color(g.color_of(k), ManimColor("#ffffff"),
                                                                          self.brighten)
        new = g.block(r0, r1, c0, c1).set_fill(opacity=0).set_stroke(col, width=self.stroke_width,
                                                                     opacity=self.opacity)
        if old is None:
            from manim import Create
            scene.add(new)
            boxes[(self.on, k)] = (cur, new)
            return [Create(new, rate_func=rate_functions.ease_out_cubic)], [("box", k)]
        mob = old[1]
        boxes[(self.on, k)] = (cur, mob)
        return [mob.animate(rate_func=rate_functions.ease_out_cubic).become(new)], []


@dataclass
class Stamp:
    """Print a solid block onto a GridView (usually a blank `like=` canvas) whenever a variable changes.

        Stamp(on="printer", when="layer",
              rows=("top[layer]", "bottom[layer]"), cols=("left[layer]", "right[layer]"),
              value="layer")                 # the color comes from the grid's colors for this value

    Expressions are evaluated against your solution's local variables at that moment.
    """
    on: str
    when: str
    rows: Tuple[str, str]
    cols: Tuple[str, str]
    value: Optional[str] = None                       # expression whose grid color fills the block
    fill: Optional[str] = None                        # or a fixed color
    opacity: float = 1.0
    stroke: Optional[str] = None
    stroke_width: float = 2.0
    duration: float = 0.7
    press: float = 1.06                               # starts this much bigger, then settles (a stamp "press")

    def build(self, grid, env):
        ev = lambda expr: _safe_eval(expr, env)
        try:
            r0, r1 = int(ev(self.rows[0])), int(ev(self.rows[1]))
            c0, c1 = int(ev(self.cols[0])), int(ev(self.cols[1]))
            val = ev(self.value) if self.value else None
        except Exception:
            return None
        if not (r0 <= r1 and c0 <= c1):
            return None
        rect = grid.block(r0, r1, c0, c1)
        col = ManimColor(self.fill) if self.fill else grid.color_of(val)
        rect.set_fill(col, opacity=self.opacity)
        rect.set_stroke(ManimColor(self.stroke) if self.stroke else None,
                        width=self.stroke_width if self.stroke else 0)
        rect.value = val
        return rect


def _safe_eval(expr, env):
    if callable(expr):
        return expr(env)
    safe = {"__builtins__": {}, "min": min, "max": max, "abs": abs, "len": len, "sum": sum}
    return eval(expr, safe, dict(env))
