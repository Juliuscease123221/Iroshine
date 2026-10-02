"""
iroshine.tiling — TilingView, for LeetCode 1240 (Tiling a Rectangle with the Fewest Squares) and other
square-packing searches.

Your solution keeps a stack of placed squares (e.g. `placed.append((x, y, size))` / `placed.pop()`);
TilingView draws them on a board and tells the search as a story in three acts, because a
backtracking search makes thousands of moves and no one can follow thousands of moves:

  1. the first dive      every square is shown landing, one at a time, until the board is full.
                         That's the first answer (usually not the best).
  2. the search          a time-lapse: the board flickers through the attempts that follow (drawn as
                         faint outlines), while a counter shows how many tries it has made
  3. the better answer   from the moment the search starts building the winning tiling, every square
                         lands one at a time again. When the board is full the answer lights up, and the
                         counter runs on through the rest of the search (proving nothing smaller exists)

It reads the whole run ahead of time (plan), so it knows where each act starts.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

import numpy as np
from manim import (Circle, FadeIn, FadeOut, GrowFromPoint, ManimColor, MarkupText, Rectangle, RoundedRectangle,
                   Text, VGroup, rate_functions, there_and_back)

MONDRIAN = {1: "#f2c230", 2: "#efe9dc", 3: "#2f5da8", 4: "#efe9dc", 5: "#efe9dc", 6: "#2f5da8",
            7: "#d64533", 8: "#efe9dc", 9: "#f2c230", 10: "#2f5da8", 11: "#efe9dc", 12: "#d64533"}


@dataclass
class TilingView:
    cols: int
    rows: int
    name: str = "placed"                       # the stack of (x, y, size) your code pushes and pops
    position: Tuple[float, float] = (0.0, 0.0)
    size: Tuple[float, float] = (3.0, 3.5)
    colors: object = field(default_factory=lambda: dict(MONDRIAN))   # {size: colour}, or a function size -> colour
    ink: Dict[int, str] = field(default_factory=dict)       # number colour per square size (default: auto)
    board: str = "#262624"
    frame_color: str = "#0c0c0c"
    dot: str = "#4a4944"
    gap: float = 0.09                          # the black lines between squares (fraction of a cell)
    numbers: bool = True
    corner: Optional[str] = "#fff2c2"          # a marker on the corner the search fills next
    place_time: float = 0.55
    lift_time: float = 0.3
    done_hold: float = 0.8
    montage_frames: int = 44                   # act 2: how many snapshots of the search
    story: str = "acts"                        # "acts": dive · time-lapse · the winner built again, then a counter
                                               # "ramp": one continuous search that starts slow (every square lands,
                                               #   solid) and speeds up into the time-lapse, fading to outlines
                                               # "reveal": a quick first try that shrinks to a thumbnail (the score
                                               #   to beat) · a time-lapse of the WHOLE search, pausing a beat when
                                               #   a better tiling appears · the best tiling snaps in at the very end
    best_label: str = "BEST"                   # e.g. "FEWEST" (a label that says what the goal is)
    dive_time: float = 0.28                    # (reveal) seconds per square in the first try
    find_hold: float = 0.55                    # (reveal) the beat when a better tiling turns up
    thumb_pos: Optional[Tuple[float, float]] = None   # (reveal) where the first try's thumbnail sits
    thumb_width: float = 0.85
    thumbnail: bool = True                     # (reveal) False: the first try just fades into the time-lapse
                                               #   (its score lives on in the FEWEST readout)
    ramp_events: int = 40                      # (ramp) the first N moves are each shown, getting quicker, while
    ramp_slow: float = 0.34                    #   the squares fade from solid to outlines; then the time-lapse
    found_style: str = "hold"                  # "proof": show the better tiling when it's found (the climax), keep it
                                               #   faintly under the rest of the search, and show every later
                                               #   attempt being cut off when it reaches that many squares
                                               # "silent": say nothing until the search ends; FEWEST drops at the reveal
                                               # "hold": pause on a better tiling, outlined · "number": don't show it
                                               #   (no spoiler); only FEWEST drops, with a bump and a sound, and the
                                               #   time-lapse keeps going. The shape is first seen at the very end
    find_transition: str = "cut"               # (proof) how the time-lapse arrives at the better tiling:
                                               #   "cut": straight to it · "pause": a held beat first (hit-stop)
                                               #   "crossfade": the last attempt dissolves into it
                                               #   "slowmo": the time-lapse slows, the winning path plays live and
                                               #   its squares turn solid as they land (the opening, reversed)
    cut_color: str = "#e0574f"                 # (proof) attempts cut off at the ceiling
    underlay_opacity: float = 0.3              # (proof) the answer stays faintly visible while the search checks it
    outline: Optional[str] = None              # an ink line around each solid square (shapes read by line, not hue)
    outline_width: float = 2.5
    end_slowdown: int = 0                      # the last N time-lapse frames slow down (a ritardando into the end)
    end_slow_dt: float = 0.2                   #   …to this many seconds per frame
    reveal_pause: float = 0.0                  # a breath before the answer: the last attempt fades, the board
                                               #   sits empty and quiet for this long, then the answer snaps in
    chord_sweep: bool = False                  # at the end, light the winning squares one by one (biggest
                                               #   first), each adding a note to a chord, then ring it out
    sweep_step: float = 0.32
    show_count: bool = True                    # False: no SQUARES readout (the board already shows the count)
    montage_after: int = 24                    # (reveal) snapshots after the best is found (the search proving
    montage_after_dt: float = 0.05             #   nothing smaller exists goes by quicker: less to see there)
    montage_dt: float = 0.075
    ghost: str = "#8a867d"                     # act 2: squares drawn as outlines in this colour
    proof_time: float = 1.2                    # act 3: the counter runs through the rest of the search
    # readouts (drawn by the view; x is the left edge)
    readout_x: Optional[float] = None
    readout_y: float = 0.0
    text: str = "#efe9dc"
    muted: str = "#8a867d"
    accent: str = "#f2c230"
    # sound
    place_instrument: str = "log_drum"
    lift_instrument: str = "wood_soft"
    tick_instrument: str = "wood_soft"
    sound_arc: str = "cut"                     # (proof + outline_build) how the time-lapse ticks are phrased
                                               #   "cut": one rise across the whole time-lapse (the original)
                                               #   "arc": the rise peaks at the find and never restarts mid-way:
                                               #     time-lapse → the winning build (same line, slowing down) →
                                               #     lands on the home note as it fills → the count climbs an
                                               #     octave to the hit → a rest → the proof is a new, softer rise
                                               #   "coda": like "arc", but the proof sits low and steady (the find
                                               #     stays the peak), lifting only as it slows into the ending
    highlight: str = "flash"                   # how a square is pointed at when counted / swept:
                                               #   "flash": it flashes white · "pop": it brightens in its own
                                               #   colour and grows into its ink line (the size colour stays
                                               #   readable); the hit is one small breath of the whole tiling
    find_count: bool = True                    # (outline_build) count the squares when the answer is found
    ending: str = "reveal"                     # (proof) "reveal": the answer fades out and is shown again
                                               #   "confirm": the faint answer under the proof lifts back to full
                                               #   colour, on one chord — the same squares, never re-revealed
                                               #   "confirm_sweep": lifts back, then the chord sweep counts it
    loop_out: str = "fade"                     # how the answer leaves before the loop restarts:
                                               #   "fade": with everything else · "dissolve": it rests for
    loop_hold: float = 0.9                     #   `loop_hold`, then its colour drains back to outlines (the
                                               #   opening's solid → outline, again) which fade as the board resets
    tick_every: int = 1                        # fast time-lapse frames (under 0.1 s) tick only every Nth frame

    # ────────────────────────────────────────────────── plan ahead ──
    def wants(self, e):
        return e.get("list") == self.name and e["type"] in ("push", "pop")

    def plan(self, scene, events):
        mine = [e for e in events if self.wants(e)]
        self.index = {id(e): k for k, e in enumerate(mine)}
        area, stack, done = self.cols * self.rows, [], []
        best_n = area + 1
        self.depth, self.types, self.full = [], [], []
        for k, e in enumerate(mine):
            if e["type"] == "push":
                stack.append(tuple(e["value"][:3]))
                if sum(s * s for _, _, s in stack) == area and len(stack) < best_n:
                    done.append(k)                      # only a tiling that beats the best so far counts
                    best_n = len(stack)
            else:
                stack.pop()
            self.depth.append(len(stack))
            self.types.append(e["type"])
            self.full.append(sum(s * s for _, _, s in stack) == area)
        self.n_events = len(mine)
        self.pushes_total = sum(1 for e in mine if e["type"] == "push")
        self.first, self.last = done[0], done[-1]
        self.D = max([k for k in range(self.last) if mine[k]["type"] == "pop"], default=self.first)
        span = list(range(self.first + 1, self.D + 1))
        if self.story == "ramp":
            R = min(self.ramp_events, self.last)
            self.ramp_end = R
            pre = list(range(R, self.last + 1))
            post = list(range(self.last + 1, self.n_events))
            a = max(1, len(pre) // self.montage_frames)
            b = max(1, len(post) // max(1, self.montage_after))
            self.snap_at = set(pre[::a]) | set(post[::b])
            if self.found_style == "proof":
                # after the answer: only the moments an attempt hits the ceiling (as many squares as the best,
                # board not full) and is cut off — the proof, made visible
                cuts = [k for k in post if self.types[k] == "push" and self.depth[k] >= best_n and not self.full[k]]
                c = max(1, len(cuts) // max(1, self.montage_after))
                self.snap_at = set(pre[::a]) | set(cuts[::c]) | set(done[1:])
                if self.find_transition in ("slowmo", "rebuild_pause", "rebuild_fade", "outline_build"):
                    self.snap_at -= set(range(self.D + 1, self.last + 1))
                    self.snap_at.add(self.D)
            elif self.found_style in ("number", "silent"):
                self.snap_at -= set(done)                # never flash the answer before the end
            else:
                self.snap_at |= set(done[1:])
        elif self.story == "reveal":                      # the time-lapse covers the whole rest of the search
            pre = list(range(self.first + 1, self.last + 1))
            post = list(range(self.last + 1, self.n_events))
            a = max(1, len(pre) // self.montage_frames)
            b = max(1, len(post) // max(1, self.montage_after))
            self.snap_at = set(pre[::a]) | set(post[::b]) | set(done[1:])
        else:
            step = max(1, len(span) // self.montage_frames)
            self.snap_at = set(span[::step][:self.montage_frames]) | {self.D} if span else set()
        self.done_at = set(done)
        self.pushes_before = []
        c = 0
        for e in mine:
            c += e["type"] == "push"
            self.pushes_before.append(c)
        # the board
        W, H = self.size
        self.s = min(W / self.cols, H / self.rows)
        self.x0 = self.position[0] - self.cols * self.s / 2
        self.y0 = self.position[1] - self.rows * self.s / 2               # bottom edge
        g = VGroup()
        fr = Rectangle(width=self.cols * self.s + self.s * 0.3, height=self.rows * self.s + self.s * 0.3)
        fr.move_to([*self.position, 0]).set_fill(ManimColor(self.frame_color), 1).set_stroke(width=0)
        bd = Rectangle(width=self.cols * self.s, height=self.rows * self.s)
        bd.move_to([*self.position, 0]).set_fill(ManimColor(self.board), 1).set_stroke(width=0)
        g.add(fr, bd)
        for i in range(self.cols):
            for j in range(self.rows):
                g.add(Circle(radius=self.s * 0.045).move_to(self._pt(i + 0.5, j + 0.5))
                      .set_fill(ManimColor(self.dot), 1).set_stroke(width=0))
        self.stack, self.mobs = [], []
        self.best, self.tries = None, 0
        rx = self.readout_x if self.readout_x is not None else self.x0 + self.cols * self.s + 0.3
        self.rx = rx
        self._rows = {"sq": 0, "best": 1, "tries": 2} if self.show_count else {"sq": 9, "best": 0, "tries": 1}
        self.lbl_sq, self.num_sq = self._label("SQUARES", self._rows["sq"]), self._num("0", self.text)
        self.lbl_best, self.num_best = self._label(self.best_label, self._rows["best"]), self._num("–", self.accent)
        self.lbl_tries, self.num_tries = self._label("TRIES", self._rows["tries"]), self._num("0", self.muted, small=True)
        for key, (l, n) in (("sq", (self.lbl_sq, self.num_sq)), ("best", (self.lbl_best, self.num_best)),
                            ("tries", (self.lbl_tries, self.num_tries))):
            self._place_num(n, self._rows[key])
            if key != "sq" or self.show_count:
                g.add(l, n)
        self.marker = None
        if self.corner:
            self.marker = Circle(radius=self.s * 0.16).set_fill(ManimColor(self.corner), 1).set_stroke(width=0)
            self.marker.move_to(self._pt(0, 0) + np.array([self.s * 0.3, self.s * 0.3, 0]))
            g.add(self.marker)
        self.phase = "dive"
        return g

    # ─────────────────────────────────────────────────── helpers ──
    def _pt(self, x, y):
        return np.array([self.x0 + x * self.s, self.y0 + y * self.s, 0.0])

    def _label(self, text, row):
        t = MarkupText(f'<span letter_spacing="1400">{text}</span>', font="IBM Plex Mono", font_size=7,
                       color=ManimColor(self.muted))
        t.move_to([self.rx, self.readout_y - row * 0.62 + 0.17, 0], aligned_edge=[-1, 0, 0])
        return t

    def _num(self, s, color, small=False):
        return Text(s, font="Inter", weight="LIGHT", font_size=18 if small else 26, color=ManimColor(color))

    def _place_num(self, n, row):
        n.move_to([self.rx, self.readout_y - row * 0.62 - 0.05, 0], aligned_edge=[-1, 0, 0])

    def _set(self, which, value, color):
        row = self._rows[which]
        mob = {"sq": self.num_sq, "best": self.num_best, "tries": self.num_tries}[which]
        new = self._num(str(value), color, small=which == "tries")
        self._place_num(new, row)
        mob.become(new)

    def _style(self, m, g):
        """Blend a square between solid (g = 0) and an outline (g = 1)."""
        sq = self._fill(m)
        sq.set_fill(opacity=1 - g)
        if getattr(m, "backing", None) is not None:
            # the outline grows on the full-cell plate, so fading squares end up touching, like the time-lapse
            m.backing.set_fill(opacity=1 - g)
            m.backing.set_stroke(ManimColor(self.ghost), width=2, opacity=0.7 * g)
            sq.set_stroke(width=0)
        else:
            sq.set_stroke(ManimColor(self.ghost), width=2, opacity=0.7 * g)
        for t in m:
            if t is not sq and t is not getattr(m, "backing", None):
                t.set_opacity(0.75 * (1 - g))

    @staticmethod
    def _fill(m):
        return getattr(m, "sq", None) or m[0]

    def _ramp_story(self, scene, e, k, v, speed):
        R = self.ramp_end
        if k < R:                                                    # every move shown, quicker and quicker
            f = k / max(1, R - 1)
            dt = self.ramp_slow * (self.montage_dt / self.ramp_slow) ** f
            g = min(1.0, max(0.0, (k - self.first) / max(1, R - self.first)))
            g = g * g * (3 - 2 * g)
            x, y, size = v
            anims = []
            self._code(scene, "put(x, low, s, 1)" if e["type"] == "push" else "put(x, low, s, -1)")
            if e["type"] == "push":
                m = self._square(x, y, size)
                self._style(m, g)
                self.mobs.append(m)
                anims.append(GrowFromPoint(m, self._pt(x, y), rate_func=rate_functions.ease_out_back))
                self._note(scene, deg=max(0, 12 - size), instrument=self.place_instrument,
                           gain=-7 + min(6, size) - 8 * f)
            else:
                old = self.mobs.pop()
                anims.append(FadeOut(old))
                self._note(scene, deg=12, instrument=self.lift_instrument, gain=-15 - 4 * f)
            for m in self.mobs[:-1] if e["type"] == "push" else self.mobs:
                self._style(m, g)
            if self.marker is not None:
                nxt = self._corner()
                if nxt is not None:
                    anims.append(self.marker.animate.move_to(nxt).set_opacity(1 - g))
            scene.play(*anims, run_time=dt / speed)
            if self.marker is not None:
                scene.bring_to_front(self.marker)
            self._set("tries", self.tries, self.muted)
            if k == self.first:                                      # the first full board: noted, not stopped for
                self.best = len(self.stack)
                self._set("best", self.best, self.accent)
                if scene.synth:
                    for j, d in enumerate((2, 4, 6)):
                        scene.note(deg=d, instrument="wood", offset=j * 0.07, gain=-9)
                scene.play(*[a for m in self.mobs for a in self._point_anims(m, 0.9)] +
                           [self.num_best.animate(rate_func=there_and_back).scale(1.35)], run_time=0.35 / speed)
            return
        if k == R and self.marker is not None:
            self.marker.set_opacity(0)
        if self.found_style == "proof" and self.find_transition == "slowmo" and self.D < k <= self.last:
            self._slowmo_live(scene, e, k, v, speed)
            return
        if self.found_style == "proof" and self.find_transition == "outline_build" and self.D < k <= self.last:
            self._outline_build(scene, e, k, v, speed)
            return
        if self.found_style == "proof" and self.find_transition.startswith("rebuild") and self.D < k <= self.last:
            self._rebuild_live(scene, e, k, v, speed)
            return
        if (self.found_style == "proof" and k in self.done_at and k != self.first
                and self.find_transition in ("pause", "crossfade")):
            self._found_proof(scene, speed)
        elif k in self.snap_at:                                      # the time-lapse
            self._snapshot(scene, k, speed)
            if k in self.done_at and k != self.first:
                if self.found_style == "proof":
                    self._found_proof(scene, speed)
                else:
                    self._found(scene, speed)
        elif k in self.done_at and k != self.first and self.found_style == "number":
            self._found_number(scene, speed)
        elif k in self.done_at and k != self.first and self.found_style == "silent":
            self._best_stack = list(self.stack)                    # known to the code, not shown yet
        if k == self.n_events - 1:
            self._final_reveal(scene, speed)

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

    def _slowmo_live(self, scene, e, k, v, speed):
        """The winning path, live: each square lands slower than the last and turns solid as it lands."""
        D, L = self.D, self.last
        if k == D + 1:                                              # the attempt so far becomes restylable squares
            for m in self.mobs:
                scene.remove(m)
            self.mobs = [self._square(x, y, s) for x, y, s in self.stack[:-1]] if e["type"] == "push" else \
                [self._square(x, y, s) for x, y, s in self.stack]
            for m in self.mobs:
                self._style(m, 1.0)
            if self.mobs:
                scene.add(*self.mobs)
        f = (k - D) / max(1, L - D)
        g = 1.0 - f
        dt = 0.12 + (0.42 - 0.12) * f ** 1.5
        x, y, size = v
        anims = []
        self._code(scene, "put(x, low, s, 1)" if e["type"] == "push" else "put(x, low, s, -1)")
        if e["type"] == "push":
            m = self._square(x, y, size)
            self._style(m, g)
            anims.append(GrowFromPoint(m, self._pt(x, y), rate_func=rate_functions.ease_out_back))
            restyle = list(self.mobs)
            self.mobs.append(m)
            self._note(scene, deg=max(0, 12 - size), instrument=self.place_instrument, gain=-12 + 8 * f)
        else:
            anims.append(FadeOut(self.mobs.pop()))
            restyle = list(self.mobs)
        for m in restyle:
            self._style(m, g)
        self._set("tries", self.tries, self.muted)
        scene.play(*anims, run_time=dt / speed)
        if k == L:
            self._found_proof(scene, speed)

    def _outline_build(self, scene, e, k, v, speed):
        """The winning attempt, in the time-lapse's own style: outline frames, one per move, a little slower so
        it can be followed. When the board fills, the outlines fill with colour, the squares are counted one by
        one (FEWEST counts along), and then the search carries on."""
        self._redraw(scene, ghost=True)
        self._code(scene, "put(x, low, s, 1)" if e["type"] == "push" else "put(x, low, s, -1)")
        self._set("tries", self.tries, self.muted)
        f = (k - self.D) / max(1, self.last - self.D)
        steps = scene.synth.steps if scene.synth else [0, 2, 4, 7, 9]
        n = len(steps)
        arc = self._arc()
        if not arc:
            self._note(scene, deg=8 + int(6 * f), instrument=self.tick_instrument, gain=-13)
            scene.wait((0.14 + 0.1 * f) / speed)
        else:                                   # the same line carries on, one step from home, slowing down
            # (the last square too: it lands on its own tick, and the colour arrives on the next one)
            self._note(scene, deg=2 * n - 2 + round(f), instrument=self.tick_instrument, gain=-12 + 2 * f)
            dt0 = getattr(self, "_arc_last_dt", self.montage_dt)
            scene.wait((dt0 + (0.26 - dt0) * f ** 1.5) / speed)
        if k != self.last:
            return
        if arc and scene.synth:                 # the board is full: the line lands on the home note
            scene.note(deg=2 * n, instrument="wood", gain=-6)
        # the outlines fill with colour
        from manim import UpdateFromAlphaFunc, Mobject
        ghosts = list(self.mobs)
        solid = [self._square(x, y, s) for x, y, s in self.stack]
        for m in solid:
            self._style(m, 1.0)
        for m in ghosts:
            scene.remove(m)
        scene.add(*solid)
        self.mobs = solid
        if scene.synth:
            scene.note(deg=0, instrument=self.place_instrument, gain=-4)
        scene.play(UpdateFromAlphaFunc(Mobject(), lambda _, a: [self._style(m, 1 - rate_functions.ease_out_cubic(a))
                                                                 for m in solid]),
                   run_time=0.6 / speed)
        # counted, one by one (FEWEST counts along)
        N = len(solid)
        order = range(N) if self.find_count else [N - 1]
        for i in order:
            m = solid[i]
            self._set("best", i + 1 if self.find_count else N, self.accent)
            if arc and i == N - 1:              # the last count IS the hit: an octave above where it landed
                if scene.synth:
                    pick = lambda semis: min(range(n), key=lambda j: abs(steps[j] - semis))
                    scene.note(deg=0, instrument=self.place_instrument, gain=-3)
                    scene.note(deg=3 * n, instrument="wood", gain=-5)
                    for d in (2 * n, 2 * n + pick(4), 2 * n + pick(7)):
                        scene.note(deg=d, instrument="soft_sine", gain=-14)
                scene.play(*self._hit_anims(solid), self.num_best.animate(rate_func=there_and_back).scale(1.5),
                           run_time=0.45 / speed)
                self._hit_done = True
                break
            if scene.synth:
                d = 2 * n + round(n * i / max(1, N - 1)) if arc else n + (i * 2) % (2 * n)
                scene.note(deg=d, instrument="wood", gain=-8)
            scene.play(*self._point_anims(m, 1.0), self.num_best.animate(rate_func=there_and_back).scale(1.3),
                       run_time=0.26 / speed)
        self._found_proof(scene, speed)

    def outro(self, scene):
        """Before the loop restarts: let the answer rest, then drain it to outlines (never a hard cut)."""
        if self.loop_out != "dissolve" or not getattr(self, "win", None):
            return
        from manim import UpdateFromAlphaFunc, Mobject
        speed = scene.S.timing.speed
        scene.wait(self.loop_hold / speed)
        fam = {id(f) for m in self.mobs for f in m.get_family()}
        for m in list(scene.mobjects):                   # grouped animations leave wrappers behind: start clean
            if any(id(f) in fam for f in m.get_family()):
                scene.remove(m)
        fresh = [self._square(x, y, s) for x, y, s in self.win]
        scene.add(*fresh)
        self.mobs = fresh
        if self.marker is not None:
            scene.bring_to_front(self.marker)
        driver = Mobject()
        scene.play(UpdateFromAlphaFunc(driver, lambda _, a: [self._style(m, rate_functions.ease_in_out_cubic(a))
                                                             for m in fresh]), run_time=0.55 / speed)
        scene.remove(driver)

    # ── pointing at squares ──
    def _lift(self, c):
        """The square's own colour, a step lighter: same hue, so its size colour still reads."""
        import colorsys
        r, g, b = ManimColor(c).to_rgb()
        h, l, s_ = colorsys.rgb_to_hls(r, g, b)
        return ManimColor(colorsys.hls_to_rgb(h, min(0.92, l + 0.14), s_))

    def _point_anims(self, m, opacity):
        """Point at one square: a white flash, or ("pop") a lift in its own colour as it grows into its ink
        line (motion onset catches the eye; the colour, which carries the size, is never wiped out)."""
        sq = self._fill(m)
        if self.highlight != "pop":
            return [sq.animate(rate_func=there_and_back).set_fill(ManimColor("#ffffff"), opacity)]
        side = sq.width
        pad = self.s * self.gap / 2
        k = 1 + 0.6 * (2 * pad) / max(side, 1e-6)        # grows ~60% of the way into the ink line
        texts = [t for t in m if t is not sq and t is not getattr(m, "backing", None)]
        # the number rides along (and stays drawn above its square, even inside a grouped animation)
        return ([sq.animate(rate_func=there_and_back).set_fill(self._lift(sq.get_fill_color()), 1).scale(k)] +
                [t.animate(rate_func=there_and_back).scale(k, about_point=sq.get_center()) for t in texts])

    def _hit_anims(self, group):
        if self.highlight != "pop":
            return [self._fill(q).animate(rate_func=there_and_back).set_fill(ManimColor("#ffffff"), 0.9)
                    for q in group]
        c = VGroup(*group).get_center()                   # one small breath of the whole tiling (each square
        return [q.animate(rate_func=there_and_back).scale(1.035, about_point=c) for q in group]   # in place)

    def _rebuild_live(self, scene, e, k, v, speed):
        """No teleporting: the attempt on screen is cleared away (the search backing out of it), then the
        winning tiling is placed square by square, solid, like the first try."""
        if k == self.D + 1:
            old = list(self.mobs)
            self.mobs = []
            if self.find_transition == "rebuild_pause":
                scene.wait(0.35 / speed)                             # hold the last attempt: a beat
                if old:                                              # …then it backs out, last square first
                    from manim import LaggedStart
                    if scene.synth:
                        for j in range(len(old)):
                            scene.note(deg=10 - j % 5, instrument=self.lift_instrument,
                                       offset=j * 0.07 / speed, gain=-16)
                    scene.play(LaggedStart(*[FadeOut(m, scale=0.6) for m in reversed(old)], lag_ratio=0.35),
                               run_time=(0.18 + 0.07 * len(old)) / speed)
            else:                                                    # "rebuild_fade": it dissolves away
                if old:
                    scene.play(*[FadeOut(m) for m in old], run_time=0.45 / speed)
            scene.wait(0.15 / speed)                                 # an empty board, for an instant
            prefix = self.stack[:-1] if e["type"] == "push" else list(self.stack)
            for (x, y, s) in prefix:                                 # anything already in place: quick
                m = self._square(x, y, s)
                self.mobs.append(m)
                scene.play(GrowFromPoint(m, self._pt(x, y), rate_func=rate_functions.ease_out_back),
                           run_time=0.2 / speed)
        x, y, size = v
        self._code(scene, "put(x, low, s, 1)" if e["type"] == "push" else "put(x, low, s, -1)")
        if e["type"] == "push":
            m = self._square(x, y, size)
            self.mobs.append(m)
            self._note(scene, deg=max(0, 12 - size), instrument=self.place_instrument, gain=-6 + min(5, size))
            scene.play(GrowFromPoint(m, self._pt(x, y), rate_func=rate_functions.ease_out_back),
                       run_time=0.34 / speed)
        else:
            scene.play(FadeOut(self.mobs.pop()), run_time=0.2 / speed)
        self._set("tries", self.tries, self.muted)
        if k == self.last:
            self._found_proof(scene, speed)

    def _found_proof(self, scene, speed):
        """The better tiling is shown the moment it's found (the climax), then stays faintly underneath while
        the search goes on trying to beat it."""
        self.win = list(self.stack)
        self.best = len(self.stack)
        self._code(scene, "best = len(placed)")
        tr = self.find_transition
        if tr == "pause":                                           # hit-stop: hold the last frame, silent
            scene.wait(0.4 / speed)
        old = list(self.mobs)
        self.mobs = []
        if tr in ("slowmo", "rebuild_pause", "rebuild_fade", "outline_build"):   # already built and solid
            self.under = old
            for m in self.under:
                self._style(m, 0.0)
            intro = []
        else:
            self.under = [self._square(x, y, s) for x, y, s in self.win]
            if tr == "crossfade":
                intro = [FadeOut(m) for m in old] + [FadeIn(m) for m in self.under]
            else:
                for m in old:
                    scene.remove(m)
                intro = [FadeIn(m, scale=0.94) for m in self.under]
        self._set("best", self.best, self.accent)
        if not getattr(self, "_hit_done", False):       # (the sound arc already played the hit on the count)
            if scene.synth:
                scene.note(deg=0, instrument=self.place_instrument, gain=-3)
                scene.note(deg=7, instrument="wood", gain=-5)
                scene.note(deg=9, instrument="wood", offset=0.1, gain=-5)
            scene.play(*intro, self.num_best.animate(rate_func=there_and_back).scale(1.5),
                       run_time=(0.7 if tr == "crossfade" else 0.45) / speed)
        scene.wait(0.75 / speed)
        self._under_full = [m.copy() for m in self.under]          # to lift back to, exactly, at the end
        scene.play(*[m.animate.set_opacity(self.underlay_opacity) for m in self.under], run_time=0.35 / speed)

    def _found_number(self, scene, speed):
        """A better tiling exists now, but it isn't shown: FEWEST drops (a teaser; the shape waits for the end)."""
        self.win = list(self.stack)
        self.best = len(self.stack)
        self._set("best", self.best, self.accent)
        if scene.synth:
            scene.note(deg=7, instrument="wood", gain=-5)
            scene.note(deg=9, instrument="wood", offset=0.1, gain=-5)
        scene.play(self.num_best.animate(rate_func=there_and_back).scale(1.5), run_time=0.4 / speed)

    def _square(self, x, y, size, ghost=False):
        pad = self.s * self.gap / 2
        side = size * self.s - 2 * pad
        sq = RoundedRectangle(width=side, height=side, corner_radius=min(self.s * 0.12, side * 0.1))
        sq.move_to(self._pt(x + size / 2, y + size / 2))
        if ghost:
            if self.outline:
                # outlines trace the cell edges themselves, so neighbouring squares share one line (they touch)
                sq = Rectangle(width=size * self.s, height=size * self.s).move_to(self._pt(x + size / 2, y + size / 2))
            sq.set_fill(opacity=0).set_stroke(ManimColor(self.ghost), width=2, opacity=0.7)
            grp = VGroup(sq)
            grp.sq, grp.backing = sq, None
            return grp
        col = self.colors(size) if callable(self.colors) else self.colors.get(size, "#efe9dc")
        col = ManimColor(col)
        sq.set_fill(col, 1).set_stroke(width=0)
        backing = None
        if self.outline:
            # "leading": like the lead cames in stained glass, or grout between tiles. Each square sits on a
            # sharp-cornered plate of ink covering its whole cell, so neighbouring plates meet edge to edge and
            # the lines between squares are one even width, with no gaps where rounded corners meet.
            backing = Rectangle(width=size * self.s, height=size * self.s).move_to(sq.get_center())
            backing.set_fill(ManimColor(self.outline), 1).set_stroke(width=0)
        grp = VGroup(backing, sq) if backing is not None else VGroup(sq)
        grp.sq, grp.backing = sq, backing
        if self.numbers and size >= 2:
            r, g, b = col.to_rgb()
            lum = 0.2126 * r ** 2.2 + 0.7152 * g ** 2.2 + 0.0722 * b ** 2.2   # light squares get dark numbers
            ink = self.ink.get(size, "#1e1e1e" if lum > 0.3 else "#efe9dc")
            t = Text(str(size), font="Inter", weight="MEDIUM", font_size=min(40, 10 + 5 * size),
                     color=ManimColor(ink)).move_to(sq)
            t.set_opacity(0.75)
            grp.add(t)
        return grp

    def _corner(self):
        """Where the search will put the next square: the lowest, leftmost empty cell."""
        h = [0] * self.cols
        for x, y, s in self.stack:
            for k in range(x, x + s):
                h[k] = max(h[k], y + s)
        low = min(h)
        if low >= self.rows:
            return None
        return self._pt(h.index(low), low) + np.array([self.s * 0.3, self.s * 0.3, 0])

    def _note(self, scene, **kw):
        if scene.synth:
            scene.note(**kw)

    # ───────────────────────────────────────────────────── events ──
    def handle(self, scene, e):
        k = self.index[id(e)]
        speed = scene.S.timing.speed
        v = tuple(e["value"][:3])
        if e["type"] == "push":
            self.stack.append(v)
        else:
            self.stack.pop()
        self.tries = self.pushes_before[k]
        if self.story == "reveal":
            return self._reveal_story(scene, e, k, v, speed)
        if self.story == "ramp":
            return self._ramp_story(scene, e, k, v, speed)
        if k <= self.first or self.D < k <= self.last:
            self._live(scene, e, k, v, speed)
        elif self.first < k <= self.D:
            if k in self.snap_at:
                self._snapshot(scene, k, speed)
        elif k == self.n_events - 1:
            self._proof(scene, speed)

    # ───────────────────────────────────────────── the "reveal" story ──
    def _reveal_story(self, scene, e, k, v, speed):
        if k <= self.first:                                          # act 1: the obvious first try, quick
            x, y, size = v
            if e["type"] == "push":
                m = self._square(x, y, size)
                self.mobs.append(m)
                nxt = self._corner()
                anims = [GrowFromPoint(m, self._pt(x, y), rate_func=rate_functions.ease_out_back)]
                if self.marker is not None:
                    anims.append(self.marker.animate.set_opacity(0) if nxt is None else
                                 self.marker.animate(rate_func=rate_functions.ease_in_out_cubic).move_to(nxt))
                self._note(scene, deg=max(0, 12 - size), instrument=self.place_instrument, gain=-7 + min(6, size))
                scene.play(*anims, run_time=self.dive_time / speed)
                self._set("sq", len(self.stack), self.text)
                self._set("tries", self.tries, self.muted)
                if self.marker is not None and nxt is not None:
                    scene.bring_to_front(self.marker)
            else:
                scene.play(FadeOut(self.mobs.pop()), run_time=self.dive_time / speed)
            if k == self.first:
                self._to_thumb(scene, speed)
            return
        if k in self.snap_at:                                        # act 2: the whole search, time-lapsed
            self._snapshot(scene, k, speed)
            if k in self.done_at:
                self._found(scene, speed)
        if k == self.n_events - 1:                                   # act 3: the answer, all at once
            self._final_reveal(scene, speed)

    def _to_thumb(self, scene, speed):
        """The first try becomes the score to beat: it shrinks into a thumbnail beside the readouts."""
        self.best = len(self.stack)
        self._set("best", self.best, self.accent)
        grp = VGroup(*self.mobs)
        f = self.thumb_width / (self.cols * self.s)
        tx, ty = self.thumb_pos or (self.rx + self.thumb_width / 2, self.readout_y - 2.1)
        frame = Rectangle(width=self.cols * self.s * f + 0.05, height=self.rows * self.s * f + 0.05)
        frame.move_to([tx, ty, 0]).set_fill(ManimColor(self.frame_color), 1).set_stroke(width=0)
        if scene.synth:
            for j, d in enumerate((2, 4, 6)):
                scene.note(deg=d, instrument="wood", offset=j * 0.08, gain=-9)
        scene.play(*[self._fill(m).animate(rate_func=there_and_back).set_fill(ManimColor("#ffffff"), 0.95) for m in self.mobs],
                   run_time=0.45 / speed)
        scene.wait(0.25 / speed)
        if not self.thumbnail:                             # the first try melts into the time-lapse
            ghosts = [self._square(x, y, s, ghost=True) for x, y, s in self.stack]
            scene.play(*[m.animate(rate_func=rate_functions.ease_in_out_cubic).become(gh)
                         for m, gh in zip(self.mobs, ghosts)], run_time=0.45 / speed)
            if self.marker is not None:
                self.marker.set_opacity(0)
            return
        scene.add(frame)
        scene.bring_to_front(grp)
        scene.play(FadeIn(frame), grp.animate(rate_func=rate_functions.ease_in_out_cubic).scale(f).move_to([tx, ty, 0]),
                   run_time=0.7 / speed)
        self.thumb = VGroup(frame, grp)
        self.mobs = []
        if self.marker is not None:
            self.marker.set_opacity(0)

    def _found(self, scene, speed):
        """A better tiling turned up mid-search: hold it for a beat, outlined in the accent colour."""
        self.win = list(self.stack)
        for m in self.mobs:
            self._fill(m).set_stroke(ManimColor(self.accent), width=3, opacity=1)
        self.best = len(self.stack)
        self._set("best", self.best, self.accent)
        if scene.synth:
            scene.note(deg=7, instrument="wood", gain=-6)
            scene.note(deg=9, instrument="wood", offset=0.1, gain=-6)
        pop = min(0.4, self.find_hold)                     # the FEWEST number jumps as it drops
        scene.play(self.num_best.animate(rate_func=there_and_back).scale(1.45), run_time=pop / speed)
        scene.wait((self.find_hold - pop) / speed)

    def _final_reveal(self, scene, speed):
        if self.ending in ("confirm", "confirm_sweep") and getattr(self, "under", None):
            return self._confirm(scene, speed)
        if self.reveal_pause and self.mobs:
            scene.play(*[FadeOut(m) for m in self.mobs], run_time=min(0.25, self.reveal_pause) / speed)
            self.mobs = []
        if self.reveal_pause:
            scene.wait(self.reveal_pause / speed)
        for m in self.mobs:
            scene.remove(m)
        for m in getattr(self, "under", []):
            scene.remove(m)
        self.under = []
        if not hasattr(self, "win") or not self.win:              # "silent": the best is known only now
            self.win = self._best_stack
        self.mobs = [self._square(x, y, s) for x, y, s in self.win]
        self._set("sq", len(self.win), self.text)
        if self.found_style == "silent":
            self.best = len(self.win)
            self._set("best", self.best, self.accent)
            if scene.synth:
                scene.note(deg=7, instrument="wood", gain=-5)
                scene.note(deg=9, instrument="wood", offset=0.1, gain=-5)
            scene.play(self.num_best.animate(rate_func=there_and_back).scale(1.5), run_time=0.35 / speed)
        self._set("tries", self.pushes_total, self.muted)
        anims = [FadeIn(m, scale=0.92) for m in self.mobs]
        if scene.synth:
            scene.note(deg=0, instrument=self.place_instrument, gain=-2)
        scene.play(*anims, run_time=0.45 / speed)
        rings = []
        from manim import Circle as _C
        for (x, y, s) in self.win:
            if s == 1:
                r = _C(radius=self.s * 0.9).move_to(self._pt(x + 0.5, y + 0.5))
                r.set_fill(opacity=0).set_stroke(ManimColor(self.accent), width=4)
                rings.append(r)
        if rings:
            scene.add(*rings)
            if scene.synth:
                scene.note(deg=12, instrument="wood", offset=0.05, gain=-8)
            scene.play(*[r.animate(rate_func=rate_functions.ease_out_cubic).scale(0.4).set_stroke(opacity=0)
                         for r in rings], run_time=0.6 / speed)
        if self.chord_sweep:
            self._sweep(scene, speed)

    def _confirm(self, scene, speed):
        """Nothing beat it: the last cut-off attempt clears, and the answer that sat faintly under the whole
        proof lifts back to full colour — the same squares in the same place, so it reads as "it survived",
        not as a second reveal. One chord: the proof's rising line lands."""
        from manim import Transform
        if self.mobs:
            scene.play(*[FadeOut(m) for m in self.mobs], run_time=0.25 / speed)
        self.mobs = []
        if self.reveal_pause:
            scene.wait(self.reveal_pause / speed)
        self._set("tries", self.pushes_total, self.muted)
        self._code(scene, "best = len(placed)")
        steps = scene.synth.steps if scene.synth else [0, 2, 4, 7, 9]
        n = len(steps)
        pick = lambda semis: min(range(n), key=lambda j: abs(steps[j] - semis))
        sweep = self.ending == "confirm_sweep" and self.chord_sweep
        if scene.synth and not sweep:
            scene.note(deg=n, instrument="log_drum", gain=-3)
            for d in (2 * n, 2 * n + pick(4), 2 * n + pick(7), 3 * n):
                scene.note(deg=d, instrument="soft_sine", gain=-11)
            scene.note(deg=3 * n, instrument="wood", gain=-7)
            scene.note(deg=3 * n, instrument="drop_bell", offset=0.04, gain=-15)
        elif scene.synth:
            scene.note(deg=n, instrument=self.place_instrument, gain=-6)
        scene.play(*[Transform(m, f) for m, f in zip(self.under, self._under_full)],
                   run_time=(0.5 if sweep else 0.9) / speed, rate_func=rate_functions.ease_out_cubic)
        self.mobs, self.under = list(self.under), []
        if sweep:
            self._sweep(scene, speed)

    def _sweep(self, scene, speed):
        """Biggest square to smallest, each lighting up and adding a note: the chord builds (low to high,
        big to small, like real objects), then everything rings out together."""
        order = sorted(range(len(self.win)), key=lambda i: (-self.win[i][2], i))
        steps = scene.synth.steps if scene.synth else [0, 2, 4, 7, 9]
        n = len(steps)
        pick = lambda semis: min(range(n), key=lambda j: abs(steps[j] - semis))
        triad = [0, pick(4 if 4 in steps else 3), pick(7)]                  # root, third, fifth of the scale
        # stacked up through the octaves, starting an octave up so even the first notes carry on a phone speaker
        tones = [o * n + t for o in (1, 2, 3) for t in triad]
        from manim import AnimationGroup, Succession
        items = []
        for j, i in enumerate(order):
            m = self.mobs[i]
            d = tones[min(j, len(tones) - 1)]
            if scene.synth:
                t0 = j * self.sweep_step / speed
                scene.note(deg=d, instrument="wood", offset=t0, gain=-7)
                scene.note(deg=d, instrument="soft_sine", offset=t0, gain=-13 + j)      # the sustain that stacks up
            items.append(AnimationGroup(*self._point_anims(m, 1)) if self.highlight == "pop" else AnimationGroup(
                self._fill(m).animate(rate_func=there_and_back).set_fill(ManimColor("#ffffff"), 1),
                m.animate(rate_func=there_and_back).scale(1.05)))
        from manim import LaggedStart
        each = self.sweep_step * 1.6
        scene.play(LaggedStart(*items, lag_ratio=self.sweep_step / each),
                   run_time=(each + self.sweep_step * (len(items) - 1)) / speed)
        # the resolution: every square glows at once, a low root under the full chord
        if scene.synth:
            scene.note(deg=n, instrument="log_drum", gain=-3)
            for d in (2 * n, 2 * n + triad[1], 2 * n + triad[2], 3 * n):
                scene.note(deg=d, instrument="soft_sine", gain=-11)
            scene.note(deg=3 * n, instrument="drop_bell", offset=0.04, gain=-15)
        glow = (self._hit_anims(self.mobs) if self.highlight == "pop" else
                [self._fill(m).animate(rate_func=there_and_back).set_fill(ManimColor(self.accent), 1) for m in self.mobs])
        scene.play(*glow, run_time=0.8 / speed)

    def _live(self, scene, e, k, v, speed):
        if k == self.D + 1 and self.phase != "live2":                # act 3 begins: back to solid squares
            self._redraw(scene, ghost=False)
            self.phase = "live2"
        x, y, size = v
        if e["type"] == "push":
            m = self._square(x, y, size)
            self.mobs.append(m)
            corner = self._pt(x, y)
            anims = [GrowFromPoint(m, corner, rate_func=rate_functions.ease_out_back)]
            nxt = self._corner()
            if self.marker is not None:
                if nxt is None:
                    anims.append(self.marker.animate.set_opacity(0))
                else:
                    anims.append(self.marker.animate(rate_func=rate_functions.ease_in_out_cubic).move_to(nxt))
            deg = max(0, 12 - size)                                   # bigger squares sound lower
            self._note(scene, deg=deg, instrument=self.place_instrument, gain=-6 + min(6, size))
            scene.play(*anims, run_time=self.place_time / speed)
            self._set("sq", len(self.stack), self.text)          # counts update as the square lands
            self._set("tries", self.tries, self.muted)
            if self.marker is not None and nxt is not None:
                scene.bring_to_front(self.marker)
        else:
            m = self.mobs.pop()
            self._note(scene, deg=12, instrument=self.lift_instrument, gain=-14)
            scene.play(FadeOut(m, shift=0.1 * np.array([0, 1, 0])), run_time=self.lift_time / speed)
        if k in (self.first, self.last):
            self._done(scene, speed, final=k == self.last)

    def _done(self, scene, speed, final):
        n = len(self.stack)
        first_best = self.best is None
        self.best = n
        self._set("best", n, self.accent)
        pulse = [self._fill(m).animate(rate_func=there_and_back).set_fill(ManimColor("#ffffff"), 0.95)
                 for m in self.mobs]
        if scene.synth:
            top = 2 * len(scene.synth.steps)
            for j, d in enumerate((0, 2, 4) if not final else (0, 2, 4, 7)):
                scene.note(deg=d + (5 if final else 2), instrument="wood", offset=j * 0.09, gain=-8)
        scene.play(*pulse, run_time=0.6 / speed) if pulse else None
        if final:                                          # the surprise: the odd little square(s)
            from manim import Circle as _C
            rings = []
            for (x, y, s), m in zip(self.stack, self.mobs):
                if s == 1:
                    r = _C(radius=self.s * 0.9).move_to(self._pt(x + 0.5, y + 0.5))
                    r.set_fill(opacity=0).set_stroke(ManimColor(self.accent), width=4)
                    rings.append(r)
            if rings:
                scene.add(*rings)
                scene.play(*[r.animate(rate_func=rate_functions.ease_out_cubic).scale(0.45) for r in rings],
                           run_time=0.5 / speed)
                self.rings = rings
        scene.wait(self.done_hold / speed)

    def _redraw(self, scene, ghost):
        for m in self.mobs:
            scene.remove(m)
        self.mobs = [self._square(x, y, s, ghost=ghost) for x, y, s in self.stack]
        if self.mobs:
            scene.add(*self.mobs)
        if self.marker is not None:
            c = self._corner()
            if c is not None:
                self.marker.move_to(c).set_opacity(0 if ghost else 1)
            scene.bring_to_front(self.marker)

    def _snapshot(self, scene, k, speed):
        if self.phase == "dive":
            self.phase = "search"
        self._redraw(scene, ghost=True)
        cut = self.found_style == "proof" and k > self.last
        if cut:                                                      # this attempt hit the ceiling: cut off
            for m in self.mobs:
                self._fill(m).set_stroke(ManimColor(self.cut_color), width=3, opacity=0.95)
            self._code(scene, "if len(placed) >= best")
        else:
            self._code(scene, "put(x, low, s, 1)" if self.types[k] == "push" else "put(x, low, s, -1)")
        self._set("sq", len(self.stack), self.muted)
        self._set("tries", self.tries, self.muted)
        order = sorted(self.snap_at)
        j = order.index(k)
        n = len(order)
        left = n - 1 - j                                              # frames still to come
        after = self.story in ("reveal", "ramp") and k > self.last
        dt = self.montage_after_dt if after else self.montage_dt
        if self._arc():
            deg, gain, dt, idx = self._arc_tick(k, after, dt, left)
        else:
            deg, gain, idx = 4 + int(10 * j / max(1, n - 1)), -17 + 5 * j / max(1, n - 1), j
        if self.find_transition == "slowmo" and self.found_style == "proof" and k <= self.D:
            before = [q for q in self.snap_at if k < q <= self.D]      # frames left before the winning path
            if len(before) < 6:
                dt = dt + (0.12 - dt) * (1 - len(before) / 6)
        if self.end_slowdown and left < self.end_slowdown:
            u = 1 - left / self.end_slowdown                   # 0 → 1 over the last frames
            dt = dt + (self.end_slow_dt - dt) * u * u
        if not (dt < 0.1 and idx % max(1, self.tick_every)):    # a buzz of ticks thinned into a beat
            self._note(scene, deg=deg, instrument=self.tick_instrument, gain=gain)
        self._arc_last_dt = dt
        scene.wait(dt / speed)

    # ── the sound arc: one rising line per question, each landing before the next begins ──
    def _arc(self):
        return (self.sound_arc in ("arc", "coda") and self.found_style == "proof"
                and self.find_transition == "outline_build")

    def _arc_tick(self, k, after, dt, left):
        if not hasattr(self, "_arc_pre"):
            order = sorted(self.snap_at)
            self._arc_pre = [q for q in order if q <= self.last]
            self._arc_post = [q for q in order if q > self.last]
        if not after:                                    # question 1: rising toward the find, peaking there
            j = self._arc_pre.index(k)
            u = j / max(1, len(self._arc_pre) - 1)
            return 3 + round(5 * u ** 1.3), -17 + 5 * u, dt, j
        j = self._arc_post.index(k)
        u = j / max(1, len(self._arc_post) - 1)
        if j < 4:                                        # picks up the tempo the build slowed to, then eases in
            dt = 0.24 + (dt - 0.24) * (j / 4)
        if self.sound_arc == "coda":                     # low and steady: a settling pendulum
            if left < self.end_slowdown:
                return 5 + (self.end_slowdown - left), -18, dt, j
            return 3 + 2 * (j % 2), -19, dt, j
        return 2 + round(6 * u), -20 + 6 * u, dt, j      # question 2: a new, softer rise

    def _proof(self, scene, speed):
        """The rest of the search, as a counter running up (no smaller tiling exists)."""
        from manim import ValueTracker, always_redraw
        start, end = self.pushes_before[self.last], self.pushes_total
        tr = ValueTracker(start)
        live = always_redraw(lambda: self._placed_num(f"{int(tr.get_value()):,}"))
        scene.remove(self.num_tries)
        scene.add(live)
        if scene.synth:
            for j in range(8):
                scene.note(deg=10 + j % 3, instrument=self.tick_instrument, offset=j * self.proof_time / 9 / speed,
                           gain=-18)
        scene.play(tr.animate(rate_func=rate_functions.ease_out_cubic).set_value(end),
                   run_time=self.proof_time / speed)
        live.clear_updaters()
        self.num_tries.become(live)
        scene.remove(live)
        scene.add(self.num_tries)

    def _placed_num(self, s):
        n = self._num(s, self.muted, small=True)
        self._place_num(n, self._rows["tries"])
        return n
