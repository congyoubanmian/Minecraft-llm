from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    Fill,
    Materials as M,
    add_arch_bridge,
    add_cantilevered_floor,
    add_dougong_cluster,
    add_fill,
    add_hollow_box,
    add_outline,
    add_ridge_roof,
    add_spiral_stair,
    run_builder,
)


"""
Penglai Island 3D (太液池蓬莱仙岛) - the immortal-island pavilion complex
in the middle of Taiye Pool, Daming Palace.

The Tang emperors built islands named after the mythical isles (Penglai,
Fangzhang, Yingzhou) in palace lakes. This module builds all three:
a main island with a stacked three-storey pavilion, two attendant islets,
and an arched bridge linking them to the north shore.

Location in Chang'an city local coordinates:
    Taiye Pool: x 2780..3220, z 5500..5740 (imperial_daming_palace.py).
    Main island centre: (3000, 5620). Attendant islets: (2900, 5680),
    (3100, 5680).

3D features:
    - Scanline-disk island mounds rising out of the water in terraces
    - Three-storey Penglai pavilion, each floor smaller, with
      cantilevered viewing galleries and dougong tiers
    - Interior spiral stair climbing all three storeys
    - Multi-arch stone bridge from the north shore to the island
    - Two attendant islets with small square pavilions
    - Boat dock with mooring posts on the south side
"""

CX, CZ = 3000, 5620
ISLETS = [(2900, 5680), (3100, 5680)]


def _disk(fills: list[Fill], label: str, cx: int, cz: int, r: int, y1: int, y2: int, block: str, step: int = 2) -> None:
    for dz in range(-r, r + 1, step):
        half = int((r * r - dz * dz) ** 0.5)
        add_fill(fills, f"{label} row {dz}", (cx - half, y1, cz + dz), (cx + half, y2, cz + dz + step - 1), block)


def build_penglai_island_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Main island: three rising terraces.
    # ------------------------------------------------------------------
    _disk(fills, "penglai isle t1", CX, CZ, 52, 0, 2, M.STONE)
    _disk(fills, "penglai isle t2", CX, CZ, 40, 2, 5, M.MOSS_STONE)
    _disk(fills, "penglai isle t3", CX, CZ, 28, 5, 9, M.ANDESITE)
    # Grass caps and rock outcrops
    _disk(fills, "penglai grass", CX, CZ, 26, 9, 9, M.GRASS)
    for i, (dx, dz, h) in enumerate([(-18, -10, 4), (14, -16, 3), (-8, 18, 5), (18, 12, 3)]):
        add_fill(fills, f"penglai rock {i}", (CX + dx - 2, 9, CZ + dz - 2), (CX + dx + 2, 9 + h, CZ + dz + 2), M.COBBLE)

    # Shore ring of stone to resist the water
    for dz in range(-52, 53, 2):
        half = int((52 * 52 - dz * dz) ** 0.5)
        add_fill(fills, f"penglai shore w {dz}", (CX - half, 1, CZ + dz), (CX - half, 2, CZ + dz + 1), M.SMOOTH)
        add_fill(fills, f"penglai shore e {dz}", (CX + half, 1, CZ + dz), (CX + half, 2, CZ + dz + 1), M.SMOOTH)

    # ------------------------------------------------------------------
    # 2. Three-storey Penglai pavilion at the island centre.
    # ------------------------------------------------------------------
    storeys = [(16, 10, 20), (12, 21, 30), (8, 31, 39)]
    for t, (half, y1, y2) in enumerate(storeys):
        add_hollow_box(fills, f"penglai pavilion s{t}", CX - half, y1, CZ - half, CX + half, y2, CZ + half, M.RED_WALL, thickness=2)
        # Cantilevered gallery + balustrade around every floor
        add_cantilevered_floor(fills, f"penglai gallery s{t}", CX - half, CZ - half, CX + half, CZ + half, y=y2, overhang=3, block=M.WOOD)
        add_outline(fills, f"penglai rail s{t}", CX - half - 3, CZ - half - 3, CX + half + 3, CZ + half + 3, y2 + 1, y2 + 1, M.FENCE, thickness=1)
        # Dougong under each corner
        for sx in (-1, 1):
            for sz in (-1, 1):
                add_dougong_cluster(fills, f"penglai dougong s{t} {sx},{sz}", CX + sx * half, CZ + sz * half, y=y2, tiers=2)
    add_ridge_roof(fills, "penglai roof", CX - 11, CZ - 11, CX + 11, CZ + 11, 40, layers=4, ridge_axis="x")
    add_fill(fills, "penglai finial", (CX - 1, 44, CZ - 1), (CX + 1, 47, CZ + 1), M.GOLD)
    # Interior spiral stair
    add_spiral_stair(fills, "penglai stair", CX, CZ, radius=10, y1=11, y2=20, block=M.SMOOTH)
    add_spiral_stair(fills, "penglai stair 2", CX, CZ, radius=7, y1=21, y2=30, block=M.SMOOTH)
    add_spiral_stair(fills, "penglai stair 3", CX, CZ, radius=5, y1=31, y2=39, block=M.SMOOTH)

    # ------------------------------------------------------------------
    # 3. Multi-arch bridge from the north shore to the island.
    # ------------------------------------------------------------------
    add_arch_bridge(fills, "penglai bridge", CX, 5500, CX, 5580, y=3, span=10, height=3, block=M.STONE)

    # ------------------------------------------------------------------
    # 4. Attendant islets (Fangzhang, Yingzhou) with small pavilions.
    # ------------------------------------------------------------------
    for i, (ix, iz) in enumerate(ISLETS):
        _disk(fills, f"islet{i} mound", ix, iz, 20, 0, 3, M.MOSS_STONE)
        _disk(fills, f"islet{i} cap", ix, iz, 16, 3, 4, M.GRASS)
        add_hollow_box(fills, f"islet{i} pavilion", ix - 7, 5, iz - 7, ix + 7, 13, iz + 7, M.RED_WALL, thickness=1)
        add_cantilevered_floor(fills, f"islet{i} gallery", ix - 7, iz - 7, ix + 7, iz + 7, y=13, overhang=2, block=M.WOOD)
        add_ridge_roof(fills, f"islet{i} roof", ix - 9, iz - 9, ix + 9, iz + 9, 14, layers=2, ridge_axis="x")

    # ------------------------------------------------------------------
    # 5. Boat dock on the south side.
    # ------------------------------------------------------------------
    add_fill(fills, "penglai dock", (CX - 10, 2, CZ + 50), (CX + 10, 2, CZ + 58), M.WOOD)
    for i, dx in enumerate((-8, 0, 8)):
        add_fill(fills, f"penglai mooring {i}", (CX + dx, 3, CZ + 56), (CX + dx, 5, CZ + 56), M.LOG)
    add_fill(fills, "penglai dock lantern post", (CX - 10, 3, CZ + 52), (CX - 10, 8, CZ + 52), M.LOG)
    add_fill(fills, "penglai dock lantern", (CX - 10, 9, CZ + 52), (CX - 10, 9, CZ + 52), M.LANTERN)


def main() -> None:
    run_builder(build_penglai_island_3d, "penglai_island_3d")


if __name__ == "__main__":
    main()
