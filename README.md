# iroshine

*EE-roh-shine* · from Japanese 色 *iro*, "color": color-shine.

Turn an algorithm into a beautiful, musical animation. Built on Manim, so everything is vector-drawn,
and anything the library doesn't cover you can do in plain Manim.

```python
SKY = Gradient("#4b1d95", "#8e2c8a", "#e2483a", "#f2873f", "#f4e3a0", by="rank")

stage = Stage(background="#000000", resolution=(3840, 2160), fps=60, crf=14, grain=Grain(9))
stage.add(BarList("nums", size=(12, 6), bar=BarStyle(fill=SKY, shade=0.18),
                  axis=Axis(ground=0.16, ground_color="#5fbf9f"), panel=None))
stage.motion(swap=Motion(path="straight", easing="ease_in_out_cubic"))
stage.run(Solution().sortArray, nums)   # your LeetCode code, unchanged
stage.render("out.mp4")                 # or stage.preview() — fast 480p draft that opens when done
```

## What's new in v3

- **Resolution and encoding.** 4K60 by default. `crf` sets the encoder quality (Manim normally uses
  23, which smears flat color on a big screen; 12–16 is visually lossless). `render(quality="medium")`
  gives 1080p30 and `"low"` gives a 480p draft.
- **Grain.** `Grain(amount, animated)` adds film or print grain after rendering. It needs the
  `ffmpeg` command-line tool.
- **Gradient modes.** `Gradient(*colors, by=...)`:
  - `"rank"`: the element's place in sorted order. The color travels with the element, so a sorted
    list becomes a perfect ramp.
  - `"value"`: where the value sits on `y_range`.
  - `"index"`: the slot the bar is in right now, so bars recolor as they move.
  - `"origin"`: the slot the element started in, so you can watch the original order get scrambled.
- **Bar shading.** `BarStyle(shade=0.2)` adds a gradient inside each bar, darker at the base.
- **Ground slab.** `Axis(ground=0.16, ground_color=...)` puts a solid ground under the bars instead
  of a hairline.
- **Swaps.** `a[i], a[j] = a[j], a[i]` is detected and animated as one swap:
  `stage.motion(swap=Motion(...))`.
- **Straight, eased moves.** `Motion(path="straight", easing="ease_in_out_cubic")` moves every point
  of the shape along a straight line, speeding up and then slowing down. You can also use
  `path="arc"` or `"hop"`, and any easing.
- **Quiet defaults.** Black canvas, sharp corners, no glow, no sparkles, no badge text, uppercase
  letter-spaced list names, and Inter / IBM Plex Mono fonts. Turn things back on when you want them.
- **Finale.** `Finale(style="sweep")` runs a highlight across the answer while it plays the values
  as an ascending run. `"recolor"` is the other style.
- **Panels.** `Panel(fill=[bottom, top])` gives a vertical gradient card. Sharp corners by default.

### Added after v3

- **Bar spacing, using the same model as D3's `scaleBand`.** `BarStyle(gap=0.2, outer_gap=0.1)`.
  - `gap` is the space between bars, as a fraction of each slot. 0 means the bars touch.
  - `outer_gap` is the space before the first bar and after the last one, in slots.
  - With `gap=0`, neighbouring bars overlap by `seam` pixels (1.5 by default). Otherwise
    anti-aliasing leaves a faint hairline between touching shapes.
- **Gradient skies.** `Stage(background=[top, ..., bottom])`.
- **Palettes.** `from iroshine import DUSK, GARDEN`. Each one has `.sky`, `.gradient(by=...)`,
  `.ground`, `.accent`, `.frame`, `.text` and `.muted`.

### Gradients with positioned stops

`Gradient` follows the CSS gradient model, the most widely used system for this:

```python
Gradient("#cfe8b8", "#8ad0e0", "#e2483a")                       # evenly spaced
Gradient(("#cfe8b8", 0.0), ("#8ad0e0", 0.2), ("#e2483a", 1.0))  # stop = (color, position)
Gradient({0.0: "#cfe8b8", 0.2: "#8ad0e0", 1.0: "#e2483a"})       # same, as a dict
Gradient("#cfe8b8", ("#8ad0e0", "20%"), "#e2483a")               # mix freely; "20%" works too
Gradient(("#fff", 0.5), ("#000", 0.5))                          # two stops at one spot = hard edge
Gradient(..., space="oklab")    # blend space: "oklab" (default), "oklch", "srgb", "linear"
Gradient(..., steps=5)          # posterize into 5 flat bands
Gradient(..., by="rank")        # what drives it on a BarList: rank | value | index | origin
```

