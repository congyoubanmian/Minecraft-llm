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
Guozijian (国子监) and Taixue (太学) - Tang imperial academy.

Location: local (1600, 4200) .. (2200, 4700)
"""

X1, Z1 = 1600, 4200
X2, Z2 = 2200, 4700


def build_guozijian(fills: list[Fill]) -> None:
    mid_x = (X1 + X2) // 2

    # Compound wall
    add_outline(fills, "guozijian wall", X1, Z1, X2, Z2, 1, 7, M.RED_WALL, thickness=2)

    # Main gate (Lingxing Gate)
    add_fill(fills, "guozijian lingxing gate", (mid_x - 18, 1, Z1 - 4), (mid_x + 18, 14, Z1 + 4), M.RED_WALL)
    add_ridge_roof(fills, "guozijian lingxing roof", mid_x - 22, Z1 - 6, mid_x + 22, Z1 + 6, 15, layers=2, ridge_axis="z")

    # Biyong (jade-disc pond)
    add_pool(fills, "guozijian biyong", mid_x - 60, Z1 + 80, mid_x + 60, Z1 + 160, 2)

    # Confucius Temple
    add_hollow_box(fills, "guozijian confucius hall", mid_x - 50, 1, Z1 + 200, mid_x + 50, 22, Z1 + 280, M.RED_WALL, thickness=2)
    add_ridge_roof(fills, "guozijian confucius roof", mid_x - 56, Z1 + 194, mid_x + 56, Z1 + 286, 23, layers=3, ridge_axis="z")

    # Lecture halls east and west
    for idx, hx in enumerate([mid_x - 100, mid_x + 100]):
        add_hollow_box(fills, f"guozijian lecture {idx}", hx - 35, 1, Z1 + 220, hx + 35, 14, Z1 + 320, M.WOOD, thickness=1)
        add_ridge_roof(fills, f"guozijian lecture roof {idx}", hx - 40, Z1 + 214, hx + 40, Z1 + 326, 15, layers=2, ridge_axis="z")

    # Student dormitories
    for idx, dz in enumerate([Z1 + 360, Z1 + 400]):
        add_hollow_box(fills, f"guozijian dorm {idx}", X1 + 30, 1, dz, X2 - 30, 10, dz + 30, M.WHITE, thickness=1)
        add_ridge_roof(fills, f"guozijian dorm roof {idx}", X1 + 24, dz - 4, X2 - 24, dz + 34, 11, layers=2, ridge_axis="z")

    # Stele pavilion
    sx, sz = mid_x, Z2 - 80
    add_fill(fills, "guozijian stele base", (sx - 6, 1, sz - 6), (sx + 6, 2, sz + 6), M.ANDESITE)
    add_fill(fills, "guozijian stele", (sx - 2, 3, sz - 1), (sx + 2, 12, sz + 1), M.STONE)
    add_ridge_roof(fills, "guozijian stele roof", sx - 8, sz - 8, sx + 8, sz + 8, 13, layers=2, ridge_axis="z")

    # Trees
    for tx, tz in [(X1 + 50, Z1 + 50), (X2 - 50, Z1 + 50), (X1 + 50, Z2 - 50), (X2 - 50, Z2 - 50)]:
        add_tree(fills, f"guozijian tree {tx},{tz}", tx, tz, 2, height=8, spread=3)


def main() -> None:
    run_builder(build_guozijian, "academy_guozijian")


if __name__ == "__main__":
    main()
