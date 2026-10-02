"""
iroshine.text — views for problems about words and lines of text.

WordStrip("words")
    A list of strings drawn as word tiles, flowed like a paragraph. The tile of the
    word being read lifts; a word that has been taken becomes a faint ghost.

LineComposer(line="cur", out="res", width="maxWidth", source="words")
    A page with a fixed measure (`width` columns), built line by line:
      · cur.append(w)        the word flies from the strip onto the current line,
                             with a hollow dot where the one required space will go
      · cur[j] += " "        a real space lands in gap j (solid dot); words to its right slide over
      · res.append(s)        the line is committed exactly as the string s says
    Word positions always come from the strings themselves, so what you see is
    what your code produced, character for character.
"""

from dataclasses import dataclass
from typing import Callable, Optional, Tuple

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Circle, Dot, FadeIn, LaggedStart, Line, ManimColor,
                   Rectangle, ReplacementTransform, RoundedRectangle, Text, VGroup, rate_functions,
                   there_and_back)


_GLYPH = {}


def _glyph_scale(font, char_w):
    """Scale that makes one monospace character exactly char_w wide (same for every word)."""
    if font not in _GLYPH:
        probe = Text("M" * 20, font=font)
        _GLYPH[font] = probe.width / 20
    return char_w / _GLYPH[font]


def _tile(word, w, h, fill, ink, font, radius, char_w=None):
    box = RoundedRectangle(width=max(w, 0.05), height=h, corner_radius=min(radius, h / 2.2, w / 2.2))
    box.set_fill(ManimColor(fill), opacity=1).set_stroke(width=0)
    parts = [box]
    if word:
        # Set a leading "x" so every word shares one baseline, then drop it.
        t = Text("x" + word, font=font, color=ManimColor(ink))
        cw = char_w if char_w else w / max(1, len(word))
        t.scale(_glyph_scale(font, cw * 0.74))          # every word at the same type size
        x_glyph = t[0]
        base = x_glyph.get_bottom()[1]
        xh = x_glyph.height
        t.remove(x_glyph)
        c = box.get_center()
        t.shift([c[0] - t.get_center()[0], (c[1] - xh / 2) - base, 0])   # x-height centered in the tile
        parts.append(t)
    g = VGroup(*parts)
    g.word = word
    return g


