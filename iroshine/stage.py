"""
iroshine.stage — the Stage collects your objects and styles, runs your
solution under the tracker, and renders the recorded events with Manim.

    stage = Stage(resolution=(3840, 2160), grain=Grain(8))
    stage.add(BarList("nums", ...), CodePanel(...))
    stage.motion(swap=Motion(path="straight", easing="ease_in_out_cubic"))
    stage.run(Solution().sortArray, nums)
    stage.render("out.mp4")          # or stage.preview()
"""

import contextlib
import copy
import dataclasses
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, List, Optional

import numpy as np
from manim import (MoveToTarget, 
    Animation,
    rate_functions,
    DOWN, LEFT, PI, RIGHT, TAU, UP, Dot, FadeIn, FadeOut, GrowFromEdge, LaggedStart,
    ManimColor, Mobject, ReplacementTransform, interpolate_color, Scene, Text, TracedPath, VGroup,
    tempconfig, there_and_back,
)

from .barlist import BarList
from .components import Caption, CodePanel, Pack, Pointer, Readout, Region, Tower
from .grid import GridBoxes, GridView, Stamp
from .graph import GraphView
from .geometry import PointSet, PointStrip, Polyline
from .story import Beats
from .text import LineComposer, WordStrip
from .sound import Synth
from .style import DEFAULT_MOTION, Finale, Grain, Motion, Sound, Timing
from .tracking import record


@dataclass
class HookContext:
    """What a custom animation hook receives."""
    scene: Scene                # the Manim scene (add things, use self.camera, ...)
    event: dict                 # the raw event: type, list, index, value, src, line...
    view: BarList               # the BarList this event happens in
    bar: Any                    # the bar mobject involved (new bar for push/set, leaving bar for pop)
    source: Any                 # where the value came from (a bar mobject) or None
    motion: Motion              # the resolved Motion for this event
    default: Callable[[], List]  # call to get the built-in animations


class Stage:
    def __init__(self, background="#000000", resolution=(3840, 2160), fps=60,   # background: a color, [top, ..., bottom], or a Gradient
                 sound: Optional[Sound] = None, timing: Optional[Timing] = None,
                 finale: Optional[Finale] = None, caption: Optional[Caption] = None,
                 grain: Optional[Grain] = None, crf: int = 14):
        self.background, self.resolution, self.fps = background, resolution, fps
        self.crf = crf                      # video quality: lower = better / bigger (12–18 is visually lossless)
        self.grain = grain
        self.views, self.components, self.extras, self.widgets = {}, [], [], []
        self.grids = {}
        self.gridboxes, self.stamps, self.graphs, self.pointsets, self.polylines = [], [], [], [], []
        self._backdrop = []
        self.handlers = []
        self.observers = []                 # see every event without consuming it (e.g. Beats)
        self.motions = copy.deepcopy(DEFAULT_MOTION)
        self.hooks = {}
        self.sound_cfg = sound if sound is not None else Sound()
        self.timing = timing or Timing()
        self.finale = finale if finale is not None else Finale()
        self.caption = caption
        self.events = None

    # ───────────────────────────────────────────────────── composing ──
    def add(self, *items):
        """Put things on the stage: views (BarList, GridView, ...), components (CodePanel, Readout, ...),
        or any plain Manim mobject (titles, shapes). Returns the stage, so calls can be chained."""
        for it in items:
            if isinstance(it, BarList):
                self.views[it.name] = it
            elif isinstance(it, Caption):
                self.caption = it
            elif isinstance(it, CodePanel):
                self.components.append(it)
            elif isinstance(it, (Pointer, Readout, Region, Pack, Tower)):
                self.widgets.append(it)
            elif isinstance(it, GridView):
                self.grids[it.name] = it
            elif isinstance(it, GridBoxes):
                self.gridboxes.append(it)
            elif isinstance(it, Stamp):
                self.stamps.append(it)
            elif isinstance(it, GraphView):
                self.graphs.append(it)
            elif isinstance(it, PointSet):
                self.pointsets.append(it)
            elif isinstance(it, Polyline):
                self.polylines.append(it)
            elif isinstance(it, (Beats, PointStrip)):
                self.observers.append(it)
            elif isinstance(it, (WordStrip, LineComposer)):
                self.handlers.append(it)                  # views that handle their own events
            elif hasattr(it, "wants") and hasattr(it, "handle"):
                self.handlers.append(it)                  # any view that handles its own events (e.g. WallToWall)
            elif isinstance(it, Mobject):
                self.extras.append(it)          # plain Manim: titles, arrows, LaTeX, anything
            else:
                raise TypeError(f"don't know how to add {it!r}")
        return self

    def motion(self, **per_event: Motion):
        """Override how events animate: stage.motion(swap=Motion(path='arc'), pop=Motion(exit='shrink'))."""
        blank = Motion()
        for kind, m in per_event.items():
            base = self.motions.setdefault(kind, Motion())
            for f in dataclasses.fields(Motion):
                v = getattr(m, f.name)
                if v != getattr(blank, f.name):
                    setattr(base, f.name, v)
        return self

    def sound(self, cfg: Sound):
        self.sound_cfg = cfg
        return self

    def on(self, event, target=None):
        """Decorator: replace the animation for an event (optionally only for one list)."""
        def deco(fn):
            self.hooks[(event, target)] = fn
            return fn
        return deco

    # ───────────────────────────────────────────────────── running ──
    def run(self, method, *args, watch=()):
        """Run your solution under the tracker. Variables used by Pointer / Readout / Region
        are watched automatically; pass extra names in `watch` to see them as "var" events."""
        names = set(watch)
        for w in self.widgets:
            names.add(w.when if isinstance(w, Region) else w.region.when if isinstance(w, Pack) else w.var)
        names.update(st.when for st in self.stamps)
        names.update(g.done_when for g in self.graphs if g.done_when)
        names.update(p.probe for p in self.polylines if p.probe)
        names.update(p.focus for p in self.pointsets if p.focus)
        for h in self.handlers:
            names.update(getattr(h, "watch", lambda: [])())
        events, self.source, self.result = record(method, *args, watch=sorted(names),
                                                  grids=[g for g in self.grids if not getattr(self.grids[g], 'like', None)])
        self.events = _coalesce_swaps(events)
        self.title = getattr(method, "__name__", "solution")
        return self.result

    def render(self, out="iroshine.mp4", quality="high", preview=False):
        """quality: "high" = your resolution/fps · "medium" = 1080p30 · "low" = 480p15 draft."""
        if self.events is None:
            raise RuntimeError("call stage.run(solution, *inputs) before render()")
        w, h = self.resolution
        fps = self.fps
        if quality in ("low", "medium"):              # scale the short side to 480 / 1080, keep the shape
            short = 480 if quality == "low" else 1080
            k = short / min(w, h)
            w, h = int(round(w * k / 2)) * 2, int(round(h * k / 2)) * 2
            fps = 15 if quality == "low" else 30
        media = Path(tempfile.mkdtemp(prefix="iroshine_"))
        settings = {
            "pixel_width": w, "pixel_height": h, "frame_rate": fps,
            "frame_height": 8.0, "frame_width": 8.0 * w / h,
            "background_color": ManimColor(self.background if isinstance(self.background, str)
                                           else _sky_colors(self.background)[0]),
            "media_dir": str(media), "output_file": Path(out).stem,
            "disable_caching": True, "verbosity": "WARNING", "progress_bar": "none",
            "preview": False,
        }
        with tempconfig(settings), _encoder_quality(self.crf if quality != "low" else 23):
            scene = _StageScene(self)
            scene.render()
            produced = Path(scene.renderer.file_writer.movie_file_path)
        if self.grain and self.grain.amount > 0 and quality != "low":
            _add_grain(produced, out, self.grain, self.crf)
        else:
            shutil.copy(produced, out)
        if preview:
            _open(out)
        return out

    def preview(self, out="iroshine_preview.mp4"):
        """Fast low-res render that opens in your video player when it's done."""
        return self.render(out, quality="low", preview=True)


# ═══════════════════════════════════════════════════════════ encoding ══
@contextlib.contextmanager
def _encoder_quality(crf, preset="medium"):
    """Manim encodes at crf 23, which smears flat colors on a 4K screen. Raise the quality."""
    import av
    real_open = av.open

    class _Container:
        def __init__(self, c): self._c = c
        def __getattr__(self, k): return getattr(self._c, k)
        def __enter__(self): self._c.__enter__(); return self
        def __exit__(self, *a): return self._c.__exit__(*a)
        def add_stream(self, codec=None, *a, **k):
            if codec == "libx264":
                opts = dict(k.get("options") or {})
                opts.update({"crf": str(crf), "preset": preset})
                k["options"] = opts
            return self._c.add_stream(codec, *a, **k)

    def patched(*a, **k):
        c = real_open(*a, **k)
        mode = k.get("mode", a[1] if len(a) > 1 else "r")
        return _Container(c) if mode == "w" else c

    av.open = patched
    try:
        yield
    finally:
        av.open = real_open


