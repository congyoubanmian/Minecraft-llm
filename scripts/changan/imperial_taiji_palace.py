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
    add_outline,
    add_platform_with_steps,
    add_ridge_roof,
    run_builder,
)


"""
Taiji Palace (太极宫) - the primary palace of early Tang, located at the north center.

Location: local (2400, 4800) .. (3600, 5800)
Main halls: Chengtian Gate, Taiji Hall, Liangyi Hall.
"""

X1, Z1 = 2400, 4800
X2, Z2 = 3600, 5800


def build_taiji_palace(fills: list[Fill]) -> None:
    # Outer palace wall
    add_outline(fills, "taiji wall", X1 - 80, Z1 - 80, X2 + 80, Z2 + 80, 1, 18, M.RED_WALL, thickness=3)

    # Chengtian Gate (south)
    mid_x = (X1 + X2) // 2
    add_fill(fills, "taiji chengtian gate", (mid_x - 20, 1, Z1 - 85), (mid_x + 20, 20, Z1 - 75), M.RED_WALL)
    add_ridge_roof(fills, "taiji chengtian roof", mid_x - 26, Z1 - 90, mid_x + 26, Z1 - 70, 21, layers=3, ridge_axis="z")

    # Taiji Hall (main hall)
    tx, tz = mid_x, (Z1 + Z2) // 2 - 200
    hall_w, hall_d = 160, 100
    add_platform_with_steps(fills, "taiji hall terrace", tx - hall_w // 2 - 30, tz - hall_d // 2 - 30, tx + hall_w // 2 + 30, tz + hall_d // 2 + 30, 1, [(3, 0, M.ANDESITE), (3, 8, M.SMOOTH)])
    terrace_top = 7
    add_hollow_box(fills, "taiji hall body", tx - hall_w // 2, terrace_top, tz - hall_d // 2, tx + hall_w // 2, terrace_top + 38, tz + hall_d // 2, M.RED_WALL, thickness=2)
    add_column_grid(fills, "taiji hall columns", tx - hall_w // 2, tz - hall_d // 2, tx + hall_w // 2, tz + hall_d // 2, terrace_top, terrace_top + 36, spacing=26, column_block=M.RED_WALL_ALT, column_size=2)
    add_ridge_roof(fills, "taiji hall roof", tx - hall_w // 2 - 20, tz - hall_d // 2 - 20, tx + hall_w // 2 + 20, tz + hall_d // 2 + 20, terrace_top + 39, layers=5, ridge_axis="z")

    # Liangyi Hall (inner hall)
    lx, lz = mid_x, (Z1 + Z2) // 2 + 100
    add_platform_with_steps(fills, "taiji liangyi terrace", lx - 70, lz - 50, lx + 70, lz + 50, 1, [(3, 0, M.ANDESITE), (2, 8, M.SMOOTH)])
    add_hollow_box(fills, "taiji liangyi body", lx - 60, 6, lz - 40, lx + 60, 6 + 28, lz + 40, M.RED_WALL, thickness=2)
    add_ridge_roof(fills, "taiji liangyi roof", lx - 68, lz - 48, lx + 68, lz + 48, 35, layers=4, ridge_axis="z")

    # Side government offices
    for side, sx in [("west", X1 - 60), ("east", X2 + 60)]:
        add_hollow_box(fills, f"taiji {side} office", sx - 40, 1, Z1 + 100, sx + 40, 22, Z2 - 100, M.WHITE, thickness=1)
        add_ridge_roof(fills, f"taiji {side} office roof", sx - 46, Z1 + 94, sx + 46, Z2 - 94, 23, layers=2, ridge_axis="z")


def main() -> None:
    run_builder(build_taiji_palace, "imperial_taiji_palace")


if __name__ == "__main__":
    main()
