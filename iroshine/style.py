"""
iroshine.style — every visual and musical knob, as plain dataclasses.

Defaults are deliberately quiet: black canvas, sharp flat shapes, no glow, no
sparkles, no badge text. Turn things *on* when you want them.

Colors: any hex string or Manim color.
Easings: any Manim rate-function name ("smooth", "ease_in_out_cubic",
"ease_in_out_expo", "ease_out_back", ...) or a callable f(t) -> t.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence, Tuple, Union

from manim import ManimColor, interpolate_color, rate_functions

Color = Union[str, ManimColor]


# ───────────────────────────────────────────────────────────── colors ──
from .gradient import Gradient   # multi-stop, positioned, OKLab — see gradient.py


# A fill can be a color, a Gradient, or a function (value, index) -> color
Fill = Union[Color, Gradient, Callable[[float, int], Color]]


# ────────────────────────────────────────────────────────────── pieces ──
@dataclass
class BarStyle:
    shape: str = "rect"                 # "rect" | "pill" | "lollipop"
    gap: Optional[float] = None         # space between bars as a fraction of each slot (like D3's paddingInner).
                                        #   0 = bars touch, 0.2 = 20% gap, None = use `width` instead
    outer_gap: Optional[float] = None   # space before the first / after the last bar, in slots
                                        #   (D3's paddingOuter). None = half of `gap`
    seam: float = 1.5                   # when gap == 0: overlap neighbours by this many pixels so
                                        #   anti-aliasing never shows a hairline between them
    width: float = 0.78                 # legacy: bar width as a fraction of each slot (= 1 - gap)
    corner_radius: float = 0.0
    fill: Fill = "#e8e4dc"
    opacity: float = 1.0
    shade: float = 0.0                  # 0..1: darken toward the base (a vertical gradient inside each bar)
    stroke: Optional[Color] = None      # outline color, e.g. an ink line "#0b0614"
    stroke_width: float = 2.0
    glow: float = 0.0                   # 0 = none, 1 = strong halo
    min_length: float = 0.03            # so a value at the bottom of y_range stays visible


@dataclass
class Labels:
    values: bool = False
    indices: bool = False
    name: bool = True
    name_position: str = "above"         # "above" | "left" (inside the panel)
    name_margin: float = 1.35            # room reserved for a left-side name
    font: str = "IBM Plex Mono"
    name_font: str = "Inter"
    font_size: float = 16
    name_size: float = 18
    name_weight: str = "NORMAL"          # "NORMAL" | "BOLD" | "LIGHT" ...
    uppercase: bool = True               # small-caps-ish list names
    color: Color = "#e8e4dc"
    muted: Color = "#6b6760"


@dataclass
class Panel:
    fill: Union[Color, Sequence[Color], None] = None   # a color, [bottom, top] for a gradient, or None
    opacity: float = 1.0
    corner_radius: float = 0.0
    stroke: Optional[Color] = None
    stroke_width: float = 1.5


@dataclass
class Axis:
    baseline: bool = True
    color: Color = "#3a3733"
    width: float = 1.5
    ground: float = 0.0                  # > 0: a solid "ground" slab of this thickness under the bars
    ground_color: Color = "#5bb89a"
    ground_stroke: Optional[Color] = None
    ticks: Sequence[float] = ()          # e.g. (300, 400, 500) draws labelled guide lines


@dataclass
class Motion:
    """How one kind of event animates. Only the fields that make sense are used."""
    duration: Optional[float] = None
    easing: Union[str, Callable, None] = None
    color: Optional[Color] = None        # highlight / in-flight color (None = keep the bar's own color)
    path: str = "straight"               # moves: "straight" | "arc" | "hop"
    arc: float = 1.2                     # radians of curvature for path="arc"
    trail: bool = False                  # moves: leave a fading trail
    sparkle: bool = False                # landing sparkle
    squash: bool = False                 # little squash on landing
    exit: str = "fade"                   # pops: "fade" | "float_up_fade" | "shrink" | "drop" | "burst"
    style: str = "pulse"                 # reads/compares: "pulse" | "none"
    lag: float = 0.3                     # when many bars fly at once

    def rate(self, default="ease_in_out_cubic"):
        e = self.easing or default
        return getattr(rate_functions, e) if isinstance(e, str) else e


DEFAULT_MOTION = {
    "create":  Motion(duration=0.5),
    "read":    Motion(duration=0.22, color="#f3e08a"),
    "compare": Motion(duration=0.3,  color="#f3e08a"),
    "push":    Motion(duration=0.7),
    "set":     Motion(duration=0.6),
    "swap":    Motion(duration=0.55),
    "pop":     Motion(duration=0.45),
    "replace": Motion(duration=0.6),
}


@dataclass
class Sound:
    scale: str = "pentatonic"            # pentatonic | major | minor | dorian | lydian | hirajoshi | blues
    key: str = "D"
    octave: int = 4
    instrument: str = "harp"             # harp | bell | marimba | music_box | soft_sine | wood | wood_soft | log_drum
    finale_instrument: str = "bell"
    soft_instrument: str = "soft_sine"   # the quiet notes: pops, recolors, loop returns (try "wood_soft")
    tick_instrument: str = "tick"        # the tiny focus ticks (try "wood_soft")
    grid_instrument: Optional[str] = None  # one instrument for every grid / graph note (None: the original mix)
    humanize: float = 0.0                # 0..1: grid notes get small random differences in pitch (±12 cents at 1),
                                         #   loudness (±2 dB) and timing (±8 ms), so repeats never sound machine-made
    grid_set_pitch: str = "cycle"        # a grid cell changing value: "cycle" walks up the scale · "rank": each distinct
                                         #   new value gets the next scale step (lowest value = lowest note) · "value": the new
                                         #   value is the scale step (e.g. store the minute a cell changed, and later
                                         #   minutes play higher)
    reverb: float = 0.35                 # 0..1 wet mix
    pitch_by_size: str = "up"            # "up": bigger values play higher · "down": bigger play lower, like real
                                         #   objects (a big drum sounds lower than a small one)
    size_gain: float = 0.0               # dB: bigger values play up to this much louder (smaller ones quieter)
    volume: float = 0.8                  # 0..1
    landing_interval: int = 2            # a move plays its note, then this many scale steps up on landing
    tick_reads: bool = False
    compare_notes: bool = False          # a soft note for each comparison (the "sound of sorting")
    finale: bool = True                  # the closing riff
    enabled: bool = True


@dataclass
class Finale:
    target: Optional[str] = "result"     # which list to celebrate (None: skip the bar sweep)
    style: str = "sweep"                 # "sweep": a highlight runs across the bars · "recolor": bars turn `color`
    color: Color = "#f3e08a"
    text: Optional[str] = None
    text_position: Optional[Tuple[float, float]] = None
    font: str = "Inter"
    font_size: float = 34
    letter_spacing: Optional[int] = None  # e.g. 1400: the text is tracked out like the titles (Pango units)
    sparkle: bool = False
    region_buildup: bool = True          # the closing shimmer over Regions (e.g. water) plays a rising run of notes
    count_regions: bool = False          # instead: count the Regions one by one (+area each), recounting the
                                         # Readout from 0, over a rising build-up, then the finishing chord
    count_label_color: Optional[Color] = None   # colour of the "+n" labels (None: `color`)
    grid_ripple: bool = False            # replay a grid's changes as one fast ripple: cells pulse in order of their
                                         # value (lowest first), one rising note per value, then the finishing chord
    grid_ripple_skip: Sequence = (0, 1)  # values that don't take part in the ripple
    ripple_instrument: Optional[str] = None     # the ripple's notes (None: Sound.instrument)
    chord_on_ripple: bool = False        # the finishing chord lands exactly as the ripple ends (no gap between the
                                         #   build-up and its resolution)
    chord_deg: Optional[int] = None      # the finishing chord's root scale step (None: two octaves up)


@dataclass
class Timing:
    speed: float = 1.0                   # global multiplier (2 = twice as fast)
    skip: Sequence[str] = ()             # event types to leave out: "read", "compare"
    pause_between: float = 0.0
    end_hold: float = 2.5
    intro: str = "animate"               # "instant": the first frame already shows the inputs (hooks, clean loops)
    loop: bool = False                   # at the end, everything returns to how the first frame looked
    loop_time: float = 1.1               # how long that return takes


@dataclass
class Grain:
    """Film / print grain added over the finished video (needs the ffmpeg command-line tool)."""
    amount: float = 8                    # 0..~30; 6–12 reads as print texture, 20+ as heavy film
    animated: bool = False               # False: fixed, like paper (small files) · True: "boils" like film (≈5× bigger, slower)