@dataclass
class WordStrip:
    name: str                                      # the list of words in your solution
    position: Tuple[float, float] = (0.0, 2.3)
    size: Tuple[float, float] = (13.0, 1.7)
    cell: float = 0.2                              # width of one character
    line_height: float = 0.42
    gap: float = 0.14                              # space between tiles
    fill: str = "#f2a861"
    ink: str = "#1b1b3a"
    font: str = "IBM Plex Mono"
    radius: float = 0.06
    used_opacity: float = 0.18
    fills: Optional[dict] = None                   # per-word colors, e.g. {"1": "#A16193", "0": "#192242"}
    inks: Optional[dict] = None                    # per-word text colors
    read_lift: float = 0.1                         # how far a tile lifts when read
    read_color: Optional[str] = None               # a tile's color while it is being read
    read_time: float = 0.28
    dim_unread: bool = False                       # at the end, dim tiles the program never reached
    unread_opacity: float = 0.25
    reveal: bool = False                           # tiles start dim and light up once read (what the code knows)
    cursor: Optional[str] = None                   # color of a caret that glides under the tile being read
    sublabels: Optional[Callable] = None           # f(i, word, n) -> small caption under tile i
    sublabel_color: str = "#6b6760"
    sublabel_size: float = 13
    stop_mark: int = 0                             # at the end, ring the last N tiles read (where the code stopped)
    stop_color: str = "#ffffff"

    def wants(self, e):
        return e.get("list") == self.name and (e["type"] == "read" or
                                               (e["type"] == "create" and e.get("role") != "input"))

    def intro(self, scene, e):
        if e.get("list") != self.name or e["type"] != "create" or e.get("role") != "input":
            return []
        return self._build([str(w) for w in e["values"]])

    def _build(self, words):
        W, H = self.size
        x0, y0 = self.position[0] - W / 2, self.position[1] + H / 2
        rows, cur, width = [[]], 0.0, 0.0
        for w in words:                                    # flow the words like a paragraph
            tw = len(w) * self.cell + self.cell
            if cur + tw > W and rows[-1]:
                rows.append([]); cur = 0.0
            rows[-1].append((w, cur, tw)); cur += tw + self.gap
        n = len(rows)
        top = self.position[1] + n * (self.line_height + 0.12) / 2
        self.tiles = []
        for r, row in enumerate(rows):
            row_w = row[-1][1] + row[-1][2]
            off = self.position[0] - row_w / 2
            for w, x, tw in row:
                fill = (self.fills or {}).get(w, self.fill)
                ink = (self.inks or {}).get(w, self.ink)
                t = _tile(w, tw, self.line_height, fill, ink, self.font, self.radius, char_w=self.cell)
                t.move_to([off + x + tw / 2, top - r * (self.line_height + 0.12) - self.line_height / 2, 0])
                self.tiles.append(t)
        self.used, self.read, self.order = set(), set(), []
        anims = [LaggedStart(*[FadeIn(t, shift=0.1 * UP) for t in self.tiles], lag_ratio=0.04)]
        if self.reveal:
            for t in self.tiles:
                t.set_opacity(self.unread_opacity)
            anims = [LaggedStart(*[FadeIn(t, shift=0.1 * UP) for t in self.tiles], lag_ratio=0.04)]
        self.subs = VGroup()
        if self.sublabels:
            for i, (t, w) in enumerate(zip(self.tiles, words)):
                txt = self.sublabels(i, w, len(words))
                if txt is None or txt == "":
                    continue
                m = Text(str(txt), font="IBM Plex Mono", font_size=self.sublabel_size,
                         color=ManimColor(self.sublabel_color))
                m.next_to(t, DOWN, buff=0.2)
                self.subs.add(m)
            anims.append(FadeIn(self.subs, shift=0.05 * UP))
        self.caret = None
        if self.cursor:
            t0 = self.tiles[0] if self.tiles else None
            if t0 is not None:
                self.caret = Line(LEFT, RIGHT, stroke_width=4, color=ManimColor(self.cursor))
                self.caret.set_width(t0.width * 0.7).next_to(t0, DOWN, buff=0.07).set_opacity(0)
        return anims

    def handle(self, scene, e):
        if e["type"] == "create":
            anims = self._build([str(w) for w in e["values"]])
            scene.play(*anims, run_time=1.0 / scene.S.timing.speed)
            return
        if e["type"] == "read" and 0 <= e["index"] < len(self.tiles) and e["index"] not in self.used:
            t = self.tiles[e["index"]]
            self.read.add(e["index"]); self.order.append(e["index"])
            anims = [t.animate(rate_func=there_and_back).shift(self.read_lift * UP)]
            if self.reveal:
                anims = [t.animate(rate_func=rate_functions.ease_out_cubic).set_opacity(1)]
            if self.caret is not None:
                target = self.caret.copy().set_width(t.width * 0.7).next_to(t, DOWN, buff=0.07)
                if self.caret.get_stroke_opacity() == 0:
                    self.caret.move_to(target); scene.add(self.caret)
                    anims.append(self.caret.animate.set_stroke(opacity=1))
                else:
                    anims.append(self.caret.animate(rate_func=rate_functions.ease_in_out_cubic).move_to(target))
            if self.read_color:
                anims.append(t[0].animate(rate_func=there_and_back).set_fill(ManimColor(self.read_color)))
            scene.play(*anims, run_time=self.read_time / scene.S.timing.speed)

    def finish(self, scene):
        out = []
        if self.dim_unread and not self.reveal:
            out += [t.animate.set_opacity(self.unread_opacity) for k, t in enumerate(self.tiles) if k not in self.read]
        if self.dim_unread and len(getattr(self, "subs", [])):
            n = len(self.tiles)
            out += [m.animate.set_opacity(self.unread_opacity) for m in self.subs
                    if self._tile_of(m) not in self.read]
        if getattr(self, "caret", None) is not None:
            out.append(self.caret.animate.set_stroke(opacity=0))
        if self.stop_mark and self.order:
            last = [self.tiles[k] for k in self.order[-self.stop_mark:]]
            g = VGroup(*last)
            ring = RoundedRectangle(width=g.width + 0.22, height=g.height + 0.22,
                                    corner_radius=min(0.14, self.radius + 0.08)).move_to(g)
            ring.set_fill(opacity=0).set_stroke(ManimColor(self.stop_color), width=3)
            from manim import Create
            out.append(Create(ring, rate_func=rate_functions.ease_in_out_cubic))
        return out

    def _tile_of(self, m):
        x = m.get_center()[0]
        return min(range(len(self.tiles)), key=lambda k: abs(self.tiles[k].get_center()[0] - x))

    def take(self, i):
        """The tile for word i is used: it becomes a ghost. Returns (copy to fly, animation)."""
        t = self.tiles[i]
        self.used.add(i)
        ghost = t.copy()
        return ghost, t.animate.set_opacity(self.used_opacity)


