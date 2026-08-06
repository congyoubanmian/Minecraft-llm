from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    Fill,
    Materials as M,
    add_cantilevered_floor,
    add_fill,
    add_outline,
    add_ridge_roof,
    add_staircase,
    add_underground_room,
    run_builder,
)


"""
Polo Stadium 3D (马球场看台) - grandstands and royal pavilion around the
existing polo field from entertainment_venues.py.

Overlays the flat polo field with true spectator architecture: stepped
grandstands on the long sides, a cantilevered royal viewing pavilion
(彩楼) on the west, and horse stables hidden underneath the south stand.

Location in Chang'an city local coordinates:
    field: x 5000..5800, z 4800..5600 (same footprint as
    entertainment_venues.build_entertainment_venues polo ground)

3D features:
    - Six-tier stepped grandstands along the north and south sides
    - Wooden bench rows and aisle stairs on every stand
    - Royal pavilion (彩楼) raised on columns, with a cantilevered
      balcony hanging over the field and a glazed-tile roof
    - Underground stable yard beneath the south stand: stalls, tack
      room, and two entry ramps
    - Goal posts at both ends and a lantern ring for night matches
"""

FX1, FZ1 = 5000, 4800
FX2, FZ2 = 5800, 5600
CZ_MID = 5200


def _grandstand(fills: list[Fill], name: str, z_edge: int, outward: int) -> None:
    """Six-tier stepped grandstand. outward=+1 builds toward +z, -1 toward -z."""
    tiers = 6
    depth = 6
    for t in range(tiers):
        z_in = z_edge + outward * t * depth
        z_out = z_edge + outward * (t * depth + depth - 1)
        y = 1 + t * 2
        z_lo, z_hi = min(z_in, z_out), max(z_in, z_out)
        # Stone base + wooden bench surface
        add_fill(fills, f"{name} tier {t} base", (FX1 - 20, y, z_lo), (FX2 + 20, y + 1, z_hi), M.STONE)
        add_fill(fills, f"{name} tier {t} bench", (FX1 - 20, y + 2, z_lo), (FX2 + 20, y + 2, z_hi), M.WOOD)
    # Back wall on the outermost edge
    z_back = z_edge + outward * (tiers * depth)
    add_fill(fills, f"{name} back wall", (FX1 - 20, 1, z_back), (FX2 + 20, 14, z_back), M.RED_WALL)
    # Aisle stairs every 100 blocks along the stand
    for x in range(FX1, FX2 + 1, 100):
        if outward > 0:
            add_staircase(fills, f"{name} aisle {x}", x, z_edge, x + 3, z_edge + tiers * depth - 1, y1=1, y2=1 + (tiers - 1) * 2 + 2, direction="south", block=M.SMOOTH)
        else:
            add_staircase(fills, f"{name} aisle {x}", x, z_edge - (tiers * depth - 1), x + 3, z_edge, y1=1, y2=1 + (tiers - 1) * 2 + 2, direction="north", block=M.SMOOTH)
    # Canopy roof over the top two tiers, on columns
    z_canopy_lo, z_canopy_hi = sorted((z_edge + outward * 4 * depth, z_edge + outward * (tiers * depth - 1)))
    for x in range(FX1 - 20, FX2 + 21, 40):
        add_fill(fills, f"{name} canopy col {x}", (x, 13, z_canopy_lo), (x + 1, 22, z_canopy_lo + 1), M.LOG)
        add_fill(fills, f"{name} canopy col b {x}", (x, 13, z_canopy_hi - 1), (x + 1, 22, z_canopy_hi), M.LOG)
    add_fill(fills, f"{name} canopy roof", (FX1 - 24, 23, z_canopy_lo - 3), (FX2 + 24, 24, z_canopy_hi + 3), M.ROOF_GREEN)


