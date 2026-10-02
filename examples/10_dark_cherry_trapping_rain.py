"""
LeetCode 42 — Trapping Rain Water (hard), in DARK CHERRY.

A monotonic stack of *indices*. Each time a taller wall arrives, the lower wall on top
of the stack is popped and the water it can hold is poured in as a Region, and the
running total counts up in a Readout. Nothing is being sorted: the answer is an area.

New pieces shown here:
  BarList(indexes="height")   the stack holds positions; each bar is drawn as the wall it names
  Pointer("i", on="height")   a marker that follows a loop variable
  Readout("water")            a number that counts as the variable changes
  Region(...)                 a shape drawn from your local variables whenever `water` changes
"""

from manim import MarkupText

from iroshine import (DARK_CHERRY as P, Axis, BarList, BarStyle, Finale, Grain, Labels, Motion,
                     Pointer, Readout, Region, Sound, Stage, Timing)


class Solution:
    def trap(self, height):
        stack = []
        water = 0
        for i in range(len(height)):
            while stack and height[i] > height[stack[-1]]:
                top = stack.pop()
                if not stack:
                    break
                left = stack[-1]
                width = i - left - 1
                bounded = min(height[left], height[i]) - height[top]
                water += width * bounded
            stack.append(i)
        return water


HEIGHTS = [3, 0, 2, 0, 4, 1, 0, 2, 5, 0, 1, 3, 2, 0, 6, 1, 2, 0, 3, 1, 4, 2]
Y = (0, 6.6)
walls = P.gradient(by="value")

stage = Stage(
    background=P.sky, resolution=(3840, 2160), fps=60, crf=14, grain=Grain(8),
    sound=Sound(scale="dorian", key="C", octave=4, instrument="harp", finale_instrument="bell",
                reverb=0.5),
    timing=Timing(speed=1.6, skip=("read",), end_hold=3),
    finale=Finale(target="height", style="sweep", color=P.accent),
)

stage.add(
    MarkupText('<span letter_spacing="3000">TRAPPING RAIN WATER</span>', font="Inter", weight="LIGHT",
               font_size=18, color=P.text).move_to([-6.6, 3.55, 0], aligned_edge=[-1, 0, 0]),
    MarkupText('<span letter_spacing="1600">42 · MONOTONIC STACK</span>', font="IBM Plex Mono",
               font_size=12, color=P.muted).move_to([6.6, 3.55, 0], aligned_edge=[1, 0, 0]),

    Readout("water", position=(-6.6, 2.15), label="water trapped", font_size=96,
            color=P.text, label_color=P.muted),

    BarList("height", position=(0, -0.75), size=(14.2, 4.5), padding=0, y_range=Y,
            bar=BarStyle(fill=walls, gap=0, outer_gap=0.5),
            axis=Axis(ground=0.35, ground_color=P.ground), labels=Labels(name=False), panel=None),

    BarList("stack", indexes="height", position=(3.9, 2.35), size=(5.6, 1.9), y_range=Y,
            capacity=6, bar=BarStyle(fill=walls, gap=0.25),
            axis=Axis(color=P.muted), labels=Labels(color=P.muted, name_size=12), panel=None),

    Pointer("i", on="height", color=P.accent, guide=True, guide_opacity=0.12),

    Region(on="height", when="water",
           x0="left + 1", x1="i - 1",
           y0="height[top]", y1="min(height[left], height[i])",
           fill="#277879", opacity=0.92, surface="#5fa3b8", surface_width=2),
)

stage.motion(
    push=Motion(path="straight", easing="ease_in_out_cubic", duration=0.55),
    pop=Motion(exit="fade", duration=0.35),
    compare=Motion(color=P.accent, duration=0.16),
)

stage.run(Solution().trap, HEIGHTS)

if __name__ == "__main__":
    import sys
    stage.render("10_dark_cherry_trapping_rain.mp4", quality=sys.argv[1] if len(sys.argv) > 1 else "medium")
