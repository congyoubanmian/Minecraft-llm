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
    add_fill,
    add_hip_roof,
    add_hollow_box,
    add_lantern_line,
    add_outline,
    add_pagoda_eave,
    add_pool,
    add_pyramid_roof,
    add_ridge_roof,
    add_spiral_stair,
    run_builder,
)


"""
Fuyong Garden 3D (芙蓉园·紫云楼) - the imperial forbidden garden on the
south shore of Qujiang Pool, best known for the Purple Cloud Tower
(紫云楼) where Tang emperors feasted while commoners watched from
outside the garden wall.

Location in Chang'an city local coordinates:
    Qujiang Pool water (qujiang_pool_3d): x 5060..5940, z 5320..5920.
    This module wraps the pool's south shore strip: x 5150..5850,
    z 5935..6075 (north suburb farms start at z 6080).

Distinctive features:
    - Purple Cloud Tower standing on stone piles at the water's edge,
      with a cantilevered imperial viewing terrace projecting OVER the
      pool water, double eaves and a green hip roof
    - Officials' tent gallery (百官幕次): alternating red/yellow wool
      tent roofs on timber posts along the shore
    - A lotus pond basin west of the tower, planted with lily pads and
      flowering lotus islets, crossed by a zigzag nine-curve bridge
    - A garden wall with a moon gate sealing the forbidden garden
    - Banquet lantern line lighting the whole waterfront
"""

TOWER_X1, TOWER_Z1 = 5560, 5960
TOWER_X2, TOWER_Z2 = 5840, 6040
LOTUS_X1, LOTUS_Z1 = 5170, 5945
LOTUS_X2, LOTUS_Z2 = 5420, 5995
GALLERY_X1, GALLERY_Z1 = 5160, 6000
GALLERY_X2, GALLERY_Z2 = 5520, 6070


def _edge_columns(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y1: int, y2: int,
) -> None:
    mx, mz = (x1 + x2) // 2, (z1 + z2) // 2
    posts = [
        (x1, z1), (x2 - 1, z1), (x1, z2 - 1), (x2 - 1, z2 - 1),
        (mx - 1, z1), (mx - 1, z2 - 1),
        (x1, mz - 1), (x2 - 1, mz - 1),
    ]
    for i, (px, pz) in enumerate(posts):
        add_fill(fills, f"{label} col {i}", (px, y1, pz), (px + 1, y2, pz + 1), M.LOG)