- **Colors** are hex strings. They're what every color picker and design tool gives you. Manim
  colors and `(r, g, b)` tuples work too.
- **Positions** run from 0 to 1, as in matplotlib and numpy. CSS-style percentages like `"20%"` are
  also accepted.
- **Missing positions** follow the CSS rules. The first stop defaults to 0 and the last to 1.
  Unpositioned stops are spaced evenly between their positioned neighbours, and positions never go
  backwards.
- **Blending uses OKLab.** Mixing in plain sRGB makes a grey, muddy middle, for example between
  teal and pink. OKLab is the perceptual space modern CSS recommends, and it keeps the midpoints clean.
- **Backgrounds** accept gradients too: `Stage(background=Gradient(...))`, where 0 is the top and
  1 is the bottom.

Palettes: `DUSK`, `GARDEN` and `ELYSIUM`. Their ramps can use positioned stops.

### Beyond sorting: variables, index lists, shapes

The tracker can now watch plain local variables (ints, floats, lists). These components react to them:

```python
BarList("stack", indexes="height")   # the list holds positions; each bar is drawn as the element it names
Pointer("i", on="height")            # a marker that follows an index variable (i, left, right, mid…)
Readout("water", label="water")      # a big number that counts up/down as the variable changes
Region(on="height", when="water",    # whenever `water` changes, draw a shape from your locals
       x0="left + 1", x1="i - 1",
       y0="height[top]", y1="min(height[left], height[i])",
       fill="#277879", surface="#5fa3b8")
```

- The Stage works out which variables to watch from the components you add. Pass
  `stage.run(..., watch=[...])` to watch more.
- `Region` coordinates are plain Python expressions, evaluated against your solution's local
  variables at that moment. They can also be functions that take a dict of locals.
- The same pieces cover two-pointer problems (`Pointer` for left/right), area problems like
  Container With Most Water or Largest Rectangle (`Region` + `Readout`), and anything with a running
  answer (`Readout`).

### Pack: turning an area answer into a picture

```python
water = Region(on="height", when="water", x0=..., x1=..., y0=..., y1=...)
stage.add(water, Pack(region=water, position=(-1.5, 2.3), size=(2.1, 2.1), rotate=False))
```

Each piece the Region draws also flies over and settles into one near-square block, so the block's
area is the answer.

- `rotate=False` keeps every piece's orientation, so its width stays horizontal.
- `rotate=True` lets pieces turn 90° if that packs squarer.
- The layout uses MaxRects with the "best short side fit" rule, from Jylänki's "A Thousand Ways to
  Pack the Bin". Box sizes are tried from the squarest up.
- Because the run is recorded first, the whole layout is solved up front, packing the biggest pieces
  first. Pieces then land in their final spots as they appear.
- Options: `fill` (a color, or a Gradient colored by arrival order), `stroke` (lines between
  pieces), `outline` (a faint preview of the finished block), `duration`, `easing`.

### Grids and graph search

```python
GridView("isInfected", colors={0: CLEAN, 1: INFECTED, -1: CONTAINED},
         unknown=0.78, forget_when="seen",               # dim = not read yet; a new `seen` = forget everything
         marks={"region":   Mark(shape="ring", stroke="#f0d3e2", keep=True),
                "frontier": Mark(shape="dot", fill="#86A0CE", keep=True)},
         walls=Walls(between=(-1, 0), color="#86A0CE"))
```

- **2-D lists** passed to your solution are tracked cell by cell. Every read and write reports its
  `(row, col)`.
- **Sets** are tracked too: `seen = set()`, `a, b = set(), set()`, `{...}` and set comprehensions.
  They report `add`, `remove` and `clear`.
- **Colors follow the data.** A cell's color comes from its current value.
- **Marks follow the data.** A cell gets the overlay for every named set it belongs to.
  - `keep=True` leaves a faded copy of the old set when the set is re-created, so earlier regions
    stay visible.
  - `shape` is `"cell"`, `"ring"` or `"dot"`.
- **Knowledge.** `unknown` dims every cell until your code reads it, so the picture is what the
  program knows. `forget_when` names a set or list; re-creating it dims everything again.
