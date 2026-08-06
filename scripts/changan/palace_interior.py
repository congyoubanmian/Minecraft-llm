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
    run_builder,
)


"""
Palace interior details: floors, throne platforms, dragon thrones, lanterns,
ceiling lights, and screens for major palace halls.
"""

HALLS = [
    # (name, x1, z1, x2, z2, floor_y, height)
    ("hanyuan", 2660, 5180, 3340, 5480, 9, 56),
    ("xuanzheng", 2740, 4880, 3260, 5080, 8, 36),
    ("zichen", 2360, 5200, 2620, 5480, 6, 28),
    ("taiji_hall", 2920, 5050, 3080, 5150, 7, 38),
    ("liangyi", 2940, 5360, 3060, 5440, 6, 28),
    ("xingqing_flower", 992, 1460, 1048, 1500, 2, 43),
]


def add_throne(fills: list[Fill], name: str, cx: int, cz: int, y: int) -> None:
    """Add an imperial throne on a raised platform."""
    add_fill(fills, f"{name} throne platform", (cx - 6, y, cz - 4), (cx + 6, y + 2, cz + 4), M.GOLD)
    add_fill(fills, f"{name} throne seat", (cx - 2, y + 3, cz - 2), (cx + 2, y + 5, cz + 2), M.RED_WOOL)
    add_fill(fills, f"{name} throne back", (cx - 2, y + 6, cz - 2), (cx + 2, y + 10, cz + 1), M.GOLD)
    add_fill(fills, f"{name} throne screen", (cx - 8, y + 3, cz - 8), (cx + 8, y + 12, cz - 5), M.RED_WALL)


def add_official_desks(fills: list[Fill], name: str, x1: int, z1: int, x2: int, z2: int, y: int) -> None:
    """Rows of minister desks for audience halls."""
    for x in range(x1 + 10, x2 - 9, 20):
        for z in range(z1 + 20, z2 - 19, 30):
            add_fill(fills, f"{name} desk {x},{z}", (x - 3, y, z - 2), (x + 3, y + 2, z + 2), M.WOOD)
            add_fill(fills, f"{name} mat {x},{z}", (x - 2, y - 1, z - 2), (x + 2, y - 1, z + 2), M.RED_WOOL)


def add_hall_interior(fills: list[Fill], name: str, x1: int, z1: int, x2: int, z2: int, floor_y: int, height: int) -> None:
    mid_x = (x1 + x2) // 2
    mid_z = (z1 + z2) // 2

    # Polished floor
    add_fill(fills, f"{name} floor", (x1 + 8, floor_y, z1 + 8), (x2 - 8, floor_y, z2 - 8), M.SMOOTH)
    # Central red carpet aisle
    add_fill(fills, f"{name} carpet", (mid_x - 4, floor_y + 1, z1 + 8), (mid_x + 4, floor_y + 1, z2 - 8), M.RED_WOOL)

    # Throne at north end
    add_throne(fills, name, mid_x, z1 + 30, floor_y)

    # Minister desks for large audience halls
    if "hanyuan" in name or "xuanzheng" in name or "taiji_hall" in name or "danfeng" in name:
        add_official_desks(fills, name, x1, z1, x2, z2, floor_y + 1)

    # Ceiling lights (sea lanterns in grid)
    ceiling_y = floor_y + height - 1
    for lx in range(x1 + 15, x2 - 14, max(30, (x2 - x1) // 4)):
        for lz in range(z1 + 15, z2 - 14, max(30, (z2 - z1) // 4)):
            add_fill(fills, f"{name} ceiling light {lx},{lz}", (lx, ceiling_y, lz), (lx + 1, ceiling_y, lz + 1), M.SEA_LANTERN)

    # Wall lanterns
    add_lantern_line(fills, f"{name} wall lamps n", mid_x - 20, z1 + 10, mid_x + 20, z1 + 10, floor_y + 4, 20)
    add_lantern_line(fills, f"{name} wall lamps s", mid_x - 20, z2 - 10, mid_x + 20, z2 - 10, floor_y + 4, 20)


def build_palace_interior(fills: list[Fill]) -> None:
    for name, x1, z1, x2, z2, floor_y, height in HALLS:
        add_hall_interior(fills, name, x1, z1, x2, z2, floor_y, height)


def main() -> None:
    run_builder(build_palace_interior, "palace_interior")


if __name__ == "__main__":
    main()
