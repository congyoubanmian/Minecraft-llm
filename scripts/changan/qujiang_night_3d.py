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
    add_outline,
    run_builder,
)


"""
Qujiang Night Banquet 3D (曲江夜宴·灯船河灯) - the Shangyuan festival
night (上元夜) on Qujiang Pool: the imperial feast lantern boats drifting
on dark water with a full river of floating lamps, while banqueting
tents and a lantern-riddle wall line the north shore.

Location in Chang'an city local coordinates:
    Hard build zone: Qujiang Pool water plus its shore strips,
    x 5100..5900, z 5300..5910. Water surface y=1 (pool floor y -1..0).
    The whole night stage keeps clear of the Leyouyuan grass terrace
    (entertainment_venues.py: x 5000..5800, y 1..2, z 4800..5600):
    - the water stage (all boats, river lamps, lamp frames) sits in the
      south-east clean water x 5600..5800, z 5620..5850, entirely south
      and east of the terrace footprint
    - the shore camp (tents, riddle wall, guide posts, piers) sits on
      the solid north-east shore strip x 5801..5900, z 5300..5319,
      east of the terrace edge and north of the pool rim (z < 5320)
    Further avoids every existing structure with 8+ blocks of clearance:
    - qujiang_pool_3d lake centre island x 5420..5580, z 5540..5660,
      and the moored pleasure boat (画舫) x 5450..5490, z 5555..5575
    - the four waterfront pavilions (水榭) centred (5120, 5380),
      (5880, 5380), (5200, 5880), (5800, 5880); the south-east one
      (x 5786..5814, z 5866..5894) bounds the clean-water stage
    - the curved stone bridge gallery x 5516..5524, z 5340..5860 and
      its mid-lake bridge pavilion x 5510..5530, z 5590..5610
    - the terraced northern inlet pools x 5420..5580, z 5220..5320
    - the west/east shore boardwalks (x <= 5062 / x >= 5938) and the
      shore trees along z 5300 (x = 5100 + 80k)
    - fuyong_yuan_3d Purple Cloud Tower on the south shore z 5935..6075
    - xingyuan_3d apricot garden west of the pool x 4620..4990

Distinctive features:
    - Grand banquet lantern boat (24x10) in the south-east clean water:
      plank hull with log gunwale, open canopy (敞棚) ringed by 12
      hanging lanterns (RED_WOOL shade + SEA_LANTERN core, alternating),
      a two-storey bow light tower with balcony and gilded cap, and a
      red-carpet feast deck with a long table and gold wine vessels
    - Two 12x6 escort lantern boats, one scarlet and one gilded theme,
      each with six side lanterns and a central lamp mast
    - A drift of 24 river lamps (河灯): lily-pad bases with red /
      yellow / pink wool flames scattered by fixed coordinates over the
      clean-water stage, clear of every boat, bridge, island, pavilion
      and the Leyouyuan terrace
    - Two water lamp frames standing in the pool: fence gantries with
      crossbars carrying four hanging lamps each
    - Three night banquet tents on the north-east shore strip: timber
      skeleton, deep-blue wool night-sky roofs, inner lamp tables,
      outer wind lanterns and landing piers into the pool
    - A lantern-riddle wall (灯谜墙, 10x5 white terracotta) hung with
      eight coloured riddle strips between two festival flag poles
    - Four guide lamp posts marking the shore banquet landings
"""

WATER_Y = 1

# Grand banquet lantern boat: hull x 5678..5701, z 5695..5704, bow
# tower to x 5707. Every water placement stays inside the south-east
# clean-water stage (x 5600..5800, z 5620..5850), 8+ blocks from the
# island (x <= 5580), the bridge corridor (x <= 5532) and the
# south-east pavilion (x >= 5786, z >= 5866).
FEAST_X1, FEAST_Z1 = 5678, 5695
FEAST_X2, FEAST_Z2 = 5701, 5704

# Escort lantern boats (one scarlet, one gilded).
RED_X1, RED_Z1 = 5725, 5758
RED_X2, RED_Z2 = 5736, 5763
GOLD_X1, GOLD_Z1 = 5615, 5743
GOLD_X2, GOLD_Z2 = 5626, 5748

