"""Pagoda body detail overlay (大雁塔·小雁塔 塔身细节深化叠加).

English name: Giant & Small Wild Goose Pagoda - body detail overlay pass.

This module adds fine surface detail ON TOP of the two already-built
pagodas. Every fill is anchored to the tier geometry derived from the
base modules, so each niche, door, tile, tablet and chain lands exactly
on the existing tower bodies.

深化对象清单 (targets and coordinate derivation):
    大雁塔 (pagoda_giant.py, centre CX,CZ = 4580,3860)
        tier t (0..6): r = 44 - 4t, y_base = 1 + 12t, body y_base..y_base+10
        (tier_height 10, pitch 12). add_pagoda_eave at y_base+10 with
        overhang 5 -> outer slab ring at offset r+6, height y_base+11.
        add_pagoda_openings: half-width hw = max(2, min(5, r//5)) = 5 for
        t0..t4 and 4 for t5..t6; each face centre is carved
        y_base+1..y_base+8 through both wall skins (offsets r-1..r+1), so
        the face CENTRE of every tier is already a deep arched recess -
        the Buddha ensembles therefore stand inside those recesses
        (buddha on the outer skin plane r, halo on the inner plane r-1)
        and no extra AIR carve is needed. The base oak lintel at
        y_base+9..y_base+10 already serves as the niche 龛楣.
        pagoda_giant_3d.py finial: jewel at (CX+-2, y 106..108); the
        tier-6 eave corner posts (GOLD_ACCENT) stand at (+-26, 84..86).
    小雁塔 (pagoda_small.py, centre CX,CZ = 1320,3700)
        tier t (0..12): r = max(8, 34 - 2t), y_base = 1 + 6t, body
        y_base..y_base+5 (tier_height 5, pitch 6), eave y_base+5 with
        overhang 3 -> slab ring at r+4, y_base+6; same hw formula.
        xiaoyanta_3d.py content strictly avoided: its crypt (y -6..-2),
        central stairwell shaft (CX+-7, y 2..78), south doors (CX+-1),
        wind bells at (+-(r+5), y_eave, +-(r+5)) and the Morning Bell
        Tower near (1412, 3746) are never touched; the rebuilt finial
        (jewel y 89..90) is only used as the chain anchor.

Sections:
    1. Giant Buddha niches (每层四面龛佛+背光环, recess placement)
    2. Small pagoda 壶门 (per-tier alternating offset arched pseudo-doors)
    3. Eave-end tiles 瓦当 on both towers' eave slab rings
    4. Giant inscription tablets 铭砖 beside the south openings
    5. Finial chains 刹链 dropping from both pagoda finials to the
       top-tier eave corners
    6. "雁塔圣教序" pixel stele mural in the giant ground-floor south
       opening (add_pixel_mural over a single dark backing slab)

Distinctive features:
    - A glowing QUARTZ Buddha with a GOLD/SEA_LANTERN halo ensemble
      inside every arched opening of all seven giant-pagoda storeys
    - Dark 壶门 pseudo-doors whose lintels join the base openings'
      lintels into a continuous carved frieze, offset one block per
      tier parity so the pattern never looks stamped
    - Alternating GOLD/QUARTZ eave-end tiles dotted along the outer
      slab ring of every giant tier (alternating tiers on the small
      pagoda: its thirteen eave rings sit only 6 blocks apart, so
      alternating keeps the fill budget and avoids visual buzz)
    - Four IRON_BARS chains per tower sagging from the finial jewel to
      the four eave corner posts (drop 2 / advance 1, then a flat
      drape onto the corner)
    - A dark stele slab with quartz "script" dots and a gold seal
      painted inside the famous south doorway, echoing the real
      雁塔圣教序 steles kept in the Big Wild Goose Pagoda
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    Fill,
    Materials as M,
    add_fill,
    add_pixel_mural,
    run_builder,
)

# ---------------------------------------------------------------------------
# Derived tier geometry (must match pagoda_giant.py / pagoda_small.py).
# ---------------------------------------------------------------------------
GIANT_CX = 4580
GIANT_CZ = 3860
GIANT_TIERS = 7
GIANT_BASE_RADIUS = 44
GIANT_TIER_HEIGHT = 10
GIANT_TIER_PITCH = 12
GIANT_EAVE_OVERHANG = 5

SMALL_CX = 1320
SMALL_CZ = 3700
SMALL_TIERS = 13
SMALL_BASE_RADIUS = 34
SMALL_TIER_HEIGHT = 5
SMALL_TIER_PITCH = 6
SMALL_EAVE_OVERHANG = 3

# Finial anchors read from the 3D overlay modules.
GIANT_JEWEL_X0 = 2  # jewel half-width at (CX+-2, y 106..108)
GIANT_CHAIN_TOP_Y = 105  # first chain link, just under the jewel
GIANT_DRAPE_Y = 87  # flat drape height, one above the corner-post top
GIANT_CORNER_OFF = 26  # tier-6 eave corner post offset (r20 + overhang 5 + 1)
SMALL_CHAIN_TOP_Y = 89  # beside the small finial jewel (y 89..90)
SMALL_DRAPE_Y = 81  # top of the small tier-12 corner posts (+-14, 79..81)

_FACES = (
    ("north", "z", -1),
    ("south", "z", 1),
    ("west", "x", -1),
    ("east", "x", 1),
)


def _giant_tier(t: int) -> tuple[int, int]:
    """Radius and base y of giant-pagoda tier t, as pagoda_giant.py builds it."""
    return GIANT_BASE_RADIUS - 4 * t, 1 + GIANT_TIER_PITCH * t


def _small_tier(t: int) -> tuple[int, int]:
    """Radius and base y of small-pagoda tier t, as pagoda_small.py builds it."""
    return max(8, SMALL_BASE_RADIUS - 2 * t), 1 + SMALL_TIER_PITCH * t


def _opening_half_width(r: int) -> int:
    """Half-width of the base modules' carved openings (lib.add_pagoda_openings)."""
    return max(2, min(5, r // 5))


# ---------------------------------------------------------------------------
# Section 6 (built first so the halo may overwrite its backing): the
# "雁塔圣教序" stele mural filling the giant ground-floor south recess.
# The base opening carve is exactly 11 wide x 8 tall (x CX-5..CX+5,
# y 2..9) at plane z = CZ + r - 1; the dark backing slab covers that
# plane plus one embedded frame column.
# ---------------------------------------------------------------------------
_STELE_ART = [
    "DDDDDDDDDDDD",
    "D.QQ..Q...QD",
    "D..........D",
    "D..Q..Q..Q.D",
    "D..........D",
    "D.Q...Q..Q.D",
    "D..........D",
    "DDDDDDDDDGGD",
]
_STELE_PALETTE = {"Q": M.QUARTZ, "G": M.GOLD}


def _giant_stele_mural(fills: list[Fill]) -> None:
    r, _ = _giant_tier(0)
    plane_z = GIANT_CZ + r - 1
    add_fill(
        fills,
        "pagodadetail giant stele backing",
        (GIANT_CX - 6, 2, plane_z),
        (GIANT_CX + 5, 9, plane_z),
        M.DARK,
    )
    add_pixel_mural(
        fills,
        "pagodadetail giant stele mural",
        _STELE_ART,
        _STELE_PALETTE,
        GIANT_CX - 6,
        9,
        plane_z,
        axis="x",
    )


# ---------------------------------------------------------------------------
# Section 1: Buddha niche ensembles in every giant-pagoda opening.
# ---------------------------------------------------------------------------
def _giant_buddha_niches(fills: list[Fill]) -> None:
    for t in range(GIANT_TIERS):
        r, y_base = _giant_tier(t)
        for face, axis, sign in _FACES:
            if axis == "z":
                b_x, b_z = GIANT_CX, GIANT_CZ + sign * r
                h_x, h_z = GIANT_CX, GIANT_CZ + sign * (r - 1)
            else:
                b_x, b_z = GIANT_CX + sign * r, GIANT_CZ
                h_x, h_z = GIANT_CX + sign * (r - 1), GIANT_CZ
            # Seated buddha: crossed-legs body + head (1x2, on the sill).
            add_fill(
                fills,
                f"pagodadetail giant buddha t{t} {face}",
                (b_x, y_base + 1, b_z),
                (b_x, y_base + 2, b_z),
                M.QUARTZ,
            )
            # Halo ring behind the statue: gold base, glowing centre.
            add_fill(
                fills,
                f"pagodadetail giant halo t{t} {face}",
                (h_x, y_base + 1, h_z),
                (h_x, y_base + 1, h_z),
                M.GOLD,
            )
            add_fill(
                fills,
                f"pagodadetail giant halo glow t{t} {face}",
                (h_x, y_base + 2, h_z),
                (h_x, y_base + 2, h_z),
                M.SEA_LANTERN,
            )


# ---------------------------------------------------------------------------
# Section 4: inscription tablets (铭砖) right of every giant south opening.
# ---------------------------------------------------------------------------
def _giant_inscription_tablets(fills: list[Fill]) -> None:
    for t in range(GIANT_TIERS):
        r, y_base = _giant_tier(t)
        hw = _opening_half_width(r)
        x0 = GIANT_CX + hw + 2  # right (east) of the south opening
        z = GIANT_CZ + r
        add_fill(
            fills,
            f"pagodadetail giant tablet t{t}",
            (x0, y_base + 2, z),
            (x0 + 1, y_base + 4, z),
            M.DARK,
        )
        # Three quartz "script" dots down the tablet.
        add_fill(
            fills,
            f"pagodadetail giant tablet dots t{t}",
            (x0, y_base + 2, z),
            (x0, y_base + 4, z),
            M.QUARTZ,
        )


# ---------------------------------------------------------------------------
# Section 2: 壶门 arched pseudo-doors on every small-pagoda face.
# ---------------------------------------------------------------------------
def _small_yaomen_doors(fills: list[Fill]) -> None:
    for t in range(SMALL_TIERS):
        r, y_base = _small_tier(t)
        hw = _opening_half_width(r)
        # Alternate the door position by one block per tier parity.
        u = hw + 3 + (t % 2)
        for face, axis, sign in _FACES:
            if axis == "z":
                d_x, d_z = SMALL_CX + u, SMALL_CZ + sign * r
                add_fill(
                    fills,
                    f"pagodadetail small yaomen t{t} {face}",
                    (d_x, y_base + 2, d_z),
                    (d_x, y_base + 3, d_z),
                    M.AIR,
                )
                add_fill(
                    fills,
                    f"pagodadetail small yaomen lintel t{t} {face}",
                    (d_x - 1, y_base + 4, d_z),
                    (d_x + 1, y_base + 4, d_z),
                    M.DARK,
                )
            else:
                d_x, d_z = SMALL_CX + sign * r, SMALL_CZ + u
                add_fill(
                    fills,
                    f"pagodadetail small yaomen t{t} {face}",
                    (d_x, y_base + 2, d_z),
                    (d_x, y_base + 3, d_z),
                    M.AIR,
                )
                add_fill(
                    fills,
                    f"pagodadetail small yaomen lintel t{t} {face}",
                    (d_x, y_base + 4, d_z - 1),
                    (d_x, y_base + 4, d_z + 1),
                    M.DARK,
                )


# ---------------------------------------------------------------------------
# Section 3: eave-end tiles (瓦当) on the outer slab ring of every eave.
# ---------------------------------------------------------------------------
def _eave_tiles(
    fills: list[Fill],
    prefix: str,
    cx: int,
    cz: int,
    tier_fn,
    tiers: int,
    tier_step: int,
    overhang: int,
    tier_height: int,
) -> None:
    """Dot one GOLD/QUARTZ tile per side onto each tier's outer slab ring.

    ring offset and height follow lib.add_pagoda_eave: outer = r + overhang,
    slab ring at outer+1 on y_eave+1. Tiles alternate gold/quartz around the
    ring; tier_step lets the dense small pagoda skip every other tier.
    """
    for t in range(0, tiers, tier_step):
        r, y_base = tier_fn(t)
        ring = r + overhang + 1
        y = y_base + tier_height + 1
        for i, (t_x, t_z) in enumerate(
            (
                (cx, cz - ring),
                (cx + ring, cz),
                (cx, cz + ring),
                (cx - ring, cz),
            )
        ):
            block = M.GOLD if i % 2 == 0 else M.QUARTZ
            add_fill(fills, f"{prefix} t{t} {i}", (t_x, y, t_z), (t_x, y, t_z), block)


# ---------------------------------------------------------------------------
# Section 5: finial chains (刹链) dropping to the top-tier eave corners.
# ---------------------------------------------------------------------------
def _giant_finial_chains(fills: list[Fill]) -> None:
    for sx, sz in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        # Steep links: down 2, outward 1 per level, from under the jewel.
        for i in range(10):
            x = GIANT_CX + sx * (GIANT_JEWEL_X0 + i)
            z = GIANT_CZ + sz * (GIANT_JEWEL_X0 + i)
            y = GIANT_CHAIN_TOP_Y - 2 * i
            add_fill(
                fills,
                f"pagodadetail giant chain {sx},{sz} drop {i}",
                (x, y, z),
                (x, y, z),
                M.IRON_BARS,
            )
        # Flat drape onto the tier-6 eave corner post.
        for j in range(12, GIANT_CORNER_OFF - 1):
            x = GIANT_CX + sx * j
            z = GIANT_CZ + sz * j
            add_fill(
                fills,
                f"pagodadetail giant chain {sx},{sz} drape {j}",
                (x, GIANT_DRAPE_Y, z),
                (x, GIANT_DRAPE_Y, z),
                M.IRON_BARS,
            )
        add_fill(
            fills,
            f"pagodadetail giant chain {sx},{sz} tip",
            (GIANT_CX + sx * (GIANT_CORNER_OFF - 1), GIANT_DRAPE_Y - 1,
             GIANT_CZ + sz * (GIANT_CORNER_OFF - 1)),
            (GIANT_CX + sx * (GIANT_CORNER_OFF - 1), GIANT_DRAPE_Y - 1,
             GIANT_CZ + sz * (GIANT_CORNER_OFF - 1)),
            M.IRON_BARS,
        )


def _small_finial_chains(fills: list[Fill]) -> None:
    for sx, sz in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        # Steep links: down 2, outward 1, from beside the finial jewel.
        for i in range(5):
            x = SMALL_CX + sx * (1 + i)
            z = SMALL_CZ + sz * (1 + i)
            y = SMALL_CHAIN_TOP_Y - 2 * i
            add_fill(
                fills,
                f"pagodadetail small chain {sx},{sz} drop {i}",
                (x, y, z),
                (x, y, z),
                M.IRON_BARS,
            )
        # Flat drape at the corner-post-top height (posts at +-14, 79..81).
        for j in range(6, 14):
            x = SMALL_CX + sx * j
            z = SMALL_CZ + sz * j
            add_fill(
                fills,
                f"pagodadetail small chain {sx},{sz} drape {j}",
                (x, SMALL_DRAPE_Y, z),
                (x, SMALL_DRAPE_Y, z),
                M.IRON_BARS,
            )


# ---------------------------------------------------------------------------
# Main entry point.
# ---------------------------------------------------------------------------
def build_pagoda_body_detail_3d(fills: list[Fill]) -> None:
    # 1. Giant: "雁塔圣教序" stele mural in the south ground-floor opening.
    _giant_stele_mural(fills)

    # 2. Giant: glowing Buddha + halo ensemble in every opening recess.
    _giant_buddha_niches(fills)

    # 3. Giant: inscription tablets beside the south openings.
    _giant_inscription_tablets(fills)

    # 4. Small: alternating 壶门 pseudo-doors on all thirteen storeys.
    _small_yaomen_doors(fills)

    # 5. Both towers: eave-end tiles on the outer eave slab rings.
    _eave_tiles(
        fills, "pagodadetail giant tile", GIANT_CX, GIANT_CZ, _giant_tier,
        GIANT_TIERS, 1, GIANT_EAVE_OVERHANG, GIANT_TIER_HEIGHT,
    )
    _eave_tiles(
        fills, "pagodadetail small tile", SMALL_CX, SMALL_CZ, _small_tier,
        SMALL_TIERS, 2, SMALL_EAVE_OVERHANG, SMALL_TIER_HEIGHT,
    )

    # 6. Both towers: finial chains sagging to the top-tier eave corners.
    _giant_finial_chains(fills)
    _small_finial_chains(fills)


def main() -> None:
    run_builder(build_pagoda_body_detail_3d, "pagoda_body_detail_3d")


if __name__ == "__main__":
    main()
