# Follow a variable

The tracker watches plain local variables (ints, floats, lists) as well as lists. These components
react to them. The Stage works out which variables to watch from the components you add; to watch
more, pass `stage.run(..., watch=["name"])`.

## An index: `Pointer`

```python
from iroshine import Pointer

Pointer("i", on="height")                              # a marker under the bar that `i` points at
Pointer("left", on="height", color="#f3e08a", guide=True)   # with a faint vertical guide line
```

## A running answer: `Readout`

```python
from iroshine import Readout

Readout("water", position=(-6.6, 2.15), label="water trapped", font_size=96)
Readout("ans", label="count", result=True)     # at the end, count on to the function's return value
```

A readout stays hidden until its variable first gets a value.

## An area: `Region`

Whenever the `when` variable changes, a `Region` draws a rectangle whose edges are Python expressions
evaluated against your solution's local variables at that moment.

```python
from iroshine import Region

Region(on="height", when="water",
       x0="left + 1", x1="i - 1",
       y0="height[top]", y1="min(height[left], height[i])",
       fill="#277879", surface="#5fa3b8")
```

Each edge can also be a function that takes a dict of the locals. This covers Trapping Rain Water,
Container With Most Water, Largest Rectangle, and anything else whose answer is a sum of areas.

## Turning the areas into one picture: `Pack`

```python
from iroshine import Pack

water = Region(on="height", when="water", x0=..., x1=..., y0=..., y1=...)
stage.add(water, Pack(region=water, position=(-1.5, 2.3), size=(2.1, 2.1), rotate=False))
```

Each piece the region draws also flies over and settles into one near-square block, so the block's
area *is* the answer.

## A running total as a tower: `Tower`

```python
from iroshine import Tower

Tower("ans", on="f", labels=True)      # ans += f[k]: the f[k] bar flies onto a stacked tower
```

Every option: [Variables reference](../reference/variables.md).