def build_fuyong_yuan_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Foundation platform levelling the shore strip.
    # ------------------------------------------------------------------
    add_fill(fills, "fuyong foundation", (5150, 0, 5935), (5850, 3, 6075), M.STONE)
    add_fill(fills, "fuyong lawn", (5150, 4, 5935), (5850, 4, 6075), M.GRASS)

    # ------------------------------------------------------------------
    # 2. Purple Cloud Tower (紫云楼): piles at the water's edge, the
    #    north face standing over the pool water.
    # ------------------------------------------------------------------
    for px in (5568, 5596, 5624, 5652, 5680, 5708, 5736, 5764, 5792, 5820):
        for pz in (5964, 5976, 5988, 6000, 6012, 6024, 6036):
            add_fill(fills, f"ziyun pile {px},{pz}", (px, 0, pz), (px + 1, 4, pz + 1), M.STONE)
    # Cantilevered imperial viewing terrace projecting north OVER the water.
    add_fill(fills, "ziyun water terrace", (5620, 4, 5946), (5780, 4, 5962), M.WOOD)
    add_outline(fills, "ziyun water rail", 5620, 5946, 5780, 5962, 5, 5, M.FENCE, thickness=1)
    for px in (5626, 5660, 5694, 5728, 5762):
        for pz in (5948, 5960):
            add_fill(fills, f"ziyun terrace brace {px},{pz}", (px, 2, pz), (px + 1, 3, pz + 1), M.LOG)

    # ------------------------------------------------------------------
    # 3. Storey 1 (y 5..14): red walls, doors to terrace and lawn.
    # ------------------------------------------------------------------
    add_hollow_box(fills, "ziyun storey1", TOWER_X1, 5, TOWER_Z1, TOWER_X2, 14, TOWER_Z2, M.RED_WALL, thickness=1)
    _edge_columns(fills, "ziyun storey1", TOWER_X1, TOWER_Z1, TOWER_X2, TOWER_Z2, 5, 14)
    add_fill(fills, "ziyun door north", (5660, 6, TOWER_Z1), (5700, 11, TOWER_Z1), M.AIR)
    add_fill(fills, "ziyun door south", (5660, 6, TOWER_Z2), (5700, 11, TOWER_Z2), M.AIR)
    add_fill(fills, "ziyun windows west", (TOWER_X1, 8, 5975), (TOWER_X1, 11, 6025), M.GLASS)
    add_fill(fills, "ziyun windows east", (TOWER_X2, 8, 5975), (TOWER_X2, 11, 6025), M.GLASS)
    add_cantilevered_floor(fills, "ziyun gallery1", TOWER_X1, TOWER_Z1, TOWER_X2, TOWER_Z2, y=15, overhang=3, block=M.WOOD)
    add_outline(fills, "ziyun rail1", TOWER_X1 - 3, TOWER_Z1 - 3, TOWER_X2 + 3, TOWER_Z2 + 3, 16, 16, M.FENCE, thickness=1)

    # ------------------------------------------------------------------
    # 4. Lower eave ring + storey 2 (y 17..25) + hip roof.
    # ------------------------------------------------------------------
    add_pagoda_eave(fills, "ziyun lower eave", (TOWER_X1 + TOWER_X2) // 2, (TOWER_Z1 + TOWER_Z2) // 2, radius=26, y=17, overhang=3, roof_block=M.ROOF_GREEN)
    add_hollow_box(fills, "ziyun storey2", TOWER_X1, 18, TOWER_Z1, TOWER_X2, 25, TOWER_Z2, M.RED_WALL, thickness=1)
    _edge_columns(fills, "ziyun storey2", TOWER_X1, TOWER_Z1, TOWER_X2, TOWER_Z2, 18, 25)
    add_cantilevered_floor(fills, "ziyun gallery2", TOWER_X1, TOWER_Z1, TOWER_X2, TOWER_Z2, y=26, overhang=3, block=M.WOOD)
    add_outline(fills, "ziyun rail2", TOWER_X1 - 3, TOWER_Z1 - 3, TOWER_X2 + 3, TOWER_Z2 + 3, 27, 27, M.FENCE, thickness=1)
    add_hip_roof(fills, "ziyun hip roof", TOWER_X1 - 3, TOWER_Z1 - 3, TOWER_X2 + 3, TOWER_Z2 + 3, y=28, layers=8, ridge_axis="x", roof_block=M.ROOF_GREEN)
    add_spiral_stair(fills, "ziyun stair1", 5700, 6000, radius=6, y1=6, y2=14, block=M.SMOOTH)
    add_spiral_stair(fills, "ziyun stair2", 5700, 6000, radius=6, y1=18, y2=25, block=M.SMOOTH)
    # Gold name plaque and emperor's seat on the terrace level.
    add_fill(fills, "ziyun plaque", (5688, 15, TOWER_Z1 - 4), (5712, 17, TOWER_Z1 - 4), M.GOLD)
    add_fill(fills, "ziyun throne dais", (5688, 5, 5970), (5712, 6, 5980), M.SMOOTH)
    add_fill(fills, "ziyun throne", (5696, 7, 5972), (5704, 10, 5976), M.GOLD)

    # ------------------------------------------------------------------
    # 5. Lotus pond (荷花池) west of the tower, with lily pads, lotus
    #    islets and a zigzag nine-curve bridge.
    # ------------------------------------------------------------------
    add_pool(fills, "lotus pond", LOTUS_X1, LOTUS_Z1, LOTUS_X2, LOTUS_Z2, 4, depth=2)
    for lx in range(LOTUS_X1 + 10, LOTUS_X2 - 5, 24):
        for lz in range(LOTUS_Z1 + 8, LOTUS_Z2 - 5, 18):
            add_fill(fills, f"lotus pad {lx},{lz}", (lx, 4, lz), (lx + 3, 4, lz + 2), "minecraft:lily_pad")
    # Three flowering lotus islets.
    for i, (ix, iz) in enumerate([(5230, 5960), (5300, 5980), (5370, 5955)]):
        add_fill(fills, f"lotus islet {i}", (ix - 5, 4, iz - 5), (ix + 5, 4, iz + 5), M.GRASS)
        add_fill(fills, f"lotus bloom {i}", (ix - 3, 5, iz - 3), (ix + 3, 5, iz + 3), M.PINK_WOOL)
        add_fill(fills, f"lotus bloom core {i}", (ix - 1, 5, iz - 1), (ix + 1, 5, iz + 1), M.WHITE_WOOL)
    # Nine-curve bridge: zigzag deck across the pond.
    seg = [
        (5395, 5990, 5345, 5990), (5345, 5990, 5345, 5970), (5345, 5970, 5290, 5970),
        (5290, 5970, 5290, 5950), (5290, 5950, 5235, 5950),
    ]
    for i, (x1, z1, x2, z2) in enumerate(seg):
        add_fill(fills, f"nine-curve deck {i}", (min(x1, x2), 4, min(z1, z2) - 1), (max(x1, x2), 4, max(z1, z2) + 1), M.WOOD)
        if x1 == x2:
            add_fill(fills, f"nine-curve rail w {i}", (x1 - 1, 5, min(z1, z2)), (x1 - 1, 5, max(z1, z2)), M.FENCE)
            add_fill(fills, f"nine-curve rail e {i}", (x1 + 1, 5, min(z1, z2)), (x1 + 1, 5, max(z1, z2)), M.FENCE)
        else:
            add_fill(fills, f"nine-curve rail n {i}", (min(x1, x2), 5, z1 - 1), (max(x1, x2), 5, z1 - 1), M.FENCE)
            add_fill(fills, f"nine-curve rail s {i}", (min(x1, x2), 5, z1 + 1), (max(x1, x2), 5, z1 + 1), M.FENCE)

    # ------------------------------------------------------------------
    # 6. Officials' tent gallery (百官幕次) along the west shore.
    # ------------------------------------------------------------------
    for i, gx in enumerate(range(GALLERY_X1, GALLERY_X2 - 20, 30)):
        roof = M.RED_WOOL if i % 2 == 0 else M.YELLOW_WOOL
        add_fill(fills, f"tent floor {i}", (gx, 5, GALLERY_Z1), (gx + 22, 5, GALLERY_Z1 + 40), M.WOOD)
        for px in (gx, gx + 10, gx + 20):
            for pz in (GALLERY_Z1, GALLERY_Z1 + 20, GALLERY_Z1 + 40):
                add_fill(fills, f"tent post {i} {px},{pz}", (px, 6, pz), (px, 10, pz), M.LOG)
        add_pyramid_roof(fills, f"tent roof {i}", gx + 11, GALLERY_Z1 + 20, radius=16, y=11, roof_block=roof, apex_block=M.GOLD)

    # ------------------------------------------------------------------
    # 7. Garden wall with a moon gate (月洞门).
    # ------------------------------------------------------------------
    add_fill(fills, "garden wall s", (5150, 5, 6070), (5850, 10, 6075), M.WHITE_TERRACOTTA)
    add_fill(fills, "garden wall w", (5150, 5, 5935), (5155, 10, 6075), M.WHITE_TERRACOTTA)
    add_fill(fills, "garden wall e", (5845, 5, 5935), (5850, 10, 6075), M.WHITE_TERRACOTTA)
    add_fill(fills, "garden coping s", (5150, 11, 6069), (5850, 11, 6076), M.DARK)
    # Moon gate in the south wall, centred on the tower axis.
    add_fill(fills, "moon gate", (5686, 5, 6070), (5714, 10, 6075), M.AIR)
    add_fill(fills, "moon gate arch", (5684, 5, 6069), (5716, 5, 6076), M.GOLD)
    add_fill(fills, "moon gate crown", (5692, 6, 6070), (5708, 8, 6075), M.AIR)
    add_fill(fills, "moon gate crown rim", (5690, 8, 6069), (5710, 10, 6076), M.WHITE_TERRACOTTA)
    add_fill(fills, "garden gate landing", (5686, 4, 6076), (5714, 4, 6082), M.SMOOTH)

    # ------------------------------------------------------------------
    # 8. Banquet lantern line along the waterfront.
    # ------------------------------------------------------------------
    add_lantern_line(fills, "banquet lanterns", 5160, 5952, 5540, 5952, y=5, every=40)
    add_lantern_line(fills, "shore lanterns", 5860, 5960, 5860, 6060, y=5, every=40)


def main() -> None:
    run_builder(build_fuyong_yuan_3d, "fuyong_yuan_3d")


if __name__ == "__main__":
    main()
