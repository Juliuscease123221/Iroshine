# iroshine

*EE-roh-shine* · from Japanese 色 *iro*, "colour": colour-shine.

Turn an algorithm into a beautiful, musical animation. Paste your LeetCode solution unchanged, name
the variables you want to see, and iroshine works out what to animate from what your code does.
Built on [Manim](https://www.manim.community/).

**[Documentation](https://juliuscease123221.github.io/Iroshine/)** ·
**[Gallery](https://juliuscease123221.github.io/Iroshine/gallery/)**

```python
from iroshine import DUSK as P, BarList, BarStyle, Pointer, Readout, Stage


class Solution:                                   # LeetCode 11, exactly as submitted
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
    Readout("best", position=(4.2, 3.0), label="most water", color=P.text, label_color=P.muted),
)
stage.run(Solution().maxArea, [1, 8, 6, 2, 5, 4, 8, 3, 7])
stage.render("out.mp4")
```

## Install

Needs Python 3.10+, FFmpeg, and the Cairo and Pango libraries
([details for each system](https://juliuscease123221.github.io/Iroshine/getting-started/install/)).

```bash
git clone https://github.com/Juliuscease123221/Iroshine.git
cd Iroshine
pip install -e .
cd examples && python 00_start_here.py low
```

## What's in the box

- **Views for lists, grids, sets, graphs, points and text**, each bound to a variable name in your code
- **Sound**: every event plays a note from a musical scale, synthesized by the library
- **Colour**: CSS-style gradients blended in OKLab, and five ready-made palettes
- **Video**: 4K at 60 fps, fast drafts, vertical formats and seamless loops

## Repository

| Folder | Contents |
|---|---|
| `iroshine/` | the library |
| `examples/` | 17 scripts, from a ten-line starter to hard problems |
| `shorts/` | two finished vertical, looping videos |
| `docs/` | the documentation site |

## License

Apache 2.0. Copyright 2026 Julius Sanchez.
