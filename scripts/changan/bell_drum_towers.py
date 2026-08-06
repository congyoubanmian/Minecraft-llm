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
Bell Tower (钟楼) and Drum Tower (鼓楼) for the palace and city.

Tang custom: morning bell and evening drum.
"""


TOWERS = [
    # (name, x, z, is_bell)
    ("daming_bell_tower", 2200, 4200, True),
    ("daming_drum_tower", 3800, 4200, False),
    ("taiji_bell_tower", 2400, 4700, True),
    ("taiji_drum_tower", 3600, 4700, False),
]


def build_tower(fills: list[Fill], name: str, cx: int, cz: int, is_bell: bool) -> None:
    # Square tower body
    add_hollow_box(fills, f"{name} body", cx - 18, 1, cz - 18, cx + 18, 42, cz + 18, M.RED_WALL, thickness=2)

    # Openings on four sides for sound
    for ox, oz, label in [(0, -19, "s"), (0, 19, "n"), (-19, 0, "w"), (19, 0, "e")]:
        add_fill(fills, f"{name} opening {label}", (cx - 8 + ox, 8, cz - 8 + oz), (cx + 8 + ox, 28, cz + 8 + oz), M.AIR)
        add_fill(fills, f"{name} frame {label}", (cx - 10 + ox, 6, cz - 10 + oz), (cx + 10 + ox, 30, cz + 10 + oz), M.WOOD)

    # Bell or drum block in center
    instrument_block = M.GOLD if is_bell else M.RED_WOOL
    add_fill(fills, f"{name} instrument", (cx - 3, 18, cz - 3), (cx + 3, 24, cz + 3), instrument_block)

    # Roof
    add_ridge_roof(fills, f"{name} roof", cx - 24, cz - 24, cx + 24, cz + 24, 43, layers=4, ridge_axis="z")

    # Spire
    add_fill(fills, f"{name} spire", (cx - 1, 51, cz - 1), (cx + 1, 60, cz + 1), M.GOLD)


def build_bell_drum_towers(fills: list[Fill]) -> None:
    for name, cx, cz, is_bell in TOWERS:
        build_tower(fills, name, cx, cz, is_bell)


def main() -> None:
    run_builder(build_bell_drum_towers, "bell_drum_towers")


if __name__ == "__main__":
    main()
