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
    add_ridge_roof,
    add_tree,
    run_builder,
)


"""
Central government offices in the Imperial City:
- Shangshu Sheng (尚书省)
- Yushi Tai (御史台)
- Dali Si (大理寺)
- Honglu Si (鸿胪寺)
"""

OFFICES = [
    ("shangshu_sheng", 2000, 4200, "尚书省"),
    ("yushi_tai", 2200, 4400, "御史台"),
    ("dali_si", 2400, 4200, "大理寺"),
    ("honglu_si", 2600, 4400, "鸿胪寺"),
]


def build_office(fills: list[Fill], name: str, cx: int, cz: int, label: str) -> None:
    x1, z1 = cx - 70, cz - 55
    x2, z2 = cx + 70, cz + 55

    # Compound wall
    add_outline(fills, f"{name} wall", x1, z1, x2, z2, 1, 7, M.STONE, thickness=2)

    # Main gate
    add_fill(fills, f"{name} gate", (cx - 14, 1, z1 - 4), (cx + 14, 12, z1 + 4), M.RED_WALL)
    add_ridge_roof(fills, f"{name} gate roof", cx - 18, z1 - 6, cx + 18, z1 + 6, 13, layers=2, ridge_axis="z")

    # Main hall
    add_hollow_box(fills, f"{name} hall", cx - 45, 1, z1 + 30, cx + 45, 20, z1 + 90, M.RED_WALL, thickness=2)
    add_ridge_roof(fills, f"{name} hall roof", cx - 52, z1 + 24, cx + 52, z1 + 96, 21, layers=3, ridge_axis="z")

    # Side offices
    add_hollow_box(fills, f"{name} west office", x1 + 10, 1, z1 + 100, x1 + 40, 12, z2 - 10, M.WHITE, thickness=1)
    add_hollow_box(fills, f"{name} east office", x2 - 40, 1, z1 + 100, x2 - 10, 12, z2 - 10, M.WHITE, thickness=1)
    add_ridge_roof(fills, f"{name} west office roof", x1 + 4, z1 + 94, x1 + 46, z2 - 4, 13, layers=2, ridge_axis="z")
    add_ridge_roof(fills, f"{name} east office roof", x2 - 46, z1 + 94, x2 - 4, z2 - 4, 13, layers=2, ridge_axis="z")

    # Courtyard
    add_fill(fills, f"{name} courtyard", (x1 + 45, 1, z1 + 100), (x2 - 45, 1, z2 - 10), M.SMOOTH)

    # Trees
    for tx, tz in [(-50, -40), (50, -40), (-50, 40), (50, 40)]:
        add_tree(fills, f"{name} tree {tx},{tz}", cx + tx, cz + tz, 2)


def build_government_offices(fills: list[Fill]) -> None:
    for name, cx, cz, label in OFFICES:
        build_office(fills, name, cx, cz, label)


def main() -> None:
    run_builder(build_government_offices, "government_offices")


if __name__ == "__main__":
    main()