# Water lamp frames: gantry lines standing in the pool.
FRAME_LINES = [
    (5640, 5651, 5660, M.RED_WOOL),     # west gantry, red lamps
    (5748, 5759, 5800, M.YELLOW_WOOL),  # east gantry, yellow lamps
]

# 24 river lamps: (x, z) fixed scatter across the clean-water stage
# (x 5610..5790, z 5630..5840), each kept 8+ blocks from the boats,
# lamp frames, island, bridge, south-east pavilion and the terrace.
RIVER_LAMPS = [
    (5660, 5680), (5650, 5700), (5665, 5720), (5690, 5718),
    (5716, 5685), (5730, 5720), (5750, 5700), (5760, 5730),
    (5780, 5760), (5770, 5790), (5740, 5810), (5700, 5820),
    (5660, 5800), (5630, 5780), (5660, 5760), (5690, 5750),
    (5620, 5700), (5665, 5645), (5690, 5640), (5720, 5650),
    (5750, 5660), (5780, 5660), (5610, 5640), (5750, 5830),
]
LAMP_FLAME = [M.RED_WOOL, M.YELLOW_WOOL, M.PINK_WOOL]

# North-shore night banquet tents (13x11 footprints, centres below) on
# the solid north-east shore strip, east of the Leyouyuan terrace
# edge (x > 5800) and north of the pool rim (z < 5320).
TENT_CENTRES = [5808, 5834, 5860]
TENT_Z1, TENT_Z2 = 5303, 5313

# Lantern-riddle wall on the shore strip.
WALL_X1, WALL_X2, WALL_Z = 5876, 5885, 5310
RIDDLE_COLORS = [
    M.RED_WOOL, M.YELLOW_WOOL, M.PINK_WOOL, M.WHITE_WOOL,
    M.GREEN_WOOL, M.RED_WOOL, M.YELLOW_WOOL, M.PINK_WOOL,
]

# Guide lamp posts along the shore strip.
GUIDE_POSTS = [5820, 5844, 5868, 5894]


def _hanging_lantern(
    fills: list[Fill],
    label: str,
    x: int,
    z: int,
    y: int,
    shade: str,
) -> None:
    """One hanging lantern: SEA_LANTERN core at y, shade block above."""
    add_fill(fills, f"{label} core", (x, y, z), (x, y, z), M.SEA_LANTERN)
    add_fill(fills, f"{label} shade", (x, y + 1, z), (x, y + 1, z), shade)


def _mooring_pile(fills: list[Fill], label: str, x: int, z: int) -> None:
    """Timber mooring pile rising out of the water beside a boat."""
    add_fill(fills, f"{label} pile", (x, WATER_Y, z), (x, WATER_Y + 2, z), M.LOG)


