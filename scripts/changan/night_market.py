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
Night market decorations for East and West Markets:
- Coloured lantern strings across streets
- Red carpet under the lanterns
- Bright shop fronts
"""


def build_night_market(fills: list[Fill]) -> None:
    markets = [
        (760, 2060, 1760, 3060),   # West Market
        (4240, 2060, 5240, 3060),  # East Market
    ]

    for idx, (x1, z1, x2, z2) in enumerate(markets):
        mid_x = (x1 + x2) // 2
        mid_z = (z1 + z2) // 2

        # Lantern strings across main streets
        for x in range(x1 + 80, x2 - 80, 60):
            add_fill(fills, f"market {idx} string x {x}", (x, 14, mid_z - 34), (x + 2, 14, mid_z + 34), M.RED_WOOL)
            add_fill(fills, f"market {idx} lamps x {x}", (x, 13, mid_z - 34), (x + 2, 13, mid_z + 34), M.SEA_LANTERN)
        for z in range(z1 + 80, z2 - 80, 60):
            add_fill(fills, f"market {idx} string z {z}", (mid_x - 34, 14, z), (mid_x + 34, 14, z + 2), M.RED_WOOL)
            add_fill(fills, f"market {idx} lamps z {z}", (mid_x - 34, 13, z), (mid_x + 34, 13, z + 2), M.SEA_LANTERN)

        # Bright carpets along main streets
        add_fill(fills, f"market {idx} carpet x", (x1 + 60, 2, mid_z - 6), (x2 - 60, 2, mid_z + 6), M.RED_WOOL)
        add_fill(fills, f"market {idx} carpet z", (mid_x - 6, 2, z1 + 60), (mid_x + 6, 2, z2 - 60), M.RED_WOOL)

        # Entrance gate lanterns
        add_lantern_line(fills, f"market {idx} south gate lamps", mid_x, z1 + 10, mid_x, z1 + 80, 3, 15)
        add_lantern_line(fills, f"market {idx} north gate lamps", mid_x, z2 - 80, mid_x, z2 - 10, 3, 15)


def main() -> None:
    run_builder(build_night_market, "night_market")


if __name__ == "__main__":
    main()
