# Text

Lists of strings as word tiles and typeset lines.

!!! note "Generated page"
    This page is built from the source by `tools/gen_reference.py`. Edit the comments in the code, not this file.

## WordStrip

`from iroshine import WordStrip` · defined in `iroshine/text.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `name` | `str` | required | the list of words in your solution |
| `position` | `Tuple[float, float]` | `(0.0, 2.3)` | where it sits on the stage, as (x, y) in scene units (the stage is 8 units tall, centred on 0, 0) |
| `size` | `Tuple[float, float]` | `(13.0, 1.7)` | its (width, height) in scene units |
| `cell` | `float` | `0.2` | width of one character |
| `line_height` | `float` | `0.42` |  |
| `gap` | `float` | `0.14` | space between tiles |
| `fill` | `str` | `"#f2a861"` | fill colour |
| `ink` | `str` | `"#1b1b3a"` |  |
| `font` | `str` | `"IBM Plex Mono"` | font family |
| `radius` | `float` | `0.06` |  |
| `used_opacity` | `float` | `0.18` | 0..1 |
| `fills` | `Optional[dict]` | `None` | per-word colors, e.g. {"1": "#A16193", "0": "#192242"} |
| `inks` | `Optional[dict]` | `None` | per-word text colors |
| `read_lift` | `float` | `0.1` | how far a tile lifts when read |
| `read_color` | `Optional[str]` | `None` | a tile's color while it is being read |
| `read_time` | `float` | `0.28` | seconds |
| `dim_unread` | `bool` | `False` | at the end, dim tiles the program never reached |
| `unread_opacity` | `float` | `0.25` | 0..1 |
| `reveal` | `bool` | `False` | tiles start dim and light up once read (what the code knows) |
| `cursor` | `Optional[str]` | `None` | color of a caret that glides under the tile being read |
| `sublabels` | `Optional[Callable]` | `None` | f(i, word, n) -> small caption under tile i |
| `sublabel_color` | `str` | `"#6b6760"` | colour, as a hex string |
| `sublabel_size` | `float` | `13` | text size |
| `stop_mark` | `int` | `0` | at the end, ring the last N tiles read (where the code stopped) |
| `stop_color` | `str` | `"#ffffff"` | colour, as a hex string |

## LineComposer

`from iroshine import LineComposer` · defined in `iroshine/text.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `line` | `str` | `"cur"` | the list holding the current line's words |
| `out` | `str` | `"res"` | the list of finished lines (strings) |
| `width` | `str` | `"maxWidth"` | variable holding the measure, in characters |
| `source` | `Optional[str]` | `"words"` | the WordStrip words come from |
| `position` | `Tuple[float, float]` | `(0.0, -1.2)` | where it sits on the stage, as (x, y) in scene units (the stage is 8 units tall, centred on 0, 0) |
| `size` | `Tuple[float, float]` | `(12.6, 4.4)` | the page is fitted inside this box |
| `paper` | `Optional[str]` | `"#d862a9"` |  |
| `paper_margin` | `float` | `0.4` |  |
| `tile` | `str` | `"#f7f1c9"` |  |
| `ink` | `str` | `"#1b1b3a"` |  |
| `committed_tile` | `Optional[str]` | `None` | tile color once a line is committed (None = same) |
| `font` | `str` | `"IBM Plex Mono"` | font family |
| `space` | `str` | `"#1e9476"` | dot color for a real space |
| `pending_space` | `str` | `"#1b1b3a"` | hollow dot where a space is still required |
| `margin_color` | `str` | `"#f7f1c9"` | colour, as a hex string |
| `ruler` | `bool` | `True` |  |
| `push_time` | `float` | `0.55` | seconds |
| `space_time` | `float` | `0.2` | seconds |
| `commit_time` | `float` | `0.5` | seconds |
