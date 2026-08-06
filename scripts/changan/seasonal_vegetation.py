from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    Fill,
    Materials as M,
    add_fill,
    iter_ward_origins,
    run_builder,
)


"""
Seasonal vegetation patches for gardens, wards, and palace courtyards.

Supports --season spring|summer|autumn|winter to switch flower colors:
- spring: peach / pink
- summer: lotus / pink + water lilies
- autumn: chrysanthemum / yellow
- winter: plum / white + snow accents
"""


SEASONS = {
    "spring": {
        "flower": M.PINK_WOOL,
        "secondary": M.WHITE_WOOL,
        "label": "peach",
    },
    "summer": {
        "flower": M.PINK_WOOL,
        "secondary": M.GREEN_WOOL,
        "label": "lotus",
    },
    "autumn": {
        "flower": M.YELLOW_WOOL,
        "secondary": M.RED_WOOL,
        "label": "chrysanthemum",
    },
    "winter": {
        "flower": M.WHITE_WOOL,
        "secondary": M.GRAY_CONCRETE,
        "label": "plum",
    },
}


GARDEN_SPOTS = [
    # (name, x1, z1, x2, z2)
    ("daming_peony", 2000, 5350, 2200, 5500),
    ("xingqing_court", 1200, 1200, 1400, 1400),
    ("taiji_court", 2600, 5600, 2750, 5750),
    ("leyou_garden", 5200, 5000, 5600, 5400),
    ("guozijian_plum", 1630, 4400, 1720, 4520),
]


def add_seasonal_bed(fills: list[Fill], name: str, x1: int, z1: int, x2: int, z2: int, season: str) -> None:
    """One seasonal flower bed."""
    cfg = SEASONS[season]
    for x in range(x1 + 6, x2 - 5, 12):
        for z in range(z1 + 6, z2 - 5, 12):
            add_fill(fills, f"{name} {cfg['label']} {x},{z}", (x, 2, z), (x + 2, 2, z + 2), cfg["flower"])
    # Winter snow accents
    if season == "winter":
        for x in range(x1 + 2, x2 - 1, 20):
            for z in range(z1 + 2, z2 - 1, 20):
                add_fill(fills, f"{name} snow {x},{z}", (x, 2, z), (x + 1, 2, z + 1), cfg["secondary"])


def add_ward_seasonal_patch(fills: list[Fill], origin_x: int, origin_z: int, season: str) -> None:
    """A small seasonal flower patch inside a ward courtyard."""
    cfg = SEASONS[season]
    x1 = origin_x + 140
    z1 = origin_z + 150
    x2 = origin_x + 155
    z2 = origin_z + 220
    label = f"ward_seasonal_{origin_x}_{origin_z}_{cfg['label']}"
    for x in range(x1 + 5, x2 - 4, 15):
        for z in range(z1 + 5, z2 - 4, 15):
            add_fill(fills, f"{label} cluster {x},{z}", (x, 2, z), (x + 2, 2, z + 2), cfg["flower"])


def build_seasonal_vegetation(fills: list[Fill], season: str = "spring") -> None:
    # Named gardens
    for name, x1, z1, x2, z2 in GARDEN_SPOTS:
        add_seasonal_bed(fills, name, x1, z1, x2, z2, season)

    # Ward patches
    for x, z in iter_ward_origins():
        add_ward_seasonal_patch(fills, x, z, season)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build seasonal vegetation patches.")
    parser.add_argument(
        "--season",
        type=str,
        default="spring",
        choices=list(SEASONS.keys()),
        help="Which seasonal palette to use.",
    )
    args, remaining = parser.parse_known_args()
    sys.argv = [sys.argv[0], *remaining]

    run_builder(
        lambda fills: build_seasonal_vegetation(fills, season=args.season),
        f"seasonal_vegetation_{args.season}",
    )


if __name__ == "__main__":
    main()
