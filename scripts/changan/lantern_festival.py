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
    add_lantern_line,
    run_builder,
)


"""
Shangyuan Festival (上元节) lantern decorations.

Adds festive atmosphere to the whole city:
- Coloured lantern canopies along Zhuque Avenue
- Gate towers lit with redstone lamps
- Market lantern arcs
- Palace courtyard festival lights
"""


def build_zhuque_lantern_canopy(fills: list[Fill]) -> None:
    """Arching coloured lantern canopies over Zhuque Avenue."""
    for z in range(200, 5800, 120):
        # Red, yellow, blue alternating arches
        colors = [M.RED_WOOL, M.YELLOW_WOOL, M.BLUE_WOOL]
        for idx, dx in enumerate([-30, -10, 10, 30]):
            color = colors[idx % len(colors)]
            x = 3000 + dx
            add_fill(fills, f"zhuque canopy {z} {dx}", (x - 3, 10, z - 3), (x + 3, 12, z + 3), color)
            add_fill(fills, f"zhuque lamp {z} {dx}", (x - 1, 9, z - 1), (x + 1, 9, z + 1), M.SEA_LANTERN)


def build_gate_tower_lights(fills: list[Fill]) -> None:
    """Light up gate towers with redstone lamps along roof ridges."""
    gates = [
        ("mingde", 3000, -90),
        ("zhuque", 3000, 0),
        ("anhua", 1200, 0),
        ("qixia", 4800, 0),
        ("xuanwu", 3000, 6000),
    ]
    for name, cx, cz in gates:
        add_fill(fills, f"{name} ridge light", (cx - 40, 75, cz - 40), (cx + 40, 76, cz + 40), M.REDSTONE_LAMP)


def build_market_lantern_arcs(fills: list[Fill]) -> None:
    """Lantern arcs at market entrances."""
    markets = [
        (760, 2060, 1760, 3060),   # West Market
        (4240, 2060, 5240, 3060),  # East Market
    ]
    for idx, (x1, z1, x2, z2) in enumerate(markets):
        mid_x, mid_z = (x1 + x2) // 2, (z1 + z2) // 2
        # Four entrance arches with hanging lanterns
        for ex, ez, label in [(mid_x, z1, "s"), (mid_x, z2, "n"), (x1, mid_z, "w"), (x2, mid_z, "e")]:
            add_fill(fills, f"market {idx} arc {label}", (ex - 18, 12, ez - 2), (ex + 18, 14, ez + 2), M.RED_WOOL)
            add_lantern_line(fills, f"market {idx} arc lamps {label}", ex - 14, ez, ex + 14, ez, 11, 7)


def build_palace_festival_lights(fills: list[Fill]) -> None:
    """Extra festival lights in palace courtyards."""
    # Daming Palace front plaza
    for x in range(2700, 3301, 100):
        for z in range(4000, 4100, 25):
            add_fill(fills, f"daming festival light {x},{z}", (x - 1, 3, z - 1), (x + 1, 7, z + 1), M.SEA_LANTERN)


def build_lantern_festival(fills: list[Fill]) -> None:
    build_zhuque_lantern_canopy(fills)
    build_gate_tower_lights(fills)
    build_market_lantern_arcs(fills)
    build_palace_festival_lights(fills)


def main() -> None:
    run_builder(build_lantern_festival, "lantern_festival")


if __name__ == "__main__":
    main()
