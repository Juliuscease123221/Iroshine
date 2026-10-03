# Make a vertical looping Reel

Two finished examples live in `shorts/`: `erect_the_fence.py` and `fewest_squares.py`.

## The canvas

```python
from iroshine import Stage, Timing

stage = Stage(resolution=(1080, 1920), fps=60, crf=16,
              timing=Timing(intro="instant", loop=True, loop_time=0.6, end_hold=0.12))
```

- `resolution=(1080, 1920)` is 9:16 for Reels and TikTok. Use `(1440, 2560)` for YouTube Shorts.
- `intro="instant"` means the first frame is already fully composed.
- `loop=True` returns everything to how the first frame looked, so the video replays seamlessly.
- `low` and `medium` renders keep the frame's shape (480×854 and 1080×1920).

## Stay inside the safe zone

Apps cover the edges of a vertical video with their own interface. On a 1080×1920 frame, keep what
matters clear of roughly the top 250 px, the left 70 px, the right 70 px in the upper half, and the
right 193 px in the lower half where the like and comment buttons sit. The scene is 4.5 × 8 units, so
240 px is one unit:

```python
PX = 240
def X(px):  return px / PX - 2.25
def Yp(px): return 4 - px / PX

LEFT      = X(70) + 0.03            # -1.93
RIGHT_TOP = X(1080 - 70) - 0.03     #  1.93   above the buttons
RIGHT_LOW = X(1080 - 193) - 0.03    #  1.42   beside the buttons
TOP       = Yp(250)                 #  2.96
```

Measure against a screenshot of a posted video on a real phone; apps change their layouts.

## Titles

Titles are plain Manim text, placed with the constants above:

```python
from manim import MarkupText

stage.add(MarkupText('<span letter_spacing="1700">FEWEST SQUARES</span>', font="Inter",
                     weight="MEDIUM", font_size=12, color="#efe9dc")
          .move_to([LEFT + 0.04, TOP - 0.32, 0], aligned_edge=[-1, 0, 0]))
```

## Check the loop

The first and last frames should be identical. Compare them:

```bash
ffmpeg -v error -i out.mp4 -frames:v 1 -y first.png
ffmpeg -v error -sseof -0.05 -i out.mp4 -frames:v 1 -y last.png
ffmpeg -i first.png -i last.png -lavfi psnr -f null - 2>&1 | grep -o "average:[0-9.inf]*"
```

About 50 dB or `inf` means the seam is invisible.

## Things that made the difference

- **One question at a time.** Show the obvious first attempt, then let the video answer "can it do
  better?".
- **Pace by importance.** Routine steps fast, the few moments that matter about a second each.
- **Never make two meaningful changes on the same frame.**
- **Let the sound rise toward the moment that matters, and land there.**
- **Let the answer rest before the loop restarts,** and take it away gradually.
