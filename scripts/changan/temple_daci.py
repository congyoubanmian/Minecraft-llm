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
Da Ci'en Temple (大慈恩寺) full monastery around the Giant Wild Goose Pagoda.

Complements pagoda_giant.py by adding the complete temple courtyards.
Location: local (4300, 3600) .. (4900, 4200)
"""

X1, Z1 = 4300, 3600
X2, Z2 = 4900, 4200


def build_daci_temple(fills: list[Fill]) -> None:
    mid_x = (X1 + X2) // 2

    # Outer wall
    add_outline(fills, "daci wall", X1, Z1, X2, Z2, 1, 8, M.RED_WALL, thickness=2)

    # South mountain gate
    add_fill(fills, "daci gate", (mid_x - 16, 1, Z1 - 4), (mid_x + 16, 15, Z1 + 4), M.RED_WALL)
    add_ridge_roof(fills, "daci gate roof", mid_x - 20, Z1 - 6, mid_x + 20, Z1 + 6, 16, layers=2, ridge_axis="z")

    # Heavenly Kings Hall
    hx, hz = mid_x, Z1 + 100
    add_hollow_box(fills, "daci heavenly hall", hx - 32, 1, hz - 22, hx + 32, 20, hz + 22, M.RED_WALL, thickness=2)
    add_ridge_roof(fills, "daci heavenly roof", hx - 38, hz - 28, hx + 38, hz + 28, 21, layers=3, ridge_axis="z")

    # Mahavira Hall
    hx2, hz2 = mid_x, Z1 + 250
    add_hollow_box(fills, "daci mahavira hall", hx2 - 48, 1, hz2 - 38, hx2 + 48, 28, hz2 + 38, M.RED_WALL, thickness=2)
    add_ridge_roof(fills, "daci mahavira roof", hx2 - 55, hz2 - 45, hx2 + 55, hz2 + 45, 29, layers=4, ridge_axis="z")

    # Dharma hall
    dx, dz = mid_x, Z1 + 380
    add_hollow_box(fills, "daci dharma hall", dx - 35, 1, dz - 25, dx + 35, 18, dz + 25, M.WOOD, thickness=1)
    add_ridge_roof(fills, "daci dharma roof", dx - 40, dz - 30, dx + 40, dz + 30, 19, layers=2, ridge_axis="z")

    # Giant Wild Goose Pagoda sits here (already built by pagoda_giant.py)
    # Add surrounding scripture pavilions
    sx1, sz1 = mid_x - 80, Z1 + 320
    sx2, sz2 = mid_x + 80, Z1 + 320
    for idx, (sx, sz) in enumerate([(sx1, sz1), (sx2, sz2)]):
        add_hollow_box(fills, f"daci sutra pavilion {idx}", sx - 18, 1, sz - 15, sx + 18, 14, sz + 15, M.WOOD, thickness=1)
        add_ridge_roof(fills, f"daci sutra roof {idx}", sx - 22, sz - 19, sx + 22, sz + 19, 15, layers=2, ridge_axis="z")

    # Ponds and trees
    add_pool(fills, "daci west pond", X1 + 80, Z1 + 180, X1 + 180, Z1 + 280, 2)
    add_pool(fills, "daci east pond", X2 - 180, Z1 + 180, X2 - 80, Z1 + 280, 2)
    for tx, tz in [(X1 + 50, Z1 + 50), (X2 - 50, Z1 + 50), (X1 + 50, Z2 - 50), (X2 - 50, Z2 - 50)]:
        add_tree(fills, f"daci tree {tx},{tz}", tx, tz, 2)


def main() -> None:
    run_builder(build_daci_temple, "temple_daci")


if __name__ == "__main__":
    main()
