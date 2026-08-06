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
    add_pool,
    add_tree,
    run_builder,
)


"""
Imperial garden rockeries and small landscape scenes.

Placed in palace gardens and large wards.
"""

GARDENS = [
    # (name, x1, z1, x2, z2)
    ("daming_rockery", 3200, 5400, 3600, 5700),
    ("xingqing_rockery", 1100, 1100, 1400, 1400),
    ("taiji_rockery", 2500, 5500, 2800, 5700),
]


def build_rockery(fills: list[Fill], name: str, x1: int, z1: int, x2: int, z2: int) -> None:
    cx, cz = (x1 + x2) // 2, (z1 + z2) // 2
    # Pond
    add_pool(fills, f"{name} pond", x1, z1, x2, z2, 2)
    # Central rock mountain
    add_fill(fills, f"{name} rock base", (cx - 12, 1, cz - 12), (cx + 12, 6, cz + 12), M.STONE)
    add_fill(fills, f"{name} rock mid", (cx - 8, 7, cz - 8), (cx + 8, 12, cz + 8), M.ANDESITE)
    add_fill(fills, f"{name} rock top", (cx - 4, 13, cz - 4), (cx + 4, 17, cz + 4), M.DARK)
    # Pavilion on top
    add_fill(fills, f"{name} pavilion base", (cx - 3, 18, cz - 3), (cx + 3, 19, cz + 3), M.WHITE)
    add_fill(fills, f"{name} pavilion body", (cx - 2, 20, cz - 2), (cx + 2, 26, cz + 2), M.RED_WALL)
    # Trees around
    for tx, tz in [(-20, -20), (20, -20), (-20, 20), (20, 20), (0, -25), (0, 25)]:
        add_tree(fills, f"{name} tree {tx},{tz}", cx + tx, cz + tz, 2)


def build_all_rockeries(fills: list[Fill]) -> None:
    for name, x1, z1, x2, z2 in GARDENS:
        build_rockery(fills, name, x1, z1, x2, z2)


def main() -> None:
    run_builder(build_all_rockeries, "garden_rockery")


if __name__ == "__main__":
    main()
