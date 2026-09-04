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
    add_pyramid_roof,
    add_ridge_roof,
    add_tree,
    run_builder,
)


"""
Jinzouyuan Compound Group (进奏院群·藩镇驻京办) 3D module - the lane of
provincial liaison offices that the military governors of the various dao
kept in Chang'an after the An Lushan rebellion: part tribute embassy, part
residence for the governors' delegates in the capital, and the busiest
intelligence exchange of the empire (every report, bribe and memorial
between the provinces and the court passed through these six courtyards).

Location in Chang'an city local coordinates:
    Plot: x 2450..2750, z 1750..2050 (strict bounds - nothing may leave
    them; nothing may reach past x 2800 where the Zhuque Avenue watchtowers
    stand, and the West Market lies far west at x <= 1800; the pre-tiled
    ward housing around the plot is deliberately overwritten). Ground is
    graded to stone y0..1 + grass y2..3 (walking surface y4); the main
    structures rise from y5. An east-west lane ("进奏院巷", z 1880..1910,
    andesite paving) runs the full width of the plot; the six courtyards
    face it in two rows of three - the Hezhong / Hedong / Jinnan
    (河中/河东/剑南) envoys on the north row with south-facing gates, and
    the Huainan / Shannan / Longyou (淮南/山南/陇右) envoys on the south
    row with north-facing gates.

Distinctive features:
    - Six uniform 60x60 liaison courtyards, identical in layout yet each
      identified by its own dao: gate tower with a narrow gold name plaque
      (门匾) and twin dao banners (道旗: dark-oak pole plus a three-segment
      wool flag in the dao colour), a document hall (文书堂) with a large
      desk, lectern and bookshelf wall, a dorm wing (寝居) with bed and
      luggage chest, and a small inner court with a stone well or a tree
    - Shared tribute screen wall (照壁) in the middle of the lane: white
      body on a dark plinth and cap, with a "Four Quarters Tribute Map"
      (四方朝贡图) on both faces - four corner wool medallions, thin
      iron-bar routes converging on a gold node marking Chang'an
    - Courier stable (驿传马厩) at the west end of the lane: four
      fence-stall bays with mangers, a long water trough, hay piles and
      four hitching posts shared by the courtyards' post horses
    - Records room (文牍房) at the east end of the lane: long desk, two
      rows of archive chests, a bookshelf wall and a glowing charcoal
      brazier (炭盆)
    - Watch tower (谯楼) in the south-east corner: doorway passage below,
      iron-bar peep windows on all four faces above, a glazed pyramid roof
      (攒尖顶) with a gold apex and a sea-lantern beacon for the nightly
      "all quiet" fire signal
    - Lantern line along the lane and twin locust trees at its ends
"""

# ---------------------------------------------------------------------------
# Site: east-of-Zhuque-Avenue liaison-office plot (strict bounds).
# ---------------------------------------------------------------------------
SITE_X1, SITE_X2 = 2450, 2750
SITE_Z1, SITE_Z2 = 1750, 2050

# The east-west lane ("进奏院巷") and the six courtyard rows.
LANE_Z1, LANE_Z2 = 1880, 1910
CY_SIZE = 60
CY_X = (2465, 2570, 2675)
CY_Z_NORTH = 1770  # north row; gates open south onto the lane
CY_Z_SOUTH = 1960  # south row; gates open north onto the lane

# Shared screen wall mid-lane (四方朝贡图照壁).
SW_X1, SW_X2 = 2572, 2640
SW_Z1, SW_Z2 = 1892, 1895

# Courier stable (west end of the lane) and records room (east end).
STB_X1, STB_Z1, STB_X2, STB_Z2 = 2455, 1915, 2545, 1955
DOC_X1, DOC_Z1, DOC_X2, DOC_Z2 = 2660, 1916, 2740, 1952

# Watch tower (谯楼) in the south-east corner of the plot.
WT_X1, WT_Z1, WT_X2, WT_Z2 = 2731, 2033, 2743, 2045
WT_CX, WT_CZ = 2737, 2039

HAY = "minecraft:hay_block"
CHEST_E = "minecraft:chest[facing=east]"
CHEST_W = "minecraft:chest[facing=west]"
LECTERN_N = "minecraft:lectern[facing=north]"
LECTERN_S = "minecraft:lectern[facing=south]"
LOG_X = "minecraft:dark_oak_log[axis=x]"
BOOKSHELF = "minecraft:bookshelf"

