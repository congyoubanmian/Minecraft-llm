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
    run_builder,
)


"""
Market atmosphere details for East and West Markets:
- Cloth drying racks (textile districts)
- Wine shop banners and hanging flags
- Shop signs
- Hawker stalls and shoulder poles
- Lantern strings over market streets
"""


def add_cloth_rack(fills: list[Fill], x: int, z: int, color: str) -> None:
    """A rack with cloth hanging to dry."""
    add_fill(fills, f"cloth rack {x},{z} pole1", (x - 6, 2, z - 1), (x - 5, 6, z + 1), M.LOG)
    add_fill(fills, f"cloth rack {x},{z} pole2", (x + 5, 2, z - 1), (x + 6, 6, z + 1), M.LOG)
    add_fill(fills, f"cloth rack {x},{z} bar", (x - 6, 6, z), (x + 6, 7, z), M.LOG)
    add_fill(fills, f"cloth rack {x},{z} cloth", (x - 5, 3, z - 1), (x + 5, 5, z + 1), color)


def add_wine_banner(fills: list[Fill], x: int, z: int, facing: str = "south") -> None:
    """Tall wine-shop banner pole with flag."""
    add_fill(fills, f"wine banner {x},{z} pole", (x - 1, 2, z - 1), (x + 1, 16, z + 1), M.LOG)
    if facing == "south":
        add_fill(fills, f"wine banner {x},{z} flag", (x - 1, 10, z - 8), (x + 1, 15, z - 1), M.RED_WOOL)
        add_fill(fills, f"wine banner {x},{z} text", (x, 11, z - 9), (x, 14, z - 9), M.YELLOW_WOOL)
    elif facing == "north":
        add_fill(fills, f"wine banner {x},{z} flag", (x - 1, 10, z + 1), (x + 1, 15, z + 8), M.RED_WOOL)
        add_fill(fills, f"wine banner {x},{z} text", (x, 11, z + 9), (x, 14, z + 9), M.YELLOW_WOOL)
    elif facing == "west":
        add_fill(fills, f"wine banner {x},{z} flag", (x - 8, 10, z - 1), (x - 1, 15, z + 1), M.RED_WOOL)
        add_fill(fills, f"wine banner {x},{z} text", (x - 9, 11, z), (x - 9, 14, z), M.YELLOW_WOOL)
    else:
        add_fill(fills, f"wine banner {x},{z} flag", (x + 1, 10, z - 1), (x + 8, 15, z + 1), M.RED_WOOL)
        add_fill(fills, f"wine banner {x},{z} text", (x + 9, 11, z), (x + 9, 14, z), M.YELLOW_WOOL)


def add_shop_sign(fills: list[Fill], x: int, y: int, z: int, color: str, facing: str = "south") -> None:
    """Hanging rectangular shop sign."""
    if facing in ("south", "north"):
        add_fill(fills, f"shop sign {x},{z}", (x - 4, y, z - 1), (x + 4, y + 3, z + 1), color)
    else:
        add_fill(fills, f"shop sign {x},{z}", (x - 1, y, z - 4), (x + 1, y + 3, z + 4), color)


def add_hawker_stall(fills: list[Fill], x: int, z: int) -> None:
    """A small portable hawker stall with a pole and cloth."""
    add_fill(fills, f"hawker {x},{z} table", (x - 2, 2, z - 2), (x + 2, 2, z + 2), M.WOOD)
    add_fill(fills, f"hawker {x},{z} pole", (x - 2, 2, z - 2), (x - 2, 7, z - 2), M.LOG)
    add_fill(fills, f"hawker {x},{z} cloth", (x - 2, 7, z - 2), (x + 2, 8, z + 2), M.RED_WOOL)


def add_lantern_string(fills: list[Fill], x1: int, z1: int, x2: int, z2: int) -> None:
    """A string of lanterns across a street."""
    if x1 == x2:
        for z in range(min(z1, z2), max(z1, z2) + 1, 10):
            add_fill(fills, f"lantern {x1},{z}", (x1 - 1, 8, z - 1), (x1 + 1, 9, z + 1), M.LANTERN)
    else:
        for x in range(min(x1, x2), max(x1, x2) + 1, 10):
            add_fill(fills, f"lantern {x},{z1}", (x - 1, 8, z1 - 1), (x + 1, 9, z1 + 1), M.LANTERN)


MARKET_BOUNDS = [
    (760, 2060, 1760, 3060),   # West Market
    (4240, 2060, 5240, 3060),  # East Market
]
CLOTH_COLORS = [M.RED_WOOL, M.BLUE_WOOL, M.YELLOW_WOOL, M.WHITE_WOOL, M.GREEN_WOOL]
SIGN_COLORS = [M.RED_WOOL, M.YELLOW_WOOL, M.BLUE_WOOL, M.GREEN_WOOL]


def build_market_details(fills: list[Fill]) -> None:
    for market_index, (mx1, mz1, mx2, mz2) in enumerate(MARKET_BOUNDS):
        mid_x, mid_z = (mx1 + mx2) // 2, (mz1 + mz2) // 2

        # 1. Wine banners along all four outer market edges
        for x in range(mx1 + 60, mx2 - 60, 80):
            add_wine_banner(fills, x, mz1 + 12, "south")
            add_wine_banner(fills, x, mz2 - 12, "north")
        for z in range(mz1 + 60, mz2 - 60, 80):
            add_wine_banner(fills, mx1 + 12, z, "east")
            add_wine_banner(fills, mx2 - 12, z, "west")

        # 2. Cloth drying racks in the four quadrants
        color_offset = market_index * 2
        quadrant_offsets = [
            (mx1 + 80, mz1 + 80), (mid_x + 80, mz1 + 80),
            (mx1 + 80, mid_z + 80), (mid_x + 80, mid_z + 80),
        ]
        for qidx, (qx, qz) in enumerate(quadrant_offsets):
            color = CLOTH_COLORS[(color_offset + qidx) % len(CLOTH_COLORS)]
            for dx in range(0, 120, 60):
                for dz in range(0, 120, 60):
                    add_cloth_rack(fills, qx + dx, qz + dz, color)

        # 3. Shop signs along the central cross streets
        for x in range(mx1 + 40, mx2 - 40, 80):
            color = SIGN_COLORS[(x // 80) % len(SIGN_COLORS)]
            add_shop_sign(fills, x, 4, mid_z - 8, color, "south")
            add_shop_sign(fills, x, 4, mid_z + 8, color, "north")
        for z in range(mz1 + 40, mz2 - 40, 80):
            color = SIGN_COLORS[(z // 80) % len(SIGN_COLORS)]
            add_shop_sign(fills, mid_x - 8, 4, z, color, "east")
            add_shop_sign(fills, mid_x + 8, 4, z, color, "west")

        # 4. Hawker stalls in the lanes between quadrants
        for x in range(mx1 + 100, mx2 - 100, 100):
            for z in range(mz1 + 100, mz2 - 100, 100):
                # Skip the central cross
                if mid_x - 20 <= x <= mid_x + 20 or mid_z - 20 <= z <= mid_z + 20:
                    continue
                if (x + z) % 200 == 0:
                    add_hawker_stall(fills, x, z)

        # 5. Lantern strings over the central cross streets
        add_lantern_string(fills, mx1 + 30, mid_z, mx2 - 30, mid_z)
        add_lantern_string(fills, mid_x, mz1 + 30, mid_x, mz2 - 30)


def main() -> None:
    run_builder(build_market_details, "market_details")


if __name__ == "__main__":
    main()
