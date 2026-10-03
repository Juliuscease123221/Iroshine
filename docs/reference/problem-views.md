# Problem views

Views written for one family of problems.

!!! note "Generated page"
    This page is built from the source by `tools/gen_reference.py`. Edit the comments in the code, not this file.

## TilingView

`from iroshine import TilingView` · defined in `iroshine/tiling.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `cols` | `int` | required | board width, in cells |
| `rows` | `int` | required | board height, in cells |
| `name` | `str` | `"placed"` | the stack of (x, y, size) your code pushes and pops |
| `position` | `Tuple[float, float]` | `(0.0, 0.0)` | where it sits on the stage, as (x, y) in scene units (the stage is 8 units tall, centred on 0, 0) |
| `size` | `Tuple[float, float]` | `(3.0, 3.5)` | its (width, height) in scene units |
| `colors` | `object` | `dict(MONDRIAN)` | {size: colour}, or a function size -> colour |
| `ink` | `Dict[int, str]` | `dict()` | number colour per square size (default: auto) |
| `board` | `str` | `"#262624"` | board colour |
| `frame_color` | `str` | `"#0c0c0c"` | colour, as a hex string |
| `dot` | `str` | `"#4a4944"` | colour of the grid dots |
| `gap` | `float` | `0.09` | the black lines between squares (fraction of a cell) |
| `numbers` | `bool` | `True` | show each value as a number |
| `corner` | `Optional[str]` | `"#fff2c2"` | a marker on the corner the search fills next |
| `place_time` | `float` | `0.55` | seconds |
| `lift_time` | `float` | `0.3` | seconds |
| `done_hold` | `float` | `0.8` | seconds held |
| `montage_frames` | `int` | `44` | act 2: how many snapshots of the search |
| `story` | `str` | `"acts"` | "acts": dive · time-lapse · the winner built again, then a counter "ramp": one continuous search that starts slow (every square lands, solid) and speeds up into the time-lapse, fading to outlines "reveal": a quick first try that shrinks to a thumbnail (the score to beat) · a time-lapse of the WHOLE search, pausing a beat when a better tiling appears · the best tiling snaps in at the very end |
| `best_label` | `str` | `"BEST"` | e.g. "FEWEST" (a label that says what the goal is) |
| `dive_time` | `float` | `0.28` | (reveal) seconds per square in the first try |
| `find_hold` | `float` | `0.55` | (reveal) the beat when a better tiling turns up |
| `thumb_pos` | `Optional[Tuple[float, float]]` | `None` | (reveal) where the first try's thumbnail sits |
| `thumb_width` | `float` | `0.85` | line thickness |
| `thumbnail` | `bool` | `True` | (reveal) False: the first try just fades into the time-lapse (its score lives on in the FEWEST readout) |
| `ramp_events` | `int` | `40` | (ramp) the first N moves are each shown, getting quicker, while |
| `ramp_slow` | `float` | `0.34` | the squares fade from solid to outlines; then the time-lapse |
| `found_style` | `str` | `"hold"` | "proof": show the better tiling when it's found (the climax), keep it faintly under the rest of the search, and show every later attempt being cut off when it reaches that many squares "silent": say nothing until the search ends; FEWEST drops at the reveal "hold": pause on a better tiling, outlined · "number": don't show it (no spoiler); only FEWEST drops, with a bump and a sound, and the time-lapse keeps going. The shape is first seen at the very end |
| `find_transition` | `str` | `"cut"` | (proof) how the time-lapse arrives at the better tiling: "cut": straight to it · "pause": a held beat first (hit-stop) "crossfade": the last attempt dissolves into it "slowmo": the time-lapse slows, the winning path plays live and its squares turn solid as they land (the opening, reversed) |
| `cut_color` | `str` | `"#e0574f"` | (proof) attempts cut off at the ceiling |
| `underlay_opacity` | `float` | `0.3` | (proof) the answer stays faintly visible while the search checks it |
| `outline` | `Optional[str]` | `None` | an ink line around each solid square (shapes read by line, not hue) |
| `outline_width` | `float` | `2.5` | line thickness |
| `end_slowdown` | `int` | `0` | the last N time-lapse frames slow down (a ritardando into the end) |
| `end_slow_dt` | `float` | `0.2` | …to this many seconds per frame |
| `reveal_pause` | `float` | `0.0` | a breath before the answer: the last attempt fades, the board sits empty and quiet for this long, then the answer snaps in |
| `chord_sweep` | `bool` | `False` | at the end, light the winning squares one by one (biggest first), each adding a note to a chord, then ring it out |
| `sweep_step` | `float` | `0.32` | (chord_sweep) seconds between squares |
| `show_count` | `bool` | `True` | False: no SQUARES readout (the board already shows the count) |
| `montage_after` | `int` | `24` | (reveal) snapshots after the best is found (the search proving |
| `montage_after_dt` | `float` | `0.05` | nothing smaller exists goes by quicker: less to see there) |
| `montage_dt` | `float` | `0.075` | seconds per time-lapse frame |
| `ghost` | `str` | `"#8a867d"` | act 2: squares drawn as outlines in this colour |
| `proof_time` | `float` | `1.2` | act 3: the counter runs through the rest of the search |
| `readout_x` | `Optional[float]` | `None` | left edge of the readouts (None: just right of the board) |
| `readout_y` | `float` | `0.0` | height of the top readout |
| `text` | `str` | `"#efe9dc"` | text colour |
| `muted` | `str` | `"#8a867d"` | colour of secondary text |
| `accent` | `str` | `"#f2c230"` | the highlight colour |
| `place_instrument` | `str` | `"log_drum"` | which instrument plays it |
| `lift_instrument` | `str` | `"wood_soft"` | which instrument plays it |
| `tick_instrument` | `str` | `"wood_soft"` | which instrument plays it |
| `sound_arc` | `str` | `"cut"` | (proof + outline_build) how the time-lapse ticks are phrased "cut": one rise across the whole time-lapse (the original) "arc": the rise peaks at the find and never restarts mid-way: time-lapse → the winning build (same line, slowing down) → lands on the home note as it fills → the count climbs an octave to the hit → a rest → the proof is a new, softer rise "coda": like "arc", but the proof sits low and steady (the find stays the peak), lifting only as it slows into the ending |
| `highlight` | `str` | `"flash"` | how a square is pointed at when counted / swept: "flash": it flashes white · "pop": it brightens in its own colour and grows into its ink line (the size colour stays readable); the hit is one small breath of the whole tiling |
| `find_count` | `bool` | `True` | (outline_build) count the squares when the answer is found |
| `ending` | `str` | `"reveal"` | (proof) "reveal": the answer fades out and is shown again "confirm": the faint answer under the proof lifts back to full colour, on one chord — the same squares, never re-revealed "confirm_sweep": lifts back, then the chord sweep counts it |
| `loop_out` | `str` | `"fade"` | how the answer leaves before the loop restarts: "fade": with everything else · "dissolve": it rests for |
| `loop_hold` | `float` | `0.9` | `loop_hold`, then its colour drains back to outlines (the opening's solid → outline, again) which fade as the board resets |
| `tick_every` | `int` | `1` | fast time-lapse frames (under 0.1 s) tick only every Nth frame |

## WallToWall

`from iroshine import WallToWall` · defined in `iroshine/crossing.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `rows` | `int` | required | number of rows |
| `cols` | `int` | required | number of columns |
| `set` | `str` | `"water"` | the set your code adds flooded cells to |
| `cells` | `str` | `"cells"` | the input list of cells (the flood order) |
| `one_indexed` | `bool` | `True` | LeetCode 1970 numbers rows and columns from 1 |
| `position` | `Tuple[float, float]` | `(0.0, 0.0)` | where it sits on the stage, as (x, y) in scene units (the stage is 8 units tall, centred on 0, 0) |
| `size` | `Tuple[float, float]` | `(4.0, 3.0)` | its (width, height) in scene units |
| `gap` | `float` | `0.1` | space between cells (fraction of a cell) |
| `corner` | `float` | `0.18` | cell corner radius (fraction of a cell) |
| `land` | `str` | `"#6b5f47"` | land colour |
| `land_top` | `str` | `"#7c6f55"` | a lighter lip on each land tile (reads as raised ground) |
| `tile_lips` | `bool` | `True` | False: flat tiles (less texture, calmer) |
| `water` | `str` | `"#2b4462"` | a pool touching neither wall |
| `left` | `str` | `"#2fa7a0"` | pools connected to the left wall |
| `right` | `str` | `"#4f7be0"` | pools connected to the right wall |
| `chain` | `str` | `"#e9f6ff"` | the wall-to-wall chain |
| `joined` | `str` | `"#3f8fc2"` | the pool that finally touches both walls (the chain runs through it) |
| `wall_width` | `float` | `0.07` | line thickness |
| `walker` | `bool` | `True` | draw a top-to-bottom path through the land |
| `walker_color` | `str` | `"#f3e3b5"` | colour, as a hex string |
| `walker_dot` | `bool` | `True` | a little walker travelling the route, top to bottom |
| `walker_dot_color` | `Optional[str]` | `None` | (None: walker_color) |
| `walker_period` | `Optional[float]` | `2.6` | seconds for one trip down · None: the walker stands at the start of the route and only moves when the route changes |
| `chain_edge` | `Optional[str]` | `None` | a dark rim under the chain (reads like a crack in the ground) |
| `day_time` | `float` | `0.22` | seconds per flooded cell (early days a little quicker, the days when the two sides are about to meet a little slower) |
| `event_time` | `float` | `0.34` | …when a pool merges, reaches a wall, or the walker reroutes |
| `final_hold` | `float` | `0.5` | a held breath before the drop that closes the chain |
| `claim_walls` | `bool` | `False` | a wall stays lit once water reaches it (instead of a flash) |
| `claimed` | `Optional[str]` | `None` | its lit colour (None: the side's colour) |
| `pacing` | `str` | `"flat"` | "importance": plain drops are quick; a pool reaching a wall or the route being cut get about a second each (one change at a time) |
| `plain_time` | `float` | `0.26` | seconds |
| `merge_time` | `float` | `0.4` | seconds |
| `wall_time` | `float` | `0.9` | seconds |
| `cut_time` | `float` | `0.35` | (importance) the route is cut… |
| `redraw_time` | `float` | `0.75` | …then the new route draws in |
| `code_follow` | `str` | `"all"` | "key": the code highlight only moves on the moments that matter |
| `drop` | `str` | `"drip"` | the instrument for a cell flooding |
| `drop_gain` | `float` | `-6.0` | loudness, in dB |
| `merge` | `Optional[str]` | `"plop"` | the instrument for two pools joining |
| `merge_gain` | `float` | `-12.0` | loudness, in dB |
| `wall` | `Optional[str]` | `"wood_soft"` | the instrument for a pool reaching a wall |
| `wall_gain` | `float` | `-9.0` | loudness, in dB |
| `reroute` | `Optional[str]` | `"wood_soft"` | the instrument for the walker changing route |
| `reroute_gain` | `float` | `-16.0` | loudness, in dB |
| `final` | `str` | `"sploosh_mid"` | the instrument for the drop that closes the chain |
| `final_gain` | `float` | `-3.0` | loudness, in dB |
| `run_instrument` | `str` | `"wood"` | which instrument plays it |
| `humanize` | `float` | `1.0` | 0..1: small random differences in pitch, loudness and timing between repeated notes |
