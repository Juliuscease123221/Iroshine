"""
iroshine.core — the "watching" half of the library.

Three pieces work together:

  1. Tagged        an int that remembers where it was read from (its *origin*)
  2. TrackedList   a list that logs every read / write / push / pop as an event
  3. rewrite()     rewrites your function's AST so every list you create
                   (stack = [], res = [0] * n, return [...]) becomes a TrackedList

A line tracer (sys.settrace) stamps each event with the source line that
caused it, so the renderer can highlight your code as it plays.
"""

import ast
import inspect
import sys
import textwrap

FILENAME = "<iroshine>"
REC = None  # the active Recorder while a visualization is running


# ─────────────────────────────────────────────────────────────── recorder ──
class Recorder:
    def __init__(self):
        self.events = []
        self.line = None

    def log(self, kind, **data):
        data["type"] = kind
        data["line"] = self.line
        self.events.append(data)


def _log(kind, **data):
    if REC is not None:
        REC.log(kind, **data)


# ───────────────────────────────────────────────────────── tagged values ──
class Tagged(int):
    """An int that carries an origin like {"list": "nums2", "index": 3}.

    Arithmetic returns a plain int, so computed values lose their tag —
    which is exactly right: a computed value didn't *come from* anywhere.
    Ordering comparisons are logged so the renderer can flash both bars.
    """

    def __new__(cls, value, origin):
        obj = super().__new__(cls, value)
        obj.origin = origin
        return obj

    def _cmp(self, other, op, result):
        _log("compare", op=op, result=bool(result),
             a=self.origin, av=int(self),
             b=getattr(other, "origin", None),
             bv=int(other) if isinstance(other, int) else other)
        return result

    # compare against plain ints so Python doesn't bounce to the reflected op
    def _o(self, other):
        return int(other) if isinstance(other, int) else other

    # a + b remembers both origins (e.g. f[i] = f[i-1] + f[i-2]) — see Derived
    def __add__(self, o):
        return _combine(self, o, int(self) + _int(o))

    def __radd__(self, o):
        return _combine(o, self, _int(o) + int(self))

    def __lt__(self, o): return self._cmp(o, "<",  int(self) <  self._o(o))
    def __le__(self, o): return self._cmp(o, "<=", int(self) <= self._o(o))
    def __gt__(self, o): return self._cmp(o, ">",  int(self) >  self._o(o))
    def __ge__(self, o): return self._cmp(o, ">=", int(self) >= self._o(o))
    __hash__ = int.__hash__


def _int(v):
    return int(v) if isinstance(v, int) else v


def _parts(v):
    if isinstance(v, Derived):
        return list(v.parts)
    o = getattr(v, "origin", None)
    return [o] if o else []


def _combine(a, b, value):
    if not isinstance(value, int) or isinstance(value, bool):
        return value
    parts = _parts(a) + _parts(b)
    return Derived(value, parts) if parts else value


class Derived(int):
    """An int computed by adding tracked values; `parts` lists where the pieces came from.
    (No `origin`: a sum didn't *come from* one place, so nothing treats it as a move.)"""

    def __new__(cls, value, parts):
        obj = super().__new__(cls, value)
        obj.parts = parts
        return obj

    def __add__(self, o):
        return _combine(self, o, int(self) + _int(o))

    def __radd__(self, o):
        return _combine(o, self, _int(o) + int(self))

    __hash__ = int.__hash__


class TaggedStr(str):
    """A str that remembers where it was read from (so a word can fly from where it came).
    Any string operation (+, join, slicing…) returns a plain str, so the tag drops off."""

    def __new__(cls, value, origin):
        obj = super().__new__(cls, value)
        obj.origin = origin
        return obj


def _tag(value, origin):
    if isinstance(value, int) and not isinstance(value, bool):
        return Tagged(value, origin)
    if isinstance(value, str):
        return TaggedStr(value, origin)
    return value


def _plain(value):
    if isinstance(value, (Tagged, Derived)):
        return int(value)
    if isinstance(value, TaggedStr):
        return str.__str__(value)
    return value


def _origin(value):
    return getattr(value, "origin", None)


