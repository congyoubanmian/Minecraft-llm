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
    add_tree,
    run_builder,
)


"""
Suburban farms and villages outside the 6000x6000 city wall.

Adds farmland patches, irrigation channels, windmills, haystacks,
village houses, and trees across the outer suburbs.
"""


def build_farm_plot(fills: list[Fill], x1: int, z1: int, x2: int, z2: int) -> None:
    """A rectangular farm plot with alternating crop rows."""
    add_fill(fills, f"farm {x1},{z1} soil", (x1, 0, z1), (x2, 0, z2), M.DIRT)
    for x in range(x1, x2 + 1, 4):
        crop = M.YELLOW_WOOL if (x // 4) % 2 == 0 else M.GREEN_WOOL
        add_fill(fills, f"farm {x1},{z1} row {x}", (x, 1, z1), (x + 2, 1, z2), crop)


def build_irrigation_ditch(fills: list[Fill], x1: int, z1: int, x2: int, z2: int) -> None:
    """A narrow water channel between fields."""
    add_fill(fills, f"ditch {x1},{z1} bed", (x1, 0, z1), (x2, 0, z2), M.COBBLE)
    add_fill(fills, f"ditch {x1},{z1} water", (x1, 1, z1), (x2, 1, z2), M.WATER)


def build_windmill(fills: list[Fill], x: int, z: int) -> None:
    """A simple village windmill."""
    # Tower
    add_fill(fills, f"windmill {x},{z} tower", (x - 3, 1, z - 3), (x + 3, 14, z + 3), M.WHITE_TERRACOTTA)
    # Roof
    add_ridge_roof(fills, f"windmill {x},{z} roof", x - 5, z - 5, x + 5, z + 5, 15, layers=2, ridge_axis="z")
    # Blades (cross)
    add_fill(fills, f"windmill {x},{z} blade x", (x - 12, 12, z - 1), (x + 12, 14, z + 1), M.WOOD)
    add_fill(fills, f"windmill {x},{z} blade z", (x - 1, 12, z - 12), (x + 1, 14, z + 12), M.WOOD)


def build_haystack(fills: list[Fill], x: int, z: int) -> None:
    """A small haystack in a farmyard."""
    add_fill(fills, f"haystack {x},{z}", (x - 3, 1, z - 3), (x + 3, 5, z + 3), M.YELLOW_WOOL)
    add_fill(fills, f"haystack {x},{z} top", (x - 2, 6, z - 2), (x + 2, 7, z + 2), M.YELLOW_WOOL)


def build_village_house(fills: list[Fill], x: int, z: int) -> None:
    """A small rural house."""
    add_hollow_box(fills, f"village house {x},{z}", x, 1, z, x + 16, 8, z + 12, M.WOOD, thickness=1)
    add_ridge_roof(fills, f"village roof {x},{z}", x - 2, z - 2, x + 18, z + 14, 9, layers=2, ridge_axis="z")
    add_fill(fills, f"village yard {x},{z}", (x - 6, 0, z - 6), (x + 22, 0, z + 18), M.GRASS)
    add_tree(fills, f"village tree {x},{z}", x + 20, z + 15, 1, height=6, spread=2)


def build_suburb_farms(fills: list[Fill]) -> None:
    # Field grid parameters
    field_step = 280
    field_w, field_d = 220, 150

    # South suburbs: deep band from z=-1000 up to the wall
    for x in range(-800, 6800, field_step):
        for z in range(-900, -80, field_step):
            build_farm_plot(fills, x, z, x + field_w, z + field_d)

    # North suburbs
    for x in range(-800, 6800, field_step):
        for z in range(6080, 6901, field_step):
            build_farm_plot(fills, x, z, x + field_w, z + field_d)

    # East suburbs
    for x in range(6080, 6901, field_step):
        for z in range(-200, 6200, field_step):
            build_farm_plot(fills, x, z, x + field_d, z + field_w)

    # West suburbs
    for x in range(-900, -80, field_step):
        for z in range(-200, 6200, field_step):
            build_farm_plot(fills, x, z, x + field_d, z + field_w)

    # Irrigation channels stay in the four suburban belts and never cross the city.
    for x in range(-650, 6650, field_step):
        build_irrigation_ditch(fills, x + field_w, -900, x + field_w + 20, -80)
        build_irrigation_ditch(fills, x + field_w, 6080, x + field_w + 20, 6900)
    for z in range(-750, 6750, field_step):
        build_irrigation_ditch(fills, -900, z + field_d, -80, z + field_d + 20)
        build_irrigation_ditch(fills, 6080, z + field_d, 6900, z + field_d + 20)

    # Scattered villages with houses, windmills, and haystacks
    villages = [
        # (center_x, center_z, num_houses)
        (-400, -400, 4),
        (800, -600, 5),
        (2200, -500, 4),
        (3800, -600, 5),
        (5400, -400, 4),
        (-400, 6400, 4),
        (800, 6600, 5),
        (2200, 6500, 4),
        (3800, 6600, 5),
        (5400, 6400, 4),
        (-600, 1200, 3),
        (-600, 3600, 3),
        (-600, 4800, 3),
        (6600, 1200, 3),
        (6600, 3600, 3),
        (6600, 4800, 3),
    ]
    for cx, cz, count in villages:
        for i in range(count):
            hx = cx + (i % 2) * 80
            hz = cz + (i // 2) * 80
            build_village_house(fills, hx, hz)
        # Village windmill and haystacks
        build_windmill(fills, cx + 160, cz + 40)
        build_haystack(fills, cx + 60, cz + 160)
        build_haystack(fills, cx + 120, cz + 180)

    # Extra windmills near major roads
    for wx, wz in [
        (1000, -800), (3000, -800), (5000, -800),
        (1000, 6800), (3000, 6800), (5000, 6800),
        (-800, 2000), (-800, 4000), (6800, 2000), (6800, 4000),
    ]:
        build_windmill(fills, wx, wz)


def main() -> None:
    run_builder(build_suburb_farms, "suburb_farms")


if __name__ == "__main__":
    main()
