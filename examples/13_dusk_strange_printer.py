"""
LeetCode 1591 — Strange Printer II (hard), in DUSK.

The printer prints one solid rectangle per color, each color once, later prints
covering earlier ones. Can it produce the target?

  1. scan the target: each color's bounding box grows as its extent is discovered
  2. scan inside each box: any other color found there must be printed *after* it —
     that's an edge in the dependency graph (drawn as an arc diagram below)
  3. topological sort: a color with nothing left underneath it gets printed —
     stamped onto the blank printer canvas — and its edges fade
  4. if every color gets printed, the canvas now matches the target

New library pieces:
  GridView(colors={...})      categorical colors per value
  GridView(like="targetGrid") a blank canvas with the same shape
  GridBoxes                   bounding boxes from four parallel arrays (top/bottom/left/right)
  GraphView                   nodes + edges from an adjacency list of sets, as an arc diagram
  Stamp                       a solid block printed onto a grid whenever a variable changes
"""

import random
import sys
from collections import deque

from manim import MarkupText

from iroshine import (DUSK as P, Finale, Grain, GraphView, GridBoxes, GridView, Readout, Sound, Stage,
                     Stamp, Timing)


class Solution:
    def isPrintable(self, targetGrid):
        m, n = len(targetGrid), len(targetGrid[0])
        top, bottom = [m] * 61, [-1] * 61
        left, right = [n] * 61, [-1] * 61
        for i in range(m):
            for j in range(n):
                c = targetGrid[i][j]
                top[c] = min(top[c], i)
                bottom[c] = max(bottom[c], i)
                left[c] = min(left[c], j)
                right[c] = max(right[c], j)
        colors = [c for c in range(61) if bottom[c] >= 0]
        graph = [set() for _ in range(61)]
        for c in colors:
            for i in range(top[c], bottom[c] + 1):
                for j in range(left[c], right[c] + 1):
                    d = targetGrid[i][j]
                    if d != c:
                        graph[c].add(d)          # d is printed on top of c
        indeg = [0] * 61
        for c in colors:
            for d in graph[c]:
                indeg[d] += 1
        queue = deque(c for c in colors if indeg[c] == 0)
        printed = 0
        while queue:
            layer = queue.popleft()
            printed += 1
            for d in graph[layer]:
                indeg[d] -= 1
                if indeg[d] == 0:
                    queue.append(d)
        return printed == len(colors)


def make_target(seed, m=10, n=14, k=7):
    """Print k random rectangles over a full base layer, so the answer is True."""
    rnd = random.Random(seed)
    g = [[1] * n for _ in range(m)]
    for c in range(2, k + 2):
        h, w = rnd.randint(3, m - 2), rnd.randint(4, n - 3)
        r, q = rnd.randint(0, m - h), rnd.randint(0, n - w)
        for i in range(r, r + h):
            for j in range(q, q + w):
                g[i][j] = c
    return g


LAYERS = {1: "#2c2240", 2: "#4b1d95", 3: "#8e2c8a", 4: "#e2483a", 5: "#f2873f",
          6: "#f4e3a0", 7: "#5fbf9f", 8: "#ece6d8"}

stage = Stage(
    background=P.sky, resolution=(3840, 2160), fps=60, crf=14, grain=Grain(7),
    sound=Sound(scale="pentatonic", key="D", octave=4, instrument="harp", finale_instrument="bell", reverb=0.45),
    timing=Timing(end_hold=3),
    finale=Finale(target=None, color=P.accent, text="printable", text_position=(3.55, -1.72),
                  font="Inter", font_size=20),
)

label = lambda text, x: MarkupText(f'<span letter_spacing="2400">{text}</span>', font="Inter", font_size=12,
                                   color=P.muted).move_to([x, 3.28, 0], aligned_edge=[-1, 0, 0])
stage.add(
    MarkupText('<span letter_spacing="3000">STRANGE PRINTER II</span>', font="Inter", weight="LIGHT",
               font_size=18, color=P.text).move_to([-6.6, 3.62, 0], aligned_edge=[-1, 0, 0]),
    MarkupText('<span letter_spacing="1600">1591 · BOUNDING BOXES · TOPOLOGICAL SORT</span>',
               font="IBM Plex Mono", font_size=12, color=P.muted).move_to([6.6, 3.62, 0], aligned_edge=[1, 0, 0]),
    label("TARGET", -6.75), label("PRINTER", 0.35),

    GridView("targetGrid", position=(-3.55, 0.85), size=(6.4, 4.6), colors=LAYERS, gap=0.07,
             unknown=0.85, unknown_color="#000000", flash="#ffffff", flash_opacity=0.6, rate=45, step=0.35),
    GridView("printer", like="targetGrid", position=(3.55, 0.85), size=(6.4, 4.6), colors=LAYERS,
             gap=0.07, blank_color="#131018", unknown=None, flash=None),

    GridBoxes(on="targetGrid", stroke_width=4),
    GraphView("graph", position=(0, -2.75), size=(9.0, 1.0), node_colors="grid:targetGrid",
              node_radius=0.24, label_color="#000000", edge_color=P.text, edge_opacity=0.32, edge_width=2, arc=0.9,
              done_when="layer", dim=0.75),
    Stamp(on="printer", when="layer", rows=("top[layer]", "bottom[layer]"),
          cols=("left[layer]", "right[layer]"), value="layer", duration=0.9),

    Readout("printed", position=(-6.6, -2.75), label="layers printed", font_size=40,
            color=P.text, label_color=P.muted),
)

stage.run(Solution().isPrintable, make_target(int(sys.argv[2]) if len(sys.argv) > 2 else 0))

if __name__ == "__main__":
    stage.render("13_dusk_strange_printer.mp4", quality=sys.argv[1] if len(sys.argv) > 1 else "medium")
