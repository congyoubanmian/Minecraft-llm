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
    add_hollow_box,
    add_outline,
    add_pyramid_roof,
    add_staircase,
    run_builder,
)


"""
Watchtower Network 3D (望楼系统) - six timber drum-signal watchtowers
flanking Zhuque Avenue (朱雀大街), modelled on the relay towers of
"The Longest Day in Chang'an" (长安十二时辰) that passed drum and flag
signals across the city.

The avenue roadway spans roughly local X 2950-3050; every tower keeps
clear of it (west-column yard edge x=2850, east-column yard edge x=3150).

Tower positions (local city coordinates; all y values are local):
    W1 (2860, 1000)  E2 (3140, 1700)  W3 (2860, 2400)
    E4 (3140, 3100)  W5 (2860, 3800)  E6 (3140, 4500)

All six towers share one design (see _watchtower), ~38 blocks tall:
    - Four 2x2 dark-oak corner posts (M.LOG) at +-6 from the centre,
      y 1..38, tied by M.WOOD ring beams every ~8 blocks (y 9/18/27)
      with short M.FENCE cross-bracing diagonals on all four faces
    - Ground yard (~20x20, M.FENCE) with a hitch-post stone
      (M.SMOOTH + M.FENCE) and a 4x4 guard hut (M.WOOD, flat slab roof)
    - Two-stage internal access: lower half by two add_staircase runs
      with a mid landing (y 2 -> 10 -> 18), upper half by ladder-like
      alternating blocks (y 19 -> 34) onto the drum deck
    - Cantilevered observation platform (add_cantilevered_floor,
      overhang 3) at y=22 with an M.FENCE railing
    - Top drum deck (y=35): plank floor, 3x3x3 red war-drum
      (M.RED_WOOL wrapped in an M.LOG frame), 2 signal lanterns
    - Pyramidal pavilion roof (攒尖顶, add_pyramid_roof) at y=41 on
      four short corner columns, with a gilded apex
    - Alternating red/yellow wool signal flag on a side pole that
      pierces the eastern eave
"""

TOWERS = [
    ("w1", 2860, 1000),
    ("e2", 3140, 1700),
    ("w3", 2860, 2400),
    ("e4", 3140, 3100),
    ("w5", 2860, 3800),
    ("e6", 3140, 4500),
]

GROUND_Y = 1
POST_TOP = 38
PLATFORM_Y = 22
DECK_Y = 35
ROOF_Y = 41
HUT_SLAB = "minecraft:dark_oak_slab[type=bottom,waterlogged=false]"


