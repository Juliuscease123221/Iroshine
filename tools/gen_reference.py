"""
Build the reference pages (docs/reference/*.md) from the library source.

Every option in iroshine is a dataclass field with a short comment beside it. This script reads those
fields and comments straight from the source, so the reference can never drift from the code.

    python tools/gen_reference.py
"""

import ast
import io
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "iroshine"
OUT = ROOT / "docs" / "reference"

# page -> (title, intro, [class names])
PAGES = {
    "stage": ("Stage", "The canvas, the run, and the render.", ["Stage", "HookContext"]),
    "settings": ("Sound, timing, motion, finale",
                 "Global settings passed to the `Stage`.",
                 ["Sound", "Timing", "Motion", "Finale", "Grain"]),
    "bars": ("Bars", "Lists drawn as bars, and everything about how a bar looks.",
             ["BarList", "BarStyle", "Labels", "Panel", "Axis"]),
    "variables": ("Variables", "Views that follow plain local variables in your solution.",
                  ["Pointer", "Readout", "Region", "Pack", "Tower"]),
    "grids": ("Grids and graphs", "2-D lists, sets of cells, and dependency graphs.",
              ["GridView", "Mark", "Walls", "GridBoxes", "Stamp", "GraphView"]),
    "geometry": ("Geometry", "Points and paths.", ["PointSet", "Polyline", "PointStrip"]),
    "text": ("Text", "Lists of strings as word tiles and typeset lines.", ["WordStrip", "LineComposer"]),
    "code-and-captions": ("Code and captions", "Your source on screen, and words over the picture.",
                          ["CodePanel", "code_style", "Caption", "Beats", "Beat"]),
    "color": ("Colour", "Gradients and ready-made palettes.", ["Gradient", "Palette"]),
    "problem-views": ("Problem views", "Views written for one family of problems.",
                      ["TilingView", "WallToWall"]),
}


# Options whose meaning is the same everywhere get one shared description (used only when the source has
# no comment of its own beside the field).
COMMON = {
    "name": "the variable in your solution that this view is bound to",
    "position": "where it sits on the stage, as (x, y) in scene units (the stage is 8 units tall, centred on 0, 0)",
    "size": "its (width, height) in scene units",
    "color": "colour, as a hex string",
    "fill": "fill colour",
    "stroke": "outline colour (None: no outline)",
    "stroke_width": "outline thickness",
    "opacity": "0..1",
    "fill_opacity": "0..1",
    "corner_radius": "how rounded the corners are",
    "font": "font family",
    "font_size": "text size",
    "weight": "font weight",
    "width": "width, in scene units",
    "padding": "space between the edge and the contents",
    "duration": "seconds the animation takes",
    "easing": "the name of a Manim rate function, e.g. \"ease_in_out_cubic\"",
    "sound": "whether it plays a note",
    "text": "text colour",
    "muted": "colour of secondary text",
    "accent": "the highlight colour",
    "background": "background colour",
    "on": "the name of the list or grid it is drawn on",
    "when": "the variable whose change triggers it",
    "var": "the variable in your solution it follows",
    "rows": "number of rows",
    "cols": "number of columns",
    "humanize": "0..1: small random differences in pitch, loudness and timing between repeated notes",
    "numbers": "show each value as a number",
    "labels": "show text labels",
    "gap": "space between neighbours, as a fraction of one slot",
}
SUFFIX = [("_time", "seconds"), ("_gain", "loudness, in dB"), ("_instrument", "which instrument plays it"),
          ("_color", "colour, as a hex string"), ("_opacity", "0..1"), ("_width", "line thickness"),
          ("_size", "text size"), ("_font", "font family"), ("_hold", "seconds held")]
