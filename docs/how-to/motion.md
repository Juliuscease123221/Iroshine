# Control pacing and motion

## Speed, skips and holds

```python
from iroshine import Stage, Timing

Stage(timing=Timing(speed=1.6,            # global multiplier (2 = twice as fast)
                    skip=("read",),       # leave out event types: "read", "compare"
                    pause_between=0.0,    # seconds of stillness after every event
                    end_hold=3))          # seconds held on the last frame
```

## How each kind of event moves

```python
from iroshine import Motion

stage.motion(
    push=Motion(path="hop", trail=True, color="#f7d154", duration=0.85, easing="ease_in_out_cubic"),
    swap=Motion(path="arc"),
    pop=Motion(exit="shrink", duration=0.35),
    compare=Motion(color="#ff5d8f", duration=0.4),
)
```

Event kinds: `create`, `read`, `compare`, `push`, `set`, `swap`, `pop`, `replace`.

| Option | Choices |
|---|---|
| `path` | `"straight"`, `"arc"`, `"hop"` |
| `exit` (pops) | `"fade"`, `"float_up_fade"`, `"shrink"`, `"drop"`, `"burst"` |
| `easing` | the name of any Manim rate function |
| `trail`, `sparkle`, `squash` | small flourishes, off by default |

## Replace one animation with your own

```python
from manim import FadeOut, RIGHT, rate_functions

@stage.on("pop", target="stack")
def whoosh(ctx):
    return [FadeOut(ctx.bar, scale=0.2, shift=0.8 * RIGHT, rate_func=rate_functions.ease_in_back)]
```

The function receives a [`HookContext`](../reference/stage.md#hookcontext) and returns a list of
Manim animations. Return `None` to fall back to the built-in animation; call `ctx.default()` to get
the built-in animations and add to them.

## Output quality

```python
Stage(resolution=(3840, 2160), fps=60, crf=14)      # the defaults: 4K at 60 fps
stage.render("out.mp4", quality="low")              # "low" 480p15 · "medium" 1080p30 · "high" as declared
stage.preview()                                     # a low render that opens when it's done
```

`crf` is the encoder quality: lower is better and bigger; 12–18 is visually lossless.
`Grain(amount)` adds film or print grain after rendering.

Every option: [Sound, timing, motion, finale reference](../reference/settings.md).
