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
    add_ridge_roof,
    run_builder,
)


"""
Fine-grained detail for all remaining Chang'an city gates.

Excludes Mingde Men and Zhuque Men, which have their own dedicated scripts.
Covers the other 10 gates of the outer wall:
    South: Anhua (安化), Qixia (启夏)
    North: Zhide (至德), Xuanwu (玄武), Anli (安礼)
    West: Kaiyuan (开远), Jinguang (金光), Yanping (延平)
    East: Tonghua (通化), Chunming (春明), Yanxing (延兴)
"""

SOUTH_GATES = [
    ("anhua_men", 1200, 0, "north_south"),
    ("qixia_men", 4800, 0, "north_south"),
]

NORTH_GATES = [
    ("zhide_men", 1200, 6000, "north_south"),
    ("xuanwu_men", 3000, 6000, "north_south"),
    ("anli_men", 4800, 6000, "north_south"),
]

WEST_GATES = [
    ("kaiyuan_men", 0, 1500, "east_west"),
    ("jinguang_men", 0, 3000, "east_west"),
    ("yanping_men", 0, 4500, "east_west"),
]

EAST_GATES = [
    ("tonghua_men", 6000, 1500, "east_west"),
    ("chunming_men", 6000, 3000, "east_west"),
    ("yanxing_men", 6000, 4500, "east_west"),
]

ALL_GATES = SOUTH_GATES + NORTH_GATES + WEST_GATES + EAST_GATES


def add_south_north_gate(fills: list[Fill], name: str, cx: int, cz: int) -> None:
    # Gate tower
    add_hollow_box(fills, f"{name} tower", cx - 36, 27, cz - 28, cx + 36, 54, cz + 28, M.RED_WALL, thickness=2)
    # Three gate passages
    for gx in range(cx - 18, cx + 19, 18):
        add_fill(fills, f"{name} passage {gx}", (gx - 4, 1, cz - 30), (gx + 4, 26, cz + 30), M.AIR)
    # Roof
    add_ridge_roof(fills, f"{name} roof", cx - 42, cz - 34, cx + 42, cz + 34, 55, layers=4, ridge_axis="z")
    # Plaque
    add_fill(fills, f"{name} plaque", (cx - 16, 46, cz - 32), (cx + 16, 52, cz - 29), M.GOLD)
    add_fill(fills, f"{name} text", (cx - 8, 47, cz - 33), (cx + 8, 51, cz - 33), M.BLACK_WOOL)
    # Side watch towers
    for ox in (cx - 110, cx + 110):
        add_hollow_box(fills, f"{name} watch {ox}", ox - 18, 1, cz - 24, ox + 18, 44, cz + 24, M.STONE, thickness=2)
        add_ridge_roof(fills, f"{name} watch roof {ox}", ox - 24, cz - 30, ox + 24, cz + 30, 45, layers=3, ridge_axis="z")


def add_east_west_gate(fills: list[Fill], name: str, cx: int, cz: int) -> None:
    add_hollow_box(fills, f"{name} tower", cx - 28, 27, cz - 36, cx + 28, 54, cz + 36, M.RED_WALL, thickness=2)
    for gz in range(cz - 18, cz + 19, 18):
        add_fill(fills, f"{name} passage {gz}", (cx - 30, 1, gz - 4), (cx + 30, 26, gz + 4), M.AIR)
    add_ridge_roof(fills, f"{name} roof", cx - 34, cz - 42, cx + 34, cz + 42, 55, layers=4, ridge_axis="x")
    add_fill(fills, f"{name} plaque", (cx - 32, 46, cz - 16), (cx - 29, 52, cz + 16), M.GOLD)
    add_fill(fills, f"{name} text", (cx - 33, 47, cz - 8), (cx - 33, 51, cz + 8), M.BLACK_WOOL)
    for oz in (cz - 110, cz + 110):
        add_hollow_box(fills, f"{name} watch {oz}", cx - 24, 1, oz - 18, cx + 24, 44, oz + 18, M.STONE, thickness=2)
        add_ridge_roof(fills, f"{name} watch roof {oz}", cx - 30, oz - 24, cx + 30, oz + 24, 45, layers=3, ridge_axis="x")


def build_all_gates(fills: list[Fill]) -> None:
    for name, cx, cz, orientation in ALL_GATES:
        if orientation == "north_south":
            add_south_north_gate(fills, name, cx, cz)
        else:
            add_east_west_gate(fills, name, cx, cz)


def main() -> None:
    run_builder(build_all_gates, "gates_all")


if __name__ == "__main__":
    main()