def build_polo_stadium_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. North and south grandstands.
    # ------------------------------------------------------------------
    _grandstand(fills, "polo stand north", FZ1 - 2, outward=-1)
    _grandstand(fills, "polo stand south", FZ2 + 2, outward=+1)

    # ------------------------------------------------------------------
    # 2. Royal viewing pavilion (彩楼) on the west side.
    # ------------------------------------------------------------------
    px1, px2 = FX1 - 70, FX1 - 10
    pz1, pz2 = CZ_MID - 60, CZ_MID + 60
    # Column grid raising the platform
    for x in range(px1 + 4, px2, 12):
        for z in range(pz1 + 4, pz2, 12):
            add_fill(fills, f"polo pavilion col {x},{z}", (x, 1, z), (x + 2, 15, z + 2), M.LOG)
    # Platform + cantilevered balcony hanging toward the field
    add_cantilevered_floor(fills, "polo pavilion deck", px1, pz1, px2, pz2, y=16, overhang=6, block=M.WOOD)
    add_outline(fills, "polo pavilion rail", px1 - 6, pz1 - 6, px2 + 6, pz2 + 6, 17, 17, M.FENCE, thickness=1)
    # Hall on the platform
    add_fill(fills, "polo pavilion wall w", (px1, 17, pz1), (px1 + 2, 26, pz2), M.RED_WALL)
    add_fill(fills, "polo pavilion wall n", (px1, 17, pz1), (px2, 26, pz1 + 2), M.RED_WALL)
    add_fill(fills, "polo pavilion wall s", (px1, 17, pz2 - 2), (px2, 26, pz2), M.RED_WALL)
    # Open east face toward the field: columns + lattice only
    for z in range(pz1 + 4, pz2 - 3, 12):
        add_fill(fills, f"polo pavilion mullion {z}", (px2 - 2, 17, z), (px2, 26, z + 2), M.LOG)
    add_ridge_roof(fills, "polo pavilion roof", px1 - 8, pz1 - 8, px2 + 8, pz2 + 8, 27, layers=3, ridge_axis="z")
    # Ceremonial stair from ground to the deck
    add_staircase(fills, "polo pavilion stair", px1 - 20, CZ_MID - 4, px1 - 2, CZ_MID + 4, y1=1, y2=16, direction="east", block=M.SMOOTH)

    # ------------------------------------------------------------------
    # 3. Underground stables beneath the south stand.
    # ------------------------------------------------------------------
    sx1, sx2 = FX1 + 60, FX2 - 60
    sz1, sz2 = FZ2 + 4, FZ2 + 34
    add_underground_room(fills, "polo stable", sx1, sz1, sx2, sz2, y_floor=-6, y_ceiling=-1, block=M.DARK_BRICKS)
    # Stall partitions and mangers along both walls
    for x in range(sx1 + 6, sx2 - 5, 10):
        add_fill(fills, f"stable partition n {x}", (x, -6, sz1 + 2), (x, -4, sz1 + 12), M.LOG)
        add_fill(fills, f"stable partition s {x}", (x, -6, sz2 - 12), (x, -4, sz2 - 2), M.LOG)
        add_fill(fills, f"stable manger n {x}", (x + 2, -6, sz1 + 2), (x + 6, -5, sz1 + 4), M.WOOD)
        add_fill(fills, f"stable manger s {x}", (x + 2, -6, sz2 - 4), (x + 6, -5, sz2 - 2), M.WOOD)
    # Stable lanterns
    for x in range(sx1 + 10, sx2 - 9, 40):
        add_fill(fills, f"stable lantern {x}", (x, -2, (sz1 + sz2) // 2), (x, -2, (sz1 + sz2) // 2), M.LANTERN)
    # Two entry ramps at the east and west ends
    for name, rx in [("west", sx1 - 14), ("east", sx2 + 2)]:
        for i in range(6):
            add_fill(fills, f"stable ramp {name} {i}", (rx, -6 + i, sz1 + 8), (rx + 11, -6 + i, sz1 + 14), M.SMOOTH)
            add_fill(fills, f"stable ramp {name} clear {i}", (rx, -5 + i, sz1 + 8), (rx + 11, -2 + i, sz1 + 14), M.AIR)

    # ------------------------------------------------------------------
    # 4. Goal posts and lantern ring.
    # ------------------------------------------------------------------
    for gx in (FX1 + 30, FX2 - 30):
        add_fill(fills, f"polo goal base {gx}", (gx - 2, 1, CZ_MID - 12), (gx + 2, 2, CZ_MID + 12), M.STONE)
        add_fill(fills, f"polo goal post n {gx}", (gx, 3, CZ_MID - 10), (gx, 12, CZ_MID - 10), M.RED_WALL_ALT)
        add_fill(fills, f"polo goal post s {gx}", (gx, 3, CZ_MID + 10), (gx, 12, CZ_MID + 10), M.RED_WALL_ALT)
        add_fill(fills, f"polo goal bar {gx}", (gx, 13, CZ_MID - 10), (gx, 14, CZ_MID + 10), M.GOLD)
    # Lantern posts along the field edges between the stands
    for x in range(FX1, FX2 + 1, 80):
        for z in (FZ1 + 4, FZ2 - 4):
            add_fill(fills, f"polo field post {x},{z}", (x, 1, z), (x, 7, z), M.LOG)
            add_fill(fills, f"polo field lantern {x},{z}", (x, 8, z), (x, 8, z), M.LANTERN)


def main() -> None:
    run_builder(build_polo_stadium_3d, "polo_stadium_3d")


if __name__ == "__main__":
    main()
