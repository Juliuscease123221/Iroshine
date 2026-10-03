# Bars

Lists drawn as bars, and everything about how a bar looks.

!!! note "Generated page"
    This page is built from the source by `tools/gen_reference.py`. Edit the comments in the code, not this file.

## BarList

`from iroshine import BarList` · defined in `iroshine/barlist.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `name` | `str` | required | the variable in your solution that this view is bound to |
| `position` | `Tuple[float, float]` | `(0.0, 0.0)` | center of the panel (Manim units, frame ≈ 14.2 × 8) |
| `size` | `Tuple[float, float]` | `(8.0, 2.4)` | its (width, height) in scene units |
| `orientation` | `str` | `"up"` | "up": vertical bars in a row · "right": horizontal bars stacked bottom→top |
| `y_range` | `Tuple[Optional[float], Optional[float]]` | `(None, None)` | bars grow from y_range[0]; None = auto |
| `capacity` | `Optional[int]` | `None` | number of slots; None = longest the list ever gets |
| `bar` | `BarStyle` | `BarStyle()` | how each bar looks: a `BarStyle` |
| `labels` | `Labels` | `Labels()` | show text labels |
| `panel` | `Optional[Panel]` | `Panel()` | the card behind the list: a `Panel`, or None |
| `axis` | `Axis` | `Axis()` | baseline, ground and guide lines: an `Axis` |
| `title` | `Optional[str]` | `None` | text shown instead of the variable name |
| `indexes` | `Optional[str]` | `None` | this list holds *indices* into another list (e.g. a |
| `index_labels` | `bool` | `False` | (indexes view) label each bar with the index it holds, not the value it points at monotonic stack of positions): draw each bar as that element, and fly it in from there |
| `padding` | `float` | `0.18` | space between the edge and the contents |

## BarStyle

`from iroshine import BarStyle` · defined in `iroshine/style.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `shape` | `str` | `"rect"` | "rect" \| "pill" \| "lollipop" |
| `gap` | `Optional[float]` | `None` | space between bars as a fraction of each slot (like D3's paddingInner). 0 = bars touch, 0.2 = 20% gap, None = use `width` instead |
| `outer_gap` | `Optional[float]` | `None` | space before the first / after the last bar, in slots (D3's paddingOuter). None = half of `gap` |
| `seam` | `float` | `1.5` | when gap == 0: overlap neighbours by this many pixels so anti-aliasing never shows a hairline between them |
| `width` | `float` | `0.78` | legacy: bar width as a fraction of each slot (= 1 - gap) |
| `corner_radius` | `float` | `0.0` | how rounded the corners are |
| `fill` | `Fill` | `"#e8e4dc"` | fill colour |
| `opacity` | `float` | `1.0` | 0..1 |
| `shade` | `float` | `0.0` | 0..1: darken toward the base (a vertical gradient inside each bar) |
| `stroke` | `Optional[Color]` | `None` | outline color, e.g. an ink line "#0b0614" |
| `stroke_width` | `float` | `2.0` | outline thickness |
| `glow` | `float` | `0.0` | 0 = none, 1 = strong halo |
| `min_length` | `float` | `0.03` | so a value at the bottom of y_range stays visible |

## Labels

`from iroshine import Labels` · defined in `iroshine/style.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `values` | `bool` | `False` | show each bar's value |
| `indices` | `bool` | `False` | show each bar's index |
| `name` | `bool` | `True` | the variable in your solution that this view is bound to |
| `name_position` | `str` | `"above"` | "above" \| "left" (inside the panel) |
| `name_margin` | `float` | `1.35` | room reserved for a left-side name |
| `font` | `str` | `"IBM Plex Mono"` | font family |
| `name_font` | `str` | `"Inter"` | font family |
| `font_size` | `float` | `16` | text size |
| `name_size` | `float` | `18` | text size |
| `name_weight` | `str` | `"NORMAL"` | "NORMAL" \| "BOLD" \| "LIGHT" ... |
| `uppercase` | `bool` | `True` | small-caps-ish list names |
| `color` | `Color` | `"#e8e4dc"` | colour, as a hex string |
| `muted` | `Color` | `"#6b6760"` | colour of secondary text |

## Panel

`from iroshine import Panel` · defined in `iroshine/style.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `fill` | `Union[Color, Sequence[Color], None]` | `None` | a color, [bottom, top] for a gradient, or None |
| `opacity` | `float` | `1.0` | 0..1 |
| `corner_radius` | `float` | `0.0` | how rounded the corners are |
| `stroke` | `Optional[Color]` | `None` | outline colour (None: no outline) |
| `stroke_width` | `float` | `1.5` | outline thickness |

## Axis

`from iroshine import Axis` · defined in `iroshine/style.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `baseline` | `bool` | `True` | draw a hairline under the bars |
| `color` | `Color` | `"#3a3733"` | colour, as a hex string |
| `width` | `float` | `1.5` | width, in scene units |
| `ground` | `float` | `0.0` | > 0: a solid "ground" slab of this thickness under the bars |
| `ground_color` | `Color` | `"#5bb89a"` | colour, as a hex string |
| `ground_stroke` | `Optional[Color]` | `None` |  |
| `ticks` | `Sequence[float]` | `()` | e.g. (300, 400, 500) draws labelled guide lines |
