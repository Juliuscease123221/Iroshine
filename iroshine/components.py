"""
iroshine.components — optional extras you can place on the stage.

    CodePanel  your solution's source with a highlight that follows the running line
    Caption    a one-line narration of each step ("stack.append(5) ← from nums2[1]")

Anything else? Pass any Manim mobject to stage.add() — titles, arrows, LaTeX...
"""

from dataclasses import dataclass
from typing import Optional, Tuple

from manim import DOWN, LEFT, UP, Code, ManimColor, Rectangle, RoundedRectangle, Text


@dataclass
class CodePanel:
    position: Tuple[float, float] = (4.6, 1.8)     # center
    width: float = 4.6
    style: str = "github-dark"                     # any Pygments style: github-dark, monokai, nord, friendly...
    background: str = "#0b0b0b"
    border: Optional[str] = None
    highlight: str = "#f3e08a"
    highlight_opacity: float = 0.14
    font: str = "IBM Plex Mono"
    line_numbers: bool = True
    glide: bool = False                            # the highlight glides smoothly to every line the code runs
    glide_speed: float = 14.0                      # how quickly it catches up (higher = snappier)
    span: str = "line"                             # (glide) "line": the running line · "loop": the whole outermost
                                                   # loop while the code is inside it (calmer: no flicking back and forth)
                                                   # · "inner": the innermost loop block (e.g. a while inside a for),
                                                   #   single lines elsewhere
    corner_radius: float = 0.0
    padding: float = 0.0                           # space around the code inside the panel (0 = Manim's default)
    show: Optional[Tuple[str, str]] = None         # crop to the core: from the first line containing show[0] to the
                                                   # first line after it containing show[1] (dedented; bigger text)
    follow_batches: bool = False                   # (glide) inside a grid wave, follow the line that changes cells
                                                   # (otherwise the highlight stays on the wave's first line)

    def build(self, source):
        self._offset = 0
        if self.show:
            import textwrap
            src = source.splitlines()
            a = next(i for i, s in enumerate(src) if self.show[0] in s)
            z = next(i for i, s in enumerate(src) if i > a and self.show[1] in s)
            self._offset, self._count = a, z - a + 1
            source = textwrap.dedent("\n".join(src[a:z + 1]))
        self.code = Code(code_string=source, language="python", formatter_style=self.style,
                         add_line_numbers=self.line_numbers, background="rectangle",
                         background_config={"fill_color": ManimColor(self.background),
                                            "stroke_color": ManimColor(self.border or self.background),
                                            "stroke_width": 1.5 if self.border else 0,
                                            **({"corner_radius": self.corner_radius, "buff": self.padding or 0.3}
                                               if self.corner_radius or self.padding else {})},
                         paragraph_config={"font": self.font})
        self.code.scale_to_fit_width(self.width).move_to([*self.position, 0])
        first = self.code.code_lines[0]
        self.hl = Rectangle(width=self.code.width - 0.08, height=first.height * 1.9,
                            fill_color=ManimColor(self.highlight), fill_opacity=0, stroke_width=0)
        self.hl.move_to([self.code.get_x(), first.get_y(), 0])
        L = self.code.code_lines
        self._pitch = abs(L[0].get_y() - L[1].get_y()) if len(L) > 1 else first.height * 1.9
        self._loops = _loop_spans(source, inner=self.span == "inner") if self.span in ("loop", "inner") else {}
        if self.glide:
            self._ty, self._th, self._on = None, None, 0.0
            self.hl.stretch_to_fit_height(self._pitch)

            def follow(m, dt):
                if self._ty is None:
                    return
                k = min(1.0, dt * self.glide_speed)
                h = m.height + (self._th - m.height) * k
                m.stretch_to_fit_height(max(h, 1e-3))
                m.set_y(m.get_y() + (self._ty - m.get_y()) * k)
                self._on += (1.0 - self._on) * k
                m.set_fill(opacity=self.highlight_opacity * self._on)
            self.hl.add_updater(follow)
        return [self.code, self.hl]

    def _local(self, line):
        if not line:
            return None
        line -= self._offset
        return line if 1 <= line <= len(self.code.code_lines) else None

    def target(self, line):
        """(glide mode) Set the line (or loop) the highlight should drift to."""
        L = self.code.code_lines
        line = self._local(line)
        if not line or line > len(L):
            return
        a, z = self._loops.get(line, (line, line))
        a, z = max(1, a), min(len(L), z)
        top, bot = L[a - 1].get_y(), L[z - 1].get_y()
        self._ty = (top + bot) / 2
        self._th = (top - bot) + self._pitch

    def release(self):
        """(glide mode) Stop following and fade out."""
        self.hl.clear_updaters()
        self._ty = None

    def goto(self, line):
        if self.glide:
            self.target(line)
            return []
        line = self._local(line)
        if not line or line > len(self.code.code_lines):
            return []
        y = self.code.code_lines[line - 1].get_y()
        return [self.hl.animate.set_fill(opacity=self.highlight_opacity).move_to([self.hl.get_x(), y, 0])]

    def clear(self):
        if self.glide:
            self.release()
        return [self.hl.animate.set_fill(opacity=0)]


