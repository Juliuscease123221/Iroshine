"""
LeetCode 587 — Erect the Fence (hard), in ELYSIUM.

Andrew's monotone chain: sort the trees left to right, then walk them twice —
once along the bottom, once back along the top — keeping a stack of fence posts.
A dashed feeler reaches from the last post to each new tree; whenever the new tree
would make the fence turn inward, the last post is pulled up (the segment retracts).
Trees exactly on the fence line stay (cross == 0 is allowed), as the problem asks.

New library pieces:
  PointSet   a list of [x, y] drawn as dots; sorting recolors them by their new order
  Polyline   a list used as a stack of points, drawn as a path that grows and retracts
"""

import random
import sys

from manim import MarkupText, Rectangle

from iroshine import ELYSIUM as P, Finale, Gradient, Grain, PointSet, Polyline, Sound, Stage, Timing


class Solution:
    def outerTrees(self, trees):
        def cross(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        trees.sort()
        hull = []
        for p in trees:                                   # lower fence, left → right
            while len(hull) >= 2 and cross(hull[-2], hull[-1], p) < 0:
                hull.pop()
            hull.append(p)
        for p in reversed(trees):                         # upper fence, right → left
            while len(hull) >= 2 and cross(hull[-2], hull[-1], p) < 0:
                hull.pop()
            hull.append(p)
        return [list(t) for t in {tuple(t) for t in hull}]


def make_trees(seed, n=26):
    rnd = random.Random(seed)
    pts = set()
    while len(pts) < n:
        pts.add((rnd.randint(0, 40), rnd.randint(0, 22)))
    pts.update({(0, 11), (40, 5), (20, 0), (10, 0)})      # a few on the boundary lines
    return [list(p) for p in pts]


INK = P.outline
stage = Stage(
    background=P.sky, resolution=(3840, 2160), fps=60, crf=14, grain=Grain(7),
    sound=Sound(scale="pentatonic", key="G", octave=4, instrument="marimba", finale_instrument="bell",
                reverb=0.4),
    timing=Timing(speed=1.35, end_hold=3),
    finale=Finale(target=None),
)
stage.add(
    Rectangle(width=13.7, height=7.5).set_stroke(INK, width=2).set_fill(opacity=0),
    MarkupText('<span letter_spacing="3000">ERECT THE FENCE</span>', font="Inter",
               font_size=18, color=P.text).move_to([-6.45, 3.35, 0], aligned_edge=[-1, 0, 0]),
    MarkupText('<span letter_spacing="1600">587 · MONOTONE CHAIN</span>', font="IBM Plex Mono",
               font_size=12, color=P.muted).move_to([6.45, 3.35, 0], aligned_edge=[1, 0, 0]),

    PointSet("trees", position=(0, -0.3), size=(12.6, 6.3), radius=0.11,
             fill=Gradient(("#93b4c6", 0.0), ("#86bf8e", 0.45), ("#b4d68f", 0.75), ("#e8e2b8", 1.0), by="index"),
             stroke=INK, stroke_width=1.5, focus="p", focus_color=INK),
    Polyline("hull", on="trees", color=INK, width=4, vertex_radius=0.13, vertex_color=INK,
             probe="p", probe_color=INK, probe_opacity=0.45, fill="#86bf8e", fill_opacity=0.35,
             push_time=0.45, pop_time=0.4),
)

stage.run(Solution().outerTrees, make_trees(int(sys.argv[2]) if len(sys.argv) > 2 else 4))

if __name__ == "__main__":
    stage.render("14_elysium_erect_the_fence.mp4", quality=sys.argv[1] if len(sys.argv) > 1 else "medium")
