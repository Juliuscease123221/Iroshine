# Sound, timing, motion, finale

Global settings passed to the `Stage`.

!!! note "Generated page"
    This page is built from the source by `tools/gen_reference.py`. Edit the comments in the code, not this file.

## Sound

`from iroshine import Sound` · defined in `iroshine/style.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `scale` | `str` | `"pentatonic"` | pentatonic \| major \| minor \| dorian \| lydian \| hirajoshi \| blues |
| `key` | `str` | `"D"` | the scale's root note |
| `octave` | `int` | `4` | which octave scale step 0 sits in |
| `instrument` | `str` | `"harp"` | harp \| bell \| marimba \| music_box \| soft_sine \| tick \| wood \| wood_soft \| log_drum \| water: drip \| plop \| pour \| drop_bell \| splash \| plish \| sploosh \| sploosh_mid \| trickle · soft: squish \| squish_big |
| `finale_instrument` | `str` | `"bell"` | which instrument plays it |
| `soft_instrument` | `str` | `"soft_sine"` | the quiet notes: pops, recolors, loop returns (try "wood_soft") |
| `tick_instrument` | `str` | `"tick"` | the tiny focus ticks (try "wood_soft") |
| `grid_instrument` | `Optional[str]` | `None` | one instrument for every grid / graph note (None: the original mix) |
| `humanize` | `float` | `0.0` | 0..1: grid notes get small random differences in pitch (±12 cents at 1), loudness (±2 dB) and timing (±8 ms), so repeats never sound machine-made |
| `grid_set_pitch` | `str` | `"cycle"` | a grid cell changing value: "cycle" walks up the scale · "rank": each distinct new value gets the next scale step (lowest value = lowest note) · "value": the new value is the scale step (e.g. store the minute a cell changed, and later minutes play higher) |
| `reverb` | `float` | `0.35` | 0..1 wet mix |
| `pitch_by_size` | `str` | `"up"` | "up": bigger values play higher · "down": bigger play lower, like real objects (a big drum sounds lower than a small one) |
| `size_gain` | `float` | `0.0` | dB: bigger values play up to this much louder (smaller ones quieter) |
| `volume` | `float` | `0.8` | 0..1 |
| `landing_interval` | `int` | `2` | a move plays its note, then this many scale steps up on landing |
| `tick_reads` | `bool` | `False` | a tiny tick for every read |
| `compare_notes` | `bool` | `False` | a soft note for each comparison (the "sound of sorting") |
| `finale` | `bool` | `True` | the closing riff |
| `enabled` | `bool` | `True` | False: a silent video |

## Timing

`from iroshine import Timing` · defined in `iroshine/style.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `speed` | `float` | `1.0` | global multiplier (2 = twice as fast) |
| `skip` | `Sequence[str]` | `()` | event types to leave out: "read", "compare" |
| `pause_between` | `float` | `0.0` | seconds of stillness after every event |
| `end_hold` | `float` | `2.5` | seconds held on the last frame |
| `intro` | `str` | `"animate"` | "instant": the first frame already shows the inputs (hooks, clean loops) |
| `loop` | `bool` | `False` | at the end, everything returns to how the first frame looked |
| `loop_time` | `float` | `1.1` | how long that return takes |

## Motion

`from iroshine import Motion` · defined in `iroshine/style.py`

How one kind of event animates. Only the fields that make sense are used.

| Option | Type | Default | What it does |
|---|---|---|---|
| `duration` | `Optional[float]` | `None` | seconds the animation takes |
| `easing` | `Union[str, Callable, None]` | `None` | the name of a Manim rate function, e.g. "ease_in_out_cubic" |
| `color` | `Optional[Color]` | `None` | highlight / in-flight color (None = keep the bar's own color) |
| `path` | `str` | `"straight"` | moves: "straight" \| "arc" \| "hop" |
| `arc` | `float` | `1.2` | radians of curvature for path="arc" |
| `trail` | `bool` | `False` | moves: leave a fading trail |
| `sparkle` | `bool` | `False` | landing sparkle |
| `squash` | `bool` | `False` | little squash on landing |
| `exit` | `str` | `"fade"` | pops: "fade" \| "float_up_fade" \| "shrink" \| "drop" \| "burst" |
| `style` | `str` | `"pulse"` | reads/compares: "pulse" \| "none" |
| `lag` | `float` | `0.3` | when many bars fly at once |

## Finale

`from iroshine import Finale` · defined in `iroshine/style.py`

| Option | Type | Default | What it does |
|---|---|---|---|
| `target` | `Optional[str]` | `"result"` | which list to celebrate (None: skip the bar sweep) |
| `style` | `str` | `"sweep"` | "sweep": a highlight runs across the bars · "recolor": bars turn `color` |
| `color` | `Color` | `"#f3e08a"` | colour, as a hex string |
| `text` | `Optional[str]` | `None` | text colour |
| `text_position` | `Optional[Tuple[float, float]]` | `None` |  |
| `font` | `str` | `"Inter"` | font family |
| `font_size` | `float` | `34` | text size |
| `letter_spacing` | `Optional[int]` | `None` | e.g. 1400: the text is tracked out like the titles (Pango units) |
| `sparkle` | `bool` | `False` |  |
| `region_buildup` | `bool` | `True` | the closing shimmer over Regions (e.g. water) plays a rising run of notes |
| `count_regions` | `bool` | `False` | instead: count the Regions one by one (+area each), recounting the Readout from 0, over a rising build-up, then the finishing chord |
| `count_label_color` | `Optional[Color]` | `None` | colour of the "+n" labels (None: `color`) |
| `grid_ripple` | `bool` | `False` | replay a grid's changes as one fast ripple: cells pulse in order of their value (lowest first), one rising note per value, then the finishing chord |
| `grid_ripple_skip` | `Sequence` | `(0, 1)` | values that don't take part in the ripple |
| `ripple_instrument` | `Optional[str]` | `None` | the ripple's notes (None: Sound.instrument) |
| `chord_on_ripple` | `bool` | `False` | the finishing chord lands exactly as the ripple ends (no gap between the build-up and its resolution) |
| `chord_deg` | `Optional[int]` | `None` | the finishing chord's root scale step (None: two octaves up) |

## Grain

`from iroshine import Grain` · defined in `iroshine/style.py`

Film / print grain added over the finished video (needs the ffmpeg command-line tool).

| Option | Type | Default | What it does |
|---|---|---|---|
| `amount` | `float` | `8` | 0..~30; 6–12 reads as print texture, 20+ as heavy film |
| `animated` | `bool` | `False` | False: fixed, like paper (small files) · True: "boils" like film (≈5× bigger, slower) |