@dataclass
class Caption:
    position: Tuple[float, float] = (-6.8, -3.65)  # left edge, vertical center
    font: str = "IBM Plex Mono"
    font_size: float = 18
    color: str = "#6b6760"

    def show(self, scene, text):
        new = Text(text, font=self.font, font_size=self.font_size, color=ManimColor(self.color))
        new.move_to([*self.position, 0], aligned_edge=LEFT)
        if getattr(self, "_current", None) is not None:
            scene.remove(self._current)
        scene.add(new)
        self._current = new


# ═════════════════════════════════════════ components driven by variables ══
# These watch plain local variables in your solution (ints, floats, lists) and
# animate when they change. The Stage figures out which names to watch.

from typing import Any, Callable, Sequence, Union   # noqa: E402

from manim import (RIGHT, Line, Triangle, ValueTracker, VGroup, always_redraw,  # noqa: E402
                   MarkupText)


@dataclass
class Pointer:
    """A marker that follows an index variable along a BarList (e.g. `i`, `left`, `right`)."""
    var: str
    on: str                                   # name of the BarList it points into
    label: Optional[str] = None               # text under the marker (default: the variable name)
    color: str = "#e8e4dc"
    size: float = 0.13
    offset: float = 0.22                      # gap below the baseline / ground
    font: str = "IBM Plex Mono"
    font_size: float = 16
    guide: bool = False                       # also draw a faint vertical line through the slot
    guide_opacity: float = 0.25

    def build(self, view):
        y = view.base - view.axis.ground - self.offset - self.size
        tri = Triangle(fill_color=ManimColor(self.color), fill_opacity=1, stroke_width=0).scale(self.size)
        tri.move_to([view.slot_center(0), y, 0])
        lab = Text(self.label if self.label is not None else self.var, font=self.font,
                   font_size=self.font_size, color=ManimColor(self.color))
        lab.next_to(tri, DOWN, buff=0.06)
        parts = [tri, lab]
        if self.guide:                       # a faint column highlight through the whole list
            g = Line([view.slot_center(0), view.base, 0], [view.slot_center(0), view.top, 0],
                     stroke_width=view.slot * 60, color=ManimColor(self.color)).set_opacity(self.guide_opacity)
            parts.insert(0, g)
            self._guide = g
        self.mob = VGroup(*parts)
        self.view, self.shown, self.at = view, False, 0
        return self.mob

    def reveal(self):
        """Animations that show the pointer at its natural opacities (the guide stays faint)."""
        anims = [m.animate.set_opacity(1) for m in self.mob if m is not getattr(self, "_guide", None)]
        if getattr(self, "_guide", None) is not None:
            anims.append(self._guide.animate.set_stroke(opacity=self.guide_opacity))
        return anims

    def spot(self, index):
        dx = self.view.slot_center(index) - self.view.slot_center(self.at)
        self.at = index
        return [dx, 0, 0]


