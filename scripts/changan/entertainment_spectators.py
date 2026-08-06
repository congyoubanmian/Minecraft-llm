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
    add_ridge_roof,
    run_builder,
)


"""
Tiered spectator stands, score-flag poles, and entrance gates for the
entertainment venues: the polo field and Leyouyuan pleasure garden.
"""


# Polo field coordinates (from entertainment_venues.py)
PF_X1, PF_Z1 = 1800, 2200
PF_X2, PF_Z2 = 2600, 3000

# Leyou Park coordinates
LY_X1, LY_Z1 = 5000, 4800
LY_X2, LY_Z2 = 5800, 5600


def add_tiered_stands(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    base_y: int,
    tiers: int,
    direction: int,
) -> None:
    """Tiered seating rising toward the field."""
    for i in range(tiers):
        y = base_y + i
        if direction == -1:
            # stands recede in -x
            add_fill(fills, f"{label} tier {i}", (x1 - i * 2, y, z1), (x2 - i * 2, y, z2), M.WOOD)
        elif direction == 1:
            # stands recede in +x
            add_fill(fills, f"{label} tier {i}", (x1 + i * 2, y, z1), (x2 + i * 2, y, z2), M.WOOD)
        elif direction == -2:
            # stands recede in -z
            add_fill(fills, f"{label} tier {i}", (x1, y, z1 - i * 2), (x2, y, z2 - i * 2), M.WOOD)
        elif direction == 2:
            # stands recede in +z
            add_fill(fills, f"{label} tier {i}", (x1, y, z1 + i * 2), (x2, y, z2 + i * 2), M.WOOD)


def add_score_pole(fills: list[Fill], label: str, x: int, z: int, y: int, color: str) -> None:
    """Tall flag pole with a coloured score flag."""
    add_fill(fills, f"{label} pole", (x, y, z), (x, y + 18, z), M.LOG)
    add_fill(fills, f"{label} flag", (x - 1, y + 16, z - 1), (x + 1, y + 18, z + 1), color)


def add_entrance_gate(fills: list[Fill], label: str, x: int, z: int, axis: str) -> None:
    """Simple paifang-style entrance gate."""
    if axis == "z":
        add_fill(fills, f"{label} left", (x - 12, 1, z - 2), (x - 9, 14, z + 2), M.RED_WALL)
        add_fill(fills, f"{label} right", (x + 9, 1, z - 2), (x + 12, 14, z + 2), M.RED_WALL)
        add_fill(fills, f"{label} beam", (x - 14, 15, z - 2), (x + 14, 17, z + 2), M.WOOD)
        add_ridge_roof(fills, f"{label} roof", x - 16, z - 4, x + 16, z + 4, 18, layers=2, ridge_axis="z")
    else:
        add_fill(fills, f"{label} left", (x - 2, 1, z - 12), (x + 2, 14, z - 9), M.RED_WALL)
        add_fill(fills, f"{label} right", (x - 2, 1, z + 9), (x + 2, 14, z + 12), M.RED_WALL)
        add_fill(fills, f"{label} beam", (x - 2, 15, z - 14), (x + 2, 17, z + 14), M.WOOD)
        add_ridge_roof(fills, f"{label} roof", x - 4, z - 16, x + 4, z + 16, 18, layers=2, ridge_axis="x")


def build_entertainment_spectators(fills: list[Fill]) -> None:
    # Polo field spectator stands on west and east sides
    add_tiered_stands(fills, "polo west stand", PF_X1 - 4, PF_Z1, PF_X1 - 1, PF_Z2, 2, 5, -1)
    add_tiered_stands(fills, "polo east stand", PF_X2 + 1, PF_Z1, PF_X2 + 4, PF_Z2, 2, 5, 1)

    # Tiered stands on the north and south short ends
    add_tiered_stands(fills, "polo south stand", PF_X1, PF_Z1 - 4, PF_X2, PF_Z1 - 1, 2, 4, -2)
    add_tiered_stands(fills, "polo north stand", PF_X1, PF_Z2 + 1, PF_X2, PF_Z2 + 4, 2, 4, 2)

    # Score-flag poles near the four corners / goals
    add_score_pole(fills, "polo flag sw", PF_X1 + 20, PF_Z1 + 20, 2, M.RED_WOOL)
    add_score_pole(fills, "polo flag se", PF_X2 - 20, PF_Z1 + 20, 2, M.BLUE_WOOL)
    add_score_pole(fills, "polo flag nw", PF_X1 + 20, PF_Z2 - 20, 2, M.YELLOW_WOOL)
    add_score_pole(fills, "polo flag ne", PF_X2 - 20, PF_Z2 - 20, 2, M.GREEN_WOOL)

    # Entrance gates at the north and south of the polo field
    cx = (PF_X1 + PF_X2) // 2
    add_entrance_gate(fills, "polo south gate", cx, PF_Z1 - 30, "z")
    add_entrance_gate(fills, "polo north gate", cx, PF_Z2 + 30, "z")

    # Leyou Park entrance gate on the west side
    lycz = (LY_Z1 + LY_Z2) // 2
    add_entrance_gate(fills, "leyou west gate", LY_X1 - 30, lycz, "x")

    # Leyou Park spectator / viewing terraces on the east and south edges
    add_tiered_stands(fills, "leyou east terrace", LY_X2 + 1, LY_Z1 + 40, LY_X2 + 4, LY_Z2 - 40, 3, 4, 1)
    add_tiered_stands(fills, "leyou south terrace", LY_X1 + 40, LY_Z1 - 4, LY_X2 - 40, LY_Z1 - 1, 3, 4, -2)

    # Flag poles at Leyou Park corners
    add_score_pole(fills, "leyou flag sw", LY_X1 + 40, LY_Z1 + 40, 3, M.RED_WOOL)
    add_score_pole(fills, "leyou flag se", LY_X2 - 40, LY_Z1 + 40, 3, M.YELLOW_WOOL)
    add_score_pole(fills, "leyou flag nw", LY_X1 + 40, LY_Z2 - 40, 3, M.BLUE_WOOL)
    add_score_pole(fills, "leyou flag ne", LY_X2 - 40, LY_Z2 - 40, 3, M.GREEN_WOOL)


def main() -> None:
    run_builder(build_entertainment_spectators, "entertainment_spectators")


if __name__ == "__main__":
    main()
