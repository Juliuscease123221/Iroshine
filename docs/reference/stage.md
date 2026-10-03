# Stage

The canvas, the run, and the render.

!!! note "Generated page"
    This page is built from the source by `tools/gen_reference.py`. Edit the comments in the code, not this file.

## Stage

`from iroshine import Stage` · defined in `iroshine/stage.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `background` |  | `"#000000"` | a colour, a list of colours (a top-to-bottom gradient), or a `Gradient` |
| `resolution` |  | `(3840, 2160)` | (width, height) in pixels; (1080, 1920) for a vertical Reel |
| `fps` |  | `60` | frames per second |
| `sound` | `Optional[Sound]` | `None` | a `Sound` (None: the defaults) |
| `timing` | `Optional[Timing]` | `None` | a `Timing` (None: the defaults) |
| `finale` | `Optional[Finale]` | `None` | a `Finale`, or None for no closing flourish |
| `caption` | `Optional[Caption]` | `None` | a `Caption` shown throughout |
| `grain` | `Optional[Grain]` | `None` | a `Grain` for film or print texture (None: clean) |
| `crf` | `int` | `14` | encoder quality: lower is better and bigger (12–18 is visually lossless) |

### Methods

#### `add(*items)`

Put things on the stage: views (BarList, GridView, ...), components (CodePanel, Readout, ...),
or any plain Manim mobject (titles, shapes). Returns the stage, so calls can be chained.

#### `motion(**per_event: Motion)`

Override how events animate: stage.motion(swap=Motion(path='arc'), pop=Motion(exit='shrink')).

#### `on(event, target=None)`

Decorator: replace the animation for an event (optionally only for one list).

#### `run(method, *args, watch=())`

Run your solution under the tracker. Variables used by Pointer / Readout / Region
are watched automatically; pass extra names in `watch` to see them as "var" events.

#### `render(out='iroshine.mp4', quality='high', preview=False)`

quality: "high" = your resolution/fps · "medium" = 1080p30 · "low" = 480p15 draft.

#### `preview(out='iroshine_preview.mp4')`

Fast low-res render that opens in your video player when it's done.

## HookContext

`from iroshine import HookContext` · defined in `iroshine/stage.py`

What a custom animation hook receives.

| Option | Type | Default | What it does |
|---|---|---|---|
| `scene` | `Scene` | required | the Manim scene (add things, use self.camera, ...) |
| `event` | `dict` | required | the raw event: type, list, index, value, src, line... |
| `view` | `BarList` | required | the BarList this event happens in |
| `bar` | `Any` | required | the bar mobject involved (new bar for push/set, leaving bar for pop) |
| `source` | `Any` | required | where the value came from (a bar mobject) or None |
| `motion` | `Motion` | required | the resolved Motion for this event |
| `default` | `Callable[[], List]` | required | call to get the built-in animations |
