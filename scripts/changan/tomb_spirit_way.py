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
Imperial tomb complex outside the north-east of Chang'an.

Features a spirit road lined with guardian animals (elephants, horses, camels,
and officials) and a stepped pyramid tomb mound.
"""


# Tomb complex sits well outside the city wall, to the north-east.
CX, CZ = 6700, 6700
SPIRIT_ROAD_START_Z = CZ + 250
SPIRIT_ROAD_END_Z = CZ + 80


def add_elephant(fills: list[Fill], label: str, x: int, z: int, facing: int = 1) -> None:
    """Blocky stone elephant facing along z."""
    add_fill(fills, f"{label} body", (x - 3, 1, z - 5), (x + 3, 5, z + 5), M.STONE)
    add_fill(fills, f"{label} head", (x - 2, 5, z + 5 * facing), (x + 2, 8, z + 8 * facing), M.SMOOTH)
    add_fill(fills, f"{label} tusk", (x - 2, 4, z + 8 * facing), (x - 1, 5, z + 9 * facing), M.ANDESITE)
    add_fill(fills, f"{label} tusk r", (x + 1, 4, z + 8 * facing), (x + 2, 5, z + 9 * facing), M.ANDESITE)


def add_horse(fills: list[Fill], label: str, x: int, z: int, facing: int = 1) -> None:
    """Blocky stone horse."""
    add_fill(fills, f"{label} body", (x - 1, 2, z - 4), (x + 1, 5, z + 4), M.SMOOTH)
    add_fill(fills, f"{label} neck", (x - 1, 5, z + 3), (x + 1, 8, z + 5), M.SMOOTH)
    add_fill(fills, f"{label} head", (x - 1, 8, z + 5), (x + 1, 9, z + 7), M.STONE)
    add_fill(fills, f"{label} legs", (x - 1, 1, z - 3), (x + 1, 2, z + 3), M.ANDESITE)


def add_camel(fills: list[Fill], label: str, x: int, z: int, facing: int = 1) -> None:
    """Blocky stone Bactrian camel with two humps."""
    add_fill(fills, f"{label} body", (x - 2, 2, z - 5), (x + 2, 5, z + 5), M.STONE)
    add_fill(fills, f"{label} hump f", (x - 1, 6, z + 1), (x + 1, 8, z + 3), M.ANDESITE)
    add_fill(fills, f"{label} hump b", (x - 1, 6, z - 2), (x + 1, 8, z), M.ANDESITE)
    add_fill(fills, f"{label} neck", (x - 1, 5, z + 5), (x + 1, 8, z + 7), M.SMOOTH)
    add_fill(fills, f"{label} head", (x - 1, 8, z + 7), (x + 1, 9, z + 9), M.STONE)


def add_official(fills: list[Fill], label: str, x: int, z: int, facing: int = 1) -> None:
    """Blocky stone official / guardian figure."""
    add_fill(fills, f"{label} robe", (x - 1, 1, z - 1), (x + 1, 5, z + 1), M.SMOOTH)
    add_fill(fills, f"{label} head", (x - 1, 6, z - 1), (x + 1, 7, z + 1), M.STONE)
    add_fill(fills, f"{label} cap", (x - 1, 8, z - 1), (x + 1, 8, z + 1), M.GOLD)


def add_pair(fills: list[Fill], z: int, builder, label: str) -> None:
    """Place one pair of guardians facing the road (toward -z)."""
    builder(fills, f"{label} w", CX - 12, z, facing=-1)
    builder(fills, f"{label} e", CX + 12, z, facing=-1)


def build_tomb_spirit_way(fills: list[Fill]) -> None:
    # Spirit road surface
    add_fill(fills, "tomb spirit road", (CX - 8, 0, SPIRIT_ROAD_END_Z), (CX + 8, 1, SPIRIT_ROAD_START_Z), M.SMOOTH)

    # Guardian pairs
    pairs = [
        (SPIRIT_ROAD_START_Z - 40, add_elephant, "elephant"),
        (SPIRIT_ROAD_START_Z - 90, add_horse, "horse"),
        (SPIRIT_ROAD_START_Z - 140, add_camel, "camel"),
        (SPIRIT_ROAD_START_Z - 190, add_official, "official"),
    ]
    for z, builder, name in pairs:
        add_pair(fills, z, builder, name)

    # Stele pavilion at the start of the spirit road
    add_fill(fills, "tomb stele base", (CX - 6, 1, SPIRIT_ROAD_START_Z - 4), (CX + 6, 2, SPIRIT_ROAD_START_Z + 4), M.ANDESITE)
    add_fill(fills, "tomb stele slab", (CX - 2, 3, SPIRIT_ROAD_START_Z), (CX + 2, 14, SPIRIT_ROAD_START_Z + 2), M.STONE)
    add_fill(fills, "tomb stele text", (CX - 1, 8, SPIRIT_ROAD_START_Z - 1), (CX + 1, 10, SPIRIT_ROAD_START_Z + 3), M.GOLD)

    # Stepped pyramid tomb mound at the north end
    base = 60
    height = 20
    for i in range(height):
        inset = i * 2
        add_fill(
            fills,
            f"tomb mound layer {i}",
            (CX - base + inset, 1 + i, CZ - base + inset),
            (CX + base - inset, 1 + i, CZ + base - inset),
            M.DIRT if i < 10 else M.GRASS,
        )

    # Small sacrificial hall in front of the mound
    hall_z = CZ + base + 30
    add_fill(fills, "tomb hall base", (CX - 20, 1, hall_z - 15), (CX + 20, 2, hall_z + 15), M.ANDESITE)
    add_fill(fills, "tomb hall walls", (CX - 18, 3, hall_z - 13), (CX + 18, 14, hall_z + 13), M.STONE)
    add_fill(fills, "tomb hall interior", (CX - 14, 3, hall_z - 9), (CX + 14, 13, hall_z + 9), M.AIR)
    add_ridge_roof(fills, "tomb hall roof", CX - 22, hall_z - 17, CX + 22, hall_z + 17, 15, layers=2, ridge_axis="z")


def main() -> None:
    run_builder(build_tomb_spirit_way, "tomb_spirit_way")


if __name__ == "__main__":
    main()
