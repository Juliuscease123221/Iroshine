"""
iroshine.packing — pack integer rectangles into a box that's as close to square as possible.

Uses MaxRects with the "best short side fit" rule, the approach Jukka Jylänki's survey
"A Thousand Ways to Pack the Bin" found to be among the strongest simple packers. We
try box sizes from smallest and squarest upward, and keep the first one everything fits in.

Because iroshine records the whole run before drawing, every rectangle is known in
advance. So the layout is solved once, up front (with pieces sorted big-first, which
packs much tighter). The animation then drops each piece into its final spot as it
appears in the run.

    rotate=False   a piece keeps its orientation: its width stays horizontal
    rotate=True    a piece may turn 90° if that packs tighter / squarer
"""

import math


def _maxrects(sizes, W, H, rotate):
    """Place each (w, h) into a W×H bin. Returns {index: (x, y, w, h, rotated)} or None."""
    free = [(0, 0, W, H)]
    placed = {}
    order = sorted(range(len(sizes)), key=lambda i: (-sizes[i][0] * sizes[i][1], -max(sizes[i])))
    for i in order:
        w, h = sizes[i]
        best = None                                      # (short_fit, long_fit, x, y, w, h, rot)
        for fx, fy, fw, fh in free:
            for (pw, ph, rot) in ((w, h, False), (h, w, True)) if rotate and w != h else ((w, h, False),):
                if pw <= fw and ph <= fh:
                    short, long_ = sorted((fw - pw, fh - ph))
                    cand = (short, long_, fy, fx, pw, ph, rot)
                    if best is None or cand < best:
                        best = cand
        if best is None:
            return None
        _, _, y, x, pw, ph, rot = best
        placed[i] = (x, y, pw, ph, rot)
        free = _split(free, (x, y, pw, ph))
    return placed


def _split(free, used):
    ux, uy, uw, uh = used
    out = []
    for fx, fy, fw, fh in free:
        if ux >= fx + fw or ux + uw <= fx or uy >= fy + fh or uy + uh <= fy:
            out.append((fx, fy, fw, fh)); continue
        if ux > fx:
            out.append((fx, fy, ux - fx, fh))
        if ux + uw < fx + fw:
            out.append((ux + uw, fy, fx + fw - ux - uw, fh))
        if uy > fy:
            out.append((fx, fy, fw, uy - fy))
        if uy + uh < fy + fh:
            out.append((fx, uy + uh, fw, fy + fh - uy - uh))
    # drop free rectangles contained in another
    pruned = []
    for i, a in enumerate(out):
        if a[2] <= 0 or a[3] <= 0:
            continue
        contained = any(i != j and b[0] <= a[0] and b[1] <= a[1] and
                        a[0] + a[2] <= b[0] + b[2] and a[1] + a[3] <= b[1] + b[3] and (a != b or j < i)
                        for j, b in enumerate(out))
        if not contained:
            pruned.append(a)
    return pruned


def pack_square(sizes, rotate=False):
    """Pack integer (w, h) rectangles as close to a square as possible.

    Returns (placements, (W, H)) where placements[i] = (x, y, w, h, rotated) in cells,
    origin at the bottom-left, and (W, H) is the bounding box actually used.
    """
    sizes = [(int(w), int(h)) for w, h in sizes]
    if not sizes:
        return {}, (0, 0)
    area = sum(w * h for w, h in sizes)
    lo_w = max(min(w, h) if rotate else w for w, h in sizes)
    lo_h = max(min(w, h) if rotate else h for w, h in sizes)
    lo_side = max(max(min(w, h) for w, h in sizes), math.ceil(math.sqrt(area)))
    cands = []
    for W in range(lo_w, 2 * lo_side + max(max(s) for s in sizes) + 2):
        for H in range(lo_h, 2 * lo_side + max(max(s) for s in sizes) + 2):
            if W * H >= area:
                cands.append((max(W, H), W * H, abs(W - H), W, H))
    for _, _, _, W, H in sorted(cands):
        placed = _maxrects(sizes, W, H, rotate)
        if placed is not None:
            bw = max(x + w for x, y, w, h, r in placed.values())
            bh = max(y + h for x, y, w, h, r in placed.values())
            return placed, (bw, bh)
    raise RuntimeError("could not pack")
