"""
LeetCode 75 — Sort Colors (medium), in GARDEN.

Dijkstra's Dutch-national-flag partition: one pass, three pointers, only swaps.
Three values means three colors: the flag assembles from both ends at once.
"""

import random

from manim import MarkupText

from iroshine import GARDEN as P, Axis, BarList, BarStyle, Finale, Grain, Labels, Motion, Sound, Stage, Timing


class Solution:
    def sortColors(self, nums):
        lo, mid, hi = 0, 0, len(nums) - 1
        while mid <= hi:
            if nums[mid] == 0:
                nums[lo], nums[mid] = nums[mid], nums[lo]
                lo += 1
                mid += 1
            elif nums[mid] == 1:
                mid += 1
            else:
                nums[mid], nums[hi] = nums[hi], nums[mid]
                hi -= 1


stage = Stage(
    background=P.sky, resolution=(3840, 2160), fps=60, crf=14, grain=Grain(8),
    sound=Sound(scale="lydian", key="E", instrument="music_box", reverb=0.5),
    timing=Timing(skip=("read", "compare"), end_hold=3),
    finale=Finale(target="nums", style="sweep", color=P.accent),
)
stage.add(
    MarkupText('<span letter_spacing="3000">SORT COLORS</span>', font="Inter", weight="LIGHT",
               font_size=20, color=P.text).move_to([-6.5, 3.45, 0], aligned_edge=[-1, 0, 0]),
    MarkupText('<span letter_spacing="1600">75 · DUTCH NATIONAL FLAG</span>', font="IBM Plex Mono",
               font_size=13, color=P.muted).move_to([6.5, 3.45, 0], aligned_edge=[1, 0, 0]),
    BarList("nums", position=(0, -1.25), size=(14.4, 5.6), padding=0, y_range=(-1.2, 2),
            bar=BarStyle(fill=P.gradient(by="rank"), gap=0, outer_gap=0.5),
            axis=Axis(ground=0.55, ground_color=P.ground), labels=Labels(name=False), panel=None),
)
stage.motion(swap=Motion(path="straight", easing="ease_in_out_cubic", duration=0.5))

random.seed(3)
stage.run(Solution().sortColors, [random.choice((0, 1, 2)) for _ in range(44)])

if __name__ == "__main__":
    import sys
    stage.render("08_garden_sort_colors.mp4", quality=sys.argv[1] if len(sys.argv) > 1 else "high")
