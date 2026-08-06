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
    add_hollow_box,
    add_ridge_roof,
    run_builder,
)


"""
Waterwheel Mills 3D (水车水磨坊) - Tang grain mills on the Yong'an Canal.

Two mill houses stand on the north bank of the canal, each driving a great
vertical undershot wheel whose paddles dip into the current. The wheel is
built as a true circle in the vertical plane (scanline ring) - geometry a
flat build can never show - with spokes, paddles, and an axle running into
the mill's grindstone room.

Location in Chang'an city local coordinates:
    Yong'an Canal runs east-west along z=3500 (canal_waterway.py).
    Mills at x=800 and x=1800, north bank (z 3482..3498).

3D features:
    - Vertical scanline-ring waterwheel (r=9) with 8 paddles and spokes
    - Stone pier carrying the axle over the water
    - Two-storey mill house: grindstone room below, grain loft above
    - Sluice channel under the wheel and a wooden grain chute
    - Quay with bollards and lanterns along the canal bank
"""

CANAL_Z = 3500
MILLS = [800, 1800]
WHEEL_R = 9


def _wheel(fills: list[Fill], label: str, cx: int, cy: int, z: int) -> None:
    """Vertical ring in the x/y plane at fixed z, with spokes and paddles."""
    r = WHEEL_R
    for dy in range(-r, r + 1):
        half = int((r * r - dy * dy) ** 0.5)
        add_fill(fills, f"{label} rim w {dy}", (cx - half, cy + dy, z), (cx - half, cy + dy, z), M.WOOD)
        add_fill(fills, f"{label} rim e {dy}", (cx + half, cy + dy, z), (cx + half, cy + dy, z), M.WOOD)
    # Vertical and horizontal spokes
    add_fill(fills, f"{label} spoke v", (cx, cy - r, z), (cx, cy + r, z), M.LOG)
    add_fill(fills, f"{label} spoke h", (cx - r, cy, z), (cx + r, cy, z), M.LOG)
    # Eight paddles at the rim (N/S/E/W + diagonals)
    for i, (dx, dy) in enumerate([(0, r), (0, -r), (r, 0), (-r, 0), (6, 6), (6, -6), (-6, 6), (-6, -6)]):
        add_fill(fills, f"{label} paddle {i}", (cx + dx - 2, cy + dy, z - 1), (cx + dx + 2, cy + dy, z + 1), M.SPRUCE)


def _mill(fills: list[Fill], label: str, mx: int) -> None:
    """One mill house with its wheel overhanging the canal."""
    # Mill house on the north bank
    hx1, hz1 = mx - 14, CANAL_Z - 20
    hx2, hz2 = mx + 14, CANAL_Z - 4
    add_hollow_box(fills, f"{label} house low", hx1, 1, hz1, hx2, 12, hz2, M.STONE, thickness=2)
    add_hollow_box(fills, f"{label} house up", hx1 + 2, 13, hz1 + 2, hx2 - 2, 20, hz2 - 2, M.RED_WALL, thickness=1)
    add_fill(fills, f"{label} loft floor", (hx1 + 1, 12, hz1 + 1), (hx2 - 1, 12, hz2 - 1), M.WOOD)
    add_ridge_roof(fills, f"{label} roof", hx1 - 3, hz1 - 3, hx2 + 3, hz2 + 3, 21, layers=2, ridge_axis="x")
    # Door and grindstone inside
    add_fill(fills, f"{label} door", (mx - 2, 2, hz2 - 1), (mx + 2, 7, hz2), M.AIR)
    add_fill(fills, f"{label} grindstone base", (mx - 2, 1, hz1 + 6), (mx + 2, 2, hz1 + 10), M.DARK)
    add_fill(fills, f"{label} grindstone", (mx - 1, 3, hz1 + 7), (mx + 1, 5, hz1 + 9), M.ANDESITE)

    # Axle from the house out over the canal, on a stone pier
    wheel_y = 11
    wheel_z = CANAL_Z + 2
    add_fill(fills, f"{label} axle pier", (mx - 2, 0, CANAL_Z + 1), (mx + 2, wheel_y - 1, CANAL_Z + 3), M.STONE)
    add_fill(fills, f"{label} axle", (mx, wheel_y, hz1 + 8), (mx, wheel_y, wheel_z), M.LOG)
    _wheel(fills, f"{label} wheel", mx, wheel_y, wheel_z)

    # Sluice channel under the wheel: carved water race with stone sides
    add_fill(fills, f"{label} sluice water", (mx - 4, 0, CANAL_Z - 2), (mx + 4, 1, CANAL_Z + 6), M.WATER)
    add_fill(fills, f"{label} sluice wall w", (mx - 5, 0, CANAL_Z - 2), (mx - 5, 2, CANAL_Z + 6), M.STONE)
    add_fill(fills, f"{label} sluice wall e", (mx + 5, 0, CANAL_Z - 2), (mx + 5, 2, CANAL_Z + 6), M.STONE)

    # Grain chute from the loft down to the quay
    add_fill(fills, f"{label} chute", (mx + 8, 12, hz2 - 2), (mx + 12, 2, hz2 + 6), M.SPRUCE)

    # Quay along the bank with bollards and a lantern
    add_fill(fills, f"{label} quay", (mx - 16, 1, hz2 + 1), (mx + 16, 1, CANAL_Z - 1), M.SMOOTH)
    for i, bx in enumerate(range(mx - 12, mx + 13, 8)):
        add_fill(fills, f"{label} bollard {i}", (bx, 2, CANAL_Z - 2), (bx, 4, CANAL_Z - 2), M.LOG)
    add_fill(fills, f"{label} lantern post", (mx - 15, 2, CANAL_Z - 2), (mx - 15, 7, CANAL_Z - 2), M.LOG)
    add_fill(fills, f"{label} lantern", (mx - 15, 8, CANAL_Z - 2), (mx - 15, 8, CANAL_Z - 2), M.LANTERN)


def build_waterwheel_mill_3d(fills: list[Fill]) -> None:
    for i, mx in enumerate(MILLS):
        _mill(fills, f"mill{i}", mx)


def main() -> None:
    run_builder(build_waterwheel_mill_3d, "waterwheel_mill_3d")


if __name__ == "__main__":
    main()
