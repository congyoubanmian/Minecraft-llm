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
Official residence / prince's mansion (王府/官邸).

A larger and more ornate courtyard compound that can be placed in
important wards near the palace.
"""

RESIDENCES = [
    ("qin_wang_fu", 2200, 3600),   # 秦王府
    ("qi_wang_fu", 3800, 3600),    # 齐王府
    ("wei_guo_gong", 3350, 3350),  # 卫国公府
]


def build_residence(fills: list[Fill], name: str, cx: int, cz: int) -> None:
    x1, z1 = cx - 90, cz - 80
    x2, z2 = cx + 90, cz + 80

    # Outer wall
    add_outline(fills, f"{name} wall", x1, z1, x2, z2, 1, 8, M.RED_WALL, thickness=2)

    # Main gate
    add_fill(fills, f"{name} gate", (cx - 16, 1, z1 - 4), (cx + 16, 14, z1 + 4), M.RED_WALL)
    add_ridge_roof(fills, f"{name} gate roof", cx - 20, z1 - 6, cx + 20, z1 + 6, 15, layers=2, ridge_axis="z")

    # Screen wall (yingbi)
    add_fill(fills, f"{name} screen", (cx - 20, 1, z1 + 20), (cx + 20, 10, z1 + 24), M.WHITE)

    # Front hall
    add_hollow_box(fills, f"{name} front hall", cx - 50, 1, z1 + 40, cx + 50, 18, z1 + 90, M.RED_WALL, thickness=2)
    add_ridge_roof(fills, f"{name} front roof", cx - 56, z1 + 34, cx + 56, z1 + 96, 19, layers=3, ridge_axis="z")

    # Rear hall
    add_hollow_box(fills, f"{name} rear hall", cx - 40, 1, z1 + 110, cx + 40, 16, z1 + 150, M.WOOD, thickness=1)
    add_ridge_roof(fills, f"{name} rear roof", cx - 46, z1 + 104, cx + 46, z1 + 156, 17, layers=2, ridge_axis="z")

    # Side wings
    add_hollow_box(fills, f"{name} west wing", x1 + 10, 1, z1 + 60, x1 + 35, 12, z1 + 140, M.WHITE, thickness=1)
    add_hollow_box(fills, f"{name} east wing", x2 - 35, 1, z1 + 60, x2 - 10, 12, z1 + 140, M.WHITE, thickness=1)
    add_ridge_roof(fills, f"{name} west wing roof", x1 + 4, z1 + 54, x1 + 41, z1 + 146, 13, layers=2, ridge_axis="z")
    add_ridge_roof(fills, f"{name} east wing roof", x2 - 41, z1 + 54, x2 - 4, z1 + 146, 13, layers=2, ridge_axis="z")

    # Courtyard pond
    add_pool(fills, f"{name} pond", cx - 25, z1 + 95, cx + 25, z1 + 130, 2)

    # Garden trees
    for tx, tz in [(-60, -50), (60, -50), (-60, 50), (60, 50), (0, 60)]:
        add_tree(fills, f"{name} tree {tx},{tz}", cx + tx, cz + tz, 2)


def build_all_residences(fills: list[Fill]) -> None:
    for name, cx, cz in RESIDENCES:
        build_residence(fills, name, cx, cz)


def main() -> None:
    run_builder(build_all_residences, "official_residence")


if __name__ == "__main__":
    main()
