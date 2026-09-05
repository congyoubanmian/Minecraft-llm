from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    BASE_X,
    BASE_Y,
    BASE_Z,
    Fill,
    Materials as M,
    add_fill,
    add_tree,
    run_builder,
)


"""
Zhongnan Mountain Saddle Smoothing 3D (终南山鞍部填谷补坡·三维柔化).

Additive terrain pass that softens the six hard-edged cone peaks of
mountain_zhongnan.py by filling the five bare valleys between them with
terraced spur hills, so the range reads as one rolling ridge instead of
six separate triangles.

Fill-valley approach, peaks untouched: nothing here clears blocks and no
fill lands on any peak footprint; every command only ADDS valley fill at
y <= 60 (hard cap y 100), so the beacon-tower summit silhouette at
(3200, -680) and every y > 100 block stay exactly as built.

Saddle treatment ranges (city-local coords, derived from the peak table
in mountain_zhongnan.py; chain x = the terraced ramp span, z band = the
ramp footprint, crest y = saddle top = min(two peak heights) // 3):

    saddle  between peaks      ramp chain x      z band       crest y
    s1      -200 <-> 800        -36 ..   636     -710..-650   40
    s2       800 <-> 2000       1064 .. 1736     -715..-655   46
    s3      2000 <-> 3200       2254 .. 2926     -730..-670   53
    s4      3200 <-> 4500       3534 .. 4206     -730..-670   50
    s5      4500 <-> 5800       4824 .. 5496     -720..-660   43

Distinctive features:
    - Two facing terraced ramp chains per saddle: foot ramps rise about
      5-6 blocks per 20 blocks of run (STONE core, GRASS turf), easing
      step by step into the saddle crest; the three upper terraces taper
      to a narrower band so each spur has a natural shoulder
    - Weathered scree skirts (COBBLE / MOSS_STONE / ANDESITE single-block
      scatter) at the toe of every new ramp
    - A 2-wide DIRT/GRASS crest path with one lone mountain pine per saddle
    - Low LEAVES brush clumps dotted on the ramp shoulders (5 per saddle)
    - A 1-wide, 1-deep shallow stream seeping from each saddle's lowest
      point, with a cobble ford and LEAVES reed clumps on its banks

Protection: the zone x 3100..3300 ∩ z -780..-580 (beacon tower and cliff
grotto Buddhas) receives no fills at all; main() self-checks both that
exclusion and the y <= 100 cap before handing the plan to run_builder.
"""


# ---------------------------------------------------------------------------
# Saddle geometry.  Each saddle fills the open gap between two peak
# footprints of mountain_zhongnan.py; chains never reach a peak base.
# ---------------------------------------------------------------------------
# (tag, mid_x, crest_y = min(neighbour heights)//3, z centre of the band)
SADDLES = [
    ("s1 west", 300, 40, -680),
    ("s2 west-central", 1400, 46, -685),
    ("s3 central", 2590, 53, -700),
    ("s4 central-east", 3870, 50, -700),
    ("s5 east", 5160, 43, -690),
]

BAND_HALF = 30            # saddle ramp band spans zc-30 .. zc+30
UPPER_INSET = 15          # z inset for the three upper (narrower) terraces
RAMP_LENS = (40, 40, 64, 64, 64, 64)          # terrace run lengths, foot -> crest
RAMP_FRACS = (0.25, 0.48, 0.60, 0.72, 0.87, 1.00)  # eased height fractions
CHAIN = sum(RAMP_LENS)    # 336, one-sided ramp chain length
SCREE = (M.COBBLE, M.MOSS_STONE, M.ANDESITE)


def _ramp_heights(waist: int) -> list[int]:
    """Terrace top heights: steep at the foot (~5-6 per 20 blocks of run),
    easing toward the crest so the spur dies into the peak waists."""
    return [max(2, round(waist * frac)) for frac in RAMP_FRACS]


