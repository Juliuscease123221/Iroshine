"""
Example 3 — "riso": quicksort, art-directed from a screen-print reference.

  · black canvas, 4K / 60 fps, visually-lossless encode, fine animated grain
  · palette sampled from the reference: violet → magenta → vermilion → orange → moon-cream
  · Gradient(by="rank"): each element owns its color, so the ramp assembles as the list sorts
  · swaps move in straight lines, easing in and out
  · flat sharp bars on a mint "ground" slab, inside a thin vermilion frame
  · almost no text
"""

import random

from manim import MarkupText, Rectangle

from iroshine import (Axis, BarList, BarStyle, Caption, Finale, Gradient, Grain, Labels,
                     Motion, Panel, Sound, Stage, Timing)


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


# ── palette (sampled from the reference print) ───────────────────────────────
VIOLET, MAGENTA, VERMILION = "#4b1d95", "#8e2c8a", "#e2483a"
ORANGE, MOON, MINT = "#f2873f", "#f4e3a0", "#5fbf9f"
INK, BONE, ASH = "#000000", "#ece6d8", "#5d5850"

SKY = Gradient(VIOLET, MAGENTA, VERMILION, ORANGE, MOON, by="rank")

stage = Stage(
    background=INK,
    resolution=(3840, 2160), fps=60, crf=14,
    grain=Grain(amount=8),
    sound=Sound(scale="pentatonic", key="D", octave=4, instrument="harp",
                finale_instrument="bell", reverb=0.45, compare_notes=True),
    timing=Timing(speed=1.2, skip=("read",), end_hold=3),
    finale=Finale(target="nums", style="sweep", color=MOON),
    caption=Caption(position=(-6.25, -3.42), font_size=15, color=ASH),
)

stage.add(
    # a thin vermilion frame, like the panel borders in the print (plain Manim)
    Rectangle(width=13.4, height=7.4).set_stroke(VERMILION, width=5).set_fill(opacity=0),
    MarkupText('<span letter_spacing="3800">QUICKSORT</span>', font="Inter", weight="LIGHT",
               font_size=20, color=BONE).move_to([-6.25, 3.3, 0], aligned_edge=[-1, 0, 0]),
    MarkupText('<span letter_spacing="1600">912 · SORT AN ARRAY</span>', font="IBM Plex Mono",
               font_size=13, color=ASH).move_to([6.25, 3.3, 0], aligned_edge=[1, 0, 0]),

    BarList("nums", position=(0, -0.15), size=(12.2, 5.9),
            bar=BarStyle(fill=SKY, width=0.74, shade=0.18),
            axis=Axis(ground=0.16, ground_color=MINT),
            labels=Labels(name=False),
            panel=None),
)

stage.motion(
    swap=Motion(path="straight", easing="ease_in_out_cubic", duration=0.5),
    compare=Motion(color=MOON, duration=0.16),
)

random.seed(4)
data = random.sample(range(1, 33), 32)
stage.run(Solution().sortArray, data)

if __name__ == "__main__":
    import sys
    stage.render("03_riso_quicksort.mp4", quality=sys.argv[1] if len(sys.argv) > 1 else "high")
