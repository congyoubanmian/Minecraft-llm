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
    add_outline,
    run_builder,
)


"""
Outer city wall enhancements:
- Crenellated battlements along the top
- Regular watch towers (every 300 blocks)
- Moat stone facing and lily pads
"""

CITY_SIZE = 6000


def build_battlements(fills: list[Fill]) -> None:
    # Top crenellation along outer wall perimeter
    # Wall top is at y=39 relative to base, wall thickness 34 blocks from edge 0..CITY_SIZE-1
    wall_top = 39
    for x in range(0, CITY_SIZE + 1, 10):
        # North and south walls
        add_fill(fills, f"battlement n {x}", (x, wall_top + 1, 0), (x + 4, wall_top + 3, 3), M.DARK)
        add_fill(fills, f"battlement s {x}", (x, wall_top + 1, CITY_SIZE - 4), (x + 4, wall_top + 3, CITY_SIZE - 1), M.DARK)
    for z in range(0, CITY_SIZE + 1, 10):
        # West and east walls
        add_fill(fills, f"battlement w {z}", (0, wall_top + 1, z), (3, wall_top + 3, z + 4), M.DARK)
        add_fill(fills, f"battlement e {z}", (CITY_SIZE - 4, wall_top + 1, z), (CITY_SIZE - 1, wall_top + 3, z + 4), M.DARK)


def build_watch_towers(fills: list[Fill]) -> None:
    # Watch towers spaced every 300 blocks along the wall
    for pos in range(300, CITY_SIZE, 300):
        # North wall tower
        add_fill(fills, f"watch n {pos}", (pos - 10, 1, -10), (pos + 10, 50, 10), M.STONE)
        add_fill(fills, f"watch n {pos} air", (pos - 6, 4, -6), (pos + 6, 46, 6), M.AIR)
        # South wall tower
        add_fill(fills, f"watch s {pos}", (pos - 10, 1, CITY_SIZE - 10), (pos + 10, 50, CITY_SIZE + 10), M.STONE)
        add_fill(fills, f"watch s {pos} air", (pos - 6, 4, CITY_SIZE - 6), (pos + 6, 46, CITY_SIZE + 6), M.AIR)
        # West wall tower
        add_fill(fills, f"watch w {pos}", (-10, 1, pos - 10), (10, 50, pos + 10), M.STONE)
        add_fill(fills, f"watch w {pos} air", (-6, 4, pos - 6), (6, 46, pos + 6), M.AIR)
        # East wall tower
        add_fill(fills, f"watch e {pos}", (CITY_SIZE - 10, 1, pos - 10), (CITY_SIZE + 10, 50, pos + 10), M.STONE)
        add_fill(fills, f"watch e {pos} air", (CITY_SIZE - 6, 4, pos - 6), (CITY_SIZE + 6, 46, pos + 6), M.AIR)


def build_moat_details(fills: list[Fill]) -> None:
    # Moat is 48 blocks wide around the wall, from -90 to -43 and CITY_SIZE+43 to CITY_SIZE+89
    # Add stone facing to inner moat edge and lily pads on water surface
    moat_y = 0
    # North and south moat stone facing
    add_fill(fills, "moat n facing", (-90, moat_y, -90), (CITY_SIZE + 90, moat_y + 1, -88), M.ANDESITE)
    add_fill(fills, "moat s facing", (-90, moat_y, CITY_SIZE + 88), (CITY_SIZE + 90, moat_y + 1, CITY_SIZE + 90), M.ANDESITE)
    # West and east moat stone facing
    add_fill(fills, "moat w facing", (-90, moat_y, -90), (-88, moat_y + 1, CITY_SIZE + 90), M.ANDESITE)
    add_fill(fills, "moat e facing", (CITY_SIZE + 88, moat_y, -90), (CITY_SIZE + 90, moat_y + 1, CITY_SIZE + 90), M.ANDESITE)

    # Lily pads scattered on water (use green wool as proxy)
    for x in range(-80, CITY_SIZE + 81, 120):
        for z in (-70, -50, CITY_SIZE + 50, CITY_SIZE + 70):
            add_fill(fills, f"moat lily {x},{z}", (x, moat_y + 1, z), (x + 2, moat_y + 1, z + 2), M.GREEN_WOOL)


def build_wall_battlement_moat(fills: list[Fill]) -> None:
    build_battlements(fills)
    build_watch_towers(fills)
    build_moat_details(fills)


def main() -> None:
    run_builder(build_wall_battlement_moat, "wall_battlement_moat")


if __name__ == "__main__":
    main()
