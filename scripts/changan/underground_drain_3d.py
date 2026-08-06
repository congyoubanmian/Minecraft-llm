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
    add_underground_room,
    run_builder,
)


"""
Underground Drain 3D (地下排水暗渠) - the vaulted brick sewer beneath
Zhuque Avenue, tying the surface ditch grid (drainage_ditches.py) into a
walkable underground layer.

Tang Chang'an drained its avenues through covered channels. This module
builds the main trunk under the imperial avenue plus sedimentation
chambers and inspection shafts - a whole hidden city layer at negative y.

Location in Chang'an city local coordinates:
    Trunk: x 2996..3004, z 800..5800 (directly under Zhuque Avenue).
    Inspection shafts at the avenue crossings z = 900, 1700, 2500,
    3300, 4100, 5000 (matching drainage_ditches.py AVENUE_ZS).

3D features:
    - Brick-vaulted trunk channel (floor y=-8, crown y=-2) with water
    - Five sedimentation chambers (wider rooms with sumps)
    - Inspection shafts up to street level, iron-bar grates on top
    - East/west branch stubs at the z=2500 crossing
    - One maintenance stair down into the z=2500 chamber
"""

TR_X1, TR_X2 = 2996, 3004
TR_Z1, TR_Z2 = 800, 5800
CHAMBER_ZS = [900, 1700, 2500, 3300, 4100, 5000]


def _shaft(fills: list[Fill], label: str, cx: int, cz: int) -> None:
    """Inspection shaft from the vault crown up to street level."""
    add_fill(fills, f"{label} hole", (cx - 1, -2, cz - 1), (cx + 1, 1, cz + 1), M.AIR)
    add_outline(fills, f"{label} lining n", cx - 2, cz - 2, cx + 2, cz - 2, -2, 1, M.STONE, thickness=1)
    add_outline(fills, f"{label} lining s", cx - 2, cz + 2, cx + 2, cz + 2, -2, 1, M.STONE, thickness=1)
    add_outline(fills, f"{label} lining w", cx - 2, cz - 2, cx - 2, cz + 2, -2, 1, M.STONE, thickness=1)
    add_outline(fills, f"{label} lining e", cx + 2, cz - 2, cx + 2, cz + 2, -2, 1, M.STONE, thickness=1)
    # Iron grate at street level
    add_fill(fills, f"{label} grate", (cx - 2, 2, cz - 2), (cx + 2, 2, cz + 2), M.IRON_BARS)


def _chamber(fills: list[Fill], label: str, cz: int) -> None:
    """Sedimentation chamber: wider room with a sump pit."""
    cx = (TR_X1 + TR_X2) // 2
    x1, x2 = cx - 8, cx + 8
    z1, z2 = cz - 8, cz + 8
    add_underground_room(fills, f"{label} room", x1, z1, x2, z2, y_floor=-8, y_ceiling=-2, block=M.DARK_BRICKS)
    # Sump pit in the middle, 3 deeper
    add_fill(fills, f"{label} sump", (cx - 3, -11, cz - 3), (cx + 3, -8, cz + 3), M.AIR)
    add_fill(fills, f"{label} sump floor", (cx - 3, -12, cz - 3), (cx + 3, -12, cz + 3), M.DARK)
    add_fill(fills, f"{label} sump water", (cx - 3, -11, cz - 3), (cx + 3, -10, cz + 3), M.WATER)
    # Wall niches with lanterns
    for dx in (-6, 6):
        add_fill(fills, f"{label} niche {dx}", (cx + dx, -6, cz - 1), (cx + dx, -4, cz + 1), M.AIR)
        add_fill(fills, f"{label} lamp {dx}", (cx + dx, -6, cz), (cx + dx, -6, cz), M.LANTERN)


def build_underground_drain_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Trunk channel: floor, water, walls, vaulted crown.
    # ------------------------------------------------------------------
    add_fill(fills, "drain trunk hollow", (TR_X1, -7, TR_Z1), (TR_X2, -3, TR_Z2), M.AIR)
    add_fill(fills, "drain trunk floor", (TR_X1 - 1, -8, TR_Z1), (TR_X2 + 1, -8, TR_Z2), M.DARK_BRICKS)
    add_fill(fills, "drain trunk water", (TR_X1 + 1, -7, TR_Z1), (TR_X2 - 1, -6, TR_Z2), M.WATER)
    add_fill(fills, "drain trunk wall w", (TR_X1 - 1, -7, TR_Z1), (TR_X1 - 1, -2, TR_Z2), M.DARK_BRICKS)
    add_fill(fills, "drain trunk wall e", (TR_X2 + 1, -7, TR_Z1), (TR_X2 + 1, -2, TR_Z2), M.DARK_BRICKS)
    # Vaulted crown: full slab at y=-2 plus stepped shoulders
    add_fill(fills, "drain trunk crown", (TR_X1 - 2, -2, TR_Z1), (TR_X2 + 2, -2, TR_Z2), M.DARK_BRICKS)
    add_fill(fills, "drain crown shoulder w", (TR_X1 - 1, -3, TR_Z1), (TR_X1 - 1, -3, TR_Z2), M.DARK_BRICKS)
    add_fill(fills, "drain crown shoulder e", (TR_X2 + 1, -3, TR_Z1), (TR_X2 + 1, -3, TR_Z2), M.DARK_BRICKS)
    # Wall ribs every 200 blocks (structural piers)
    for z in range(TR_Z1 + 200, TR_Z2, 200):
        add_fill(fills, f"drain rib w {z}", (TR_X1 - 2, -7, z), (TR_X1, -2, z + 2), M.STONE)
        add_fill(fills, f"drain rib e {z}", (TR_X2, -7, z), (TR_X2 + 2, -2, z + 2), M.STONE)

    # ------------------------------------------------------------------
    # 2. Chambers + inspection shafts at each avenue crossing.
    # ------------------------------------------------------------------
    for i, cz in enumerate(CHAMBER_ZS):
        _chamber(fills, f"drain chamber{i}", cz)
        _shaft(fills, f"drain shaft{i}", TR_X1 - 6, cz)

    # ------------------------------------------------------------------
    # 3. East/west branch stubs at the z=2500 crossing.
    # ------------------------------------------------------------------
    for name, (bx1, bx2) in [("west", (TR_X1 - 60, TR_X1)), ("east", (TR_X2, TR_X2 + 60))]:
        add_fill(fills, f"drain branch {name} hollow", (bx1, -7, 2498), (bx2, -3, 2502), M.AIR)
        add_fill(fills, f"drain branch {name} floor", (bx1, -8, 2498), (bx2, -8, 2502), M.DARK_BRICKS)
        add_fill(fills, f"drain branch {name} crown", (bx1, -2, 2497), (bx2, -2, 2503), M.DARK_BRICKS)
        add_fill(fills, f"drain branch {name} water", (bx1, -7, 2499), (bx2, -6, 2501), M.WATER)

    # ------------------------------------------------------------------
    # 4. Maintenance stair down into the z=2500 chamber.
    # ------------------------------------------------------------------
    for i in range(9):
        z = 2476 - i * 2
        y = 1 - i
        add_fill(fills, f"drain stair {i}", (3006, y, z), (3008, y, z + 1), M.SMOOTH)
        add_fill(fills, f"drain stair clear {i}", (3006, y + 1, z), (3008, y + 4, z + 1), M.AIR)
    add_fill(fills, "drain stair tunnel", (3006, -8, 2460), (3008, -4, 2492), M.AIR)


def main() -> None:
    run_builder(build_underground_drain_3d, "underground_drain_3d")


if __name__ == "__main__":
    main()
