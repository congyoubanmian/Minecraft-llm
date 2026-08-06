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
Road paving hierarchy for Chang'an avenues.

- Imperial way (Zhuque Avenue): central polished andesite strip + white marble markers
- Main avenues: smooth stone with polished edges
- Side streets: cobblestone / gravel
"""


def build_imperial_way(fills: list[Fill]) -> None:
    """Upgrade Zhuque Avenue with imperial paving."""
    # Central imperial strip
    add_fill(fills, "zhuque imperial strip", (2996, 3, 0), (3004, 3, 5999), M.ANDESITE)
    # White marble curb on both sides
    add_fill(fills, "zhuque west curb", (2992, 3, 0), (2995, 4, 5999), M.WHITE)
    add_fill(fills, "zhuque east curb", (3005, 3, 0), (3008, 4, 5999), M.WHITE)
    # Distance markers every 300 blocks
    for z in range(0, 6000, 300):
        add_fill(fills, f"zhuque marker {z}", (2998, 4, z), (3002, 5, z + 2), M.GOLD)


def build_main_avenues(fills: list[Fill]) -> None:
    """Upgrade other main avenues with stone paving and edges."""
    avenue_xs = [900, 1800, 4200, 5100]
    for x in avenue_xs:
        add_fill(fills, f"avenue x={x} road", (x - 28, 2, 80), (x + 28, 2, 5999 - 80), M.SMOOTH)
        add_fill(fills, f"avenue x={x} edge w", (x - 32, 2, 80), (x - 29, 3, 5999 - 80), M.ANDESITE)
        add_fill(fills, f"avenue x={x} edge e", (x + 29, 2, 80), (x + 32, 3, 5999 - 80), M.ANDESITE)

    avenue_zs = [900, 1700, 2500, 3300, 4100, 5000]
    for z in avenue_zs:
        add_fill(fills, f"avenue z={z} road", (80, 2, z - 28), (5999 - 80, 2, z + 28), M.SMOOTH)
        add_fill(fills, f"avenue z={z} edge n", (80, 2, z - 32), (5999 - 80, 3, z - 29), M.ANDESITE)
        add_fill(fills, f"avenue z={z} edge s", (80, 2, z + 29), (5999 - 80, 3, z + 32), M.ANDESITE)


def build_side_streets(fills: list[Fill]) -> None:
    """Cobblestone side streets in wards and markets."""
    for x, z in iter_ward_origins():
        mid_x, mid_z = x + 130, z + 130
        add_fill(fills, f"ward lane {x},{z} x", (x + 20, 1, mid_z - 3), (x + 240, 1, mid_z + 3), M.COBBLE)
        add_fill(fills, f"ward lane {x},{z} z", (mid_x - 3, 1, z + 20), (mid_x + 3, 1, z + 240), M.COBBLE)


def build_road_paving(fills: list[Fill]) -> None:
    build_imperial_way(fills)
    build_main_avenues(fills)
    build_side_streets(fills)


def main() -> None:
    run_builder(build_road_paving, "road_paving")


if __name__ == "__main__":
    main()
