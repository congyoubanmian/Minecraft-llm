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
    add_spiral_stair,
    add_underground_room,
    run_builder,
)


"""
Imperial Observatory 3D (司天台) - the Tang star-gazing tower.

A tall stepped tower east of Daming Palace, exploiting vertical space in
three directions: a deep underground star-map chamber, the stepped tower
body wrapped by an external spiral stair, and a bronze armillary sphere
(浑天仪) floating above the top platform.

Location in Chang'an city local coordinates:
    center: (4400, 5900)  (just east of Daming Palace's east wall at
    x=4200, on the northern high ground)

3D features:
    - Four setback tiers (44 -> 20 blocks) rising to y=48
    - External spiral stair wrapping the tower from ground to summit
    - Armillary sphere: three perpendicular gold rings + glass core
      hovering over the top platform on a dark-stone pedestal
    - Underground star-map chamber with sea-lantern constellations
    - Entry stair shaft descending from the tower base
"""

CX = 4400
CZ = 5900


def build_observatory_3d(fills: list[Fill]) -> None:
    add_fill(fills, "observatory clear", (CX - 40, 1, CZ - 40), (CX + 40, 70, CZ + 40), M.AIR)

    # ------------------------------------------------------------------
    # 1. Underground star-map chamber (地下星图室).
    # ------------------------------------------------------------------
    add_underground_room(fills, "observatory starmap", CX - 16, CZ - 16, CX + 16, CZ + 16, y_floor=-8, y_ceiling=-2, block=M.DARK_BRICKS)
    # Constellation inlays: sea lanterns set into the dark floor
    for i, (dx, dz) in enumerate([(-10, -8), (-4, -12), (2, -6), (8, -10), (12, -2), (-12, 4), (-6, 10), (4, 8), (10, 6), (0, 0)]):
        add_fill(fills, f"starmap star {i}", (CX + dx, -9, CZ + dz), (CX + dx, -9, CZ + dz), M.SEA_LANTERN)
    # Central globe pedestal
    add_fill(fills, "starmap pedestal", (CX - 1, -8, CZ - 1), (CX + 1, -6, CZ + 1), M.GOLD_ACCENT)
    add_fill(fills, "starmap globe", (CX - 2, -5, CZ - 2), (CX + 2, -3, CZ + 2), M.ROOF_BLUE)

    # Entry stair shaft on the south side, ground (y=1) down to y=-7
    for i in range(9):
        z = CZ - 26 + i * 2
        y = 1 - i
        add_fill(fills, f"starmap stair {i}", (CX - 2, y, z), (CX + 2, y, z + 1), M.SMOOTH)
        add_fill(fills, f"starmap stair clear {i}", (CX - 2, y + 1, z), (CX + 2, y + 4, z + 1), M.AIR)
    add_fill(fills, "starmap tunnel", (CX - 2, -8, CZ - 15), (CX + 2, -4, CZ - 8), M.AIR)

    # ------------------------------------------------------------------
    # 2. Stepped tower body: four setback tiers up to y=48.
    # ------------------------------------------------------------------
    tiers = [(22, 1, 12), (17, 12, 24), (13, 24, 36), (9, 36, 48)]
    for t, (half, y1, y2) in enumerate(tiers):
        add_fill(fills, f"observatory tier {t}", (CX - half, y1, CZ - half), (CX + half, y2, CZ + half), M.DARK)
        # Light stone trim band on each setback ledge
        add_outline(fills, f"observatory trim {t}", CX - half, CZ - half, CX + half, CZ + half, y2, y2, M.ANDESITE, thickness=1)

    # External spiral stair wrapping the body, ground -> summit
    add_spiral_stair(fills, "observatory stair", CX, CZ, radius=24, y1=1, y2=12, block=M.SMOOTH)
    add_spiral_stair(fills, "observatory stair 2", CX, CZ, radius=19, y1=12, y2=24, block=M.SMOOTH)
    add_spiral_stair(fills, "observatory stair 3", CX, CZ, radius=15, y1=24, y2=36, block=M.SMOOTH)
    add_spiral_stair(fills, "observatory stair 4", CX, CZ, radius=11, y1=36, y2=48, block=M.SMOOTH)

    # Summit platform + balustrade
    add_fill(fills, "observatory summit", (CX - 10, 48, CZ - 10), (CX + 10, 49, CZ + 10), M.ANDESITE)
    add_outline(fills, "observatory summit rail", CX - 10, CZ - 10, CX + 10, CZ + 10, 50, 50, M.QUARTZ, thickness=1)

    # ------------------------------------------------------------------
    # 3. Armillary sphere (浑天仪) above the summit.
    # ------------------------------------------------------------------
    # Pedestal
    add_fill(fills, "armillary pedestal", (CX - 3, 49, CZ - 3), (CX + 3, 54, CZ + 3), M.DARK_BRICKS)
    add_fill(fills, "armillary pedestal cap", (CX - 4, 55, CZ - 4), (CX + 4, 56, CZ + 4), M.GOLD_ACCENT)
    # Three perpendicular rings, centred at y=63, radius 8 (square rings)
    cy = 63
    # horizontal equator ring
    add_outline(fills, "armillary equator", CX - 8, CZ - 8, CX + 8, CZ + 8, cy, cy, M.GOLD, thickness=1)
    # vertical meridian rings (x-axis and z-axis), four edges each
    for label, axis in [("meridian x", "x"), ("meridian z", "z")]:
        for lo, hi in [(-8, -8), (8, 8)]:
            if axis == "x":
                add_fill(fills, f"armillary {label} v{lo}", (CX + lo, cy - 8, CZ), (CX + hi, cy + 8, CZ), M.GOLD)
                add_fill(fills, f"armillary {label} h{lo}", (CX - 8, cy + lo, CZ), (CX + 8, cy + hi, CZ), M.GOLD)
            else:
                add_fill(fills, f"armillary {label} v{lo}", (CX, cy - 8, CZ + lo), (CX, cy + 8, CZ + hi), M.GOLD)
                add_fill(fills, f"armillary {label} h{lo}", (CX, cy + lo, CZ - 8), (CX, cy + hi, CZ + 8), M.GOLD)
    # Glass celestial globe at the core
    add_fill(fills, "armillary core", (CX - 2, cy - 2, CZ - 2), (CX + 2, cy + 2, CZ + 2), M.RED_STAINED_GLASS)
    add_fill(fills, "armillary heart", (CX - 1, cy - 1, CZ - 1), (CX + 1, cy + 1, CZ + 1), M.SEA_LANTERN)

    # ------------------------------------------------------------------
    # 4. Corner braziers on the summit.
    # ------------------------------------------------------------------
    for sx in (-1, 1):
        for sz in (-1, 1):
            bx, bz = CX + sx * 7, CZ + sz * 7
            add_fill(fills, f"observatory brazier {sx},{sz}", (bx - 1, 49, bz - 1), (bx + 1, 51, bz + 1), M.GOLD_ACCENT)
            add_fill(fills, f"observatory flame {sx},{sz}", (bx, 52, bz), (bx, 52, bz), M.LANTERN)


def main() -> None:
    run_builder(build_observatory_3d, "observatory_3d")


if __name__ == "__main__":
    main()
