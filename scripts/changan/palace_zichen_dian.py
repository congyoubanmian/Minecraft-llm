from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    Fill,
    Materials as M,
    add_column_grid,
    add_fill,
    add_hollow_box,
    add_platform_with_steps,
    add_pool,
    add_ridge_roof,
    add_tree,
    run_builder,
)


"""
Zichen Dian (紫宸殿) - the inner-court hall of Daming Palace.

Location: local (2360, 5200) .. (2620, 5480)
Intimate scale, surrounded by a small garden and pond.
"""

X1, Z1 = 2360, 5200
X2, Z2 = 2620, 5480
PLATFORM_Y = 1


def build_zichen_dian(fills: list[Fill]) -> None:
    # Low white-stone terrace
    add_platform_with_steps(fills, "zichen terrace", X1 - 20, Z1 - 20, X2 + 20, Z2 + 20, PLATFORM_Y, [(3, 0, M.WHITE), (2, 6, M.ANDESITE)])
    terrace_top = PLATFORM_Y + 3 + 2  # = 6

    hall_height = 28
    add_hollow_box(fills, "zichen body", X1, terrace_top, Z1, X2, terrace_top + hall_height, Z2, M.RED_WALL, thickness=2)
    add_column_grid(fills, "zichen columns", X1, Z1, X2, Z2, terrace_top, terrace_top + hall_height - 2, spacing=22, column_block=M.RED_WALL_ALT, column_size=2)

    # Roof
    add_ridge_roof(fills, "zichen roof", X1 - 18, Z1 - 18, X2 + 18, Z2 + 18, terrace_top + hall_height + 1, layers=4, ridge_axis="z", roof_block=M.ROOF_BLUE)

    # Garden pond on north side
    add_pool(fills, "zichen pond", X1 - 30, Z2 + 20, X2 + 30, Z2 + 70, 2)

    # Garden trees
    for tx, tz in [(-40, 40), (40, 40), (-40, 90), (40, 90), (0, 60)]:
        add_tree(fills, f"zichen tree {tx},{tz}", (X1 + X2) // 2 + tx, Z2 + tz, 2)

    # Side pavilions
    for side, sx in [("west", X1 - 60), ("east", X2 + 60)]:
        add_hollow_box(fills, f"zichen {side} pavilion", sx - 20, terrace_top, Z1 + 60, sx + 20, terrace_top + 16, Z2 - 60, M.WOOD, thickness=1)
        add_ridge_roof(fills, f"zichen {side} pavilion roof", sx - 24, Z1 + 56, sx + 24, Z2 - 56, terrace_top + 17, layers=2, ridge_axis="z")


def main() -> None:
    run_builder(build_zichen_dian, "palace_zichen_dian")


if __name__ == "__main__":
    main()
