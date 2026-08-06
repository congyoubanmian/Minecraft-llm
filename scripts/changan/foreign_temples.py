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
    add_ridge_roof,
    add_tree,
    run_builder,
)


"""
Foreign religious temples in the international district near West Market:
- Persian Temple (波斯寺, Zoroastrian fire temple)
- Zoroastrian Shrine (祆祠)
- Nestorian Church (景教寺, Da Qin Monastery)
"""


def build_persian_temple(fills: list[Fill]) -> None:
    """Persian Zoroastrian fire temple near West Market."""
    x1, z1, x2, z2 = 500, 2000, 900, 2400
    cx, cz = (x1 + x2) // 2, (z1 + z2) // 2

    add_outline(fills, "persian wall", x1, z1, x2, z2, 1, 7, M.STONE, thickness=2)

    # Main fire hall (square, domed-ish)
    add_hollow_box(fills, "persian fire hall", cx - 30, 1, cz - 30, cx + 30, 22, cz + 30, M.STONE, thickness=2)
    # Flat-topped roof with central fire altar
    add_fill(fills, "persian roof", (cx - 32, 23, cz - 32), (cx + 32, 24, cz + 32), M.ANDESITE)
    add_fill(fills, "persian fire altar", (cx - 5, 25, cz - 5), (cx + 5, 32, cz + 5), M.GOLD)
    # Flames around altar
    add_fill(fills, "persian flame", (cx - 2, 33, cz - 2), (cx + 2, 36, cz + 2), M.RED_WOOL)

    # Four corner towers
    for dx, dz in [(-25, -25), (25, -25), (-25, 25), (25, 25)]:
        add_fill(fills, f"persian tower {dx},{dz}", (cx + dx - 4, 1, cz + dz - 4), (cx + dx + 4, 18, cz + dz + 4), M.STONE)


def build_zoroastrian_shrine(fills: list[Fill]) -> None:
    """Zoroastrian shrine with an open-air fire platform."""
    x1, z1, x2, z2 = 1000, 2000, 1300, 2300
    cx, cz = (x1 + x2) // 2, (z1 + z2) // 2

    add_outline(fills, "zoroastrian wall", x1, z1, x2, z2, 1, 5, M.STONE, thickness=2)

    # Central fire platform
    add_fill(fills, "zoroastrian platform", (cx - 12, 1, cz - 12), (cx + 12, 4, cz + 12), M.ANDESITE)
    add_fill(fills, "zoroastrian fire", (cx - 3, 5, cz - 3), (cx + 3, 12, cz + 3), M.RED_WOOL)

    # Covered ambulatory
    add_hollow_box(fills, "zoroastrian hall", cx - 25, 1, cz - 40, cx + 25, 12, cz - 15, M.STONE, thickness=1)
    add_ridge_roof(fills, "zoroastrian roof", cx - 30, cz - 45, cx + 30, cz - 10, 13, layers=2, ridge_axis="z")


def build_nestorian_church(fills: list[Fill]) -> None:
    """Nestorian Da Qin Monastery with a cross-topped hall."""
    x1, z1, x2, z2 = 1400, 2000, 1800, 2400
    cx, cz = (x1 + x2) // 2, (z1 + z2) // 2

    add_outline(fills, "nestorian wall", x1, z1, x2, z2, 1, 6, M.WHITE, thickness=2)

    # Main church hall
    add_hollow_box(fills, "nestorian church", cx - 40, 1, cz - 30, cx + 40, 18, cz + 30, M.WHITE, thickness=1)
    add_ridge_roof(fills, "nestorian roof", cx - 46, cz - 36, cx + 46, cz + 36, 19, layers=2, ridge_axis="z")

    # Cross on roof
    add_fill(fills, "nestorian cross v", (cx - 2, 23, cz - 12), (cx + 2, 35, cz + 12), M.GOLD)
    add_fill(fills, "nestorian cross h", (cx - 8, 28, cz - 2), (cx + 8, 32, cz + 2), M.GOLD)

    # Bell tower
    add_fill(fills, "nestorian tower", (cx - 8, 1, z1 - 8), (cx + 8, 22, z1 + 8), M.WHITE)
    add_fill(fills, "nestorian tower top", (cx - 6, 23, z1 - 6), (cx + 6, 26, z1 + 6), M.GOLD)


def build_foreign_temples(fills: list[Fill]) -> None:
    build_persian_temple(fills)
    build_zoroastrian_shrine(fills)
    build_nestorian_church(fills)


def main() -> None:
    run_builder(build_foreign_temples, "foreign_temples")


if __name__ == "__main__":
    main()