def _feast_boat(fills: list[Fill]) -> None:
    """Section 1 - the grand banquet lantern boat (主宴灯船, 24x10)."""
    mx = (FEAST_X1 + FEAST_X2) // 2
    # Hull and raised gunwale.
    add_fill(fills, "qjnight feast hull", (FEAST_X1, WATER_Y, FEAST_Z1), (FEAST_X2, WATER_Y + 1, FEAST_Z2), M.WOOD)
    add_outline(fills, "qjnight feast gunwale", FEAST_X1, FEAST_Z1, FEAST_X2, FEAST_Z2, WATER_Y + 2, WATER_Y + 2, M.LOG)
    # Bow hull extension and raised stern deck.
    add_fill(fills, "qjnight feast bow hull", (FEAST_X2 + 1, WATER_Y, FEAST_Z1 + 1), (FEAST_X2 + 6, WATER_Y + 1, FEAST_Z2 - 1), M.WOOD)
    add_fill(fills, "qjnight feast stern deck", (FEAST_X1 - 3, WATER_Y, FEAST_Z1 + 2), (FEAST_X1 - 1, WATER_Y + 2, FEAST_Z2 - 2), M.WOOD)
    # Deck lanterns set into the gunwale.
    add_fill(fills, "qjnight feast deck lamp n", (mx, WATER_Y + 2, FEAST_Z1 - 1), (mx, WATER_Y + 2, FEAST_Z1 - 1), M.SEA_LANTERN)
    add_fill(fills, "qjnight feast deck lamp s", (mx, WATER_Y + 2, FEAST_Z2 + 1), (mx, WATER_Y + 2, FEAST_Z2 + 1), M.SEA_LANTERN)
    # Feast deck: red carpet, long banquet table, gold wine vessels.
    add_fill(fills, "qjnight feast carpet", (FEAST_X1 + 4, WATER_Y + 2, FEAST_Z1 + 2), (FEAST_X2 - 4, WATER_Y + 2, FEAST_Z2 - 2), M.RED_WOOL)
    add_fill(fills, "qjnight feast table", (FEAST_X1 + 7, WATER_Y + 3, FEAST_Z1 + 3), (FEAST_X2 - 6, WATER_Y + 3, FEAST_Z2 - 3), M.WOOD)
    for i, vx in enumerate((FEAST_X1 + 9, FEAST_X1 + 12, FEAST_X1 + 15)):
        vz = FEAST_Z1 + 4 + (i % 2)
        add_fill(fills, f"qjnight feast vessel {i}", (vx, WATER_Y + 4, vz), (vx, WATER_Y + 4, vz), M.GOLD)
    # Open canopy (敞棚): six posts and a wide roof with a gold ridge.
    for i, (px, pz) in enumerate([
        (FEAST_X1 + 1, FEAST_Z1 + 1), (FEAST_X1 + 1, FEAST_Z2 - 1),
        (FEAST_X2 - 1, FEAST_Z1 + 1), (FEAST_X2 - 1, FEAST_Z2 - 1),
        (mx, FEAST_Z1 + 1), (mx, FEAST_Z2 - 1),
    ]):
        add_fill(fills, f"qjnight feast post {i}", (px, WATER_Y + 3, pz), (px, WATER_Y + 7, pz), M.LOG)
    add_fill(fills, "qjnight feast roof", (FEAST_X1 - 2, WATER_Y + 8, FEAST_Z1 - 2), (FEAST_X2 + 2, WATER_Y + 8, FEAST_Z2 + 2), M.WOOD)
    add_fill(fills, "qjnight feast roof ridge", (FEAST_X1, WATER_Y + 9, FEAST_Z1 + 3), (FEAST_X2, WATER_Y + 9, FEAST_Z2 - 3), M.GOLD)
    # Lantern ring: 12 lanterns around the canopy eaves, alternating
    # RED_WOOL shade + SEA_LANTERN core.
    ring = [
        (FEAST_X1 + 2, FEAST_Z1 - 1), (FEAST_X1 + 9, FEAST_Z1 - 1),
        (FEAST_X2 - 7, FEAST_Z1 - 1), (FEAST_X2 - 2, FEAST_Z1 - 1),
        (FEAST_X2 - 2, FEAST_Z2 + 1), (FEAST_X2 - 7, FEAST_Z2 + 1),
        (FEAST_X1 + 9, FEAST_Z2 + 1), (FEAST_X1 + 2, FEAST_Z2 + 1),
        (FEAST_X1 - 1, FEAST_Z1 + 2), (FEAST_X1 - 1, FEAST_Z2 - 2),
        (FEAST_X1 - 1, FEAST_Z1 - 1), (FEAST_X1 - 1, FEAST_Z2 + 1),
    ]
    for i, (lx, lz) in enumerate(ring):
        shade = M.RED_WOOL if i % 2 == 0 else M.SEA_LANTERN
        core = M.SEA_LANTERN if i % 2 == 0 else M.RED_WOOL
        add_fill(fills, f"qjnight feast ring shade {i}", (lx, WATER_Y + 7, lz), (lx, WATER_Y + 7, lz), shade)
        add_fill(fills, f"qjnight feast ring core {i}", (lx, WATER_Y + 6, lz), (lx, WATER_Y + 6, lz), core)
    # Bow light tower (船头灯楼): two storeys, balcony, gilded cap.
    add_hollow_box(fills, "qjnight feast tower base", FEAST_X2 + 1, WATER_Y + 2, FEAST_Z1 + 1, FEAST_X2 + 6, WATER_Y + 6, FEAST_Z2 - 1, M.RED_WALL)
    add_outline(fills, "qjnight feast tower balcony", FEAST_X2 + 1, FEAST_Z1 + 1, FEAST_X2 + 6, FEAST_Z2 - 1, WATER_Y + 7, WATER_Y + 7, M.GOLD)
    add_hollow_box(fills, "qjnight feast tower lamp room", FEAST_X2 + 2, WATER_Y + 8, FEAST_Z1 + 2, FEAST_X2 + 5, WATER_Y + 10, FEAST_Z2 - 2, M.RED_WALL)
    add_fill(fills, "qjnight feast tower beacon", (FEAST_X2 + 3, WATER_Y + 9, FEAST_Z1 + 4), (FEAST_X2 + 4, WATER_Y + 9, FEAST_Z1 + 5), M.SEA_LANTERN)
    add_fill(fills, "qjnight feast tower cap", (FEAST_X2 + 1, WATER_Y + 11, FEAST_Z1 + 1), (FEAST_X2 + 6, WATER_Y + 11, FEAST_Z2 - 1), M.GOLD)
    add_fill(fills, "qjnight feast tower finial", (FEAST_X2 + 3, WATER_Y + 12, FEAST_Z1 + 4), (FEAST_X2 + 4, WATER_Y + 12, FEAST_Z1 + 5), M.GOLD)
    # Stern banner and mooring piles.
    add_fill(fills, "qjnight feast flag pole", (FEAST_X1 - 3, WATER_Y + 3, FEAST_Z1 + 4), (FEAST_X1 - 3, WATER_Y + 8, FEAST_Z1 + 4), M.LOG)
    add_fill(fills, "qjnight feast flag cloth", (FEAST_X1 - 3, WATER_Y + 7, FEAST_Z1 + 5), (FEAST_X1 - 3, WATER_Y + 8, FEAST_Z1 + 7), M.RED_WOOL)
    _mooring_pile(fills, "qjnight feast moor w", FEAST_X1 + 4, FEAST_Z2 + 5)
    _mooring_pile(fills, "qjnight feast moor e", FEAST_X2 - 4, FEAST_Z2 + 5)


