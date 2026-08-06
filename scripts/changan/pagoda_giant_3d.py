from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    Fill,
    Materials as M,
    add_cantilevered_floor,
    add_dougong_cluster,
    add_fill,
    add_outline,
    add_spiral_stair,
    add_underground_room,
    run_builder,
)


"""
Giant Wild Goose Pagoda 3D enhancement (大雁塔 3D 强化).

Overlays the base pagoda_giant module with true vertical/3D detail:
    - Underground reliquary palace (地宫) below the tower with a gold
      relic stupa and a descending entry stair from the courtyard
    - Interior spiral staircase climbing every storey (use the new
      add_spiral_stair primitive) instead of a hollow shaft
    - Cantilevered wooden gallery around every storey (平座回廊)
      with fence balustrades
    - Dougong bracket clusters under each eave corner
    - Segmented finial (塔刹分节) replacing the plain gold rod:
      stacked rings, a slender mast, and a top jewel
    - Corner wind bells (檐角风铃) hanging from every eave

Coordinates match pagoda_giant.py: center (4580, 3860).
Tier geometry matches the base module exactly so galleries and stairs
line up with the existing body:
    tier t (0..6): r = 44 - 4t, y_base = 1 + 12t, body height 10.
"""

CX = 4580
CZ = 3860

TIERS = 7
TIER_HEIGHT = 10
TIER_STEP = 12


def _tier(t: int) -> tuple[int, int]:
    return 44 - t * 4, 1 + t * TIER_STEP


