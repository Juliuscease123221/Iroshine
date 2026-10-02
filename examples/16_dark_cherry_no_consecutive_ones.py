"""
LeetCode 600 — Non-negative Integers without Consecutive Ones (hard), in DARK CHERRY.

f[k] counts the k-bit strings with no "11". It's Fibonacci: a valid string starts
with 0 (then any valid k-1 bits) or with 10 (then any valid k-2 bits), so
f[k] = f[k-1] + f[k-2]. Then read n's bits from the top: at every 1, all numbers
that put a 0 there instead are valid and smaller than n — that's f[remaining bits].
Two 1s in a row means n's own prefix is invalid, so stop.

What you see:
  · each Fibonacci bar is built from the two bars before it, stacked
  · n's bits are read left to right
  · every 1 sends its f[k] bar over to the tower, which is the running count
  · the scan stops at the first "11"; the bits it never needed dim

New library pieces:
  sums remember their parts (f[i-1] + f[i-2]), so a bar can be built from its pieces
  Tower            a running total drawn as stacked blocks, on the same scale as the bars
  WordStrip        now also shows lists created inside your code, with per-word colors
  Readout(result=True)  counts on to the function's return value at the end
"""

import sys

from manim import MarkupText

from iroshine import (DARK_CHERRY as P, Axis, BarList, BarStyle, Finale, Gradient, Grain, Labels, Motion, Readout,
                     Sound, Stage, Timing, Tower, WordStrip)


class Solution:
    def findIntegers(self, n):
        bits = list(bin(n)[2:])
        L = len(bits)
        f = [0] * (L + 1)
        f[0], f[1] = 1, 2
        for i in range(2, L + 1):
            f[i] = f[i - 1] + f[i - 2]
        ans, prev = 0, "0"
        for i, b in enumerate(bits):
            if b == "1":
                ans += f[L - 1 - i]
                if prev == "1":
                    return ans
            prev = b
        return ans + 1


N = 662                                      # 1010010110 in binary
stage = Stage(
    background=P.sky, resolution=(3840, 2160), fps=60, crf=14, grain=Grain(7),
    sound=Sound(scale="dorian", key="C", octave=4, instrument="harp", finale_instrument="bell", reverb=0.5),
    timing=Timing(skip=("read", "compare"), end_hold=3),
    finale=Finale(target=None, color=P.accent),
)
stage.add(
    MarkupText('<span letter_spacing="3000">NO CONSECUTIVE ONES</span>', font="Inter", weight="LIGHT",
               font_size=18, color=P.text).move_to([-6.6, 3.62, 0], aligned_edge=[-1, 0, 0]),
    MarkupText(f'<span letter_spacing="1600">600 · FIBONACCI · DIGIT DP · n = {N}</span>',
               font="IBM Plex Mono", font_size=12, color=P.muted).move_to([6.6, 3.62, 0], aligned_edge=[1, 0, 0]),

    WordStrip("bits", position=(-1.3, 2.45), size=(12.5, 0.8), cell=0.46, line_height=0.66, gap=0.16,
              fills={"1": "#A16193", "0": "#1d1640"}, inks={"1": "#230832", "0": "#86A0CE"},
              reveal=True, unread_opacity=0.3, read_time=0.45, cursor="#86A0CE",
              sublabels=lambda i, w, n: n - 1 - i,         # bits left after this one = which f[k] it unlocks
              sublabel_color=P.muted, sublabel_size=17, dim_unread=True, stop_mark=2, stop_color="#86A0CE"),

    BarList("f", position=(-1.3, -1.1), size=(10.8, 4.5), y_range=(0, 150),
            bar=BarStyle(fill=Gradient("#792446", "#A16193", "#86A0CE", by="index"), gap=0.16),
            axis=Axis(ground=0.16, ground_color="#0A3426"),
            labels=Labels(values=True, indices=True, name=False, color=P.text, muted=P.muted, font_size=15),
            panel=None),

    Tower("ans", on="f", x=5.55, width=0.95, stroke="#1d1439", extra_fill=P.accent,
          labels=True, label_color="#230832", label_size=14),
    Readout("ans", position=(5.0, 2.45), label="count", font_size=64, color=P.text,
            label_color=P.muted, result=True),
)
stage.motion(combine=Motion(duration=0.75, easing="ease_in_out_cubic"))

stage.run(Solution().findIntegers, N)

if __name__ == "__main__":
    stage.render("16_dark_cherry_no_consecutive_ones.mp4", quality=sys.argv[1] if len(sys.argv) > 1 else "medium")
