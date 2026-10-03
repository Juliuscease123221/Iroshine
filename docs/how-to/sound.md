# Design the sound

Every event plays a note. Notes are synthesized by the library and tuned to a musical scale, so
whatever your algorithm does, it stays in key.

```python
from iroshine import Sound, Stage

Stage(sound=Sound(scale="pentatonic", key="D", octave=3,
                  instrument="wood",            # the main voice
                  finale_instrument="log_drum", # the closing notes
                  soft_instrument="wood_soft",  # quiet notes: pops, recolours, loop returns
                  tick_instrument="wood_soft",  # the tiny focus ticks
                  reverb=0.04))
```

## Scales

`pentatonic`, `major`, `minor`, `dorian`, `lydian`, `hirajoshi`, `blues`. Pentatonic is the safest:
any two of its notes sound fine together, which matters when the algorithm chooses the melody.

## Instruments

| Family | Names |
|---|---|
| Plucked and struck | `harp`, `bell`, `marimba`, `music_box` |
| Pure | `soft_sine`, `tick` |
| Wood | `wood`, `wood_soft`, `log_drum` |
| Water | `drip`, `plop`, `pour`, `drop_bell`, `splash`, `plish`, `sploosh`, `sploosh_mid`, `trickle` |
| Soft | `squish`, `squish_big` |

## Pitch that follows the data

```python
Sound(pitch_by_size="down")       # bigger values play lower, like real objects
Sound(size_gain=4)                # …and up to 4 dB louder
Sound(grid_set_pitch="value")     # on a grid: the value written is the scale step
Sound(compare_notes=True)         # a soft note for each comparison (the "sound of sorting")
```

## Make repeats sound less mechanical

```python
Sound(humanize=1.0)   # small random differences in pitch, loudness and timing between repeated notes
```

## The ending

```python
from iroshine import Finale

Stage(finale=Finale(style="sweep"))       # a highlight runs across the answer over an ascending run
Stage(finale=Finale(grid_ripple=True, chord_on_ripple=True))   # replay a grid's changes as one rising ripple
Stage(sound=Sound(finale=False))          # no closing riff
```

## Silence

```python
Stage(sound=Sound(enabled=False))
```

## Advice for phones

Phone speakers reproduce very little below about 1 kHz, so truly low notes disappear. Wooden
instruments at `octave=3` carry because of their overtones. If you export for social media, normalise
the loudness afterwards:

```bash
ffmpeg -i in.mp4 -c:v copy -af "loudnorm=I=-15:TP=-1.5:LRA=11" -ar 48000 -c:a aac -b:a 256k out.mp4
```

Every option: [Sound reference](../reference/settings.md#sound).