def _escort_boat(
    fills: list[Fill],
    tag: str,
    x1: int, z1: int, x2: int, z2: int,
    theme: str,
) -> None:
    """Section 2 - one 12x6 escort lantern boat with 6 side lanterns."""
    add_fill(fills, f"qjnight {tag} hull", (x1, WATER_Y, z1), (x2, WATER_Y + 1, z2), M.WOOD)
    add_outline(fills, f"qjnight {tag} gunwale", x1, z1, x2, z2, WATER_Y + 2, WATER_Y + 2, M.LOG)
    # Six side lanterns: three per long side, theme wool over a core.
    mx = (x1 + x2) // 2
    for side, sz in enumerate((z1 - 1, z2 + 1)):
        for j, lx in enumerate((x1 + 2, mx, x2 - 1)):
            _hanging_lantern(fills, f"qjnight {tag} side lamp {side}{j}", lx, sz, WATER_Y + 2, theme)
    # Central lamp mast with lantern and theme cap.
    add_fill(fills, f"qjnight {tag} mast", (mx, WATER_Y + 2, z1 + 2), (mx + 1, WATER_Y + 5, z1 + 3), M.LOG)
    add_fill(fills, f"qjnight {tag} mast lamp", (mx, WATER_Y + 6, z1 + 2), (mx + 1, WATER_Y + 6, z1 + 3), M.SEA_LANTERN)
    add_fill(fills, f"qjnight {tag} mast cap", (mx, WATER_Y + 7, z1 + 2), (mx + 1, WATER_Y + 7, z1 + 3), theme)
    # Bow theme accent and mooring piles.
    add_fill(fills, f"qjnight {tag} bow", (x2, WATER_Y + 2, z1 + 2), (x2, WATER_Y + 3, z1 + 3), theme)
    _mooring_pile(fills, f"qjnight {tag} moor w", x1 - 2, z1 + 2)
    _mooring_pile(fills, f"qjnight {tag} moor e", x2 + 2, z1 + 2)


def _river_lamps(fills: list[Fill]) -> None:
    """Section 3 - 24 drifting river lamps (河灯) on the pool."""
    for i, (lx, lz) in enumerate(RIVER_LAMPS):
        add_fill(fills, f"qjnight river lamp {i} pad", (lx, WATER_Y, lz), (lx, WATER_Y, lz), "minecraft:lily_pad")
        add_fill(fills, f"qjnight river lamp {i} flame", (lx, WATER_Y + 1, lz), (lx, WATER_Y + 1, lz), LAMP_FLAME[i % 3])


