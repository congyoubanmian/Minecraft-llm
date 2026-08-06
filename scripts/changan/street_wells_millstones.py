from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    Fill,
    Materials as M,
    WARD_BLOCK_SIZE,
    add_fill,
    iter_ward_origins,
    run_builder,
)


"""
Public wells with stone curbs and wooden covers, millstones, and firewood stacks
scattered through ward lanes and market corners.
"""


MARKETS = [
    (760, 2060, 1760, 3060),   # West Market
    (4240, 2060, 5240, 3060),  # East Market
]


def add_well(fills: list[Fill], label: str, x: int, z: int, y: int = 1) -> None:
    """A public well with a stone curb and wooden cover."""
    add_fill(fills, f"{label} curb", (x - 3, y, z - 3), (x + 3, y + 2, z + 3), M.ANDESITE)
    add_fill(fills, f"{label} water", (x - 2, y, z - 2), (x + 2, y, z + 2), M.WATER)
    add_fill(fills, f"{label} cover", (x - 3, y + 3, z - 3), (x + 3, y + 3, z + 3), M.WOOD)
    add_fill(fills, f"{label} hole", (x - 1, y + 3, z - 1), (x + 1, y + 3, z + 1), M.AIR)
    add_fill(fills, f"{label} winch", (x, y + 4, z), (x, y + 6, z), M.LOG)


def add_millstone(fills: list[Fill], label: str, x: int, z: int, y: int = 1) -> None:
    """Round millstone on the ground."""
    add_fill(fills, f"{label} stone", (x - 2, y, z - 2), (x + 2, y + 1, z + 2), M.SMOOTH)
    add_fill(fills, f"{label} axle", (x, y + 2, z), (x, y + 3, z), M.ANDESITE)


def add_firewood_stack(fills: list[Fill], label: str, x: int, z: int, y: int = 1) -> None:
    """A stack of firewood."""
    add_fill(fills, f"{label} base", (x - 2, y, z - 2), (x + 2, y + 2, z + 2), M.SPRUCE)
    add_fill(fills, f"{label} top", (x - 1, y + 3, z - 1), (x + 1, y + 3, z + 1), M.SPRUCE)


def build_street_wells_millstones(fills: list[Fill]) -> None:
    for wx, wz in iter_ward_origins():
        # Central well at the lane intersection
        mid_x = wx + WARD_BLOCK_SIZE // 2
        mid_z = wz + WARD_BLOCK_SIZE // 2
        add_well(fills, f"ward well {wx},{wz}", mid_x, mid_z)

        # Millstones near each quadrant mansion
        offsets = [(45, 45), (215, 45), (45, 215), (215, 215)]
        for idx, (ox, oz) in enumerate(offsets):
            add_millstone(fills, f"ward millstone {wx},{wz} {idx}", wx + ox, wz + oz)

        # Firewood stacks at alternating ward corners
        if (wx + wz) % 520 == 0:
            for idx, (ox, oz) in enumerate([(30, 130), (230, 130), (130, 30), (130, 230)]):
                add_firewood_stack(fills, f"ward wood {wx},{wz} {idx}", wx + ox, wz + oz)

    # Market corners and centers
    for mx1, mz1, mx2, mz2 in MARKETS:
        cx, cz = (mx1 + mx2) // 2, (mz1 + mz2) // 2
        add_well(fills, f"market well {cx},{cz}", cx, cz, y=2)
        for idx, (ox, oz) in enumerate([(-200, -200), (200, -200), (-200, 200), (200, 200)]):
            add_millstone(fills, f"market millstone {cx},{cz} {idx}", cx + ox, cz + oz)
        for idx, (ox, oz) in enumerate([(-150, -300), (150, -300), (-150, 300), (150, 300)]):
            add_firewood_stack(fills, f"market wood {cx},{cz} {idx}", cx + ox, cz + oz)


def main() -> None:
    run_builder(build_street_wells_millstones, "street_wells_millstones")


if __name__ == "__main__":
    main()
