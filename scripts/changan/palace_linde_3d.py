from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    Fill,
    Materials as M,
    add_cantilevered_floor,
    add_dougong_cluster,
    add_fill,
    add_hollow_box,
    add_outline,
    add_ridge_roof,
    add_staircase,
    run_builder,
)


"""
Linde Hall 3D (麟德殿) - the great Tang banquet hall complex in Daming Palace.

Historically the Linde Hall was a triple-joined hall (前/中/后三殿相连) on a
massive terraced platform west of Taiye Pool, flanked by the East and West
pavilions (东亭/西亭) linked by elevated corridors (飞廊复道).

Location in Chang'an city local coordinates:
    footprint: x 1970..2630, z 5210..5790  (west zone of Daming Palace,
    west of the Taiye Pool at x 2780..3220, z 5500..5740)

3D features:
    - Three-tier stone platform with grand southern staircase
    - Front / middle / rear halls at rising heights, joined by enclosed
      two-level corridors (复道) with their own roofs
    - East / West pavilions: two-storey towers with dougong tiers and
      cantilevered viewing galleries
    - Flying corridors (飞廊) from pavilions to the middle hall
    - Banquet side terraces with balustrades and lantern posts
"""

X1, Z1 = 1970, 5210
X2, Z2 = 2630, 5790
CX = 2300


def _hall(
    fills: list[Fill],
    name: str,
    x1: int, z1: int, x2: int, z2: int,
    y_base: int, y_top: int,
    roof_layers: int,
) -> None:
    """One hollow hall with columns, dougong, and a ridge roof."""
    add_hollow_box(fills, f"linde {name} walls", x1, y_base, z1, x2, y_top, z2, M.RED_WALL, thickness=2)
    # Interior floor
    add_fill(fills, f"linde {name} floor", (x1 + 1, y_base, z1 + 1), (x2 - 1, y_base, z2 - 1), M.SMOOTH)
    # Door openings on south and north faces
    mid_x = (x1 + x2) // 2
    add_fill(fills, f"linde {name} door s", (mid_x - 6, y_base + 1, z1), (mid_x + 6, y_base + 8, z1 + 1), M.AIR)
    add_fill(fills, f"linde {name} door n", (mid_x - 6, y_base + 1, z2 - 1), (mid_x + 6, y_base + 8, z2), M.AIR)
    # Window lattice strips on the long sides
    for x in range(x1 + 10, x2 - 9, 20):
        add_fill(fills, f"linde {name} window w {x}", (x, y_base + 4, z1), (x + 6, y_base + 8, z1), M.GLASS)
        add_fill(fills, f"linde {name} window e {x}", (x, y_base + 4, z2), (x + 6, y_base + 8, z2), M.GLASS)
    # Dougong rows under the eaves at the four corners
    for sx in (-1, 1):
        for sz in (-1, 1):
            add_dougong_cluster(
                fills, f"linde {name} dougong {sx},{sz}",
                mid_x + sx * (x2 - x1) // 2, (z1 + z2) // 2 + sz * (z2 - z1) // 2,
                y=y_top, tiers=2,
            )
    add_ridge_roof(fills, f"linde {name} roof", x1 - 6, z1 - 6, x2 + 6, z2 + 6, y_top + 1, layers=roof_layers, ridge_axis="x")


