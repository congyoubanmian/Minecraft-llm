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
    add_ridge_roof,
    add_spiral_stair,
    add_staircase,
    add_underground_room,
    run_builder,
)


"""
Hanyuan Dian (含元殿) 3D enhancement pass.

Builds on the base palace_hanyuan_dian module and adds true vertical depth:
- Switchback dragon-tail staircases
- Cantilevered flying corridors to the que towers
- Multi-tier dougong bracket clusters
- A three-storey rooftop pavilion (ge 阁)
- A small underground treasury beneath the hall

Coordinates match the original module:
    x: 2660 .. 3340
    z: 5180 .. 5480
"""

X1, Z1 = 2660, 5180
X2, Z2 = 3340, 5480
MID_X = (X1 + X2) // 2
MID_Z = (Z1 + Z2) // 2
TERRACE_TOP = 9
HALL_HEIGHT = 48
DOUGONG_Y = TERRACE_TOP + HALL_HEIGHT + 1  # 58
ROOF_Y = DOUGONG_Y + 3                     # 61


def build_hanyuan_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Switchback dragon-tail staircases (true 3D stairs)
    # ------------------------------------------------------------------
    # East switchback: two straight runs joined by a landing
    add_staircase(
        fills, "hanyuan stair east lower",
        MID_X + 140, Z1 - 120,
        MID_X + 140, Z1 - 80,
        2, 6,
        "north",
        block=M.ANDESITE,
    )
    add_fill(fills, "hanyuan stair east landing", (MID_X + 130, 6, Z1 - 80), (MID_X + 150, 6, Z1 - 70), M.ANDESITE)
    add_staircase(
        fills, "hanyuan stair east upper",
        MID_X + 140, Z1 - 70,
        MID_X + 60, Z1 - 20,
        6, TERRACE_TOP,
        "north",
        block=M.SMOOTH,
    )

    # West switchback
    add_staircase(
        fills, "hanyuan stair west lower",
        MID_X - 140, Z1 - 120,
        MID_X - 140, Z1 - 80,
        2, 6,
        "north",
        block=M.ANDESITE,
    )
    add_fill(fills, "hanyuan stair west landing", (MID_X - 150, 6, Z1 - 80), (MID_X - 130, 6, Z1 - 70), M.ANDESITE)
    add_staircase(
        fills, "hanyuan stair west upper",
        MID_X - 140, Z1 - 70,
        MID_X - 60, Z1 - 20,
        6, TERRACE_TOP,
        "north",
        block=M.SMOOTH,
    )

    # Central imperial ramp (wider, straight)
    add_staircase(
        fills, "hanyuan stair central",
        MID_X - 30, Z1 - 100,
        MID_X + 30, Z1 - 20,
        2, TERRACE_TOP,
        "north",
        block=M.GRANITE,
    )

    # ------------------------------------------------------------------
    # 2. Cantilevered flying corridors to the que towers
    # ------------------------------------------------------------------
    # East corridor from hall to Xiangluan que
    corridor_z = MID_Z
    add_cantilevered_floor(
        fills, "hanyuan corridor east",
        X2, corridor_z - 8,
        X2 + 120, corridor_z + 8,
        TERRACE_TOP + 12,
        overhang=4,
        block=M.WOOD,
        support_block=M.LOG,
    )
    # Corridor roof
    add_ridge_roof(
        fills, "hanyuan corridor east roof",
        X2 - 6, corridor_z - 14, X2 + 126, corridor_z + 14,
        TERRACE_TOP + 14,
        layers=2,
        ridge_axis="x",
        roof_block=M.ROOF_GREEN,
    )

    # West corridor from hall to Qifeng que
    add_cantilevered_floor(
        fills, "hanyuan corridor west",
        X1 - 120, corridor_z - 8,
        X1, corridor_z + 8,
        TERRACE_TOP + 12,
        overhang=4,
        block=M.WOOD,
        support_block=M.LOG,
    )
    add_ridge_roof(
        fills, "hanyuan corridor west roof",
        X1 - 126, corridor_z - 14, X1 + 6, corridor_z + 14,
        TERRACE_TOP + 14,
        layers=2,
        ridge_axis="x",
        roof_block=M.ROOF_GREEN,
    )

    # ------------------------------------------------------------------
    # 3. Multi-tier dougong clusters along the main eave line
    # ------------------------------------------------------------------
    for dx in range(X1 + 20, X2 - 10, 40):
        add_dougong_cluster(fills, f"hanyuan dougong n {dx}", dx, Z1 - 6, DOUGONG_Y, tiers=3)
        add_dougong_cluster(fills, f"hanyuan dougong s {dx}", dx, Z2 + 6, DOUGONG_Y, tiers=3)
    for dz in range(Z1 + 20, Z2 - 10, 40):
        add_dougong_cluster(fills, f"hanyuan dougong w {dz}", X1 - 6, dz, DOUGONG_Y, tiers=3)
        add_dougong_cluster(fills, f"hanyuan dougong e {dz}", X2 + 6, dz, DOUGONG_Y, tiers=3)

    # ------------------------------------------------------------------
    # 4. Three-storey rooftop pavilion (ge 阁) above the main ridge
    # ------------------------------------------------------------------
    ge_x1, ge_z1 = MID_X - 40, MID_Z - 30
    ge_x2, ge_z2 = MID_X + 40, MID_Z + 30
    for storey in range(3):
        y_base = ROOF_Y + 10 + storey * 12
        # Body
        add_fill(
            fills, f"hanyuan ge storey {storey}",
            (ge_x1, y_base, ge_z1), (ge_x2, y_base + 8, ge_z2),
            M.RED_WALL,
        )
        # Balcony overhang
        add_cantilevered_floor(
            fills, f"hanyuan ge balcony {storey}",
            ge_x1, ge_z1, ge_x2, ge_z2,
            y_base + 9,
            overhang=6,
            block=M.WOOD,
        )
        # Storey roof
        add_ridge_roof(
            fills, f"hanyuan ge roof {storey}",
            ge_x1 - 8, ge_z1 - 8, ge_x2 + 8, ge_z2 + 8,
            y_base + 10,
            layers=2,
            ridge_axis="z",
            roof_block=M.ROOF_GREEN,
        )

    # Spiral stair inside the pavilion
    add_spiral_stair(
        fills, "hanyuan ge spiral",
        MID_X, MID_Z,
        radius=20,
        y1=ROOF_Y + 10,
        y2=ROOF_Y + 10 + 3 * 12,
        block=M.SMOOTH,
    )

    # Golden spire above the pavilion
    spire_y = ROOF_Y + 10 + 3 * 12 + 2
    add_fill(fills, "hanyuan ge spire", (MID_X - 2, spire_y, MID_Z - 2), (MID_X + 2, spire_y + 12, MID_Z + 2), M.GOLD)

    # ------------------------------------------------------------------
    # 5. Underground treasury beneath the hall
    # ------------------------------------------------------------------
    add_underground_room(
        fills, "hanyuan treasury",
        MID_X - 30, MID_Z - 20,
        MID_X + 30, MID_Z + 20,
        y_floor=-4,
        y_ceiling=2,
        block=M.STONE,
    )
    # Treasury entrance stair from the hall floor
    add_staircase(
        fills, "hanyuan treasury stair",
        MID_X - 20, MID_Z + 18,
        MID_X - 20, MID_Z + 30,
        TERRACE_TOP, -4,
        "south",
        block=M.STONE,
    )
    # Iron-bar gate at the bottom
    add_fill(fills, "hanyuan treasury gate", (MID_X - 21, -3, MID_Z + 29), (MID_X - 19, 1, MID_Z + 31), M.IRON_BARS)


def main() -> None:
    run_builder(build_hanyuan_3d, "palace_hanyuan_3d")


if __name__ == "__main__":
    main()
