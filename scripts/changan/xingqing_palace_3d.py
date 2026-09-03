from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    Fill,
    Materials as M,
    add_arch_bridge,
    add_cantilevered_floor,
    add_fill,
    add_hip_roof,
    add_hollow_box,
    add_outline,
    add_pagoda_eave,
    add_pool,
    add_pyramid_roof,
    add_ridge_roof,
    add_spiral_stair,
    add_staircase,
    run_builder,
)


"""
Xingqing Palace 3D (兴庆宫花萼相辉楼·沉香亭) - deepened overlay pass for
the two most famous structures of Tang Xingqing Palace on Longqing Pool.

Location in Chang'an city local coordinates:
    Xingqing Palace: x 900..1700, z 800..1600 (palace_xingqing.py).
    Longqing Pool (龙池): x 1100..1500, z 1050..1350, water surface y=2.
    Hua'e Xianghui Pavilion (花萼相辉楼): centred (1120, 1280) on the
    south-west shore of the pool, standing partly over the water.
    Chenxiang Pavilion (沉香亭): centred (1300, 1030) in a shallow basin
    off the pool's north shore.

3D features:
    - Stone platform on visible stone piles carrying a two-storey pavilion,
      each storey with red walls, dark-oak edge columns and a cantilevered
      balcony gallery with fence railings
    - Double roofs: a lower eave ring (重檐) plus a gilded hip roof (庑殿顶)
    - Interior spiral stair linking both storeys
    - Covered flying corridor (飞廊) on timber piles crossing the water
      westward to the shore, with a stone stair down to the bank
    - Square Chenxiang Pavilion on piles in shallow water: four red
      columns, a pyramid roof (攒尖顶) with a gold apex, four geometric
      peony beds (牡丹花坛) and an L-shaped arch bridge from the north bank
    - Reflection colonnade along the pool's north edge: quartz columns
      every 6 blocks on a low stone base with a slab cap
"""

# Longqing Pool bounds (from palace_xingqing.py); water surface at y=2.
POOL_X1, POOL_Z1 = 1100, 1050
POOL_X2, POOL_Z2 = 1500, 1350

# Hua'e Xianghui Pavilion centre and footprint (36 x 28).
HE_CX, HE_CZ = 1120, 1280
HE_X1, HE_Z1 = 1102, 1266
HE_X2, HE_Z2 = 1137, 1293

# Chenxiang Pavilion centre; square platform radius 10.
CX_CX, CX_CZ = 1300, 1030
CX_X1, CX_Z1 = 1290, 1020
CX_X2, CX_Z2 = 1310, 1040


def _edge_columns(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y1: int, y2: int,
) -> None:
    """Dark-oak columns on the four corners and edge midpoints of a storey."""
    mx, mz = (x1 + x2) // 2, (z1 + z2) // 2
    posts = [
        (x1, z1), (x2 - 1, z1), (x1, z2 - 1), (x2 - 1, z2 - 1),
        (mx - 1, z1), (mx - 1, z2 - 1),
        (x1, mz - 1), (x2 - 1, mz - 1),
    ]
    for i, (px, pz) in enumerate(posts):
        add_fill(fills, f"{label} col {i}", (px, y1, pz), (px + 1, y2, pz + 1), M.LOG)


def _peony_bed(fills: list[Fill], label: str, cx: int, cz: int) -> None:
    """One geometric peony bed: grass base, leaves border, striped flowers."""
    add_fill(fills, f"{label} base", (cx - 3, 2, cz - 3), (cx + 3, 2, cz + 3), M.GRASS)
    add_outline(fills, f"{label} border", cx - 3, cz - 3, cx + 3, cz + 3, 3, 3, M.LEAVES, thickness=1)
    for dz in range(-2, 3):
        block = M.PINK_WOOL if dz % 2 == 0 else M.RED_WOOL
        add_fill(fills, f"{label} peony {dz}", (cx - 2, 3, cz + dz), (cx + 2, 3, cz + dz), block)


