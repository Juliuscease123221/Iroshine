"""
LeetCode 749 — Contain Virus (hard), in DARK CHERRY.

Each night:
  1. scan every cell; a cell lights up when the program reads it (dim = not known yet)
  2. an infected cell that hasn't been seen starts a BFS: the region is outlined,
     and the clean cells it threatens get a dot
  3. already-seen cells are just scanned past
  4. the region threatening the most cells is walled off (walls = its perimeter,
     not counting the grid's edge), and every other region spreads one step
  5. knowledge resets (`seen = set()`), and the next night begins

The answer is the number of walls built.

New library pieces used here:
  GridView    a 2-D list drawn as cells; color comes from the value, knowledge from reads
  Mark        how members of a named set ("region", "frontier") are drawn on the grid
  Walls       walls on every edge between a contained cell (-1) and a clean one (0)
  forget_when re-creating `seen` makes the whole grid unknown again
"""

import random
import sys
from collections import deque

from manim import MarkupText

from iroshine import (DARK_CHERRY as P, Finale, Grain, GridView, Mark, Readout, Sound, Stage,
                     Timing, Walls)


class Solution:
    def containVirus(self, isInfected):
        R, C = len(isInfected), len(isInfected[0])
        ans = 0
        while True:
            seen = set()
            regions, frontiers, perimeters = [], [], []
            for r in range(R):
                for c in range(C):
                    if isInfected[r][c] == 1 and (r, c) not in seen:
                        region, frontier, walls = set(), set(), 0
                        queue = deque([(r, c)])
                        seen.add((r, c))
                        while queue:
                            cr, cc = queue.popleft()
                            region.add((cr, cc))
                            for nr, nc in ((cr + 1, cc), (cr - 1, cc), (cr, cc + 1), (cr, cc - 1)):
                                if 0 <= nr < R and 0 <= nc < C:
                                    if isInfected[nr][nc] == 1 and (nr, nc) not in seen:
                                        seen.add((nr, nc))
                                        queue.append((nr, nc))
                                    elif isInfected[nr][nc] == 0:
                                        frontier.add((nr, nc))
                                        walls += 1
                        regions.append(region)
                        frontiers.append(frontier)
                        perimeters.append(walls)
            if not regions:
                break
            worst = max(range(len(regions)), key=lambda k: len(frontiers[k]))
            if not frontiers[worst]:
                break
            ans += perimeters[worst]
            for k, region in enumerate(regions):
                if k == worst:
                    for r, c in region:
                        isInfected[r][c] = -1          # contained
                else:
                    for r, c in frontiers[k]:
                        isInfected[r][c] = 1           # the virus spreads
        return ans


def make_grid(seed, R=9, C=15, seeds=5):
    rnd = random.Random(seed)
    g = [[0] * C for _ in range(R)]
    for _ in range(seeds):
        r, c = rnd.randrange(R), rnd.randrange(C)
        for dr, dc in ((0, 0), (0, 1), (1, 0), (1, 1), (0, -1))[:rnd.randint(1, 4)]:
            if 0 <= r + dr < R and 0 <= c + dc < C:
                g[r + dr][c + dc] = 1
    return g


CLEAN, INFECTED, CONTAINED = "#277879", "#c04f7c", "#3a1a4a"

stage = Stage(
    background=P.sky, resolution=(3840, 2160), fps=60, crf=14, grain=Grain(7),
    sound=Sound(scale="dorian", key="C", octave=4, instrument="harp", finale_instrument="bell", reverb=0.45),
    timing=Timing(speed=1.25, end_hold=3),
    finale=Finale(target=None, color=P.accent),
)

stage.add(
    MarkupText('<span letter_spacing="3000">CONTAIN VIRUS</span>', font="Inter", weight="LIGHT",
               font_size=18, color=P.text).move_to([-6.6, 3.55, 0], aligned_edge=[-1, 0, 0]),
    MarkupText('<span letter_spacing="1600">749 · BFS · GREEDY</span>', font="IBM Plex Mono",
               font_size=12, color=P.muted).move_to([6.6, 3.55, 0], aligned_edge=[1, 0, 0]),

    GridView("isInfected", position=(-1.35, -0.3), size=(10.6, 6.4),
             colors={0: CLEAN, 1: INFECTED, -1: CONTAINED}, gap=0.1,
             unknown=0.78, unknown_color="#150a22", forget_when="seen",
             flash=P.text, flash_opacity=0.55, rate=55, step=0.3,
             marks={"region":   Mark(stroke="#f0d3e2", stroke_width=3, shape="ring", inset=0.08,
                                     keep=True, kept_opacity=0.5),
                    "frontier": Mark(fill=P.accent, shape="dot", keep=True, kept_opacity=0.6)},
             walls=Walls(between=(-1, 0), color=P.accent, width=7)),

    Readout("ans", position=(4.55, 1.9), label="walls built", font_size=84,
            color=P.text, label_color=P.muted),
    Readout("walls", position=(4.55, -0.35), label="perimeter", font_size=44,
            color=P.muted, label_color=P.muted),
)

GRID = make_grid(int(sys.argv[2]) if len(sys.argv) > 2 else 0)
stage.run(Solution().containVirus, GRID)

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "medium"
    stage.render("12_dark_cherry_contain_virus.mp4", quality=q)
