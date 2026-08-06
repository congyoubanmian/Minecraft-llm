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
    add_ridge_roof,
    run_builder,
)


"""
Corner watch towers for the outer city wall.

Can be placed at the four corners of the 6000x6000 city square:
    (0, 0), (0, 6000), (6000, 0), (6000, 6000)
"""

TOWERS = [
    ("sw", 80, 80),
    ("nw", 80, 5920),
    ("se", 5920, 80),
    ("ne", 5920, 5920),
]


def build_corner_towers(fills: list[Fill]) -> None:
    for name, cx, cz in TOWERS:
        # Main tower body
        add_hollow_box(fills, f"corner {name} body", cx - 28, 1, cz - 28, cx + 28, 54, cz + 28, M.STONE, thickness=2)
        # Crenellated top
        add_fill(fills, f"corner {name} crenel", (cx - 30, 55, cz - 30), (cx + 30, 58, cz + 30), M.DARK)
        # Roof
        add_ridge_roof(fills, f"corner {name} roof", cx - 34, cz - 34, cx + 34, cz + 34, 59, layers=4, ridge_axis="z")
        # Beacon fire platform
        add_fill(fills, f"corner {name} beacon", (cx - 4, 67, cz - 4), (cx + 4, 72, cz + 4), M.GOLD)


def main() -> None:
    run_builder(build_corner_towers, "wall_corner_tower")


if __name__ == "__main__":
    main()
