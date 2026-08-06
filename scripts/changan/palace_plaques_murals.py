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
    run_builder,
)


"""
Palace plaques, murals, and folding screens.

Adds hanging name plaques above gates/halls, colored wool mural panels
on palace walls, and folding screens inside throne rooms.
"""


def add_plaque(fills: list[Fill], x: int, y: int, z: int, width: int, facing: str) -> None:
    """A horizontal gold-framed plaque with dark text."""
    if facing in ("south", "north"):
        add_fill(fills, f"plaque {x},{z} frame", (x - width // 2, y, z - 1), (x + width // 2, y + 4, z + 1), M.GOLD)
        add_fill(fills, f"plaque {x},{z} text", (x - width // 2 + 2, y + 1, z - 2), (x + width // 2 - 2, y + 3, z - 2), M.BLACK_WOOL)
    else:
        add_fill(fills, f"plaque {x},{z} frame", (x - 1, y, z - width // 2), (x + 1, y + 4, z + width // 2), M.GOLD)
        add_fill(fills, f"plaque {x},{z} text", (x - 2, y + 1, z - width // 2 + 2), (x - 2, y + 3, z + width // 2 - 2), M.BLACK_WOOL)


def add_mural_panel(fills: list[Fill], x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, color: str, facing: str) -> None:
    """A colored wool mural inset into a wall."""
    if facing in ("south", "north"):
        add_fill(fills, f"mural {x1},{z1}", (x1, y1, z1), (x2, y2, z1 + 1), color)
        # Thin gold border
        add_fill(fills, f"mural {x1},{z1} border t", (x1 - 1, y1 - 1, z1), (x2 + 1, y1 - 1, z1 + 1), M.GOLD)
        add_fill(fills, f"mural {x1},{z1} border b", (x1 - 1, y2 + 1, z1), (x2 + 1, y2 + 1, z1 + 1), M.GOLD)
    else:
        add_fill(fills, f"mural {x1},{z1}", (x1, y1, z1), (x1 + 1, y2, z2), color)
        add_fill(fills, f"mural {x1},{z1} border t", (x1, y1 - 1, z1 - 1), (x1 + 1, y1 - 1, z2 + 1), M.GOLD)
        add_fill(fills, f"mural {x1},{z1} border b", (x1, y2 + 1, z1 - 1), (x1 + 1, y2 + 1, z2 + 1), M.GOLD)


def add_folding_screen(fills: list[Fill], x: int, y: int, z: int, width: int) -> None:
    """A zig-zag folding screen behind a throne."""
    for i in range(width):
        px = x - width // 2 + i
        pz = z + (i % 2)  # zigzag depth
        add_fill(fills, f"screen {x},{z} panel {i}", (px, y, pz), (px, y + 8, pz), M.RED_WALL_ALT)
        if i % 2 == 0:
            add_fill(fills, f"screen {x},{z} trim {i}", (px, y + 8, pz), (px, y + 8, pz), M.GOLD)


def build_palace_decor(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # Gate plaques
    # ------------------------------------------------------------------
    # Outer city gates already carry plaques in their dedicated modules.
    add_plaque(fills, 3000, 43, 4047, 16, "south")  # Danfeng Gate
    add_plaque(fills, 3000, 10, 4712, 12, "south")  # Chengtian Gate

    # ------------------------------------------------------------------
    # Hall plaques
    # ------------------------------------------------------------------
    add_plaque(fills, 3000, 28, 5177, 12, "south")   # Hanyuan Dian
    add_plaque(fills, 3000, 26, 4877, 12, "south")   # Xuanzheng Dian
    add_plaque(fills, 2490, 22, 5197, 12, "south")   # Zichen Dian
    add_plaque(fills, 3000, 27, 5047, 12, "south")   # Taiji Dian
    add_plaque(fills, 1020, 25, 1449, 10, "south")   # Flower-Attending Tower
    add_plaque(fills, 1300, 13, 1181, 10, "south")   # Chenxiang Pavilion

    # ------------------------------------------------------------------
    # Murals inside palace halls (south walls)
    # ------------------------------------------------------------------
    mural_colors = [M.RED_WOOL, M.BLUE_WOOL, M.YELLOW_WOOL, M.GREEN_WOOL]
    for i, color in enumerate(mural_colors):
        # Hanyuan Dian interior murals
        add_mural_panel(fills, 2800 + i * 120, 25, 5479, 2880 + i * 120, 45, 5479, color, "south")
        # Taiji Dian interior murals
        add_mural_panel(fills, 2940 + i * 30, 18, 5149, 2960 + i * 30, 34, 5149, color, "south")
        # Xingqing Flower Tower murals
        add_mural_panel(fills, 996 + i * 12, 10, 1507, 1004 + i * 12, 25, 1507, color, "south")


def main() -> None:
    run_builder(build_palace_decor, "palace_plaques_murals")


if __name__ == "__main__":
    main()