def _watchtower(fills: list[Fill], label: str, cx: int, cz: int) -> None:
    # ------------------------------------------------------------------
    # 1. Ground yard (~20x20 fence) with hitch-post stone and guard hut.
    # ------------------------------------------------------------------
    add_outline(fills, f"{label} yard", cx - 10, cz - 10, cx + 10, cz + 10, GROUND_Y, GROUND_Y, M.FENCE, thickness=1)
    add_fill(fills, f"{label} hitch stone", (cx + 8, GROUND_Y, cz - 8), (cx + 8, GROUND_Y + 1, cz - 8), M.SMOOTH)
    add_fill(fills, f"{label} hitch ring", (cx + 8, GROUND_Y + 2, cz - 8), (cx + 8, GROUND_Y + 2, cz - 8), M.FENCE)
    add_hollow_box(fills, f"{label} hut", cx - 2, GROUND_Y, cz + 6, cx + 1, GROUND_Y + 3, cz + 9, M.WOOD, thickness=1)
    add_fill(fills, f"{label} hut roof", (cx - 3, GROUND_Y + 4, cz + 5), (cx + 2, GROUND_Y + 4, cz + 10), HUT_SLAB)
    add_fill(fills, f"{label} hut door", (cx - 1, GROUND_Y, cz + 6), (cx, GROUND_Y + 1, cz + 6), M.AIR)

    # ------------------------------------------------------------------
    # 2. Timber frame: four 2x2 corner posts, ring beams, cross-bracing.
    # ------------------------------------------------------------------
    for sx in (-1, 1):
        for sz in (-1, 1):
            x0 = cx + 6 if sx > 0 else cx - 7
            z0 = cz + 6 if sz > 0 else cz - 7
            add_fill(fills, f"{label} post {sx},{sz}", (x0, GROUND_Y, z0), (x0 + 1, POST_TOP, z0 + 1), M.LOG)
    for ring_y in (9, 18, 27):
        add_outline(fills, f"{label} ring {ring_y}", cx - 7, cz - 7, cx + 7, cz + 7, ring_y, ring_y, M.WOOD, thickness=1)
    # Short fence diagonals suggesting cross-bracing on each face
    for bx, by, bz, suffix in (
        (cx - 3, 13, cz - 7, "n1"), (cx - 2, 14, cz - 7, "n2"),
        (cx + 2, 13, cz + 7, "s1"), (cx + 3, 14, cz + 7, "s2"),
        (cx - 7, 13, cz - 3, "w1"), (cx - 7, 14, cz - 2, "w2"),
        (cx + 7, 13, cz + 2, "e1"), (cx + 7, 14, cz + 3, "e2"),
    ):
        add_fill(fills, f"{label} brace {suffix}", (bx, by, bz), (bx, by, bz), M.FENCE)

    # ------------------------------------------------------------------
    # 3. Two-stage access: stairs + mid landing, then ladder blocks.
    # ------------------------------------------------------------------
    add_staircase(fills, f"{label} stair a", cx - 3, cz - 5, cx - 2, cz - 1, 2, 10, "north", M.WOOD)
    add_fill(fills, f"{label} landing 1", (cx - 3, 10, cz - 1), (cx - 1, 10, cz + 2), M.WOOD)
    add_staircase(fills, f"{label} stair b", cx - 3, cz + 3, cx - 2, cz + 7, 10, 18, "north", M.WOOD)
    add_fill(fills, f"{label} landing 2", (cx - 3, 18, cz + 5), (cx - 1, 18, cz + 7), M.WOOD)
    for i in range(8):
        lx = cx - 3 + (i % 2)
        y0 = 19 + i * 2
        add_fill(fills, f"{label} ladder {i}", (lx, y0, cz + 6), (lx, y0 + 1, cz + 6), M.WOOD)

    # ------------------------------------------------------------------
    # 4. Mid-height cantilevered observation platform with railing.
    # ------------------------------------------------------------------
    add_cantilevered_floor(
        fills, f"{label} obs platform",
        cx - 7, cz - 7, cx + 7, cz + 7,
        PLATFORM_Y, overhang=3, block=M.WOOD, support_block=M.LOG,
    )
    add_outline(fills, f"{label} obs rail", cx - 10, cz - 10, cx + 10, cz + 10, PLATFORM_Y + 1, PLATFORM_Y + 1, M.FENCE, thickness=1)

    # ------------------------------------------------------------------
    # 5. Top drum deck: plank floor, war-drum, lanterns.
    # ------------------------------------------------------------------
    add_fill(fills, f"{label} drum deck", (cx - 7, DECK_Y, cz - 7), (cx + 7, DECK_Y, cz + 7), M.WOOD)
    add_fill(fills, f"{label} war drum", (cx - 1, DECK_Y + 1, cz - 1), (cx + 1, DECK_Y + 3, cz + 1), M.RED_WOOL)
    for sx in (-1, 1):
        for sz in (-1, 1):
            add_fill(
                fills, f"{label} drum frame {sx},{sz}",
                (cx + sx * 2, DECK_Y + 1, cz + sz * 2),
                (cx + sx * 2, DECK_Y + 4, cz + sz * 2),
                M.LOG,
            )
    add_fill(fills, f"{label} lantern nw", (cx - 5, DECK_Y + 1, cz - 5), (cx - 5, DECK_Y + 1, cz - 5), M.LANTERN)
    add_fill(fills, f"{label} lantern se", (cx + 5, DECK_Y + 1, cz + 5), (cx + 5, DECK_Y + 1, cz + 5), M.LANTERN)

    # ------------------------------------------------------------------
    # 6. Pyramidal pavilion roof (攒尖顶) on four short corner columns.
    # ------------------------------------------------------------------
    for sx in (-1, 1):
        for sz in (-1, 1):
            add_fill(
                fills, f"{label} roof col {sx},{sz}",
                (cx + sx * 4, DECK_Y + 1, cz + sz * 4),
                (cx + sx * 4, ROOF_Y - 1, cz + sz * 4),
                M.LOG,
            )
    add_pyramid_roof(fills, f"{label} roof", cx, cz, 4, ROOF_Y, M.ROOF_GREEN, M.GOLD)

    # ------------------------------------------------------------------
    # 7. Signal flag on a side pole (built last: the pole pierces the eave).
    # ------------------------------------------------------------------
    add_fill(fills, f"{label} flag pole", (cx + 5, DECK_Y + 1, cz + 2), (cx + 5, DECK_Y + 10, cz + 2), M.FENCE)
    add_fill(fills, f"{label} flag red top", (cx + 6, DECK_Y + 9, cz + 2), (cx + 8, DECK_Y + 9, cz + 2), M.RED_WOOL)
    add_fill(fills, f"{label} flag yellow", (cx + 6, DECK_Y + 8, cz + 2), (cx + 8, DECK_Y + 8, cz + 2), M.YELLOW_WOOL)
    add_fill(fills, f"{label} flag red bottom", (cx + 6, DECK_Y + 7, cz + 2), (cx + 8, DECK_Y + 7, cz + 2), M.RED_WOOL)


def build_wanglou_network_3d(fills: list[Fill]) -> None:
    for name, cx, cz in TOWERS:
        _watchtower(fills, f"wanglou {name}", cx, cz)


def main() -> None:
    run_builder(build_wanglou_network_3d, "wanglou_network_3d")


if __name__ == "__main__":
    main()
