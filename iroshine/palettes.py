"""
iroshine.palettes — named color sets, sampled from reference prints.

    from iroshine.palettes import GARDEN
    Stage(background=GARDEN.sky)
    BarStyle(fill=GARDEN.gradient(by="rank"))
    Axis(ground=0.2, ground_color=GARDEN.ground)
"""

from dataclasses import dataclass
from typing import Sequence, Union

from .style import Gradient


@dataclass(frozen=True)
class Palette:
    name: str
    background: Union[str, Sequence[str]]   # a color, or [top, ..., bottom] for a gradient sky
    ramp: Union[Sequence, Gradient]          # bar colors: plain colors, (color, position) stops, or a Gradient
    ground: str
    accent: str                             # highlights: compares, the finale sweep
    frame: str
    text: str
    muted: str

    outline: str = ""                        # ink line color, if the style uses outlines

    def gradient(self, by="rank", **kw):
        if isinstance(self.ramp, Gradient):
            g = self.ramp
            return Gradient(*[(c, p) for p, c in g.stops], by=by,
                            space=kw.get("space", g.space), steps=kw.get("steps", g.steps))
        return Gradient(*self.ramp, by=by, **kw)

    @property
    def sky(self):
        return self.background


# "Dusk" — the first reference: violet sky burning down to vermilion, mint ground, moon cream.
DUSK = Palette(
    name="dusk",
    background="#000000",
    ramp=("#4b1d95", "#8e2c8a", "#e2483a", "#f2873f", "#f4e3a0"),
    ground="#5fbf9f", accent="#f4e3a0", frame="#e2483a",
    text="#ece6d8", muted="#5d5850",
)

# "Garden" — the second reference: ultramarine night, a violet glow at the horizon,
# pink paper squares, apricot skin, cream petals, a teal tree and ground.
GARDEN = Palette(
    name="garden",
    background=("#1c3a8e", "#1c3a8e", "#1c3a8e", "#1c3a8e", "#3f3fa3", "#9a55c0"),
    ramp=("#d05aa5", "#f09a5e", "#f7f1c9"),
    ground="#1e9476", accent="#bfe8cf", frame="#d862a9",
    text="#f7f1c9", muted="#8d93c9",
)

# "Elysium" — the third reference: a sage-and-mint architectural poster. Flat paper colors,
# every shape outlined in a thin dark ink line, dusty blue pooled at the bottom.
ELYSIUM = Palette(
    name="elysium",
    background=Gradient(("#dde9d6", 0.0), ("#d6e6d4", 0.7), ("#cfe2d6", 1.0)),
    ramp=Gradient(("#93b4c6", 0.0),      # dusty blue — the pool
                  ("#86bf8e", 0.30),     # leaf green
                  ("#b4d68f", 0.58),     # spring green
                  ("#d6dcc9", 0.80),     # putty
                  ("#f4efd2", 1.0)),     # paper cream
    ground="#86bf8e", accent="#fbf8e6", frame="#2f352e",
    text="#2f352e", muted="#6f7a6c", outline="#2f352e",
)

# "Dark Cherry" — plum night, cherry and orchid walls, periwinkle light, teal water.
#   #230832 plum · #792446 cherry · #192242 navy · #5931C7 violet
#   #277879 teal · #0A3426 forest · #A16193 orchid · #86A0CE periwinkle
DARK_CHERRY = Palette(
    name="dark_cherry",
    background=Gradient(("#230832", 0.0), ("#1d1439", 0.55), ("#192242", 1.0)),
    ramp=Gradient(("#792446", 0.0), ("#A16193", 0.55), ("#86A0CE", 1.0)),
    ground="#0A3426", accent="#86A0CE", frame="#5931C7",
    text="#d9d2ec", muted="#7d6a96",
)
DARK_CHERRY_HEX = ["#230832", "#792446", "#192242", "#5931C7",
                   "#277879", "#0A3426", "#A16193", "#86A0CE"]

# "Lake" — a dusk lake: violet-to-peach sky, indigo mountains, cobalt water, one orange figure.
LAKE = Palette(
    name="lake",
    background=Gradient(("#8a4f92", 0.0), ("#b86c98", 0.2), ("#da8da2", 0.4), ("#f1bfb4", 0.62),
                        ("#f6caa2", 0.82), ("#f5d9a9", 1.0)),
    ramp=Gradient(("#c24d8f", 0.0), ("#6a2f7d", 0.5), ("#201556", 1.0)),   # lake pink → violet → mountain indigo
    ground="#201556", accent="#ec785d", frame="#201556",
    text="#201556", muted="#6a4a78",
)
LAKE_WATER, LAKE_SURFACE, LAKE_CREAM = "#284dbd", "#77a0e4", "#fbf2df"

ALL = {p.name: p for p in (DUSK, GARDEN, ELYSIUM, DARK_CHERRY, LAKE)}