def build_xingqing_palace_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Hua'e Xianghui Pavilion (花萼相辉楼): platform and piles.
    # ------------------------------------------------------------------
    # Stone piles rising from the pool floor (y 0-1) through the water (y 2).
    for px in (1100, 1112, 1124, 1136):
        for pz in (1268, 1280, 1292):
            add_fill(fills, f"huae pile {px},{pz}", (px, 0, pz), (px + 1, 3, pz + 1), M.STONE)
    # Stone platform (~3 high) extending over the pool's west edge.
    add_fill(fills, "huae platform", (1098, 4, 1262), (1142, 6, 1298), M.STONE)

    # ------------------------------------------------------------------
    # 2. Flying corridor (飞廊) westward over the water to the shore.
    #    Built before the pavilion walls/eaves so their fills stay intact.
    # ------------------------------------------------------------------
    add_fill(fills, "huae corridor floor", (1086, 7, 1277), (1101, 7, 1283), M.WOOD)
    add_fill(fills, "huae corridor rail n", (1086, 8, 1277), (1101, 8, 1277), M.FENCE)
    add_fill(fills, "huae corridor rail s", (1086, 8, 1283), (1101, 8, 1283), M.FENCE)
    # Timber piles under the corridor, down to the pool floor.
    for px in (1090, 1096):
        for pz in (1278, 1282):
            add_fill(fills, f"huae corridor pile {px},{pz}", (px, 0, pz), (px + 1, 6, pz + 1), M.LOG)
    # Slim roof posts at the corridor corners.
    for px in (1087, 1100):
        for pz in (1277, 1283):
            add_fill(fills, f"huae corridor post {px},{pz}", (px, 8, pz), (px, 11, pz), M.LOG)
    add_ridge_roof(fills, "huae corridor roof", 1085, 1276, 1100, 1284, 12, layers=2, ridge_axis="x")
    # Stone stair from the corridor deck down to the west bank.
    add_fill(fills, "huae bank landing", (1075, 2, 1277), (1080, 2, 1283), M.STONE)
    add_staircase(fills, "huae bank steps", 1080, 1278, 1086, 1282, 2, 7, "east", block=M.STONE)

    # ------------------------------------------------------------------
    # 3. Storey 1 (y 7-15): red walls, edge columns, doors, gallery.
    # ------------------------------------------------------------------
    add_hollow_box(fills, "huae storey1", HE_X1, 7, HE_Z1, HE_X2, 15, HE_Z2, M.RED_WALL, thickness=1)
    _edge_columns(fills, "huae storey1", HE_X1, HE_Z1, HE_X2, HE_Z2, 7, 15)
    # Doorways on the west (corridor) and east faces.
    add_fill(fills, "huae door west", (HE_X1, 8, 1278), (HE_X1, 11, 1282), M.AIR)
    add_fill(fills, "huae door east", (HE_X2, 8, 1278), (HE_X2, 11, 1282), M.AIR)
    add_cantilevered_floor(fills, "huae gallery1", HE_X1, HE_Z1, HE_X2, HE_Z2, y=16, overhang=3, block=M.WOOD)
    add_outline(fills, "huae rail1", 1099, 1263, 1140, 1296, 17, 17, M.FENCE, thickness=1)

    # ------------------------------------------------------------------
    # 4. Lower eave ring (重檐) above the first gallery.
    # ------------------------------------------------------------------
    add_pagoda_eave(fills, "huae lower eave", HE_CX, HE_CZ, radius=18, y=18, overhang=3, roof_block=M.ROOF_GREEN)

    # ------------------------------------------------------------------
    # 5. Storey 2 (y 19-27), its balcony gallery, and the hip roof (庑殿顶).
    # ------------------------------------------------------------------
    add_hollow_box(fills, "huae storey2", HE_X1, 19, HE_Z1, HE_X2, 27, HE_Z2, M.RED_WALL, thickness=1)
    _edge_columns(fills, "huae storey2", HE_X1, HE_Z1, HE_X2, HE_Z2, 19, 27)
    add_cantilevered_floor(fills, "huae gallery2", HE_X1, HE_Z1, HE_X2, HE_Z2, y=28, overhang=3, block=M.WOOD)
    add_outline(fills, "huae rail2", 1099, 1263, 1140, 1296, 29, 29, M.FENCE, thickness=1)
    add_hip_roof(fills, "huae hip roof", 1099, 1263, 1140, 1296, y=30, layers=7, ridge_axis="x", roof_block=M.ROOF_GREEN)

    # Interior spiral stair linking both storeys.
    add_spiral_stair(fills, "huae stair1", HE_CX, HE_CZ, radius=5, y1=8, y2=15, block=M.SMOOTH)
    add_spiral_stair(fills, "huae stair2", HE_CX, HE_CZ, radius=5, y1=20, y2=26, block=M.SMOOTH)

    # ------------------------------------------------------------------
    # 6. Chenxiang Pavilion (沉香亭): shallow basin, piles, platform.
    # ------------------------------------------------------------------
    add_pool(fills, "chenxiang basin", 1287, 1017, 1313, 1043, 2, depth=1)
    for px in (1292, 1299, 1306):
        for pz in (1022, 1036):
            add_fill(fills, f"chenxiang pile {px},{pz}", (px, 1, pz), (px + 1, 3, pz + 1), M.STONE)
    for pz in (1029,):
        for px in (1292, 1306):
            add_fill(fills, f"chenxiang pile {px},{pz}", (px, 1, pz), (px + 1, 3, pz + 1), M.STONE)
    add_fill(fills, "chenxiang platform", (CX_X1, 3, CX_Z1), (CX_X2, 4, CX_Z2), M.STONE)
    # Fence railing on three sides; the north side stays open for the bridge.
    add_fill(fills, "chenxiang rail s", (CX_X1, 5, CX_Z2), (CX_X2, 5, CX_Z2), M.FENCE)
    add_fill(fills, "chenxiang rail w", (CX_X1, 5, CX_Z1), (CX_X1, 5, CX_Z2), M.FENCE)
    add_fill(fills, "chenxiang rail e", (CX_X2, 5, CX_Z1), (CX_X2, 5, CX_Z2), M.FENCE)

    # Four red columns and the pyramid roof (攒尖顶) with a gold apex.
    for px in (1293, 1305):
        for pz in (1023, 1035):
            add_fill(fills, f"chenxiang column {px},{pz}", (px, 5, pz), (px + 1, 12, pz + 1), M.RED_WALL)
    add_pyramid_roof(fills, "chenxiang roof", CX_CX, CX_CZ, radius=12, y=13, roof_block=M.ROOF_GREEN, apex_block=M.GOLD)

    # L-shaped arch bridge from the north bank (two straight segments).
    add_arch_bridge(fills, "chenxiang bridge a", 1292, 1006, 1292, 1024, y=4, span=6, height=3, block=M.STONE)
    add_arch_bridge(fills, "chenxiang bridge b", 1292, 1024, 1300, 1024, y=4, span=6, height=3, block=M.STONE)

    # Four geometric peony beds (牡丹花坛) around the pavilion.
    for i, (bx, bz) in enumerate([(1281, 1012), (1319, 1012), (1281, 1042), (1319, 1042)]):
        _peony_bed(fills, f"peony bed {i}", bx, bz)

    # ------------------------------------------------------------------
    # 7. Reflection colonnade along the pool's north edge.
    # ------------------------------------------------------------------
    add_fill(fills, "colonnade base", (1120, 2, 1046), (1480, 3, 1049), M.STONE)
    for cx in range(1122, 1479, 6):
        add_fill(fills, f"colonnade col n {cx}", (cx, 4, 1046), (cx, 8, 1046), M.QUARTZ)
        add_fill(fills, f"colonnade col s {cx}", (cx, 4, 1049), (cx, 8, 1049), M.QUARTZ)
    add_fill(
        fills, "colonnade cap",
        (1120, 9, 1046), (1480, 9, 1049),
        "minecraft:smooth_stone_slab[type=bottom,waterlogged=false]",
    )


def main() -> None:
    run_builder(build_xingqing_palace_3d, "xingqing_palace_3d")


if __name__ == "__main__":
    main()
