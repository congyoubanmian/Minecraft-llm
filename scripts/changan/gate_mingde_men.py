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
    add_lantern_line,
    add_outline,
    add_ridge_roof,
    run_builder,
)


"""
Mingde Men (明德门) - the main southern gate of Chang'an, five gateways.

Location: local (3000, -90) on the central axis, just south of Zhuque Avenue.
This is the ceremonial main entrance to the entire capital.
"""

CX = 3000
CZ = -90


def build_mingde_men(fills: list[Fill]) -> None:
    # Massive gate tower
    tower_y1 = 35
    tower_y2 = 72
    add_hollow_box(fills, "mingde tower", CX - 70, tower_y1, CZ - 55, CX + 70, tower_y2, CZ + 55, M.RED_WALL, thickness=3)

    # Five gate passages
    for gx in range(CX - 48, CX + 49, 24):
        add_fill(fills, f"mingde passage {gx}", (gx - 5, 1, CZ - 60), (gx + 5, tower_y1 - 1, CZ + 60), M.AIR)
        add_fill(fills, f"mingde passage arch {gx}", (gx - 5, tower_y1, CZ - 60), (gx + 5, tower_y1 + 8, CZ + 60), M.AIR)

    # Triple-eave roof
    add_ridge_roof(fills, "mingde roof", CX - 80, CZ - 65, CX + 80, CZ + 65, tower_y2 + 1, layers=6, ridge_axis="z")

    # Plaque
    add_fill(fills, "mingde plaque", (CX - 30, 58, CZ - 60), (CX + 30, 64, CZ - 56), M.GOLD)
    add_fill(fills, "mingde plaque text", (CX - 18, 59, CZ - 61), (CX + 18, 63, CZ - 61), M.BLACK_WOOL)

    # Side que towers
    for ox in (CX - 180, CX + 180):
        add_hollow_box(fills, f"mingde que {ox}", ox - 28, 1, CZ - 40, ox + 28, 58, CZ + 40, M.STONE, thickness=2)
        add_ridge_roof(fills, f"mingde que roof {ox}", ox - 34, CZ - 46, ox + 34, CZ + 46, 59, layers=5, ridge_axis="z")

    # Outer barbican wall
    add_outline(fills, "mingde barbican", CX - 140, CZ - 180, CX + 140, CZ - 80, 1, 12, M.STONE, thickness=4)
    # Gate through barbican
    add_fill(fills, "mingde barbican gate", (CX - 16, 1, CZ - 182), (CX + 16, 16, CZ - 178), M.AIR)

    # Ceremonial approach lamps
    add_lantern_line(fills, "mingde west lamps", CX - 50, CZ + 80, CX - 50, 800, 3, 60)
    add_lantern_line(fills, "mingde east lamps", CX + 50, CZ + 80, CX + 50, 800, 3, 60)


def main() -> None:
    run_builder(build_mingde_men, "gate_mingde_men")


if __name__ == "__main__":
    main()
