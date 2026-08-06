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
    add_ridge_roof,
    add_tree,
    run_builder,
)


"""
Temple ritual details: incense burners, prayer banners, stone steles,
sacred trees, and flagpoles at the major Buddhist and Daoist temples.
"""


TEMPLES = [
    # (name, x1, z1, x2, z2, type)  type: buddhist or daoist
    ("daci", 4300, 3600, 4900, 4200, "buddhist"),
    ("jianfu", 1100, 3500, 1550, 3950, "buddhist"),
    ("qinglong", 4800, 800, 5300, 1300, "buddhist"),
    ("daxingshan", 1200, 2200, 1700, 2700, "buddhist"),
    ("dayan", 900, 3500, 1400, 4000, "buddhist"),
    ("xuandu", 4600, 3500, 5100, 4000, "daoist"),
]


def add_incense_burner(fills: list[Fill], x: int, z: int) -> None:
    """Stone incense burner with iron grate top."""
    add_fill(fills, f"incense {x},{z} base", (x - 2, 2, z - 2), (x + 2, 4, z + 2), M.STONE)
    add_fill(fills, f"incense {x},{z} grate", (x - 1, 5, z - 1), (x + 1, 5, z + 1), M.IRON_BARS)


def add_prayer_banner(fills: list[Fill], x: int, z: int, color: str) -> None:
    """Tall wooden pole with hanging colored prayer banner."""
    add_fill(fills, f"banner {x},{z} pole", (x - 1, 2, z - 1), (x + 1, 14, z + 1), M.LOG)
    add_fill(fills, f"banner {x},{z} flag", (x - 1, 10, z - 3), (x + 1, 13, z + 3), color)


def add_stone_stele(fills: list[Fill], x: int, z: int, name: str) -> None:
    """A rectangular stone stele on a turtle base (bixi)."""
    # Turtle base
    add_fill(fills, f"{name} stele {x},{z} base", (x - 3, 2, z - 2), (x + 3, 3, z + 2), M.ANDESITE)
    # Stele body
    add_fill(fills, f"{name} stele {x},{z} body", (x - 2, 4, z - 1), (x + 2, 12, z + 1), M.QUARTZ)
    # Cap
    add_fill(fills, f"{name} stele {x},{z} cap", (x - 3, 13, z - 2), (x + 3, 14, z + 2), M.DARK)


def add_flagpole_line(fills: list[Fill], x1: int, z1: int, x2: int, z2: int, every: int) -> None:
    """Row of small flagpoles along a courtyard path."""
    if x1 == x2:
        for z in range(min(z1, z2), max(z1, z2) + 1, every):
            add_fill(fills, f"flagpole {x1},{z}", (x1 - 1, 2, z - 1), (x1 + 1, 8, z + 1), M.LOG)
            add_fill(fills, f"flagpole {x1},{z} cloth", (x1 - 1, 6, z - 1), (x1 + 1, 8, z + 1), M.YELLOW_WOOL)
    else:
        for x in range(min(x1, x2), max(x1, x2) + 1, every):
            add_fill(fills, f"flagpole {x},{z1}", (x - 1, 2, z1 - 1), (x + 1, 8, z1 + 1), M.LOG)
            add_fill(fills, f"flagpole {x},{z1} cloth", (x - 1, 6, z1 - 1), (x + 1, 8, z1 + 1), M.YELLOW_WOOL)


def build_temple_rituals(fills: list[Fill]) -> None:
    for name, x1, z1, x2, z2, ttype in TEMPLES:
        cx, cz = (x1 + x2) // 2, (z1 + z2) // 2

        # Main incense burner in front of the main hall
        add_incense_burner(fills, cx, z1 + 25)

        # Prayer banners flanking the main gate
        banner_colors = [M.RED_WOOL, M.YELLOW_WOOL, M.BLUE_WOOL]
        for i, color in enumerate(banner_colors):
            add_prayer_banner(fills, cx - 20 + i * 8, z1 - 8, color)
            add_prayer_banner(fills, cx + 20 - i * 8, z1 - 8, color)

        # Stone steles in the courtyard
        add_stone_stele(fills, cx - 30, z1 + 60, name)
        add_stone_stele(fills, cx + 30, z1 + 60, name)

        # Flagpole line along the central axis path
        add_flagpole_line(fills, cx, z1 + 15, cx, z1 + 50, 12)

        # Sacred trees at the four courtyard corners
        for tx, tz in [(x1 + 30, z1 + 30), (x2 - 30, z1 + 30), (x1 + 30, z2 - 30), (x2 - 30, z2 - 30)]:
            add_tree(fills, f"{name} sacred tree {tx},{tz}", tx, tz, 2)

        # Daoist temples get extra peach trees; Buddhist get bodhi-like oaks
        if ttype == "daoist":
            for tx, tz in [(x1 + 50, z1 + 50), (x2 - 50, z1 + 50), (x1 + 50, z2 - 50), (x2 - 50, z2 - 50)]:
                add_tree(fills, f"{name} peach {tx},{tz}", tx, tz, 2, height=6, spread=3)


def main() -> None:
    run_builder(build_temple_rituals, "temple_incense_banners")


if __name__ == "__main__":
    main()