SPECIFIC = {
    ("Stage", "background"): "a colour, a list of colours (a top-to-bottom gradient), or a `Gradient`",
    ("Stage", "resolution"): "(width, height) in pixels; (1080, 1920) for a vertical Reel",
    ("Stage", "fps"): "frames per second",
    ("Stage", "sound"): "a `Sound` (None: the defaults)",
    ("Stage", "timing"): "a `Timing` (None: the defaults)",
    ("Stage", "finale"): "a `Finale`, or None for no closing flourish",
    ("Stage", "caption"): "a `Caption` shown throughout",
    ("Stage", "grain"): "a `Grain` for film or print texture (None: clean)",
    ("Stage", "crf"): "encoder quality: lower is better and bigger (12–18 is visually lossless)",
    ("TilingView", "rows"): "board height, in cells", ("TilingView", "cols"): "board width, in cells",
    ("TilingView", "board"): "board colour", ("TilingView", "dot"): "colour of the grid dots",
    ("WallToWall", "drop"): "the instrument for a cell flooding", ("WallToWall", "merge"): "the instrument for two pools joining",
    ("WallToWall", "wall"): "the instrument for a pool reaching a wall", ("WallToWall", "reroute"): "the instrument for the walker changing route",
    ("WallToWall", "final"): "the instrument for the drop that closes the chain", ("WallToWall", "land"): "land colour",
    ("BarList", "bar"): "how each bar looks: a `BarStyle`", ("BarList", "panel"): "the card behind the list: a `Panel`, or None",
    ("BarList", "axis"): "baseline, ground and guide lines: an `Axis`",
    ("Labels", "values"): "show each bar's value", ("Labels", "indices"): "show each bar's index",
    ("Axis", "baseline"): "draw a hairline under the bars",
    ("CodePanel", "highlight"): "colour of the line highlight", ("CodePanel", "line_numbers"): "show line numbers",
    ("Beats", "beats"): "the captions, in order",
    ("Gradient", "*stops"): "colours, or (colour, position) pairs, or one {position: colour} dict",
    ("Gradient", "by"): "what drives the colour on a BarList: \"rank\", \"value\", \"index\" or \"origin\"",
    ("Gradient", "space"): "blend space: \"oklab\", \"oklch\", \"srgb\" or \"linear\"",
    ("Gradient", "steps"): "posterize into this many flat bands (None: smooth)",
    ("Region", "x0"): "left edge: an expression over your solution's local variables, or a function of them",
    ("Region", "x1"): "right edge (same form as x0)", ("Region", "y0"): "bottom edge (same form as x0)",
    ("Region", "y1"): "top edge (same form as x0)",
    ("Pack", "rotate"): "let pieces turn 90° if that packs squarer",
    ("GridView", "colors"): "{value: colour}, or a function value -> colour: a cell's colour follows its current value",
    ("GridView", "marks"): "{set name: Mark}: an overlay on every cell that is a member of that set",
    ("GridView", "walls"): "a `Walls` rule for drawing boundaries between cells",
    ("Walls", "between"): "draw a wall on every edge between a cell with the first value and one with the second",
    ("GridBoxes", "top"): "name of the list holding each box's top row", ("GridBoxes", "bottom"): "name of the list holding each box's bottom row",
    ("GridBoxes", "left"): "name of the list holding each box's left column", ("GridBoxes", "right"): "name of the list holding each box's right column",
    ("Readout", "format"): "a Python format string for the number",
    ("TilingView", "sweep_step"): "(chord_sweep) seconds between squares", ("TilingView", "montage_dt"): "seconds per time-lapse frame",
    ("TilingView", "readout_x"): "left edge of the readouts (None: just right of the board)", ("TilingView", "readout_y"): "height of the top readout",
    ("Sound", "key"): "the scale's root note", ("Sound", "octave"): "which octave scale step 0 sits in",
    ("Sound", "tick_reads"): "a tiny tick for every read", ("Sound", "enabled"): "False: a silent video",
    ("Timing", "pause_between"): "seconds of stillness after every event", ("Timing", "end_hold"): "seconds held on the last frame",
}


def fallback(cls, name, typ=""):
    if (cls, name) in SPECIFIC:
        return SPECIFIC[(cls, name)]
    if name == "size" and "Tuple" not in typ:
        return "how big it is, in scene units"
    if name in COMMON:
        return COMMON[name]
    for suf, text in SUFFIX:
        if name.endswith(suf):
            return text
    return ""


def comments_by_line(text):
    out = {}
    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
        if tok.type == tokenize.COMMENT:
            out[tok.start[0]] = (tok.start[1], tok.string.lstrip("#").strip())
    return out


def code_lines(text):
    """Line numbers that hold code (not only a comment / blank)."""
    lines = set()
    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
        if tok.type not in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
                            tokenize.DEDENT, tokenize.ENDMARKER):
            lines.update(range(tok.start[0], tok.end[0] + 1))
    return lines


def esc(s):
    return s.replace("|", "\\|").replace("\n", " ")


def short(src, limit=46):
    src = " ".join(src.split())
    if src.startswith("field(default_factory=lambda: ") and src.endswith(")"):
        src = src[len("field(default_factory=lambda: "):-1]
    elif src.startswith("field(default_factory=") and src.endswith(")"):
        src = src[len("field(default_factory="):-1] + "()"
    return src if len(src) <= limit else src[:limit - 1] + "…"


