"""
LeetCode 324 — Wiggle Sort II (medium), in ELYSIUM.

Sort a copy, then deal it back out: evens take the small half from the top down,
odds take the big half from the top down, so nums[0] < nums[1] > nums[2] < ...
Every value flies down into the sorted copy, then back up to its wiggle slot.
"""

import random

from manim import MarkupText, Rectangle

from iroshine import ELYSIUM as P, Axis, BarList, BarStyle, Finale, Grain, Labels, Motion, Sound, Stage, Timing


class Solution:
    def wiggleSort(self, nums):
        s = list(sorted(nums))
        n = len(nums)
        j, k = (n + 1) // 2 - 1, n - 1
        for i in range(n):
            if i % 2 == 0:
                nums[i] = s[j]
                j -= 1
            else:
                nums[i] = s[k]
                k -= 1


ink = dict(stroke=P.outline, stroke_width=2)
names = Labels(color=P.text, name_size=14)
ground = Axis(ground=0.28, ground_color=P.ground, ground_stroke=P.outline)

stage = Stage(
    background=P.sky, resolution=(3840, 2160), fps=60, crf=14, grain=Grain(7),
    sound=Sound(scale="pentatonic", key="G", instrument="marimba", reverb=0.4, landing_interval=3),
    timing=Timing(skip=("read", "compare"), end_hold=3),
    finale=Finale(target="nums", style="sweep", color=P.accent),
)
stage.add(
    Rectangle(width=13.7, height=7.5).set_stroke(P.outline, width=2).set_fill(opacity=0),
    MarkupText('<span letter_spacing="3000">WIGGLE SORT II</span>', font="Inter",
               font_size=20, color=P.text).move_to([-6.45, 3.35, 0], aligned_edge=[-1, 0, 0]),
    MarkupText('<span letter_spacing="1600">324 · SORT, THEN INTERLEAVE</span>', font="IBM Plex Mono",
               font_size=13, color=P.muted).move_to([6.45, 3.35, 0], aligned_edge=[1, 0, 0]),
    BarList("nums", position=(0, 1.05), size=(12.6, 2.9), padding=0, labels=names, axis=ground, panel=None,
            bar=BarStyle(fill=P.gradient(by="rank"), gap=0, outer_gap=0, **ink)),
    BarList("s", title="sorted", position=(0, -2.25), size=(12.6, 2.6), padding=0, labels=names,
            axis=ground, panel=None, bar=BarStyle(fill=P.gradient(by="rank"), gap=0, outer_gap=0, **ink)),
)
stage.motion(
    push=Motion(path="straight", easing="ease_in_out_cubic", duration=0.8, lag=0.12),
    set=Motion(path="straight", easing="ease_in_out_cubic", duration=0.6),
)

random.seed(8)
stage.run(Solution().wiggleSort, random.sample(range(4, 60), 24))

if __name__ == "__main__":
    import sys
    stage.render("09_elysium_wiggle_sort.mp4", quality=sys.argv[1] if len(sys.argv) > 1 else "high")
