# iroshine

*EE-roh-shine* · from Japanese 色 *iro*, "colour": colour-shine.

Turn an algorithm into a beautiful, musical animation. You paste your LeetCode solution unchanged,
name the variables you want to see, and iroshine works out what to animate from what your code does.

```python
from iroshine import DUSK as P, BarList, BarStyle, Pointer, Readout, Stage


class Solution:                       # LeetCode 11, exactly as submitted
    def maxArea(self, height):
        l, r, best = 0, len(height) - 1, 0
        while l < r:
            best = max(best, min(height[l], height[r]) * (r - l))
            if height[l] < height[r]:
                l += 1
            else:
                r -= 1
        return best


stage = Stage(background=P.sky)
stage.add(
    BarList("height", position=(0, -0.4), size=(11, 4.8),
            bar=BarStyle(fill=P.gradient(by="value"), gap=0.2)),
    Pointer("l", on="height", color=P.accent),
    Pointer("r", on="height", color=P.accent),
    Readout("best", position=(4.2, 3.0), label="most water"),
)
stage.run(Solution().maxArea, [1, 8, 6, 2, 5, 4, 8, 3, 7])
stage.render("out.mp4")
```

That is the whole script. It renders this:

<video src="assets/videos/00_start_here.mp4" poster="assets/videos/00_start_here.jpg" controls loop muted playsinline></video>

And with more direction, the same library makes this (see the [gallery](gallery.md)):

<video class="tall" src="assets/videos/fewest_squares.mp4" poster="assets/videos/fewest_squares.jpg" controls loop muted playsinline></video>

## Why it exists

- **You never write an animation.** The library records what your code does to the variables you
  named and replays it.
- **It makes sound.** Every event plays a note from a musical scale, so a run of the algorithm is
  also a small piece of music.
- **It is built on [Manim](https://www.manim.community/).** Everything is vector-drawn, and anything
  iroshine doesn't cover you can add as plain Manim.

## Where to go next

| If you want to… | Read |
|---|---|
| install it and render something in five minutes | [Getting started](getting-started/install.md) |
| see what it can make | [Gallery](gallery.md) |
| do one specific thing | [How-to guides](how-to/index.md) |
| look up an option | [Reference](reference/index.md) |
| understand what happens under the hood | [How it works](how-it-works.md) |
