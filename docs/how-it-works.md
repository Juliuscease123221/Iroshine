# How it works

iroshine does three things in order: it **records** your solution running, **replays** that recording
as animation, and adds **sound** as it goes.

## 1. Record

You hand `stage.run` your solution, unchanged. iroshine makes a rewritten copy of the function in
which every list you create becomes a list that reports what happens to it, and runs that copy once.

Three pieces do the work (`iroshine/tracking.py`):

| Piece | What it does |
|---|---|
| A tagged value | a number or string that remembers where it was read from, so when `stack.append(nums[i])` runs, the library knows the new stack entry *came from* `nums[i]` and can fly the bar across |
| A tracked list | a list that logs every read, write, push and pop |
| The rewrite | your function's syntax tree is rewritten so `stack = []`, `res = [0] * n` and `return [...]` produce tracked lists; grids, sets and watched local variables are handled the same way |

A line tracer stamps each event with the source line that caused it, which is how the code panel
knows what to highlight.

The result is a plain list of events:

```python
{"type": "read", "list": "nums",  "index": 0, "value": 3, "line": 4}
{"type": "push", "list": "stack", "index": 0, "value": 3, "src": {"list": "nums", "index": 0}, "line": 5}
{"type": "var",  "name": "best",  "value": 3, "line": 6}
{"type": "pop",  "list": "stack", "index": 2, "value": 2, "line": 8}
{"type": "sadd", "set": "seen",   "value": [1, 2], "line": 9}
```

The `src` on the push is the origin: this value was read from `nums[0]`.

Your original function is never modified.

## 2. Replay

You declared views bound to variable names: a `BarList("stack")`, a `Readout("best")`. The Stage
walks the events in order and gives each one to the view that asked for it. The view turns it into a
[Manim](https://www.manim.community/) animation: a bar rises, a marker slides, a cell changes colour.

This is the "interesting events" idea from early algorithm-animation systems (Marc Brown's BALSA and
Zeus), combined with declarative mapping from data to appearance: a cell's colour and a bar's fill
are rules over the data, not hand-written animation calls.

Because the whole run is recorded before anything is drawn, a view can look ahead while planning. A
packing layout can be solved up front so pieces land in their final places; a search can speed
through its routine stretch and slow down just before the answer.

## 3. Sound

As each animation is scheduled, the view places a note at the same moment. Notes are synthesized
from scratch (`iroshine/sound.py`): sums of sine partials shaped to sound like a harp, a wooden bar
or a bubble in water. Every note is a step of one musical scale, so the result stays in key whatever
the algorithm does. Manim mixes the notes into the video's audio track.

## What the tracker can and can't see

It sees:

- lists and lists of lists (as grids, when a `GridView` with that name is declared)
- sets, and lists of sets
- local variables that hold ints, floats or lists, when a component names them or you pass
  `watch=[...]`
- swaps written as `a[i], a[j] = a[j], a[i]`
- sums of two list values (`f[i] = f[i - 1] + f[i - 2]`), which remember their parts

It doesn't yet see:

- dicts used as adjacency lists (`defaultdict(set)`)
- objects and linked structures (trees and linked lists built from node classes)
- work done inside library calls, such as the comparisons inside `sorted()`: only the result is
  seen, not the steps

When a problem doesn't fit, restructure the solution so its key steps are list, set or variable
operations, or [write your own view](how-to/custom-view.md).

## Files

| File | Role |
|---|---|
| `tracking.py` | record |
| `stage.py` | replay: the Stage, the Manim scene, rendering and encoding |
| `barlist.py`, `grid.py`, `graph.py`, `geometry.py`, `text.py`, `components.py` | the built-in views |
| `tiling.py`, `crossing.py` | views written for one family of problems |
| `sound.py` | the synthesizer |
| `style.py`, `gradient.py`, `palettes.py`, `code_styles.py` | settings and colour |
| `packing.py`, `story.py` | rectangle packing; captions |
