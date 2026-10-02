"""
iroshine.graph — GraphView: nodes and directed edges from an adjacency list of sets.

Bind it to a list whose elements are sets, e.g. `graph = [set() for _ in range(n)]`.
Every `graph[u].add(v)` draws the edge u → v. `done_when="node"` marks a node as
finished whenever that variable takes its value (e.g. the node popped in a
topological sort): the node fills in and its outgoing edges fade, because the
dependencies they stood for are now satisfied.

layout="line"    nodes on a horizontal line, edges as arcs (an arc diagram):
                 u < v arcs over the top, u > v arcs underneath
layout="circle"  nodes around a circle
"""

import math
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Sequence, Tuple, Union

import numpy as np
from manim import (DOWN, PI, UP, Circle, CurvedArrow, FadeIn, ManimColor, Text, VGroup,
                   interpolate_color, rate_functions)


@dataclass
class GraphView:
    adj: str                                         # the adjacency list: adj[u] is a set of v
    position: Tuple[float, float] = (0.0, 0.0)
    size: Tuple[float, float] = (8.0, 1.6)           # line layout: width × arc room; circle: diameter
    layout: str = "line"
    node_radius: float = 0.2
    node_colors: Any = None                          # "grid:<name>" to borrow a GridView's colors, a dict, or a color
    node_stroke: str = "#ffffff"
    labels: bool = True
    label_font: str = "IBM Plex Mono"
    label_size: float = 14
    label_color: str = "#000000"
    edge_color: str = "#ffffff"
    edge_width: float = 2.5
    edge_opacity: float = 0.75
    arc: float = 1.1                                 # arc curvature (radians)
    done_when: Optional[str] = None                  # a variable: when it takes value u, node u is finished
    done_edge_opacity: float = 0.12
    dim: float = 0.7                                 # untouched nodes start dimmed toward the background
    background: str = "#000000"

    # ---------------------------------------------------------------- setup
    def plan(self, scene, events):
        nodes = set()
        for e in events:
            if e["type"] == "sadd" and self._u(e) is not None:
                nodes.add(self._u(e)); nodes.add(e["value"])
            if e["type"] == "var" and e["name"] == self.done_when and isinstance(e["value"], int):
                nodes.add(e["value"])
        self.nodes = sorted(n for n in nodes if isinstance(n, int))
        self.pos = {}
        n = max(1, len(self.nodes))
        cx, cy = self.position
        w, h = self.size
        for k, u in enumerate(self.nodes):
            if self.layout == "circle":
                a = PI / 2 - 2 * PI * k / n
                self.pos[u] = np.array([cx + w / 2 * math.cos(a), cy + w / 2 * math.sin(a), 0])
            else:
                x = cx - w / 2 + (w * (k + 0.5) / n)
                self.pos[u] = np.array([x, cy, 0])
        self.scene = scene
        self.mobs, self.edges, self.touched, self.done = {}, {}, set(), set()
        group = VGroup()
        for u in self.nodes:
            g = self._node(u)
            g.set_opacity(0.0)
            self.mobs[u] = g
            group.add(g)
        return group

    def color(self, u):
        c = self.node_colors
        if isinstance(c, str) and c.startswith("grid:"):
            return self.scene.S.grids[c[5:]].color_of(u)
        if isinstance(c, dict):
            return ManimColor(c.get(u, "#888888"))
        return ManimColor(c or "#cccccc")

    def _node(self, u):
        dot = Circle(radius=self.node_radius).move_to(self.pos[u])
        dot.set_fill(self.color(u), opacity=1).set_stroke(ManimColor(self.node_stroke), width=0)
        parts = [dot]
        if self.labels:
            t = Text(str(u), font=self.label_font, font_size=self.label_size, color=ManimColor(self.label_color))
            parts.append(t.move_to(dot.get_center()))
        return VGroup(*parts)

    def _u(self, e):
        name = e.get("set") or ""
        if name.startswith(self.adj + "[") and name.endswith("]"):
            try:
                return int(name[len(self.adj) + 1:-1])
            except ValueError:
                return None
        return None

    def intro(self):
        """Nodes fade in dimmed: they exist, but nothing is known about them yet."""
        return [m.animate.set_opacity(1 - self.dim) for m in self.mobs.values()]

    # ------------------------------------------------------------ batching
    def handles(self, e):
        return e["type"] == "sadd" and self._u(e) is not None and e["value"] in self.pos

    def key(self, e):
        return ("edge", self.adj, self._u(e), e["value"])

    def anim(self, scene, e):
        u, v = self._u(e), e["value"]
        parts, notes = [], []
        for x in (u, v):
            if x not in self.touched:
                self.touched.add(x)
                parts.append(self.mobs[x].animate.set_opacity(1))
        if (u, v) in self.edges or u == v:
            return parts, notes
        a, b = self.pos[u], self.pos[v]
        d = (b - a) / (np.linalg.norm(b - a) or 1)
        start, end = a + d * self.node_radius * 1.15, b - d * self.node_radius * 1.15
        bend = -self.arc if (self.layout == "line" and u < v) else self.arc
        arrow = CurvedArrow(start, end, angle=bend, color=ManimColor(self.edge_color),
                            stroke_width=self.edge_width, tip_length=0.14)
        arrow.set_opacity(self.edge_opacity)
        self.edges[(u, v)] = arrow
        scene.add(arrow)
        scene.bring_to_front(*self.mobs.values())
        from manim import Create
        parts.append(Create(arrow, rate_func=rate_functions.ease_in_out_cubic))
        notes.append(("edge", len(self.edges)))
        return parts, notes

    # -------------------------------------------------------------- finish
    def finish(self, u):
        """Animations for node u being done: it pulses, and its outgoing edges fade."""
        out = []
        if u in self.mobs:
            self.done.add(u)
            ring = Circle(radius=self.node_radius * 1.45).move_to(self.pos[u])
            ring.set_fill(opacity=0).set_stroke(ManimColor(self.node_stroke), width=2.5)
            self.scene.add(ring)
            out.append(self.mobs[u].animate(rate_func=rate_functions.there_and_back).scale(1.25))
            out.append(FadeIn(ring, scale=0.6))
            self.mobs[u].set_opacity(1)
        for (a, b), arrow in self.edges.items():
            if a == u:
                out.append(arrow.animate.set_opacity(self.done_edge_opacity))
        return out
