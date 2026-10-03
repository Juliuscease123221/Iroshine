# Write your own view

When the built-in views can't express the choreography a problem needs, write a view. A view is any
object with a `wants` and a `handle` method; `stage.add` accepts it. `iroshine/tiling.py` and
`iroshine/crossing.py` are full examples.

## The interface

| Method | When it runs | What it does |
|---|---|---|
| `wants(e)` | for each event | return `True` for the events this view animates |
| `watch()` | before the run | optional: names of extra local variables to track |
| `plan(scene, events)` | once, before playback | look through every event, then return the static drawing (a Manim mobject) |
| `intro(scene, e)` | for each input list | return a list of animations, or `[]` |
| `handle(scene, e)` | for each wanted event | play animations and notes |
| `outro(scene)` | after the last event | optional: stage an exit before a loop returns |

## Events

An event is a dict. The common keys:

| Key | Meaning |
|---|---|
| `type` | `"create"`, `"read"`, `"compare"`, `"push"`, `"pop"`, `"set"`, `"swap"`, `"var"` (a watched variable changed), `"screate"` / `"sadd"` (a set created / added to), `"done"` |
| `list` | the name of the list it happened to (set events use `set` instead; `var` events use `name`) |
| `value` | the value involved |
| `index` | the position in the list, where that applies |
| `src` | where the value came from, e.g. `{"list": "nums", "index": 0}` |
| `line` | the source line that caused it |

## A minimal view

This draws a dot for every item pushed onto a list called `path`:

```python
from dataclasses import dataclass
from manim import Dot, FadeIn, FadeOut, VGroup


@dataclass
class DotTrail:
    name: str = "path"

    def wants(self, e):
        return e.get("list") == self.name and e["type"] in ("push", "pop")

    def plan(self, scene, events):
        self.dots = []
        return VGroup()                           # nothing static to draw

    def intro(self, scene, e):
        return []

    def handle(self, scene, e):
        speed = scene.S.timing.speed
        if e["type"] == "push":
            x, y = e["value"][:2]
            d = Dot([x * 0.4 - 2, y * 0.4 - 2, 0])
            self.dots.append(d)
            scene.note(deg=len(self.dots), instrument="wood", gain=-8)
            scene.play(FadeIn(d, scale=0.5), run_time=0.3 / speed)
        else:
            scene.play(FadeOut(self.dots.pop()), run_time=0.2 / speed)
```

```python
stage.add(DotTrail("path"))
```

## Planning ahead

The whole run is recorded before anything is drawn, so `plan()` can see the future: where the answer
turns up, how long the search is, which moments deserve time. `TilingView.plan` uses this to pick the
frames of its time-lapse and to make the pitch rise toward the moment the answer is found.

## Sound

`scene.note(deg=..., instrument=..., gain=..., offset=...)` schedules a note at the current moment.
`deg` is a step of the stage's scale (with a five-note scale, `deg=5` is one octave above `deg=0`),
`gain` is in dB, and `offset` delays it by that many seconds.

## Manim details worth knowing

- `scene.add(m)` on something already on screen moves it to the top of the drawing order.
- Grouped animations (`AnimationGroup`, `LaggedStart`) take their mobjects into a new group at the
  top. If you animate one part of a shape alone, it can end up drawn over its siblings; animate the
  whole family together.
- New options should default to the old behaviour, so existing videos re-render unchanged.
