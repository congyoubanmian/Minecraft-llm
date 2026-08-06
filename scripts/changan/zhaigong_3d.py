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
    add_hollow_box,
    add_outline,
    add_pool,
    add_ridge_roof,
    add_tree,
    run_builder,
)


"""
Zhai Palace 3D (斋宫) - the fasting palace where the emperor purified
himself before the heaven-worship ceremony at the Round Altar (圜丘).

A walled ritual compound east of the altar: gate court, two-storey
abstinence hall, bronze-man pavilion (铜人亭, holding the tablet that
reminded the emperor of the fast), side halls, well, and a quiet garden.

Location in Chang'an city local coordinates:
    x 3350..3560, z -1420..-1180 (east of the Round Altar at
    (3000, -1300), whose outer enclosure ends at x=3132).

3D features:
    - Self-levelling base platform (raw suburban terrain)
    - Double courtyard walls with a three-bay south gate
    - Two-storey abstinence hall (斋戒殿) with an upper fasting chamber
    - Bronze-man pavilion with the standing bronze figure
    - Side halls on raised terraces linked by covered walkways
    - Well pavilion, garden pond, and lantern-lined processional path
"""

X1, Z1 = 3350, -1420
X2, Z2 = 3560, -1180
CX = (X1 + X2) // 2


