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
City guard posts and ceremonial guards for Chang'an.

Adds static guard figures at palace gates, city gates, and watch towers.
"""


def add_guard(fills: list[Fill], x: int, y: int, z: int, facing: str = "south") -> None:
    """Simple guard figure with helmet and spear."""
    # Body
    add_fill(fills, f"guard {x},{y},{z} body", (x - 1, y, z - 1), (x + 1, y + 3, z + 1), M.RED_WALL)
    # Head/helmet
    add_fill(fills, f"guard {x},{y},{z} head", (x - 1, y + 4, z - 1), (x + 1, y + 5, z + 1), M.GOLD)
    # Spear
    if facing in ("south", "north"):
        add_fill(fills, f"guard {x},{y},{z} spear", (x + 2, y, z), (x + 2, y + 6, z), M.IRON_BARS)
    else:
        add_fill(fills, f"guard {x},{y},{z} spear", (x, y, z + 2), (x, y + 6, z + 2), M.IRON_BARS)


def add_guard_post(fills: list[Fill], x: int, z: int, y: int = 2) -> None:
    """A small guard hut/platform."""
    add_fill(fills, f"guard post {x},{z}", (x - 2, y, z - 2), (x + 2, y + 1, z + 2), M.ANDESITE)
    add_fill(fills, f"guard post {x},{z} roof", (x - 3, y + 2, z - 3), (x + 3, y + 2, z + 3), M.WOOD)
    add_guard(fills, x, y + 1, z)


def build_city_guards(fills: list[Fill]) -> None:
    # Palace gate guards (Daming Palace Danfeng Gate)
    for x in range(2920, 3081, 40):
        add_guard(fills, x, 1, 4050, "north")

    # City gate guards at main gates
    gate_positions = [
        (3000, -60), (1200, -60), (4800, -60),
        (3000, 6060), (1200, 6060), (4800, 6060),
        (-60, 1500), (-60, 3000), (-60, 4500),
        (6060, 1500), (6060, 3000), (6060, 4500),
    ]
    for idx, (x, z) in enumerate(gate_positions):
        add_guard_post(fills, x, z)

    # Imperial guard posts along palace walls
    for x in range(1900, 4110, 120):
        add_guard(fills, x, 1, 4110, "south")
        add_guard(fills, x, 1, 5810, "north")
    for z in range(4200, 5710, 120):
        add_guard(fills, 1810, 1, z, "east")
        add_guard(fills, 4190, 1, z, "west")


def main() -> None:
    run_builder(build_city_guards, "city_guards")


if __name__ == "__main__":
    main()
