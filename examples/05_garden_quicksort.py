"""
Example 5 — "garden": quicksort in the second reference's palette.

  · BarStyle(gap=0): bars touch, so the list reads as one silhouette
  · Stage(background=[top, ..., bottom]): ultramarine sky with a violet glow at the horizon
  · GARDEN.gradient(by="rank"): violet → pink → apricot → cream, assembling as it sorts
  · a thick teal ground running edge to edge
"""

import random

from manim import MarkupText

from iroshine import (GARDEN as P, Axis, BarList, BarStyle, Finale, Grain, Labels, Motion,
                     Sound, Stage, Timing)


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


stage = Stage(
    background=P.sky,
    resolution=(3840, 2160), fps=60, crf=14,
    grain=Grain(amount=8),
    sound=Sound(scale="lydian", key="E", octave=4, instrument="music_box",
                finale_instrument="bell", reverb=0.5, compare_notes=True),
    timing=Timing(speed=1.5, skip=("read",), end_hold=3),
    finale=Finale(target="nums", style="sweep", color=P.accent),
)

stage.add(
    MarkupText('<span letter_spacing="3000">QUICKSORT</span>', font="Inter", weight="LIGHT",
               font_size=20, color=P.text).move_to([-6.5, 3.45, 0], aligned_edge=[-1, 0, 0]),
    MarkupText('<span letter_spacing="1600">912 · SORT AN ARRAY</span>', font="IBM Plex Mono",
               font_size=13, color=P.muted).move_to([6.5, 3.45, 0], aligned_edge=[1, 0, 0]),

    BarList("nums", position=(0, -1.25), size=(14.4, 5.6), padding=0,
            bar=BarStyle(fill=P.gradient(by="rank"), gap=0, outer_gap=0.5),
            axis=Axis(ground=0.55, ground_color=P.ground),
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
    stage.render("05_garden_quicksort.mp4", quality=sys.argv[1] if len(sys.argv) > 1 else "high")
