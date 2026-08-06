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
Xingqing Palace (兴庆宫) - the Southern Palace, leisure palace of Tang emperors.

Location: local (900, 800) .. (1700, 1600) (north-east of the city)
Features a central lake (Longqing Pool), flower-attending tower, and pavilions.
"""

X1, Z1 = 900, 800
X2, Z2 = 1700, 1600


def build_xingqing_palace(fills: list[Fill]) -> None:
    # Palace wall
    add_outline(fills, "xingqing wall", X1, Z1, X2, Z2, 1, 8, M.RED_WALL, thickness=2)

    # Main gate (Xingqing Gate) on west side
    add_fill(fills, "xingqing gate", (X1 - 3, 1, (Z1 + Z2) // 2 - 14), (X1 + 3, 14, (Z1 + Z2) // 2 + 14), M.RED_WALL)
    add_ridge_roof(fills, "xingqing gate roof", X1 - 5, (Z1 + Z2) // 2 - 18, X1 + 5, (Z1 + Z2) // 2 + 18, 15, layers=2, ridge_axis="x")

    # Longqing Pool (large central lake)
    cx, cz = (X1 + X2) // 2, (Z1 + Z2) // 2
    add_pool(fills, "xingqing longqing pool", cx - 200, cz - 150, cx + 200, cz + 150, 2)

    # Flower-Attending Tower (Huazheng Xianghui Lou) on southwest
    tx, tz = X1 + 120, Z2 - 120
    add_hollow_box(fills, "xingqing flower tower", tx - 28, 1, tz - 28, tx + 28, 42, tz + 28, M.RED_WALL, thickness=2)
    add_ridge_roof(fills, "xingqing flower tower roof", tx - 34, tz - 34, tx + 34, tz + 34, 43, layers=5, ridge_axis="z")
    add_fill(fills, "xingqing flower tower spire", (tx - 2, 53, tz - 2), (tx + 2, 68, tz + 2), M.GOLD)

    # Chenxiang Pavilion in lake
    add_fill(fills, "xingqing chenxiang base", (cx - 20, 1, cz - 20), (cx + 20, 3, cz + 20), M.WHITE)
    add_hollow_box(fills, "xingqing chenxiang pavilion", cx - 16, 4, cz - 16, cx + 16, 22, cz + 16, M.RED_WALL, thickness=1)
    add_ridge_roof(fills, "xingqing chenxiang roof", cx - 22, cz - 22, cx + 22, cz + 22, 23, layers=3, ridge_axis="z")

    # Garden trees scattered
    for tx, tz in [
        (X1 + 80, Z1 + 80), (X2 - 80, Z1 + 80), (X1 + 80, Z2 - 80), (X2 - 80, Z2 - 80),
        (cx - 150, cz - 200), (cx + 150, cz - 200), (cx - 150, cz + 200), (cx + 150, cz + 200),
    ]:
        add_tree(fills, f"xingqing tree {tx},{tz}", tx, tz, 2)


def main() -> None:
    run_builder(build_xingqing_palace, "palace_xingqing")


if __name__ == "__main__":
    main()
