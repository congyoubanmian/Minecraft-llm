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
Qinglong Temple (青龙寺) - important Tang Buddhist temple.

Location: local (4800, 800) .. (5300, 1300)
Features mountain gate, Buddha hall, pagoda, and sutra library.
"""

X1, Z1 = 4800, 800
X2, Z2 = 5300, 1300


def build_qinglong_temple(fills: list[Fill]) -> None:
    # Temple wall
    add_outline(fills, "qinglong wall", X1, Z1, X2, Z2, 1, 8, M.RED_WALL, thickness=2)

    # Mountain gate (south)
    mid_x = (X1 + X2) // 2
    add_fill(fills, "qinglong mountain gate", (mid_x - 16, 1, Z1 - 4), (mid_x + 16, 16, Z1 + 4), M.RED_WALL)
    add_ridge_roof(fills, "qinglong mountain gate roof", mid_x - 20, Z1 - 6, mid_x + 20, Z1 + 6, 17, layers=2, ridge_axis="z")

    # Buddha hall (Mahavira Hall)
    hx, hz = mid_x, (Z1 + Z2) // 2
    add_hollow_box(fills, "qinglong buddha hall", hx - 45, 1, hz - 35, hx + 45, 28, hz + 35, M.RED_WALL, thickness=2)
    add_ridge_roof(fills, "qinglong buddha hall roof", hx - 52, hz - 42, hx + 52, hz + 42, 29, layers=4, ridge_axis="z")

    # Pagoda
    px, pz = hx - 80, hz + 80
    y = 1
    for tier in range(5):
        r = 18 - tier * 2
        add_hollow_box(fills, f"qinglong pagoda t{tier}", px - r, y, pz - r, px + r, y + 8, pz + r, M.WHITE_TERRACOTTA, thickness=2)
        add_pagoda_openings(fills, f"qinglong pagoda t{tier}", px, pz, r, y, 8)
        add_pagoda_eave(fills, f"qinglong pagoda eave t{tier}", px, pz, r, y + 8)
        y += 9
    add_fill(fills, "qinglong pagoda spire", (px - 1, y, pz - 1), (px + 1, y + 12, pz + 1), M.GOLD)

    # Sutra library
    sx, sz = hx + 80, hz + 80
    add_hollow_box(fills, "qinglong sutra library", sx - 25, 1, sz - 20, sx + 25, 18, sz + 20, M.WOOD, thickness=1)
    add_ridge_roof(fills, "qinglong sutra roof", sx - 30, sz - 25, sx + 30, sz + 25, 19, layers=2, ridge_axis="z")

    # Pond and trees
    add_pool(fills, "qinglong pond", hx - 60, hz - 100, hx + 60, hz - 40, 2)
    for tx, tz in [(-100, -100), (100, -100), (-100, 100), (100, 100), (0, -120)]:
        add_tree(fills, f"qinglong tree {tx},{tz}", hx + tx, hz + tz, 2)


def main() -> None:
    run_builder(build_qinglong_temple, "temple_qinglong")


if __name__ == "__main__":
    main()