def _add_grain(src, out, g: Grain, crf):
    if not shutil.which("ffmpeg"):
        print("iroshine: grain needs the ffmpeg command-line tool; skipping it")
        shutil.copy(src, out); return
    flags = "t+u" if g.animated else "u"
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(src),
           "-vf", f"noise=c0s={g.amount:g}:c0f={flags}",
           "-c:v", "libx264", "-crf", str(max(crf + 6, 20)), "-preset", "medium", "-pix_fmt", "yuv420p",
           "-c:a", "copy", str(out)]
    subprocess.run(cmd, check=True)


def _open(path):
    import os, platform
    try:
        if platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        elif platform.system() == "Windows":
            os.startfile(path)   # noqa
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        pass


MERGEABLE = {"box", "mvar"}     # batch keys whose later events simply supersede earlier ones


def _sky_colors(bg):
    """A background given as [top, ..., bottom] or as a Gradient (0 = top, 1 = bottom)."""
    from .gradient import Gradient
    if isinstance(bg, Gradient):
        return bg.sample(48)
    return [ManimColor(c) for c in bg]


def _coalesce_swaps(events):
    """`a[i], a[j] = a[j], a[i]` records as two sets; merge them into one "swap" event."""
    out, k = [], 0
    while k < len(events):
        e = events[k]
        if e["type"] == "set" and k + 1 < len(events):
            f = events[k + 1]
            s1, s2 = e.get("src"), f.get("src")
            if (f["type"] == "set" and f["list"] == e["list"] and s1 and s2
                    and not s1.get("popped") and not s2.get("popped")
                    and s1["list"] == e["list"] == s2["list"]
                    and s1["index"] == f["index"] and s2["index"] == e["index"]):
                out.append({"type": "swap", "list": e["list"], "i": e["index"], "j": f["index"],
                            "vi": f["value"], "vj": e["value"], "line": e["line"]})
                k += 2
                continue
        out.append(e)
        k += 1
    return out


