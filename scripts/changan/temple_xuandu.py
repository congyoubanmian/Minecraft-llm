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
Xuandu Temple (玄都观) - Taoist temple famous in Tang literature.

Location: local (4600, 3500) .. (5100, 4000)
"""

X1, Z1 = 4600, 3500
X2, Z2 = 5100, 4000


def build_xuandu_temple(fills: list[Fill]) -> None:
    # Temple wall
    add_outline(fills, "xuandu wall", X1, Z1, X2, Z2, 1, 8, M.GRAY_CONCRETE if hasattr(M, 'GRAY_CONCRETE') else M.DARK, thickness=2)

    # Gate (use DARK if no gray concrete)
    gate_block = M.GRAY_CONCRETE if hasattr(M, 'GRAY_CONCRETE') else M.DARK
    mid_x = (X1 + X2) // 2
    add_fill(fills, "xuandu gate", (mid_x - 14, 1, Z1 - 4), (mid_x + 14, 14, Z1 + 4), gate_block)
    add_ridge_roof(fills, "xuandu gate roof", mid_x - 18, Z1 - 6, mid_x + 18, Z1 + 6, 15, layers=2, ridge_axis="z")

    # Sanqing Hall (main Taoist hall)
    hx, hz = mid_x, Z1 + 160
    add_hollow_box(fills, "xuandu sanqing", hx - 40, 1, hz - 30, hx + 40, 26, hz + 30, gate_block, thickness=2)
    add_ridge_roof(fills, "xuandu sanqing roof", hx - 46, hz - 36, hx + 46, hz + 36, 27, layers=3, ridge_axis="z")

    # Side pavilions for the Three Pure Ones
    for idx, px in enumerate([hx - 90, hx + 90]):
        add_hollow_box(fills, f"xuandu pavilion {idx}", px - 18, 1, hz - 15, px + 18, 18, hz + 15, M.WOOD, thickness=1)
        add_ridge_roof(fills, f"xuandu pavilion roof {idx}", px - 22, hz - 19, px + 22, hz + 19, 19, layers=2, ridge_axis="z")

    # Taoist scripture pavilion
    sx, sz = hx, Z1 + 300
    add_hollow_box(fills, "xuandu scripture", sx - 25, 1, sz - 20, sx + 25, 18, sz + 20, M.WOOD, thickness=1)
    add_ridge_roof(fills, "xuandu scripture roof", sx - 30, sz - 25, sx + 30, sz + 25, 19, layers=2, ridge_axis="z")

    # Peach orchard (玄都观以桃花闻名)
    for tx, tz in [(X1 + 60, Z1 + 60), (X2 - 60, Z1 + 60), (X1 + 60, Z2 - 60), (X2 - 60, Z2 - 60), (mid_x, Z1 + 80), (mid_x, Z2 - 80)]:
        add_tree(fills, f"xuandu peach {tx},{tz}", tx, tz, 2, height=5, spread=3)

    # Reflecting pond
    add_pool(fills, "xuandu pond", X1 + 80, Z2 - 120, X2 - 80, Z2 - 60, 2)


def main() -> None:
    run_builder(build_xuandu_temple, "temple_xuandu")


if __name__ == "__main__":
    main()
