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
    add_outline,
    add_staircase,
    run_builder,
)


"""
Jiacheng Fudao 3D (夹城复道) - the Tang double-decker elevated corridor.

Historically Emperor Xuanzong built walled elevated corridors (复道) from
Daming Palace along the eastern side of the city to Xingqing Palace and
Qujiang, so the court could travel unseen. This module builds that linear
megastructure: a two-level enclosed sky-corridor carried on stone piers
across the eastern wards.

Route in Chang'an city local coordinates:
    (4200, 4700) Daming Palace east wall
        -> east along z=4700 to (5900, 4700)
        -> south along x=5900 to (5900, 5200) Qujiang north-east corner

3D features:
    - Stone piers every 24 blocks carrying the whole structure
    - Lower deck: enclosed corridor (walls, slit windows, tiled roof)
    - Upper deck: open viewing gallery with waist walls and its own roof
    - Corner transfer platform at the turn, with dougong capitals
    - Three stair towers connecting ground level to both decks
"""

CORRIDOR_Y_PIER = 13
Y_DECK_LOW = 14
Y_GALLERY = 23
HALF_W = 5  # corridor half width

# Route segments: (x1, z1, x2, z2)
SEGMENTS = [
    (4200, 4700, 5900, 4700),   # east-west leg
    (5900, 4700, 5900, 5200),   # north-south leg
]
CORNER = (5900, 4700)
STAIR_TOWERS = [(4600, 4700), (5400, 4700), (5900, 4950)]


