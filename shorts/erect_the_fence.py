"""
REELS (tall) — LeetCode 587 · Erect the Fence: code + no graph lines + moss fence, laid out from
a real screenshot of the Reel on a phone.

What the screenshot showed (phone 787×1548 → the 1080×1920 video is scaled ×0.806 to fill the
height, so about 52 video px are cropped off each side):
  · the like / comment / share buttons start around y ≈ 1230 px, not 1110
  · the username + caption start around y ≈ 1700 px, so there was free room below the code
So the fence area is now much taller (a taller set of trees to match), the code sits lower, and
"made with iroshine" sits just above the username.
"""

import os
import random
import sys

from manim import MarkupText

from iroshine import ELYSIUM as P, CodePanel, Finale, Gradient, PointSet, Polyline, Sound, Stage, Timing


class Solution:
    def outerTrees(self, trees):
        def cross(o, a, b):
            return ((a[0] - o[0]) * (b[1] - o[1]) -
                    (a[1] - o[1]) * (b[0] - o[0]))

        trees.sort()
        hull = []
        for p in trees + trees[::-1]:
            while len(hull) > 1 and cross(*hull[-2:], p) < 0:
                hull.pop()
            hull.append(p)
        return [list(t) for t in {tuple(t) for t in hull}]


def make_trees(seed=5):
    """The very first data set (from short #1): 11 random trees plus 4 on the edges."""
    rnd = random.Random(seed)
    pts = set()
    while len(pts) < 11:
        pts.add((rnd.randint(1, 19), rnd.randint(1, 15)))
    pts.update({(0, 8), (20, 6), (10, 0), (9, 16)})
    return [list(p) for p in pts]


from tree_sets import SETS               # candidate layouts; TREESET=0 uses make_trees() above
CHOSEN = 5                               # the picked layout (a ring-like scatter, 9 fence posts)
_pick = int(os.environ.get("TREESET", CHOSEN))
TREES = make_trees() if _pick == 0 else [list(t) for t in SETS[_pick - 1]]


INK = P.outline
FENCES = {                       # OKLCH (L 0.33, C 0.06) at three palette hues, plus the original ink
    "blue":   ("#0b3a4f", "#93b4c6"),   # hue 232: the pool
    "forest": ("#1e3e23", "#86bf8e"),   # hue 148: the leaf
    "teal":   ("#003f3c", "#8fc3b8"),   # hue 190: between them
    "moss":   ("#2e3e17", "#b4d68f"),   # hue 128: a warmer green, toward the spring green (L 0.34, C 0.065)
    "ink":    (INK, "#86bf8e"),
}
FENCE, FILL = FENCES[sys.argv[2] if len(sys.argv) > 2 else "moss"]

# Instagram Reels safe zone (1080×1920 reference): 250 px clear at the top, 420 px at the bottom,
# 70 px on the left, 55 px on the right down to y = 1110 px, then 193 px on the right (the like /
# comment / share buttons). The scene is 4.5 × 8 units, so 240 px = 1 unit.
PX = 240
def X(px): return px / PX - 2.25
def Y(px): return 4 - px / PX

LEFT = X(70) + 0.03                   # -1.93
RIGHT_TOP = X(1080 - 70) - 0.03       #  1.93  (above the buttons; mirrors the left margin — phones crop the sides)
RIGHT_LOW = X(1080 - 193) - 0.03      #  1.42  (beside the buttons)
TOP, BOTTOM = Y(250), Y(1920 - 420)   #  2.96, -2.25

stage = Stage(
    background=P.sky, resolution=(1080, 1920), fps=60, crf=16, grain=None,
    sound=Sound(scale="pentatonic", key="G", octave=2, reverb=0.18,
                instrument="wood", finale_instrument="log_drum",
                soft_instrument="wood_soft", tick_instrument="wood_soft"),
    timing=Timing(speed=1.8, end_hold=0.5, intro="instant"),
    finale=Finale(target=None),
)
code_w = RIGHT_LOW - LEFT
stage.add(
    MarkupText('<span letter_spacing="2400">ERECT THE FENCE</span>', font="Inter", weight="MEDIUM",
               font_size=12, color=P.text).move_to([LEFT + 0.04, TOP - 0.32, 0], aligned_edge=[-1, 0, 0]),
    MarkupText('<span letter_spacing="1400">LEETCODE 587 · HARD</span>', font="IBM Plex Mono",
               font_size=8, color=P.muted).move_to([LEFT + 0.04, TOP - 0.54, 0], aligned_edge=[-1, 0, 0]),

    MarkupText('<span letter_spacing="1400">MADE WITH IROSHINE</span>', font="IBM Plex Mono",
               font_size=8, color=P.muted).move_to([LEFT + 0.04, -2.9, 0], aligned_edge=[-1, 0, 0]),

    PointSet("trees", position=((LEFT + RIGHT_TOP) / 2, 0.62), size=(RIGHT_TOP - LEFT - 0.4, 3.0), radius=0.078,
             fill=Gradient(("#93b4c6", 0.0), ("#86bf8e", 0.45), ("#b4d68f", 0.75), ("#e8e2b8", 1.0), by="index"),
             stroke=INK, stroke_width=1.1, focus="p", focus_color=FENCE),
    Polyline("hull", on="trees", color=FENCE, width=2.8, vertex_radius=0.084, vertex_color=FENCE,
             probe="p", probe_color=FENCE, probe_opacity=0.45, fill=FILL, fill_opacity=0.35,
             push_time=0.45, pop_time=0.4, ghost=True, ghost_opacity=0.28, loop=True),
    CodePanel(position=(LEFT + code_w / 2, -1.9), width=code_w, style="friendly", background="#f3f6ec",
              highlight=FILL, highlight_opacity=0.4, line_numbers=False,
              glide=True, glide_speed=10, span="loop", corner_radius=0.1, padding=0.18),
)

stage.run(Solution().outerTrees, [list(t) for t in TREES])

if __name__ == "__main__":
    stage.render(f"erect_the_fence_set{_pick}.mp4", quality=sys.argv[1] if len(sys.argv) > 1 else "high")
