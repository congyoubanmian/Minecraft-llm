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
Rampart horse-ways (登城马道) on the outer city wall.

Adds sloped stone ramps leading from ground level to the wall top,
so defenders could ride or run up to the battlements.
"""


WALL_TOP_Y = 27
RAMP_WIDTH = 8
RAMP_LENGTH = 24

# (center_x, center_z, direction)
# direction indicates which face of the wall the ramp climbs.
HORSE_WAYS = [
    # South wall (ramps climb northward toward z=0)
    (1500, -RAMP_LENGTH, "north"),
    (4500, -RAMP_LENGTH, "north"),
    # North wall (ramps climb southward toward z=6000)
    (1500, 6000 + RAMP_LENGTH, "south"),
    (4500, 6000 + RAMP_LENGTH, "south"),
    # West wall (ramps climb eastward toward x=0)
    (-RAMP_LENGTH, 1500, "east"),
    (-RAMP_LENGTH, 4500, "east"),
    # East wall (ramps climb westward toward x=6000)
    (6000 + RAMP_LENGTH, 1500, "west"),
    (6000 + RAMP_LENGTH, 4500, "west"),
]


def add_horse_way(fills: list[Fill], cx: int, cz: int, direction: str) -> None:
    """Build one sloped ramp from ground up to the wall top."""
    half_w = RAMP_WIDTH // 2
    if direction == "north":
        # Ramp rises as z increases toward the wall at z=0
        for i in range(RAMP_LENGTH):
            y = 1 + (WALL_TOP_Y - 1) * i // (RAMP_LENGTH - 1)
            z = cz + i
            add_fill(fills, f"horseway {cx},{cz} step {i}", (cx - half_w, y, z), (cx + half_w, y, z + 1), M.ANDESITE)
            add_fill(fills, f"horseway {cx},{cz} rail w {i}", (cx - half_w - 1, y + 1, z), (cx - half_w - 1, y + 2, z + 1), M.STONE)
            add_fill(fills, f"horseway {cx},{cz} rail e {i}", (cx + half_w + 1, y + 1, z), (cx + half_w + 1, y + 2, z + 1), M.STONE)
    elif direction == "south":
        for i in range(RAMP_LENGTH):
            y = 1 + (WALL_TOP_Y - 1) * i // (RAMP_LENGTH - 1)
            z = cz - i
            add_fill(fills, f"horseway {cx},{cz} step {i}", (cx - half_w, y, z - 1), (cx + half_w, y, z), M.ANDESITE)
            add_fill(fills, f"horseway {cx},{cz} rail w {i}", (cx - half_w - 1, y + 1, z - 1), (cx - half_w - 1, y + 2, z), M.STONE)
            add_fill(fills, f"horseway {cx},{cz} rail e {i}", (cx + half_w + 1, y + 1, z - 1), (cx + half_w + 1, y + 2, z), M.STONE)
    elif direction == "east":
        for i in range(RAMP_LENGTH):
            y = 1 + (WALL_TOP_Y - 1) * i // (RAMP_LENGTH - 1)
            x = cx + i
            add_fill(fills, f"horseway {cx},{cz} step {i}", (x, y, cz - half_w), (x + 1, y, cz + half_w), M.ANDESITE)
            add_fill(fills, f"horseway {cx},{cz} rail n {i}", (x, y + 1, cz - half_w - 1), (x + 1, y + 2, cz - half_w - 1), M.STONE)
            add_fill(fills, f"horseway {cx},{cz} rail s {i}", (x, y + 1, cz + half_w + 1), (x + 1, y + 2, cz + half_w + 1), M.STONE)
    else:  # west
        for i in range(RAMP_LENGTH):
            y = 1 + (WALL_TOP_Y - 1) * i // (RAMP_LENGTH - 1)
            x = cx - i
            add_fill(fills, f"horseway {cx},{cz} step {i}", (x - 1, y, cz - half_w), (x, y, cz + half_w), M.ANDESITE)
            add_fill(fills, f"horseway {cx},{cz} rail n {i}", (x - 1, y + 1, cz - half_w - 1), (x, y + 2, cz - half_w - 1), M.STONE)
            add_fill(fills, f"horseway {cx},{cz} rail s {i}", (x - 1, y + 1, cz + half_w + 1), (x, y + 2, cz + half_w + 1), M.STONE)


def build_horse_ways(fills: list[Fill]) -> None:
    for cx, cz, direction in HORSE_WAYS:
        add_horse_way(fills, cx, cz, direction)


def main() -> None:
    run_builder(build_horse_ways, "rampart_horse_way")


if __name__ == "__main__":
    main()
