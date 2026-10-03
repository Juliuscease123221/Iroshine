"""
Example 2 — the same solution, fully art-directed.

Shows off: y_range that starts at 280 (every value is ≥ 300), guide ticks,
value gradients with glow, pill and lollipop shapes, a sideways stack,
hop-shaped flights with trails, a custom pop animation written in plain
Manim, a plain-Manim title, and a different scale / key / instrument.
"""

from manim import RIGHT, FadeOut, Text, rate_functions

from iroshine import (Axis, BarList, BarStyle, Caption, CodePanel, Finale, Gradient,
                     Labels, Motion, Panel, Sound, Stage, Timing)


class Solution:                                   # LeetCode 496, still untouched
    def nextGreaterElement(self, nums1, nums2):
        greater = {}
        stack = []
        for n in nums2:
            while stack and stack[-1] < n:
                greater[stack.pop()] = n
            stack.append(n)
        return [greater.get(x, -1) for x in nums1]


# ── a small design system: define once, reuse everywhere ───────────────────
INK, MUTED = "#dfe6f5", "#6f7aa0"
NEON = Gradient("#7b5cff", "#29d3c2", "#f7d154", by="value")
panel = Panel(fill="#141a33", opacity=0.92, corner_radius=0.25, stroke="#2a3561")
labels = Labels(color=INK, muted=MUTED, font_size=17, name_size=20)
guides = Axis(color="#2a3561", ticks=(300, 450, 600))
Y = (280, 620)                                    # ← baseline at 280, not 0

stage = Stage(
    background="#0b0f1e",
    sound=Sound(scale="lydian", key="F", octave=5, instrument="music_box",
                finale_instrument="bell", reverb=0.55, landing_interval=4, tick_reads=False),
    timing=Timing(speed=1.1, skip=("read",)),
    finale=Finale(color="#29d3c2", text="all found ✧", font_size=34),
)

stage.add(
    Text("next greater element", font="DejaVu Sans", weight="BOLD", font_size=34, color=INK)
        .to_corner([-1, 1, 0], buff=0.35),                                   # plain Manim
    BarList("nums2", title="nums2", position=(-2.2, 1.95), size=(9.4, 2.35), y_range=Y,
            bar=BarStyle(shape="pill", fill=NEON, glow=0.7), panel=panel, labels=labels, axis=guides),
    BarList("nums1", position=(-5.0, -1.25), size=(4.0, 2.5), y_range=Y,
            bar=BarStyle(shape="lollipop", fill=NEON, glow=0.5), panel=panel,
            labels=Labels(color=INK, muted=MUTED, font_size=15, name_size=20, name_margin=1.05),
            axis=Axis(color="#2a3561")),
    BarList("stack", position=(-0.8, -1.25), size=(4.1, 2.5), y_range=Y, orientation="right",
            bar=BarStyle(shape="pill", fill=NEON, glow=0.7, width=0.62), panel=panel,
            labels=Labels(color=INK, muted=MUTED, font_size=15, name_size=20, name_margin=1.05),
            axis=Axis(color="#2a3561")),
    BarList("result", title="answer", position=(4.85, -1.25), size=(4.3, 2.5), y_range=Y,
            bar=BarStyle(shape="rect", corner_radius=0.12, fill="#3a4675", glow=0.3), panel=panel,
            labels=Labels(color=INK, muted=MUTED, font_size=15, name_size=20, name_margin=1.1),
            axis=Axis(color="#2a3561")),
    CodePanel(position=(4.85, 1.95), width=4.3, style="monokai", background="#141a33",
              border="#2a3561", highlight="#7b5cff", highlight_opacity=0.35),
    Caption(position=(-6.8, -3.55), font_size=17, color=MUTED),
)

stage.motion(
    push=Motion(path="hop", trail=True, color="#f7d154", duration=0.85, easing="ease_in_out_cubic"),
    compare=Motion(color="#ff5d8f", duration=0.4),
)


@stage.on("pop", target="stack")                 # replace one animation with your own Manim
def whoosh(ctx):
    return [FadeOut(ctx.bar, scale=0.2, shift=0.8 * RIGHT, rate_func=rate_functions.ease_in_back)]


stage.run(Solution().nextGreaterElement,
          [470, 360, 410, 340, 600],
          [310, 470, 360, 520, 410, 340, 580, 600])

if __name__ == "__main__":
    import sys
    stage.render("02_neon.mp4", quality=sys.argv[1] if len(sys.argv) > 1 else "high")
