# Colour

Gradients and ready-made palettes.

!!! note "Generated page"
    This page is built from the source by `tools/gen_reference.py`. Edit the comments in the code, not this file.

## Gradient

`from iroshine import Gradient` · defined in `iroshine/gradient.py`

A multi-stop color ramp with optional stop positions. See the module docstring.

| Option | Type | Default | What it does |
|---|---|---|---|
| `*stops` |  |  |  |
| `by` |  | `"rank"` | what drives the colour on a BarList: "rank", "value", "index" or "origin" |
| `space` |  | `"oklab"` | blend space: "oklab", "oklch", "srgb" or "linear" |
| `steps` |  | `None` | posterize into this many flat bands (None: smooth) |

### Methods

#### `at(t)`

Color at position t (0–1) as a ManimColor.

#### `sample(n=32)`

n evenly spaced colors (e.g. for a background).

## Palette

`from iroshine import Palette` · defined in `iroshine/palettes.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `name` | `str` | required | the variable in your solution that this view is bound to |
| `background` | `Union[str, Sequence[str]]` | required | a color, or [top, ..., bottom] for a gradient sky |
| `ramp` | `Union[Sequence, Gradient]` | required | bar colors: plain colors, (color, position) stops, or a Gradient |
| `ground` | `str` | required |  |
| `accent` | `str` | required | highlights: compares, the finale sweep |
| `frame` | `str` | required |  |
| `text` | `str` | required | text colour |
| `muted` | `str` | required | colour of secondary text |
| `outline` | `str` | `""` | ink line color, if the style uses outlines |
