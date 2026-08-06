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
    add_pagoda_eave,
    add_pagoda_openings,
    add_pool,
    add_ridge_roof,
    add_tree,
    run_builder,
)


"""
Daxingshan Temple (大兴善寺) - major Buddhist temple and translation center.

Location: local (1200, 2200) .. (1700, 2700)
"""

X1, Z1 = 1200, 2200
X2, Z2 = 1700, 2700


def build_daxingshan_temple(fills: list[Fill]) -> None:
    # Temple wall
    add_outline(fills, "daxingshan wall", X1, Z1, X2, Z2, 1, 8, M.RED_WALL, thickness=2)

    # South mountain gate
    mid_x = (X1 + X2) // 2
    add_fill(fills, "daxingshan gate", (mid_x - 14, 1, Z1 - 4), (mid_x + 14, 14, Z1 + 4), M.RED_WALL)
    add_ridge_roof(fills, "daxingshan gate roof", mid_x - 18, Z1 - 6, mid_x + 18, Z1 + 6, 15, layers=2, ridge_axis="z")

    # Heavenly Kings Hall
    hx, hz = mid_x, Z1 + 120
    add_hollow_box(fills, "daxingshan heavenly hall", hx - 30, 1, hz - 20, hx + 30, 22, hz + 20, M.RED_WALL, thickness=2)
    add_ridge_roof(fills, "daxingshan heavenly roof", hx - 36, hz - 26, hx + 36, hz + 26, 23, layers=3, ridge_axis="z")

    # Mahavira Hall
    hx2, hz2 = mid_x, Z1 + 280
    add_hollow_box(fills, "daxingshan mahavira hall", hx2 - 45, 1, hz2 - 35, hx2 + 45, 30, hz2 + 35, M.RED_WALL, thickness=2)
    add_ridge_roof(fills, "daxingshan mahavira roof", hx2 - 52, hz2 - 42, hx2 + 52, hz2 + 42, 31, layers=4, ridge_axis="z")

    # Dharma pagoda
    px, pz = hx2 + 90, hz2
    y = 1
    for tier in range(7):
        r = 16 - tier * 2
        add_hollow_box(fills, f"daxingshan pagoda t{tier}", px - r, y, pz - r, px + r, y + 7, pz + r, M.WHITE_TERRACOTTA, thickness=2)
        add_pagoda_openings(fills, f"daxingshan pagoda t{tier}", px, pz, r, y, 7)
        add_pagoda_eave(fills, f"daxingshan pagoda eave t{tier}", px, pz, r, y + 7)
        y += 8
    add_fill(fills, "daxingshan pagoda spire", (px - 1, y, pz - 1), (px + 1, y + 12, pz + 1), M.GOLD)

    # Sutra translation pavilion
    sx, sz = hx2 - 90, hz2
    add_hollow_box(fills, "daxingshan sutra pavilion", sx - 25, 1, sz - 20, sx + 25, 20, sz + 20, M.WOOD, thickness=1)
    add_ridge_roof(fills, "daxingshan sutra roof", sx - 30, sz - 25, sx + 30, sz + 25, 21, layers=2, ridge_axis="z")

    # Pond and trees
    add_pool(fills, "daxingshan pond", X1 + 80, Z2 - 120, X2 - 80, Z2 - 60, 2)
    for tx, tz in [(X1 + 50, Z1 + 50), (X2 - 50, Z1 + 50), (X1 + 50, Z2 - 50), (X2 - 50, Z2 - 50)]:
        add_tree(fills, f"daxingshan tree {tx},{tz}", tx, tz, 2)


def main() -> None:
    run_builder(build_daxingshan_temple, "temple_daxingshan")


if __name__ == "__main__":
    main()
