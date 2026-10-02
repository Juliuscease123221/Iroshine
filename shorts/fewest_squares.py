"""
REELS — LeetCode 1240 · Fewest Squares.

One continuous search: slow and solid at first, then faster and fading to outlines. When a smaller
tiling turns up it is built in the same outline style, fills with colour, and stays faintly under the
rest of the search while every later attempt is cut off at that many squares. At the end it lifts
back to full colour and the squares build a chord, biggest first.

  python fewest_squares.py <quality> <palette> <style> <find>
      quality   low | medium | high
      palette   1: navy → red → gold on a dark page · 2: soft blue → green → cream on a pale page
      style     number | silent | hold | proof            (TilingView.found_style)
      find      cut | pause | crossfade | slowmo | rebuild_pause | rebuild_fade | outline_build

  Environment: TILE_N, TILE_M (board, default 11 × 13) · SOUND_ARC (cut | arc | coda) · TICK_EVERY ·
  HIGHLIGHT (flash | pop) · ENDING (reveal | confirm | confirm_sweep) · FIND_COUNT (1 | 0) ·
  LOOP_OUT (fade | dissolve) · TAG (a suffix for the output file name)

  With no arguments it renders the finished video (palette 1, proof, outline_build, and the
  environment defaults arc / pop / confirm_sweep / no count at the find / dissolve).
"""

import os
import sys

from manim import MarkupText

from iroshine import CodePanel, Finale, Gradient, Sound, Stage, Timing, TilingView, code_style


class Solution:
    def tilingRectangle(self, n, m):
        h = [0] * n                      # how high each column is filled
        placed = []
        best = n * m

        def fill():
            nonlocal best
            if len(placed) >= best:
                return
            low = min(h)
            if low == m:
                best = len(placed)
                return
            x = h.index(low)
            room = width_at(x, low)
            for s in range(min(room, m - low), 0, -1):
                put(x, low, s, 1)
                fill()
                put(x, low, s, -1)

        def put(x, y, s, d):
            for k in range(x, x + s):
                h[k] += d * s
            if d > 0:
                placed.append((x, y, s))
            else:
                placed.pop()

        def width_at(x, low):
            w = 1
            while x + w < n and h[x + w] == low:
                w += 1
            return w

        fill()
        return best


N, M = int(__import__("os").environ.get("TILE_N", 11)), int(__import__("os").environ.get("TILE_M", 13))
PALETTE = sys.argv[2] if len(sys.argv) > 2 else "1"
STYLE = sys.argv[3] if len(sys.argv) > 3 else "proof"    # TilingView.found_style
FIND = sys.argv[4] if len(sys.argv) > 4 else "outline_build"   # TilingView.find_transition
SHOWN = {(11, 13): [11, 7, 6, 5, 4, 2, 1], (9, 10): [9, 5, 4, 2, 1]}.get((N, M), [11, 7, 6, 5, 4, 2, 1])   # sizes seen solid


def _lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def _unlin(c): return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
def mute(hexcol, k):
    """Scale a colour's chroma (saturation) by k in OKLab, keeping its lightness and hue."""
    r, g, b = (_lin(int(hexcol[i:i + 2], 16) / 255) for i in (1, 3, 5))
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s_ = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s_
    A = (1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s_) * k
    B = (0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s_) * k
    l, m, s_ = [(L + x * A + y * B) ** 3 for x, y in ((0.3963377774, 0.2158037573), (-0.1055613458, -0.0638541728),
                                                      (-0.0894841775, -1.2914855480))]
    rgb = (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s_, -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s_,
           -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s_)
    return "#%02x%02x%02x" % tuple(round(max(0, min(1, _unlin(max(0, v)))) * 255) for v in rgb)


def rank_t(s):                                   # 0 = biggest shown … 1 = smallest shown
    if s in SHOWN:
        return SHOWN.index(s) / (len(SHOWN) - 1)
    return min(1.0, max(0.0, 1 - (s - 1) / 10))


if PALETTE == "1":
    BG, TEXT, MUTED = "#121212", "#efe9dc", "#8a867d"
    NAVY, RED, GOLD = "#1a2a6c", "#b21f1f", "#fdbb2d"
    ACCENT = GOLD
    RAMP = Gradient(NAVY, RED, GOLD)
    def size_color(s):
        c = RAMP.at(rank_t(s)).to_hex()[:7]
        return c if s == 1 else mute(c, 0.8 + 0.2 * rank_t(s))     # a little muted on the biggest squares only
    VIEW = dict(board="#34332f", frame_color="#0c0c0c", dot="#4f4e49", outline="#0c0c0c", outline_width=3,
                gap=0.20,                                           # the ink lines: 20% of a grid cell
                ghost="#8a867d", corner="#fff2c2")
    CODE = dict(background="#1b1b1a", style=code_style(text="#e6e1d6", keyword="#e0574f", string=GOLD,
                                                         number="#8fa3e6", comment=MUTED),
                highlight=GOLD, highlight_opacity=0.16)
