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
    iter_ward_origins,
    run_builder,
)


"""
Drainage system for Chang'an:
- Stone-lined open ditches along main avenues
- Underground drain covers (manholes) at major intersections
- Small gutters and rain-water drains along ward lanes
"""


AVENUE_XS = [900, 1800, 3000, 4200, 5100]
AVENUE_ZS = [900, 1700, 2500, 3300, 4100, 5000]


def build_avenue_ditches(fills: list[Fill]) -> None:
    """Main avenue drainage channels."""
    for x in AVENUE_XS:
        add_fill(fills, f"ditch x={x} west", (x - 38, 1, 80), (x - 35, 0, 5999 - 80), M.ANDESITE)
        add_fill(fills, f"ditch x={x} east", (x + 35, 1, 80), (x + 38, 0, 5999 - 80), M.ANDESITE)
        add_fill(fills, f"ditch x={x} water w", (x - 37, 1, 80), (x - 36, 1, 5999 - 80), M.WATER)
        add_fill(fills, f"ditch x={x} water e", (x + 36, 1, 80), (x + 37, 1, 5999 - 80), M.WATER)

    for z in AVENUE_ZS:
        add_fill(fills, f"ditch z={z} north", (80, 1, z - 38), (5999 - 80, 0, z - 35), M.ANDESITE)
        add_fill(fills, f"ditch z={z} south", (80, 1, z + 35), (5999 - 80, 0, z + 38), M.ANDESITE)
        add_fill(fills, f"ditch z={z} water n", (80, 1, z - 37), (5999 - 80, 1, z - 36), M.WATER)
        add_fill(fills, f"ditch z={z} water s", (80, 1, z + 36), (5999 - 80, 1, z + 37), M.WATER)


def build_manholes(fills: list[Fill]) -> None:
    """Drain covers at every major avenue intersection."""
    idx = 0
    for x in AVENUE_XS:
        for z in AVENUE_ZS:
            add_fill(fills, f"manhole {idx}", (x - 2, 3, z - 2), (x + 2, 3, z + 2), M.DARK)
            idx += 1


def build_ward_gutters(fills: list[Fill]) -> None:
    """Small drains at the corners of ward internal lanes."""
    for origin_index, (x, z) in enumerate(iter_ward_origins()):
        mid_x, mid_z = x + 130, z + 130
        # One drain at each corner of the cross-shaped lane
        corners = [
            (x + 20, mid_z - 3),
            (x + 240, mid_z - 3),
            (x + 20, mid_z + 3),
            (x + 240, mid_z + 3),
            (mid_x - 3, z + 20),
            (mid_x - 3, z + 240),
            (mid_x + 3, z + 20),
            (mid_x + 3, z + 240),
        ]
        for cx, cz in corners:
            add_fill(fills, f"ward drain {origin_index} {cx},{cz}", (cx - 1, 1, cz - 1), (cx + 1, 1, cz + 1), M.GRAY_CONCRETE)


def build_drainage_ditches(fills: list[Fill]) -> None:
    build_avenue_ditches(fills)
    build_manholes(fills)
    build_ward_gutters(fills)


def main() -> None:
    run_builder(build_drainage_ditches, "drainage_ditches")


if __name__ == "__main__":
    main()
