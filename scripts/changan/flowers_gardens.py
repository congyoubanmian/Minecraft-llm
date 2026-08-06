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
Flower gardens and decorative plantings in palace courtyards, temples,
and wealthy wards.

Uses wool blocks as flower proxies. Two layers:
1. Named landmark gardens (palace/temple courtyards)
2. Tiled neighbourhood gardens inside residential wards
"""


# (name, x1, z1, x2, z2, flower_color)
LANDMARK_GARDENS = [
    ("daming_peony", 2000, 5350, 2200, 5500, M.RED_WOOL),
    ("xingqing_lotus", 1200, 1200, 1400, 1400, M.PINK_WOOL),
    ("taiji_chrysanthemum", 2600, 5600, 2750, 5750, M.YELLOW_WOOL),
    ("daxingshan_azalea", 1120, 2350, 1280, 2480, M.PINK_WOOL),
    ("guozijian_plum", 1630, 4400, 1720, 4520, M.WHITE_WOOL),
]

WARD_FLOWER_TYPES = [
    ("peony", M.RED_WOOL),
    ("lotus", M.PINK_WOOL),
    ("chrysanthemum", M.YELLOW_WOOL),
    ("plum", M.WHITE_WOOL),
    ("azalea", M.PINK_WOOL),
]


def build_flower_garden(fills: list[Fill], name: str, x1: int, z1: int, x2: int, z2: int, flower: str) -> None:
    if name == "xingqing_lotus":
        for x in range(x1 + 8, x2 - 7, 16):
            for z in range(z1 + 8, z2 - 7, 16):
                add_fill(fills, f"{name} lily {x},{z}", (x, 3, z), (x, 3, z), "minecraft:lily_pad")
        return

    # Narrow edging preserves existing palace paving and terrain.
    add_fill(fills, f"{name} north edge", (x1, 1, z1), (x2, 1, z1 + 1), M.ANDESITE)
    add_fill(fills, f"{name} south edge", (x1, 1, z2 - 1), (x2, 1, z2), M.ANDESITE)
    add_fill(fills, f"{name} west edge", (x1, 1, z1), (x1 + 1, 1, z2), M.ANDESITE)
    add_fill(fills, f"{name} east edge", (x2 - 1, 1, z1), (x2, 1, z2), M.ANDESITE)
    # Flower clusters
    for x in range(x1 + 5, x2 - 4, 10):
        for z in range(z1 + 5, z2 - 4, 10):
            add_fill(fills, f"{name} cluster {x},{z}", (x, 2, z), (x + 2, 2, z + 2), flower)


def build_ward_garden(
    fills: list[Fill],
    origin_x: int,
    origin_z: int,
    flower_name: str,
    flower_block: str,
) -> None:
    """A small garden patch inside one residential ward."""
    x1 = origin_x + 105
    z1 = origin_z + 150
    x2 = origin_x + 120
    z2 = origin_z + 220
    label = f"ward_garden_{origin_x}_{origin_z}_{flower_name}"
    add_fill(fills, f"{label} bed", (x1, 1, z1), (x2, 1, z2), M.GRASS)
    for x in range(x1 + 5, x2 - 4, 12):
        for z in range(z1 + 5, z2 - 4, 12):
            add_fill(fills, f"{label} cluster {x},{z}", (x, 2, z), (x + 2, 2, z + 2), flower_block)
    # Small central tree
    cx, cz = (x1 + x2) // 2, (z1 + z2) // 2
    add_fill(fills, f"{label} trunk", (cx, 2, cz), (cx, 5, cz), M.TREE_LOG)
    add_fill(fills, f"{label} leaves", (cx - 2, 5, cz - 2), (cx + 2, 7, cz + 2), M.LEAVES)


def build_flowers_gardens(fills: list[Fill]) -> None:
    # Landmark gardens
    for name, x1, z1, x2, z2, flower in LANDMARK_GARDENS:
        build_flower_garden(fills, name, x1, z1, x2, z2, flower)

    # Tiled ward gardens
    for index, (x, z) in enumerate(iter_ward_origins()):
        flower_name, flower_block = WARD_FLOWER_TYPES[index % len(WARD_FLOWER_TYPES)]
        build_ward_garden(fills, x, z, flower_name, flower_block)


def main() -> None:
    run_builder(build_flowers_gardens, "flowers_gardens")


if __name__ == "__main__":
    main()
