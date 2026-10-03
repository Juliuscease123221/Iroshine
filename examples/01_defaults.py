"""
Example 1 — mostly defaults.

Declare which lists you want to see and where; everything else is the
built-in look (hyrule theme, harp on a D pentatonic scale).
"""

from iroshine import BarList, Caption, CodePanel, Stage


class Solution:                                   # LeetCode 496, untouched
    def nextGreaterElement(self, nums1, nums2):
        greater = {}
        stack = []
        for n in nums2:
            while stack and stack[-1] < n:
                greater[stack.pop()] = n
            stack.append(n)
        return [greater.get(x, -1) for x in nums1]


stage = Stage()
stage.add(
    BarList("nums1",  position=(-2.35, 2.9),  size=(9.0, 1.75)),
    BarList("nums2",  position=(-2.35, 0.97), size=(9.0, 1.75)),
    BarList("stack",  position=(-2.35, -0.96), size=(9.0, 1.75)),
    BarList("result", position=(-2.35, -2.89), size=(9.0, 1.75)),
    CodePanel(position=(4.6, 3.0)),
    Caption(position=(2.4, -3.6), font_size=15),
)
stage.run(Solution().nextGreaterElement, [5, 3, 4, 2, 8], [1, 5, 3, 6, 4, 2, 7, 8])

if __name__ == "__main__":
    import sys
    stage.render("01_defaults.mp4", quality=sys.argv[1] if len(sys.argv) > 1 else "high")