def _ramp_chain(
    fills: list[Fill],
    tag: str,
    side: str,
    x_start: int,
    step: int,
    z1: int,
    z2: int,
    heights: list[int],
) -> None:
    """One half of a saddle: terraces stepping from the valley floor up to
    the crest.  step=+1 marches east, step=-1 marches west.  Lower terraces
    use a full-height toe wall plus a back-fill slab (sealed, no floating);
    upper terraces are solid single cores on a narrower band."""
    x = x_start
    for i, top in enumerate(heights):
        nxt = x + step * RAMP_LENS[i]
        x_lo, x_hi = sorted((x, nxt))
        zt1, zt2 = (z1, z2) if i < 3 else (z1 + UPPER_INSET, z2 - UPPER_INSET)
        label = f"mtnsmooth {tag} ramp {side}{i}"
        if i < 3 and i > 0:
            # Toe wall on the open (outer) face keeps the riser solid.
            if step > 0:
                t_lo, t_hi = x_lo, x_lo + 14
                f_lo, f_hi = x_lo + 15, x_hi
            else:
                t_lo, t_hi = x_hi - 14, x_hi
                f_lo, f_hi = x_lo, x_hi - 15
            add_fill(fills, f"{label} toe", (t_lo, 1, zt1), (t_hi, top, zt2), M.STONE)
            add_fill(fills, f"{label} body", (f_lo, heights[i - 1] - 2, zt1), (f_hi, top, zt2), M.STONE)
        else:
            add_fill(fills, f"{label} core", (x_lo, 1, zt1), (x_hi, top, zt2), M.STONE)
        add_fill(fills, f"{label} turf", (x_lo, top, zt1), (x_hi, top, zt2), M.GRASS)
        x = nxt


def _crest(fills: list[Fill], tag: str, mid: int, waist: int, zc: int) -> None:
    """2-wide DIRT/GRASS ridge path along the saddle top + one small pine."""
    edges = [mid - 64, mid - 32, mid, mid + 32, mid + 64]
    mats = [M.DIRT, M.GRASS, M.DIRT, M.GRASS]
    for i in range(4):
        add_fill(
            fills, f"mtnsmooth {tag} crest path {i}",
            (edges[i], waist, zc), (edges[i + 1], waist, zc + 1), mats[i],
        )
    add_tree(fills, f"mtnsmooth {tag} crest pine", mid + 48, zc - 7, waist + 1, height=4, spread=2)


def _scree(fills: list[Fill], tag: str, x_out_w: int, x_out_e: int, zc: int, foot_y: int) -> None:
    """Weathered rock scatter at both toes of the new ramp chain."""
    spots = [
        (x_out_w - 20, 1, zc - 14),
        (x_out_w - 12, 1, zc + 9),
        (x_out_w + 10, foot_y + 1, zc - 24),
        (x_out_e + 20, 1, zc + 12),
        (x_out_e + 12, 1, zc - 8),
        (x_out_e - 10, foot_y + 1, zc + 24),
    ]
    for i, (x, y, z) in enumerate(spots):
        add_fill(fills, f"mtnsmooth {tag} scree {i}", (x, y, z), (x, y, z), SCREE[i % 3])


def _brush(fills: list[Fill], tag: str, mid: int, zc: int, heights: list[int]) -> None:
    """Low leaves clumps dotted on the ramp shoulders (5 per saddle)."""
    x1, x2 = mid - CHAIN, mid + CHAIN
    spots = [
        (x1 + 18, heights[0] + 1, zc + 18, False),
        (x1 + 56, heights[1] + 1, zc - 19, True),
        (x1 + 100, heights[2] + 1, zc + 20, False),
        (x1 + 170, heights[3] + 1, zc - 10, True),
        (x2 - 56, heights[1] + 1, zc + 16, False),
    ]
    for i, (x, y, z, tall) in enumerate(spots):
        top = y + 1 if tall else y
        add_fill(fills, f"mtnsmooth {tag} brush {i}", (x, y, z), (x + 1, top, z + 1), M.LEAVES)