def _lamp_frames(fills: list[Fill]) -> None:
    """Section 4 - two water lamp frames standing in the pool."""
    for fi, (fx1, fx2, fz, shade) in enumerate(FRAME_LINES):
        for pi, px in enumerate((fx1, fx2)):
            add_fill(fills, f"qjnight frame {fi} base {pi}", (px, WATER_Y - 1, fz), (px, WATER_Y - 1, fz), M.STONE)
            add_fill(fills, f"qjnight frame {fi} post {pi}", (px, WATER_Y, fz), (px, WATER_Y + 5, fz), M.FENCE)
        add_fill(fills, f"qjnight frame {fi} bar", (fx1 + 1, WATER_Y + 5, fz), (fx2 - 1, WATER_Y + 5, fz), M.FENCE)
        for li, lx in enumerate((fx1 + 2, fx1 + 4, fx2 - 4, fx2 - 2)):
            _hanging_lantern(fills, f"qjnight frame {fi} lamp {li}", lx, fz, WATER_Y + 3, shade)


def _banquet_tents(fills: list[Fill]) -> None:
    """Section 5 - three night banquet tents (夜宴帐) on the north shore."""
    for ti, cx in enumerate(TENT_CENTRES):
        x1, x2 = cx - 6, cx + 6
        # Stone platform and timber floor (shore ground levelling).
        add_fill(fills, f"qjnight tent {ti} platform", (x1, 1, TENT_Z1), (x2, 2, TENT_Z2), M.STONE)
        add_fill(fills, f"qjnight tent {ti} floor", (x1, 3, TENT_Z1), (x2, 3, TENT_Z2), M.WOOD)
        # Timber skeleton: corner and mid posts.
        posts = [
            (x1, TENT_Z1), (x2, TENT_Z1), (x1, TENT_Z2), (x2, TENT_Z2),
            (cx, TENT_Z1), (cx, TENT_Z2),
        ]
        for pi, (px, pz) in enumerate(posts):
            add_fill(fills, f"qjnight tent {ti} post {pi}", (px, 4, pz), (px, 7, pz), M.LOG)
        # Deep-blue wool night-sky roof, three stepped layers + finial.
        add_fill(fills, f"qjnight tent {ti} roof 0", (x1, 8, TENT_Z1), (x2, 8, TENT_Z2), M.BLUE_WOOL)
        add_fill(fills, f"qjnight tent {ti} roof 1", (x1 + 1, 9, TENT_Z1 + 1), (x2 - 1, 9, TENT_Z2 - 1), M.BLUE_WOOL)
        add_fill(fills, f"qjnight tent {ti} roof 2", (x1 + 2, 10, TENT_Z1 + 2), (x2 - 2, 10, TENT_Z2 - 2), M.BLUE_WOOL)
        add_fill(fills, f"qjnight tent {ti} finial", (cx, 11, 5308), (cx, 11, 5308), M.GOLD)
        # Inner lamp table with gold vessels and a hanging lamp.
        add_fill(fills, f"qjnight tent {ti} table", (cx - 4, 4, 5307), (cx + 1, 4, 5309), M.WOOD)
        add_fill(fills, f"qjnight tent {ti} vessel a", (cx - 3, 5, 5307), (cx - 3, 5, 5307), M.GOLD)
        add_fill(fills, f"qjnight tent {ti} vessel b", (cx - 1, 5, 5309), (cx - 1, 5, 5309), M.GOLD)
        add_fill(fills, f"qjnight tent {ti} lamp", (cx - 2, 7, 5308), (cx - 2, 7, 5308), M.SEA_LANTERN)
        # Outer wind lantern on the pool-facing south side.
        add_fill(fills, f"qjnight tent {ti} wind post", (cx, 4, TENT_Z2 + 3), (cx, 6, TENT_Z2 + 3), M.LOG)
        add_fill(fills, f"qjnight tent {ti} wind lamp", (cx, 7, TENT_Z2 + 3), (cx, 7, TENT_Z2 + 3), M.SEA_LANTERN)
        add_fill(fills, f"qjnight tent {ti} wind shade", (cx, 8, TENT_Z2 + 3), (cx, 8, TENT_Z2 + 3), M.RED_WOOL)
        # Landing pier stepping into the pool.
        add_fill(fills, f"qjnight pier {ti} deck", (cx - 2, 2, 5318), (cx + 2, 2, 5322), M.WOOD)
        add_fill(fills, f"qjnight pier {ti} pile w", (cx - 2, WATER_Y - 1, 5322), (cx - 2, WATER_Y, 5322), M.LOG)
        add_fill(fills, f"qjnight pier {ti} pile e", (cx + 2, WATER_Y - 1, 5322), (cx + 2, WATER_Y, 5322), M.LOG)


