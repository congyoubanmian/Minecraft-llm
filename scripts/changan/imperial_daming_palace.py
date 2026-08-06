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
Daming Palace (大明宫) overall enhancement:
- Complete palace wall with gates
- Danfeng Gate (main south gate)
- Taiye Pool (太液池) with pavilion
- Scattered pavilions and gardens in the inner court

This wraps around the three main halls (Hanyuan, Xuanzheng, Zichen)
which have their own dedicated modules.
"""

# Daming Palace footprint in local coords
X1, Z1 = 1800, 4100
X2, Z2 = 4200, 5820


def build_daming_palace(fills: list[Fill]) -> None:
    # Outer palace wall with crenellations
    add_outline(fills, "daming wall", X1, Z1, X2, Z2, 1, 22, M.STONE, thickness=3)
    for x in range(X1, X2 + 1, 16):
        add_fill(fills, f"daming crenel n {x}", (x, 23, Z1), (x + 4, 25, Z1 + 3), M.DARK)
        add_fill(fills, f"daming crenel s {x}", (x, 23, Z2 - 3), (x + 4, 25, Z2), M.DARK)
    for z in range(Z1, Z2 + 1, 16):
        add_fill(fills, f"daming crenel w {z}", (X1, 23, z), (X1 + 3, 25, z + 4), M.DARK)
        add_fill(fills, f"daming crenel e {z}", (X2 - 3, 23, z), (X2, 25, z + 4), M.DARK)

    # Danfeng Gate (main south gate, five gateways)
    mid_x = (X1 + X2) // 2
    add_hollow_box(fills, "daming danfeng tower", mid_x - 55, 23, Z1 - 50, mid_x + 55, 58, Z1 + 50, M.RED_WALL, thickness=2)
    for gx in range(mid_x - 36, mid_x + 37, 18):
        add_fill(fills, f"daming danfeng passage {gx}", (gx - 5, 1, Z1 - 55), (gx + 5, 22, Z1 + 55), M.AIR)
    add_ridge_roof(fills, "daming danfeng roof", mid_x - 62, Z1 - 58, mid_x + 62, Z1 + 58, 59, layers=5, ridge_axis="z")

    # Side que towers
    for ox in (mid_x - 150, mid_x + 150):
        add_hollow_box(fills, f"daming que {ox}", ox - 22, 1, Z1 - 35, ox + 22, 48, Z1 + 35, M.STONE, thickness=2)
        add_ridge_roof(fills, f"daming que roof {ox}", ox - 28, Z1 - 40, ox + 28, Z1 + 40, 49, layers=4, ridge_axis="z")

    # Taiye Pool (large lake in the inner court)
    add_pool(fills, "daming taiye pool", mid_x - 220, Z2 - 320, mid_x + 220, Z2 - 80, 2)

    # Penglai Pavilion in the middle of Taiye Pool
    px, pz = mid_x, Z2 - 200
    add_fill(fills, "daming penglai base", (px - 30, 1, pz - 30), (px + 30, 3, pz + 30), M.WHITE)
    add_hollow_box(fills, "daming penglai pavilion", px - 24, 4, pz - 24, px + 24, 28, pz + 24, M.RED_WALL, thickness=1)
    add_ridge_roof(fills, "daming penglai roof", px - 30, pz - 30, px + 30, pz + 30, 29, layers=3, ridge_axis="z")

    # Scattered garden pavilions
    pavilions = [
        (mid_x - 300, Z2 - 450),
        (mid_x + 300, Z2 - 450),
        (mid_x - 350, Z2 - 250),
        (mid_x + 350, Z2 - 120),
    ]
    for idx, (px, pz) in enumerate(pavilions):
        add_hollow_box(fills, f"daming pavilion {idx}", px - 18, 1, pz - 18, px + 18, 16, pz + 18, M.WOOD, thickness=1)
        add_ridge_roof(fills, f"daming pavilion {idx} roof", px - 24, pz - 24, px + 24, pz + 24, 17, layers=2, ridge_axis="z")

    # Garden trees around Taiye Pool
    for tx, tz in [(-180, -340), (180, -340), (-250, -150), (250, -150), (-150, -280), (150, -280)]:
        add_tree(fills, f"daming tree {tx},{tz}", mid_x + tx, Z2 + tz, 2)


def main() -> None:
    run_builder(build_daming_palace, "imperial_daming_palace")


if __name__ == "__main__":
    main()
