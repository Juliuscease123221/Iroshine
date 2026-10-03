# Code and captions

Your source on screen, and words over the picture.

!!! note "Generated page"
    This page is built from the source by `tools/gen_reference.py`. Edit the comments in the code, not this file.

## CodePanel

`from iroshine import CodePanel` · defined in `iroshine/components.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `position` | `Tuple[float, float]` | `(4.6, 1.8)` | center |
| `width` | `float` | `4.6` | width, in scene units |
| `style` | `str` | `"github-dark"` | any Pygments style: github-dark, monokai, nord, friendly... |
| `background` | `str` | `"#0b0b0b"` | background colour |
| `border` | `Optional[str]` | `None` |  |
| `highlight` | `str` | `"#f3e08a"` | colour of the line highlight |
| `highlight_opacity` | `float` | `0.14` | 0..1 |
| `font` | `str` | `"IBM Plex Mono"` | font family |
| `line_numbers` | `bool` | `True` | show line numbers |
| `glide` | `bool` | `False` | the highlight glides smoothly to every line the code runs |
| `glide_speed` | `float` | `14.0` | how quickly it catches up (higher = snappier) |
| `span` | `str` | `"line"` | (glide) "line": the running line · "loop": the whole outermost loop while the code is inside it (calmer: no flicking back and forth) · "inner": the innermost loop block (e.g. a while inside a for), single lines elsewhere |
| `corner_radius` | `float` | `0.0` | how rounded the corners are |
| `padding` | `float` | `0.0` | space around the code inside the panel (0 = Manim's default) |
| `show` | `Optional[Tuple[str, str]]` | `None` | crop to the core: from the first line containing show[0] to the first line after it containing show[1] (dedented; bigger text) |
| `follow_batches` | `bool` | `False` | (glide) inside a grid wave, follow the line that changes cells (otherwise the highlight stays on the wave's first line) |

## code_style

`from iroshine import code_style` · defined in `iroshine/code_styles.py`

```python
code_style(text='#e8e4dc', keyword='#e8a9c4', string='#f0a870', number='#6fb3a2', comment='#7c83b8', name=None, operator=None, background='#000000')
```

## Caption

`from iroshine import Caption` · defined in `iroshine/components.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `position` | `Tuple[float, float]` | `(-6.8, -3.65)` | left edge, vertical center |
| `font` | `str` | `"IBM Plex Mono"` | font family |
| `font_size` | `float` | `18` | text size |
| `color` | `str` | `"#6b6760"` | colour, as a hex string |

## Beats

`from iroshine import Beats` · defined in `iroshine/story.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `beats` | `List[Beat]` | `list()` | the captions, in order |
| `position` | `Tuple[float, float]` | `(0.0, 2.0)` | center of the text block |
| `width` | `float` | `3.6` | wrap long phrases to this width |
| `font` | `str` | `"Inter"` | font family |
| `weight` | `str` | `"MEDIUM"` | font weight |
| `font_size` | `float` | `30` | text size |
| `color` | `str` | `"#ffffff"` | colour, as a hex string |
| `sub_font` | `str` | `"IBM Plex Mono"` | font family |
| `sub_size` | `float` | `15` | text size |
| `sub_color` | `str` | `"#bbbbbb"` | colour, as a hex string |
| `word_lag` | `float` | `0.12` | words appear one after another |
| `duration` | `float` | `0.45` | seconds the animation takes |
| `loop` | `bool` | `False` | at the very end, return to the first beat |
| `chime` | `bool` | `True` | a soft note as each phrase appears |

## Beat

`from iroshine import Beat` · defined in `iroshine/story.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `text` | `str` | required | text colour |
| `at` | `Optional[str]` | `None` | "start", "end", or a piece of source code (fires when that line runs) |
| `on` | `Optional[str]` | `None` | or an event type: "pop", "push", "swap", "set", "replace", ... |
| `list` | `Optional[str]` | `None` | ...on this list only |
| `sub` | `Optional[str]` | `None` | a smaller second line under the text |
| `color` | `Optional[str]` | `None` | override the text color for this beat |
