# Show a list as bars

A `BarList` is a view bound to a list in your solution. Add one for every list you want to see: the
input, a `stack`, the returned result.

```python
from iroshine import BarList, Stage

stage = Stage()
stage.add(
    BarList("nums2",  position=(-2.35, 0.97),  size=(9.0, 1.75)),
    BarList("stack",  position=(-2.35, -0.96), size=(9.0, 1.75)),
    BarList("result", position=(-2.35, -2.89), size=(9.0, 1.75)),
)
```

- `"result"` is the list your function returns.
- Lists you don't declare are still tracked, so values can fly out of and into them; they just aren't
  drawn.
- When a value moves from one list to another (`stack.append(nums[i])`), its bar flies across,
  because every value remembers where it came from.

## Style the bars

```python
from iroshine import BarStyle, Gradient

SKY = Gradient("#4b1d95", "#8e2c8a", "#e2483a", "#f2873f", "#f4e3a0", by="rank")

BarList("nums", size=(12, 6),
        bar=BarStyle(shape="rect",      # "rect" | "pill" | "lollipop"
                     fill=SKY,          # a colour, a Gradient, or a function f(value, index)
                     gap=0.2,           # space between bars, as a fraction of a slot (0 = touching)
                     shade=0.18))       # a gradient inside each bar, darker at the base
```

What drives a gradient is set by `by`:

| `by` | The colour follows… |
|---|---|
| `"rank"` | the element's place in sorted order, so a sorted list becomes a perfect ramp |
| `"value"` | where the value sits on `y_range` |
| `"index"` | the slot the bar is in right now, so bars recolour as they move |
| `"origin"` | the slot the element started in |

## Ground, labels and the card behind

```python
from iroshine import Axis, Labels, Panel

BarList("height",
        axis=Axis(ground=0.16, ground_color="#5fbf9f"),   # a solid slab under the bars
        labels=Labels(values=True, name=False),           # show values, hide the list's name
        panel=None)                                       # no card behind (or Panel(fill=..., corner_radius=...))
```

## A list of indices

When a list holds positions in another list (a monotonic stack of indices), draw each entry as the
element it points at:

```python
BarList("stack", indexes="height")
```

## Swaps

`a[i], a[j] = a[j], a[i]` is detected and animated as one swap. To change how it moves, see
[Control pacing and motion](motion.md).

Every option: [Bars reference](../reference/bars.md).
