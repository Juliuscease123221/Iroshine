"""
Build docs/gallery.md from the list below. The videos themselves are small web copies in
docs/assets/videos/ (see docs/contributing.md).

    python tools/gen_gallery.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (video file stem, script, title, one line on what it shows)
LANDSCAPE = [
    ("00_start_here", "examples/00_start_here.py", "Container With Most Water · 11",
     "The starter: one list, two pointers, a running best."),
    ("01_defaults", "examples/01_defaults.py", "Next Greater Element · 496",
     "Four lists and a code panel with every setting left at its default."),
    ("02_neon", "examples/02_neon.py", "Next Greater Element, art-directed",
     "The same solution restyled: pills and lollipops, glow, hop-shaped flights, a custom pop."),
    ("03_riso_quicksort", "examples/03_riso_quicksort.py", "Quicksort, screen-print",
     "A rank gradient: each element owns its colour, so the ramp assembles as the list sorts."),
    ("04_riso_next_greater", "examples/04_riso_next_greater.py", "Next Greater Element, screen-print",
     "Values fly between lists in straight eased lines and keep their colour wherever they go."),
    ("05_garden_quicksort", "examples/05_garden_quicksort.py", "Quicksort · GARDEN",
     "Touching bars read as one silhouette against a gradient sky."),
    ("06_elysium_quicksort", "examples/06_elysium_quicksort.py", "Quicksort · ELYSIUM",
     "A gradient with positioned stops, ink outlines, a paper background."),
    ("07_dusk_rotate_array", "examples/07_dusk_rotate_array.py", "Rotate Array · 189",
     "The three-reversal trick; the rank gradient shows what each reversal does."),
    ("08_garden_sort_colors", "examples/08_garden_sort_colors.py", "Sort Colors · 75",
     "The Dutch-flag partition: three pointers, only swaps."),
    ("09_elysium_wiggle_sort", "examples/09_elysium_wiggle_sort.py", "Wiggle Sort II · 324",
     "Every value flies down into a sorted copy, then back up to its wiggle slot."),
    ("10_dark_cherry_trapping_rain", "examples/10_dark_cherry_trapping_rain.py", "Trapping Rain Water · 42",
     "A stack of indices; each pocket of water is poured in as a Region while a Readout counts."),
    ("11_dark_cherry_rain_pack_fixed", "examples/11_dark_cherry_rain_pack.py", "Trapping Rain Water, packed",
     "Every pocket of water also flies into one block whose area is the answer."),
    ("12_dark_cherry_contain_virus", "examples/12_dark_cherry_contain_virus.py", "Contain Virus · 749",
     "A grid search: cells light up when read, regions are outlined, walls are built."),
    ("13_dusk_strange_printer", "examples/13_dusk_strange_printer.py", "Strange Printer II · 1591",
     "Bounding boxes, a dependency graph, and the print replayed layer by layer."),
    ("14_elysium_erect_the_fence", "examples/14_elysium_erect_the_fence.py", "Erect the Fence · 587",
     "Monotone chain: a path grows over a point set, pulling posts back out when it turns inward."),
    ("15_garden_text_justification", "examples/15_garden_text_justification.py", "Text Justification · 68",
     "Words lift into a line, spaces are dealt out, the line is committed."),
    ("16_dark_cherry_no_consecutive_ones", "examples/16_dark_cherry_no_consecutive_ones.py",
     "Integers without Consecutive Ones · 600",
     "Fibonacci bars built from their two parts, then summed into a tower."),
]
VERTICAL = [
    ("fewest_squares", "shorts/fewest_squares.py", "Fewest Squares · 1240",
     "A backtracking search that speeds into a time-lapse, finds the answer, then proves nothing beats it."),
    ("erect_the_fence", "shorts/erect_the_fence.py", "Erect the Fence · 587",
     "The convex hull as a looping Reel, with the code alongside."),
]
REPO = "https://github.com/Juliuscease123221/Iroshine/blob/main/"


def card(stem, script, title, note):
    return (f'<figure class="card" markdown>\n'
            f'<video src="../assets/videos/{stem}.mp4" poster="../assets/videos/{stem}.jpg" controls loop muted playsinline preload="none"></video>\n'
            f'<figcaption markdown>\n\n### {title}\n\n{note}\n\n[`{script}`]({REPO}{script})\n\n</figcaption>\n'
            f'</figure>\n')


def main():
    md = ["# Gallery\n",
          "Every video here is rendered by a script in the repository; the link under each one opens it. "
          "The videos are small web copies with sound: unmute to hear them.\n",
          "## Vertical, looping\n", '<div class="gallery tall" markdown>\n']
    md += [card(*v) for v in VERTICAL]
    md += ["</div>\n", "## Examples\n", '<div class="gallery" markdown>\n']
    md += [card(*v) for v in LANDSCAPE]
    md += ["</div>\n"]
    (ROOT / "docs" / "gallery.md").write_text("\n".join(md))
    missing = [s for s, *_ in VERTICAL + LANDSCAPE if not (ROOT / "docs/assets/videos" / f"{s}.mp4").exists()]
    if missing:
        print("no video yet for:", missing)


if __name__ == "__main__":
    main()