def _segment(fills: list[Fill], label: str, x1: int, z1: int, x2: int, z2: int) -> None:
    """One straight corridor segment with piers, lower deck, upper gallery."""
    along_x = z1 == z2
    min_x, max_x = min(x1, x2), max(x1, x2)
    min_z, max_z = min(z1, z2), max(z1, z2)

    # Piers
    if along_x:
        for x in range(min_x + 12, max_x, 24):
            add_fill(fills, f"{label} pier {x}", (x, 1, z1 - 2), (x + 3, CORRIDOR_Y_PIER, z1 + 2), M.STONE)
        # Lower deck floor + walls + slit windows + roof
        add_fill(fills, f"{label} low floor", (min_x, Y_DECK_LOW, z1 - HALF_W), (max_x, Y_DECK_LOW, z1 + HALF_W), M.WOOD)
        add_fill(fills, f"{label} low wall n", (min_x, Y_DECK_LOW + 1, z1 - HALF_W), (max_x, Y_DECK_LOW + 6, z1 - HALF_W + 1), M.RED_WALL)
        add_fill(fills, f"{label} low wall s", (min_x, Y_DECK_LOW + 1, z1 + HALF_W - 1), (max_x, Y_DECK_LOW + 6, z1 + HALF_W), M.RED_WALL)
        for x in range(min_x + 20, max_x - 19, 40):
            add_fill(fills, f"{label} slit n {x}", (x, Y_DECK_LOW + 3, z1 - HALF_W), (x + 6, Y_DECK_LOW + 4, z1 - HALF_W + 1), M.GLASS)
            add_fill(fills, f"{label} slit s {x}", (x, Y_DECK_LOW + 3, z1 + HALF_W - 1), (x + 6, Y_DECK_LOW + 4, z1 + HALF_W), M.GLASS)
        add_fill(fills, f"{label} low roof", (min_x - 2, Y_DECK_LOW + 7, z1 - HALF_W - 2), (max_x + 2, Y_DECK_LOW + 8, z1 + HALF_W + 2), M.ROOF_GREEN)
        # Upper gallery: floor, waist walls, columns, roof
        add_fill(fills, f"{label} gal floor", (min_x, Y_GALLERY, z1 - HALF_W), (max_x, Y_GALLERY, z1 + HALF_W), M.WOOD)
        add_fill(fills, f"{label} gal waist n", (min_x, Y_GALLERY + 1, z1 - HALF_W), (max_x, Y_GALLERY + 2, z1 - HALF_W), M.RED_WALL)
        add_fill(fills, f"{label} gal waist s", (min_x, Y_GALLERY + 1, z1 + HALF_W), (max_x, Y_GALLERY + 2, z1 + HALF_W), M.RED_WALL)
        for x in range(min_x + 10, max_x, 24):
            add_fill(fills, f"{label} gal col n {x}", (x, Y_GALLERY + 1, z1 - HALF_W), (x + 1, Y_GALLERY + 6, z1 - HALF_W), M.LOG)
            add_fill(fills, f"{label} gal col s {x}", (x, Y_GALLERY + 1, z1 + HALF_W - 1), (x + 1, Y_GALLERY + 6, z1 + HALF_W - 1), M.LOG)
        add_fill(fills, f"{label} gal roof", (min_x - 2, Y_GALLERY + 7, z1 - HALF_W - 2), (max_x + 2, Y_GALLERY + 8, z1 + HALF_W + 2), M.ROOF_GREEN)
    else:
        for z in range(min_z + 12, max_z, 24):
            add_fill(fills, f"{label} pier {z}", (x1 - 2, 1, z), (x1 + 2, CORRIDOR_Y_PIER, z + 3), M.STONE)
        add_fill(fills, f"{label} low floor", (x1 - HALF_W, Y_DECK_LOW, min_z), (x1 + HALF_W, Y_DECK_LOW, max_z), M.WOOD)
        add_fill(fills, f"{label} low wall w", (x1 - HALF_W, Y_DECK_LOW + 1, min_z), (x1 - HALF_W + 1, Y_DECK_LOW + 6, max_z), M.RED_WALL)
        add_fill(fills, f"{label} low wall e", (x1 + HALF_W - 1, Y_DECK_LOW + 1, min_z), (x1 + HALF_W, Y_DECK_LOW + 6, max_z), M.RED_WALL)
        for z in range(min_z + 20, max_z - 19, 40):
            add_fill(fills, f"{label} slit w {z}", (x1 - HALF_W, Y_DECK_LOW + 3, z), (x1 - HALF_W + 1, Y_DECK_LOW + 4, z + 6), M.GLASS)
            add_fill(fills, f"{label} slit e {z}", (x1 + HALF_W - 1, Y_DECK_LOW + 3, z), (x1 + HALF_W, Y_DECK_LOW + 4, z + 6), M.GLASS)
        add_fill(fills, f"{label} low roof", (x1 - HALF_W - 2, Y_DECK_LOW + 7, min_z - 2), (x1 + HALF_W + 2, Y_DECK_LOW + 8, max_z + 2), M.ROOF_GREEN)
        add_fill(fills, f"{label} gal floor", (x1 - HALF_W, Y_GALLERY, min_z), (x1 + HALF_W, Y_GALLERY, max_z), M.WOOD)
        add_fill(fills, f"{label} gal waist w", (x1 - HALF_W, Y_GALLERY + 1, min_z), (x1 - HALF_W, Y_GALLERY + 2, max_z), M.RED_WALL)
        add_fill(fills, f"{label} gal waist e", (x1 + HALF_W, Y_GALLERY + 1, min_z), (x1 + HALF_W, Y_GALLERY + 2, max_z), M.RED_WALL)
        for z in range(min_z + 10, max_z, 24):
            add_fill(fills, f"{label} gal col w {z}", (x1 - HALF_W, Y_GALLERY + 1, z), (x1 - HALF_W, Y_GALLERY + 6, z + 1), M.LOG)
            add_fill(fills, f"{label} gal col e {z}", (x1 + HALF_W - 1, Y_GALLERY + 1, z), (x1 + HALF_W - 1, Y_GALLERY + 6, z + 1), M.LOG)
        add_fill(fills, f"{label} gal roof", (x1 - HALF_W - 2, Y_GALLERY + 7, min_z - 2), (x1 + HALF_W + 2, Y_GALLERY + 8, max_z + 2), M.ROOF_GREEN)


