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
Entertainment venues of Chang'an:
- Polo field (马球场) with spectator stands
- Leyou Park (乐游园) with pavilions and viewing terraces
"""


def build_polo_field(fills: list[Fill]) -> None:
    """Polo field east of the city, near Daxingshan Temple."""
    fx1, fz1 = 1800, 2200
    fx2, fz2 = 2600, 3000

    # Field surface - smooth sand/grass
    add_fill(fills, "polo field ground", (fx1, 1, fz1), (fx2, 1, fz2), M.SMOOTH)

    # Boundary markers
    add_outline(fills, "polo boundary", fx1, fz1, fx2, fz2, 1, 2, M.ANDESITE, thickness=1)

    # Goals at short ends
    add_fill(fills, "polo goal n", (fx1 + 20, 2, fz1 + 10), (fx1 + 60, 5, fz1 + 14), M.RED_WOOL)
    add_fill(fills, "polo goal s", (fx2 - 60, 2, fz2 - 14), (fx2 - 20, 5, fz2 - 10), M.RED_WOOL)

    # Spectator stands on east and west
    add_fill(fills, "polo west stand", (fx1 - 20, 2, fz1), (fx1 - 4, 6, fz2), M.WOOD)
    add_fill(fills, "polo east stand", (fx2 + 4, 2, fz1), (fx2 + 20, 6, fz2), M.WOOD)

    # Imperial viewing pavilion on north side
    vx, vz = (fx1 + fx2) // 2, fz1 - 40
    add_hollow_box(fills, "polo pavilion", vx - 30, 2, vz - 15, vx + 30, 14, vz + 15, M.RED_WALL, thickness=1)
    add_ridge_roof(fills, "polo pavilion roof", vx - 36, vz - 20, vx + 36, vz + 20, 15, layers=2, ridge_axis="z")


def build_leyou_park(fills: list[Fill]) -> None:
    """Leyou Park (乐游园) on the high ground south-east of the city."""
    px1, pz1 = 5000, 4800
    px2, pz2 = 5800, 5600

    # Terraced ground
    add_fill(fills, "leyou terrace", (px1, 1, pz1), (px2, 2, pz2), M.GRASS)

    # Main viewing pavilion (Qingqiu 清秋阁)
    cx, cz = (px1 + px2) // 2, (pz1 + pz2) // 2
    add_hollow_box(fills, "leyou qingqiu pavilion", cx - 28, 3, cz - 28, cx + 28, 22, cz + 28, M.RED_WALL, thickness=2)
    add_ridge_roof(fills, "leyou qingqiu roof", cx - 34, cz - 34, cx + 34, cz + 34, 23, layers=4, ridge_axis="z")
    add_fill(fills, "leyou qingqiu spire", (cx - 2, 31, cz - 2), (cx + 2, 38, cz + 2), M.GOLD)

    # Side pavilions
    for ox in (cx - 120, cx + 120):
        add_hollow_box(fills, f"leyou side {ox}", ox - 18, 3, cz - 18, ox + 18, 14, cz + 18, M.WOOD, thickness=1)
        add_ridge_roof(fills, f"leyou side roof {ox}", ox - 22, cz - 22, ox + 22, cz + 22, 15, layers=2, ridge_axis="z")

    # Wandering paths and trees
    for tx, tz in [(px1 + 80, pz1 + 80), (px2 - 80, pz1 + 80), (px1 + 80, pz2 - 80), (px2 - 80, pz2 - 80), (cx, pz1 + 60), (cx, pz2 - 60)]:
        add_tree(fills, f"leyou tree {tx},{tz}", tx, tz, 3, height=8, spread=3)

    # Stone tables and benches
    for tx, tz in [(cx - 80, cz + 80), (cx + 80, cz - 80)]:
        add_fill(fills, f"leyou table {tx},{tz}", (tx - 2, 3, tz - 2), (tx + 2, 4, tz + 2), M.ANDESITE)
        add_fill(fills, f"leyou bench {tx},{tz} n", (tx - 2, 3, tz - 6), (tx + 2, 3, tz - 3), M.WOOD)
        add_fill(fills, f"leyou bench {tx},{tz} s", (tx - 2, 3, tz + 3), (tx + 2, 3, tz + 6), M.WOOD)


def build_entertainment_venues(fills: list[Fill]) -> None:
    build_polo_field(fills)
    build_leyou_park(fills)


def main() -> None:
    run_builder(build_entertainment_venues, "entertainment_venues")


if __name__ == "__main__":
    main()
