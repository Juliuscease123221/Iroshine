# Changelog

## 0.5.0

First public release.

**Views**

- `BarList` for lists, with `BarStyle`, `Labels`, `Panel`, `Axis`; swaps detected and animated as one move
- `Pointer`, `Readout`, `Region`, `Pack`, `Tower` for plain local variables
- `GridView` with `Mark`, `Walls`, `GridBoxes`, `Stamp`; `GraphView`
- `PointSet`, `Polyline`, `PointStrip`
- `WordStrip`, `LineComposer`
- `TilingView` (square-tiling searches) and `WallToWall` (flood-and-crossing problems)
- a duck-typed handler interface for writing your own views

**Look**

- `Gradient` with positioned stops, OKLab blending, and four drivers (`rank`, `value`, `index`, `origin`)
- palettes: `DUSK`, `GARDEN`, `ELYSIUM`, `DARK_CHERRY`, `LAKE`
- gradient backgrounds, bar shading, ground slabs, film grain
- `CodePanel` with a gliding highlight, loop-span highlighting, and cropping; `code_style` themes

**Sound**

- seven scales; plucked, wooden, water and soft instruments, all synthesized
- `humanize`, data-driven pitch, finales (`sweep`, `recolor`, grid ripple with a closing chord)

**Video**

- 4K at 60 fps by default, with `low` and `medium` drafts that keep the frame's shape
- vertical formats, instant intros, and seamless loops (`Timing(intro="instant", loop=True)`)
