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
Small Wild Goose Pagoda (小雁塔) - multi-eave brick pagoda in Jianfu Temple.

Location: local (1320, 3700)
"""

CX = 1320
CZ = 3700


def build_small_pagoda(fills: list[Fill]) -> None:
    add_fill(fills, "small pagoda clear old tower", (CX - 45, 1, CZ - 45), (CX + 45, 110, CZ + 45), M.AIR)
    y = 1
    base_radius = 34
    tiers = 13  # dense eaves
    tier_height = 5

    for tier in range(tiers):
        r = max(8, base_radius - tier * 2)
        add_hollow_box(fills, f"small pagoda body t{tier}", CX - r, y, CZ - r, CX + r, y + tier_height, CZ + r, M.WHITE_TERRACOTTA, thickness=2)
        add_pagoda_openings(fills, f"small pagoda t{tier}", CX, CZ, r, y, tier_height)
        add_pagoda_eave(fills, f"small pagoda eave t{tier}", CX, CZ, r, y + tier_height)
        y += tier_height + 1

    # Spire
    add_fill(fills, "small pagoda spire", (CX - 1, y, CZ - 1), (CX + 1, y + 14, CZ + 1), M.GOLD)

    # Temple courtyard
    wall_min_x, wall_min_z = CX - 80, CZ - 80
    wall_max_x, wall_max_z = CX + 80, CZ + 80
    add_outline(fills, "small pagoda wall", wall_min_x, wall_min_z, wall_max_x, wall_max_z, 1, 7, M.RED_WALL, thickness=2)

    # Gate
    add_fill(fills, "small pagoda gate", (CX - 12, 1, wall_min_z - 3), (CX + 12, 12, wall_min_z + 3), M.RED_WALL)
    add_ridge_roof(fills, "small pagoda gate roof", CX - 16, wall_min_z - 5, CX + 16, wall_min_z + 5, 13, layers=2, ridge_axis="z")

    # Pond
    add_pool(fills, "small pagoda pond", CX - 20, wall_min_z + 30, CX + 20, wall_min_z + 60, 2)

    # Trees
    for tx, tz in [(-50, -50), (50, -50), (-50, 50), (50, 50)]:
        add_tree(fills, f"small pagoda tree {tx},{tz}", CX + tx, CZ + tz, 2)


def main() -> None:
    run_builder(build_small_pagoda, "pagoda_small")


if __name__ == "__main__":
    main()