# ─────────────────────────────────────────────────────────── tracked list ──
class TrackedList(list):
    """A real list (isinstance(x, list) is True) that narrates what happens to it."""

    def __init__(self, name, iterable=(), role="local", row=None):
        items = list(iterable)
        # a list of sets (an adjacency list like `graph = [set() for _ in range(n)]`):
        # track each inner set too, as "graph[0]", "graph[1]", ...
        items = [TrackedSet(f"{name}[{k}]", v) if isinstance(v, set) and not isinstance(v, TrackedSet) else v
                 for k, v in enumerate(items)]
        super().__init__(v if isinstance(v, TrackedSet) else _plain(v) for v in items)
        self.name = name
        self.row = row                      # set when this list is one row of a 2-D grid
        if row is None:
            _log("create", list=name, role=role, values=list.copy(self),
                 origins=[_origin(v) for v in items])

    def _ev(self, kind, **data):
        if self.row is not None:
            data["row"] = self.row
        _log(kind, list=self.name, **data)

    def _idx(self, i):
        i = int(i)                      # plain int: comparing a tracked value here would log a fake compare
        return i if i >= 0 else len(self) + i

    # reads ----------------------------------------------------------------
    def __getitem__(self, i):
        if isinstance(i, slice):
            return list.__getitem__(self, i)          # slices are plain copies
        v = list.__getitem__(self, i)
        j = self._idx(i)
        if not isinstance(v, TrackedList):              # reading a whole grid row isn't interesting
            self._ev("read", index=j, value=_plain(v))
        o = {"list": self.name, "index": j}
        if self.row is not None:
            o["row"] = self.row
        return _tag(v, o)

    def __iter__(self):
        j = 0
        while j < len(self):
            yield self[j]                             # goes through __getitem__
            j += 1

    # writes ---------------------------------------------------------------
    def __setitem__(self, i, v):
        if isinstance(i, slice):
            list.__setitem__(self, i, [_plain(x) for x in v])
            _log("replace", list=self.name, values=list.copy(self))
            return
        j = self._idx(i)
        parts = getattr(v, "parts", None)
        if parts:
            self._ev("set", index=j, value=_plain(v), src=_origin(v), parts=parts)
        else:
            self._ev("set", index=j, value=_plain(v), src=_origin(v))
        list.__setitem__(self, i, _plain(v))

    def append(self, v):
        _log("push", list=self.name, index=len(self), value=_plain(v), src=_origin(v))
        list.append(self, _plain(v))

    def extend(self, iterable):
        for v in iterable:
            self.append(v)

    def pop(self, i=-1):
        j = self._idx(i)
        v = list.pop(self, i)
        _log("pop", list=self.name, index=j, value=v)
        return _tag(v, {"list": self.name, "index": j, "popped": True})

    # everything else: just snapshot the new contents
    def _snapshot(method):
        def wrapper(self, *a, **k):
            out = getattr(list, method)(self, *a, **k)
            _log("replace", list=self.name, values=list.copy(self))
            return out
        wrapper.__name__ = method
        return wrapper

    insert = _snapshot("insert")
    remove = _snapshot("remove")
    sort = _snapshot("sort")
    reverse = _snapshot("reverse")
    clear = _snapshot("clear")
    del _snapshot


# ───────────────────────────────────────────────────────────── tracked set ──
def _key(v):
    """Set members as JSON-friendly values: (r, c) tuples become [r, c] lists."""
    if isinstance(v, tuple):
        return [_plain(x) for x in v]
    return _plain(v)


class TrackedSet(set):
    """A real set that reports add / remove / clear. Used for `seen`, `visited`, frontiers…"""

    def __init__(self, name, iterable=()):
        super().__init__(iterable)
        self.name = name
        _log("screate", set=name, values=[_key(v) for v in set.__iter__(self)])

    def add(self, v):
        if v not in self:
            _log("sadd", set=self.name, value=_key(v))
        set.add(self, v)

    def discard(self, v):
        if v in self:
            _log("sremove", set=self.name, value=_key(v))
        set.discard(self, v)

    def remove(self, v):
        _log("sremove", set=self.name, value=_key(v))
        set.remove(self, v)

    def update(self, *its):
        for it in its:
            for v in it:
                self.add(v)

    def clear(self):
        _log("sclear", set=self.name)
        set.clear(self)


def __viz_track__(name, value):
    """Called by rewritten code: `stack = []` → `stack = __viz_track__('stack', [])`."""
    if isinstance(value, list) and not isinstance(value, TrackedList):
        return TrackedList(name, value)
    if isinstance(value, set) and not isinstance(value, TrackedSet):
        return TrackedSet(name, value)
    return value


