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
Poem steles, named pavilion plaques, and stone benches
for the Leyouyuan pleasure garden (乐游园).
"""

# Leyouyuan bounds
LX1, LZ1 = 5000, 4800
LX2, LZ2 = 5800, 5600
CX, CZ = (LX1 + LX2) // 2, (LZ1 + LZ2) // 2


def add_poem_stele(fills: list[Fill], x: int, z: int, name: str) -> None:
    """A stone stele with a poem inscribed on its face."""
    add_fill(fills, f"{name} stele {x},{z} base", (x - 2, 2, z - 1), (x + 2, 3, z + 1), M.ANDESITE)
    add_fill(fills, f"{name} stele {x},{z} body", (x - 1, 4, z - 1), (x + 1, 10, z + 1), M.QUARTZ)
    add_fill(fills, f"{name} stele {x},{z} cap", (x - 2, 11, z - 1), (x + 2, 12, z + 1), M.DARK)
    # Text lines on the stele face
    for i in range(3):
        add_fill(fills, f"{name} stele {x},{z} text {i}", (x, 5 + i * 2, z - 2), (x, 6 + i * 2, z - 2), M.BLACK_WOOL)


def add_pavilion_plaque(fills: list[Fill], x: int, z: int, y: int, width: int, name: str) -> None:
    """A horizontal gold plaque with the pavilion name."""
    add_fill(fills, f"{name} plaque {x},{z} frame", (x - width // 2, y, z - 1), (x + width // 2, y + 3, z + 1), M.GOLD)
    add_fill(fills, f"{name} plaque {x},{z} text", (x - width // 2 + 2, y + 1, z - 2), (x + width // 2 - 2, y + 2, z - 2), M.BLACK_WOOL)


def add_stone_bench(fills: list[Fill], x: int, z: int) -> None:
    """A low stone bench for poets to sit and compose."""
    add_fill(fills, f"bench {x},{z}", (x - 3, 2, z - 1), (x + 3, 2, z + 1), M.SMOOTH)


def build_leyouyuan_details(fills: list[Fill]) -> None:
    # Poem steles scattered along the paths
    steles = [
        (CX - 150, CZ - 200, "li_bai"),
        (CX + 150, CZ - 200, "du_fu"),
        (CX - 200, CZ + 150, "wang_wei"),
        (CX + 200, CZ + 150, "bai_juyi"),
        (CX, CZ - 250, "qingqiu"),
    ]
    for x, z, name in steles:
        add_poem_stele(fills, x, z, name)

    # Pavilion plaques
    add_pavilion_plaque(fills, CX, CZ - 28, 25, 14, "qingqiu")   # Qingqiu Pavilion
    add_pavilion_plaque(fills, CX - 120, CZ - 18, 15, 10, "east_side")
    add_pavilion_plaque(fills, CX + 120, CZ - 18, 15, 10, "west_side")

    # Stone benches near steles and pavilions
    benches = [
        (CX - 150, CZ - 190), (CX + 150, CZ - 190),
        (CX - 200, CZ + 160), (CX + 200, CZ + 160),
        (CX - 30, CZ + 30), (CX + 30, CZ - 30),
        (CX - 80, CZ + 80), (CX + 80, CZ - 80),
    ]
    for x, z in benches:
        add_stone_bench(fills, x, z)


def main() -> None:
    run_builder(build_leyouyuan_details, "leyouyuan_stele")


if __name__ == "__main__":
    main()