@dataclass
class Readout:
    """A big number that counts up/down as a variable changes (e.g. `water`, `best`, `ans`)."""
    var: str
    position: Tuple[float, float] = (-6.4, 2.6)   # left edge, vertical center of the number
    label: Optional[str] = None                   # small caption above the number
    format: str = "{:,.0f}"
    font: str = "Inter"
    weight: str = "LIGHT"
    font_size: float = 64
    color: str = "#e8e4dc"
    label_font: str = "Inter"
    label_size: float = 13
    label_color: str = "#6b6760"
    count: bool = True                            # animate through the in-between numbers
    result: bool = False                          # at the end, count on to the function's return value
    result_label: Optional[str] = None            # …and the caption changes to this (e.g. "day" → "last day")
    finish_color: Optional[str] = None            # the colour it settles on at the end (None: the finale colour)
    sound: Optional[str] = None                   # a note each time the value changes (e.g. a clock tick for `minute`)
    sound_deg: int = 0                            # its scale step
    sound_gain: float = -14.0
    merge: bool = False                           # inside a grid wave, a new value replaces the pending one instead of
                                                  # ending the wave (for counters that change every cell, e.g. `fresh`)

    def build(self):
        self.tracker = ValueTracker(0)
        pos = [*self.position, 0]

        def number():
            t = Text(self.format.format(self.tracker.get_value()), font=self.font, weight=self.weight,
                     font_size=self.font_size, color=ManimColor(self.color))
            return t.move_to(pos, aligned_edge=LEFT)

        self.number = always_redraw(number)
        parts = [self.number]
        if self.label:
            cap = MarkupText(f'<span letter_spacing="1800">{self.label.upper()}</span>', font=self.label_font,
                             font_size=self.label_size, color=ManimColor(self.label_color))
            cap.move_to([pos[0], pos[1] + self.font_size / 64 * 0.62, 0], aligned_edge=LEFT)
            parts.append(cap)
        self.mob = VGroup(*parts)
        self.shown = False
        return self.mob


@dataclass
class Region:
    """A filled shape added to a BarList whenever a variable changes.

    Coordinates are expressions evaluated against your solution's local variables at
    that moment. x0/x1 are slot indices (inclusive); y0/y1 are values on the list's scale.

        Region(on="height", when="water",
               x0="left + 1", x1="i - 1",
               y0="height[top]", y1="min(height[left], height[i])")

    Each coordinate can also be a function taking a dict of locals.
    """
    on: str
    when: str
    x0: Union[str, Callable]
    x1: Union[str, Callable]
    y0: Union[str, Callable]
    y1: Union[str, Callable]
    fill: Union[str, Sequence[str]] = "#277879"    # a color, or [bottom, top] for a vertical gradient
    opacity: float = 0.92
    stroke: Optional[str] = None
    stroke_width: float = 1.5
    surface: Optional[str] = None                  # a thin line along the top edge (a water surface)
    sound: Optional[str] = None                    # instrument for the note it plays (None: the finale instrument)
    sound_gain: float = -5.0                       # its loudness in dB
    surface_width: float = 3
    duration: float = 0.7
    note: bool = True                              # play a note when it appears

    def eval(self, key, env):
        expr = getattr(self, key)
        if callable(expr):
            return expr(env)
        safe = {"__builtins__": {}, "min": min, "max": max, "abs": abs, "len": len, "sum": sum}
        return eval(expr, safe, dict(env))

    def build(self, view, env):
        try:
            x0, x1 = int(self.eval("x0", env)), int(self.eval("x1", env))
            y0, y1 = float(self.eval("y0", env)), float(self.eval("y1", env))
        except Exception:
            return None
        if x1 < x0 or y1 <= y0:
            return None
        from manim import Rectangle
        up = view.orientation == "up"
        a = view.slot_center(x0) - view.slot / 2
        b = view.slot_center(x1) + view.slot / 2
        c, d = view.value_pos(y0), view.value_pos(y1)
        w, h = (b - a, d - c) if up else (d - c, b - a)
        rect = Rectangle(width=w, height=h).move_to([(a + b) / 2, (c + d) / 2, 0] if up
                                                     else [(c + d) / 2, (a + b) / 2, 0])
        if isinstance(self.fill, (list, tuple)):
            rect.set_fill([ManimColor(x) for x in self.fill], opacity=self.opacity).set_sheen_direction(UP)
        else:
            rect.set_fill(ManimColor(self.fill), opacity=self.opacity)
        rect.set_stroke(ManimColor(self.stroke) if self.stroke else None,
                        width=self.stroke_width if self.stroke else 0)
        g = VGroup(rect)
        if self.surface:
            g.add(Line(rect.get_corner(UP + LEFT), rect.get_corner(UP + RIGHT),
                       color=ManimColor(self.surface), stroke_width=self.surface_width))
        g.depth = y1 - y0
        g.area = (x1 - x0 + 1) * (y1 - y0)
        return g


