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
    add_tree,
    run_builder,
)


"""
Suburban irrigation system: channels, wooden water wheels, and sluice gates
connecting the farm plots outside the city wall to the canals and moat.
Covers all four sides of the city.
"""


CITY_SIZE = 6000
CHANNEL_WIDTH = 6
CHANNEL_Y = 0


def add_channel(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
) -> None:
    """Irrigation channel with stone bed and flowing water."""
    if x1 == x2:
        add_fill(fills, f"{label} bed", (x1 - 2, CHANNEL_Y, z1), (x1 + 2, CHANNEL_Y, z2), M.COBBLE)
        add_fill(fills, f"{label} water", (x1 - 1, CHANNEL_Y + 1, z1), (x1 + 1, CHANNEL_Y + 1, z2), M.WATER)
    elif z1 == z2:
        add_fill(fills, f"{label} bed", (x1, CHANNEL_Y, z1 - 2), (x2, CHANNEL_Y, z1 + 2), M.COBBLE)
        add_fill(fills, f"{label} water", (x1, CHANNEL_Y + 1, z1 - 1), (x2, CHANNEL_Y + 1, z1 + 1), M.WATER)


def add_sluice_gate(fills: list[Fill], label: str, x: int, z: int, axis: str) -> None:
    """Wooden sluice frame over a channel."""
    if axis == "z":
        add_fill(fills, f"{label} post w", (x - 3, CHANNEL_Y + 1, z - 1), (x - 2, CHANNEL_Y + 5, z + 1), M.WOOD)
        add_fill(fills, f"{label} post e", (x + 2, CHANNEL_Y + 1, z - 1), (x + 3, CHANNEL_Y + 5, z + 1), M.WOOD)
        add_fill(fills, f"{label} beam", (x - 4, CHANNEL_Y + 5, z - 1), (x + 4, CHANNEL_Y + 6, z + 1), M.LOG)
        add_fill(fills, f"{label} gate", (x - 2, CHANNEL_Y + 2, z - 2), (x + 2, CHANNEL_Y + 4, z + 2), M.ANDESITE)
    else:
        add_fill(fills, f"{label} post n", (x - 1, CHANNEL_Y + 1, z - 3), (x + 1, CHANNEL_Y + 5, z - 2), M.WOOD)
        add_fill(fills, f"{label} post s", (x - 1, CHANNEL_Y + 1, z + 2), (x + 1, CHANNEL_Y + 5, z + 3), M.WOOD)
        add_fill(fills, f"{label} beam", (x - 1, CHANNEL_Y + 5, z - 4), (x + 1, CHANNEL_Y + 6, z + 4), M.LOG)
        add_fill(fills, f"{label} gate", (x - 2, CHANNEL_Y + 2, z - 2), (x + 2, CHANNEL_Y + 4, z + 2), M.ANDESITE)


def add_water_wheel(fills: list[Fill], label: str, x: int, z: int, axis: str) -> None:
    """A simple wooden water wheel standing in the channel."""
    # Hub
    add_fill(fills, f"{label} hub", (x - 1, CHANNEL_Y + 1, z - 1), (x + 1, CHANNEL_Y + 3, z + 1), M.LOG)
    # Vertical or horizontal blades
    if axis == "z":
        add_fill(fills, f"{label} blades x", (x - 5, CHANNEL_Y + 2, z - 1), (x + 5, CHANNEL_Y + 2, z + 1), M.WOOD)
        add_fill(fills, f"{label} blades y", (x - 1, CHANNEL_Y - 2, z - 1), (x + 1, CHANNEL_Y + 6, z + 1), M.WOOD)
    else:
        add_fill(fills, f"{label} blades z", (x - 1, CHANNEL_Y + 2, z - 5), (x + 1, CHANNEL_Y + 2, z + 5), M.WOOD)
        add_fill(fills, f"{label} blades y", (x - 1, CHANNEL_Y - 2, z - 1), (x + 1, CHANNEL_Y + 6, z + 1), M.WOOD)


def build_farm_irrigation(fills: list[Fill]) -> None:
    # Channels radiate from the wall to the farm belts and canals.
    channel_positions = []

    # South side: channels running south from the moat
    for x in range(400, CITY_SIZE, 800):
        channel_positions.append((x, -100, x, -700))
    # North side
    for x in range(400, CITY_SIZE, 800):
        channel_positions.append((x, CITY_SIZE + 100, x, CITY_SIZE + 700))
    # West side
    for z in range(400, CITY_SIZE, 800):
        channel_positions.append((-100, z, -700, z))
    # East side
    for z in range(400, CITY_SIZE, 800):
        channel_positions.append((CITY_SIZE + 100, z, CITY_SIZE + 700, z))

    for idx, (x1, z1, x2, z2) in enumerate(channel_positions):
        add_channel(fills, f"irrigation channel {idx}", x1, z1, x2, z2)
        # Sluice gate near the wall
        add_sluice_gate(fills, f"irrigation sluice {idx}", x1, z1, "z" if x1 == x2 else "x")
        # Water wheel near the outer end
        add_water_wheel(fills, f"irrigation wheel {idx}", x2, z2, "z" if x1 == x2 else "x")

    # Willow trees along the main channels for shade
    for x in range(400, CITY_SIZE, 800):
        add_tree(fills, f"irrigation willow s {x}", x, -750, 1, height=5, spread=2)
        add_tree(fills, f"irrigation willow n {x}", x, CITY_SIZE + 750, 1, height=5, spread=2)
    for z in range(400, CITY_SIZE, 800):
        add_tree(fills, f"irrigation willow w {z}", -750, z, 1, height=5, spread=2)
        add_tree(fills, f"irrigation willow e {z}", CITY_SIZE + 750, z, 1, height=5, spread=2)


def main() -> None:
    run_builder(build_farm_irrigation, "farm_irrigation")


if __name__ == "__main__":
    main()
