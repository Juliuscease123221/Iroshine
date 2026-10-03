# Your first video

This lesson takes one LeetCode problem from solution to rendered video. It uses
[Container With Most Water](https://leetcode.com/problems/container-with-most-water/) (LeetCode 11),
and the finished script is `examples/00_start_here.py`.

<video src="../../assets/videos/00_start_here.mp4" poster="../../assets/videos/00_start_here.jpg" controls loop muted playsinline></video>

## 1. Paste your solution

Write the solution exactly as you would submit it. Nothing in it mentions iroshine.

```python
class Solution:
    def maxArea(self, height):
        l, r, best = 0, len(height) - 1, 0
        while l < r:
            best = max(best, min(height[l], height[r]) * (r - l))
            if height[l] < height[r]:
                l += 1
            else:
                r -= 1
        return best
```

## 2. Say what to show

Make a `Stage` and add one object for each variable you want on screen. The names you pass
(`"height"`, `"l"`, `"r"`, `"best"`) must match the variable names in your code.

```python
from iroshine import DUSK as P, BarList, BarStyle, Pointer, Readout, Stage

stage = Stage(background=P.sky)
stage.add(
    BarList("height", position=(0, -0.4), size=(11, 4.8),          # the list `height`, as bars
            bar=BarStyle(fill=P.gradient(by="value"), gap=0.2)),
    Pointer("l", on="height", color=P.accent),                     # a marker that follows `l`
    Pointer("r", on="height", color=P.accent),                     # a marker that follows `r`
    Readout("best", position=(4.2, 3.0), label="most water",       # `best`, as a number
            color=P.text, label_color=P.muted),
)
```

`DUSK` is one of the built-in [palettes](../how-to/color.md): a matching background, gradient,
accent and text colours.

## 3. Run it like a test case

```python
stage.run(Solution().maxArea, [1, 8, 6, 2, 5, 4, 8, 3, 7])
```

This runs your solution once and records everything it does to the variables you named.

## 4. Render

```python
import sys
stage.render("first.mp4", quality=sys.argv[1] if len(sys.argv) > 1 else "high")
```

```bash
python first.py low       # 480p draft: fast, for iterating
python first.py medium    # 1080p, 30 fps
python first.py           # the stage's full resolution (4K at 60 fps by default): slow
```

Work at `low` until the video looks right, then render the final once.

## What you just saw

- The **bars** are the input list.
- The two **markers** walk inward because the code changes `l` and `r`.
- The **number** climbs to 49 because the code assigns to `best`.
- Each change plays a **note**, and the ending plays a short closing phrase.

You wrote no animation code. To change how any of it looks or sounds, see the
[how-to guides](../how-to/index.md); to see what else is possible, see the [gallery](../gallery.md).
