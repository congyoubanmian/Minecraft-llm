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
    add_outline,
    add_pagoda_eave,
    add_pagoda_openings,
    add_pool,
    add_ridge_roof,
    add_tree,
    run_builder,
)


"""
Giant Wild Goose Pagoda (大雁塔) - seven-storey square pagoda in Da Ci'en Temple.

Location in Chang'an city local coordinates:
    center: (4580, 3860)

Features:
    - Square brick body that tapers upward
    - Overhanging eaves on each storey
    - Golden spire
    - Surrounding temple walls, gate, and courtyard
    - Lotus pond and trees
"""

CX = 4580
CZ = 3860


def build_giant_pagoda(fills: list[Fill]) -> None:
    add_fill(fills, "pagoda clear old tower", (CX - 60, 1, CZ - 60), (CX + 60, 115, CZ + 60), M.AIR)
    y = 1
    base_radius = 44
    tier_height = 10
    tiers = 7

    for tier in range(tiers):
        r = base_radius - tier * 4
        # Square hollow brick body
        add_hollow_box(fills, f"pagoda body t{tier}", CX - r, y, CZ - r, CX + r, y + tier_height, CZ + r, M.WHITE_TERRACOTTA, thickness=2)
        # Wooden floor visible from outside at each level
        add_outline(fills, f"pagoda floor t{tier}", CX - r + 2, CZ - r + 2, CX + r - 2, CZ + r - 2, y + tier_height - 1, y + tier_height - 1, M.WOOD, thickness=1)
        add_pagoda_openings(fills, f"pagoda t{tier}", CX, CZ, r, y, tier_height)
        add_pagoda_eave(fills, f"pagoda eave t{tier}", CX, CZ, r, y + tier_height, overhang=5)
        y += tier_height + 2

    # Central spire
    add_fill(fills, "pagoda spire", (CX - 2, y, CZ - 2), (CX + 2, y + 22, CZ + 2), M.GOLD)

    # Temple courtyard wall
    wall_min_x, wall_min_z = CX - 100, CZ - 100
    wall_max_x, wall_max_z = CX + 100, CZ + 100
    add_outline(fills, "pagoda temple wall", wall_min_x, wall_min_z, wall_max_x, wall_max_z, 1, 8, M.RED_WALL, thickness=2)

    # Temple gate on south side
    add_fill(fills, "pagoda temple gate", (CX - 16, 1, wall_min_z - 4), (CX + 16, 16, wall_min_z + 4), M.RED_WALL)
    add_ridge_roof(fills, "pagoda temple gate roof", CX - 20, wall_min_z - 6, CX + 20, wall_min_z + 6, 17, layers=2, ridge_axis="z")

    # Bell and drum towers flanking the gate
    add_hollow_box(fills, "pagoda bell tower", CX - 40, 1, wall_min_z - 12, CX - 24, 18, wall_min_z + 4, M.STONE, thickness=1)
    add_hollow_box(fills, "pagoda drum tower", CX + 24, 1, wall_min_z - 12, CX + 40, 18, wall_min_z + 4, M.STONE, thickness=1)
    add_ridge_roof(fills, "pagoda bell roof", CX - 42, wall_min_z - 14, CX - 22, wall_min_z + 6, 19, layers=2, ridge_axis="z")
    add_ridge_roof(fills, "pagoda drum roof", CX + 22, wall_min_z - 14, CX + 42, wall_min_z + 6, 19, layers=2, ridge_axis="z")

    # Lotus pond in front courtyard
    add_pool(fills, "pagoda lotus pond", CX - 30, wall_min_z + 30, CX + 30, wall_min_z + 70, 2)

    # Trees in courtyard
    for tx, tz in [(-70, -70), (70, -70), (-70, 70), (70, 70), (-50, 0), (50, 0), (0, -50)]:
        add_tree(fills, f"pagoda tree {tx},{tz}", CX + tx, CZ + tz, 2)

    # Incense burner
    add_fill(fills, "pagoda incense burner", (CX - 4, 2, wall_min_z + 20), (CX + 4, 8, wall_min_z + 28), M.GOLD)


def main() -> None:
    run_builder(build_giant_pagoda, "pagoda_giant")


if __name__ == "__main__":
    main()
