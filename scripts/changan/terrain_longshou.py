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
Longshou Plateau (龙首原) terrain elevation.

Raises the northern palace area by 2-4 blocks to reflect the historical fact
that Daming Palace and Taiji Palace sat on higher ground overlooking the city.
"""


def build_longshou_elevation(fills: list[Fill]) -> None:
    # Raise the palace area in the north
    # Daming Palace footprint: 1800,4100 - 4200,5820
    # Taiji Palace footprint: 2400,4800 - 3600,5800
    # Use a gentle slope from y=64 base to y=66-68 in the north

    # Daming Palace plateau: raise by 2 blocks
    add_fill(fills, "daming plateau", (1800, 0, 4100), (4200, 1, 5820), M.GRASS)

    # Taiji Palace higher plateau: raise by 3 blocks
    add_fill(fills, "taiji plateau lower", (2400, 0, 4800), (3600, 2, 5800), M.GRASS)

    # Transition slopes to south (palace front)
    for x in range(1800, 4201, 200):
        add_fill(fills, f"daming slope {x}", (x, 0, 3900), (x + 199, 0, 4099), M.GRASS)


def main() -> None:
    run_builder(build_longshou_elevation, "terrain_longshou")


if __name__ == "__main__":
    main()
