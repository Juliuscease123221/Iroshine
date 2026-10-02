"""
iroshine — turn your algorithm into a beautiful, musical animation.

You compose a Stage from objects (BarList, CodePanel, Caption, any Manim
mobject), style every detail, run your solution, and render.
"""

from .barlist import BarList
from .components import Caption, CodePanel, Pack, Pointer, Readout, Region, Tower
from .stage import HookContext, Stage
from .grid import GridBoxes, GridView, Mark, Stamp, Walls
from .graph import GraphView
from .geometry import PointSet, PointStrip, Polyline
from .text import LineComposer, WordStrip
from .story import Beat, Beats
from .crossing import WallToWall
from .tiling import TilingView
from .code_styles import code_style
from .palettes import DARK_CHERRY, DUSK, ELYSIUM, GARDEN, LAKE, Palette
from .style import Axis, BarStyle, Finale, Gradient, Grain, Labels, Motion, Panel, Sound, Timing

__all__ = ["Stage", "BarList", "BarStyle", "Gradient", "Labels", "Panel", "Axis",
           "Motion", "Sound", "Finale", "Timing", "Grain", "CodePanel", "Caption", "HookContext",
           "Palette", "DUSK", "GARDEN", "ELYSIUM", "DARK_CHERRY", "LAKE",
           "Pointer", "Readout", "Region", "Pack", "GridView", "Mark", "Walls",
           "GridBoxes", "Stamp", "GraphView", "PointSet", "Polyline", "WordStrip", "LineComposer", "Tower", "Beat", "Beats", "PointStrip", "WallToWall", "code_style", "TilingView"]
