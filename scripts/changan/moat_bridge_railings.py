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
    run_builder,
)


"""
Bridge railings, piers, and guardian lions for the main city-gate bridges
that cross the moat around Chang'an.
"""


CITY_SIZE = 6000
MOAT_OUTER = 90
BRIDGE_WIDTH = 18

# Main gate positions (cx, cz, axis)
GATE_BRIDGES = [
    # South gates
    (1200, 0, "z"), (3000, 0, "z"), (4800, 0, "z"),
    # North gates
    (1200, CITY_SIZE, "z"), (3000, CITY_SIZE, "z"), (4800, CITY_SIZE, "z"),
    # West gates
    (0, 1500, "x"), (0, 3000, "x"), (0, 4500, "x"),
    # East gates
    (CITY_SIZE, 1500, "x"), (CITY_SIZE, 3000, "x"), (CITY_SIZE, 4500, "x"),
]


def add_guardian_lion(fills: list[Fill], x: int, y: int, z: int) -> None:
    """A simple stone lion statue at a bridgehead."""
    add_fill(fills, f"lion {x},{z} base", (x - 2, y, z - 2), (x + 2, y + 1, z + 2), M.ANDESITE)
    add_fill(fills, f"lion {x},{z} body", (x - 1, y + 2, z - 1), (x + 1, y + 4, z + 1), M.SMOOTH)
    add_fill(fills, f"lion {x},{z} head", (x - 1, y + 5, z - 1), (x + 1, y + 6, z + 1), M.SMOOTH)


def add_bridge(fills: list[Fill], cx: int, cz: int, axis: str) -> None:
    """Add a bridge with deck, railings, piers, and guardian lions."""
    half_w = BRIDGE_WIDTH // 2
    if axis == "z":
        # Bridge runs north-south across the moat
        z_inner = cz if cz == 0 else CITY_SIZE
        z_outer = -MOAT_OUTER if cz == 0 else CITY_SIZE + MOAT_OUTER
        z_start, z_end = sorted((z_inner, z_outer))
        # Deck
        add_fill(fills, f"bridge {cx},{cz} deck", (cx - half_w, 3, z_start), (cx + half_w, 3, z_end), M.SMOOTH)
        # Railings
        add_fill(fills, f"bridge {cx},{cz} rail w", (cx - half_w - 1, 4, z_start), (cx - half_w - 1, 5, z_end), M.ANDESITE)
        add_fill(fills, f"bridge {cx},{cz} rail e", (cx + half_w + 1, 4, z_start), (cx + half_w + 1, 5, z_end), M.ANDESITE)
        # Piers in the water
        for z in range(z_start + 20, z_end - 19, 35):
            add_fill(fills, f"bridge {cx},{cz} pier {z}", (cx - half_w, 0, z - 2), (cx + half_w, 2, z + 2), M.STONE)
        # Guardian lions at both ends
        add_guardian_lion(fills, cx - half_w - 3, 3, z_start + 2)
        add_guardian_lion(fills, cx + half_w + 3, 3, z_start + 2)
        add_guardian_lion(fills, cx - half_w - 3, 3, z_end - 2)
        add_guardian_lion(fills, cx + half_w + 3, 3, z_end - 2)
    else:
        # Bridge runs east-west
        x_inner = cx if cx == 0 else CITY_SIZE
        x_outer = -MOAT_OUTER if cx == 0 else CITY_SIZE + MOAT_OUTER
        x_start, x_end = sorted((x_inner, x_outer))
        add_fill(fills, f"bridge {cx},{cz} deck", (x_start, 3, cz - half_w), (x_end, 3, cz + half_w), M.SMOOTH)
        add_fill(fills, f"bridge {cx},{cz} rail n", (x_start, 4, cz - half_w - 1), (x_end, 5, cz - half_w - 1), M.ANDESITE)
        add_fill(fills, f"bridge {cx},{cz} rail s", (x_start, 4, cz + half_w + 1), (x_end, 5, cz + half_w + 1), M.ANDESITE)
        for x in range(x_start + 20, x_end - 19, 35):
            add_fill(fills, f"bridge {cx},{cz} pier {x}", (x - 2, 0, cz - half_w), (x + 2, 2, cz + half_w), M.STONE)
        add_guardian_lion(fills, x_start + 2, 3, cz - half_w - 3)
        add_guardian_lion(fills, x_start + 2, 3, cz + half_w + 3)
        add_guardian_lion(fills, x_end - 2, 3, cz - half_w - 3)
        add_guardian_lion(fills, x_end - 2, 3, cz + half_w + 3)


def build_moat_bridge_railings(fills: list[Fill]) -> None:
    for cx, cz, axis in GATE_BRIDGES:
        add_bridge(fills, cx, cz, axis)


def main() -> None:
    run_builder(build_moat_bridge_railings, "moat_bridge_railings")


if __name__ == "__main__":
    main()
