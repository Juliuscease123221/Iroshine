# Variables

Views that follow plain local variables in your solution.

!!! note "Generated page"
    This page is built from the source by `tools/gen_reference.py`. Edit the comments in the code, not this file.

## Pointer

`from iroshine import Pointer` · defined in `iroshine/components.py`

A marker that follows an index variable along a BarList (e.g. `i`, `left`, `right`).

| Option | Type | Default | What it does |
|---|---|---|---|
| `var` | `str` | required | the variable in your solution it follows |
| `on` | `str` | required | name of the BarList it points into |
| `label` | `Optional[str]` | `None` | text under the marker (default: the variable name) |
| `color` | `str` | `"#e8e4dc"` | colour, as a hex string |
| `size` | `float` | `0.13` | how big it is, in scene units |
| `offset` | `float` | `0.22` | gap below the baseline / ground |
| `font` | `str` | `"IBM Plex Mono"` | font family |
| `font_size` | `float` | `16` | text size |
| `guide` | `bool` | `False` | also draw a faint vertical line through the slot |
| `guide_opacity` | `float` | `0.25` | 0..1 |

## Readout

`from iroshine import Readout` · defined in `iroshine/components.py`

A big number that counts up/down as a variable changes (e.g. `water`, `best`, `ans`).

| Option | Type | Default | What it does |
|---|---|---|---|
| `var` | `str` | required | the variable in your solution it follows |
| `position` | `Tuple[float, float]` | `(-6.4, 2.6)` | left edge, vertical center of the number |
| `label` | `Optional[str]` | `None` | small caption above the number |
| `format` | `str` | `"{:,.0f}"` | a Python format string for the number |
| `font` | `str` | `"Inter"` | font family |
| `weight` | `str` | `"LIGHT"` | font weight |
| `font_size` | `float` | `64` | text size |
| `color` | `str` | `"#e8e4dc"` | colour, as a hex string |
| `label_font` | `str` | `"Inter"` | font family |
| `label_size` | `float` | `13` | text size |
| `label_color` | `str` | `"#6b6760"` | colour, as a hex string |
| `count` | `bool` | `True` | animate through the in-between numbers |
| `result` | `bool` | `False` | at the end, count on to the function's return value |
| `result_label` | `Optional[str]` | `None` | …and the caption changes to this (e.g. "day" → "last day") |
| `finish_color` | `Optional[str]` | `None` | the colour it settles on at the end (None: the finale colour) |
| `sound` | `Optional[str]` | `None` | a note each time the value changes (e.g. a clock tick for `minute`) |
| `sound_deg` | `int` | `0` | its scale step |
| `sound_gain` | `float` | `-14.0` | loudness, in dB |
| `merge` | `bool` | `False` | inside a grid wave, a new value replaces the pending one instead of ending the wave (for counters that change every cell, e.g. `fresh`) |

## Region

`from iroshine import Region` · defined in `iroshine/components.py`

A filled shape added to a BarList whenever a variable changes.

Coordinates are expressions evaluated against your solution's local variables at
that moment. x0/x1 are slot indices (inclusive); y0/y1 are values on the list's scale.

    Region(on="height", when="water",
           x0="left + 1", x1="i - 1",
           y0="height[top]", y1="min(height[left], height[i])")

Each coordinate can also be a function taking a dict of locals.