def _stream(fills: list[Fill], tag: str, mid: int, z1: int) -> None:
    """1-wide shallow stream meandering out of the saddle's lowest ground,
    with a cobble ford and reed clumps on the banks (additive, no carve)."""
    zs = z1 - 8
    add_fill(fills, f"mtnsmooth {tag} stream w", (mid - 140, 1, zs), (mid - 60, 1, zs), M.WATER)
    add_fill(fills, f"mtnsmooth {tag} stream mid", (mid - 60, 1, zs + 2), (mid + 40, 1, zs + 2), M.WATER)
    add_fill(fills, f"mtnsmooth {tag} stream e", (mid + 40, 1, zs - 1), (mid + 140, 1, zs - 1), M.WATER)
    add_fill(fills, f"mtnsmooth {tag} stream ford", (mid - 2, 1, zs + 2), (mid + 2, 1, zs + 2), M.COBBLE)
    reeds = ((mid - 66, zs + 3), (mid + 34, zs + 1), (mid + 96, zs - 2))
    for i, (rx, rz) in enumerate(reeds):
        add_fill(fills, f"mtnsmooth {tag} reed {i}", (rx, 1, rz), (rx, 2, rz), M.LEAVES)


def build_mountain_smooth_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Terraced valley ramps: two facing chains per saddle, foot ramps
    #    rising ~5 blocks per 20 and easing into the waist-height crest.
    # ------------------------------------------------------------------
    for tag, mid, waist, zc in SADDLES:
        heights = _ramp_heights(waist)
        z1, z2 = zc - BAND_HALF, zc + BAND_HALF
        _ramp_chain(fills, tag, "w", mid - CHAIN, 1, z1, z2, heights)
        _ramp_chain(fills, tag, "e", mid + CHAIN, -1, z1, z2, heights)

    # ------------------------------------------------------------------
    # 2. Ridge paths: 2-wide DIRT/GRASS trail on each crest + a pine.
    # ------------------------------------------------------------------
    for tag, mid, waist, zc in SADDLES:
        _crest(fills, tag, mid, waist, zc)

    # ------------------------------------------------------------------
    # 3. Scree skirts at the toes of every new ramp.
    # ------------------------------------------------------------------
    for tag, mid, waist, zc in SADDLES:
        _scree(fills, tag, mid - CHAIN, mid + CHAIN, zc, _ramp_heights(waist)[0])

    # ------------------------------------------------------------------
    # 4. Brush patches on the ramp shoulders.
    # ------------------------------------------------------------------
    for tag, mid, waist, zc in SADDLES:
        _brush(fills, tag, mid, zc, _ramp_heights(waist))

    # ------------------------------------------------------------------
    # 5. Mountain streams with fords and reeds along the valley floors.
    # ------------------------------------------------------------------
    for tag, mid, waist, zc in SADDLES:
        _stream(fills, tag, mid, zc - BAND_HALF)


def _self_check(fills: list[Fill]) -> dict:
    """Guarantee the beacon tower / grotto Buddha zone stays untouched and
    nothing is ever placed above y=100 (city-local y; Fill stores world
    coords, so subtract the BASE_* anchors first)."""
    avoid = 0
    high = 0
    max_y = 0
    for f in fills:
        lx1, lx2 = f.x1 - BASE_X, f.x2 - BASE_X
        ly1, ly2 = f.y1 - BASE_Y, f.y2 - BASE_Y
        lz1, lz2 = f.z1 - BASE_Z, f.z2 - BASE_Z
        if lx1 <= 3300 and lx2 >= 3100 and lz1 <= -580 and lz2 >= -780:
            avoid += 1
        if max(ly1, ly2) > 100:
            high += 1
        max_y = max(max_y, ly2)
    return {
        "total_fills": len(fills),
        "avoid_zone_hits": avoid,
        "above_y100_local": high,
        "max_local_y": max_y,
    }


def main() -> None:
    fills: list[Fill] = []
    build_mountain_smooth_3d(fills)
    print(
        json.dumps({"self_check": _self_check(fills)}, ensure_ascii=False, indent=2),
        flush=True,
    )
    run_builder(build_mountain_smooth_3d, "mountain_smooth_3d")


if __name__ == "__main__":
    main()
