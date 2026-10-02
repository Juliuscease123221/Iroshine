"""
Example 4 — the monotonic-stack problem in the same "riso" language.

Multiple lists, values flying between them in straight eased lines, a
sideways stack, a small code panel. Colors follow value, so a number keeps its
color wherever it goes.
"""

from manim import MarkupText, Rectangle

from iroshine import (Axis, BarList, BarStyle, CodePanel, Finale, Gradient, Grain, Labels,
                     Motion, Panel, Sound, Stage, Timing)


class Solution:                                   # LeetCode 496 — untouched
    def nextGreaterElement(self, nums1, nums2):
        greater = {}
        stack = []
        for n in nums2:
            while stack and stack[-1] < n:
                greater[stack.pop()] = n
            stack.append(n)
        return [greater.get(x, -1) for x in nums1]


VIOLET, MAGENTA, VERMILION = "#4b1d95", "#8e2c8a", "#e2483a"
ORANGE, MOON, MINT = "#f2873f", "#f4e3a0", "#5fbf9f"
INK, BONE, ASH = "#000000", "#ece6d8", "#5d5850"

SKY = Gradient(VIOLET, MAGENTA, VERMILION, ORANGE, MOON, by="value")
Y = (0, 52)                                       # one shared scale, so a value is the same height everywhere
bars = BarStyle(fill=SKY, width=0.7, shade=0.18)
ground = Axis(ground=0.12, ground_color=MINT)
text = Labels(values=True, font_size=13, color=ASH, name_size=13)

stage = Stage(
    background=INK, resolution=(3840, 2160), fps=60, crf=14,
    grain=Grain(amount=8),
    sound=Sound(scale="lydian", key="F", instrument="music_box", reverb=0.5, landing_interval=4),
    timing=Timing(skip=("read",), end_hold=3),
    finale=Finale(target="result", style="sweep", color=MOON),
)

stage.add(
    Rectangle(width=13.4, height=7.4).set_stroke(VERMILION, width=5).set_fill(opacity=0),
    MarkupText('<span letter_spacing="2600">NEXT GREATER</span>', font="Inter", weight="LIGHT",
               font_size=20, color=BONE).move_to([-6.25, 3.3, 0], aligned_edge=[-1, 0, 0]),
    MarkupText('<span letter_spacing="1600">496 · MONOTONIC STACK</span>', font="IBM Plex Mono",
               font_size=13, color=ASH).move_to([6.25, 3.3, 0], aligned_edge=[1, 0, 0]),

    BarList("nums2", position=(-2.1, 1.15), size=(8.6, 3.1), y_range=Y, bar=bars, axis=ground,
            labels=text, panel=None),
    BarList("stack", position=(4.45, 1.15), size=(3.5, 3.1), y_range=Y, orientation="right",
            bar=bars, axis=ground, labels=text, panel=None),
    BarList("nums1", position=(-4.2, -2.15), size=(4.6, 2.3), y_range=Y, bar=bars, axis=ground,
            labels=text, panel=None),
    BarList("result", title="answer", position=(0.75, -2.15), size=(4.6, 2.3), y_range=Y, bar=bars,
            axis=ground, labels=text, panel=None),
    CodePanel(position=(4.75, -2.15), width=3.4, background=INK, highlight=MOON),
)

stage.motion(
    push=Motion(path="straight", easing="ease_in_out_cubic", duration=0.75),
    pop=Motion(exit="fade", duration=0.4),
    compare=Motion(color=MOON, duration=0.3),
)

stage.run(Solution().nextGreaterElement, [31, 18, 25, 15, 52], [12, 31, 18, 40, 25, 15, 47, 52])

if __name__ == "__main__":
    import sys
    stage.render("04_riso_next_greater.mp4", quality=sys.argv[1] if len(sys.argv) > 1 else "high")