| Option | Type | Default | What it does |
|---|---|---|---|
| `on` | `str` | required | the name of the list or grid it is drawn on |
| `when` | `str` | required | the variable whose change triggers it |
| `x0` | `Union[str, Callable]` | required | left edge: an expression over your solution's local variables, or a function of them |
| `x1` | `Union[str, Callable]` | required | right edge (same form as x0) |
| `y0` | `Union[str, Callable]` | required | bottom edge (same form as x0) |
| `y1` | `Union[str, Callable]` | required | top edge (same form as x0) |
| `fill` | `Union[str, Sequence[str]]` | `"#277879"` | a color, or [bottom, top] for a vertical gradient |
| `opacity` | `float` | `0.92` | 0..1 |
| `stroke` | `Optional[str]` | `None` | outline colour (None: no outline) |
| `stroke_width` | `float` | `1.5` | outline thickness |
| `surface` | `Optional[str]` | `None` | a thin line along the top edge (a water surface) |
| `sound` | `Optional[str]` | `None` | instrument for the note it plays (None: the finale instrument) |
| `sound_gain` | `float` | `-5.0` | its loudness in dB |
| `surface_width` | `float` | `3` | line thickness |
| `duration` | `float` | `0.7` | seconds the animation takes |
| `note` | `bool` | `True` | play a note when it appears |

## Pack

`from iroshine import Pack` · defined in `iroshine/components.py`

Collect every shape a Region draws and assemble them into one near-square block.

Each time the Region adds a piece, a copy flies over and settles into its slot,
so the total becomes a picture of the answer. The layout is solved up front
(see packing.py), so pieces land in their final places as the run goes.

    Pack(region=water_region, position=(-3, 2.4), size=(2.6, 1.8), rotate=False)

rotate=False  pieces keep their orientation (width stays horizontal)
rotate=True   pieces may turn 90° to make the block tighter / squarer
Cells are square: one unit of width × one unit of value.

| Option | Type | Default | What it does |
|---|---|---|---|
| `region` | `Any` | required | the Region whose shapes get collected |
| `position` | `Tuple[float, float]` | `(0.0, 2.4)` | center of the assembled block |
| `size` | `Tuple[float, float]` | `(2.6, 1.8)` | the block is scaled to fit inside this box |
| `rotate` | `bool` | `False` | let pieces turn 90° if that packs squarer |
| `fill` | `Any` | `None` | None = the region's fill; a color; or a Gradient (colored by the order pieces arrive) |
| `opacity` | `float` | `0.95` | 0..1 |
| `stroke` | `Optional[str]` | `None` | a line between pieces (e.g. the background color) |
| `stroke_width` | `float` | `2.5` | outline thickness |
| `duration` | `float` | `0.8` | seconds the animation takes |
| `easing` | `str` | `"ease_in_out_cubic"` | the name of a Manim rate function, e.g. "ease_in_out_cubic" |
| `outline` | `Optional[str]` | `None` | a faint outline of the final block, shown from the start |
| `outline_opacity` | `float` | `0.35` | 0..1 |

## Tower

`from iroshine import Tower` · defined in `iroshine/components.py`

A column that grows by one block each time a variable increases (a running total).

It shares a BarList's scale and baseline, so its height is directly comparable to the
bars. If the increase came from list values (ans += f[k]), a copy of that bar flies
over and becomes the new block. With show_result, the function's return value
tops it off (e.g. the final "+ 1").

| Option | Type | Default | What it does |
|---|---|---|---|
| `var` | `str` | required | the variable in your solution it follows |
| `on` | `str` | required | the BarList whose scale and baseline it uses |
| `x` | `float` | `5.5` |  |
| `width` | `float` | `0.9` | width, in scene units |
| `fill` | `Any` | `None` | None = each block keeps its source bar's color; or a color, or a Gradient over the block order |
| `stroke` | `Optional[str]` | `"#000000"` | a line between blocks |
| `stroke_width` | `float` | `2.5` | outline thickness |
| `extra_fill` | `Optional[str]` | `None` |  |
| `labels` | `bool` | `False` | write each block's size inside it (when it fits) |
| `label_color` | `str` | `"#ffffff"` | colour, as a hex string |
| `label_size` | `float` | `14` | text size |
| `finale` | `bool` | `True` | at the end, the blocks ring out bottom to top                 # color of a block with no source (e.g. the final + 1) |
| `show_result` | `bool` | `True` |  |
| `duration` | `float` | `0.8` | seconds the animation takes |
