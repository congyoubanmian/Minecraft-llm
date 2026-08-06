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
    add_dougong_cluster,
    add_fill,
    add_hollow_box,
    add_outline,
    add_ridge_roof,
    run_builder,
)


"""
Wall Enemy Towers 3D (城墙双层敌楼) - two-storey fighting towers on top of
the outer city wall, upgrading the flat watch-tower line from
wall_battlement_moat.py.

Wall facts (from wall_battlement_moat.py):
    wall top at y=39, thickness 34 blocks (z 0..33 south wall,
    z 5966..5999 north wall).

Towers sit BETWEEN the existing 300-spacing watch towers:
    south wall (z=0):    x = 1350, 4350
    north wall (z=5999): x = 1350, 4350

3D features:
    - Tower body straddling the wall top, two full storeys
    - Cantilevered hoarding (悬楼) jutting over the outer face,
      with murder holes left open beneath
    - Arrow slits on all faces at both storey levels
    - Internal ladder stair between wall walk, storeys, and roof deck
    - Dougong capitals and a glazed ridge roof
    - Beacon brazier on the roof deck
"""

WALL_TOP = 39
TOWERS = [
    ("s1350", 1350, 0, 33, +1),      # south wall, outer face toward -z
    ("s4350", 4350, 0, 33, +1),
    ("n1350", 1350, 5966, 5999, -1),  # north wall, outer face toward +z
    ("n4350", 4350, 5966, 5999, -1),
]

BODY_Y1 = WALL_TOP + 1        # 40
STOREY1_TOP = BODY_Y1 + 9     # 49
STOREY2_TOP = STOREY1_TOP + 9 # 58
HALF = 12                     # tower half width


def _tower(fills: list[Fill], label: str, cx: int, z_in1: int, z_in2: int, outward: int) -> None:
    z_mid = (z_in1 + z_in2) // 2
    x1, x2 = cx - HALF, cx + HALF
    z1, z2 = z_in1 - 4 if outward > 0 else z_in1, z_in2 + 4 if outward < 0 else z_in2
    z1, z2 = min(z1, z2), max(z1, z2)

    # Two-storey body
    add_hollow_box(fills, f"{label} storey1", x1, BODY_Y1, z1, x2, STOREY1_TOP, z2, M.DARK_BRICKS, thickness=2)
    add_fill(fills, f"{label} floor2", (x1 + 1, STOREY1_TOP, z1 + 1), (x2 - 1, STOREY1_TOP, z2 - 1), M.WOOD)
    add_hollow_box(fills, f"{label} storey2", x1 + 2, STOREY1_TOP + 1, z1 + 2, x2 - 2, STOREY2_TOP, z2 - 2, M.RED_WALL, thickness=2)

    # Arrow slits on all four faces, both storeys
    for lvl, (ly1, ly2) in enumerate([(BODY_Y1 + 3, BODY_Y1 + 5), (STOREY1_TOP + 4, STOREY1_TOP + 6)]):
        half_lvl = HALF if lvl == 0 else HALF - 2
        for off in (-7, 0, 7):
            add_fill(fills, f"{label} slit l{lvl} w {off}", (cx - half_lvl, ly1, z_mid + off), (cx - half_lvl, ly2, z_mid + off + 1), M.AIR)
            add_fill(fills, f"{label} slit l{lvl} e {off}", (cx + half_lvl, ly1, z_mid + off), (cx + half_lvl, ly2, z_mid + off + 1), M.AIR)
            add_fill(fills, f"{label} slit l{lvl} n {off}", (cx + off, ly1, z_mid - half_lvl), (cx + off + 1, ly2, z_mid - half_lvl), M.AIR)
            add_fill(fills, f"{label} slit l{lvl} s {off}", (cx + off, ly1, z_mid + half_lvl), (cx + off + 1, ly2, z_mid + half_lvl), M.AIR)

    # Cantilevered hoarding jutting over the outer face
    hz1 = z_mid - HALF - 2 if outward > 0 else z_mid + HALF - 4
    hz2 = z_mid + HALF - 4 if outward > 0 else z_mid + HALF + 2
    add_cantilevered_floor(
        fills, f"{label} hoarding",
        x1, min(hz1, hz2), x2, max(hz1, hz2),
        y=STOREY1_TOP + 1, overhang=3, block=M.WOOD, support_block=M.LOG,
    )
    add_outline(fills, f"{label} hoarding rail", x1 - 3, min(hz1, hz2) - 3, x2 + 3, max(hz1, hz2) + 3, STOREY1_TOP + 2, STOREY1_TOP + 2, M.FENCE, thickness=1)
    # Murder holes: two gaps carved under the hoarding lip
    outer_z = min(hz1, hz2) - 3 if outward > 0 else max(hz1, hz2) + 3
    for off in (-6, 6):
        add_fill(fills, f"{label} murder hole {off}", (cx + off, STOREY1_TOP + 1, outer_z), (cx + off + 2, STOREY1_TOP + 1, outer_z), M.AIR)

    # Internal stair: wall walk -> storey1 -> storey2 -> roof
    for i in range(18):
        sx = x1 + 3 + (i % 6)
        sz = z1 + 3 if i < 9 else z2 - 3
        add_fill(fills, f"{label} stair {i}", (sx, BODY_Y1 + 1 + i, sz), (sx + 1, BODY_Y1 + 1 + i, sz + 1), M.SMOOTH)

    # Dougong capitals and ridge roof
    for sx in (-1, 1):
        for sz in (-1, 1):
            add_dougong_cluster(
                fills, f"{label} dougong {sx},{sz}",
                cx + sx * (HALF - 2), z_mid + sz * (HALF - 2), y=STOREY2_TOP, tiers=2,
            )
    add_ridge_roof(fills, f"{label} roof", x1 - 2, z1 - 2, x2 + 2, z2 + 2, STOREY2_TOP + 2, layers=3, ridge_axis="x")

    # Beacon brazier on the roof deck
    add_fill(fills, f"{label} beacon base", (cx - 2, STOREY2_TOP + 3, z_mid - 2), (cx + 2, STOREY2_TOP + 4, z_mid + 2), M.DARK)
    add_fill(fills, f"{label} beacon fire", (cx - 1, STOREY2_TOP + 5, z_mid - 1), (cx + 1, STOREY2_TOP + 5, z_mid + 1), M.LANTERN)

    # Door from the wall walk into storey 1
    add_fill(fills, f"{label} door", (cx - 2, BODY_Y1 + 1, z_mid - 1 if outward > 0 else z_mid + 1), (cx + 2, BODY_Y1 + 6, z_mid + 1 if outward > 0 else z_mid + 3), M.AIR)


def build_wall_dilou_3d(fills: list[Fill]) -> None:
    for label, cx, z_in1, z_in2, outward in TOWERS:
        _tower(fills, f"dilou {label}", cx, z_in1, z_in2, outward)


def main() -> None:
    run_builder(build_wall_dilou_3d, "wall_dilou_3d")


if __name__ == "__main__":
    main()
