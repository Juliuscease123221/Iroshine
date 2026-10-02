"""
iroshine.story — short on-screen captions that tell the story of a run.

Beats([...]) is a list of short phrases shown one at a time, large and centered,
each appearing when the code reaches a certain line or does a certain thing:

    Beats([
        Beat("Fence in every tree.", at="start"),
        Beat("sort left to right",  at="trees.sort()"),        # a piece of a line of your code
        Beat("pull back inward turns", on="pop", list="hull"),  # the first time something happens
        Beat("walk back over the top", at="reversed(trees)"),
        Beat("the shortest fence",   at="end"),
    ])

Made for short-form video (captions are what people read with the sound off), but
works anywhere. With loop=True the story returns to its first beat at the very end,
so the last frame matches the first and the video loops cleanly.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from manim import UP, FadeIn, FadeOut, LaggedStart, ManimColor, Text, VGroup, rate_functions


@dataclass
class Beat:
    text: str
    at: Optional[str] = None          # "start", "end", or a piece of source code (fires when that line runs)
    on: Optional[str] = None          # or an event type: "pop", "push", "swap", "set", "replace", ...
    list: Optional[str] = None        # ...on this list only
    sub: Optional[str] = None         # a smaller second line under the text
    color: Optional[str] = None       # override the text color for this beat


@dataclass
class Beats:
    beats: List[Beat] = field(default_factory=list)
    position: Tuple[float, float] = (0.0, 2.0)   # center of the text block
    width: float = 3.6                            # wrap long phrases to this width
    font: str = "Inter"
    weight: str = "MEDIUM"
    font_size: float = 30
    color: str = "#ffffff"
    sub_font: str = "IBM Plex Mono"
    sub_size: float = 15
    sub_color: str = "#bbbbbb"
    word_lag: float = 0.12                        # words appear one after another
    duration: float = 0.45
    loop: bool = False                            # at the very end, return to the first beat
    chime: bool = True                            # a soft note as each phrase appears

    # -------------------------------------------------------------- setup
    def setup(self, scene):
        src = (scene.S.source or "").splitlines()
        self.lines = {}
        for b in self.beats:
            if b.at not in (None, "start", "end"):
                self.lines[id(b)] = {k + 1 for k, s in enumerate(src) if b.at in s}
        self.fired, self.current = set(), None

    def _make(self, b):
        space = self.font_size / 48 * 0.22
        words = [Text(w, font=self.font, weight=self.weight, font_size=self.font_size,
                      color=ManimColor(b.color or self.color)) for w in b.text.split()]
        widths = [w.width for w in words]

        def width(a, z):
            return sum(widths[a:z]) + space * (z - a - 1)

        # balanced wrapping: the fewest lines that fit, with line lengths as even as possible
        # (no lonely last word)
        n = len(words)
        best = [(0, n)]
        if width(0, n) > self.width:
            for lines in range(2, n + 1):
                cands = []

                def split(start, left, acc):
                    if left == 1:
                        if width(start, n) <= self.width:
                            cands.append(acc + [(start, n)])
                        return
                    for z in range(start + 1, n - left + 2):
                        if width(start, z) <= self.width:
                            split(z, left - 1, acc + [(start, z)])
                split(0, lines, [])
                if cands:
                    best = min(cands, key=lambda c: max(width(a, z) for a, z in c) - min(width(a, z) for a, z in c))
                    break
        lines = VGroup()
        for a, z in best:                                 # one Text per line keeps a true shared baseline;
            ws = b.text.split()[a:z]                       # its glyphs are then grouped back into words
            t = Text(" ".join(ws), font=self.font, weight=self.weight, font_size=self.font_size,
                     color=ManimColor(b.color or self.color))
            glyphs, k, row = list(t.submobjects), 0, VGroup()
            for w in ws:
                row.add(VGroup(*glyphs[k:k + len(w)])); k += len(w)
            lines.add(row)
        lines.arrange(direction=[0, -1, 0], buff=self.font_size / 48 * 0.16)
        block = VGroup(lines)
        if b.sub:
            s = Text(b.sub, font=self.sub_font, font_size=self.sub_size, color=ManimColor(self.sub_color))
            s.next_to(lines, [0, -1, 0], buff=0.18)
            block.add(s)
        block.move_to([*self.position, 0])
        block.words = [w for g in lines for w in g] + ([block[1]] if b.sub else [])
        return block

    def _swap(self, scene, b, instant=False):
        new = self._make(b)
        old, self.current = self.current, new
        if instant:
            if old is not None:
                scene.remove(old)
            scene.add(new)
            return []
        anims = []
        if old is not None:                               # the old phrase leaves in the first third
            anims.append(FadeOut(old, shift=0.12 * UP,
                                 rate_func=lambda t: rate_functions.ease_in_cubic(min(1.0, t * 3))))
        late = (lambda t: rate_functions.ease_out_cubic(max(0.0, (t - 0.3) / 0.7))) if old is not None \
            else rate_functions.ease_out_cubic
        anims.append(LaggedStart(*[FadeIn(w, shift=0.1 * UP, rate_func=late) for w in new.words],
                                 lag_ratio=self.word_lag))
        return anims

    def _chime(self, scene, k):
        if self.chime and scene.synth:
            top = 2 * len(scene.synth.steps)
            scene.note(deg=top - (k % 3), instrument="soft_sine", gain=-13)

    def play(self, scene, b):
        self._chime(scene, len(self.fired))
        anims = self._swap(scene, b)
        n = len(self.current.words)
        scene.play(*anims, run_time=(self.duration + 0.06 * n) / scene.S.timing.speed)

    # ---------------------------------------------------------- the story
    def start(self, scene, instant):
        for b in self.beats:
            if b.at == "start":
                self.fired.add(id(b))
                if instant:
                    self._chime(scene, 0)
                    self._swap(scene, b, instant=True)
                else:
                    self.play(scene, b)
                return

    def observe(self, scene, e):
        for b in self.beats:
            if id(b) in self.fired or b.at in ("start", "end"):
                continue
            hit = False
            if b.at is not None and e.get("line") in self.lines.get(id(b), ()):
                hit = True
            if b.on is not None and e["type"] == b.on and (b.list is None or e.get("list") == b.list):
                hit = True
            if hit:
                self.fired.add(id(b))
                self.play(scene, b)
                return

    def end(self, scene):
        for b in self.beats:
            if b.at == "end":
                self.play(scene, b)
                return

    def unwind(self, scene):
        """Animations that return to the first beat (for a clean loop)."""
        first = next((b for b in self.beats if b.at == "start"), None)
        if not self.loop or first is None:
            return []
        return self._swap(scene, first)
