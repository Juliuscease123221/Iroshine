"""
LeetCode 68 — Text Justification (hard), in GARDEN.

Greedy line filling: take words until the next one won't fit (each gap needs at
least one space). Then deal out the line's spaces round-robin, left gaps first,
until the line reaches the measure exactly. The last line stays left-aligned.

What you see:
  · words lift as they're read and fly from the strip onto the page
  · a hollow dot marks each space a line still owes; solid teal dots are real spaces
  · each `cur[k % gaps] += " "` drops one space into a gap and slides the words over
  · a committed line glints at the right margin — every line ends exactly there

New library pieces:
  WordStrip      a list of strings as word tiles
  LineComposer   a page with a fixed measure, built from `cur` and committed from `res`
  strings now carry their origin too, so a word knows which tile it came from
"""

import sys

from manim import MarkupText

from iroshine import GARDEN as P, Finale, Grain, LineComposer, Sound, Stage, Timing, WordStrip


class Solution:
    def fullJustify(self, words, maxWidth):
        res, cur, length = [], [], 0
        for w in words:
            if length + len(w) + len(cur) > maxWidth:
                gaps = len(cur) - 1 or 1
                for k in range(maxWidth - length):
                    cur[k % gaps] += " "
                res.append("".join(cur))
                cur, length = [], 0
            cur.append(w)
            length += len(w)
        res.append(" ".join(cur).ljust(maxWidth))
        return res


TEXT = ("Text justification is the quiet craft of making every line end exactly at the margin, "
        "spreading the leftover space as evenly as it can from left to right, while the final "
        "line is allowed to rest.")

stage = Stage(
    background=P.sky, resolution=(3840, 2160), fps=60, crf=14, grain=Grain(7),
    sound=Sound(scale="lydian", key="E", octave=4, instrument="harp", finale_instrument="bell", reverb=0.5),
    timing=Timing(speed=1.15, end_hold=3),
    finale=Finale(target=None),
)
stage.add(
    MarkupText('<span letter_spacing="3000">TEXT JUSTIFICATION</span>', font="Inter", weight="LIGHT",
               font_size=18, color=P.text).move_to([-6.6, 3.62, 0], aligned_edge=[-1, 0, 0]),
    MarkupText('<span letter_spacing="1600">68 · GREEDY · ROUND-ROBIN SPACES · WIDTH 30</span>',
               font="IBM Plex Mono", font_size=12, color=P.muted).move_to([6.6, 3.62, 0], aligned_edge=[1, 0, 0]),

    WordStrip("words", position=(0, 2.2), size=(13.2, 1.6), cell=0.19, line_height=0.34,
              fill="#f2a861", ink="#1b1b3a"),
    LineComposer(line="cur", out="res", width="maxWidth", source="words",
                 position=(0, -1.35), size=(12.4, 4.3), paper="#d862a9", tile="#f7f1c9",
                 ink="#1b1b3a", space="#1e9476", pending_space="#1b1b3a", margin_color="#f7f1c9"),
)

stage.run(Solution().fullJustify, TEXT.split(), 30)

if __name__ == "__main__":
    stage.render("15_garden_text_justification.mp4", quality=sys.argv[1] if len(sys.argv) > 1 else "medium")