def _riddle_wall(fills: list[Fill]) -> None:
    """Section 6 - lantern-riddle wall (灯谜墙) with 8 riddle strips."""
    add_fill(fills, "qjnight wall base", (WALL_X1 - 1, 0, WALL_Z - 2), (WALL_X2 + 1, 2, WALL_Z + 2), M.STONE)
    add_fill(fills, "qjnight wall face", (WALL_X1, 3, WALL_Z), (WALL_X2, 7, WALL_Z), M.WHITE_TERRACOTTA)
    add_fill(fills, "qjnight wall cap", (WALL_X1 - 1, 8, WALL_Z - 1), (WALL_X2 + 1, 8, WALL_Z + 1), M.DARK)
    # Eight coloured riddle strips hung on the pool-facing face.
    for i, color in enumerate(RIDDLE_COLORS):
        rx = WALL_X1 + 1 + i
        add_fill(fills, f"qjnight riddle strip {i}", (rx, 5, WALL_Z + 1), (rx, 6, WALL_Z + 1), color)
    # Festival flag poles flanking the wall.
    for fi, (fx, flag) in enumerate([(WALL_X1 - 4, M.RED_WOOL), (WALL_X2 + 4, M.YELLOW_WOOL)]):
        add_fill(fills, f"qjnight wall flag pole {fi}", (fx, 3, WALL_Z + 1), (fx, 9, WALL_Z + 1), M.LOG)
        add_fill(fills, f"qjnight wall flag cloth {fi}", (fx, 7, WALL_Z + 2), (fx, 8, WALL_Z + 3), flag)


def _guide_posts(fills: list[Fill]) -> None:
    """Section 7 - four shore guide lamp posts (导引灯柱)."""
    for gi, px in enumerate(GUIDE_POSTS):
        add_fill(fills, f"qjnight guide {gi} base", (px, 1, 5308), (px + 1, 2, 5309), M.STONE)
        add_fill(fills, f"qjnight guide {gi} shaft", (px, 3, 5308), (px + 1, 8, 5309), M.LOG)
        add_fill(fills, f"qjnight guide {gi} lamp", (px, 9, 5308), (px + 1, 10, 5309), M.SEA_LANTERN)
        add_fill(fills, f"qjnight guide {gi} cap", (px, 11, 5308), (px + 1, 11, 5309), M.RED_WOOL)


def build_qujiang_night_3d(fills: list[Fill]) -> None:
    # 1. Grand banquet lantern boat in the north-east open water.
    _feast_boat(fills)
    # 2. Two escort lantern boats: scarlet and gilded themes.
    _escort_boat(fills, "red boat", RED_X1, RED_Z1, RED_X2, RED_Z2, M.RED_WOOL)
    _escort_boat(fills, "gold boat", GOLD_X1, GOLD_Z1, GOLD_X2, GOLD_Z2, M.YELLOW_WOOL)
    # 3. Twenty-four drifting river lamps.
    _river_lamps(fills)
    # 4. Two water lamp frames standing in the pool.
    _lamp_frames(fills)
    # 5. North-shore night banquet tents with landing piers.
    _banquet_tents(fills)
    # 6. Lantern-riddle wall with hanging riddle strips.
    _riddle_wall(fills)
    # 7. Shore guide lamp posts.
    _guide_posts(fills)


def main() -> None:
    run_builder(build_qujiang_night_3d, "qujiang_night_3d")


if __name__ == "__main__":
    main()
