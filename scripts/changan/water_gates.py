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
Water gates (水关) where canals pass through the city wall.

These connect the moat/canal system to the outside and inside of the city.
"""

WATER_GATES = [
    # (name, x, z, axis) axis: 'x' means gate runs east-west through wall, 'z' north-south
    ("longshou_water_gate", 4200, 2000, "z"),
    ("qingming_water_gate", 2400, 4000, "x"),
    ("yongan_water_gate", 2500, 3500, "z"),
]


def build_water_gate(fills: list[Fill], name: str, cx: int, cz: int, axis: str) -> None:
    if axis == "z":
        # Water flows north-south through the wall
        # Tunnel through the wall
        add_fill(fills, f"{name} tunnel", (cx - 8, 0, cz - 20), (cx + 8, 5, cz + 20), M.WATER)
        # Stone arch over tunnel
        add_fill(fills, f"{name} arch top", (cx - 10, 6, cz - 20), (cx + 10, 8, cz + 20), M.STONE)
        # Gatehouse on top
        add_fill(fills, f"{name} gatehouse", (cx - 12, 9, cz - 12), (cx + 12, 18, cz + 12), M.STONE)
        add_ridge_roof(fills, f"{name} roof", cx - 16, cz - 16, cx + 16, cz + 16, 19, layers=2, ridge_axis="z")
        # Iron bars gate
        add_fill(fills, f"{name} bars", (cx - 7, 1, cz - 2), (cx + 7, 5, cz + 2), M.IRON_BARS if hasattr(M, 'IRON_BARS') else M.DARK)
    else:
        # Water flows east-west
        add_fill(fills, f"{name} tunnel", (cx - 20, 0, cz - 8), (cx + 20, 5, cz + 8), M.WATER)
        add_fill(fills, f"{name} arch top", (cx - 20, 6, cz - 10), (cx + 20, 8, cz + 10), M.STONE)
        add_fill(fills, f"{name} gatehouse", (cx - 12, 9, cz - 12), (cx + 12, 18, cz + 12), M.STONE)
        add_ridge_roof(fills, f"{name} roof", cx - 16, cz - 16, cx + 16, cz + 16, 19, layers=2, ridge_axis="x")
        add_fill(fills, f"{name} bars", (cx - 2, 1, cz - 7), (cx + 2, 5, cz + 7), M.IRON_BARS if hasattr(M, 'IRON_BARS') else M.DARK)


def build_water_gates(fills: list[Fill]) -> None:
    for name, cx, cz, axis in WATER_GATES:
        build_water_gate(fills, name, cx, cz, axis)


def main() -> None:
    run_builder(build_water_gates, "water_gates")


if __name__ == "__main__":
    main()
