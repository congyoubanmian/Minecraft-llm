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
    add_platform_with_steps,
    add_ridge_roof,
    add_tree,
    run_builder,
)


"""
Tai Miao (太庙) and She Ji Tan (社稷坛) - ritual complexes south of the palace.

Location:
    Tai Miao: local (800, 4200) .. (1400, 4700)  (south-east of palace)
    She Ji Tan: local (4600, 4200) .. (5200, 4700) (south-west of palace)
"""


def build_tai_miao(fills: list[Fill]) -> None:
    """Imperial ancestral temple."""
    x1, z1, x2, z2 = 800, 4200, 1400, 4700
    mid_x = (x1 + x2) // 2

    # Wall
    add_outline(fills, "taimiao wall", x1, z1, x2, z2, 1, 8, M.RED_WALL, thickness=2)

    # Three successive halls on axis
    halls = [
        ("taimiao qian_dian", mid_x, z1 + 120, 80, 50, 28),
        ("taimiao zhong_dian", mid_x, z1 + 260, 70, 45, 24),
        ("taimiao hou_dian", mid_x, z1 + 380, 60, 40, 20),
    ]
    for name, hx, hz, w, d, h in halls:
        add_platform_with_steps(fills, f"{name} terrace", hx - w // 2 - 12, hz - d // 2 - 12, hx + w // 2 + 12, hz + d // 2 + 12, 1, [(2, 0, M.ANDESITE)])
        add_hollow_box(fills, name, hx - w // 2, 3, hz - d // 2, hx + w // 2, 3 + h, hz + d // 2, M.RED_WALL, thickness=2)
        add_ridge_roof(fills, f"{name} roof", hx - w // 2 - 10, hz - d // 2 - 10, hx + w // 2 + 10, hz + d // 2 + 10, 3 + h + 1, layers=4, ridge_axis="z")

    # Sacred way
    add_fill(fills, "taimiao sacred way", (mid_x - 6, 2, z1 + 20), (mid_x + 6, 2, z2 - 20), M.SMOOTH)

    # Spirit tablets pavilion
    add_fill(fills, "taimiao tablet pavilion", (mid_x - 10, 3, z1 + 60), (mid_x + 10, 14, z1 + 80), M.GOLD)

    # Trees
    for tx, tz in [(x1 + 60, z1 + 60), (x2 - 60, z1 + 60), (x1 + 60, z2 - 60), (x2 - 60, z2 - 60)]:
        add_tree(fills, f"taimiao tree {tx},{tz}", tx, tz, 2, height=9, spread=3)


def build_sheji_tan(fills: list[Fill]) -> None:
    """Altar of Soil and Grain."""
    x1, z1, x2, z2 = 4600, 4200, 5200, 4700
    cx, cz = (x1 + x2) // 2, (z1 + z2) // 2

    # Wall
    add_outline(fills, "sheji wall", x1, z1, x2, z2, 1, 6, M.RED_WALL, thickness=2)

    # Three-tier earthen altar
    add_platform_with_steps(
        fills, "sheji altar",
        cx - 80, cz - 80, cx + 80, cz + 80,
        1,
        [
            (3, 0, M.DIRT),
            (3, 10, M.GRASS),
            (2, 20, M.GRASS),
        ],
    )

    # Five-coloured soil mounds on top (representing five elements)
    colours = [M.RED_WOOL, M.YELLOW_WOOL, M.BLUE_WOOL, M.WHITE_WOOL, M.BLACK_WOOL]
    for idx, (dx, dz) in enumerate([(0, 0), (-20, -20), (20, -20), (-20, 20), (20, 20)]):
        add_fill(fills, f"sheji soil {idx}", (cx + dx - 6, 10, cz + dz - 6), (cx + dx + 6, 13, cz + dz + 6), colours[idx])

    # Sacrificial hall on north side
    add_hollow_box(fills, "sheji hall", cx - 40, 1, z1 + 30, cx + 40, 18, z1 + 80, M.RED_WALL, thickness=2)
    add_ridge_roof(fills, "sheji hall roof", cx - 46, z1 + 24, cx + 46, z1 + 86, 19, layers=3, ridge_axis="z")

    # Trees
    for tx, tz in [(x1 + 60, z1 + 60), (x2 - 60, z1 + 60), (x1 + 60, z2 - 60), (x2 - 60, z2 - 60)]:
        add_tree(fills, f"sheji tree {tx},{tz}", tx, tz, 2, height=8, spread=3)


def build_ancestral_temple_altar(fills: list[Fill]) -> None:
    build_tai_miao(fills)
    build_sheji_tan(fills)


def main() -> None:
    run_builder(build_ancestral_temple_altar, "ancestral_temple_altar")


if __name__ == "__main__":
    main()
