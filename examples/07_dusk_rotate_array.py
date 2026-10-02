"""
LeetCode 189 — Rotate Array (medium), in DUSK.

The reversal trick: reverse everything, then reverse the first k, then the rest.
The input starts sorted, so the rank gradient shows exactly what each reversal does.
"""

from manim import MarkupText, Rectangle

from iroshine import DUSK as P, Axis, BarList, BarStyle, Finale, Grain, Labels, Motion, Sound, Stage, Timing


class Solution:
    def rotate(self, nums, k):
        n = len(nums)
        k %= n

        def reverse(l, r):
            while l < r:
                nums[l], nums[r] = nums[r], nums[l]
                l += 1
                r -= 1

        reverse(0, n - 1)
        reverse(0, k - 1)
        reverse(k, n - 1)


stage = Stage(
    background=P.sky, resolution=(3840, 2160), fps=60, crf=14, grain=Grain(8),
    sound=Sound(scale="pentatonic", key="D", instrument="harp", reverb=0.45),
    timing=Timing(skip=("read", "compare"), end_hold=3),
    finale=Finale(target="nums", style="sweep", color=P.accent),
)
stage.add(
    Rectangle(width=13.4, height=7.4).set_stroke(P.frame, width=5).set_fill(opacity=0),
    MarkupText('<span letter_spacing="3200">ROTATE ARRAY</span>', font="Inter", weight="LIGHT",
               font_size=20, color=P.text).move_to([-6.25, 3.3, 0], aligned_edge=[-1, 0, 0]),
    MarkupText('<span letter_spacing="1600">189 · THREE REVERSALS · k = 11</span>', font="IBM Plex Mono",
               font_size=13, color=P.muted).move_to([6.25, 3.3, 0], aligned_edge=[1, 0, 0]),
    BarList("nums", position=(0, -0.15), size=(12.2, 5.9),
            bar=BarStyle(fill=P.gradient(by="rank"), gap=0.22, shade=0.18),
            axis=Axis(ground=0.16, ground_color=P.ground), labels=Labels(name=False), panel=None),
)
stage.motion(swap=Motion(path="straight", easing="ease_in_out_cubic", duration=0.55))
stage.run(Solution().rotate, list(range(1, 37)), 11)

if __name__ == "__main__":
    import sys
    stage.render("07_dusk_rotate_array.mp4", quality=sys.argv[1] if len(sys.argv) > 1 else "high")
