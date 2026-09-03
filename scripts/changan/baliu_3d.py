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
    add_lantern_line,
    add_outline,
    add_pyramid_roof,
    run_builder,
)


"""
Ba Bridge 3D (灞桥·折柳送别) - the great multi-arch bridge over the Ba
River east of the city. Tang travellers were seen off here with willow
branches ("折柳送别"); the scene "灞柳风雪" is one of the Eight Views
of Guanzhong.

Location in Chang'an city local coordinates:
    East suburb beyond the farm belt: x 7000..7600, z 1700..2200.
    The Ba River channel runs north-south at x 7260..7300.

Distinctive features:
    - A full river: carved channel, stone-lined banks and a sandy bed
    - A five-arch stone bridge with cutwaters (分水尖) and end stairs
    - Willow rows drooping over both banks (two-layer drooping canopy)
    - The Ba Farewell Pavilion (灞亭) at the western bridge head
    - A post road (驿道) with milestone markers and a rest shed
    - Willow-breaking platform (折柳台) at the water's edge
"""

RIVER_X1, RIVER_X2 = 7260, 7300
RIVER_Z1, RIVER_Z2 = 1550, 2350
BRIDGE_Z1, BRIDGE_Z2 = 1852, 1908
DECK_Y = 9


def _willow(fills: list[Fill], label: str, x: int, z: int, y: int) -> None:
    """Weeping willow: high canopy with a drooping lower leaf ring."""
    add_fill(fills, f"{label} trunk", (x, y, z), (x, y + 7, z), M.LOG)
    add_fill(fills, f"{label} canopy", (x - 3, y + 6, z - 3), (x + 3, y + 8, z + 3), M.LEAVES)
    add_fill(fills, f"{label} crown", (x - 2, y + 9, z - 2), (x + 2, y + 9, z + 2), M.LEAVES)
    add_outline(fills, f"{label} droop", x - 4, z - 4, x + 4, z + 4, y + 4, y + 4, M.LEAVES, thickness=1)
    for dx, dz in ((-4, 0), (4, 0), (0, -4), (0, 4)):
        add_fill(fills, f"{label} curtain {dx},{dz}", (x + dx, y + 3, z + dz), (x + dx, y + 5, z + dz), M.LEAVES)