# ──────────────────────────────────────────────────────────── AST rewrite ──
class _Rewriter(ast.NodeTransformer):
    @staticmethod
    def _listy(node):
        if isinstance(node, (ast.List, ast.ListComp, ast.Set, ast.SetComp)):
            return True
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("list", "set"):
            return True
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
            return isinstance(node.left, ast.List) or isinstance(node.right, ast.List)
        return False

    @staticmethod
    def _wrap(name, node):
        return ast.Call(func=ast.Name("__viz_track__", ast.Load()),
                        args=[ast.Constant(name), node], keywords=[])

    def visit_Assign(self, node):
        self.generic_visit(node)
        if len(node.targets) != 1:
            return node
        t = node.targets[0]
        if isinstance(t, ast.Name) and self._listy(node.value):
            node.value = self._wrap(t.id, node.value)
        elif isinstance(t, ast.Tuple) and isinstance(node.value, ast.Tuple) \
                and len(t.elts) == len(node.value.elts):             # a, b = [], set()
            node.value.elts = [self._wrap(n.id, v) if isinstance(n, ast.Name) and self._listy(v) else v
                               for n, v in zip(t.elts, node.value.elts)]
        return node

    def visit_AnnAssign(self, node):
        self.generic_visit(node)
        if node.value is not None and isinstance(node.target, ast.Name) and self._listy(node.value):
            node.value = self._wrap(node.target.id, node.value)
        return node

    def visit_Return(self, node):
        self.generic_visit(node)
        if node.value is not None and self._listy(node.value):
            node.value = self._wrap("result", node.value)
        return node


def rewrite(func):
    """Return (instrumented_function, source_text). The user's file is untouched."""
    source = textwrap.dedent(inspect.getsource(func))
    tree = ast.parse(source)
    fdef = tree.body[0]
    fdef.decorator_list = []
    _Rewriter().visit(tree)
    ast.fix_missing_locations(tree)
    namespace = dict(func.__globals__)
    namespace["__viz_track__"] = __viz_track__
    exec(compile(tree, FILENAME, "exec"), namespace)
    return namespace[fdef.name], source


# ─────────────────────────────────────────────────────────────── tracing ──
def _snapshot_value(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return _plain(v)
    if isinstance(v, list):
        return [_plain(x) for x in list.copy(v)]
    return None


def _check_vars(frame):
    """Emit a "var" event for every watched variable whose value changed.

    The event carries a snapshot of the frame's simple locals (numbers and lists),
    so things like Region(y0="height[top]") can be evaluated later at render time.
    """
    if not REC.watch:
        return
    f_locals = frame.f_locals
    key = id(frame)
    last = REC.last.setdefault(key, {})
    snap = None
    for name in REC.watch:
        if name in f_locals:
            v = _snapshot_value(f_locals[name])
            if v is not None and last.get(name, _MISSING) != v:
                last[name] = v
                if snap is None:
                    snap = {k: sv for k, x in f_locals.items()
                            if not k.startswith("__") and (sv := _snapshot_value(x)) is not None}
                extra = {}
                parts = getattr(f_locals[name], "parts", None)
                if parts:
                    extra["parts"] = list(parts)
                REC.log("var", name=name, value=v, locals=snap, **extra)


_MISSING = object()


def _tracer(frame, event, arg):
    if frame.f_code.co_filename != FILENAME:
        return None

    def local(frame, event, arg):
        if event in ("line", "return"):
            _check_vars(frame)             # changes made by the line that just finished
        if event == "line":
            REC.line = frame.f_lineno
        return local

    REC.line = frame.f_lineno
    return local


def _track_input(name, a):
    if name in REC.grids and isinstance(a, list) and a and all(isinstance(r, list) for r in a):   # a 2-D grid
        grid = [[_plain(x) for x in r] for r in a]
        REC.log("create", list=name, role="input", grid=grid, values=[], origins=[])
        outer = list.__new__(TrackedList)
        list.__init__(outer, [TrackedList(name, r, row=k) for k, r in enumerate(a)])
        outer.name, outer.row = name + "#rows", None
        return outer
    if isinstance(a, list):
        return TrackedList(name, a, role="input")
    if isinstance(a, set):
        return TrackedSet(name, a)
    return a


# ─────────────────────────────────────────────────────────────── public ──
def record(method, *args, watch=(), grids=()):
    """Run `method(*args)` instrumented. Returns (events, source, result).

    watch: names of local variables (ints, floats, lists) to report as "var" events
           when they change — used by Pointer, Readout and Region.
    """
    global REC
    func = getattr(method, "__func__", method)
    bound_self = getattr(method, "__self__", None)
    new_func, source = rewrite(func)

    params = list(inspect.signature(func).parameters)
    if bound_self is not None:
        params = params[1:]

    REC = Recorder()
    REC.watch, REC.last, REC.grids = tuple(watch), {}, set(grids)
    try:
        call_args = [_track_input(name, a) for name, a in zip(params, args)]
        sys.settrace(_tracer)
        try:
            result = new_func(bound_self, *call_args) if bound_self is not None else new_func(*call_args)
        finally:
            sys.settrace(None)
        REC.line = None
        REC.log("done", value=[_plain(v) for v in list.copy(result)] if isinstance(result, list) else _plain(result))
        return REC.events, source, result
    finally:
        REC = None
