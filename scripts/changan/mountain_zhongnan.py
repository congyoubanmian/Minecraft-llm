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
    add_tree,
    run_builder,
)


"""
Zhongnan Mountain (终南山) distant view south of Chang'an.

Creates a stylized mountain range far beyond the city wall to serve as a
backdrop.  Kept low-detail to save commands.
"""


def build_zhongnan_mountain(fills: list[Fill]) -> None:
    # Mountain ridge south of the city, from x=-500 to x=6500, z=-800 to z=-400
    # Main peaks
    peaks = [
        (-200, -700, 40, 120),
        (800, -650, 50, 140),
        (2000, -720, 60, 160),
        (3200, -680, 70, 180),
        (4500, -710, 55, 150),
        (5800, -670, 45, 130),
    ]

    for idx, (cx, cz, half_width, height) in enumerate(peaks):
        # Triangular mountain core
        for y in range(height):
            inset = y // 2
            current_half = max(1, half_width - inset)
            add_fill(fills, f"zhongnan peak {idx} layer {y}", (cx - current_half, y, cz - current_half), (cx + current_half, y, cz + current_half), M.STONE if y < height // 2 else M.GRASS)

    # Forest on mountain slopes
    for cx, cz, _, _ in peaks:
        for tx, tz in [(-20, -20), (20, -20), (-20, 20), (20, 20), (0, -30), (0, 30)]:
            add_tree(fills, f"zhongnan tree {cx},{cz},{tx},{tz}", cx + tx, cz + tz, 10, height=5, spread=2)


def main() -> None:
    run_builder(build_zhongnan_mountain, "mountain_zhongnan")


if __name__ == "__main__":
    main()
