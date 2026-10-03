# Draw points and paths

```python
from iroshine import Gradient, PointSet, Polyline

PointSet("trees", position=(0, -0.3), size=(12.6, 6.3), radius=0.11,
         fill=Gradient("#93b4c6", "#86bf8e", "#b4d68f", "#e8e2b8", by="index"),
         focus="p")                       # ring the point the variable `p` currently holds
Polyline("hull", on="trees",              # the list `hull`, drawn as a growing path over `trees`
         color="#2f352e", width=4,
         probe="p",                       # a dashed feeler from the path's end to the candidate `p`
         fill="#86bf8e", fill_opacity=0.35)
```

- **`PointSet`** draws a list of `[x, y]` points. Sorting the list (`trees.sort()`) recolours the
  dots by their new order, so you can watch the sort happen.
- **`Polyline`** draws a list of points as a path. `hull.append(p)` extends it; `hull.pop()` pulls the
  last post back out. That is all a convex-hull video needs: see `examples/14_elysium_erect_the_fence.py`.
- `push_time` and `pop_time` set how long each move takes.

For looping videos, `Polyline(..., ghost=True, loop=True)` draws the finished answer faintly from the
first frame and returns to that state at the end. See [Make a vertical looping Reel](reels.md).

Every option: [Geometry reference](../reference/geometry.md).