def build_giant_pagoda_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Underground reliquary palace (地宫) under the tower base.
    # ------------------------------------------------------------------
    gx1, gz1 = CX - 14, CZ - 14
    gx2, gz2 = CX + 14, CZ + 14
    add_underground_room(fills, "pagoda crypt", gx1, gz1, gx2, gz2, y_floor=-8, y_ceiling=-2, block=M.STONE)
    # Central gold relic stupa
    add_fill(fills, "crypt stupa base", (CX - 3, -8, CZ - 3), (CX + 3, -7, CZ + 3), M.GOLD_ACCENT)
    add_fill(fills, "crypt stupa body", (CX - 2, -6, CZ - 2), (CX + 2, -4, CZ + 2), M.GOLD)
    add_fill(fills, "crypt stupa jewel", (CX - 1, -3, CZ - 1), (CX + 1, -2, CZ + 1), M.SEA_LANTERN)
    # Offering altars along the walls
    for dx, dz in [(-10, 0), (10, 0), (0, -10), (0, 10)]:
        add_fill(fills, f"crypt altar {dx},{dz}", (CX + dx - 1, -8, CZ + dz - 1), (CX + dx + 1, -7, CZ + dz + 1), M.QUARTZ)
        add_fill(fills, f"crypt lamp {dx},{dz}", (CX + dx, -6, CZ + dz), (CX + dx, -6, CZ + dz), M.LANTERN)
    # Descending entry stair: open shaft on the south side of the base,
    # stepping down from courtyard level (y=1) to the crypt floor (y=-7).
    for i in range(9):
        z = CZ - 46 + i * 2
        y = 1 - i
        add_fill(fills, f"crypt stair {i}", (CX - 2, y, z), (CX + 2, y, z + 1), M.SMOOTH)
        add_fill(fills, f"crypt stair clear {i}", (CX - 2, y + 1, z), (CX + 2, y + 4, z + 1), M.AIR)
    # Connect shaft bottom to crypt north wall
    add_fill(fills, "crypt stair tunnel", (CX - 2, -8, gz2 + 1), (CX + 2, -4, CZ - 46 + 18), M.AIR)

    # ------------------------------------------------------------------
    # 2. Per-storey 3D detail: galleries, spiral stairs, dougong, bells.
    # ------------------------------------------------------------------
    for t in range(TIERS):
        r, y_base = _tier(t)
        y_floor = y_base + TIER_HEIGHT - 1  # storey floor plate level
        y_eave = y_base + TIER_HEIGHT       # eave level from base module

        # Cantilevered gallery (平座): slab rings the body outside the wall.
        add_cantilevered_floor(
            fills, f"pagoda gallery t{t}",
            CX - r, CZ - r, CX + r, CZ + r,
            y=y_floor, overhang=4, block=M.WOOD, support_block=M.LOG,
        )
        # Balustrade around the gallery edge
        add_outline(
            fills, f"pagoda balustrade t{t}",
            CX - r - 4, CZ - r - 4, CX + r + 4, CZ + r + 4,
            y_floor + 1, y_floor + 1, M.FENCE, thickness=1,
        )

        # Interior spiral stair climbing this storey (skip top tier: too small).
        if r >= 12:
            add_spiral_stair(
                fills, f"pagoda stair t{t}",
                CX, CZ, radius=max(6, r - 6),
                y1=y_base + 1, y2=y_floor, block=M.SMOOTH,
            )

        # Dougong clusters under each eave corner
        for sx in (-1, 1):
            for sz in (-1, 1):
                add_dougong_cluster(
                    fills, f"pagoda dougong t{t} {sx},{sz}",
                    CX + sx * r, CZ + sz * r, y=y_eave, tiers=2, block=M.WOOD,
                )

        # Wind bells hanging from the four eave corners
        for sx in (-1, 1):
            for sz in (-1, 1):
                add_fill(
                    fills, f"pagoda bell t{t} {sx},{sz}",
                    (CX + sx * (r + 5), y_eave - 1, CZ + sz * (r + 5)),
                    (CX + sx * (r + 5), y_eave - 1, CZ + sz * (r + 5)),
                    M.GOLD,
                )

    # ------------------------------------------------------------------
    # 3. Segmented finial (塔刹) replacing the base module's solid gold rod.
    # ------------------------------------------------------------------
    y_top = 1 + TIER_STEP * TIERS  # = 85, where the base spire starts
    # Clear the old rod
    add_fill(fills, "spire clear old", (CX - 3, y_top, CZ - 3), (CX + 3, y_top + 23, CZ + 3), M.AIR)
    # Finial base (覆钵) sitting on the roof
    add_fill(fills, "finial bowl", (CX - 4, y_top, CZ - 4), (CX + 4, y_top + 2, CZ + 4), M.GOLD_ACCENT)
    # Stacked rings (相轮): seven rings shrinking upward on a slender mast
    add_fill(fills, "finial mast", (CX - 1, y_top + 3, CZ - 1), (CX + 1, y_top + 20, CZ + 1), M.GOLD)
    for i in range(7):
        ring_r = max(2, 4 - i // 2)
        y = y_top + 4 + i * 2
        add_fill(fills, f"finial ring {i}", (CX - ring_r, y, CZ - ring_r), (CX + ring_r, y, CZ + ring_r), M.GOLD)
    # Top jewel (宝珠)
    add_fill(fills, "finial jewel", (CX - 2, y_top + 21, CZ - 2), (CX + 2, y_top + 23, CZ + 2), M.SEA_LANTERN)

    # ------------------------------------------------------------------
    # 4. Temple courtyard 3D extras: stele pavilions and lantern posts.
    # ------------------------------------------------------------------
    wall_min_z = CZ - 100
    for sx in (-1, 1):
        px = CX + sx * 60
        pz = wall_min_z + 50
        # Stone stele on a tortoise base, sheltered by four posts + roof slab
        add_fill(fills, f"stele base {sx}", (px - 2, 1, pz - 1), (px + 2, 2, pz + 1), M.MOSS_STONE)
        add_fill(fills, f"stele tablet {sx}", (px - 1, 3, pz), (px + 1, 9, pz), M.DARK)
        for ox in (-4, 4):
            for oz in (-4, 4):
                add_fill(fills, f"stele post {sx} {ox},{oz}", (px + ox, 1, pz + oz), (px + ox, 11, pz + oz), M.LOG)
        add_fill(fills, f"stele roof {sx}", (px - 6, 12, pz - 6), (px + 6, 13, pz + 6), M.ROOF_GREEN)
    # Lantern posts lining the approach from the temple gate
    for i in range(4):
        z = wall_min_z + 10 + i * 8
        for sx in (-1, 1):
            x = CX + sx * 10
            add_fill(fills, f"approach post {i} {sx}", (x, 1, z), (x, 6, z), M.LOG)
            add_fill(fills, f"approach lantern {i} {sx}", (x, 7, z), (x, 7, z), M.LANTERN)


def main() -> None:
    run_builder(build_giant_pagoda_3d, "pagoda_giant_3d")


if __name__ == "__main__":
    main()