def build_baliu_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 0. Level the whole river plain first (stone base, grass on top).
    # ------------------------------------------------------------------
    add_fill(fills, "ba plain base", (6980, 0, 1550), (7620, 1, 2350), M.STONE)
    add_fill(fills, "ba plain grass", (6980, 2, 1550), (7620, 3, 2350), M.GRASS)

    # ------------------------------------------------------------------
    # 1. The Ba River: carve the channel, line the banks, sandy bed.
    # ------------------------------------------------------------------
    add_fill(fills, "ba river carve", (RIVER_X1 - 8, -3, RIVER_Z1), (RIVER_X2 + 8, 4, RIVER_Z2), M.AIR)
    add_fill(fills, "ba river bed", (RIVER_X1, 0, RIVER_Z1), (RIVER_X2, 0, RIVER_Z2), "minecraft:sand")
    add_fill(fills, "ba river water", (RIVER_X1, 1, RIVER_Z1), (RIVER_X2, 2, RIVER_Z2), M.WATER)
    # Stone banks on both sides.
    add_fill(fills, "ba bank w", (RIVER_X1 - 8, -3, RIVER_Z1), (RIVER_X1 - 1, 2, RIVER_Z2), M.STONE)
    add_fill(fills, "ba bank e", (RIVER_X2 + 1, -3, RIVER_Z1), (RIVER_X2 + 8, 2, RIVER_Z2), M.STONE)
    add_fill(fills, "ba bank w top", (RIVER_X1 - 8, 3, RIVER_Z1), (RIVER_X1 - 1, 3, RIVER_Z2), M.SMOOTH)
    add_fill(fills, "ba bank e top", (RIVER_X2 + 1, 3, RIVER_Z1), (RIVER_X2 + 8, 3, RIVER_Z2), M.SMOOTH)

    # ------------------------------------------------------------------
    # 2. Five-arch stone bridge across the river.
    # ------------------------------------------------------------------
    bx1, bx2 = 7100, 7460
    # Stepped approaches: five terraces climbing from the post road (y 3)
    # to the deck (y 9) on each side.
    for i in range(5):
        wy = 4 + i
        add_fill(fills, f"ba ramp w {i}", (6920 + i * 36, 3, BRIDGE_Z1 + 2), (6955 + i * 36, wy, BRIDGE_Z2 - 2), M.STONE)
        add_fill(fills, f"ba ramp w top {i}", (6920 + i * 36, wy, BRIDGE_Z1 + 2), (6955 + i * 36, wy, BRIDGE_Z2 - 2), M.SMOOTH)
        add_fill(fills, f"ba ramp e {i}", (7461 + i * 36, 3, BRIDGE_Z1 + 2), (7496 + i * 36, 8 - i, BRIDGE_Z2 - 2), M.STONE)
        add_fill(fills, f"ba ramp e top {i}", (7461 + i * 36, 8 - i, BRIDGE_Z1 + 2), (7496 + i * 36, 8 - i, BRIDGE_Z2 - 2), M.SMOOTH)
    add_fill(fills, "ba bridge deck", (bx1, DECK_Y, BRIDGE_Z1), (bx2, DECK_Y, BRIDGE_Z2), M.SMOOTH)
    add_fill(fills, "ba bridge rail n", (bx1, DECK_Y + 1, BRIDGE_Z1), (bx2, DECK_Y + 2, BRIDGE_Z1), M.STONE)
    add_fill(fills, "ba bridge rail s", (bx1, DECK_Y + 1, BRIDGE_Z2), (bx2, DECK_Y + 2, BRIDGE_Z2), M.STONE)
    # Five piers with arched voids and pointed cutwaters (分水尖).
    for px in (7160, 7210, 7260, 7310, 7360, 7410):
        add_fill(fills, f"ba pier {px}", (px, 0, BRIDGE_Z1 + 2), (px + 10, DECK_Y - 1, BRIDGE_Z2 - 2), M.STONE)
        add_fill(fills, f"ba arch {px}", (px + 1, 4, BRIDGE_Z1 + 1), (px + 9, DECK_Y - 2, BRIDGE_Z2 - 1), M.AIR)
        add_fill(fills, f"ba cutwater n {px}", (px + 3, 1, BRIDGE_Z1 - 3), (px + 7, 3, BRIDGE_Z1 + 1), M.STONE)
        add_fill(fills, f"ba cutwater s {px}", (px + 3, 1, BRIDGE_Z2 - 1), (px + 7, 3, BRIDGE_Z2 + 3), M.STONE)
    # Bridge-head ornamental columns (华表) with gold caps.
    for hx in (7104, 7456):
        for hz in (BRIDGE_Z1 + 6, BRIDGE_Z2 - 6):
            add_fill(fills, f"ba huabiao {hx},{hz}", (hx, DECK_Y + 1, hz), (hx, DECK_Y + 7, hz), M.WHITE_TERRACOTTA)
            add_fill(fills, f"ba huabiao cap {hx},{hz}", (hx, DECK_Y + 8, hz), (hx, DECK_Y + 8, hz), M.GOLD)

    # ------------------------------------------------------------------
    # 3. Ba Farewell Pavilion (灞亭) at the western head: four columns,
    #    pyramid roof, wine table for the farewell rite.
    # ------------------------------------------------------------------
    fx, fz = 7140, 1800
    add_fill(fills, "ba pavilion base", (fx - 14, 4, fz - 14), (fx + 14, 5, fz + 14), M.STONE)
    add_outline(fills, "ba pavilion rail", fx - 14, fz - 14, fx + 14, fz + 14, 6, 6, M.FENCE, thickness=1)
    for px in (fx - 9, fx + 8):
        for pz in (fz - 9, fz + 8):
            add_fill(fills, f"ba pavilion col {px},{pz}", (px, 6, pz), (px + 1, 12, pz + 1), M.RED_WALL)
    add_pyramid_roof(fills, "ba pavilion roof", fx, fz, radius=18, y=13, roof_block=M.ROOF_GREEN, apex_block=M.GOLD)
    add_fill(fills, "ba pavilion table", (fx - 6, 6, fz - 2), (fx + 6, 7, fz + 2), M.WOOD)
    add_fill(fills, "ba farewell jars", (fx - 4, 8, fz - 1), (fx + 4, 9, fz + 1), "minecraft:barrel")
    add_fill(fills, "ba pavilion step1", (7120, 4, fz - 2), (7122, 4, fz + 2), M.SMOOTH)
    add_fill(fills, "ba pavilion step2", (7123, 4, fz - 2), (7125, 5, fz + 2), M.SMOOTH)

    # ------------------------------------------------------------------
    # 4. Willow rows (灞柳) along both banks.
    # ------------------------------------------------------------------
    for wz in range(1580, 2330, 30):
        if BRIDGE_Z1 - 20 <= wz <= BRIDGE_Z2 + 20:
            continue  # keep the bridge clear
        _willow(fills, f"willow w {wz}", RIVER_X1 - 14, wz, y=4)
        _willow(fills, f"willow e {wz}", RIVER_X2 + 14, wz, y=4)

    # ------------------------------------------------------------------
    # 5. Post road (驿道) east-west with milestones and a rest shed.
    # ------------------------------------------------------------------
    add_fill(fills, "post road w", (6980, 3, 1866), (7100, 3, 1894), M.ANDESITE)
    add_fill(fills, "post road e", (7460, 3, 1866), (7580, 3, 1894), M.ANDESITE)
    for i, mx in enumerate(range(6990, 7100, 34)):
        add_fill(fills, f"milestone w {i}", (mx, 4, 1860), (mx, 6, 1860), M.WHITE_TERRACOTTA)
        add_fill(fills, f"milestone cap w {i}", (mx, 7, 1860), (mx, 7, 1860), M.GOLD)
    for i, mx in enumerate(range(7480, 7580, 34)):
        add_fill(fills, f"milestone e {i}", (mx, 4, 1860), (mx, 6, 1860), M.WHITE_TERRACOTTA)
        add_fill(fills, f"milestone cap e {i}", (mx, 7, 1860), (mx, 7, 1860), M.GOLD)
    # Rest shed for departing travellers.
    add_fill(fills, "shed floor", (7000, 4, 1920), (7060, 4, 1960), M.SMOOTH)
    for px in (7002, 7058):
        for pz in (1922, 1958):
            add_fill(fills, f"shed post {px},{pz}", (px, 5, pz), (px, 10, pz), M.LOG)
    add_fill(fills, "shed roof", (6998, 11, 1918), (7062, 12, 1962), M.DARK)
    add_fill(fills, "shed bench", (7008, 5, 1950), (7052, 6, 1956), M.WOOD)

    # ------------------------------------------------------------------
    # 6. Willow-breaking platform (折柳台) at the northwest water's edge.
    # ------------------------------------------------------------------
    add_fill(fills, "willow platform", (7196, 4, 1640), (7244, 5, 1688), M.SMOOTH)
    add_outline(fills, "willow platform rail", 7196, 1640, 7244, 1688, 6, 6, M.FENCE, thickness=1)
    add_fill(fills, "willow platform steps", (7245, 4, 1656), (7247, 4, 1672), M.SMOOTH)
    add_lantern_line(fills, "willow platform lanterns", 7200, 1684, 7240, 1684, y=6, every=20)
    _willow(fills, "willow platform tree", 7200, 1650, y=6)

    add_lantern_line(fills, "bridge lanterns", 7100, 1846, 7460, 1846, y=DECK_Y + 3, every=60)


def main() -> None:
    run_builder(build_baliu_3d, "baliu_3d")


if __name__ == "__main__":
    main()
