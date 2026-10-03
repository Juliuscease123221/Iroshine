# Show the code

```python
from iroshine import CodePanel

CodePanel(position=(4.6, 3.0))                      # your solution, with the running line highlighted
```

## A calmer highlight

By default the highlight jumps to each line as it runs. In a tight loop that flickers faster than
anyone can read. Let it glide, and widen it to the enclosing loop:

```python
CodePanel(glide=True, glide_speed=8,
          span="inner")       # "line" | "loop" (the outermost loop) | "inner" (the innermost loop block)
```

## Show only the part that matters

```python
CodePanel(show=("if len(placed)", "put(x, low, s, -1)"))
```

This crops the panel to the lines from the first one containing the first snippet to the first one
after it containing the second, dedented and set larger.

## Colours

`style` takes any [Pygments style](https://pygments.org/styles/) name. To build a theme from your own
palette:

```python
from iroshine import code_style

CodePanel(background="#1b1b1a",
          style=code_style(text="#e6e1d6", keyword="#e0574f", string="#fdbb2d",
                           number="#8fa3e6", comment="#8a867d"),
          highlight="#fdbb2d", highlight_opacity=0.16, line_numbers=False)
```

## Captions

```python
from iroshine import Beat, Beats, Caption

Caption(position=(2.4, -3.6), font_size=15)         # a small line describing each step as it happens

Beats([Beat("What's the shortest fence around every tree?", at="start"),
       Beat("Sort the trees left to right.", at="trees.sort()"),      # fires when that line runs
       Beat("Turns inward? Pull the post.", on="pop", list="hull"),   # or the first time something happens
       Beat("The shortest fence.", at="end")])
```

`Beats` are large captions that appear word by word, each with a soft chime.

Every option: [Code and captions reference](../reference/code-and-captions.md).
