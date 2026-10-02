"""
Example 6 — "elysium": quicksort in the sage-and-mint poster palette.

  · a gradient with positioned stops, blended in OKLab:
        blue 0.0 → leaf 0.30 → spring 0.58 → putty 0.80 → cream 1.0
  · touching bars (gap=0) outlined in thin ink, so they tile like the poster's shapes
  · ink-outlined green ground, paper background, fine grain
"""

import random

from manim import MarkupText, Rectangle

from iroshine import (ELYSIUM as P, Axis, BarList, BarStyle, Finale, Gradient, Grain, Labels,
                     Motion, Sound, Stage, Timing)


class Solution:                                   # LeetCode 912 — Sort an Array
    def sortArray(self, nums):
        def quicksort(lo, hi):
            if lo >= hi:
                return
            pivot = nums[hi]
            i = lo
            for j in range(lo, hi):
                if nums[j] < pivot:
                    nums[i], nums[j] = nums[j], nums[i]
                    i += 1
            nums[i], nums[hi] = nums[hi], nums[i]
            quicksort(lo, i - 1)
            quicksort(i + 1, hi)

        quicksort(0, len(nums) - 1)
        return nums


# The palette's ramp, spelled out so you can see the stop syntax. Same as P.gradient(by="rank").
RAMP = Gradient(("#93b4c6", 0.0), ("#86bf8e", 0.30), ("#b4d68f", 0.58),
                ("#d6dcc9", 0.80), ("#f4efd2", 1.0), by="rank", space="oklab")

stage = Stage(
    background=P.sky,
    resolution=(3840, 2160), fps=60, crf=14,
    grain=Grain(amount=7),
    sound=Sound(scale="pentatonic", key="G", octave=4, instrument="marimba",
                finale_instrument="bell", reverb=0.4, compare_notes=True),
    timing=Timing(speed=1.5, skip=("read",), end_hold=3),
    finale=Finale(target="nums", style="sweep", color=P.accent),
)

stage.add(
    Rectangle(width=13.7, height=7.5).set_stroke(P.outline, width=2).set_fill(opacity=0),
    MarkupText('<span letter_spacing="3000">QUICKSORT</span>', font="Inter", weight="NORMAL",
               font_size=20, color=P.text).move_to([-6.45, 3.35, 0], aligned_edge=[-1, 0, 0]),
    MarkupText('<span letter_spacing="1600">912 · SORT AN ARRAY</span>', font="IBM Plex Mono",
               font_size=13, color=P.muted).move_to([6.45, 3.35, 0], aligned_edge=[1, 0, 0]),

    BarList("nums", position=(0, -0.55), size=(13.5, 6.4), padding=0,
            bar=BarStyle(fill=RAMP, gap=0, outer_gap=0, stroke=P.outline, stroke_width=2),
            axis=Axis(ground=0.5, ground_color=P.ground, ground_stroke=P.outline),
            labels=Labels(name=False),
            panel=None),
)

stage.motion(
    swap=Motion(path="straight", easing="ease_in_out_cubic", duration=0.45),
    compare=Motion(color=P.accent, duration=0.14),
)

random.seed(11)
stage.run(Solution().sortArray, random.sample(range(1, 41), 40))

if __name__ == "__main__":
    import sys
    stage.render("06_elysium_quicksort.mp4", quality=sys.argv[1] if len(sys.argv) > 1 else "high")