- **Walls.** `Walls(between=(a, b))` draws a wall on every edge between a cell valued `a` and one
  valued `b`. Walls stay once built. That covers any problem whose answer is a boundary.
- **Pacing.** A search does hundreds of reads, so grid events play as overlapping waves.
  - `rate`: how many cell events per second.
  - `step`: how long each little animation lasts.
  - A new wave starts whenever the same cell is touched twice.

The design follows two classic algorithm-animation ideas:

- **Interesting events** (Marc Brown's BALSA and Zeus). The tracker records the events that matter,
  and your code isn't modified.
- **State mapping** (as in Vega-Lite's declarative encodings). Cell colors and marks are rules over
  the data, not hand-written animation calls.

### Dependencies, printing, and geometry

```python
GridView("targetGrid", colors={1: "#2c2240", 2: "#4b1d95", ...})   # categorical colors
GridView("printer", like="targetGrid")         # a blank canvas the same shape (nothing bound to it)
GridBoxes(on="targetGrid")                      # boxes from top[c]/bottom[c]/left[c]/right[c] as they update
GraphView("graph", layout="line", done_when="layer")   # graph = [set() ...]: graph[u].add(v) draws u → v
Stamp(on="printer", when="layer", rows=("top[layer]", "bottom[layer]"),
      cols=("left[layer]", "right[layer]"), value="layer")   # print a block when `layer` changes

PointSet("trees", focus="p", fill=Gradient(..., by="index"))  # [x, y] points; sort() recolors by order
Polyline("hull", on="trees", probe="p", fill=...)             # a stack of points drawn as a growing path
```

- **Lists of sets** (`[set() for _ in range(n)]`) are tracked element by element, as `graph[0]`,
  `graph[1]` and so on.
- **List mirrors.** The Stage keeps a plain copy of every list, including ones you don't draw.
  That's how `GridBoxes` reads `top` and `bottom` as they change.
- **2-D input.** A list of lists is only treated as a 2-D grid if a `GridView` with that name is
  declared. Otherwise, like `trees`, it stays a list of points.
- **Merging.** Grid, box and edge events play as overlapping waves. Box updates within one wave
  merge, so a box redraws once per wave instead of four times per cell.
- **Not yet supported:** dict-of-set adjacency (`defaultdict(set)`), undirected-graph layouts, and
  force-directed layout.

### Text

```python
WordStrip("words")                                     # a list of strings as word tiles, flowed like a paragraph
LineComposer(line="cur", out="res", width="maxWidth")  # a page with a fixed measure, built from your lists
```

- **Strings carry their origin** (`TaggedStr`), just like ints do. A word appended to `cur` flies
  from its own tile.
- **The layout comes from the strings themselves.** Trailing spaces in `cur[j]` are real spaces
  (solid dots). A gap that still needs its one required space shows a hollow dot. `res.append(s)`
  commits the line exactly as `s` spells it.
- **One type size and one baseline** for every word, set from the monospace glyph width. Short and
  long words look like the same typeface.
- **New components only.** These are new views, so no existing function changed behavior. The
  Stage has a generic `handlers` hook, so future views can take their own events the same way.

### Sums and running totals (600 · Fibonacci / digit DP)

```python
f[i] = f[i - 1] + f[i - 2]      # copies of both bars fly over, stack, and become the new bar
Tower("ans", on="f", labels=True)          # ans += f[k]: the f[k] bar flies onto a stacked tower
Readout("ans", label="count", result=True) # counts on to the return value at the end
WordStrip("bits", reveal=True, cursor="#86A0CE", sublabels=lambda i, w, n: n - 1 - i,
          fills={"1": ..., "0": ...}, dim_unread=True, stop_mark=2)
```

- **Sums remember their parts.** `a + b` of two list values is a `Derived` int that keeps where each
  part came from, so a set shows the parts stacking into the new bar. It works only for bars that grow
  upward. The tempo follows the size: small sums go by quickly, and big ones take their time.
- **Tower** shares the bar list's scale, so a block is exactly as tall as the bar it came from. At the
  end, the tower rings out from the bottom block to the top.
- **WordStrip additions** (all opt-in):
  - `reveal`: tiles start dim and light up once the code reads them, like the grid's knowledge dimming.
  - `cursor`: a caret that glides under the tile being read.
  - `sublabels`: small captions under each tile.
  - `stop_mark`: rings the last N tiles read. That's where an early return stopped.
- **Readouts** stay hidden until their variable gets its first value.

### Short-form video (vertical, looping)

```python
Stage(resolution=(1440, 2560), fps=60, timing=Timing(intro="instant"))   # 9:16; the first frame is already composed
Polyline("hull", on="trees", ghost=True, loop=True)   # the answer drawn faintly from frame 0; returns there at the end
Beats([Beat("What's the shortest fence around every tree?", at="start"),
       Beat("Sort the trees left to right.", at="trees.sort()"),      # fires when that line of your code runs
       Beat("Turns inward? Pull the post.", on="pop", list="hull"),   # or the first time something happens
       Beat("The shortest fence.", at="end")], loop=True)
```

- **Beats** are large captions that appear word by word. Long phrases wrap into lines of even length,
  so no word ends up alone on the last line. Each phrase plays a soft chime. With `loop=True`, the story
  returns to its first beat at the end.
- **Loops.** `ghost` + `loop` + `intro="instant"` make the last frame match the first, so the video
  replays seamlessly.
- **`low` and `medium` keep the frame's shape:** a vertical stage renders at 480×854 or 1080×1920.
- **The sound is cut at the last frame**, with a short fade, so trailing notes no longer leave frozen
  frames at the end.
- See `shorts/erect_the_fence.py` and `shorts/fewest_squares.py`. Specs: 1440×2560 at 60 fps for YouTube Shorts (it keeps the extra
  sharpness) and 1080×1920 for TikTok and Reels. Keep what matters inside the safe zone: roughly the
  middle, clear of the top 12%, the bottom 32% and the right 13%.

## How it fits together

1. **tracking.py** runs your solution on a rewritten copy. Every list is tracked, and every value
   remembers where it came from.
2. **BarList** objects are *views* bound to variable names (`"stack"` shows your `stack` variable).
3. **Stage** replays the events as Manim animations, using your styles, motions, hooks and sound.

## Knobs

| Object | What it controls |
|---|---|
| `Stage(background, resolution, fps, crf, grain, sound, timing, finale, caption)` | canvas, output quality, global settings |
| `BarList(name, position, size, orientation, y_range, capacity, bar, labels, panel, axis, title)` | one list's look and placement |
| `BarStyle(shape, width, corner_radius, fill, opacity, shade, stroke, stroke_width, glow, min_length)` | shape is `rect`, `pill` or `lollipop`. fill is a color, a `Gradient`, or `f(value, index)` |
| `Gradient(*colors, by="rank" \| "value" \| "index" \| "origin")` | multi-stop color ramps |
| `Labels(values, indices, name, name_position, uppercase, name_weight, fonts, sizes, colors)` | all text on a list |
| `Panel(fill, opacity, corner_radius, stroke)` / `panel=None` | the card behind a list |
| `Axis(baseline, ground, ground_color, ground_stroke, color, width, ticks)` | baseline, ground slab, guide lines |
| `Motion(duration, easing, color, path, arc, trail, sparkle, squash, exit, style, lag)` | per event: `stage.motion(swap=…, push=…, pop=…, compare=…, read=…, set=…)` |
| `Sound(scale, key, octave, instrument, finale_instrument, reverb, volume, landing_interval, tick_reads, compare_notes, finale)` | instruments: harp, bell, marimba, music_box, soft_sine |
| `Finale(target, style, color, text, text_position, font, font_size, sparkle)` / `finale=None` | the ending |
| `Timing(speed, skip, pause_between, end_hold)` | pacing |
| `Grain(amount, animated)` | film or print texture |
| `CodePanel(...)`, `Caption(...)`, any Manim mobject | extras you place yourself |
| `@stage.on(event, target)` | full override with a `HookContext` |

## Getting started

```bash
brew install cairo pango ffmpeg pkg-config      # Mac (Windows: see the Manim install guide)
cd iroshine
python3 -m venv .venv && source .venv/bin/activate
pip install -e .                                # installs manim + numpy, and makes `import iroshine` work anywhere
cd examples && python 00_start_here.py low      # writes 00_start_here.mp4
```

Copy `00_start_here.py` to begin a new problem: paste your solution, name the lists and variables to show,
change the input, and run it with `low` while you iterate and with no argument for the 4K final.

## Requirements

`pip install manim` (needs Cairo, Pango and FFmpeg on your system; on a Mac: `brew install cairo pango ffmpeg`).
Fonts used by the defaults: Inter and IBM Plex Mono (free from Google Fonts). If they're missing,
Pango falls back to a system font.
