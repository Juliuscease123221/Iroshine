# Geometry

Points and paths.

!!! note "Generated page"
    This page is built from the source by `tools/gen_reference.py`. Edit the comments in the code, not this file.

## PointSet

`from iroshine import PointSet` · defined in `iroshine/geometry.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `name` | `str` | required | the variable in your solution that this view is bound to |
| `position` | `Tuple[float, float]` | `(0.0, 0.0)` | where it sits on the stage, as (x, y) in scene units (the stage is 8 units tall, centred on 0, 0) |
| `size` | `Tuple[float, float]` | `(10.0, 6.0)` | its (width, height) in scene units |
| `x_range` | `Optional[Tuple[float, float]]` | `None` | None = fit the data |
| `y_range` | `Optional[Tuple[float, float]]` | `None` |  |
| `margin` | `float` | `0.06` |  |
| `radius` | `float` | `0.09` |  |
| `fill` | `Any` | `"#ffffff"` | a color, or a Gradient (by the list's current order) |
| `stroke` | `Optional[str]` | `None` | outline colour (None: no outline) |
| `stroke_width` | `float` | `1.5` | outline thickness |
| `focus` | `Optional[str]` | `None` | variable holding the current point |
| `focus_color` | `str` | `"#ffffff"` | colour, as a hex string |
| `flash_reads` | `bool` | `False` |  |
| `grid` | `bool` | `False` | faint dotted graph lines behind the points |
| `grid_step` | `float` | `1.0` | in data units |
| `grid_color` | `str` | `"#000000"` | colour, as a hex string |
| `grid_opacity` | `float` | `0.12` | 0..1 |
| `grid_major` | `int` | `0` | every Nth line a bit stronger (0 = all the same) |
| `grid_width` | `float` | `1.2` | line thickness |

## Polyline

`from iroshine import Polyline` · defined in `iroshine/geometry.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `name` | `str` | required | a list of points used as a stack (append / pop) |
| `on` | `str` | required | the PointSet whose coordinates it uses |
| `color` | `str` | `"#ffffff"` | colour, as a hex string |
| `width` | `float` | `5.0` | width, in scene units |
| `vertex_radius` | `float` | `0.12` |  |
| `vertex_color` | `Optional[str]` | `None` | None = the line color |
| `probe` | `Optional[str]` | `None` | variable holding the candidate point |
| `probe_color` | `str` | `"#ffffff"` | colour, as a hex string |
| `probe_opacity` | `float` | `0.55` | 0..1 |
| `fill` | `Optional[str]` | `None` | fill the closed shape at the end |
| `fill_opacity` | `float` | `0.35` | 0..1 |
| `buildup` | `bool` | `True` | the closing sweep over the posts plays a rising run of notes |
| `push_time` | `float` | `0.45` | seconds |
| `pop_time` | `float` | `0.35` | seconds |
| `ghost` | `bool` | `False` | show the final shape faintly from the start (the promise) |
| `ghost_opacity` | `float` | `0.3` | 0..1 |
| `ghost_dash` | `float` | `0.07` |  |
| `loop` | `bool` | `False` | at the very end, return to the opening frame |

## PointStrip

`from iroshine import PointStrip` · defined in `iroshine/geometry.py`

A list of points shown as a row of chips (each tinted like its dot), that changes live.

    PointStrip("trees", on="trees", cursor="p")    # the input: reorders when sorted; a ring follows p
    PointStrip("hull",  on="trees", stack=True)    # a stack: pushed chips fly in from `source`, pops lift away

Chips wrap onto new rows every `per_row`. Pairs with a PointSet (for colors) and plays alongside
the fence animation rather than after it.

| Option | Type | Default | What it does |
|---|---|---|---|
| `name` | `str` | required | the list in your solution |
| `on` | `str` | required | the PointSet whose dots give the chips their colors |
| `position` | `Tuple[float, float]` | `(0.0, -1.0)` | top-left corner of the strip |
| `width` | `float` | `3.4` | width, in scene units |
| `per_row` | `int` | `7` |  |
| `chip_height` | `float` | `0.21` |  |
| `gap` | `float` | `0.06` | space between neighbours, as a fraction of one slot |
| `row_gap` | `float` | `0.07` |  |
| `label` | `Optional[str]` | `None` | small caption above the chips |
| `label_color` | `str` | `"#6f7a6c"` | colour, as a hex string |
| `label_size` | `float` | `8` | text size |
| `label_spacing` | `int` | `1400` | tracking for the all-caps caption |
| `ink` | `str` | `"#2f352e"` | coordinate text |
| `font` | `str` | `"IBM Plex Mono"` | font family |
| `border` | `Optional[str]` | `None` | chip outline (e.g. the fence color for the stack) |
| `border_width` | `float` | `2.0` | line thickness |
| `cursor` | `Optional[str]` | `None` | variable holding the current point: a ring follows it |
| `cursor_color` | `str` | `"#2f352e"` | colour, as a hex string |
| `source` | `Optional[str]` | `None` | the strip pushed points fly in from |
| `stack` | `bool` | `False` |  |
| `loop` | `bool` | `False` | at the very end, return to the opening state |
