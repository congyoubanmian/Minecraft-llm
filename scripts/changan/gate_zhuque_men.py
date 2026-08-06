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
Zhuque Men (朱雀门) - the southern gate of the Imperial City.

In Chang'an city local coordinates this sits on the central axis at
z = 0 (south edge of the city grid), x = 3000.

Features:
    - Massive gate tower with double-eave roof
    - Five gate passages
    - Side watch towers and barbican (outer half-moon wall)
    - Plaque and lantern posts
"""

CX = 3000
CZ = 0


def build_zhuque_men(fills: list[Fill]) -> None:
    # Main gate tower sits on top of the existing gatehouse
    tower_y1 = 39
    tower_y2 = 68
    add_hollow_box(fills, "zhuque tower", CX - 50, tower_y1, -42, CX + 50, tower_y2, 42, M.RED_WALL, thickness=2)

    # Five gate passages through the tower
    for gx in range(CX - 32, CX + 33, 16):
        add_fill(fills, f"zhuque passage {gx}", (gx - 4, 1, -45), (gx + 4, tower_y1 - 1, 45), M.AIR)
        add_fill(fills, f"zhuque passage arch {gx}", (gx - 4, tower_y1, -45), (gx + 4, tower_y1 + 6, 45), M.AIR)

    # Double-eave roof on tower
    add_ridge_roof(fills, "zhuque tower roof", CX - 58, -50, CX + 58, 50, tower_y2 + 1, layers=5, ridge_axis="z")

    # Plaque
    add_fill(fills, "zhuque plaque board", (CX - 24, 52, -47), (CX + 24, 58, -44), M.GOLD)
    add_fill(fills, "zhuque plaque text", (CX - 14, 53, -48), (CX + 14, 57, -48), M.BLACK_WOOL)

    # Side watch towers
    for ox in (CX - 130, CX + 130):
        add_hollow_box(fills, f"zhuque watch tower {ox}", ox - 22, 1, -30, ox + 22, 55, 30, M.STONE, thickness=2)
        add_ridge_roof(fills, f"zhuque watch roof {ox}", ox - 28, -36, ox + 28, 36, 56, layers=4, ridge_axis="z")

    # Barbican - outer half-moon defensive wall
    add_outline(fills, "zhuque barbican", CX - 110, 80, CX + 110, 200, 1, 12, M.STONE, thickness=4)
    # Gate through barbican
    add_fill(fills, "zhuque barbican gate", (CX - 12, 1, 78), (CX + 12, 14, 86), M.AIR)

    # Lanterns along the approach
    add_lantern_line(fills, "zhuque west lamps", CX - 40, 120, CX - 40, 580, 3, 60)
    add_lantern_line(fills, "zhuque east lamps", CX + 40, 120, CX + 40, 580, 3, 60)


def main() -> None:
    run_builder(build_zhuque_men, "gate_zhuque_men")


if __name__ == "__main__":
    main()
