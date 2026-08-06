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
    add_lantern_line,
    add_ridge_roof,
    add_tree,
    run_builder,
)


"""
Street facilities across the 6000x6000 city:
- Lamp posts along all major avenues
- Ceremonial archways (fang) at intersections
- Trees along streets
"""


def build_street_facilities(fills: list[Fill]) -> None:
    # Zhuque Avenue central median and lamps
    add_fill(fills, "zhuque median", (2994, 3, 0), (3006, 3, 5999), M.ANDESITE)
    add_lantern_line(fills, "zhuque west lamps", 2960, 0, 2960, 5999, 3, 80)
    add_lantern_line(fills, "zhuque east lamps", 3040, 0, 3040, 5999, 3, 80)

    # North-south avenue lamps and trees
    avenue_xs = [900, 1800, 3000, 4200, 5100]
    for x in avenue_xs:
        add_lantern_line(fills, f"avenue x={x} lamps", x, 80, x, 5920, 3, 100)
        for z in range(100, 5900, 120):
            add_tree(fills, f"avenue x={x} tree {z}", x - 45, z, 2)
            add_tree(fills, f"avenue x={x} tree e {z}", x + 45, z, 2)

    # East-west avenue lamps and trees
    avenue_zs = [900, 1700, 2500, 3300, 4100, 5000]
    for z in avenue_zs:
        add_lantern_line(fills, f"avenue z={z} lamps", 80, z, 5920, z, 3, 100)
        for x in range(100, 5900, 120):
            add_tree(fills, f"avenue z={z} tree {x}", x, z - 45, 2)
            add_tree(fills, f"avenue z={z} tree s {x}", x, z + 45, 2)

    # Ceremonial archways at major intersections
    intersections = [
        (3000, 3000, "tianxia"),
        (1200, 3000, "anping"),
        (4800, 3000, "changning"),
        (3000, 1500, "mingde"),
        (3000, 4800, "danfeng"),
        (900, 900, "tonggui"),
        (5100, 5100, "zhaofu"),
    ]
    for idx, (ix, iz, name) in enumerate(intersections):
        for dx, dz in [(-18, -4), (18, -4), (-18, 4), (18, 4)]:
            add_fill(fills, f"arch {name} pillar {dx},{dz}", (ix + dx, 2, iz + dz), (ix + dx + 3, 22, iz + dz + 3), M.RED_WALL)
        add_fill(fills, f"arch {name} beam", (ix - 24, 22, iz - 6), (ix + 24, 26, iz + 6), M.WOOD)
        add_ridge_roof(fills, f"arch {name} roof", ix - 28, iz - 8, ix + 28, iz + 8, 27, layers=2, ridge_axis="z")
        add_fill(fills, f"arch {name} plaque", (ix - 8, 23, iz - 7), (ix + 8, 25, iz - 7), M.GOLD)


def main() -> None:
    run_builder(build_street_facilities, "street_facilities")


if __name__ == "__main__":
    main()
