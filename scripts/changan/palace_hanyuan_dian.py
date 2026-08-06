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
    add_lantern_line,
    add_platform_with_steps,
    add_ridge_roof,
    add_stair_run,
    run_builder,
)


"""
Hanyuan Dian (含元殿) - the outer-court main hall of Daming Palace.

Location in Chang'an city local coordinates:
    x: 2660 .. 3340
    z: 5180 .. 5480

Features:
    - Triple stone terrace (longwei dao 龙尾道)
    - Red-wall hall body with column grid
    - Double-eave hip roof with golden ridge and corner ornaments
    - East/west que towers (Xiangluan & Qifeng)
    - Front plaza lamps and red carpet axis
"""

# Hall footprint
X1, Z1 = 2660, 5180
X2, Z2 = 3340, 5480
PLATFORM_Y = 1


def build_hanyuan_dian(fills: list[Fill]) -> None:
    # Triple terrace: lowest andesite, middle smooth stone, top andesite
    add_platform_with_steps(
        fills, "hanyuan terrace",
        X1 - 60, Z1 - 60, X2 + 60, Z2 + 60,
        PLATFORM_Y,
        [
            (3, 0, M.ANDESITE),
            (3, 8, M.SMOOTH),
            (2, 16, M.ANDESITE),
        ],
    )
    terrace_top = PLATFORM_Y + 3 + 3 + 2  # = 9

    # Main hall body (hollow red wall box)
    hall_height = 48
    add_hollow_box(
        fills, "hanyuan body",
        X1, terrace_top, Z1,
        X2, terrace_top + hall_height, Z2,
        M.RED_WALL, thickness=2,
    )

    # Timber column grid on the exterior (read as red painted columns)
    add_column_grid(
        fills, "hanyuan columns",
        X1, Z1, X2, Z2,
        terrace_top, terrace_top + hall_height - 2,
        spacing=30,
        column_block=M.RED_WALL_ALT,
        column_size=2,
    )

    # Central main entrance void on south facade
    mid_x = (X1 + X2) // 2
    add_fill(fills, "hanyuan main door", (mid_x - 16, terrace_top + 1, Z1 - 3), (mid_x + 16, terrace_top + 14, Z1 + 2), M.AIR)
    add_fill(fills, "hanyuan door frame", (mid_x - 18, terrace_top + 1, Z1 - 5), (mid_x + 18, terrace_top + 16, Z1 - 2), M.GOLD)

    # Side windows on east/west walls
    for wx in range(X1 + 40, X2 - 30, 44):
        add_fill(fills, f"hanyuan window w{wx}", (wx, terrace_top + 10, Z1 - 2), (wx + 10, terrace_top + 22, Z1 + 1), M.AIR)
        add_fill(fills, f"hanyuan window frame w{wx}", (wx - 1, terrace_top + 9, Z1 - 3), (wx + 11, terrace_top + 23, Z1 - 2), M.LOG)

    # Dougong bracket layer under the main eaves
    dougong_y = terrace_top + hall_height + 1
    add_dougong_brackets(fills, "hanyuan dougong", X1 - 8, Z1 - 8, X2 + 8, Z2 + 8, dougong_y, spacing=30)

    # Lower eave ring
    add_fill(fills, "hanyuan lower eave", (X1 - 28, dougong_y + 1, Z1 - 28), (X2 + 28, dougong_y + 2, Z2 + 28), M.ROOF_GREEN)

    # Main double-eave roof
    add_ridge_roof(
        fills, "hanyuan roof",
        X1 - 36, Z1 - 36, X2 + 36, Z2 + 36,
        dougong_y + 3,
        layers=6,
        ridge_axis="z",
        roof_block=M.ROOF_GREEN,
        ridge_block=M.GOLD,
    )

    # Corner ornaments (chiwen)
    for cx, cz in [(X1 - 36, Z1 - 36), (X2 + 36, Z1 - 36), (X1 - 36, Z2 + 36), (X2 + 36, Z2 + 36)]:
        add_fill(fills, f"hanyuan corner {cx},{cz}", (cx - 2, dougong_y + 12, cz - 2), (cx + 2, dougong_y + 16, cz + 2), M.GOLD)

    # East and West Que towers (Xiangluan & Qifeng)
    for side, qx in [("xiangluan", X1 - 120), ("qifeng", X2 + 120)]:
        add_hollow_box(fills, f"hanyuan {side} que", qx - 28, terrace_top, Z1 + 80, qx + 28, terrace_top + 42, Z2 - 80, M.RED_WALL, thickness=2)
        add_ridge_roof(fills, f"hanyuan {side} que roof", qx - 34, Z1 + 74, qx + 34, Z2 - 74, terrace_top + 43, layers=4, ridge_axis="z")
        # Connecting corridor to main hall
        add_fill(fills, f"hanyuan {side} corridor", (min(qx, X1 if side == 'xiangluan' else X2), terrace_top + 4, (Z1 + Z2) // 2 - 6), (max(qx, X1 if side == 'xiangluan' else X2), terrace_top + 7, (Z1 + Z2) // 2 + 6), M.RED_WALL)

    # Dragon-tail stairs (Longwei Dao) on south side
    add_stair_run(fills, "hanyuan east stairs", mid_x + 60, Z1 - 40, mid_x + 120, Z1 - 10, terrace_top, 8, "south", block=M.SMOOTH)
    add_stair_run(fills, "hanyuan west stairs", mid_x - 120, Z1 - 40, mid_x - 60, Z1 - 10, terrace_top, 8, "south", block=M.SMOOTH)
    add_stair_run(fills, "hanyuan central stairs", mid_x - 40, Z1 - 50, mid_x + 40, Z1 - 20, terrace_top, 10, "south", block=M.ANDESITE)

    # Front plaza lamps and red carpet
    add_fill(fills, "hanyuan carpet", (mid_x - 18, 2, Z1 - 120), (mid_x + 18, 2, Z1), M.RED_WOOL)
    add_lantern_line(fills, "hanyuan west lamps", mid_x - 40, Z1 - 120, mid_x - 40, Z1, 3, 30)
    add_lantern_line(fills, "hanyuan east lamps", mid_x + 40, Z1 - 120, mid_x + 40, Z1, 3, 30)


def main() -> None:
    run_builder(build_hanyuan_dian, "palace_hanyuan_dian")


if __name__ == "__main__":
    main()