def field_rows(cls, text, comments, code):
    rows = []
    body = [n for n in cls.body if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)]
    for k, node in enumerate(body):
        name = node.target.id
        if name.startswith("_"):
            continue
        typ = ast.get_source_segment(text, node.annotation) or ""
        default = short(ast.get_source_segment(text, node.value)) if node.value is not None else "required"
        # the comment beside the field, plus comment lines that continue it (until the next code line)
        note = []
        for ln in range(node.lineno, node.end_lineno + 1):
            if ln in comments:
                note.append(comments[ln][1])
        ln = node.end_lineno + 1
        while ln in comments and ln not in code:
            col, c = comments[ln]
            if col <= node.col_offset and not note:       # a section comment, not a continuation
                break
            if col <= node.col_offset:                    # a new section heading for the next field
                break
            note.append(c)
            ln += 1
        rows.append((name, typ, default, " ".join(note) or fallback(cls.name, name, typ)))
    return rows


def init_rows(cls, text, comments):
    init = next((n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "__init__"), None)
    if init is None:
        return []
    a = init.args
    args = a.args[1:]
    defaults = [None] * (len(args) - len(a.defaults)) + list(a.defaults)
    rows = []
    for arg, d in list(zip(args, defaults)) + list(zip(a.kwonlyargs, a.kw_defaults)):
        typ = ast.get_source_segment(text, arg.annotation) if arg.annotation else ""
        default = short(ast.get_source_segment(text, d)) if d is not None else "required"
        note = comments.get(arg.lineno, (0, ""))[1] if arg.lineno != init.lineno else ""
        rows.append((arg.arg, typ or "", default, note or fallback(cls.name, arg.arg)))
    if a.vararg:
        rows.insert(0, ("*" + a.vararg.arg, "", "", ""))
    return rows


def table(rows):
    if not rows:
        return ""
    out = ["| Option | Type | Default | What it does |", "|---|---|---|---|"]
    for name, typ, default, note in rows:
        t = f"`{esc(typ)}`" if typ else ""
        d = f"`{esc(default)}`" if default not in ("required", "") else default
        out.append(f"| `{name}` | {t} | {d} | {esc(note)} |")
    return "\n".join(out) + "\n"


def main():
    index = {}
    for path in sorted(SRC.glob("*.py")):
        text = path.read_text()
        tree = ast.parse(text)
        comments, code = comments_by_line(text), code_lines(text)
        for node in tree.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                index[node.name] = (path, text, node, comments, code)

    OUT.mkdir(parents=True, exist_ok=True)
    missing = []
    for slug, (title, intro, names) in PAGES.items():
        md = [f"# {title}\n", f"{intro}\n",
              "!!! note \"Generated page\"\n    This page is built from the source by `tools/gen_reference.py`. "
              "Edit the comments in the code, not this file.\n"]
        for name in names:
            if name not in index:
                missing.append(name)
                continue
            path, text, node, comments, code = index[name]
            md.append(f"## {name}\n")
            md.append(f"`from iroshine import {name}` · defined in `iroshine/{path.name}`\n")
            doc = ast.get_docstring(node)
            if doc:
                md.append(doc.strip() + "\n")
            if isinstance(node, ast.ClassDef):
                is_dc = any("dataclass" in ast.unparse(d) for d in node.decorator_list)
                rows = field_rows(node, text, comments, code) if is_dc else init_rows(node, text, comments)
                md.append(table(rows))
                if not is_dc:                         # an ordinary class: its public methods too
                    meths = [m for m in node.body if isinstance(m, ast.FunctionDef)
                             and not m.name.startswith("_") and ast.get_docstring(m)]
                    if meths:
                        md.append("### Methods\n")
                    for m in meths:
                        sig = ast.unparse(m.args)
                        sig = sig[6:] if sig.startswith("self, ") else ("" if sig == "self" else sig)
                        md.append(f"#### `{m.name}({sig})`\n")
                        md.append(ast.get_docstring(m).strip() + "\n")
            else:
                md.append("```python\n" + f"{name}({ast.unparse(node.args)})" + "\n```\n")
        (OUT / f"{slug}.md").write_text("\n".join(md))
    listing = ["# Reference\n", "Every object you can import from `iroshine`, with every option it takes.\n",
               "| Page | Objects |", "|---|---|"]
    for slug, (title, intro, names) in PAGES.items():
        listing.append(f"| [{title}]({slug}.md) | " + ", ".join(f"`{n}`" for n in names) + " |")
    (OUT / "index.md").write_text("\n".join(listing) + "\n")
    if missing:
        print("not found in source:", missing, file=sys.stderr)
    documented = {n for _, _, ns in PAGES.values() for n in ns}
    import re
    exported = set(re.findall(r'"(\w+)"', (SRC / "__init__.py").read_text().split("__all__")[1]))
    left = sorted(exported - documented)
    if left:
        print("exported but not on any reference page:", left, file=sys.stderr)


if __name__ == "__main__":
    main()