def build_linde_3d(fills: list[Fill]) -> None:
    add_fill(fills, "linde clear", (X1, 1, Z1), (X2, 75, Z2), M.AIR)

    # ------------------------------------------------------------------
    # 1. Three-tier stone platform with balustrades.
    # ------------------------------------------------------------------
    add_fill(fills, "linde platform t1", (2010, 1, 5250), (2590, 3, 5750), M.STONE)
    add_fill(fills, "linde platform t2", (2050, 4, 5290), (2550, 6, 5710), M.STONE)
    add_fill(fills, "linde platform t3", (2090, 7, 5330), (2510, 9, 5670), M.STONE)
    # White marble balustrades on each tier edge
    add_outline(fills, "linde rail t1", 2010, 5250, 2590, 5750, 4, 4, M.QUARTZ, thickness=1)
    add_outline(fills, "linde rail t2", 2050, 5290, 2550, 5710, 7, 7, M.QUARTZ, thickness=1)
    add_outline(fills, "linde rail t3", 2090, 5330, 2510, 5670, 10, 10, M.QUARTZ, thickness=1)

    # Grand southern staircase climbing all three tiers
    add_staircase(fills, "linde grand stair 1", 2280, 5220, 2320, 5250, y1=1, y2=3, direction="south", block=M.SMOOTH)
    add_staircase(fills, "linde grand stair 2", 2280, 5260, 2320, 5290, y1=3, y2=6, direction="south", block=M.SMOOTH)
    add_staircase(fills, "linde grand stair 3", 2280, 5300, 2320, 5330, y1=6, y2=9, direction="south", block=M.SMOOTH)
    # Stair balustrades
    for z in range(5220, 5330, 10):
        y = 2 + (z - 5220) // 20
        add_fill(fills, f"linde stair rail w {z}", (2278, y, z), (2278, y + 1, z + 6), M.QUARTZ)
        add_fill(fills, f"linde stair rail e {z}", (2322, y, z), (2322, y + 1, z + 6), M.QUARTZ)

    # ------------------------------------------------------------------
    # 2. Triple-joined halls, rising toward the rear (north).
    # ------------------------------------------------------------------
    _hall(fills, "front", 2150, 5350, 2450, 5450, y_base=10, y_top=24, roof_layers=3)
    _hall(fills, "middle", 2130, 5470, 2470, 5550, y_base=10, y_top=30, roof_layers=4)
    _hall(fills, "rear", 2170, 5570, 2430, 5650, y_base=10, y_top=22, roof_layers=3)

    # Enclosed two-level corridors (复道) joining front->middle->rear
    for name, z1, z2 in [("fm", 5450, 5470), ("mr", 5550, 5570)]:
        x1, x2 = 2270, 2330
        # Lower passage
        add_fill(fills, f"linde fudao {name} low wall w", (x1, 10, z1), (x1 + 1, 17, z2), M.RED_WALL)
        add_fill(fills, f"linde fudao {name} low wall e", (x2 - 1, 10, z1), (x2, 17, z2), M.RED_WALL)
        # Upper gallery: cantilevered floor, waist walls, roof
        add_cantilevered_floor(fills, f"linde fudao {name} upper", x1, z1, x2, z2, y=18, overhang=2, block=M.WOOD)
        add_fill(fills, f"linde fudao {name} up wall w", (x1 - 2, 19, z1), (x1 - 1, 22, z2), M.RED_WALL)
        add_fill(fills, f"linde fudao {name} up wall e", (x2 + 1, 19, z1), (x2 + 2, 22, z2), M.RED_WALL)
        add_fill(fills, f"linde fudao {name} roof", (x1 - 4, 23, z1 - 2), (x2 + 4, 24, z2 + 2), M.ROOF_GREEN)
        # Windows along the upper gallery
        add_fill(fills, f"linde fudao {name} glass w", (x1 - 2, 20, z1 + 4), (x1 - 1, 21, z2 - 4), M.GLASS)
        add_fill(fills, f"linde fudao {name} glass e", (x2 + 1, 20, z1 + 4), (x2 + 2, 21, z2 - 4), M.GLASS)

    # ------------------------------------------------------------------
    # 3. East / West pavilions (东亭/西亭): two-storey towers.
    # ------------------------------------------------------------------
    for side, px1, px2 in [("west", 2040, 2120), ("east", 2480, 2560)]:
        pz1, pz2 = 5460, 5540
        pmid_x, pmid_z = (px1 + px2) // 2, (pz1 + pz2) // 2
        add_hollow_box(fills, f"linde {side} pavilion low", px1, 10, pz1, px2, 22, pz2, M.RED_WALL, thickness=2)
        add_cantilevered_floor(
            fills, f"linde {side} pavilion gallery",
            px1, pz1, px2, pz2, y=22, overhang=4, block=M.WOOD,
        )
        add_outline(fills, f"linde {side} pavilion rail", px1 - 4, pz1 - 4, px2 + 4, pz2 + 4, 23, 23, M.FENCE, thickness=1)
        add_hollow_box(fills, f"linde {side} pavilion up", px1 + 6, 23, pz1 + 6, px2 - 6, 34, pz2 - 6, M.RED_WALL, thickness=2)
        for sx in (-1, 1):
            for sz in (-1, 1):
                add_dougong_cluster(
                    fills, f"linde {side} pavilion dougong {sx},{sz}",
                    pmid_x + sx * (px2 - px1) // 2, pmid_z + sz * (pz2 - pz1) // 2, y=34, tiers=3,
                )
        add_ridge_roof(fills, f"linde {side} pavilion roof", px1 - 4, pz1 - 4, px2 + 4, pz2 + 4, 36, layers=4, ridge_axis="x")
        # Interior stair between storeys
        for i in range(12):
            add_fill(
                fills, f"linde {side} pavilion stair {i}",
                (px1 + 4 + i % 4, 10 + i, pz1 + 4 + i // 4),
                (px1 + 5 + i % 4, 10 + i, pz1 + 4 + i // 4),
                M.SMOOTH,
            )

        # Flying corridor (飞廊) from pavilion to the middle hall
        fx1 = px2 if side == "west" else 2470
        fx2 = 2130 if side == "west" else px1
        fz1, fz2 = 5490, 5510
        # Piers
        for x in range(min(fx1, fx2) + 8, max(fx1, fx2), 16):
            add_fill(fills, f"linde {side} fylang pier {x}", (x, 9, fz1 + 6), (x + 3, 21, fz1 + 9), M.LOG)
        add_cantilevered_floor(fills, f"linde {side} fylang deck", min(fx1, fx2), fz1, max(fx1, fx2), fz2, y=22, overhang=2, block=M.WOOD)
        add_fill(fills, f"linde {side} fylang roof", (min(fx1, fx2) - 2, 26, fz1 - 2), (max(fx1, fx2) + 2, 27, fz2 + 2), M.ROOF_GREEN)
        add_fill(fills, f"linde {side} fylang wall n", (min(fx1, fx2), 23, fz1), (max(fx1, fx2), 25, fz1), M.RED_WALL)
        add_fill(fills, f"linde {side} fylang wall s", (min(fx1, fx2), 23, fz2), (max(fx1, fx2), 25, fz2), M.RED_WALL)

    # ------------------------------------------------------------------
    # 4. Banquet side terraces + courtyard dressing.
    # ------------------------------------------------------------------
    for side, tx1, tx2 in [("west", 2100, 2130), ("east", 2470, 2500)]:
        add_fill(fills, f"linde terrace {side}", (tx1, 9, 5360), (tx2, 10, 5440), M.WOOD)
        add_outline(fills, f"linde terrace rail {side}", tx1, 5360, tx2, 5440, 11, 11, M.FENCE, thickness=1)

    # Lantern posts around the top platform
    for x in range(2120, 2500, 60):
        for z in (5340, 5660):
            add_fill(fills, f"linde lantern post {x},{z}", (x, 10, z), (x, 15, z), M.LOG)
            add_fill(fills, f"linde lantern {x},{z}", (x, 16, z), (x, 16, z), M.LANTERN)

    # Incense braziers flanking the grand stair
    for sx in (-1, 1):
        bx = CX + sx * 60
        add_fill(fills, f"linde brazier base {sx}", (bx - 4, 9, 5320), (bx + 4, 11, 5336), M.DARK_BRICKS)
        add_fill(fills, f"linde brazier bowl {sx}", (bx - 3, 12, 5323), (bx + 3, 14, 5333), M.GOLD_ACCENT)


def main() -> None:
    run_builder(build_linde_3d, "palace_linde_3d")


if __name__ == "__main__":
    main()