# ═══════════════════════════════════════════════════════════════ scene ══
class _StageScene(Scene):
    def __init__(self, stage: Stage, **kw):
        super().__init__(**kw)
        self.S = stage
        self._companions = []

    def play(self, *anims, **kw):
        """Views that follow along (observers) can queue animations to run with the next move."""
        if self._companions:
            anims, self._companions = anims + tuple(self._companions), []
        super().play(*anims, **kw)

    # ─────────────────────────────────────────────────────── helpers ──
    def dur(self, kind):
        return (self.S.motions[kind].duration or 0.5) / self.S.timing.speed

    def note(self, value=None, deg=None, shift=0, instrument=None, offset=0.0, gain=0.0, cents=0, variant=0):
        if not self.synth:
            return
        d = self.synth.degree(value) if deg is None else deg
        cfg = self.S.sound_cfg
        if deg is None and value is not None and self.synth.values:
            vals = self.synth.values
            r = vals.index(value) / max(1, len(vals) - 1) if value in vals else 0.5
            if cfg.pitch_by_size == "down":            # the bigger the thing, the lower it sounds
                d = self.synth.degree(vals[-1]) - d
            gain += cfg.size_gain * (2 * r - 1)          # …and the louder
        inst = instrument or cfg.instrument
        self.add_sound(self.synth.note(inst, d + shift, cents, variant), time_offset=max(0.0, offset),
                       gain=self.synth.gain_db(gain))

    def view(self, name):
        return self.S.views.get(name)

    def mk(self, v, i, val, color=None, origin=None):
        """Make a bar for view v. Index views draw the element their value points at."""
        if v.indexes:
            ref = self.bars.get(v.indexes, [])
            src = ref[val] if isinstance(val, int) and 0 <= val < len(ref) and ref[val] is not None else None
            shown = src.value if src is not None else 0
            bar = v.make_bar(i, shown, color=color or (src.hue if src is not None else None),
                             origin=origin)
            bar.value, bar.shown, bar.ref = val, shown, src
            if v.index_labels and v.labels.values and len(bar) > 1:     # show what the stack really holds
                from manim import Text
                old = bar[1]
                lab = Text(str(val), font=v.labels.font, font_size=v.labels.font_size,
                           color=ManimColor(v.labels.color))
                lab.next_to(bar[0], UP, buff=0.08)
                bar.remove(old); bar.add(lab)
            return bar
        bar = v.make_bar(i, val, color=color, origin=origin)
        bar.shown = val
        return bar

    def source_of(self, o):
        if not o or o["list"] not in self.S.views:
            return None
        if o.get("popped"):
            return self.ghosts.get((o["list"], o["index"]))
        bars = self.bars[o["list"]]
        return bars[o["index"]] if o["index"] < len(bars) else None

    def grow_edge(self, v):
        return DOWN if v.orientation == "up" else LEFT

    def tip(self, bar, v):
        body = bar[0]
        return body.get_top() + 0.08 * UP if v.orientation == "up" else body.get_right() + 0.08 * RIGHT

    def bend(self, m, forward=True):
        b = {"straight": 0, "hop": PI * 0.95}.get(m.path, m.arc)
        return -b if forward else b

    def pulse(self, bar, color):
        return bar[0].animate(rate_func=there_and_back).set_fill(ManimColor(color))

    def sparkle(self, point, color, n=7, reach=0.38):
        dots = VGroup(*[Dot(point, radius=0.035, color=ManimColor(color)) for _ in range(n)])
        self.add(dots)
        anims = [d.animate.shift(reach * np.array([np.cos(k / n * TAU + .3), np.sin(k / n * TAU + .3), 0])
                                 + 0.1 * UP).set_opacity(0)
                 for k, d in enumerate(dots)]
        return anims, dots

    def fly(self, src, dest, m):
        """Move a copy of `src` into `dest` (dest isn't on screen yet). Returns (anims, cleanup)."""
        mover = src.copy()
        if m.color:
            mover[0].set_fill(ManimColor(m.color))
        if len(mover) > 1 and len(dest) > 1 and not mover[1].family_members_with_points() \
                and dest[1].family_members_with_points():
            # the source has no label but the destination does (e.g. a stack showing indices): start the
            # label invisible at the source instead of growing it out of a stray point
            ghost = dest[1].copy().set_opacity(0).next_to(mover[0], UP, buff=0.08)
            mover.remove(mover[1]); mover.add(ghost)
        self.add(mover)
        forward = dest.get_x() >= mover.get_x()
        anims = [ReplacementTransform(mover, dest, path_arc=self.bend(m, forward), rate_func=m.rate())]
        cleanup = []
        if m.trail:
            trail = TracedPath(mover.get_center, stroke_color=ManimColor(m.color or dest.hue),
                               stroke_width=4, dissipating_time=0.45)
            self.add(trail); cleanup.append(trail)
        if m.color and any(src is b for bars in self.bars.values() for b in bars):
            anims.append(self.pulse(src, m.color))
        return anims, cleanup

    def land(self, bar, v, m):
        anims, extra = [], []
        if m.sparkle:
            sp, dots = self.sparkle(self.tip(bar, v), m.color or bar.hue); anims += sp; extra.append(dots)
        if m.squash:
            anims.append(bar.animate(rate_func=there_and_back).stretch(
                0.86, 1 if v.orientation == "up" else 0, about_edge=DOWN if v.orientation == "up" else LEFT))
        if anims:
            self.play(*anims, run_time=0.35 / self.S.timing.speed)
            self.remove(*extra)

    def hooked(self, kind, e, v, bar, source, default):
        fn = self.S.hooks.get((kind, e.get("list"))) or self.S.hooks.get((kind, None))
        if fn is None:
            return default()
        ctx = HookContext(self, e, v, bar, source, self.S.motions[kind], default)
        out = fn(ctx)
        return default() if out is None else list(out)

    def narrate(self, e):
        cap = self.S.caption
        if not cap:
            return
        on = lambda o: "?" if not o else (f"{o['list']}.pop()" if o.get("popped") else f"{o['list']}[{o['index']}]")
        fmt = lambda xs: "[" + ", ".join(map(str, xs)) + "]"
        text = {
            "create":  lambda: f"{e['list']} = {fmt(e['values'])}",
            "read":    lambda: f"read {e['list']}[{e['index']}] → {e['value']}",
            "compare": lambda: f"{on(e['a'])} {e['op']} {on(e['b'])}   {e['av']} {e['op']} {e['bv']}",
            "push":    lambda: f"{e['list']}.append({e['value']})",
            "pop":     lambda: f"{e['list']}.pop() → {e['value']}",
            "set":     lambda: f"{e['list']}[{e['index']}] = {e['value']}",
            "swap":    lambda: f"swap {e['list']}[{e['i']}] ↔ {e['list']}[{e['j']}]",
            "replace": lambda: f"{e['list']} → {fmt(e['values'])}",
            "var":     lambda: f"{e['name']} = {e['value']}",
            "done":    lambda: f"return {fmt(e['value']) if isinstance(e['value'], list) else e['value']}",
        }[e["type"]]()
        cap.show(self, text)

    def code_to(self, line):
        out = []
        for c in self.S.components:
            if isinstance(c, CodePanel):
                out += c.goto(line)
        return out

    # ─────────────────────────────────────────────────────── construct ──
    def construct(self):
        S = self.S
        seen, maxlen, length, allv = {}, {}, {}, []
        for e in S.events:
            n, t = e.get("list"), e["type"]
            vals = e.get("values") if t in ("create", "replace") else [e["value"]] if t in ("push", "set") else []
            if t in ("create", "replace"):
                length[n] = len(vals)
            elif t == "push":
                length[n] = length.get(n, 0) + 1
            elif t == "pop":
                length[n] -= 1
            if n:
                seen.setdefault(n, []).extend(vals); allv += vals
                maxlen[n] = max(maxlen.get(n, 0), length.get(n, 0))
        for name, v in S.views.items():
            v.prepare(seen.get(v.indexes or name, []), maxlen.get(name, 1))
        missing = sorted(set(seen) - set(S.views))
        if missing:
            print(f"iroshine: not drawing {missing} (declare a BarList with that name to show it)")

        self.synth = Synth(S.sound_cfg, allv, Path(tempfile.gettempdir()) / "iroshine_notes") \
            if S.sound_cfg and S.sound_cfg.enabled else None
        self.bars = {n: [] for n in seen}
        self._set_ranks, self._last_set = {}, {}
        for gname in S.grids:                          # every value a grid cell is ever set to, and its last change
            sets = [ev for ev in S.events if ev["type"] == "set" and ev.get("list") == gname and "row" in ev]
            self._set_ranks[gname] = sorted({ev["value"] for ev in sets
                                             if isinstance(ev["value"], (int, float))})
            if sets:
                self._last_set[gname] = sets[-1]
        import random as _random
        self._hum = _random.Random(11)
        self.ghosts, self.shown, self.statics = {}, set(), {}
        for n, v in S.views.items():
            self.statics[n] = v.build_static()
        if not isinstance(S.background, str):          # a list of colors = a top→bottom gradient
            from manim import Rectangle, config
            sky = Rectangle(width=config.frame_width + 0.1, height=config.frame_height + 0.1)
            sky.set_fill(list(reversed(_sky_colors(S.background))), opacity=1).set_stroke(width=0)
            sky.set_sheen_direction(UP)
            self.add(sky)
            S._backdrop = [sky]
        for m in S.extras:
            self.add(m)
        for c in S.components:
            self.add(*c.build(S.source))
        self.regions_drawn = []
        for w in S.widgets:
            if isinstance(w, Pointer) and w.on in S.views:
                w.build(S.views[w.on]).set_opacity(0); self.add(w.mob)
            elif isinstance(w, Readout):
                w.build(); w.mob.set_opacity(0)              # added on its first value (the number redraws itself)
            elif isinstance(w, Pack):
                self.plan_pack(w)
        self.mirror = {}
        self.batchers = list(S.grids.values()) + list(S.gridboxes) + list(S.graphs)
        graph_intro = []
        for g in S.graphs:
            self.add(g.plan(self, S.events))
        for pl in S.polylines:
            pl.setup(self)
        for h in S.handlers:
            if hasattr(h, "plan"):
                self.add(h.plan(self, S.events))

        # opening: inputs appear, bars rise with a soft arpeggio
        i, intro, grow, t = 0, [], [], 0.0
        while i < len(S.events) and S.events[i]["type"] == "create" and S.events[i]["role"] == "input":
            e = S.events[i]; i += 1
            g = S.grids.get(e["list"])
            if g is not None and e.get("grid") is not None:
                mob = g.build(e["grid"])
                intro.append(LaggedStart(*[FadeIn(m, scale=0.9) for m in mob], lag_ratio=0.004))
                for cv in S.grids.values():                   # blank canvases shaped like this grid
                    if cv.like == g.name:
                        cm = cv.build([[None] * g.C for _ in range(g.R)])
                        intro.append(LaggedStart(*[FadeIn(m) for m in cm], lag_ratio=0.004))
                continue
            hand = [a for h in S.handlers for a in h.intro(self, e)]
            if hand:
                intro += hand
                continue
            ps = next((p for p in S.pointsets if p.name == e["list"]), None)
            if ps is not None:
                dots = ps.build(e["values"])
                if ps.grid_mob is not None:
                    self.add(ps.grid_mob)
                    for m in S._backdrop:
                        self.bring_to_back(m)
                self.add(ps.ring)
                if S.timing.intro == "instant":
                    self.add(dots)
                else:
                    intro.append(LaggedStart(*[FadeIn(d, scale=0.2) for d in dots], lag_ratio=0.06))
                continue
            v = self.view(e["list"])
            if not v:
                continue
            self.shown.add(e["list"])
            if S.timing.intro == "instant":                  # the first frame already shows the input
                self.add(self.statics[e["list"]])
                for k, val in enumerate(e["values"]):
                    b = self.mk(v, k, val); self.bars[e["list"]].append(b); self.add(b)
                continue
            intro.append(FadeIn(self.statics[e["list"]]))
            for k, val in enumerate(e["values"]):
                b = self.mk(v, k, val); self.bars[e["list"]].append(b)
                grow.append(GrowFromEdge(b, self.grow_edge(v), rate_func=S.motions["create"].rate()))
                self.note(val, offset=0.7 + t, gain=-7); t += 0.05
        for g in S.graphs:
            intro += g.intro()
        if intro and S.timing.intro == "instant":           # jump straight to the end of the intro
            from manim.animation.animation import prepare_animation
            for a in intro:
                a = prepare_animation(a)                    # `.animate` builders become animations
                a._setup_scene(self)
                a.begin()
                a.finish()
                a.clean_up_from_scene(self)
        elif intro:
            self.play(*intro, run_time=1.2 if S.grids or S.pointsets else 0.7)
        if grow:
            self.play(LaggedStart(*grow, lag_ratio=0.06), run_time=max(1.0, t + 0.5))
        for pl in S.polylines:
            pl.show_ghost(self)
        for ob in S.observers:
            ob.setup(self)
            ob.start(self, instant=S.timing.intro == "instant")
        if S.timing.loop:                                  # remember the opening frame, to return to it
            self._opening = [(m, m.copy()) for m in self.mobjects]

        self._grid_trash, self._note_count = [], {}
        evs, k = S.events, i
        self._mirror_upto = -1
        self.mirror_to(i - 1)
        while k < len(evs):
            e = evs[k]
            self.mirror_to(k)
            for ob in S.observers:
                ob.observe(self, e)
            for c in S.components:                         # gliding code highlights follow every event
                if isinstance(c, CodePanel) and c.glide and e.get("line"):
                    c.target(e["line"])
            if self.is_noop(e):
                k += 1; continue
            pl = self.polyline_for(e) or next((h for h in S.handlers if h.wants(e)), None)
            if pl is not None:
                pl.handle(self, e)
                k += 1; continue
            if any(g.forgets(e) for g in S.grids.values()):
                parts = [p for g in S.grids.values() if g.forgets(e) for p in g.forget(self)]
                if parts:
                    self.play(*parts, run_time=0.6 / S.timing.speed)
                k += 1; continue
            if self.batchable(e):
                batch, keys = [], set()
                while k < len(evs) and len(batch) < 400:
                    e2 = evs[k]
                    self.mirror_to(k)
                    if self.is_noop(e2):
                        k += 1; continue
                    if not self.batchable(e2) or any(g.forgets(e2) for g in S.grids.values()):
                        break
                    key = self.batch_key(e2)
                    if key in keys:
                        if key[0] in MERGEABLE:              # e.g. a box resized again: keep only the latest
                            batch = [b for b in batch if self.batch_key(b) != key]
                        else:
                            break
                    keys.add(key); batch.append(e2); k += 1
                for c in S.components:                     # opt-in: the highlight follows the cell changes
                    if isinstance(c, CodePanel) and c.glide and c.follow_batches:
                        sets = [b for b in batch if b["type"] == "set" and b.get("line")]
                        if sets:
                            c.target(sets[-1]["line"])
                self.play_batch(batch)
                continue
            k += 1
            if e["type"] in S.timing.skip and e["type"] in ("read", "compare"):
                continue
            self.narrate(e)
            getattr(self, "on_" + e["type"])(e)
            if S.timing.pause_between:
                self.wait(S.timing.pause_between)
        self.wait(S.timing.end_hold)
        self._trim_audio()

    def _trim_audio(self, fade_ms=250):
        """Cut the sound at the last frame. Note tails (reverb) would otherwise run past the picture,
        leaving seconds of frozen video at the end, which also breaks loops."""
        fw = self.renderer.file_writer
        seg = getattr(fw, "audio_segment", None)
        if seg is None:
            return
        end_ms = int(self.renderer.time * 1000)
        if len(seg) > end_ms:
            fw.audio_segment = seg[:end_ms].fade_out(min(fade_ms, end_ms))

    # ─────────────────────────────────────────────────────── events ──
    def on_create(self, e):
        name, v = e["list"], self.view(e["list"])
        if not v:
            self.bars[name] = [None] * len(e["values"]); return
        anims = self.code_to(e["line"])
        if name not in self.shown:
            anims.append(FadeIn(self.statics[name])); self.shown.add(name)
        for b in self.bars[name]:
            if b is not None:
                self.remove(b)
        self.bars[name] = []
        if anims:
            self.play(*anims, run_time=0.4)
        if not e["values"]:
            return
        pm = self.S.motions["push"]
        moves, cleanup, t = [], [], 0.0
        for k, (val, o) in enumerate(zip(e["values"], e["origins"])):
            src = self.source_of(o)
            dest = self.mk(v, k, val, origin=getattr(src, "origin", None))
            self.bars[name].append(dest)
            if src is not None:
                a, c = self.fly(src, dest, pm); moves.append(a[0]); cleanup += c
                self.note(val, offset=t, gain=-2)
                self.note(val, shift=self.S.sound_cfg.landing_interval, offset=t + self.dur("push") * 0.85, gain=-4)
            else:
                moves.append(GrowFromEdge(dest, self.grow_edge(v), rate_func=pm.rate()))
                self.note(val, offset=t, gain=-5)
            t += self.dur("push") * pm.lag
        self.play(LaggedStart(*moves, lag_ratio=pm.lag), run_time=self.dur("push") + t)
        self.remove(*cleanup)

    def on_read(self, e):
        v, m = self.view(e["list"]), self.S.motions["read"]
        bars = self.bars.get(e["list"], [])
        if not v or e["index"] >= len(bars) or bars[e["index"]] is None:
            return
        b = bars[e["index"]]
        default = lambda: [] if m.style == "none" else [self.pulse(b, m.color or b.hue)]
        anims = self.hooked("read", e, v, b, None, default)
        if self.synth and self.S.sound_cfg.tick_reads:
            self.note(e["value"], shift=len(self.synth.steps), instrument="tick", gain=-10)
        self.play(*self.code_to(e["line"]), *anims, run_time=self.dur("read"))

    def on_compare(self, e):
        m = self.S.motions["compare"]
        live = {id(b) for bs in self.bars.values() for b in bs if b is not None}
        pair = [p for p in (self.source_of(o) for o in (e["a"], e["b"]))     # only bars on screen (not ghosts
                if p is not None and id(p) in live]                           # of popped values)
        v = self.view((e["a"] or {}).get("list")) or self.view((e["b"] or {}).get("list"))
        default = lambda: [] if m.style == "none" else [self.pulse(p, m.color or p.hue) for p in pair]
        anims = self.hooked("compare", e, v, pair[0] if pair else None,
                            pair[1] if len(pair) > 1 else None, default)
        if self.synth and self.S.sound_cfg.compare_notes:
            self.note(e["av"], instrument="soft_sine", gain=-12)
        code = self.code_to(e["line"])
        if anims or code:
            self.play(*code, *anims, run_time=self.dur("compare"))

    def on_swap(self, e):
        name, v, m = e["list"], self.view(e["list"]), self.S.motions["swap"]
        bars = self.bars.get(name, [])
        i, j = e["i"], e["j"]
        if not v or i == j or max(i, j) >= len(bars):
            return
        bi, bj = bars[i], bars[j]
        ti = self.mk(v, j, bi.value, origin=bi.origin)          # bi's element lands in slot j
        tj = self.mk(v, i, bj.value, origin=bj.origin)
        cleanup = []

        def default():
            fwd = j > i
            out = [ReplacementTransform(bi, ti, path_arc=self.bend(m, fwd), rate_func=m.rate()),
                   ReplacementTransform(bj, tj, path_arc=self.bend(m, fwd), rate_func=m.rate())]
            if m.trail:
                for mob in (bi, bj):
                    tr = TracedPath(mob.get_center, stroke_color=ManimColor(m.color or mob.hue),
                                    stroke_width=4, dissipating_time=0.4)
                    self.add(tr); cleanup.append(tr)
            return out

        anims = self.hooked("swap", e, v, bi, bj, default)
        self.note(bi.value, gain=-3)
        self.note(bj.value, gain=-3)
        self.play(*self.code_to(e["line"]), *anims, run_time=self.dur("swap"))
        for mob in (ti, tj):
            if mob not in self.mobjects:
                self.add(mob)
        self.remove(*cleanup)
        bars[j], bars[i] = ti, tj

    def on_push(self, e):
        name, v, m = e["list"], self.view(e["list"]), self.S.motions["push"]
        if not v:
            self.bars.setdefault(name, []).insert(e["index"], None); return
        src = self.source_of(e.get("src"))
        dest = self.mk(v, e["index"], e["value"], origin=getattr(src, "origin", None))
        if src is None and v.indexes:
            src = dest.ref                          # an index flies in from the element it names
        cleanup = []

        def default():
            if src is not None:
                a, c = self.fly(src, dest, m); cleanup.extend(c); return a
            return [GrowFromEdge(dest, self.grow_edge(v), rate_func=m.rate())]

        anims = self.hooked("push", e, v, dest, src, default)
        self.note(dest.shown)
        if src is not None:
            self.note(dest.shown, shift=self.S.sound_cfg.landing_interval, offset=self.dur("push") * 0.85, gain=-3)
        self.play(*self.code_to(e["line"]), *anims, run_time=self.dur("push"))
        if dest not in self.mobjects:
            self.add(dest)
        self.remove(*cleanup)
        self.bars[name].insert(e["index"], dest)
        self.land(dest, v, m)

    def on_pop(self, e):
        name, v, m = e["list"], self.view(e["list"]), self.S.motions["pop"]
        bars = self.bars.get(name, [])
        b = bars.pop(e["index"]) if e["index"] < len(bars) else None
        if not v or b is None:
            return
        self.ghosts[(name, e["index"])] = b.copy()
        step = v.slot_offset(1, 0)
        shifts = [o.animate(rate_func=m.rate()).shift(step) for o in bars[e["index"]:] if o is not None]
        extra = []

        def default():
            r = m.rate()
            if m.exit == "shrink":
                return [b.animate(rate_func=r).scale(0.01)]
            if m.exit == "drop":
                return [b.animate(rate_func=r).shift(0.6 * DOWN).set_opacity(0)]
            if m.exit == "float_up_fade":
                return [b.animate(rate_func=r).shift(0.35 * UP).set_opacity(0)]
            if m.exit == "burst":
                sp, dots = self.sparkle(b.get_center(), m.color or b.hue, n=11, reach=0.6); extra.append(dots)
                return [b.animate(rate_func=r).scale(1.35).set_opacity(0), *sp]
            return [FadeOut(b, rate_func=r)]                                                   # "fade"

        anims = self.hooked("pop", e, v, b, None, default)
        self.note(e["value"], shift=-3, gain=-4)
        self.play(*self.code_to(e["line"]), *anims, *shifts, run_time=self.dur("pop"))
        # remove the bar and every part of it: an earlier animation (a compare flash, a landing
        # squash) can register a part on its own, and that part would otherwise stay on screen
        self.remove(b, *b.get_family(), *extra)

    def on_set(self, e):
        name, v, m = e["list"], self.view(e["list"]), self.S.motions["set"]
        bars = self.bars.get(name, [])
        if not v or e["index"] >= len(bars):
            return
        old = bars[e["index"]]
        src = self.source_of(e.get("src"))
        dest = self.mk(v, e["index"], e["value"], origin=getattr(src, "origin", None))
        parts = [self.source_of(o) for o in (e.get("parts") or [])]
        if src is None and parts and all(p is not None for p in parts) and v.orientation == "up":
            self.combine(e, v, old, dest, parts)
            bars[e["index"]] = dest
            return
        self.note(e["value"])
        if src is not None and src is not old:
            a, cleanup = self.fly(src, dest, m)
            self.play(*self.code_to(e["line"]), *a, FadeOut(old), run_time=self.dur("set"))
            self.remove(old, *cleanup)
        else:
            self.play(*self.code_to(e["line"]), ReplacementTransform(old, dest, rate_func=m.rate()),
                      run_time=self.dur("set"))
        bars[e["index"]] = dest

    def combine(self, e, v, old, dest, parts):
        """a[i] = a[j] + a[k]: copies of the parts fly over and stack into the new bar."""
        from manim import Rectangle
        m = self.S.motions.get("combine") or self.S.motions["set"]
        x = dest[0][-1].get_x()
        w = dest[0][-1].width
        y, flights, blocks = v.base, [], []
        for k, p in enumerate(parts):
            h = v.value_pos(p.shown if hasattr(p, "shown") else p.value) - v.base
            h = max(h, 0.02)
            block = Rectangle(width=w, height=h).move_to([x, y + h / 2, 0])
            block.set_fill(p.hue, opacity=1).set_stroke(ManimColor(self.S.background) if isinstance(
                self.S.background, str) else ManimColor("#000000"), width=2)
            mover = p[0][-1].copy()
            self.add(mover)
            flights.append(ReplacementTransform(mover, block, path_arc=-0.9 if k % 2 == 0 else 0.9,
                                                rate_func=m.rate()))
            flights.append(p[0].animate(rate_func=there_and_back).set_opacity(0.45))
            self.note(p.value, offset=k * 0.12, gain=-3)
            blocks.append(block)
            y += h
        # small sums go by quickly, big ones take their time: the tempo follows the growth
        frac = min(1.0, (y - v.base) / max(1e-6, v.size[1]) * 2.5)
        pace = 0.45 + 0.55 * frac
        self.play(*self.code_to(e["line"]), LaggedStart(*flights, lag_ratio=0.15),
                  run_time=(m.duration or 0.7) * pace / self.S.timing.speed)
        self.note(e["value"], instrument=self.S.sound_cfg.finale_instrument, gain=-4)
        stack = VGroup(*blocks)
        self.play(FadeOut(old), ReplacementTransform(stack, dest, rate_func=rate_functions.ease_in_out_cubic),
                  run_time=0.4 * (0.6 + 0.4 * frac) / self.S.timing.speed)

    def on_replace(self, e):
        name, v = e["list"], self.view(e["list"])
        if not v:
            self.bars[name] = [None] * len(e["values"]); return
        new = [self.mk(v, k, val) for k, val in enumerate(e["values"])]
        old = [b for b in self.bars[name] if b is not None]
        anims = [FadeOut(b) for b in old] + [GrowFromEdge(b, self.grow_edge(v)) for b in new]
        self.play(*self.code_to(e["line"]), *anims, run_time=self.dur("replace"))
        self.bars[name] = new

    def tower_step(self, tw, value, part):
        """Grow a Tower from its current total to `value`. Returns animations."""
        from manim import Rectangle
        from .gradient import Gradient
        v = self.S.views.get(tw.on)
        if v is None:
            return []
        old = getattr(tw, "total", None)
        tw.blocks = getattr(tw, "blocks", [])
        tw.total = value
        if old is None or value <= old:
            return []
        y0, y1 = v.value_pos(old), v.value_pos(value)
        block = Rectangle(width=tw.width, height=max(0.02, y1 - y0)).move_to([tw.x, (y0 + y1) / 2, 0])
        src = self.source_of(part) if part else None
        if src is None:
            col = ManimColor(tw.extra_fill or (tw.fill if isinstance(tw.fill, str) else "#ffffff"))
        elif isinstance(tw.fill, Gradient):
            col = tw.fill.at(len(tw.blocks) / 6)
        elif tw.fill is None:
            col = src.hue
        else:
            col = ManimColor(tw.fill)
        block.set_fill(col, opacity=1)
        block.set_stroke(ManimColor(tw.stroke) if tw.stroke else None, width=tw.stroke_width if tw.stroke else 0)
        tw.blocks.append(block)
        self.note(deg=2 + len(tw.blocks) * 2, instrument=self.S.sound_cfg.finale_instrument, gain=-3)
        extra = []
        if tw.labels and block.height > tw.label_size / 48 * 0.5:
            lbl = Text(f"{value - old:g}", font="IBM Plex Mono", font_size=tw.label_size,
                       color=ManimColor(tw.label_color)).move_to(block)
            tw.block_labels = getattr(tw, "block_labels", []) + [lbl]
            self.add_foreground_mobject(lbl)               # stays on top of the blocks, even when they pulse
            extra.append(FadeIn(lbl, rate_func=lambda a: rate_functions.smooth(max(0.0, (a - 0.65) / 0.35))))
        if src is not None:
            mover = src[0][-1].copy()
            self.add(mover)
            return [ReplacementTransform(mover, block, path_arc=-0.6, rate_func=rate_functions.ease_in_out_cubic),
                    src[0].animate(rate_func=there_and_back).set_opacity(0.4)] + extra
        self.add(block)
        return [GrowFromEdge(block, DOWN, rate_func=rate_functions.ease_out_cubic)] + extra

    def plan_pack(self, pk):
        """Find every piece this Pack's Region will draw, and solve the layout up front."""
        R = pk.region
        view = self.S.views.get(R.on)
        sizes = []
        for e in self.S.events:
            if e["type"] == "var" and e["name"] == R.when and view is not None:
                try:
                    x0, x1 = int(R.eval("x0", e["locals"])), int(R.eval("x1", e["locals"]))
                    y0, y1 = float(R.eval("y0", e["locals"])), float(R.eval("y1", e["locals"]))
                except Exception:
                    continue
                if x1 >= x0 and y1 > y0:
                    sizes.append((x1 - x0 + 1, round(y1 - y0)))
        pk.plan(sizes)
        pk.pieces = []
        g = pk.ghost()
        if g is not None:
            self.add(g)

    def pack_flight(self, pk, shape):
        """Animation: a copy of a new region piece flies to its slot in the Pack."""
        k = pk.count
        if k >= len(pk.sizes):
            return None
        pk.count += 1
        from manim import Rectangle, UpdateFromAlphaFunc
        center, W1, H1, rot = pk.target(k)
        src = shape[0]
        c0 = src.get_center(); W0, H0 = src.width, src.height
        color = pk.color(k)
        piece = Rectangle(width=W0, height=H0).move_to(c0)
        piece.set_fill(src.get_fill_color(), opacity=pk.opacity).set_stroke(width=0)
        self.add(piece)
        rate = getattr(rate_functions, pk.easing)
        start_color = src.get_fill_color()

        def step(mob, a):
            t = rate(a)
            w, h = W0 + (W1 - W0) * t, H0 + (H1 - H0) * t
            r = Rectangle(width=w, height=h)
            r.set_fill(interpolate_color(start_color, color, t), opacity=pk.opacity)
            if pk.stroke:
                r.set_stroke(ManimColor(pk.stroke), width=pk.stroke_width * t)
            else:
                r.set_stroke(width=0)
            if rot:
                r.rotate(PI / 2 * t)
            r.move_to(np.array(c0) + (np.array(center) - np.array(c0)) * t)
            mob.become(r)

        pk.pieces.append(piece)
        return UpdateFromAlphaFunc(piece, step, run_time=pk.duration / self.S.timing.speed)

    # ─────────────────────────────────────────── batching (grids etc.) ──
    def is_noop(self, e):
        """Events about things nothing on screen shows."""
        S, t = self.S, e["type"]
        if any(b.handles(e) for b in self.batchers) or self.forgets(e) or self.polyline_for(e) or \
                any(h.wants(e) for h in S.handlers):
            return False
        if t in ("screate", "sadd", "sremove", "sclear"):
            return True
        if t in ("read", "set", "push", "pop", "create", "replace", "swap"):
            n = e.get("list")
            return n not in S.views
        if t == "compare":
            names = {(o or {}).get("list") for o in (e.get("a"), e.get("b"))}
            return not (names & set(S.views))
        if t == "var":
            return not any(getattr(w, "var", None) == e["name"] or getattr(w, "when", None) == e["name"]
                           for w in S.widgets) and \
                not any(getattr(g, "done_when", None) == e["name"] for g in S.graphs) and \
                not any(st.when == e["name"] for st in S.stamps) and \
                not any(getattr(p, "probe", None) == e["name"] for p in S.polylines) and \
                not any(getattr(p, "focus", None) == e["name"] for p in S.pointsets)
        return False

    def forgets(self, e):
        return any(g.forgets(e) for g in self.S.grids.values())

    def batchable(self, e):
        if any(b.handles(e) for b in self.batchers):
            return True
        if e["type"] == "var" and self.batchers:
            ws = [w for w in self.S.widgets if getattr(w, "var", None) == e["name"]
                  or getattr(w, "when", None) == e["name"]]
            others = any(getattr(g, "done_when", None) == e["name"] for g in self.S.graphs) or \
                any(st.when == e["name"] for st in self.S.stamps) or \
                any(p.probe == e["name"] for p in self.S.polylines) or \
                any(p.focus == e["name"] for p in self.S.pointsets)
            return bool(ws) and not others and all(isinstance(w, Readout) for w in ws)
        return False

    def batch_key(self, e):
        for b in self.batchers:
            if b.handles(e):
                return b.key(e)
        if any(isinstance(w, Readout) and w.var == e["name"] and w.merge for w in self.S.widgets):
            return ("mvar", e["name"])
        return ("var", e["name"])

    def play_batch(self, batch):
        S = self.S
        g0 = next(iter(S.grids.values()), None)
        rate, step = (g0.rate, g0.step) if g0 else (30.0, 0.35)
        d = step / S.timing.speed
        dt = 1.0 / (rate * S.timing.speed)
        items, t = [], 0.0
        from manim import AnimationGroup
        for gname, last in self._last_set.items():         # a held breath before the last change
            g = S.grids[gname]
            if g.final_hold and any(e is last for e in batch):
                self.wait(g.final_hold)
        # grid_set_pitch="value": many cells turning at once share the loudness of one (equal-power sum)
        self._set_gain = 0.0
        if S.sound_cfg.grid_set_pitch in ("value", "rank"):
            import math
            n_sets = sum(1 for e in batch if e["type"] == "set")
            self._set_gain = -10 * math.log10(max(1, n_sets)) * 0.7
        for e in batch:
            parts, notes = [], []
            for b in self.batchers:
                if b.handles(e):
                    p, n = b.anim(self, e); parts += p; notes += n
            if e["type"] == "var":
                parts += self._readout_parts(e)
            if not parts and not notes:
                continue                             # nothing visible changed: don't spend time on it
            final = next((S.grids[g] for g, last in self._last_set.items() if e is last), None)
            for kind, val in notes:
                self._grid_note(kind, val, t, grid=e.get("list"), final=final)
            if e["type"] == "var" and self.synth:
                for w in S.widgets:
                    if isinstance(w, Readout) and w.var == e["name"] and w.sound and w.shown:
                        self.note(deg=w.sound_deg, instrument=w.sound, offset=t, gain=w.sound_gain)
            items.append(AnimationGroup(*parts) if parts else Animation(Mobject()))
            t += dt
        if not items:
            return
        if len(items) == 1:
            self.play(items[0], run_time=d)
        else:
            lag = dt / d
            self.play(LaggedStart(*items, lag_ratio=lag), run_time=d * (1 + lag * (len(items) - 1)))
        if self._grid_trash:
            self.remove(*self._grid_trash); self._grid_trash = []

    def mirror_to(self, k):
        while self._mirror_upto < k:
            self._mirror_upto += 1
            self.update_mirror(self.S.events[self._mirror_upto])

    def update_mirror(self, e):
        """Keep a plain copy of every list, so boxes and stamps can read current values."""
        t, n, M = e["type"], e.get("list"), self.mirror
        if n is None or "row" in e:
            return
        if t in ("create", "replace"):
            M[n] = list(e.get("values") or [])
        elif n in M:
            L = M[n]
            if t == "set" and e["index"] < len(L):
                L[e["index"]] = e["value"]
            elif t == "push":
                L.insert(e["index"], e["value"])
            elif t == "pop" and e["index"] < len(L):
                L.pop(e["index"])
            elif t == "swap":
                L[e["i"]], L[e["j"]] = L[e["j"]], L[e["i"]]

    def polyline_for(self, e):
        for p in self.S.polylines:
            if e.get("list") == p.name and e["type"] in ("push", "pop", "create", "replace"):
                return p
        for p in self.S.pointsets:
            if e.get("list") == p.name and e["type"] in ("create", "replace", "read"):
                return p
        return None

    def _readout_parts(self, e):
        from manim import UpdateFromAlphaFunc
        out = []
        for w in self.S.widgets:
            if isinstance(w, Readout) and w.var == e["name"] and isinstance(e["value"], (int, float)):
                if not w.shown:
                    w.tracker.set_value(e["value"]); w.mob.set_opacity(1); self.add(w.mob); w.shown = True
                    w.first_value, w.first_frame = e["value"], self.renderer.time < 0.5
                    continue
                old, new, tr = w.tracker.get_value(), e["value"], w.tracker
                out.append(UpdateFromAlphaFunc(Mobject(), lambda m, a, o=old, n=new, tr=tr:
                                               tr.set_value(o + (n - o) * rate_functions.ease_out_cubic(a))))
        return out

    def _grid_note(self, kind, val, offset, grid=None, final=None):
        if not self.synth:
            return
        cfg = self.S.sound_cfg
        if kind == "set" and cfg.grid_set_pitch == "rank" and grid in self._set_ranks:
            ranks = self._set_ranks[grid]
            deg = ranks.index(val) if val in ranks else 0
            h, cents, var, jit, dg = cfg.humanize, 0, 0, 0.0, 0.0
            if h:
                cents = round(self._hum.uniform(-12, 12) * h)
                var = self._hum.randrange(4)
                jit = self._hum.uniform(-0.008, 0.008) * h
                dg = self._hum.uniform(-2, 2) * h
            inst = (final.final_instrument if final is not None and final.final_instrument else
                    cfg.grid_instrument or cfg.instrument)
            gain = -1 + getattr(self, "_set_gain", 0.0) + dg + (final.final_gain if final is not None else 0)
            self.note(deg=deg, instrument=inst, offset=offset + jit, gain=gain, cents=cents, variant=var)
            return
        n = self._note_count.get(kind, 0)
        self._note_count[kind] = n + 1
        span = 2 * len(self.synth.steps)
        gi = self.S.sound_cfg.grid_instrument         # None: the original mix of instruments
        if kind == "reveal":
            self.note(deg=span, instrument=self.S.sound_cfg.soft_instrument if gi else "soft_sine", offset=offset, gain=-16)
        elif kind == "mark":
            self.note(deg=(n % span) + 2, instrument=gi or self.S.sound_cfg.instrument, offset=offset, gain=-11)
        elif kind == "set" and self.S.sound_cfg.grid_set_pitch == "value" and isinstance(val, (int, float)):
            self.note(deg=max(0, min(span, int(val))), instrument=gi or "music_box", offset=offset,
                      gain=-9 + getattr(self, "_set_gain", 0.0))
        elif kind == "set":
            self.note(deg=(n * 2) % span + 1, instrument=gi or "music_box", offset=offset, gain=-12)
        elif kind == "wall":
            self.note(deg=(n % 7) + 3, instrument=gi or "marimba", offset=offset, gain=-6)
        elif kind == "box":
            self.note(deg=(int(val) * 2) % span + 2, instrument=gi or self.S.sound_cfg.instrument, offset=offset, gain=-10)
        elif kind == "edge":
            self.note(deg=(n % 7) + 5, instrument=gi or "marimba", offset=offset, gain=-5)

    def on_var(self, e):
        name, env = e["name"], e["locals"]
        anims, run, first, pending_packs = [], 0.25, [], []
        for w in self.S.widgets:
            if isinstance(w, Pointer) and w.var == name and w.on in self.S.views:
                if not isinstance(e["value"], int):
                    continue
                if not w.shown:
                    w.mob.shift(w.spot(e["value"])); first.append(w.mob); w.shown = True
                else:
                    anims.append(w.mob.animate(rate_func=self.S.motions["swap"].rate()).shift(w.spot(e["value"])))
            elif isinstance(w, Readout) and w.var == name and isinstance(e["value"], (int, float)):
                if not w.shown:
                    w.tracker.set_value(e["value"]); self.add(w.mob); first.append(w.mob); w.shown = True
                    w.first_value, w.first_frame = e["value"], self.renderer.time < 0.5
                elif w.count:
                    anims.append(w.tracker.animate.set_value(e["value"])); run = max(run, 0.6)
                    if w.sound and self.synth:
                        self.note(deg=w.sound_deg, instrument=w.sound, gain=w.sound_gain)
                else:
                    w.tracker.set_value(e["value"])
            elif isinstance(w, Region) and w.when == name and w.on in self.S.views:
                v = self.S.views[w.on]
                shape = w.build(v, env)
                if shape is None:
                    continue
                self.regions_drawn.append(shape)
                if v.orientation == "up":                     # fills upward, wall to wall, like water rising
                    shape.generate_target()
                    shape.stretch(1e-3, 1, about_edge=DOWN)
                    self.add(shape)
                    anims.append(MoveToTarget(shape, rate_func=rate_functions.ease_out_cubic))
                else:
                    anims.append(GrowFromEdge(shape, self.grow_edge(v), rate_func=rate_functions.ease_out_cubic))
                for pk in self.S.widgets:
                    if isinstance(pk, Pack) and pk.region is w:
                        pending_packs.append((pk, shape))
                run = max(run, w.duration / self.S.timing.speed)
                if w.note and self.synth:
                    self.note(deg=min(len(self.synth.steps) * 2 + 2, 2 + int(shape.depth)),
                              instrument=w.sound or self.S.sound_cfg.finale_instrument, gain=w.sound_gain)
        for tw in self.S.widgets:
            if isinstance(tw, Tower) and tw.var == name and isinstance(e["value"], (int, float)):
                anims += self.tower_step(tw, e["value"], (e.get("parts") or [None])[-1])
                run = max(run, tw.duration / self.S.timing.speed)
        for st in self.S.stamps:
            if st.when == name and st.on in self.S.grids:
                g = self.S.grids[st.on]
                rect = st.build(g, env)
                if rect is not None:
                    self.add(rect)
                    self._stamps = getattr(self, "_stamps", []) + [rect]
                    anims.append(FadeIn(rect, scale=st.press, rate_func=rate_functions.ease_out_cubic))
                    run = max(run, st.duration / self.S.timing.speed)
                    self.note(deg=2 + len(self._stamps) * 2 % 14, instrument=self.S.sound_cfg.finale_instrument,
                              gain=-3)
        for gv in self.S.graphs:
            if gv.done_when == name and isinstance(e["value"], int):
                anims += gv.finish(e["value"])
                run = max(run, 0.6 / self.S.timing.speed)
        for pl in self.S.polylines:
            if pl.probe == name and isinstance(e["value"], list):
                anims += pl.probe_to(self, e["value"])
        for ps in self.S.pointsets:
            if ps.focus == name and isinstance(e["value"], list):
                anims += ps.focus_on(e["value"])
                if self.synth:
                    self.note(deg=len(self.synth.steps) * 2, instrument=self.S.sound_cfg.tick_instrument, gain=-12)
        if first and self.S.timing.loop and self.S.timing.intro == "instant" and self.renderer.time == 0:
            for m in first:                                # part of the opening frame (so the loop matches)
                m.set_opacity(1)
            first = []
        if first:
            reveal = []
            for m in first:
                pw = next((w for w in self.S.widgets if isinstance(w, Pointer) and w.mob is m), None)
                reveal += pw.reveal() if pw is not None else [m.animate.set_opacity(1)]
            self.play(*reveal, run_time=0.3)
            for w in self.S.widgets:
                if isinstance(w, Pointer) and w.mob in first and not w.guide:
                    pass
        if anims:
            self.play(*self.code_to(e["line"]), *anims, run_time=run)
        flights = [f for f in (self.pack_flight(pk, sh) for pk, sh in pending_packs) if f is not None]
        if flights:
            self.play(*flights)

    def on_done(self, e):
        S, F = self.S, self.S.finale
        for ob in S.observers:
            ob.end(self)
        for h in S.handlers:                               # a view may stage its own exit before the loop
            if hasattr(h, "outro"):
                h.outro(self)
        self._on_done(e)
        back = [a for pl in S.polylines for a in pl.unwind(self)]
        back += [a for ob in S.observers for a in ob.unwind(self)]
        if back:                                           # loop: return to the opening frame
            if self.synth:
                for j, d in enumerate((4, 2, 0)):
                    self.note(deg=d, instrument=S.sound_cfg.soft_instrument, offset=j * 0.18, gain=-10)
            self.play(*back, run_time=1.1 / S.timing.speed)
        if S.timing.loop and getattr(self, "_opening", None):
            keep = {id(f) for m, _ in self._opening for f in m.get_family()}   # parts count as kept too
            opened = {id(m) for m, _ in self._opening}
            for m in list(self.mobjects):                  # an animation group can adopt opening mobjects
                if id(m) in keep:                          #   (the scene then holds the group, not them):
                    continue                               #   unwrap it so they aren't faded out with it
                inner = [f for f in m.get_family()[1:] if id(f) in opened]
                if inner:
                    rest = [f for f in m.submobjects if id(f) not in keep]
                    self.remove(m)
                    self.add(*inner, *rest)
            anims = [FadeOut(m) for m in self.mobjects if id(m) not in keep]
            for w in S.widgets:                            # readouts shown from the first frame come back
                if isinstance(w, Readout) and w.shown and getattr(w, "first_frame", False):
                    fresh = Readout(**{f: getattr(w, f) for f in w.__dataclass_fields__})
                    fresh.build(); fresh.tracker.set_value(w.first_value); fresh.number.update(); fresh.number.clear_updaters()
                    anims.append(FadeIn(fresh.mob)); keep |= {id(f) for f in fresh.mob.get_family()}
            for m, snap in self._opening:
                m.clear_updaters()
                m.target = snap
                anims.append(MoveToTarget(m, rate_func=rate_functions.ease_in_out_cubic))
            if self.synth:
                for j, d in enumerate((4, 2, 0)):
                    self.note(deg=d, instrument=S.sound_cfg.soft_instrument, offset=j * 0.18, gain=-10)
            # the opening mobjects go back in first, then everything that is leaving goes above them: otherwise
            # play() re-adds an opening group on top and it covers what should be fading (a hard cut)
            leaving = [m for m in self.mobjects if id(m) not in keep]
            self.add(*[m for m, _ in self._opening])
            self.add(*leaving)
            self.play(*anims, run_time=S.timing.loop_time / S.timing.speed)
            for m in list(self.mobjects):
                if id(m) not in keep:
                    self.remove(m)

    def _on_done(self, e):
        S, F = self.S, self.S.finale
        clear = [a for c in S.components if isinstance(c, CodePanel) for a in c.clear()]
        if clear:
            self.play(*clear, run_time=0.3)
        if not F:
            return
        v = self.view(F.target)
        bars = [b for b in self.bars.get(F.target, []) if b is not None]
        if bars:
            n, each = len(bars), 0.4                       # each bar's highlight lasts `each` seconds
            lag = min(0.3, 2.4 / max(1, n) / each)          # the whole sweep takes ~2.5 s
            total = each * (1 + lag * (n - 1))
            if F.style == "recolor":
                anims = [b[0].animate.set_fill(ManimColor(F.color)) for b in bars]
            else:
                anims = [self.pulse(b, F.color) for b in bars]
            for k, b in enumerate(bars):
                self.note(b.value, instrument=S.sound_cfg.finale_instrument, offset=k * lag * each, gain=-4)
            self.play(LaggedStart(*anims, lag_ratio=lag), run_time=total)
        # regions shimmer in turn, and every readout settles on its final value
        tail = []
        if isinstance(e.get("value"), (int, float)) and not isinstance(e.get("value"), bool):
            res_anims = []
            for w in S.widgets:
                if isinstance(w, Tower) and w.show_result and getattr(w, "total", None) is not None:
                    res_anims += self.tower_step(w, e["value"], None)
                if isinstance(w, Readout) and w.result and w.shown:
                    res_anims.append(w.tracker.animate.set_value(e["value"]))
                    if w.result_label and w.label and len(w.mob) > 1:
                        from manim import MarkupText
                        cap = w.mob[1]
                        new = MarkupText(f'<span letter_spacing="1800">{w.result_label.upper()}</span>',
                                         font=w.label_font, font_size=w.label_size,
                                         color=ManimColor(w.finish_color or F.color))
                        new.move_to(cap.get_left(), aligned_edge=LEFT)
                        res_anims.append(cap.animate.become(new))
            if res_anims:
                self.play(*res_anims, run_time=0.8 / S.timing.speed)
        for w in S.widgets:                                # towers ring out, bottom block first
            if isinstance(w, Tower) and w.finale and len(getattr(w, "blocks", [])) > 1:
                n, each = len(w.blocks), 0.45
                lag = 0.35
                for j in range(n):
                    self.note(deg=2 + 2 * j, instrument=S.sound_cfg.finale_instrument, offset=j * lag * each, gain=-4)
                self.play(LaggedStart(*[b.animate(rate_func=there_and_back).set_fill(ManimColor(F.color))
                                        for b in w.blocks], lag_ratio=lag), run_time=each * (1 + lag * (n - 1)))
        if F.grid_ripple:
            self._grid_ripple(F)
        closing = [a for pl in S.polylines for a in pl.finish(self)]
        closing += [a for h in S.handlers if hasattr(h, "finish") for a in h.finish(self)]
        if closing:
            self.play(*closing, run_time=1.6 / S.timing.speed)
        if getattr(self, "_stamps", None):
            self.play(LaggedStart(*[st.animate(rate_func=there_and_back).set_opacity(0.55)
                                    for st in self._stamps], lag_ratio=0.2), run_time=1.6)
        packed = [p for w in S.widgets if isinstance(w, Pack) for p in getattr(w, "pieces", [])]
        if packed:
            tail.append(LaggedStart(*[p.animate(rate_func=there_and_back).set_fill(ManimColor(F.color))
                                      for p in packed], lag_ratio=0.12))
        if self.regions_drawn and F.count_regions:
            self._count_regions(F)
        elif self.regions_drawn:
            # the water chunks light up left to right, with a rising run of notes (a build-up to the finish)
            chunks = sorted(self.regions_drawn, key=lambda r: (r.get_x(), -r.get_y()))
            lag, T, n = 0.15, 1.6, len(chunks)
            tail.append(LaggedStart(*[r[0].animate(rate_func=there_and_back).set_fill(ManimColor(F.color))
                                      for r in chunks], lag_ratio=lag))
            if self.synth and F.region_buildup:
                d = T / (1 + lag * (n - 1))
                top = 2 * len(self.synth.steps)
                for k in range(n):
                    f = k / max(1, n - 1)
                    self.note(deg=round(2 + f * (top - 3)), instrument=S.sound_cfg.instrument,
                              offset=k * lag * d + d / 2, gain=-14 + 10 * f)
        for w in S.widgets:
            if isinstance(w, Readout) and w.shown:
                w.number.clear_updaters()
                tail.append(w.number.animate.set_color(ManimColor(w.finish_color or F.color)))
        if tail:
            self.play(*tail, run_time=1.6)
        if self.synth and S.sound_cfg.finale and not getattr(self, "_chord_done", False):
            top = 2 * len(self.synth.steps) if F.chord_deg is None else F.chord_deg
            for d in _chord(self.synth.steps, top):
                self.note(deg=d, instrument=S.sound_cfg.finale_instrument, gain=-4)
        anims = []
        if F.sparkle:
            for b in bars:
                sp, _ = self.sparkle(self.tip(b, v), F.color); anims += sp
        if F.text:
            if F.letter_spacing:
                from manim import MarkupText
                txt = MarkupText(f'<span letter_spacing="{F.letter_spacing}">{F.text}</span>', font=F.font,
                                 font_size=F.font_size, color=ManimColor(F.color))
            else:
                txt = Text(F.text, font=F.font, font_size=F.font_size, color=ManimColor(F.color))
            txt.move_to(self.finale_spot(txt, v, bars))
            anims.append(FadeIn(txt, shift=0.15 * UP))
        if anims:
            self.play(*anims, run_time=0.9)

    def _grid_ripple(self, F):
        from manim import AnimationGroup
        """Every changed cell pulses in order of its value, one rising note per value: the whole run replayed
        as a single quick wave, building up to the finishing chord."""
        S = self.S
        for g in S.grids.values():
            if g.like:
                continue
            levels = sorted({v for row in g.values for v in row
                             if isinstance(v, (int, float)) and v not in F.grid_ripple_skip})
            if not levels:
                continue
            n = len(levels)
            lag, each = 0.16, 0.42                             # seconds between levels · one pulse
            waves = []
            for j, lv in enumerate(levels):
                cells = [g.cells[r][c] for r in range(g.R) for c in range(g.C) if g.values[r][c] == lv]
                waves.append(AnimationGroup(*[m.animate(rate_func=there_and_back).set_fill(ManimColor(F.color))
                                              for m in cells]))
                if self.synth:
                    f = j / max(1, n - 1)
                    top = 2 * len(self.synth.steps)
                    ranks = self._set_ranks.get(g.name, [])
                    deg = ranks.index(lv) if S.sound_cfg.grid_set_pitch == "rank" and lv in ranks \
                        else round(1 + f * (top - 2))
                    self.note(deg=deg, instrument=F.ripple_instrument or S.sound_cfg.instrument,
                              offset=j * lag + each * 0.3, gain=-8 + 9 * f)
            total = each + lag * (n - 1)
            if F.chord_on_ripple and self.synth and S.sound_cfg.finale:
                root = F.chord_deg if F.chord_deg is not None else 2 * len(self.synth.steps)
                for d in _chord(self.synth.steps, root):
                    self.note(deg=d, instrument=S.sound_cfg.finale_instrument, offset=(n - 1) * lag + each * 0.3 + lag,
                              gain=-4)
                self._chord_done = True
            self.play(LaggedStart(*waves, lag_ratio=lag / each), run_time=total)

    def _count_regions(self, F):
        """Count the water: dim every chunk, then light them back one at a time, each showing +area
        while the total recounts from 0, over a rising, quickening run of notes."""
        S = self.S
        chunks = sorted(self.regions_drawn, key=lambda r: (round(r.get_x(), 2), r.get_y()))
        ro = next((w for w in S.widgets if isinstance(w, Readout) and w.shown), None)
        dim = [c.animate.set_opacity(0.35) for c in chunks]
        if ro is not None:
            dim.append(ro.tracker.animate.set_value(0))
        self.play(*dim, run_time=0.45 / S.timing.speed)
        n = len(chunks)
        top = 2 * len(self.synth.steps) if self.synth else 10
        total = 0
        for k, c in enumerate(chunks):
            f = k / max(1, n - 1)
            dur = (0.42 - 0.2 * f) / S.timing.speed                 # quickening as it builds
            area = getattr(c, "area", 0)
            total += area
            lab = Text(f"+{area:g}", font="IBM Plex Mono", font_size=11,
                       color=ManimColor(F.count_label_color or F.color))
            lab.move_to(c.get_center())
            glow = c[0].copy().set_fill(ManimColor(F.color), opacity=0).set_stroke(width=0)
            self.add(glow)
            anims = [c.animate.set_opacity(1),                       # one animation per object: two on
                     glow.animate(rate_func=there_and_back).set_fill(opacity=0.85),   # the same shape fight
                     FadeIn(lab, shift=0.12 * UP, scale=0.8)]
            if ro is not None:
                anims.append(ro.tracker.animate.set_value(total))
            if self.synth:
                self.note(deg=round(2 + f * (top - 3)), instrument=S.sound_cfg.instrument, gain=-12 + 9 * f)
            self.play(*anims, run_time=dur)
            self.play(FadeOut(lab, shift=0.08 * UP), run_time=0.12 / S.timing.speed)
            self.remove(glow)

    def finale_spot(self, txt, v, bars):
        F = self.S.finale
        if F.text_position:
            return [*F.text_position, 0]
        panels = [c for c in self.S.components if isinstance(c, CodePanel)]
        if panels:
            c = min(panels, key=lambda c: c.code.get_bottom()[1]).code
            return [c.get_x(), c.get_bottom()[1] - 0.7, 0]
        if v:
            return [v.position[0], v.position[1] + v.size[1] / 2 + 0.6, 0]
        return [0, 3.4, 0]


def _chord(steps, root_deg):
    """Scale degrees closest to a root / third / fifth above root_deg."""
    n = len(steps)
    pick = lambda semis: min(range(n), key=lambda k: abs(steps[k] - semis))
    return [root_deg, root_deg + pick(4 if 4 in steps else 3), root_deg + pick(7)]
