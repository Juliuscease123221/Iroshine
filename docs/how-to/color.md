# Choose colours

## Start from a palette

A palette is a matching set: a background, a ramp for bars, a ground colour, an accent, and text
colours.

```python
from iroshine import DUSK as P, Axis, BarList, BarStyle, Stage

stage = Stage(background=P.sky)
stage.add(BarList("nums", bar=BarStyle(fill=P.gradient(by="rank")),
                  axis=Axis(ground=0.2, ground_color=P.ground)))
```

Built in: `DUSK`, `GARDEN`, `ELYSIUM`, `DARK_CHERRY`, `LAKE`. Each has `.sky`, `.gradient(by=...)`,
`.ground`, `.accent`, `.frame`, `.text`, `.muted` (and `.outline` where the style uses ink lines).
The [gallery](../gallery.md) shows each one in use.

## Build a gradient

`Gradient` follows the CSS gradient model.

```python
from iroshine import Gradient

Gradient("#cfe8b8", "#8ad0e0", "#e2483a")                       # evenly spaced
Gradient(("#cfe8b8", 0.0), ("#8ad0e0", 0.2), ("#e2483a", 1.0))  # stop = (colour, position)
Gradient({0.0: "#cfe8b8", 0.2: "#8ad0e0", 1.0: "#e2483a"})      # the same, as a dict
Gradient("#cfe8b8", ("#8ad0e0", "20%"), "#e2483a")              # mix freely; "20%" works too
Gradient(("#fff", 0.5), ("#000", 0.5))                          # two stops at one spot = a hard edge
Gradient(..., space="oklab")    # blend space: "oklab" (default), "oklch", "srgb", "linear"
Gradient(..., steps=5)          # posterize into 5 flat bands
Gradient(..., by="rank")        # what drives it on a BarList: rank | value | index | origin
```

- **Colours** are hex strings. Manim colours and `(r, g, b)` tuples work too.
- **Positions** run from 0 to 1. Missing positions follow the CSS rules: the first stop defaults to 0,
  the last to 1, and unpositioned stops are spaced evenly between their neighbours.
- **Blending uses OKLab** by default. Mixing in plain sRGB makes a grey, muddy middle (between teal and
  pink, for example); OKLab keeps the midpoints clean.
- `gradient.at(t)` returns the colour at position `t`, for colouring things yourself.

## Gradient backgrounds

```python
Stage(background=["#1a2a6c", "#b21f1f", "#fdbb2d"])     # top to bottom
Stage(background=Gradient(...))                          # 0 is the top, 1 is the bottom
```

## Advice that held up in practice

- **Let colour mean one thing.** In the Fewest Squares short, colour is square size and nothing else.
- **Spread the ramp over the values that actually appear**, so neighbouring values are
  distinguishable.
- **Keep full saturation for small areas.** Large shapes at full saturation are tiring; mute the
  biggest ones a little and save the strongest colour for the detail you want noticed.
- **Separate shapes with a dark line, not with hue.** `TilingView(outline=..., gap=...)` draws an even
  ink line between tiles.

Every option: [Colour reference](../reference/color.md).
