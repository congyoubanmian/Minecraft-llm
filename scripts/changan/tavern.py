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
Tang-style tavern / restaurant (酒楼) - repeatable commercial building.

Can be tiled along market streets.  Features:
    - Two-storey timber-framed body
    - Overhanging upper floor (common Tang feature)
    - Coloured signboard and banner
    - Outdoor seating platform
"""


def build_tavern(
    fills: list[Fill],
    x: int = 0,
    z: int = 0,
    width: int = 36,
    depth: int = 28,
    height: int = 18,
    facing: str = "south",
    sign_colour: str = M.RED_WOOL,
) -> None:
    """Build one tavern at local (x, z)."""
    y = 2

    # Ground floor
    add_hollow_box(fills, f"tavern {x},{z} ground", x, y, z, x + width, y + 8, z + depth, M.WOOD, thickness=1)
    # Upper floor with overhang
    add_hollow_box(fills, f"tavern {x},{z} upper", x - 3, y + 9, z - 3, x + width + 3, y + height, z + depth + 3, M.WOOD, thickness=1)

    # Roof
    add_ridge_roof(fills, f"tavern {x},{z} roof", x - 6, z - 6, x + width + 6, z + depth + 6, y + height + 1, layers=2, ridge_axis="z")

    # Signboard
    if facing == "south":
        add_fill(fills, f"tavern {x},{z} sign", (x + 6, y + 6, z - 2), (x + width - 6, y + 10, z - 1), sign_colour)
    else:
        add_fill(fills, f"tavern {x},{z} sign", (x + 6, y + 6, z + depth + 1), (x + width - 6, y + 10, z + depth + 2), sign_colour)

    # Outdoor seating platform
    add_fill(fills, f"tavern {x},{z} platform", (x - 6, y, z - 6 if facing == "south" else z + depth), (x + width + 6, y, z if facing == "south" else z + depth + 6), M.SMOOTH)

    # Banner pole
    pole_x = x + width + 8
    pole_z = z + depth // 2
    add_fill(fills, f"tavern {x},{z} pole", (pole_x, y, pole_z - 1), (pole_x, y + 16, pole_z + 1), M.LOG)
    add_fill(fills, f"tavern {x},{z} banner", (pole_x + 1, y + 10, pole_z - 4), (pole_x + 1, y + 15, pole_z + 4), sign_colour)


def build_taverns_in_markets(fills: list[Fill]) -> None:
    """Scatter taverns along the edges of East and West Markets."""
    markets = [
        (760, 2060, 1760, 3060),   # West Market
        (4240, 2060, 5240, 3060),  # East Market
    ]
    for mx1, mz1, mx2, mz2 in markets:
        # North and south rows of taverns
        for x in range(mx1 + 20, mx2 - 60, 60):
            build_tavern(fills, x, mz1 + 8, facing="south", sign_colour=M.RED_WOOL)
            build_tavern(fills, x, mz2 - 36, facing="north", sign_colour=M.BLUE_WOOL)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build Tang-style taverns.")
    parser.add_argument("--single", action="store_true", help="Build one demo tavern at (0,0).")
    args, remaining = parser.parse_known_args()
    sys.argv = [sys.argv[0], *remaining]

    if args.single:
        run_builder(lambda fills: build_tavern(fills, x=0, z=0, facing="south"), "tavern_single")
    else:
        run_builder(build_taverns_in_markets, "tavern")


if __name__ == "__main__":
    main()