else:
    BG, TEXT, MUTED = "#dde6d6", "#2f352e", "#6f7a6c"
    ACCENT = "#b98212"                                             # darker gold: readable on the pale page
    RAMP = Gradient("#93b4c6", "#86bf8e", "#b4d68f", "#e8e2b8")    # dusty blue → leaf → spring → cream
    def size_color(s):
        if s == 1:
            return "#eab13b"                                       # the one saturated accent: the surprise
        return RAMP.at(rank_t(s) / rank_t(2)).to_hex()[:7]
    VIEW = dict(board="#cdd8c6", frame_color="#2f352e", dot="#b3bfad", outline="#2f352e", outline_width=2.5,
                ghost="#56604f", corner="#2f352e")
    CODE = dict(background="#f3f6ec", style=code_style(text="#2f352e", keyword="#3d7a55", string="#a8742a",
                                                         number="#4f7596", comment="#8a948a"),
                highlight="#86bf8e", highlight_opacity=0.35)
GOLD = ACCENT
if STYLE == "proof":                                   # each cut-off attempt gets long enough to read
    VIEW.update(montage_after=18, montage_after_dt=0.11)

LOOP_OUT = os.environ.get("LOOP_OUT", "dissolve")
PX = 240
def X(px): return px / PX - 2.25
def Yp(px): return 4 - px / PX
LEFT = X(70) + 0.03
RIGHT_TOP = X(1080 - 70) - 0.03
RIGHT_LOW = X(1080 - 193) - 0.03
TOP = Yp(250)
code_w = RIGHT_LOW - LEFT
BOARD_W = 2.4

stage = Stage(
    background=BG, resolution=(1080, 1920), fps=60, crf=16, grain=None,
    sound=Sound(scale="pentatonic", key="D", octave=3, reverb=0.04, instrument="wood",
                finale_instrument="log_drum", soft_instrument="wood_soft", tick_instrument="wood_soft",
                finale=False),                  # the ending chord is built by the squares themselves
    timing=Timing(speed=1.0, end_hold=0.4 if LOOP_OUT == "fade" else 0.12, intro="instant", loop=True,
                  loop_time=1.1 if LOOP_OUT == "fade" else 0.6),
    finale=Finale(target=None, color=ACCENT),
)

stage.add(
    MarkupText('<span letter_spacing="1700">FEWEST SQUARES</span>', font="Inter", weight="MEDIUM",
               font_size=12, color=TEXT).move_to([LEFT + 0.04, TOP - 0.32, 0], aligned_edge=[-1, 0, 0]),
    MarkupText(f'<span letter_spacing="1400">LEETCODE 1240 · HARD · {N} × {M}</span>', font="IBM Plex Mono",
               font_size=8, color=MUTED).move_to([LEFT + 0.04, TOP - 0.54, 0], aligned_edge=[-1, 0, 0]),
    MarkupText('<span letter_spacing="1400">MADE WITH IROSHINE</span>', font="IBM Plex Mono",
               font_size=8, color=MUTED).move_to([LEFT + 0.04, -3.04, 0], aligned_edge=[-1, 0, 0]),

    TilingView(N, M, position=(LEFT + BOARD_W / 2 + 0.1, 0.55), size=(BOARD_W, 2.8),
               readout_x=LEFT + BOARD_W + 0.45, readout_y=1.35, text=TEXT, muted=MUTED, accent=ACCENT,
               colors=size_color, story="ramp", best_label="FEWEST", found_style=STYLE, find_transition=FIND,
               montage_frames=64, show_count=False, ramp_events=20, ramp_slow=0.3, chord_sweep=True,
               end_slowdown=7, end_slow_dt=0.2, reveal_pause=0.4,
               sound_arc=os.environ.get("SOUND_ARC", "arc"), tick_every=int(os.environ.get("TICK_EVERY", "1")),
               highlight=os.environ.get("HIGHLIGHT", "pop"), ending=os.environ.get("ENDING", "confirm_sweep"),
               find_count=os.environ.get("FIND_COUNT", "0") == "1", loop_out=LOOP_OUT,
               **VIEW),

    CodePanel(position=(LEFT + code_w / 2, -1.93), width=code_w, line_numbers=False,
              show=("if len(placed)", "put(x, low, s, -1)"), glide=True, glide_speed=8, span="inner",
              corner_radius=0.1, padding=0.16, **CODE),
)

stage.run(Solution().tilingRectangle, N, M)

if __name__ == "__main__":
    stage.render(f"fewest_squares_{N}x{M}{os.environ.get('TAG', '')}.mp4",
                 quality=sys.argv[1] if len(sys.argv) > 1 else "high")
