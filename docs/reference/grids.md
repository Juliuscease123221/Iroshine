# Grids and graphs

2-D lists, sets of cells, and dependency graphs.

!!! note "Generated page"
    This page is built from the source by `tools/gen_reference.py`. Edit the comments in the code, not this file.

## GridView

`from iroshine import GridView` · defined in `iroshine/grid.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `name` | `str` | required | the 2-D list in your solution |
| `position` | `Tuple[float, float]` | `(0.0, 0.0)` | center |
| `size` | `Tuple[float, float]` | `(8.0, 6.0)` | the grid is fitted inside this box (square cells) |
| `colors` | `Dict[Any, str]` | `{0: "#2b2b2b", 1: "#e8e4dc"}` | {value: colour}, or a function value -> colour: a cell's colour follows its current value |
| `default_color` | `str` | `"#444444"` | for values not in `colors` |
| `gap` | `float` | `0.08` | space between cells, as a fraction of a cell |
| `corner_radius` | `float` | `0.0` | how rounded the corners are |
| `stroke` | `Optional[str]` | `None` | outline colour (None: no outline) |
| `stroke_width` | `float` | `1.5` | outline thickness |
| `unknown` | `Optional[float]` | `0.8` | dim cells the program hasn't read yet (0–1); None = off |
| `unknown_color` | `str` | `"#000000"` | what unknown cells fade toward |
| `forget_when` | `Optional[str]` | `None` | re-creating this set/list makes every cell unknown again |
| `flash` | `Optional[str]` | `"#ffffff"` | outline that blinks on each read (the "cursor"); None = off |
| `flash_opacity` | `float` | `0.9` | 0..1 |
| `marks` | `Dict[str, Mark]` | `dict()` | {set name: Mark}: an overlay on every cell that is a member of that set |
| `walls` | `Optional[Walls]` | `None` | a `Walls` rule for drawing boundaries between cells |
| `rate` | `float` | `40.0` | grid events per second (they play as overlapping waves) |
| `step` | `float` | `0.3` | length of each cell's little animation (s) |
| `like` | `Optional[str]` | `None` | a blank canvas the same shape as another GridView (nothing is bound to it; Stamps draw on it) |
| `blank_color` | `str` | `"#111111"` | canvas cells' color |
| `reads` | `bool` | `True` | False: reading a cell shows nothing and takes no time |
| `set_scale` | `float` | `1.0` | a cell settles at this size when its value changes (e.g. 0.86: it shrivels a little); applied once per cell |
| `set_bounce` | `bool` | `False` | the change overshoots and settles (a little squish) |
| `final_hold` | `float` | `0.0` | a held breath (s) before the wave that makes the grid's last change |
| `final_instrument` | `Optional[str]` | `None` | that last change plays this instead (bigger, the peak) |
| `final_gain` | `float` | `0.0` | loudness, in dB |
| `sizes` | `Dict[Any, float]` | `dict()` | cells of these values start smaller, e.g. {0: 0.3} (empty spots recede as small dots) |

## Mark

`from iroshine import Mark` · defined in `iroshine/grid.py`

How members of a named set are drawn on a GridView. Members must be (row, col) pairs.

| Option | Type | Default | What it does |
|---|---|---|---|
| `fill` | `Optional[str]` | `None` | fill colour |
| `fill_opacity` | `float` | `0.35` | 0..1 |
| `stroke` | `Optional[str]` | `None` | outline colour (None: no outline) |
| `stroke_width` | `float` | `3.0` | outline thickness |
| `shape` | `str` | `"cell"` | "cell" (fills the cell) \| "ring" (outline) \| "dot" |
| `inset` | `float` | `0.12` | how far inside the cell edge (fraction of a cell) |
| `keep` | `bool` | `False` | when the set is re-created, keep old marks (faded) instead of clearing |
| `kept_opacity` | `float` | `0.4` | how visible kept marks stay (relative) |
| `sound` | `bool` | `True` | whether it plays a note |

## Walls

`from iroshine import Walls` · defined in `iroshine/grid.py`

Draw walls on cell edges between two kinds of values, e.g. between=(-1, 0).

| Option | Type | Default | What it does |
|---|---|---|---|
| `between` | `Tuple[Any, Any]` | `(-1, 0)` | draw a wall on every edge between a cell with the first value and one with the second |
| `color` | `str` | `"#ffffff"` | colour, as a hex string |
| `width` | `float` | `6.0` | width, in scene units |
| `sticky` | `bool` | `True` | once built, a wall stays even if the cells change later |
| `sound` | `bool` | `True` | whether it plays a note |

## GridBoxes

`from iroshine import GridBoxes` · defined in `iroshine/grid.py`

One outline per id, from four parallel arrays of bounds, e.g. top[c], bottom[c], left[c], right[c].

Every time your code writes one of those arrays, the box for that index is redrawn,
so you can watch bounding boxes grow as the scan discovers them. An id's box shows
once it is valid (top <= bottom and left <= right).

| Option | Type | Default | What it does |
|---|---|---|---|
| `on` | `str` | required | the GridView the boxes sit on |
| `top` | `str` | `"top"` | name of the list holding each box's top row |
| `bottom` | `str` | `"bottom"` | name of the list holding each box's bottom row |
| `left` | `str` | `"left"` | name of the list holding each box's left column |
| `right` | `str` | `"right"` | name of the list holding each box's right column |
| `color` | `Optional[str]` | `None` | None = the grid's color for that id |
| `stroke_width` | `float` | `3.5` | outline thickness |
| `opacity` | `float` | `0.95` | 0..1 |
| `brighten` | `float` | `0.25` | lift the grid color a little so the outline reads |

## Stamp

`from iroshine import Stamp` · defined in `iroshine/grid.py`

Print a solid block onto a GridView (usually a blank `like=` canvas) whenever a variable changes.

    Stamp(on="printer", when="layer",
          rows=("top[layer]", "bottom[layer]"), cols=("left[layer]", "right[layer]"),
          value="layer")                 # the color comes from the grid's colors for this value

Expressions are evaluated against your solution's local variables at that moment.

| Option | Type | Default | What it does |
|---|---|---|---|
| `on` | `str` | required | the name of the list or grid it is drawn on |
| `when` | `str` | required | the variable whose change triggers it |
| `rows` | `Tuple[str, str]` | required | number of rows |
| `cols` | `Tuple[str, str]` | required | number of columns |
| `value` | `Optional[str]` | `None` | expression whose grid color fills the block |
| `fill` | `Optional[str]` | `None` | or a fixed color |
| `opacity` | `float` | `1.0` | 0..1 |
| `stroke` | `Optional[str]` | `None` | outline colour (None: no outline) |
| `stroke_width` | `float` | `2.0` | outline thickness |
| `duration` | `float` | `0.7` | seconds the animation takes |
| `press` | `float` | `1.06` | starts this much bigger, then settles (a stamp "press") |

## GraphView

`from iroshine import GraphView` · defined in `iroshine/graph.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `adj` | `str` | required | the adjacency list: adj[u] is a set of v |
| `position` | `Tuple[float, float]` | `(0.0, 0.0)` | where it sits on the stage, as (x, y) in scene units (the stage is 8 units tall, centred on 0, 0) |
| `size` | `Tuple[float, float]` | `(8.0, 1.6)` | line layout: width × arc room; circle: diameter |
| `layout` | `str` | `"line"` |  |
| `node_radius` | `float` | `0.2` |  |
| `node_colors` | `Any` | `None` | "grid:<name>" to borrow a GridView's colors, a dict, or a color |
| `node_stroke` | `str` | `"#ffffff"` |  |
| `labels` | `bool` | `True` | show text labels |
| `label_font` | `str` | `"IBM Plex Mono"` | font family |
| `label_size` | `float` | `14` | text size |
| `label_color` | `str` | `"#000000"` | colour, as a hex string |
| `edge_color` | `str` | `"#ffffff"` | colour, as a hex string |
| `edge_width` | `float` | `2.5` | line thickness |
| `edge_opacity` | `float` | `0.75` | 0..1 |
| `arc` | `float` | `1.1` | arc curvature (radians) |
| `done_when` | `Optional[str]` | `None` | a variable: when it takes value u, node u is finished |
| `done_edge_opacity` | `float` | `0.12` | 0..1 |
| `dim` | `float` | `0.7` | untouched nodes start dimmed toward the background |
| `background` | `str` | `"#000000"` | background colour |