def build_zhaigong_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 0. Self-levelling base platform.
    # ------------------------------------------------------------------
    add_fill(fills, "zhaigong clear", (X1 - 10, 1, Z1 - 10), (X2 + 10, 50, Z2 + 10), M.AIR)
    add_fill(fills, "zhaigong base", (X1 - 10, 0, Z1 - 10), (X2 + 10, 1, Z2 + 10), M.GRASS)

    # ------------------------------------------------------------------
    # 1. Enclosure walls + three-bay south gate.
    # ------------------------------------------------------------------
    add_outline(fills, "zhaigong wall n", X1, Z1, X2, Z1, 1, 8, M.RED_WALL, thickness=2)
    add_outline(fills, "zhaigong wall s", X1, Z2, X2, Z2, 1, 8, M.RED_WALL, thickness=2)
    add_outline(fills, "zhaigong wall w", X1, Z1, X1, Z2, 1, 8, M.RED_WALL, thickness=2)
    add_outline(fills, "zhaigong wall e", X2, Z1, X2, Z2, 1, 8, M.RED_WALL, thickness=2)
    # South gate (toward +z, facing the altar road)
    gz = Z2
    add_fill(fills, "zhaigong gate opening", (CX - 12, 1, gz - 1), (CX + 12, 7, gz + 1), M.AIR)
    for dx in (-14, -6, 6, 14):
        add_fill(fills, f"zhaigong gate pillar {dx}", (CX + dx, 1, gz - 2), (CX + dx + 2, 12, gz + 2), M.RED_WALL_ALT)
    add_fill(fills, "zhaigong gate roof", (CX - 18, 13, gz - 5), (CX + 18, 14, gz + 5), M.ROOF_GREEN)
    add_fill(fills, "zhaigong gate ridge", (CX - 2, 15, gz - 1), (CX + 2, 16, gz + 1), M.GOLD)

    # ------------------------------------------------------------------
    # 2. Two-storey abstinence hall (斋戒殿) on a raised terrace.
    # ------------------------------------------------------------------
    hx1, hz1 = CX - 50, Z1 + 40
    hx2, hz2 = CX + 50, Z1 + 100
    add_fill(fills, "zhaigong hall terrace", (hx1 - 8, 1, hz1 - 8), (hx2 + 8, 4, hz2 + 8), M.STONE)
    add_outline(fills, "zhaigong hall rail", hx1 - 8, hz1 - 8, hx2 + 8, hz2 + 8, 5, 5, M.QUARTZ, thickness=1)
    add_hollow_box(fills, "zhaigong hall low", hx1, 5, hz1, hx2, 16, hz2, M.RED_WALL, thickness=2)
    add_fill(fills, "zhaigong hall floor2", (hx1 + 1, 16, hz1 + 1), (hx2 - 1, 16, hz2 - 1), M.WOOD)
    add_hollow_box(fills, "zhaigong hall up", hx1 + 6, 17, hz1 + 6, hx2 - 6, 26, hz2 - 6, M.RED_WALL, thickness=2)
    add_ridge_roof(fills, "zhaigong hall roof", hx1 - 4, hz1 - 4, hx2 + 4, hz2 + 4, 27, layers=4, ridge_axis="x")
    # Fasting chamber fittings on the upper floor: mat platform + screen
    add_fill(fills, "zhaigong mat platform", (CX - 8, 17, hz1 + 12), (CX + 8, 18, hz1 + 24), M.WHITE_WOOL)
    add_fill(fills, "zhaigong screen", (CX - 6, 17, hz1 + 28), (CX + 6, 22, hz1 + 29), M.WOOD)
    # Internal stair to the upper floor
    for i in range(11):
        add_fill(fills, f"zhaigong hall stair {i}", (hx1 + 3 + i, 5 + i, hz2 - 4), (hx1 + 4 + i, 5 + i, hz2 - 2), M.SMOOTH)
    # Terrace stairs on the south side
    for i in range(4):
        add_fill(fills, f"zhaigong terrace stair {i}", (CX - 6, 1 + i, hz1 - 12 + i), (CX + 6, 1 + i, hz1 - 11 + i), M.SMOOTH)

    # ------------------------------------------------------------------
    # 3. Bronze-man pavilion (铜人亭) in the front court.
    # ------------------------------------------------------------------
    bx, bz = CX, Z1 + 130
    for dx in (-5, 5):
        for dz in (-5, 5):
            add_fill(fills, f"zhaigong bronze pavilion post {dx},{dz}", (bx + dx, 1, bz + dz), (bx + dx, 9, bz + dz), M.LOG)
    add_fill(fills, "zhaigong bronze pavilion roof", (bx - 8, 10, bz - 8), (bx + 8, 11, bz + 8), M.ROOF_GREEN)
    add_fill(fills, "zhaigong bronze pavilion finial", (bx - 1, 12, bz - 1), (bx + 1, 14, bz + 1), M.GOLD)
    # Standing bronze figure holding the fasting tablet
    add_fill(fills, "zhaigong bronze base", (bx - 2, 1, bz - 2), (bx + 2, 2, bz + 2), M.DARK)
    add_fill(fills, "zhaigong bronze legs", (bx - 1, 3, bz - 1), (bx + 1, 5, bz + 1), M.GOLD_ACCENT)
    add_fill(fills, "zhaigong bronze body", (bx - 1, 6, bz - 1), (bx + 1, 7, bz + 1), M.GOLD_ACCENT)
    add_fill(fills, "zhaigong bronze tablet", (bx, 6, bz - 2), (bx, 8, bz - 2), M.QUARTZ)

    # ------------------------------------------------------------------
    # 4. Side halls on terraces + covered walkways.
    # ------------------------------------------------------------------
    for side, sx1, sx2 in [("west", X1 + 20, X1 + 60), ("east", X2 - 60, X2 - 20)]:
        sz1, sz2 = Z1 + 50, Z1 + 90
        add_fill(fills, f"zhaigong {side} terrace", (sx1 - 4, 1, sz1 - 4), (sx2 + 4, 2, sz2 + 4), M.STONE)
        add_hollow_box(fills, f"zhaigong {side} hall", sx1, 3, sz1, sx2, 12, sz2, M.RED_WALL, thickness=1)
        add_ridge_roof(fills, f"zhaigong {side} roof", sx1 - 3, sz1 - 3, sx2 + 3, sz2 + 3, 13, layers=2, ridge_axis="z")
        # Covered walkway from the side hall to the main hall terrace
        wx1 = sx2 if side == "west" else hx1 - 8
        wx2 = hx1 - 8 if side == "west" else sx1
        add_fill(fills, f"zhaigong {side} walkway floor", (min(wx1, wx2), 3, sz1 + 16), (max(wx1, wx2), 3, sz1 + 22), M.WOOD)
        for x in range(min(wx1, wx2) + 4, max(wx1, wx2), 12):
            add_fill(fills, f"zhaigong {side} walkway col {x}", (x, 3, sz1 + 16), (x + 1, 9, sz1 + 17), M.LOG)
            add_fill(fills, f"zhaigong {side} walkway col b {x}", (x, 3, sz1 + 21), (x + 1, 9, sz1 + 22), M.LOG)
        add_fill(fills, f"zhaigong {side} walkway roof", (min(wx1, wx2) - 2, 10, sz1 + 14), (max(wx1, wx2) + 2, 11, sz1 + 24), M.ROOF_GREEN)

    # ------------------------------------------------------------------
    # 5. Well pavilion, garden pond, processional path, lanterns.
    # ------------------------------------------------------------------
    wx, wz = CX - 80, Z1 + 140
    add_fill(fills, "zhaigong well rim", (wx - 3, 1, wz - 3), (wx + 3, 2, wz + 3), M.STONE)
    add_fill(fills, "zhaigong well water", (wx - 2, 1, wz - 2), (wx + 2, 1, wz + 2), M.WATER)
    for dx in (-4, 4):
        for dz in (-4, 4):
            add_fill(fills, f"zhaigong well post {dx},{dz}", (wx + dx, 1, wz + dz), (wx + dx, 7, wz + dz), M.LOG)
    add_fill(fills, "zhaigong well roof", (wx - 6, 8, wz - 6), (wx + 6, 9, wz + 6), M.ROOF_GREEN)

    add_pool(fills, "zhaigong pond", CX + 60, Z1 + 130, CX + 90, Z1 + 160, 2)
    for i, (tx, tz) in enumerate([(CX + 70, Z1 + 120), (CX + 95, Z1 + 145), (CX + 60, Z1 + 165)]):
        add_tree(fills, f"zhaigong tree {i}", tx, tz, 2)

    # Processional path from the gate to the hall terrace
    add_fill(fills, "zhaigong path", (CX - 4, 1, hz2 + 9), (CX + 4, 1, Z2 - 4), M.SMOOTH)
    for i, z in enumerate(range(hz2 + 20, Z2 - 10, 20)):
        for sx in (-1, 1):
            x = CX + sx * 8
            add_fill(fills, f"zhaigong path post {i} {sx}", (x, 1, z), (x, 6, z), M.LOG)
            add_fill(fills, f"zhaigong path lantern {i} {sx}", (x, 7, z), (x, 7, z), M.LANTERN)


def main() -> None:
    run_builder(build_zhaigong_3d, "zhaigong_3d")


if __name__ == "__main__":
    main()
