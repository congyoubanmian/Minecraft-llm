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
Jianfu Temple (荐福寺) full monastery around the Small Wild Goose Pagoda.

Complements pagoda_small.py.
Location: local (1100, 3500) .. (1550, 3950)
"""

X1, Z1 = 1100, 3500
X2, Z2 = 1550, 3950


def build_jianfu_temple(fills: list[Fill]) -> None:
    mid_x = (X1 + X2) // 2

    # Outer wall
    add_outline(fills, "jianfu wall", X1, Z1, X2, Z2, 1, 7, M.RED_WALL, thickness=2)

    # South gate
    add_fill(fills, "jianfu gate", (mid_x - 14, 1, Z1 - 4), (mid_x + 14, 14, Z1 + 4), M.RED_WALL)
    add_ridge_roof(fills, "jianfu gate roof", mid_x - 18, Z1 - 6, mid_x + 18, Z1 + 6, 15, layers=2, ridge_axis="z")

    # Buddha hall
    hx, hz = mid_x, Z1 + 100
    add_hollow_box(fills, "jianfu buddha hall", hx - 35, 1, hz - 25, hx + 35, 20, hz + 25, M.RED_WALL, thickness=2)
    add_ridge_roof(fills, "jianfu buddha roof", hx - 40, hz - 30, hx + 40, hz + 30, 21, layers=3, ridge_axis="z")

    # Small Wild Goose Pagoda sits here (already built by pagoda_small.py)
    # Add bell pavilion
    bx, bz = X1 + 80, Z1 + 200
    add_hollow_box(fills, "jianfu bell pavilion", bx - 12, 1, bz - 12, bx + 12, 18, bz + 12, M.STONE, thickness=1)
    add_ridge_roof(fills, "jianfu bell roof", bx - 16, bz - 16, bx + 16, bz + 16, 19, layers=2, ridge_axis="z")
    add_fill(fills, "jianfu bell", (bx - 4, 8, bz - 4), (bx + 4, 14, bz + 4), M.GOLD)

    # Monk quarters
    add_hollow_box(fills, "jianfu quarters", X2 - 120, 1, Z1 + 220, X2 - 30, 10, Z2 - 30, M.WHITE, thickness=1)
    add_ridge_roof(fills, "jianfu quarters roof", X2 - 126, Z1 + 214, X2 - 24, Z2 - 24, 11, layers=2, ridge_axis="z")

    # Pond
    add_pool(fills, "jianfu pond", X1 + 80, Z2 - 150, X1 + 200, Z2 - 80, 2)

    # Trees
    for tx, tz in [(X1 + 50, Z1 + 50), (X2 - 50, Z1 + 50), (X1 + 50, Z2 - 50), (X2 - 50, Z2 - 50)]:
        add_tree(fills, f"jianfu tree {tx},{tz}", tx, tz, 2)


def main() -> None:
    run_builder(build_jianfu_temple, "temple_jianfu")


if __name__ == "__main__":
    main()
