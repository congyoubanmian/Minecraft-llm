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
    run_builder,
)


"""
Stone arch bridges for Chang'an canals and palace moats.

Can be placed at multiple crossing points.
"""

BRIDGES = [
    # (name, center_x, center_z, orientation)
    ("zhuque_bridge", 3000, 1500, "z"),
    ("west_canal_bridge", 1500, 3000, "x"),
    ("east_canal_bridge", 4500, 3000, "x"),
    ("taiye_bridge", 3000, 5550, "x"),
]


def build_bridge(
    fills: list[Fill],
    name: str,
    cx: int,
    cz: int,
    orientation: str,
    span: int = 60,
    width: int = 14,
) -> None:
    """Build a single stone arch bridge."""
    if orientation == "z":
        # Deck spans along z
        add_fill(fills, f"{name} deck", (cx - width // 2, 4, cz - span // 2), (cx + width // 2, 5, cz + span // 2), M.SMOOTH)
        # Side rails
        add_fill(fills, f"{name} rail w", (cx - width // 2 - 1, 6, cz - span // 2), (cx - width // 2 - 1, 7, cz + span // 2), M.STONE)
        add_fill(fills, f"{name} rail e", (cx + width // 2 + 1, 6, cz - span // 2), (cx + width // 2 + 1, 7, cz + span // 2), M.STONE)
        # Arch abutments
        for oz in (cz - span // 2, cz + span // 2):
            add_fill(fills, f"{name} abut {oz}", (cx - width // 2 - 2, 1, oz - 6), (cx + width // 2 + 2, 6, oz + 6), M.STONE)
        # Arch profile blocks under deck
        for i in range(8):
            inset = i
            add_fill(fills, f"{name} arch {i}", (cx - width // 2, 3 - i // 3, cz - span // 2 + 8 + i * 3), (cx + width // 2, 3 - i // 3, cz - span // 2 + 10 + i * 3), M.STONE)
            add_fill(fills, f"{name} arch s {i}", (cx - width // 2, 3 - i // 3, cz + span // 2 - 10 - i * 3), (cx + width // 2, 3 - i // 3, cz + span // 2 - 8 - i * 3), M.STONE)
    else:
        # Deck spans along x
        add_fill(fills, f"{name} deck", (cx - span // 2, 4, cz - width // 2), (cx + span // 2, 5, cz + width // 2), M.SMOOTH)
        add_fill(fills, f"{name} rail n", (cx - span // 2, 6, cz - width // 2 - 1), (cx + span // 2, 7, cz - width // 2 - 1), M.STONE)
        add_fill(fills, f"{name} rail s", (cx - span // 2, 6, cz + width // 2 + 1), (cx + span // 2, 7, cz + width // 2 + 1), M.STONE)
        for ox in (cx - span // 2, cx + span // 2):
            add_fill(fills, f"{name} abut {ox}", (ox - 6, 1, cz - width // 2 - 2), (ox + 6, 6, cz + width // 2 + 2), M.STONE)
        for i in range(8):
            add_fill(fills, f"{name} arch {i}", (cx - span // 2 + 8 + i * 3, 3 - i // 3, cz - width // 2), (cx - span // 2 + 10 + i * 3, 3 - i // 3, cz + width // 2), M.STONE)
            add_fill(fills, f"{name} arch e {i}", (cx + span // 2 - 10 - i * 3, 3 - i // 3, cz - width // 2), (cx + span // 2 - 8 - i * 3, 3 - i // 3, cz + width // 2), M.STONE)

    # Pavilion at the bridge center
    add_fill(fills, f"{name} pavilion base", (cx - 6, 6, cz - 6), (cx + 6, 7, cz + 6), M.ANDESITE)
    add_fill(fills, f"{name} pavilion body", (cx - 5, 8, cz - 5), (cx + 5, 16, cz + 5), M.RED_WALL)
    add_ridge_roof(fills, f"{name} pavilion roof", cx - 8, cz - 8, cx + 8, cz + 8, 17, layers=2, ridge_axis="z")


def build_all_bridges(fills: list[Fill]) -> None:
    for name, cx, cz, orientation in BRIDGES:
        build_bridge(fills, name, cx, cz, orientation)


def main() -> None:
    run_builder(build_all_bridges, "bridge_stone_arch")


if __name__ == "__main__":
    main()
