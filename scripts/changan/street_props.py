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
Street props: horse carts, sedan chairs, market stalls, vendor carts,
water buckets, and street-side benches.

Distributed across:
- Main avenue intersections
- Market blocks (East/West Markets)
- Ward internal lanes
- Palace approach roads
"""


def add_cart(fills: list[Fill], x: int, z: int, facing: str = "z") -> None:
    """Simple two-wheeled cart."""
    if facing == "z":
        add_fill(fills, f"cart {x},{z} body", (x - 3, 2, z - 5), (x + 3, 4, z + 5), M.WOOD)
        add_fill(fills, f"cart {x},{z} wheel w", (x - 4, 1, z - 4), (x - 2, 3, z - 2), M.DARK)
        add_fill(fills, f"cart {x},{z} wheel e", (x + 2, 1, z - 4), (x + 4, 3, z - 2), M.DARK)
        add_fill(fills, f"cart {x},{z} shaft", (x - 1, 2, z - 9), (x + 1, 3, z - 6), M.LOG)
    else:
        add_fill(fills, f"cart {x},{z} body", (x - 5, 2, z - 3), (x + 5, 4, z + 3), M.WOOD)
        add_fill(fills, f"cart {x},{z} wheel n", (x - 4, 1, z - 4), (x - 2, 3, z - 2), M.DARK)
        add_fill(fills, f"cart {x},{z} wheel s", (x - 4, 1, z + 2), (x - 2, 3, z + 4), M.DARK)
        add_fill(fills, f"cart {x},{z} shaft", (x - 9, 2, z - 1), (x - 6, 3, z + 1), M.LOG)


def add_sedan_chair(fills: list[Fill], x: int, z: int) -> None:
    """A sedan chair carried by two poles."""
    add_fill(fills, f"sedan {x},{z} cabin", (x - 2, 2, z - 2), (x + 2, 6, z + 2), M.RED_WOOL)
    add_fill(fills, f"sedan {x},{z} pole 1", (x - 8, 3, z - 1), (x - 2, 4, z + 1), M.LOG)
    add_fill(fills, f"sedan {x},{z} pole 2", (x + 2, 3, z - 1), (x + 8, 4, z + 1), M.LOG)
    add_fill(fills, f"sedan {x},{z} curtain", (x - 1, 3, z + 2), (x + 1, 5, z + 3), M.YELLOW_WOOL)


def add_market_stall(fills: list[Fill], x: int, z: int, color: str = M.RED_WOOL) -> None:
    """A simple market stall with awning."""
    add_fill(fills, f"stall {x},{z} table", (x - 3, 2, z - 2), (x + 3, 3, z + 2), M.WOOD)
    add_fill(fills, f"stall {x},{z} awning", (x - 4, 5, z - 3), (x + 4, 6, z + 3), color)
    add_fill(fills, f"stall {x},{z} pole", (x - 3, 2, z - 2), (x - 3, 5, z - 2), M.LOG)
    add_fill(fills, f"stall {x},{z} pole 2", (x + 3, 2, z - 2), (x + 3, 5, z - 2), M.LOG)


def add_vendor_cart(fills: list[Fill], x: int, z: int) -> None:
    """A wheeled vendor cart."""
    add_fill(fills, f"vendor {x},{z} cart", (x - 2, 2, z - 3), (x + 2, 4, z + 3), M.WOOD)
    add_fill(fills, f"vendor {x},{z} wheel", (x - 3, 1, z - 2), (x - 1, 3, z), M.DARK)
    add_fill(fills, f"vendor {x},{z} handle", (x - 1, 3, z + 4), (x + 1, 4, z + 8), M.LOG)


def add_water_bucket(fills: list[Fill], x: int, z: int) -> None:
    """A roadside water bucket for pedestrians."""
    add_fill(fills, f"bucket {x},{z}", (x - 1, 2, z - 1), (x + 1, 3, z + 1), M.IRON_BARS)


def add_bench(fills: list[Fill], x: int, z: int) -> None:
    """A simple stone roadside bench."""
    add_fill(fills, f"bench {x},{z}", (x - 2, 2, z - 1), (x + 2, 2, z + 1), M.ANDESITE)


# ---------------------------------------------------------------------------
# Placement generators
# ---------------------------------------------------------------------------
AVENUE_XS = [900, 1800, 3000, 4200, 5100]
AVENUE_ZS = [900, 1700, 2500, 3300, 4100, 5000]
MARKET_BOUNDS = [
    (760, 2060, 1760, 3060),   # West Market
    (4240, 2060, 5240, 3060),  # East Market
]
PROP_COLORS = [M.RED_WOOL, M.BLUE_WOOL, M.YELLOW_WOOL, M.GREEN_WOOL]


def build_main_avenue_props(fills: list[Fill]) -> None:
    """Carts and benches at major avenue intersections and along roads."""
    for x in AVENUE_XS:
        for z in AVENUE_ZS:
            if (x + z) % 400 == 0:
                add_cart(fills, x + 20, z + 20, "z" if x == 3000 else "x")
            elif (x + z) % 400 == 200:
                add_bench(fills, x + 25, z + 25)
            elif (x + z) % 600 == 100:
                add_sedan_chair(fills, x - 20, z - 20)
            elif (x + z) % 600 == 400:
                add_water_bucket(fills, x - 25, z + 25)


def build_market_props(fills: list[Fill]) -> None:
    """Dense stalls and carts inside East and West Markets."""
    for mx1, mz1, mx2, mz2 in MARKET_BOUNDS:
        color_index = 0
        for x in range(mx1 + 40, mx2 - 40, 80):
            for z in range(mz1 + 40, mz2 - 40, 80):
                # Skip the central cross-street
                mid_x, mid_z = (mx1 + mx2) // 2, (mz1 + mz2) // 2
                if mid_x - 10 <= x <= mid_x + 10 or mid_z - 10 <= z <= mid_z + 10:
                    continue
                color = PROP_COLORS[color_index % len(PROP_COLORS)]
                if (x + z) % 160 == 0:
                    add_vendor_cart(fills, x, z)
                else:
                    add_market_stall(fills, x, z, color)
                color_index += 1


def build_ward_lane_props(fills: list[Fill]) -> None:
    """Scattered vendor carts and water buckets along ward lanes."""
    for origin_index, (x, z) in enumerate(iter_ward_origins()):
        mid_x, mid_z = x + 130, z + 130
        # Place one prop per ward, rotating through types
        prop_type = origin_index % 4
        if prop_type == 0:
            add_vendor_cart(fills, mid_x - 40, mid_z)
        elif prop_type == 1:
            add_water_bucket(fills, mid_x + 40, mid_z)
        elif prop_type == 2:
            add_bench(fills, mid_x, mid_z - 40)
        else:
            add_sedan_chair(fills, mid_x, mid_z + 40)


def build_palace_approach_props(fills: list[Fill]) -> None:
    """Sedan chairs and carts on the approach to Daming/Taiji palaces."""
    for x in range(2920, 3081, 60):
        add_sedan_chair(fills, x, 4040)
    for x in range(2420, 3581, 80):
        add_cart(fills, x, 4720, "z")


def build_street_props(fills: list[Fill]) -> None:
    build_main_avenue_props(fills)
    build_market_props(fills)
    build_ward_lane_props(fills)
    build_palace_approach_props(fills)


def main() -> None:
    run_builder(build_street_props, "street_props")


if __name__ == "__main__":
    main()