@dataclass
class Pack:
    """Collect every shape a Region draws and assemble them into one near-square block.

    Each time the Region adds a piece, a copy flies over and settles into its slot,
    so the total becomes a picture of the answer. The layout is solved up front
    (see packing.py), so pieces land in their final places as the run goes.

        Pack(region=water_region, position=(-3, 2.4), size=(2.6, 1.8), rotate=False)

    rotate=False  pieces keep their orientation (width stays horizontal)
    rotate=True   pieces may turn 90° to make the block tighter / squarer
    Cells are square: one unit of width × one unit of value.
    """
    region: Any                                   # the Region whose shapes get collected
    position: Tuple[float, float] = (0.0, 2.4)    # center of the assembled block
    size: Tuple[float, float] = (2.6, 1.8)        # the block is scaled to fit inside this box
    rotate: bool = False
    fill: Any = None                              # None = the region's fill; a color; or a Gradient
                                                  #   (colored by the order pieces arrive)
    opacity: float = 0.95
    stroke: Optional[str] = None                  # a line between pieces (e.g. the background color)
    stroke_width: float = 2.5
    duration: float = 0.8
    easing: str = "ease_in_out_cubic"
    outline: Optional[str] = None                 # a faint outline of the final block, shown from the start
    outline_opacity: float = 0.35

    def plan(self, sizes):
        from .packing import pack_square
        self.sizes = sizes
        self.placed, (W, H) = pack_square(sizes, rotate=self.rotate)
        self.W, self.H = W, H
        self.cell = min(self.size[0] / max(1, W), self.size[1] / max(1, H))
        self.origin = (self.position[0] - W * self.cell / 2, self.position[1] - H * self.cell / 2)
        self.count = 0

    def color(self, k):
        from .gradient import Gradient
        f = self.fill if self.fill is not None else self.region.fill
        if isinstance(f, Gradient):
            return f.at(k / max(1, len(self.sizes) - 1))
        if isinstance(f, (list, tuple)):
            return ManimColor(f[-1])
        return ManimColor(f)

    def target(self, k):
        """(center, unrotated width, unrotated height, rotated?) for piece k, in scene units."""
        x, y, w, h, rot = self.placed[k]
        c = self.cell
        cx = self.origin[0] + (x + w / 2) * c
        cy = self.origin[1] + (y + h / 2) * c
        W0, H0 = self.sizes[k]
        return [cx, cy, 0], W0 * c, H0 * c, rot

    def ghost(self):
        from manim import Rectangle
        if not self.outline:
            return None
        r = Rectangle(width=self.W * self.cell, height=self.H * self.cell).move_to([*self.position, 0])
        return r.set_fill(opacity=0).set_stroke(ManimColor(self.outline), width=1.5, opacity=self.outline_opacity)



@dataclass
class Tower:
    """A column that grows by one block each time a variable increases (a running total).

    It shares a BarList's scale and baseline, so its height is directly comparable to the
    bars. If the increase came from list values (ans += f[k]), a copy of that bar flies
    over and becomes the new block. With show_result, the function's return value
    tops it off (e.g. the final "+ 1").
    """
    var: str
    on: str                                          # the BarList whose scale and baseline it uses
    x: float = 5.5
    width: float = 0.9
    fill: Any = None                                 # None = each block keeps its source bar's color;
                                                     #   or a color, or a Gradient over the block order
    stroke: Optional[str] = "#000000"                # a line between blocks
    stroke_width: float = 2.5
    extra_fill: Optional[str] = None
    labels: bool = False                          # write each block's size inside it (when it fits)
    label_color: str = "#ffffff"
    label_size: float = 14
    finale: bool = True                           # at the end, the blocks ring out bottom to top                 # color of a block with no source (e.g. the final + 1)
    show_result: bool = True
    duration: float = 0.8


def _loop_spans(source, inner=False):
    """line -> (first, last) line of the outermost for / while loop that contains it.
    inner=True: only loops with no loop inside them count (other lines stay single lines)."""
    import ast
    import textwrap
    try:
        tree = ast.parse(textwrap.dedent(source))
    except SyntaxError:
        return {}
    spans = {}
    if inner:
        loops = (ast.For, ast.While, ast.AsyncFor)
        for n in ast.walk(tree):
            if isinstance(n, loops) and not any(isinstance(c, loops) for c in ast.walk(n) if c is not n):
                for ln in range(n.lineno, n.end_lineno + 1):
                    spans[ln] = (n.lineno, n.end_lineno)
        return spans

    def visit(node, inside):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) and inside is None:
                visit(ch, None)                           # nested helpers keep their own lines
            elif isinstance(ch, (ast.For, ast.While, ast.AsyncFor)) and inside is None:
                a, z = ch.lineno, ch.end_lineno
                for ln in range(a, z + 1):
                    spans[ln] = (a, z)
                visit(ch, (a, z))
            else:
                visit(ch, inside)
    visit(tree, None)
    return spans
