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
Da Yan Temple (大庄严寺) - major Tang Buddhist temple with the famous Da Yan Pagoda.

Location: local (900, 3500) .. (1400, 4000)
"""

X1, Z1 = 900, 3500
X2, Z2 = 1400, 4000


def build_dayan_temple(fills: list[Fill]) -> None:
    # Temple wall
    add_outline(fills, "dayan wall", X1, Z1, X2, Z2, 1, 8, M.RED_WALL, thickness=2)

    # South mountain gate
    mid_x = (X1 + X2) // 2
    add_fill(fills, "dayan gate", (mid_x - 14, 1, Z1 - 4), (mid_x + 14, 14, Z1 + 4), M.RED_WALL)
    add_ridge_roof(fills, "dayan gate roof", mid_x - 18, Z1 - 6, mid_x + 18, Z1 + 6, 15, layers=2, ridge_axis="z")

    # Da Yan Pagoda (square, multi-storey)
    px, pz = mid_x, Z1 + 150
    y = 1
    for tier in range(9):
        r = 22 - tier * 2
        add_hollow_box(fills, f"dayan pagoda t{tier}", px - r, y, pz - r, px + r, y + 8, pz + r, M.WHITE_TERRACOTTA, thickness=2)
        add_pagoda_openings(fills, f"dayan pagoda t{tier}", px, pz, r, y, 8)
        add_pagoda_eave(fills, f"dayan pagoda eave t{tier}", px, pz, r, y + 8)
        y += 9
    add_fill(fills, "dayan pagoda spire", (px - 1, y, pz - 1), (px + 1, y + 14, pz + 1), M.GOLD)

    # Mahavira Hall
    hx, hz = mid_x, Z1 + 300
    add_hollow_box(fills, "dayan mahavira", hx - 45, 1, hz - 35, hx + 45, 30, hz + 35, M.RED_WALL, thickness=2)
    add_ridge_roof(fills, "dayan mahavira roof", hx - 52, hz - 42, hx + 52, hz + 42, 31, layers=4, ridge_axis="z")

    # Lecture hall
    lx, lz = mid_x, Z1 + 430
    add_hollow_box(fills, "dayan lecture", lx - 35, 1, lz - 25, lx + 35, 20, lz + 25, M.WOOD, thickness=1)
    add_ridge_roof(fills, "dayan lecture roof", lx - 40, lz - 30, lx + 40, lz + 30, 21, layers=2, ridge_axis="z")

    # Monk quarters
    for idx, qx in enumerate([X1 + 80, X2 - 80]):
        add_hollow_box(fills, f"dayan quarters {idx}", qx - 30, 1, Z1 + 200, qx + 30, 12, Z2 - 50, M.WHITE, thickness=1)
        add_ridge_roof(fills, f"dayan quarters roof {idx}", qx - 34, Z1 + 194, qx + 34, Z2 - 44, 13, layers=2, ridge_axis="z")

    # Pond and trees
    add_pool(fills, "dayan pond", X1 + 80, Z2 - 120, X2 - 80, Z2 - 60, 2)
    for tx, tz in [(X1 + 50, Z1 + 50), (X2 - 50, Z1 + 50), (X1 + 50, Z2 - 50), (X2 - 50, Z2 - 50)]:
        add_tree(fills, f"dayan tree {tx},{tz}", tx, tz, 2)


def main() -> None:
    run_builder(build_dayan_temple, "temple_dayan")


if __name__ == "__main__":
    main()
