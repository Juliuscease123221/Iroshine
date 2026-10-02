"""
START HERE: your first iroshine video.

  1. Paste your LeetCode solution into the Solution class, exactly as you submitted it.
  2. Tell the Stage what to show: BarList("height") draws the list named `height`,
     Pointer("l", on="height") follows the variable `l`, and Readout("best") shows `best` as a number.
     Those names must match the variable names in your code.
  3. Call stage.run(...) with the method and the input, just like a LeetCode test case.
  4. Run:  python 00_start_here.py low      (a fast 480p draft, good for iterating)
           python 00_start_here.py medium   (1080p)
           python 00_start_here.py          (full 4K, 60 fps: slow, for the final)
"""

import sys

from iroshine import DUSK as P, BarList, BarStyle, Pointer, Readout, Stage


class Solution:                                   # LeetCode 11 · Container With Most Water
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

if __name__ == "__main__":
    stage.render("00_start_here.mp4", quality=sys.argv[1] if len(sys.argv) > 1 else "high")