def _stair_tower(fills: list[Fill], label: str, tx: int, tz: int) -> None:
    """Ground-to-deck stair tower: stone shaft, internal switchback, gate."""
    add_fill(fills, f"{label} shaft", (tx - 8, 1, tz - 8), (tx + 8, Y_DECK_LOW + 8, tz + 8), M.STONE)
    # Carve interior and switchback stairs: ground -> lower deck
    add_fill(fills, f"{label} hollow", (tx - 6, 2, tz - 6), (tx + 6, Y_DECK_LOW + 6, tz + 6), M.AIR)
    for i in range(12):
        add_fill(fills, f"{label} step a {i}", (tx - 5 + i % 6, 2 + i, tz - 5 if i < 6 else tz + 5), (tx - 5 + i % 6, 2 + i, tz - 5 if i < 6 else tz + 5), M.SMOOTH)
    # Door at ground level and at deck level
    add_fill(fills, f"{label} door ground", (tx - 2, 2, tz - 8), (tx + 2, 7, tz - 8), M.AIR)
    add_fill(fills, f"{label} door deck", (tx - 2, Y_DECK_LOW + 1, tz + 7), (tx + 2, Y_DECK_LOW + 5, tz + 8), M.AIR)
    # Roof
    add_fill(fills, f"{label} roof", (tx - 10, Y_DECK_LOW + 9, tz - 10), (tx + 10, Y_DECK_LOW + 10, tz + 10), M.ROOF_GREEN)


def build_fudao_jiacheng_3d(fills: list[Fill]) -> None:
    for i, (x1, z1, x2, z2) in enumerate(SEGMENTS):
        _segment(fills, f"fudao seg{i}", x1, z1, x2, z2)

    # Corner transfer platform: wider deck, dougong capitals, pavilion roof
    cx, cz = CORNER
    add_fill(fills, "fudao corner platform", (cx - 12, Y_DECK_LOW, cz - 12), (cx + 12, Y_DECK_LOW, cz + 12), M.WOOD)
    add_fill(fills, "fudao corner gallery", (cx - 12, Y_GALLERY, cz - 12), (cx + 12, Y_GALLERY, cz + 12), M.WOOD)
    add_outline(fills, "fudao corner rail", cx - 12, cz - 12, cx + 12, cz + 12, Y_GALLERY + 1, Y_GALLERY + 1, M.FENCE, thickness=1)
    for sx in (-1, 1):
        for sz in (-1, 1):
            add_fill(fills, f"fudao corner pier {sx},{sz}", (cx + sx * 9 - 1, 1, cz + sz * 9 - 1), (cx + sx * 9 + 2, CORRIDOR_Y_PIER, cz + sz * 9 + 2), M.STONE)
            add_fill(fills, f"fudao corner col {sx},{sz}", (cx + sx * 10, Y_GALLERY + 1, cz + sz * 10), (cx + sx * 10, Y_GALLERY + 7, cz + sz * 10), M.LOG)
    add_fill(fills, "fudao corner roof", (cx - 15, Y_GALLERY + 8, cz - 15), (cx + 15, Y_GALLERY + 9, cz + 15), M.ROOF_GREEN)
    add_fill(fills, "fudao corner finial", (cx - 1, Y_GALLERY + 10, cz - 1), (cx + 1, Y_GALLERY + 13, cz + 1), M.GOLD)

    for i, (tx, tz) in enumerate(STAIR_TOWERS):
        _stair_tower(fills, f"fudao stairtower {i}", tx, tz)

    # Terminal gates where the corridor meets Daming wall and Qujiang
    add_fill(fills, "fudao gate daming", (4196, Y_DECK_LOW + 1, 4694), (4204, Y_DECK_LOW + 6, 4706), M.AIR)
    add_fill(fills, "fudao gate qujiang arch", (5894, Y_GALLERY + 1, 5194), (5906, Y_GALLERY + 6, 5200), M.AIR)


def main() -> None:
    run_builder(build_fudao_jiacheng_3d, "fudao_jiacheng_3d")


if __name__ == "__main__":
    main()
