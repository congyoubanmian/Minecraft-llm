from __future__ import annotations

import math
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
Bell & Drum Towers 3D (钟鼓楼强化) - full rebuild of the Daming Palace
bell tower and drum tower with working interiors.

Replaces the plain towers from bell_drum_towers.py at:
    bell tower: (2200, 4200)   drum tower: (3800, 4200)

3D features:
    - Three-eave tower on a stone pedestal with all-round stairs
    - Bell tower: bronze bell hanging from a heavy timber frame,
      swung striker beam, sound-hole windows
    - Drum tower: platform of twelve red drums (十二面更鼓)
    - Internal switchback stair from ground to the bell/drum floor
    - Cantilevered viewing gallery + dougong tiers on every eave
"""

TOWERS = [
    ("bell", 2200, 4200),
    ("drum", 3800, 4200),
]

PED_TOP = 4
FLOOR1 = (PED_TOP + 1, PED_TOP + 12)      # 5..16
FLOOR2 = (FLOOR1[1] + 1, FLOOR1[1] + 11)  # 17..27
FLOOR3 = (FLOOR2[1] + 1, FLOOR2[1] + 10)  # 28..37


def _tower(fills: list[Fill], kind: str, cx: int, cz: int) -> None:
    label = f"{kind} tower"
    add_fill(fills, f"{label} clear", (cx - 20, 1, cz - 20), (cx + 20, 55, cz + 20), M.AIR)

    # Stone pedestal + all-round stairs
    add_fill(fills, f"{label} pedestal", (cx - 16, 1, cz - 16), (cx + 16, PED_TOP, cz + 16), M.STONE)
    add_outline(fills, f"{label} pedestal rail", cx - 16, cz - 16, cx + 16, cz + 16, PED_TOP + 1, PED_TOP + 1, M.QUARTZ, thickness=1)
    for i in range(4):
        add_fill(fills, f"{label} stair s {i}", (cx - 4, 1 + i, cz + 18 + i), (cx + 4, 1 + i, cz + 19 + i), M.SMOOTH)

    # Three storeys, each smaller
    halves = [13, 10, 7]
    floors = [FLOOR1, FLOOR2, FLOOR3]
    for t, (half, (y1, y2)) in enumerate(zip(halves, floors)):
        add_hollow_box(fills, f"{label} s{t}", cx - half, y1, cz - half, cx + half, y2, cz + half, M.RED_WALL, thickness=2)
        add_cantilevered_floor(fills, f"{label} gal s{t}", cx - half, cz - half, cx + half, cz + half, y=y2, overhang=3, block=M.WOOD)
        add_outline(fills, f"{label} rail s{t}", cx - half - 3, cz - half - 3, cx + half + 3, cz + half + 3, y2 + 1, y2 + 1, M.FENCE, thickness=1)
        for sx in (-1, 1):
            for sz in (-1, 1):
                add_dougong_cluster(fills, f"{label} dougong s{t} {sx},{sz}", cx + sx * half, cz + sz * half, y=y2, tiers=2)
        # Sound-hole windows on each face
        for off in (-5, 0, 5):
            add_fill(fills, f"{label} window s{t} n {off}", (cx + off, y1 + 4, cz - half), (cx + off + 2, y1 + 7, cz - half), M.AIR)
            add_fill(fills, f"{label} window s{t} s {off}", (cx + off, y1 + 4, cz + half), (cx + off + 2, y1 + 7, cz + half), M.AIR)
            add_fill(fills, f"{label} window s{t} w {off}", (cx - half, y1 + 4, cz + off), (cx - half, y1 + 7, cz + off + 2), M.AIR)
            add_fill(fills, f"{label} window s{t} e {off}", (cx + half, y1 + 4, cz + off), (cx + half, y1 + 7, cz + off + 2), M.AIR)

    add_ridge_roof(fills, f"{label} roof", cx - 10, cz - 10, cx + 10, cz + 10, FLOOR3[1] + 1, layers=4, ridge_axis="x")
    add_fill(fills, f"{label} finial", (cx - 1, FLOOR3[1] + 5, cz - 1), (cx + 1, FLOOR3[1] + 8, cz + 1), M.GOLD)

    # Internal switchback stair, pedestal top -> third floor
    for i in range(32):
        side = (i // 8) % 4
        step_y = PED_TOP + 1 + i
        off = -9 + (i % 8) * 2
        if side == 0:
            add_fill(fills, f"{label} stair {i}", (cx + off, step_y, cz - 9), (cx + off + 1, step_y, cz - 9), M.SMOOTH)
        elif side == 1:
            add_fill(fills, f"{label} stair {i}", (cx + 9, step_y, cz + off), (cx + 9, step_y, cz + off + 1), M.SMOOTH)
        elif side == 2:
            add_fill(fills, f"{label} stair {i}", (cx - off, step_y, cz + 9), (cx - off + 1, step_y, cz + 9), M.SMOOTH)
        else:
            add_fill(fills, f"{label} stair {i}", (cx - 9, step_y, cz - off), (cx - 9, step_y, cz - off + 1), M.SMOOTH)

    # Door at ground level
    add_fill(fills, f"{label} door", (cx - 2, PED_TOP + 1, cz + 12), (cx + 2, PED_TOP + 6, cz + 13), M.AIR)

    # ---- instrument floor (second storey) -----------------------------
    iy = FLOOR2[0]
    if kind == "bell":
        # Timber gallows frame + hanging bronze bell
        for dx in (-4, 4):
            add_fill(fills, f"{label} bell frame {dx}", (cx + dx, iy, cz - 1), (cx + dx + 1, iy + 8, cz + 1), M.LOG)
        add_fill(fills, f"{label} bell beam", (cx - 5, iy + 8, cz - 1), (cx + 5, iy + 9, cz + 1), M.LOG)
        add_fill(fills, f"{label} bell hook", (cx, iy + 6, cz), (cx, iy + 8, cz), M.IRON_BARS)
        add_fill(fills, f"{label} bell body", (cx - 2, iy + 2, cz - 2), (cx + 2, iy + 5, cz + 2), M.GOLD_ACCENT)
        add_fill(fills, f"{label} bell mouth", (cx - 3, iy + 1, cz - 3), (cx + 3, iy + 1, cz + 3), M.GOLD_ACCENT)
        # Striker beam on pivot posts
        add_fill(fills, f"{label} striker", (cx - 8, iy + 3, cz - 6), (cx - 3, iy + 4, cz - 5), M.LOG)
        add_fill(fills, f"{label} striker post a", (cx - 9, iy, cz - 6), (cx - 8, iy + 4, cz - 5), M.LOG)
        add_fill(fills, f"{label} striker post b", (cx - 3, iy, cz - 6), (cx - 2, iy + 4, cz - 5), M.LOG)
    else:
        # Twelve red drums on stands around the floor + one great drum
        for i in range(12):
            ang = i * math.pi / 6
            dx, dz = int(6 * math.cos(ang)), int(6 * math.sin(ang))
            add_fill(fills, f"{label} drum stand {i}", (cx + dx - 1, iy, cz + dz - 1), (cx + dx + 1, iy + 1, cz + dz + 1), M.LOG)
            add_fill(fills, f"{label} drum {i}", (cx + dx - 1, iy + 2, cz + dz - 1), (cx + dx + 1, iy + 3, cz + dz + 1), M.RED_WALL_ALT)
        add_fill(fills, f"{label} great drum stand", (cx - 2, iy, cz - 2), (cx + 2, iy + 1, cz + 2), M.DARK)
        add_fill(fills, f"{label} great drum", (cx - 2, iy + 2, cz - 2), (cx + 2, iy + 5, cz + 2), M.RED_WALL_ALT)
        add_fill(fills, f"{label} great drum head", (cx - 2, iy + 6, cz - 2), (cx + 2, iy + 6, cz + 2), M.WHITE_WOOL)


def build_bell_drum_3d(fills: list[Fill]) -> None:
    for kind, cx, cz in TOWERS:
        _tower(fills, kind, cx, cz)


def main() -> None:
    run_builder(build_bell_drum_3d, "bell_drum_3d")


if __name__ == "__main__":
    main()
