from __future__ import annotations

import argparse
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
    add_lantern_line,
    add_ridge_roof,
    run_builder,
)


"""
Tang market block - a repeatable 120x120 shop quarter.

Can be tiled across East Market and West Market to create dense commercial
streets.  Each block contains:
    - Cross-shaped stone-paved street
    - Four shop units of varying trades
    - A central well or tree
    - Lantern posts
"""

BLOCK_SIZE = 120
SHOP_SIZE_X = 46
SHOP_SIZE_Z = 32

SHOP_TYPES = [
    ("tavern", M.RED_WOOL, M.RED_WALL),
    ("cloth", M.BLUE_WOOL, M.BLUE_WOOL),
    ("tea", M.YELLOW_WOOL, M.YELLOW_WOOL),
    ("iron", M.SMOOTH, M.DARK),
]


def build_market_block(
    fills: list[Fill],
    origin_x: int = 0,
    origin_z: int = 0,
    base_y: int = 2,
) -> None:
    """Build one repeatable market quarter at local (origin_x, origin_z)."""
    x1, z1 = origin_x, origin_z
    x2, z2 = origin_x + BLOCK_SIZE, origin_z + BLOCK_SIZE
    mid_x, mid_z = (x1 + x2) // 2, (z1 + z2) // 2

    # Cross-shaped paved street
    street_width = 12
    add_fill(fills, "market street x", (x1, base_y, mid_z - street_width // 2), (x2, base_y, mid_z + street_width // 2), M.SMOOTH)
    add_fill(fills, "market street z", (mid_x - street_width // 2, base_y, z1), (mid_x + street_width // 2, base_y, z2), M.SMOOTH)

    # Four shop quadrants
    shop_origins = [
        (x1 + 8, z1 + 8, "south"),
        (x2 - 8 - SHOP_SIZE_X, z1 + 8, "south"),
        (x1 + 8, z2 - 8 - SHOP_SIZE_Z, "north"),
        (x2 - 8 - SHOP_SIZE_X, z2 - 8 - SHOP_SIZE_Z, "north"),
    ]

    for index, (sx, sz, facing) in enumerate(shop_origins):
        shop_type, sign_block, wall_block = SHOP_TYPES[index % len(SHOP_TYPES)]
        add_hollow_box(fills, f"market {shop_type} {index}", sx, base_y + 1, sz, sx + SHOP_SIZE_X, base_y + 12, sz + SHOP_SIZE_Z, wall_block, thickness=1)
        # Roof
        add_ridge_roof(fills, f"market {shop_type} {index} roof", sx - 4, sz - 4, sx + SHOP_SIZE_X + 4, sz + SHOP_SIZE_Z + 4, base_y + 13, layers=2, ridge_axis="z")
        # Signboard on front
        if facing == "south":
            add_fill(fills, f"market {shop_type} {index} sign", (sx + 8, base_y + 8, sz - 1), (sx + SHOP_SIZE_X - 8, base_y + 11, sz - 1), sign_block)
        else:
            add_fill(fills, f"market {shop_type} {index} sign", (sx + 8, base_y + 8, sz + SHOP_SIZE_Z + 1), (sx + SHOP_SIZE_X - 8, base_y + 11, sz + SHOP_SIZE_Z + 1), sign_block)

    # Central feature (well)
    add_fill(fills, "market well curb", (mid_x - 6, base_y, mid_z - 6), (mid_x + 6, base_y + 2, mid_z + 6), M.ANDESITE)
    add_fill(fills, "market well water", (mid_x - 4, base_y, mid_z - 4), (mid_x + 4, base_y, mid_z + 4), M.WATER)

    # Lanterns along streets
    add_lantern_line(fills, "market lamps x", mid_x, z1 + 20, mid_x, z2 - 20, base_y + 1, 30)
    add_lantern_line(fills, "market lamps z", x1 + 20, mid_z, x2 - 20, mid_z, base_y + 1, 30)


def build_all_market_blocks(fills: list[Fill]) -> None:
    """Tile market blocks across West Market and East Market."""
    markets = [
        (760, 2060, 1760, 3060),   # West Market
        (4240, 2060, 5240, 3060),  # East Market
    ]
    for mx1, mz1, mx2, mz2 in markets:
        for x in range(mx1, mx2 - BLOCK_SIZE + 1, BLOCK_SIZE):
            for z in range(mz1, mz2 - BLOCK_SIZE + 1, BLOCK_SIZE):
                build_market_block(fills, origin_x=x, origin_z=z)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build repeatable Tang market blocks.")
    parser.add_argument("--single", action="store_true", help="Build only one demo block at (0,0).")
    # Parse only our custom flag; pass the rest to run_builder later.
    args, remaining = parser.parse_known_args()
    sys.argv = [sys.argv[0], *remaining]

    if args.single:
        run_builder(lambda fills: build_market_block(fills, origin_x=0, origin_z=0), "market_block_single")
    else:
        run_builder(build_all_market_blocks, "market_block")


if __name__ == "__main__":
    main()
