"""
iroshine.crossing — WallToWall, for "can you still get across?" problems (LeetCode 1970 and friends).

The trick in these problems is a change of view: instead of asking whether a walker can still get
from the top to the bottom, watch the water. The walk is blocked exactly when the water forms an
unbroken chain from the left wall to the right wall (touching diagonally counts).

WallToWall draws that idea:
  · land cells flood one by one as your code adds them to a set (e.g. `water.add((r, c))`)
  · water that touches the left wall takes the left colour, water touching the right wall the right
    colour, and when a pool touches both, the chain lights up wall to wall
  · (optional) a walker's path from top to bottom, which dodges the water until it can't
  · sound: each drop is pitched by how close the two walls' water is to meeting, so the video gets
    higher as it gets tenser; a pool reaching a wall knocks; the walker rerouting ticks; the final drop
    is held for a beat, then the chain is traced left to right with a rising run into the chord

It keeps its own copy of the pools (a small union-find), so the picture never depends on how your
solution stores them.
"""

from collections import deque
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
from manim import (Circle, Create, FadeIn, FadeOut, Line, ManimColor, RoundedRectangle, VGroup, VMobject,
                   rate_functions, there_and_back)


@dataclass
class WallToWall:
    rows: int
    cols: int
    set: str = "water"                       # the set your code adds flooded cells to
    cells: str = "cells"                     # the input list of cells (the flood order)
    one_indexed: bool = True                 # LeetCode 1970 numbers rows and columns from 1
    position: Tuple[float, float] = (0.0, 0.0)
    size: Tuple[float, float] = (4.0, 3.0)
    gap: float = 0.1                         # space between cells (fraction of a cell)
    corner: float = 0.18                     # cell corner radius (fraction of a cell)
    land: str = "#6b5f47"
    land_top: str = "#7c6f55"                # a lighter lip on each land tile (reads as raised ground)
    tile_lips: bool = True                   # False: flat tiles (less texture, calmer)
    water: str = "#2b4462"                   # a pool touching neither wall
    left: str = "#2fa7a0"                    # pools connected to the left wall
    right: str = "#4f7be0"                   # pools connected to the right wall
    chain: str = "#e9f6ff"                   # the wall-to-wall chain
    joined: str = "#3f8fc2"                  # the pool that finally touches both walls (the chain runs through it)
    wall_width: float = 0.07
    walker: bool = True                      # draw a top-to-bottom path through the land
    walker_color: str = "#f3e3b5"
    walker_dot: bool = True                  # a little walker travelling the route, top to bottom
    walker_dot_color: Optional[str] = None   # (None: walker_color)
    walker_period: Optional[float] = 2.6     # seconds for one trip down · None: the walker stands at the
                                             #   start of the route and only moves when the route changes
    chain_edge: Optional[str] = None         # a dark rim under the chain (reads like a crack in the ground)
    day_time: float = 0.22                   # seconds per flooded cell (early days a little quicker, the
                                             #   days when the two sides are about to meet a little slower)
    event_time: float = 0.34                 # …when a pool merges, reaches a wall, or the walker reroutes
    final_hold: float = 0.5                  # a held breath before the drop that closes the chain
    claim_walls: bool = False                # a wall stays lit once water reaches it (instead of a flash)
    claimed: Optional[str] = None            # its lit colour (None: the side's colour)
    pacing: str = "flat"                     # "importance": plain drops are quick; a pool reaching a wall or the
                                             #   route being cut get about a second each (one change at a time)
    plain_time: float = 0.26
    merge_time: float = 0.4
    wall_time: float = 0.9
    cut_time: float = 0.35                   # (importance) the route is cut…
    redraw_time: float = 0.75                # …then the new route draws in
    code_follow: str = "all"                 # "key": the code highlight only moves on the moments that matter
    # sound
    drop: str = "drip"
    drop_gain: float = -6.0
    merge: Optional[str] = "plop"
    merge_gain: float = -12.0
    wall: Optional[str] = "wood_soft"
    wall_gain: float = -9.0
    reroute: Optional[str] = "wood_soft"
    reroute_gain: float = -16.0
    final: str = "sploosh_mid"
    final_gain: float = -3.0
    run_instrument: str = "wood"
    humanize: float = 1.0

    # ───────────────────────────────────────────────────────── setup ──
    def wants(self, e):
        return e["type"] == "sadd" and e.get("set") == self.set

    def watch(self):
        return []

    def intro(self, scene, e):
        if e.get("list") != self.cells or e["type"] != "create" or e.get("role") != "input":
            return []
        R, C = self.rows, self.cols
        w, h = self.size
        self.s = min(w / C, h / R)
        self.x0 = self.position[0] - C * self.s / 2
        self.y0 = self.position[1] + R * self.s / 2
        self.water_set, self.par, self.side = set(), {}, {}
        self.order = [self._rc(v) for v in e["values"]]
        self.done = False
        self._rng = np.random.default_rng(5)
        side = self.s * (1 - self.gap)
        self.tiles, self.lips = {}, {}
        grp = VGroup()
        for r in range(R):
            for c in range(C):
                t = RoundedRectangle(width=side, height=side, corner_radius=self.corner * side)
                t.move_to(self.center(r, c)).set_fill(ManimColor(self.land), 1).set_stroke(width=0)
                lip = RoundedRectangle(width=side, height=side * 0.34, corner_radius=self.corner * side * 0.6)
                lip.move_to(self.center(r, c) + np.array([0, side * 0.33, 0]))
                lip.set_fill(ManimColor(self.land_top), 1 if self.tile_lips else 0).set_stroke(width=0)
                self.tiles[r, c], self.lips[r, c] = t, lip
                grp.add(t, lip) if self.tile_lips else grp.add(t)
        H = R * self.s
        xl, xr = self.x0 - self.s * 0.28, self.x0 + C * self.s + self.s * 0.28
        self.wall_l = Line([xl, self.y0, 0], [xl, self.y0 - H, 0], stroke_width=self.wall_width * 100,
                           color=ManimColor(self.left)).set_stroke(opacity=0.35)
        self.wall_r = Line([xr, self.y0, 0], [xr, self.y0 - H, 0], stroke_width=self.wall_width * 100,
                           color=ManimColor(self.right)).set_stroke(opacity=0.35)
        grp.add(self.wall_l, self.wall_r)
        self.path, self.path_mob, self.dot = None, None, None
        anims = [FadeIn(grp)]
        if self.walker:
            self.path = self._walk()
            self.path_mob = self._path_mob(self.path)
            anims.append(FadeIn(self.path_mob))
            if self.walker_dot:
                col = ManimColor(self.walker_dot_color or self.walker_color)
                self.dot = Circle(radius=self.s * 0.16).set_fill(col, 1).set_stroke(ManimColor("#000000"),
                                                                                    width=2, opacity=0.35)
                self.dot.move_to(self.path_mob.point_from_proportion(0))
                self.cur_path = self.path_mob
                self._clock = [0.0]
                period, pm = self.walker_period, self.path_mob

                def walk_on(m, dt, period=period):
                    self._clock[0] += dt
                    a = (self._clock[0] / period) % 2.0     # down, then back up (no jumping)
                    a = rate_functions.ease_in_out_sine(a if a <= 1 else 2 - a)
                    m.move_to(self.path_mob.point_from_proportion(a))
                self._walk_on = walk_on
                anims.append(FadeIn(self.dot))
        self.group = grp
        return anims

    def _rc(self, v):
        r, c = v[0], v[1]
        return (r - 1, c - 1) if self.one_indexed else (r, c)

    def center(self, r, c):
        return np.array([self.x0 + (c + 0.5) * self.s, self.y0 - (r + 0.5) * self.s, 0.0])

    # ─────────────────────────────────────────────────── the pools ──
    def _find(self, x):
        while self.par[x] != x:
            self.par[x] = self.par[self.par[x]]
            x = self.par[x]
        return x

    def _union(self, a, b):
        ra, rb = self._find(a), self._find(b)
        if ra == rb:
            return False
        la, lb = self.side[ra], self.side[rb]
        self.par[ra] = rb
        self.side[rb] = (la[0] or lb[0], la[1] or lb[1])
        return True

    def _members(self, root):
        return [p for p in self.water_set if self._find(p) == root]

    def _gap(self):
        """How many more cells the two walls' water needs to meet (Chebyshev distance - 1)."""
        L = [p for p in self.water_set if self.side[self._find(p)][0]]
        Rr = [p for p in self.water_set if self.side[self._find(p)][1]]
        Lx = L + [(r, -1) for r in range(self.rows)]
        Rx = Rr + [(r, self.cols) for r in range(self.rows)]
        best = self.cols
        for a in Lx:
            for b in Rx:
                d = max(abs(a[0] - b[0]), abs(a[1] - b[1])) - 1
                if d < best:
                    best = d
        return max(0, best)

    def _color(self, root):
        l, r = self.side[root]
        if l and r:
            return self.joined
        return self.left if l else self.right if r else self.water

    # ─────────────────────────────────────────────────── the walker ──
    def _walk(self):
        """Shortest 4-connected path through land from the top row to the bottom row (or None)."""
        R, C = self.rows, self.cols
        starts = [(0, c) for c in range(C) if (0, c) not in self.water_set]
        prev = {s: None for s in starts}
        dq = deque(sorted(starts, key=lambda p: abs(p[1] - (C - 1) / 2)))
        while dq:
            p = dq.popleft()
            if p[0] == R - 1:
                out = []
                while p is not None:
                    out.append(p); p = prev[p]
                return out[::-1]
            for a, b in ((p[0] + 1, p[1]), (p[0], p[1] - 1), (p[0], p[1] + 1), (p[0] - 1, p[1])):
                if 0 <= a < R and 0 <= b < C and (a, b) not in self.water_set and (a, b) not in prev:
                    prev[a, b] = p; dq.append((a, b))
        return None

    def _path_mob(self, path):
        pts = [self.center(*path[0]) + np.array([0, self.s * 0.5, 0])] + [self.center(*p) for p in path] + \
              [self.center(*path[-1]) - np.array([0, self.s * 0.5, 0])]
        m = VMobject().set_points_as_corners(pts)
        m.set_stroke(ManimColor(self.walker_color), width=3.2, opacity=0.8)
        return m

    # ───────────────────────────────────────────────────── one day ──
    def handle(self, scene, e):
        if self.done:
            return
        if self.dot is not None and self.walker_period and not self.dot.updaters:
            self.dot.add_updater(self._walk_on)
        if not hasattr(self, "cur_path"):
            self.cur_path = self.path_mob
        p = tuple(e["value"][:2])
        p = self._rc(p)
        speed = scene.S.timing.speed
        last = self._is_last(p)
        if last and self.final_hold:
            scene.wait(self.final_hold / speed)
        self.water_set.add(p)
        self.par[p] = p
        self.side[p] = (p[1] == 0, p[1] == self.cols - 1)
        before = {q: self.side[self._find(q)] for q in self.water_set if q != p}
        merged = 0
        for a in (p[0] - 1, p[0], p[0] + 1):
            for b in (p[1] - 1, p[1], p[1] + 1):
                if (a, b) != p and (a, b) in self.water_set:
                    merged += self._union((a, b), p)
        root = self._find(p)
        members = self._members(root)
        col = ManimColor(self._color(root))
        anims = []
        t, lip = self.tiles[p], self.lips[p]
        # the drop: the tile dips and turns to water, the lip drains away
        anims.append(t.animate(rate_func=rate_functions.ease_out_back).set_fill(col).scale(0.92))
        if self.tile_lips:
            anims.append(lip.animate(rate_func=rate_functions.ease_out_cubic).set_fill(opacity=0).stretch(0.2, 1))
        recolor = [q for q in members if q != p and before.get(q) != self.side[root]]
        for q in recolor:
            anims.append(self.tiles[q].animate(rate_func=rate_functions.ease_out_cubic).set_fill(col))
        reached = []
        was = (any(before[q][0] for q in members if q != p), any(before[q][1] for q in members if q != p))
        now = self.side[root]
        if now[0] and not was[0]:
            reached.append(0)
        if now[1] and not was[1]:
            reached.append(1)
        for k in reached:
            wall = self.wall_l if k == 0 else self.wall_r
            if self.claim_walls:
                lit = ManimColor(self.claimed or (self.left if k == 0 else self.right))
                anims.append(wall.animate(rate_func=rate_functions.ease_out_cubic).set_stroke(color=lit, opacity=1))
            else:
                anims.append(wall.animate(rate_func=there_and_back).set_stroke(opacity=1))
        # the walker
        rerouted, redraw = False, []
        if self.walker and self.path is not None and p in self.path:
            new = self._walk()
            if new is not None:
                self.path = new
                if self.pacing == "importance":
                    # simple staging: the cut route fades as the water lands, then the new route draws in
                    old = self.cur_path
                    anims.append(old.animate(rate_func=rate_functions.ease_out_cubic).set_stroke(opacity=0))
                    fresh = self._path_mob(new)
                    redraw.append(Create(fresh, rate_func=rate_functions.ease_in_out_cubic))
                    if self.dot is not None and not self.walker_period:
                        redraw.append(self.dot.animate(rate_func=rate_functions.ease_in_out_cubic)
                                      .move_to(fresh.point_from_proportion(0)))
                    self._old_paths = getattr(self, "_old_paths", []) + ([old] if old is not self.path_mob else [])
                    self.cur_path = fresh
                else:
                    anims.append(self.path_mob.animate(rate_func=rate_functions.ease_in_out_cubic)
                                 .become(self._path_mob(new)))
                rerouted = True
        crossed = now[0] and now[1]
        self._sounds(scene, merged, reached, rerouted, last or crossed)
        busy = merged or reached or rerouted
        tension = 1 - self._gap() / self.cols
        key = crossed or reached or merged
        if self.code_follow != "key" or key:
            self._code(scene, "find(" if crossed else "union((a, b)" if merged else
                       ("c == 1" if 0 in reached else "c == col") if reached else ".add(")
        if self.pacing == "importance":
            base = self.wall_time if reached else self.cut_time if rerouted else \
                self.merge_time if merged else self.plain_time
            base *= 1 + 0.8 * tension ** 2                      # the last few days before they meet slow down
        else:
            base = (self.event_time if busy else self.day_time) * (0.7 + 0.6 * tension)
        scene.play(*anims, run_time=base / speed)
        if redraw:
            scene.add(self.cur_path)
            if self.dot is not None:
                scene.bring_to_front(self.dot)
            scene.play(*redraw, run_time=self.redraw_time / speed)
        if crossed:
            self.done = True
            self._finish_chain(scene, p)

    def _code(self, scene, snippet):
        """Point a gliding code highlight at the first source line containing `snippet`."""
        from .components import CodePanel
        src = (scene.S.source or "").splitlines()
        line = next((k + 1 for k, t in enumerate(src) if snippet in t), None)
        if line is None:
            return
        for c in scene.S.components:
            if isinstance(c, CodePanel) and c.glide:
                c.target(line)

    def _is_last(self, p):
        """Is this the drop that will close the chain? (Checked on a copy, before it happens.)"""
        par, side = dict(self.par), dict(self.side)
        par[p] = p
        side[p] = (p[1] == 0, p[1] == self.cols - 1)

        def f(x):
            while par[x] != x:
                x = par[x]
            return x
        l, r = side[p]
        for a in (p[0] - 1, p[0], p[0] + 1):
            for b in (p[1] - 1, p[1], p[1] + 1):
                if (a, b) != p and (a, b) in self.water_set:
                    s = side[f((a, b))]
                    l, r = l or s[0], r or s[1]
        return l and r

    # ───────────────────────────────────────────────────── sounds ──
    def _sounds(self, scene, merged, reached, rerouted, final):
        if not scene.synth:
            return
        h = self.humanize
        rng = self._rng
        tension = (self.cols - self._gap()) / self.cols     # 0 far apart … 1 touching
        # small bubbles ring high (≈0.5–1.5 kHz here, where a phone speaker plays well); the closer the
        # two sides are to meeting, the higher and a little louder each drop (a built-in crescendo)
        deg = 9 + int(round(tension * 8))
        cents = int(rng.uniform(-12, 12) * h)
        var = int(rng.integers(4))
        if final:
            scene.note(deg=5, instrument=self.final, gain=self.final_gain)
            return
        scene.note(deg=deg, instrument=self.drop, gain=self.drop_gain - 2 + 10 * tension + rng.uniform(-1.5, 1.5) * h,
                   cents=cents, variant=var)
        if merged and self.merge:
            scene.note(deg=max(0, deg - 5), instrument=self.merge, gain=self.merge_gain, offset=0.03)
        for k in reached:
            if self.wall:
                scene.note(deg=5 if k == 0 else 8, instrument=self.wall, gain=self.wall_gain, offset=0.02)
        if rerouted and self.reroute:
            scene.note(deg=12, instrument=self.reroute, gain=self.reroute_gain,
                       offset=self.cut_time / scene.S.timing.speed if self.pacing == "importance" else 0.05)

    # ────────────────────────────────────────────────── the payoff ──
    def _chain_cells(self, last):
        W = self.water_set

        def bfs(starts, goal):
            prev = {s: None for s in starts}
            dq = deque(starts)
            while dq:
                q = dq.popleft()
                if goal(q):
                    out = []
                    while q is not None:
                        out.append(q); q = prev[q]
                    return out[::-1]
                for a in (-1, 0, 1):
                    for b in (-1, 0, 1):
                        n = (q[0] + a, q[1] + b)
                        if n in W and n not in prev:
                            prev[n] = q; dq.append(n)
        a = bfs(sorted(q for q in W if q[1] == 0), lambda q: q == last)
        b = bfs([last], lambda q: q[1] == self.cols - 1)
        return a + b[1:]

    def _finish_chain(self, scene, last):
        speed = scene.S.timing.speed
        cells = self._chain_cells(last)
        xl = self.wall_l.get_start()[0]
        xr = self.wall_r.get_start()[0]
        pts = [np.array([xl, self.center(*cells[0])[1], 0])] + [self.center(*q) for q in cells] + \
              [np.array([xr, self.center(*cells[-1])[1], 0])]
        glow = VMobject().set_points_as_corners(pts).set_stroke(ManimColor(self.chain_edge or self.chain),
                                                                width=16 if self.chain_edge else 18,
                                                                opacity=0.9 if self.chain_edge else 0.25)
        line = VMobject().set_points_as_corners(pts).set_stroke(ManimColor(self.chain), width=5, opacity=1)
        dots = VGroup(*[Circle(radius=self.s * 0.12).move_to(self.center(*q))
                        .set_fill(ManimColor(self.chain), 1).set_stroke(width=0) for q in cells])
        scene.add(glow, line)
        n = len(cells)
        T = 1.3 / speed
        anims = [Create(glow, rate_func=rate_functions.linear), Create(line, rate_func=rate_functions.linear),
                 *[FadeIn(d, scale=0.3, rate_func=lambda t, k=k: rate_functions.ease_out_back(
                     min(1, max(0, (t - k / n) * n / 1.5)))) for k, d in enumerate(dots)],
                 self.wall_l.animate.set_stroke(color=ManimColor(self.chain), opacity=1),
                 self.wall_r.animate.set_stroke(color=ManimColor(self.chain), opacity=1)]
        if self.path_mob is not None:
            anims.append(self.path_mob.animate.set_stroke(opacity=0))
            cur = getattr(self, "cur_path", None)
            if cur is not None and cur is not self.path_mob:
                anims.append(cur.animate.set_stroke(opacity=0))
        if self.dot is not None:
            self.dot.clear_updaters()
            anims.append(self.dot.animate.set_opacity(0).scale(0.4))
        if scene.synth:
            top = 2 * len(scene.synth.steps)
            for k in range(n):
                f = k / max(1, n - 1)
                scene.note(deg=5 + round(f * (top - 1)), instrument=self.run_instrument,
                           offset=(k + 0.5) / n * T, gain=-12 + 8 * f)
            if scene.S.sound_cfg.finale:                       # the run resolves straight into the chord
                from .stage import _chord
                for d in _chord(scene.synth.steps, 5 + top):
                    scene.note(deg=d, instrument=scene.S.sound_cfg.finale_instrument, offset=T + 0.02, gain=-4)
                scene._chord_done = True
        scene.play(*anims, run_time=T)
        self.chain_mobs = [glow, line, dots]
