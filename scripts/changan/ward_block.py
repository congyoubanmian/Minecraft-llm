from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    WARD_BLOCK_SIZE,
    Fill,
    Materials as M,
    add_fill,
    add_hollow_box,
    add_lantern_line,
    add_outline,
    add_pool,
    add_ridge_roof,
    add_tree,
    iter_ward_origins,
    run_builder,
)


"""
Tang ward (fang 坊) block - a repeatable 260x260 residential quarter.

Can be tiled across the 108 wards of Chang'an.  Each ward contains:
    - Perimeter ward wall with paifang gate
    - Cross-shaped internal lane
    - Courtyard houses, a small temple, and trees
    - A central public well
"""

WALL_HEIGHT = 7


def build_ward_block(
    fills: list[Fill],
    origin_x: int = 0,
    origin_z: int = 0,
    base_y: int = 1,
) -> None:
    """Build one repeatable residential ward at local (origin_x, origin_z)."""
    x1, z1 = origin_x, origin_z
    x2, z2 = origin_x + WARD_BLOCK_SIZE, origin_z + WARD_BLOCK_SIZE
    mid_x, mid_z = (x1 + x2) // 2, (z1 + z2) // 2

    # Perimeter wall
    add_outline(fills, "ward wall", x1, z1, x2, z2, base_y, base_y + WALL_HEIGHT, M.STONE, thickness=3)

    # Paifang gate on south side
    gate_x = mid_x
    add_fill(fills, "ward gate left pillar", (gate_x - 18, base_y, z1 - 3), (gate_x - 13, base_y + 18, z1 + 3), M.RED_WALL)
    add_fill(fills, "ward gate right pillar", (gate_x + 13, base_y, z1 - 3), (gate_x + 18, base_y + 18, z1 + 3), M.RED_WALL)
    add_fill(fills, "ward gate beam", (gate_x - 22, base_y + 18, z1 - 4), (gate_x + 22, base_y + 22, z1 + 4), M.WOOD)
    add_ridge_roof(fills, "ward gate roof", gate_x - 26, z1 - 6, gate_x + 26, z1 + 6, base_y + 23, layers=2, ridge_axis="z")

    # Internal cross lane
    lane_width = 8
    add_fill(fills, "ward lane x", (x1 + 10, base_y, mid_z - lane_width // 2), (x2 - 10, base_y, mid_z + lane_width // 2), M.SMOOTH)
    add_fill(fills, "ward lane z", (mid_x - lane_width // 2, base_y, z1 + 10), (mid_x + lane_width // 2, base_y, z2 - 10), M.SMOOTH)

    # Four courtyard mansions in quadrants
    mansion_size = 70
    mansion_origins = [
        (x1 + 25, z1 + 25),
        (x2 - 25 - mansion_size, z1 + 25),
        (x1 + 25, z2 - 25 - mansion_size),
        (x2 - 25 - mansion_size, z2 - 25 - mansion_size),
    ]
    for index, (mx, mz) in enumerate(mansion_origins):
        # Courtyard wall
        add_outline(fills, f"ward mansion {index} wall", mx, mz, mx + mansion_size, mz + mansion_size, base_y, base_y + 6, M.WHITE, thickness=1)
        # Main house
        add_hollow_box(fills, f"ward mansion {index} house", mx + 15, base_y + 1, mz + 15, mx + mansion_size - 15, base_y + 10, mz + mansion_size - 15, M.WOOD, thickness=1)
        add_ridge_roof(fills, f"ward mansion {index} roof", mx + 10, mz + 10, mx + mansion_size - 10, mz + mansion_size - 10, base_y + 11, layers=2, ridge_axis="z")
        # Courtyard garden
        add_fill(fills, f"ward mansion {index} courtyard", (mx + 20, base_y, mz + 20), (mx + mansion_size - 20, base_y, mz + mansion_size - 20), M.GRASS)
        add_tree(fills, f"ward mansion {index} tree", mx + mansion_size // 2, mz + mansion_size // 2, base_y + 1)

    # Small temple in one corner
    tx, tz = x1 + 150, z1 + 25
    add_hollow_box(fills, "ward temple hall", tx, base_y + 1, tz, tx + 50, base_y + 14, tz + 40, M.RED_WALL, thickness=1)
    add_ridge_roof(fills, "ward temple roof", tx - 6, tz - 6, tx + 56, tz + 46, base_y + 15, layers=3, ridge_axis="z")
    add_fill(fills, "ward temple incense", (tx + 22, base_y + 1, tz + 45), (tx + 28, base_y + 3, tz + 50), M.GOLD)

    # Central well
    add_fill(fills, "ward well curb", (mid_x - 5, base_y, mid_z - 5), (mid_x + 5, base_y + 2, mid_z + 5), M.ANDESITE)
    add_fill(fills, "ward well water", (mid_x - 3, base_y, mid_z - 3), (mid_x + 3, base_y, mid_z + 3), M.WATER)

    # Street lamps along lanes
    add_lantern_line(fills, "ward lamps x", mid_x, z1 + 30, mid_x, z2 - 30, base_y + 1, 40)
    add_lantern_line(fills, "ward lamps z", x1 + 30, mid_z, x2 - 30, mid_z, base_y + 1, 40)


def build_all_ward_blocks(fills: list[Fill]) -> None:
    """Tile ward blocks across the residential grid, skipping imperial/market areas."""
    for x, z in iter_ward_origins():
        build_ward_block(fills, origin_x=x, origin_z=z)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build repeatable Tang ward blocks.")
    parser.add_argument("--single", action="store_true", help="Build only one demo block at (520,620).")
    args, remaining = parser.parse_known_args()
    sys.argv = [sys.argv[0], *remaining]

    if args.single:
        run_builder(lambda fills: build_ward_block(fills, origin_x=520, origin_z=620), "ward_block_single")
    else:
        run_builder(build_all_ward_blocks, "ward_block")


if __name__ == "__main__":
    main()