@dataclass
class LineComposer:
    line: str = "cur"                             # the list holding the current line's words
    out: str = "res"                              # the list of finished lines (strings)
    width: str = "maxWidth"                       # variable holding the measure, in characters
    source: Optional[str] = "words"               # the WordStrip words come from
    position: Tuple[float, float] = (0.0, -1.2)
    size: Tuple[float, float] = (12.6, 4.4)       # the page is fitted inside this box
    paper: Optional[str] = "#d862a9"
    paper_margin: float = 0.4
    tile: str = "#f7f1c9"
    ink: str = "#1b1b3a"
    committed_tile: Optional[str] = None          # tile color once a line is committed (None = same)
    font: str = "IBM Plex Mono"
    space: str = "#1e9476"                        # dot color for a real space
    pending_space: str = "#1b1b3a"                # hollow dot where a space is still required
    margin_color: str = "#f7f1c9"
    ruler: bool = True
    push_time: float = 0.55
    space_time: float = 0.2
    commit_time: float = 0.5

    # ---------------------------------------------------------------- setup
    def watch(self):
        return [self.width]

    def plan(self, scene, events):
        self.cols = next((e["value"] for e in events if e["type"] == "var" and e["name"] == self.width), 16)
        self.rows = max(1, sum(1 for e in events if e["type"] == "push" and e.get("list") == self.out))
        W, H = self.size
        self.cw = min(W / self.cols, H / self.rows / 1.75)
        self.rh = self.cw * 1.75
        self.x0 = self.position[0] - self.cols * self.cw / 2
        self.y0 = self.position[1] + self.rows * self.rh / 2
        g = VGroup()
        if self.paper:
            m = self.paper_margin
            paper = Rectangle(width=self.cols * self.cw + 2 * m, height=self.rows * self.rh + 2 * m)
            paper.move_to([*self.position, 0]).set_fill(ManimColor(self.paper), opacity=1).set_stroke(width=0)
            g.add(paper)
        for x in (self.x0, self.x0 + self.cols * self.cw):        # the measure: both margins
            g.add(Line([x, self.y0 + 0.12, 0], [x, self.y0 - self.rows * self.rh - 0.12, 0],
                       color=ManimColor(self.margin_color), stroke_width=2.5).set_opacity(0.85))
        if self.ruler:
            for c in range(self.cols + 1):
                tall = 0.12 if c % 5 == 0 else 0.06
                g.add(Line([self.x0 + c * self.cw, self.y0 + 0.14, 0], [self.x0 + c * self.cw, self.y0 + 0.14 + tall, 0],
                           color=ManimColor(self.margin_color), stroke_width=1.5).set_opacity(0.7))
        self.static = g
        self.row = 0
        self.strs, self.tiles, self.dots = [], [], []
        self.committed = []
        self.strip = next((h for h in scene.S.handlers if isinstance(h, WordStrip) and h.name == self.source), None)
        return g

    def wants(self, e):
        return (e.get("list") == self.line and e["type"] in ("create", "push", "set")) or \
               (e.get("list") == self.out and e["type"] == "push")

    def intro(self, scene, e):
        return []

    # ------------------------------------------------------------- layout
    def cell_center(self, row, col):
        return np.array([self.x0 + (col + 0.5) * self.cw, self.y0 - (row + 0.5) * self.rh, 0.0])

    def layout(self, strs):
        """Word start columns, real space columns, and pending (required) space columns."""
        starts, real, pending, col = [], [], [], 0
        for i, s in enumerate(strs):
            word = s.rstrip(" ")
            trail = len(s) - len(word)
            starts.append(col); col += len(word)
            real += list(range(col, col + trail)); col += trail
            if trail == 0 and i < len(strs) - 1:
                pending.append(col); col += 1
        return starts, real, pending

    def layout_string(self, s):
        starts, real, col = [], [], 0
        while col < len(s):
            if s[col] == " ":
                real.append(col); col += 1
            else:
                starts.append(col)
                while col < len(s) and s[col] != " ":
                    col += 1
        return starts, real

    def word_target(self, word, row, start):
        w = len(word) * self.cw
        c = self.cell_center(row, start)
        return np.array([c[0] - self.cw / 2 + w / 2, c[1], 0.0])

    def make_tile(self, word, fill=None):
        return _tile(word, len(word) * self.cw - self.cw * 0.18, self.rh * 0.72, fill or self.tile,
                     self.ink, self.font, 0.05, char_w=self.cw)

    def dot(self, row, col, real):
        d = Circle(radius=self.cw * 0.12).move_to(self.cell_center(row, col) + DOWN * self.rh * 0.0)
        if real:
            d.set_fill(ManimColor(self.space), opacity=1).set_stroke(width=0)
        else:
            d.set_fill(opacity=0).set_stroke(ManimColor(self.pending_space), width=2, opacity=0.8)
        return d

    def relayout(self, scene, starts, real, pending):
        """Animations that move this row's tiles and dots to a new layout."""
        anims = []
        for t, s in zip(self.tiles, starts):
            anims.append(t.animate(rate_func=rate_functions.ease_in_out_cubic)
                         .move_to(self.word_target(t.word, self.row, s)))
        new_dots = [self.dot(self.row, c, True) for c in real] + [self.dot(self.row, c, False) for c in pending]
        old = self.dots
        # match dots by position so existing ones slide; new ones pop in
        for k, nd in enumerate(new_dots):
            if k < len(old):
                anims.append(old[k].animate(rate_func=rate_functions.ease_in_out_cubic).become(nd))
            else:
                scene.add(nd); nd.scale(0.01)
                anims.append(nd.animate(rate_func=rate_functions.ease_out_back).scale(100))
                old.append(nd)
        for extra in old[len(new_dots):]:
            anims.append(extra.animate.scale(0.01).set_opacity(0))
        self.dots = old[:len(new_dots)]
        return anims

    # -------------------------------------------------------------- events
    def handle(self, scene, e):
        t, sp = e["type"], scene.S.timing.speed
        if e.get("list") == self.line and t == "create":
            self.strs, self.tiles, self.dots = [str(v) for v in e.get("values") or []], [], []
            return
        if e.get("list") == self.line and t == "push":
            word = str(e["value"])
            self.strs.insert(e["index"], word)
            starts, real, pending = self.layout(self.strs)
            tile = self.make_tile(word)
            tile.move_to(self.word_target(word, self.row, starts[e["index"]]))
            anims = []
            src = e.get("src") or {}
            if self.strip is not None and src.get("list") == self.strip.name and src.get("index") is not None:
                ghost, fade = self.strip.take(src["index"])
                scene.add(ghost)
                anims += [ReplacementTransform(ghost, tile, rate_func=rate_functions.ease_in_out_cubic), fade]
            else:
                anims.append(FadeIn(tile, scale=0.8))
            self.tiles.insert(e["index"], tile)
            anims += self.relayout(scene, starts, real, pending)
            scene.note(deg=2 + len(word) % 10, gain=-4)
            scene.play(*anims, run_time=self.push_time / sp)
            return
        if e.get("list") == self.line and t == "set":
            j = e["index"]
            if j < len(self.strs):
                self.strs[j] = str(e["value"])
            starts, real, pending = self.layout(self.strs)
            anims = self.relayout(scene, starts, real, pending)
            self._spaces = getattr(self, "_spaces", 0) + 1
            scene.note(deg=4 + (j * 2) % 10, instrument="music_box", gain=-9)
            scene.play(*anims, run_time=self.space_time / sp)
            return
        if e.get("list") == self.out and t == "push":
            s = str(e["value"])
            starts, real = self.layout_string(s)
            anims = []
            if len(starts) == len(self.tiles):
                anims += self.relayout(scene, starts, real, [])
            if self.committed_tile:
                anims += [tl[0].animate.set_fill(ManimColor(self.committed_tile)) for tl in self.tiles]
            # the line locks to the measure: a quick glint along its right edge
            edge = Line(self.cell_center(self.row, self.cols - 1) + RIGHT * self.cw / 2 + UP * self.rh * 0.4,
                        self.cell_center(self.row, self.cols - 1) + RIGHT * self.cw / 2 + DOWN * self.rh * 0.4,
                        color=ManimColor(self.margin_color), stroke_width=6)
            scene.add(edge)
            anims.append(edge.animate(rate_func=there_and_back).set_stroke(width=14))
            scene.note(deg=9 + self.row % 5, instrument=scene.S.sound_cfg.finale_instrument, gain=-4)
            scene.play(*anims, run_time=self.commit_time / sp)
            scene.remove(edge)
            self.committed.append((self.tiles, self.dots))
            self.row += 1
            self.tiles, self.dots, self.strs = [], [], []

    def finish(self, scene):
        """A slow wave down the finished page."""
        rows = [VGroup(*tiles) for tiles, _ in self.committed if tiles]
        return [LaggedStart(*[r.animate(rate_func=there_and_back).shift(0.06 * RIGHT) for r in rows], lag_ratio=0.25)]
