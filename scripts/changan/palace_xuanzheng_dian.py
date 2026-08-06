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
    add_dougong_brackets,
    add_fill,
    add_hollow_box,
    add_platform_with_steps,
    add_ridge_roof,
    add_stair_run,
    run_builder,
)


"""
Xuanzheng Dian (宣政殿) - the middle-court hall of Daming Palace.

Location: local (2740, 4880) .. (3260, 5080)
Smaller than Hanyuan Dian, with a single-eave roof and side halls.
"""

X1, Z1 = 2740, 4880
X2, Z2 = 3260, 5080
PLATFORM_Y = 1


def build_xuanzheng_dian(fills: list[Fill]) -> None:
    # Single high stone terrace
    add_platform_with_steps(
        fills, "xuanzheng terrace",
        X1 - 30, Z1 - 30, X2 + 30, Z2 + 30,
        PLATFORM_Y,
        [(4, 0, M.ANDESITE), (3, 8, M.SMOOTH)],
    )
    terrace_top = PLATFORM_Y + 4 + 3  # = 8

    hall_height = 36
    add_hollow_box(fills, "xuanzheng body", X1, terrace_top, Z1, X2, terrace_top + hall_height, Z2, M.RED_WALL, thickness=2)

    add_column_grid(fills, "xuanzheng columns", X1, Z1, X2, Z2, terrace_top, terrace_top + hall_height - 2, spacing=26, column_block=M.RED_WALL_ALT, column_size=2)

    # South entrance
    mid_x = (X1 + X2) // 2
    add_fill(fills, "xuanzheng door", (mid_x - 12, terrace_top + 1, Z1 - 3), (mid_x + 12, terrace_top + 12, Z1 + 2), M.AIR)
    add_fill(fills, "xuanzheng door frame", (mid_x - 14, terrace_top + 1, Z1 - 5), (mid_x + 14, terrace_top + 14, Z1 - 2), M.GOLD)

    # Central stairs
    add_stair_run(fills, "xuanzheng stairs", mid_x - 30, Z1 - 30, mid_x + 30, Z1 - 10, terrace_top, 7, "south", block=M.ANDESITE)

    # Dougong and roof
    dougong_y = terrace_top + hall_height + 1
    add_dougong_brackets(fills, "xuanzheng dougong", X1 - 6, Z1 - 6, X2 + 6, Z2 + 6, dougong_y, spacing=26)
    add_ridge_roof(fills, "xuanzheng roof", X1 - 24, Z1 - 24, X2 + 24, Z2 + 24, dougong_y + 1, layers=5, ridge_axis="z")

    # Side halls (Zhongshu and Menxia provinces)
    for side, sx in [("west", X1 - 120), ("east", X2 + 120)]:
        add_hollow_box(fills, f"xuanzheng {side} hall", sx - 40, terrace_top, Z1 + 20, sx + 40, terrace_top + 24, Z2 - 20, M.WHITE, thickness=1)
        add_ridge_roof(fills, f"xuanzheng {side} roof", sx - 46, Z1 + 14, sx + 46, Z2 - 14, terrace_top + 25, layers=3, ridge_axis="z")


def main() -> None:
    run_builder(build_xuanzheng_dian, "palace_xuanzheng_dian")


if __name__ == "__main__":
    main()
