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
    add_tree,
    run_builder,
)


"""
Canals and waterways of Chang'an:
- Longshou Canal (龙首渠) from north-east
- Qingming Canal (清明渠) from south
- Yong'an Canal (永安渠) from west

These add water channels with stone banks and willow trees.
"""


def build_canal(
    fills: list[Fill],
    name: str,
    x1: int, z1: int,
    x2: int, z2: int,
    width: int = 12,
    y: int = 1,
) -> None:
    """Build a straight canal segment from (x1,z1) to (x2,z2)."""
    # Water channel
    if x1 == x2:
        # North-south canal
        add_fill(fills, f"{name} water", (x1 - width // 2, y, min(z1, z2)), (x1 + width // 2, y, max(z1, z2)), M.WATER)
        # Stone banks
        add_fill(fills, f"{name} west bank", (x1 - width // 2 - 2, y, min(z1, z2)), (x1 - width // 2 - 1, y + 1, max(z1, z2)), M.ANDESITE)
        add_fill(fills, f"{name} east bank", (x1 + width // 2 + 1, y, min(z1, z2)), (x1 + width // 2 + 2, y + 1, max(z1, z2)), M.ANDESITE)
        # Willow trees along banks
        for z in range(min(z1, z2) + 20, max(z1, z2) - 20, 80):
            add_tree(fills, f"{name} willow w {z}", x1 - width // 2 - 6, z, y + 1, height=6, spread=3)
            add_tree(fills, f"{name} willow e {z}", x1 + width // 2 + 6, z, y + 1, height=6, spread=3)
    elif z1 == z2:
        # East-west canal
        add_fill(fills, f"{name} water", (min(x1, x2), y, z1 - width // 2), (max(x1, x2), y, z1 + width // 2), M.WATER)
        add_fill(fills, f"{name} north bank", (min(x1, x2), y, z1 - width // 2 - 2), (max(x1, x2), y + 1, z1 - width // 2 - 1), M.ANDESITE)
        add_fill(fills, f"{name} south bank", (min(x1, x2), y, z1 + width // 2 + 1), (max(x1, x2), y + 1, z1 + width // 2 + 2), M.ANDESITE)
        for x in range(min(x1, x2) + 20, max(x1, x2) - 20, 80):
            add_tree(fills, f"{name} willow n {x}", x, z1 - width // 2 - 6, y + 1, height=6, spread=3)
            add_tree(fills, f"{name} willow s {x}", x, z1 + width // 2 + 6, y + 1, height=6, spread=3)


def build_canals(fills: list[Fill]) -> None:
    # Longshou Canal enters from north-east, flows south-west
    build_canal(fills, "longshou", 5200, 0, 4200, 2000)
    # Qingming Canal enters from south
    build_canal(fills, "qingming", 2400, 6000, 2400, 4000)
    # Yong'an Canal enters from west
    build_canal(fills, "yongan", 0, 3500, 2500, 3500)


def main() -> None:
    run_builder(build_canals, "canal_waterway")


if __name__ == "__main__":
    main()
