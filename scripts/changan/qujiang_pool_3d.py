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
    add_fill,
    add_pool,
    add_ridge_roof,
    add_staircase,
    add_tree,
    run_builder,
)


"""
Qujiang Pool (曲江池) 3D enhancement pass.

A multi-level water garden south-east of the city with:
- Terraced pools with artificial waterfalls
- A central island with a painted pleasure boat
- Overhanging waterfront pavilions
- A curved stone bridge across the lake
- Underwater stone steps and lakeside boardwalks

Local coordinates:
    x: 5000 .. 6000
    z: 5200 .. 6000
"""

X1, Z1 = 5000, 5200
X2, Z2 = 6000, 6000
CX, CZ = (X1 + X2) // 2, (Z1 + Z2) // 2
WATER_Y = 1


def build_qujiang_pool_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Main lake basin with terraced northern inlet
    # ------------------------------------------------------------------
    add_pool(fills, "qujiang main pool", X1 + 60, Z1 + 120, X2 - 60, Z2 - 80, WATER_Y, depth=2)

    # Terraced northern pools feeding the main lake
    for tier in range(3):
        tz1 = Z1 + 20 + tier * 35
        tz2 = tz1 + 30
        ty = WATER_Y + (3 - tier)  # higher tiers are upstream
        add_pool(fills, f"qujiang terrace {tier}", CX - 80, tz1, CX + 80, tz2, ty, depth=2, floor_block=M.SMOOTH)
        # Waterfall step between tiers
        if tier < 2:
            add_fill(fills, f"qujiang fall {tier}", (CX - 6, ty - 1, tz2), (CX + 6, ty - 1, tz2 + 6), M.WATER)

    # ------------------------------------------------------------------
    # 2. Central island with painted pleasure boat (huafang 画舫)
    # ------------------------------------------------------------------
    island_x1, island_z1 = CX - 80, CZ - 60
    island_x2, island_z2 = CX + 80, CZ + 60
    add_fill(fills, "qujiang island base", (island_x1, WATER_Y - 1, island_z1), (island_x2, WATER_Y, island_z2), M.GRASS)
    # Island trees
    for tx, tz in [(island_x1 + 20, island_z1 + 20), (island_x2 - 20, island_z1 + 20), (island_x1 + 20, island_z2 - 20), (island_x2 - 20, island_z2 - 20)]:
        add_tree(fills, f"qujiang island tree {tx},{tz}", tx, tz, WATER_Y + 1)

    # Pleasure boat on the island lake (moored)
    boat_x1, boat_z1 = island_x1 + 30, island_z1 + 15
    boat_x2, boat_z2 = island_x1 + 70, island_z1 + 35
    add_fill(fills, "qujiang boat hull", (boat_x1, WATER_Y, boat_z1), (boat_x2, WATER_Y + 2, boat_z2), M.WOOD)
    add_fill(fills, "qujiang boat cabin", (boat_x1 + 10, WATER_Y + 3, boat_z1 + 5), (boat_x2 - 10, WATER_Y + 8, boat_z2 - 5), M.RED_WALL)
    add_ridge_roof(fills, "qujiang boat roof", boat_x1 + 5, boat_z1, boat_x2 - 5, boat_z2, WATER_Y + 9, layers=2, ridge_axis="x")

    # ------------------------------------------------------------------
    # 3. Overhanging waterfront pavilions (shui xie 水榭)
    # ------------------------------------------------------------------
    pavilions = [
        (X1 + 120, Z1 + 180, "west"),
        (X2 - 120, Z1 + 180, "east"),
        (X1 + 200, Z2 - 120, "southwest"),
        (X2 - 200, Z2 - 120, "southeast"),
    ]
    for px, pz, name in pavilions:
        # Support pillars into the water
        add_fill(fills, f"qujiang {name} pillar", (px - 12, WATER_Y - 2, pz - 12), (px - 12, WATER_Y + 6, pz - 12), M.LOG)
        add_fill(fills, f"qujiang {name} pillar 2", (px + 12, WATER_Y - 2, pz - 12), (px + 12, WATER_Y + 6, pz - 12), M.LOG)
        add_fill(fills, f"qujiang {name} pillar 3", (px - 12, WATER_Y - 2, pz + 12), (px - 12, WATER_Y + 6, pz + 12), M.LOG)
        add_fill(fills, f"qujiang {name} pillar 4", (px + 12, WATER_Y - 2, pz + 12), (px + 12, WATER_Y + 6, pz + 12), M.LOG)
        # Cantilevered deck over the water
        add_cantilevered_floor(fills, f"qujiang {name} deck", px - 10, pz - 10, px + 10, pz + 10, WATER_Y + 7, overhang=4, block=M.WOOD)
        # Pavilion body
        add_fill(fills, f"qujiang {name} body", (px - 8, WATER_Y + 8, pz - 8), (px + 8, WATER_Y + 16, pz + 8), M.RED_WALL)
        add_ridge_roof(fills, f"qujiang {name} roof", px - 12, pz - 12, px + 12, pz + 12, WATER_Y + 17, layers=2, ridge_axis="z")
        # Connecting boardwalk to shore
        add_fill(fills, f"qujiang {name} walkway", (px - 4, WATER_Y + 7, pz - 30), (px + 4, WATER_Y + 7, pz - 10), M.WOOD)

    # ------------------------------------------------------------------
    # 4. Curved stone bridge across the lake
    # ------------------------------------------------------------------
    bridge_x = CX + 20
    add_arch_bridge(
        fills, "qujiang curved bridge",
        bridge_x, Z1 + 140,
        bridge_x, Z2 - 140,
        WATER_Y + 4,
        span=40,
        height=3,
        block=M.STONE,
    )

    # Bridge pavilion at the midpoint
    add_fill(fills, "qujiang bridge pavilion base", (bridge_x - 8, WATER_Y + 5, CZ - 8), (bridge_x + 8, WATER_Y + 5, CZ + 8), M.WOOD)
    add_fill(fills, "qujiang bridge pavilion body", (bridge_x - 6, WATER_Y + 6, CZ - 6), (bridge_x + 6, WATER_Y + 12, CZ + 6), M.RED_WALL)
    add_ridge_roof(fills, "qujiang bridge pavilion roof", bridge_x - 10, CZ - 10, bridge_x + 10, CZ + 10, WATER_Y + 13, layers=2, ridge_axis="z")

    # ------------------------------------------------------------------
    # 5. Underwater stone steps and lakeside boardwalks
    # ------------------------------------------------------------------
    # Underwater steps at the south shore
    add_staircase(
        fills, "qujiang underwater steps",
        CX - 20, Z2 - 20,
        CX + 20, Z2 - 10,
        WATER_Y - 2, WATER_Y + 2,
        "north",
        block=M.STONE,
    )

    # Lakeside boardwalk along the west shore
    for z in range(Z1 + 150, Z2 - 150, 60):
        add_cantilevered_floor(fills, f"qujiang west boardwalk {z}", X1 + 40, z - 10, X1 + 60, z + 10, WATER_Y + 2, overhang=2, block=M.WOOD)

    # East shore boardwalk
    for z in range(Z1 + 150, Z2 - 150, 60):
        add_cantilevered_floor(fills, f"qujiang east boardwalk {z}", X2 - 60, z - 10, X2 - 40, z + 10, WATER_Y + 2, overhang=2, block=M.WOOD)

    # ------------------------------------------------------------------
    # 6. Shore trees and lamps
    # ------------------------------------------------------------------
    for tx in range(X1 + 100, X2 - 90, 80):
        add_tree(fills, f"qujiang shore tree n {tx}", tx, Z1 + 100, 2)
        add_tree(fills, f"qujiang shore tree s {tx}", tx, Z2 - 40, 2)


def main() -> None:
    run_builder(build_qujiang_pool_3d, "qujiang_pool_3d")


if __name__ == "__main__":
    main()
