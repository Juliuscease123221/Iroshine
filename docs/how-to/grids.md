# Animate a grid search

A `GridView` is bound to a 2-D list in your solution. Every read and write is tracked cell by cell.

```python
from iroshine import GridView, Mark, Walls

GridView("isInfected", position=(-1.35, -0.3), size=(10.6, 6.4),
         colors={0: CLEAN, 1: INFECTED, -1: CONTAINED},          # a cell's colour follows its value
         unknown=0.78, forget_when="seen",                       # dim until the code reads it
         marks={"region":   Mark(shape="ring", stroke="#f0d3e2", keep=True),
                "frontier": Mark(shape="dot", fill="#86A0CE", keep=True)},
         walls=Walls(between=(-1, 0), color="#86A0CE"))
```

## Colours follow the data

`colors` is a dict from value to colour, or a function `value -> colour`. When your code writes
`grid[r][c] = 2`, the cell changes colour. Nothing else is needed for flood fills, BFS waves and
similar problems.

To make a wave visible as a contour map, store *when* each cell changed
(`grid[r][c] = 2 + minute`) and map the value through a gradient.

## Marks follow sets

Sets are tracked too (`seen = set()`, `seen.add((r, c))`). A cell gets the overlay for every named
set it belongs to. `keep=True` leaves a faded copy when the set is re-created, so earlier regions stay
visible. `shape` is `"cell"`, `"ring"` or `"dot"`.

## Show what the program knows

`unknown=0.78` dims every cell until your code reads it. `forget_when="seen"` dims everything again
each time the set (or list) called `seen` is re-created, so each new search starts in the dark.

## Walls

`Walls(between=(a, b))` draws a wall on every edge between a cell valued `a` and one valued `b`.
Walls stay once built. That covers any problem whose answer is a boundary.

## Pacing

A search does hundreds of reads, so grid events play as overlapping waves.

| Option | Meaning |
|---|---|
| `rate` | how many cell events per second |
| `step` | how long each small animation lasts |

A new wave starts whenever the same cell is touched twice.

## Related views

```python
GridView("printer", like="targetGrid")          # a blank canvas shaped like another grid
GridBoxes(on="targetGrid")                      # bounding boxes from top[c] / bottom[c] / left[c] / right[c]
Stamp(on="printer", when="layer", rows=("top[layer]", "bottom[layer]"),
      cols=("left[layer]", "right[layer]"), value="layer")      # print a block when `layer` changes
GraphView("graph", layout="line", done_when="layer")            # graph[u].add(v) draws u → v
```

!!! note "2-D input"
    A list of lists is treated as a grid only if a `GridView` with that name is declared. Otherwise
    it stays a list of points (see [Draw points and paths](geometry.md)).

Not yet supported: dict-of-set adjacency (`defaultdict(set)`), undirected-graph layouts, and
force-directed layout.

Every option: [Grids and graphs reference](../reference/grids.md).