# Six dao banners: three courtyards per row, west to east.
_DAOS_NORTH = (
    ("hezhong", M.RED_WOOL),
    ("hedong", M.BLUE_WOOL),
    ("jinnan", M.GREEN_WOOL),
)
_DAOS_SOUTH = (
    ("huainan", M.YELLOW_WOOL),
    ("shannan", M.WHITE_WOOL),
    ("longyou", M.PINK_WOOL),
)

_ROOF_STAIRS = {
    M.ROOF_GREEN: "minecraft:dark_prismarine_stairs",
    M.ROOF_BLUE: "minecraft:prismarine_brick_stairs",
    M.ROOF_DARK: "minecraft:deepslate_tile_stairs",
}


# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------
def _stair(roof_block: str, facing: str) -> str:
    """Directional stair state matching lib's roof-block conventions."""
    stair_id = _ROOF_STAIRS.get(roof_block, _ROOF_STAIRS[M.ROOF_DARK])
    return f"{stair_id}[facing={facing},half=bottom,shape=straight,waterlogged=false]"


def _gable_roof(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y: int,
    axis: str = "x",
    roof_block: str = M.ROOF_DARK,
) -> None:
    """Compact hand-stepped gable: two stair slopes per layer plus a ridge.

    axis 'x' = ridge runs east-west (slopes step in from north/south);
    axis 'z' = ridge runs north-south (slopes step in from west/east).
    """
    if axis == "x":
        layers = min(3, (z2 - z1) // 2)
        for i in range(layers):
            add_fill(fills, f"{label} n {i}", (x1, y + i, z1 + i), (x2, y + i, z1 + i), _stair(roof_block, "south"))
            add_fill(fills, f"{label} s {i}", (x1, y + i, z2 - i), (x2, y + i, z2 - i), _stair(roof_block, "north"))
        add_fill(fills, f"{label} ridge", (x1 + 1, y + layers, z1 + layers), (x2 - 1, y + layers, z2 - layers), roof_block)
    else:
        layers = min(3, (x2 - x1) // 2)
        for i in range(layers):
            add_fill(fills, f"{label} w {i}", (x1 + i, y + i, z1), (x1 + i, y + i, z2), _stair(roof_block, "east"))
            add_fill(fills, f"{label} e {i}", (x2 - i, y + i, z1), (x2 - i, y + i, z2), _stair(roof_block, "west"))
        add_fill(fills, f"{label} ridge", (x1 + layers, y + layers, z1 + 1), (x2 - layers, y + layers, z2 - 1), roof_block)


def _courtyard(
    fills: list[Fill],
    label: str,
    x1: int,
    z1: int,
    banner_wool: str,
    gate_on_south: bool,
    court_well: bool,
) -> None:
    """One dao liaison courtyard: enclosure wall, gate tower with gold
    plaque and twin dao banners, document hall, dorm wing and a small
    well/tree inner court. All six share this exact layout.
    """
    x2 = x1 + CY_SIZE
    z2 = z1 + CY_SIZE
    cx = x1 + CY_SIZE // 2
    if gate_on_south:
        gz = z2          # wall row carrying the gate
        out = 1          # lane-side direction
        hz1, hz2 = z1 + 2, z1 + 13   # document hall at the back
        fz = hz2                     # hall front (door) face
        iz = hz1 + 1                 # hall back-wall interior face
        dz1, dz2 = hz1 + 4, hz1 + 7  # desk footprint
        wz1, wz2 = z1 + 18, z1 + 42  # dorm wing
        tz1, tz2 = z1 + 20, z1 + 30  # small inner court
        lectern = LECTERN_S
    else:
        gz = z1
        out = -1
        hz1, hz2 = z2 - 13, z2 - 2
        fz = hz1
        iz = hz2 - 1
        dz1, dz2 = hz2 - 7, hz2 - 4
        wz1, wz2 = z2 - 42, z2 - 18
        tz1, tz2 = z2 - 30, z2 - 20
        lectern = LECTERN_N

    # Enclosure wall: white rammed earth, six tall.
    add_outline(fills, f"{label} wall", x1, z1, x2, z2, 4, 9, M.WHITE_TERRACOTTA, thickness=1)

    # Gate bay: carved opening framed by dark piers, timber lintel, gold
    # name plaque (门匾) on the lane face, small dark gable over it.
    add_fill(fills, f"{label} gate opening", (cx - 3, 4, gz), (cx + 3, 7, gz), M.AIR)
    add_fill(fills, f"{label} gate pier w", (cx - 5, 4, gz - 1), (cx - 4, 11, gz + 1), M.DARK)
    add_fill(fills, f"{label} gate pier e", (cx + 4, 4, gz - 1), (cx + 5, 11, gz + 1), M.DARK)
    add_fill(fills, f"{label} gate panel", (cx - 3, 10, gz), (cx + 3, 10, gz), M.WHITE_TERRACOTTA)
    add_fill(fills, f"{label} gate lintel", (cx - 5, 11, gz), (cx + 5, 11, gz), LOG_X)
    add_fill(fills, f"{label} gate plaque", (cx - 3, 9, gz + out), (cx + 3, 10, gz + out), M.GOLD)
    add_fill(fills, f"{label} gate roof n", (cx - 6, 12, gz - 1), (cx + 6, 12, gz - 1), _stair(M.ROOF_DARK, "south"))
    add_fill(fills, f"{label} gate roof s", (cx - 6, 12, gz + 1), (cx + 6, 12, gz + 1), _stair(M.ROOF_DARK, "north"))
    add_fill(fills, f"{label} gate ridge", (cx - 6, 13, gz), (cx + 6, 13, gz), M.ROOF_DARK)

    # Twin dao banners (道旗): log poles flanking the gate on the lane
    # side, each flying a three-segment wool flag in the dao colour.
    banner_z = gz + 3 * out
    for side, bx in ((-1, cx - 10), (1, cx + 10)):
        add_fill(fills, f"{label} banner pole {side}", (bx, 4, banner_z), (bx, 9, banner_z), M.LOG)
        add_fill(fills, f"{label} banner flag {side}", (bx + side, 10, banner_z), (bx + side, 12, banner_z), banner_wool)

    # Path from the gate to the hall door.
    add_fill(fills, f"{label} path", (cx - 2, 3, min(gz, fz)), (cx + 2, 3, max(gz, fz)), M.ANDESITE)

    # Document hall (文书堂) across the back: red walls, wood floor, desk
    # with lectern, and a bookshelf wall of dossiers.
    add_fill(fills, f"{label} hall floor", (cx - 14, 4, hz1 + 1), (cx + 14, 4, hz2 - 1), M.WOOD)
    add_hollow_box(fills, f"{label} hall", cx - 15, 5, hz1, cx + 15, 10, hz2, M.RED_WALL, thickness=1)
    add_fill(fills, f"{label} hall floor air", (cx - 14, 5, hz1 + 1), (cx + 14, 5, hz2 - 1), M.AIR)
    add_fill(fills, f"{label} hall door", (cx - 3, 5, fz), (cx + 3, 7, fz), M.AIR)
    add_fill(fills, f"{label} hall window", (cx - 11, 7, fz), (cx - 6, 9, fz), M.GLASS)
    add_fill(fills, f"{label} hall shelves", (cx - 12, 5, iz), (cx - 2, 7, iz), BOOKSHELF)
    add_fill(fills, f"{label} hall desk base", (cx + 3, 5, dz1), (cx + 13, 5, dz2), M.LOG)
    add_fill(fills, f"{label} hall desk top", (cx + 3, 6, dz1), (cx + 13, 6, dz2), M.WOOD)
    add_fill(fills, f"{label} hall lectern", (cx + 8, 5, fz - 3 * out), (cx + 8, 5, fz - 3 * out), lectern)
    _gable_roof(fills, f"{label} hall roof", cx - 15, hz1, cx + 15, hz2, 11, axis="x")

    # Dorm wing (寝居) along the west wall: bed with red blanket, luggage
    # chest, door and gable roof.
    wx1, wx2 = x1 + 2, x1 + 13
    add_fill(fills, f"{label} wing floor", (wx1 + 1, 4, wz1 + 1), (wx2 - 1, 4, wz2 - 1), M.WOOD)
    add_hollow_box(fills, f"{label} wing", wx1, 5, wz1, wx2, 8, wz2, M.WHITE_TERRACOTTA, thickness=1)
    add_fill(fills, f"{label} wing floor air", (wx1 + 1, 5, wz1 + 1), (wx2 - 1, 5, wz2 - 1), M.AIR)
    mz = (wz1 + wz2) // 2
    add_fill(fills, f"{label} wing door", (wx2, 5, mz - 1), (wx2, 7, mz + 1), M.AIR)
    add_fill(fills, f"{label} wing window", (wx2, 6, wz1 + 4), (wx2, 7, wz1 + 8), M.GLASS)
    add_fill(fills, f"{label} wing bed", (wx1 + 2, 5, wz1 + 3), (wx1 + 4, 5, wz1 + 8), M.WOOD)
    add_fill(fills, f"{label} wing blanket", (wx1 + 2, 6, wz1 + 4), (wx1 + 3, 6, wz1 + 8), M.RED_WOOL)
    add_fill(fills, f"{label} wing pillow", (wx1 + 4, 6, wz1 + 3), (wx1 + 4, 6, wz1 + 3), M.WHITE_WOOL)
    add_fill(fills, f"{label} wing chest", (wx1 + 2, 5, wz2 - 3), (wx1 + 3, 6, wz2 - 3), CHEST_E)
    _gable_roof(fills, f"{label} wing roof", wx1, wz1, wx2, wz2, 9, axis="z")

    # Small inner court (小天井): a stone well or a tree.
    twx = cx + 10
    twz = (tz1 + tz2) // 2
    if court_well:
        add_outline(fills, f"{label} well curb", twx - 2, twz - 2, twx + 2, twz + 2, 4, 5, M.STONE, thickness=1)
        add_fill(fills, f"{label} well water", (twx - 1, 2, twz - 1), (twx + 1, 4, twz + 1), M.WATER)
    else:
        add_tree(fills, f"{label} court tree", twx, twz, 4, height=7, spread=2)


# ---------------------------------------------------------------------------
# Main builder.
# ---------------------------------------------------------------------------
def build_jinzouyuan_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site grading and the east-west "进奏院巷" lane.
    # ------------------------------------------------------------------
    add_fill(fills, "jinzou clear site", (SITE_X1, 4, SITE_Z1), (SITE_X2, 7, SITE_Z2), M.AIR)
    add_fill(fills, "jinzou terrace stone", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "jinzou terrace grass", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)
    add_fill(fills, "jinzou lane pave", (SITE_X1, 3, LANE_Z1), (SITE_X2, 3, LANE_Z2), M.ANDESITE)

    # ------------------------------------------------------------------
    # 2. Six liaison courtyards: two rows of three, one dao each, wells
    #    and trees alternating down the lane.
    # ------------------------------------------------------------------
    for i, (name, wool) in enumerate(_DAOS_NORTH):
        _courtyard(fills, f"jinzou cy {name}", CY_X[i], CY_Z_NORTH, wool, True, i % 2 == 0)
    for i, (name, wool) in enumerate(_DAOS_SOUTH):
        _courtyard(fills, f"jinzou cy {name}", CY_X[i], CY_Z_SOUTH, wool, False, (i + 1) % 2 == 0)

    # ------------------------------------------------------------------
    # 3. Shared tribute screen wall (照壁) mid-lane with the "Four
    #    Quarters Tribute Map" on both faces.
    # ------------------------------------------------------------------
    add_fill(fills, "jinzou screen base", (SW_X1, 4, SW_Z1 - 1), (SW_X2, 5, SW_Z2 + 1), M.DARK)
    add_fill(fills, "jinzou screen body", (SW_X1, 6, SW_Z1), (SW_X2, 14, SW_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "jinzou screen cap", (SW_X1 - 2, 15, SW_Z1 - 2), (SW_X2 + 2, 16, SW_Z2 + 2), M.DARK)
    for face, mz in (("n", SW_Z1 - 1), ("s", SW_Z2 + 1)):
        add_fill(fills, f"jinzou map frame {face} top", (2576, 13, mz), (2636, 13, mz), M.DARK)
        add_fill(fills, f"jinzou map frame {face} bottom", (2576, 7, mz), (2636, 7, mz), M.DARK)
        add_fill(fills, f"jinzou map frame {face} w", (2576, 8, mz), (2576, 12, mz), M.DARK)
        add_fill(fills, f"jinzou map frame {face} e", (2636, 8, mz), (2636, 12, mz), M.DARK)
        # Four corner medallions: west white tiger, east azure dragon,
        # south vermilion bird, north dark warrior.
        add_fill(fills, f"jinzou map nw {face}", (2578, 11, mz), (2580, 12, mz), M.WHITE_WOOL)
        add_fill(fills, f"jinzou map ne {face}", (2632, 11, mz), (2634, 12, mz), M.BLUE_WOOL)
        add_fill(fills, f"jinzou map sw {face}", (2578, 8, mz), (2580, 9, mz), M.RED_WOOL)
        add_fill(fills, f"jinzou map se {face}", (2632, 8, mz), (2634, 9, mz), M.GREEN_WOOL)
        # Thin iron-bar routes from the corners to the gold Chang'an node.
        add_fill(fills, f"jinzou map route h {face}", (2580, 10, mz), (2632, 10, mz), M.IRON_BARS)
        add_fill(fills, f"jinzou map route v w {face}", (2579, 9, mz), (2579, 11, mz), M.IRON_BARS)
        add_fill(fills, f"jinzou map route v e {face}", (2633, 9, mz), (2633, 11, mz), M.IRON_BARS)
        add_fill(fills, f"jinzou map changan {face}", (2604, 10, mz), (2608, 10, mz), M.GOLD)

    # ------------------------------------------------------------------
    # 4. Courier stable (驿传马厩) at the west end: hay roof, four fence
    #    stalls with mangers, water trough, hay piles and hitching posts.
    # ------------------------------------------------------------------
    add_fill(fills, "jinzou stable pave", (STB_X1, 3, STB_Z1), (STB_X2, 3, STB_Z2), M.ANDESITE)
    add_fill(fills, "jinzou stable back wall", (STB_X1, 4, 1954), (STB_X2, 8, 1955), M.WOOD)
    add_fill(fills, "jinzou stable end w", (STB_X1, 4, 1917), (STB_X1 + 1, 8, 1953), M.WOOD)
    add_fill(fills, "jinzou stable end e", (STB_X2 - 1, 4, 1917), (STB_X2, 8, 1953), M.WOOD)
    for px in (2475, 2495, 2515, 2535):
        add_fill(fills, f"jinzou stable post {px}", (px, 4, 1917), (px + 1, 8, 1918), M.LOG)
    add_fill(fills, "jinzou stable beam", (STB_X1, 9, 1917), (STB_X2, 9, 1918), LOG_X)
    add_fill(fills, "jinzou stable roof", (STB_X1 - 2, 10, STB_Z1), (STB_X2 + 2, 10, STB_Z2 + 1), HAY)
    for dx in (2477, 2499, 2521):
        add_fill(fills, f"jinzou stall divider {dx}", (dx, 4, 1919), (dx, 8, 1953), M.FENCE)
    for si, (a, b) in enumerate(((2458, 2475), (2479, 2497), (2501, 2519), (2523, 2541))):
        add_fill(fills, f"jinzou stall manger {si}", (a, 4, 1921), (b, 5, 1921), M.FENCE)
    add_fill(fills, "jinzou stall hay w", (2460, 4, 1948), (2463, 5, 1951), HAY)
    add_fill(fills, "jinzou stall hay e", (2535, 4, 1948), (2538, 5, 1951), HAY)
    add_fill(fills, "jinzou trough", (2459, 4, 1944), (2541, 4, 1946), M.SMOOTH)
    add_fill(fills, "jinzou trough water", (2460, 4, 1945), (2540, 4, 1945), M.WATER)
    for hx in (2465, 2485, 2505, 2525):
        add_fill(fills, f"jinzou hitch post {hx}", (hx, 4, STB_Z1 - 3), (hx, 7, STB_Z1 - 3), M.FENCE)

    # ------------------------------------------------------------------
    # 5. Records room (文牍房) at the east end: long desk, two rows of
    #    archive chests, bookshelf wall and a charcoal brazier.
    # ------------------------------------------------------------------
    add_fill(fills, "jinzou doc floor", (DOC_X1 + 1, 4, DOC_Z1 + 1), (DOC_X2 - 1, 4, DOC_Z2 - 1), M.WOOD)
    add_hollow_box(fills, "jinzou doc", DOC_X1, 5, DOC_Z1, DOC_X2, 10, DOC_Z2, M.RED_WALL, thickness=1)
    add_fill(fills, "jinzou doc floor air", (DOC_X1 + 1, 5, DOC_Z1 + 1), (DOC_X2 - 1, 5, DOC_Z2 - 1), M.AIR)
    add_fill(fills, "jinzou doc door", (2694, 5, DOC_Z1), (2706, 8, DOC_Z1), M.AIR)
    add_fill(fills, "jinzou doc window w", (2670, 7, DOC_Z1), (2686, 9, DOC_Z1), M.GLASS)
    add_fill(fills, "jinzou doc window e", (2714, 7, DOC_Z1), (2730, 9, DOC_Z1), M.GLASS)
    add_ridge_roof(fills, "jinzou doc roof", DOC_X1 - 2, DOC_Z1 - 2, DOC_X2 + 2, DOC_Z2 + 2, 11,
                   layers=2, ridge_axis="x", roof_block=M.ROOF_DARK, ridge_block=M.GOLD)
    add_fill(fills, "jinzou doc desk base", (2668, 5, 1940), (2700, 5, 1944), M.LOG)
    add_fill(fills, "jinzou doc desk top", (2668, 6, 1940), (2700, 6, 1944), M.WOOD)
    add_fill(fills, "jinzou doc chests r1", (2706, 5, 1922), (2736, 6, 1922), CHEST_W)
    add_fill(fills, "jinzou doc chests r2", (2706, 5, 1926), (2736, 6, 1926), CHEST_W)
    add_fill(fills, "jinzou doc shelves", (DOC_X1 + 4, 5, 1922), (DOC_X1 + 5, 8, 1938), BOOKSHELF)
    add_fill(fills, "jinzou doc brazier", (2700, 5, 1948), (2702, 5, 1950), M.SMOOTH)
    add_fill(fills, "jinzou doc brazier coal", (2701, 5, 1949), (2701, 5, 1949), M.LANTERN)

    # ------------------------------------------------------------------
    # 6. Watch tower (谯楼) in the south-east corner: doorway passage,
    #    iron-bar peep windows, glazed pyramid roof with a gold apex and
    #    a beacon core for the nightly "all quiet" signal.
    # ------------------------------------------------------------------
    add_fill(fills, "jinzou tower plinth", (WT_X1 - 2, 4, WT_Z1 - 2), (WT_X2 + 2, 4, WT_Z2 + 2), M.STONE)
    add_hollow_box(fills, "jinzou tower lower", WT_X1, 5, WT_Z1, WT_X2, 9, WT_Z2, M.WHITE_TERRACOTTA, thickness=1)
    add_fill(fills, "jinzou tower door", (2734, 5, WT_Z1), (2740, 8, WT_Z1), M.AIR)
    add_hollow_box(fills, "jinzou tower upper", 2732, 10, 2034, 2742, 13, 2044, M.RED_WALL, thickness=1)
    add_fill(fills, "jinzou tower bars n", (2732, 11, 2034), (2742, 12, 2034), M.IRON_BARS)
    add_fill(fills, "jinzou tower bars s", (2732, 11, 2044), (2742, 12, 2044), M.IRON_BARS)
    add_fill(fills, "jinzou tower bars w", (2732, 11, 2035), (2732, 12, 2043), M.IRON_BARS)
    add_fill(fills, "jinzou tower bars e", (2742, 11, 2035), (2742, 12, 2043), M.IRON_BARS)
    add_fill(fills, "jinzou tower beacon", (2735, 11, 2037), (2739, 12, 2041), M.SEA_LANTERN)
    add_pyramid_roof(fills, "jinzou tower roof", WT_CX, WT_CZ, radius=6, y=14,
                     roof_block=M.ROOF_GREEN, apex_block=M.GOLD)

    # ------------------------------------------------------------------
    # 7. Lane lamp line and twin locust trees (槐树).
    # ------------------------------------------------------------------
    add_lantern_line(fills, "jinzou lane lamp", 2462, 1884, 2738, 1884, 4, every=50)
    add_tree(fills, "jinzou locust w", 2470, 1873, 4, height=8, spread=3)
    add_tree(fills, "jinzou locust e", 2730, 1873, 4, height=8, spread=3)


def main() -> None:
    run_builder(build_jinzouyuan_3d, "jinzouyuan_3d")


if __name__ == "__main__":
    main()
