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
    add_fill,
    add_hollow_box,
    add_lantern_line,
    add_outline,
    add_platform_with_steps,
    add_pool,
    add_pyramid_roof,
    add_ridge_roof,
    add_tree,
    run_builder,
)


"""
Hanlin Academy - Academy of Scholarly Awaiters (翰林院·学士待诏) - the quiet
scholarly office west of Zichen Hall in the Daming Palace, where Li Bai
served as a Hanlin scholar-in-waiting (待诏) drafting court poems and
documents for the emperor.

Location in Chang'an city local coordinates:
    Plot: x 2170..2340, z 5010..5180, west of Zichen Hall (紫宸殿,
    x 2360-2620 / from z 5200), north of Linde Hall (麟德殿, x 1970-2630 /
    from z 5210) and east of the Forest of Steles (碑林, x <=2150, z <=5150).
    All construction is kept inside x 2172..2338, z 5012..5178 so none of
    the neighbouring buildings is touched. Ground y 0..4, main masses
    rise from y 5.

Distinctive features:
    - Graded platform (stone y0..1, lawn y2..3) ringed by a white wall with
      a south chuihua gate (垂花门): beam, hanging pendant columns and a
      small gable roof astride the entry passage
    - Scholars' study court (学士值房): east and west wings plus a north
      main study, each on its own stepped platform with red walls and an
      overhanging gable roof (悬山顶); interiors fitted with bookshelf
      walls, wood desks with quartz paperweights, lecterns and candle
      lanterns; the main study is a walk-through hall (穿堂) linking the
      courtyards
    - Duty court (待诏直院), the deepest yard: one duty room, a north-facing
      open-view gazebo (望亭) with two red columns and a gilded pyramid
      roof gazing toward the palace, and a smooth-stone chess table set
      with black and white wool stones
    - Two-storey book pavilion (藏书小阁) used as the second gate hall:
      ground floor ringed by three-tier bookshelf walls, cantilevered
      upper gallery with fence railings, a shelf-lined upper study and a
      blue-glazed gable roof
    - Painting hall (画案院): open colonnade studio with a long painting
      table laid with white-wool paper, a fence-and-log brush rack with
      hanging brushes, wool pigment dishes and ink barrels
    - Bamboo-and-plum garden (竹影梅枝庭院) entered through a round moon
      gate (月洞门): leaf-column bamboo groves and two pink-blossom plum
      trees
    - Winding pool (曲水小池) with staggered smooth-stone stepping stones
    - Stone axial causeway with lantern posts linking the three courts
"""


# ---------------------------------------------------------------------------
# Site constants (local Chang'an coordinates; world = +9000/+64/+9000 via lib).
# All construction stays inside x 2172..2338, z 5012..5178.
# ---------------------------------------------------------------------------
SITE_X1, SITE_Z1 = 2170, 5010
SITE_X2, SITE_Z2 = 2340, 5180
WALL_X1, WALL_Z1 = 2172, 5012
WALL_X2, WALL_Z2 = 2338, 5178

AXIS_X = 2254
PATH_X1, PATH_X2 = 2248, 2260

# Painting hall (画堂) in the south court.
HALL_X1, HALL_Z1 = 2208, 5112
HALL_X2, HALL_Z2 = 2300, 5152

# Book pavilion (藏书小阁) between the south and middle courts.
PAV_X1, PAV_Z1 = 2226, 5086
PAV_X2, PAV_Z2 = 2282, 5110

# Scholars' study court (学士值房): north study + two wings.
STUDY_N_X1, STUDY_N_Z1 = 2226, 5046
STUDY_N_X2, STUDY_N_Z2 = 2282, 5062
WING_W_X1, WING_W_Z1 = 2186, 5050
WING_W_X2, WING_W_Z2 = 2216, 5076
WING_E_X1, WING_E_Z1 = 2292, 5050
WING_E_X2, WING_E_Z2 = 2322, 5076

# Duty court (待诏直院): duty room + north-facing gazebo.
DUTY_X1, DUTY_Z1 = 2186, 5018
DUTY_X2, DUTY_Z2 = 2222, 5034
GAZEBO_CX, GAZEBO_CZ = AXIS_X, 5026

# Bamboo-and-plum garden (west strip) and winding pool (east strip).
GARDEN_X2 = 2217
POOL_R1_X1, POOL_R1_Z1 = 2304, 5118
POOL_R1_X2, POOL_R1_Z2 = 2326, 5134
POOL_R2_X1, POOL_R2_Z1 = 2310, 5135
POOL_R2_X2, POOL_R2_Z2 = 2330, 5150


def _lantern_post(fills: list[Fill], label: str, x: int, z: int, y: int = 4) -> None:
    """One courtyard lantern: dark-oak post with a sea-lantern head."""
    add_fill(fills, f"{label} post", (x - 1, y, z - 1), (x + 1, y + 5, z + 1), M.LOG)
    add_fill(fills, f"{label} lamp", (x - 1, y + 6, z - 1), (x + 1, y + 6, z + 1), M.SEA_LANTERN)


def _bamboo_cluster(fills: list[Fill], label: str, x: int, z: int) -> None:
    """A bamboo clump simulated by thin leaf columns with a shared crown."""
    stalks = [(x, z), (x + 2, z + 1), (x - 1, z + 2), (x + 1, z + 3)]
    for i, (sx, sz) in enumerate(stalks):
        add_fill(fills, f"{label} stalk {i}", (sx, 4, sz), (sx, 8, sz), M.LEAVES)
    add_fill(fills, f"{label} crown", (x - 2, 9, z - 1), (x + 3, 9, z + 4), M.LEAVES)


def _plum_tree(fills: list[Fill], label: str, x: int, z: int) -> None:
    """A blossoming plum: dark trunk with a pink-wool flower crown."""
    add_fill(fills, f"{label} trunk", (x, 4, z), (x, 9, z), M.TREE_LOG)
    add_fill(fills, f"{label} bloom", (x - 2, 8, z - 2), (x + 2, 9, z + 2), M.PINK_WOOL)
    add_fill(fills, f"{label} bloom top", (x - 1, 10, z - 1), (x + 1, 10, z + 1), M.PINK_WOOL)


def _study_fittings(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    fy: int,
    shelf: str,
    desk: str = "center",
) -> None:
    """Furnish a study interior: bookshelf wall, desk with quartz
    paperweights, lectern, candle lanterns and a ceiling lamp.

    (x1,z1)-(x2,z2) are the interior bounds; fy is the floor level.
    shelf: 'w' | 'e' | 'n' (north shelf splits around a central passage).
    desk: 'center' | 'dual' (dual desks flank the passage).
    """
    cx, cz = (x1 + x2) // 2, (z1 + z2) // 2
    if shelf == "w":
        add_fill(fills, f"{label} shelf w", (x1, fy + 1, z1), (x1 + 1, fy + 4, z2), "minecraft:bookshelf")
        stand_x = x2 - 2
    elif shelf == "e":
        add_fill(fills, f"{label} shelf e", (x2 - 1, fy + 1, z1), (x2, fy + 4, z2), "minecraft:bookshelf")
        stand_x = x1 + 2
    else:
        add_fill(fills, f"{label} shelf n w", (x1, fy + 1, z1), (cx - 9, fy + 4, z1 + 1), "minecraft:bookshelf")
        add_fill(fills, f"{label} shelf n e", (cx + 9, fy + 1, z1), (x2, fy + 4, z1 + 1), "minecraft:bookshelf")
        stand_x = x2 - 2
    add_fill(fills, f"{label} candle post", (stand_x, fy + 1, z2 - 2), (stand_x, fy + 2, z2 - 2), M.LOG)
    add_fill(fills, f"{label} candle", (stand_x, fy + 3, z2 - 2), (stand_x, fy + 3, z2 - 2), M.LANTERN)
    add_fill(fills, f"{label} lamp", (cx, fy + 4, cz), (cx, fy + 4, cz), M.SEA_LANTERN)
    if desk == "center":
        add_fill(fills, f"{label} desk", (cx - 8, fy + 1, cz - 3), (cx + 8, fy + 1, cz + 3), M.WOOD)
        add_fill(fills, f"{label} paperweight a", (cx - 5, fy + 2, cz - 2), (cx - 5, fy + 2, cz - 2), M.QUARTZ)
        add_fill(fills, f"{label} paperweight b", (cx + 5, fy + 2, cz + 2), (cx + 5, fy + 2, cz + 2), M.QUARTZ)
        add_fill(fills, f"{label} lectern", (cx, fy + 2, cz), (cx, fy + 2, cz), "minecraft:lectern")
        add_fill(fills, f"{label} candle a", (cx - 7, fy + 2, cz + 2), (cx - 7, fy + 2, cz + 2), M.LANTERN)
        add_fill(fills, f"{label} candle b", (cx + 7, fy + 2, cz - 2), (cx + 7, fy + 2, cz - 2), M.LANTERN)
    else:
        add_fill(fills, f"{label} desk w", (x1 + 3, fy + 1, cz - 3), (cx - 10, fy + 1, cz + 3), M.WOOD)
        add_fill(fills, f"{label} desk e", (cx + 10, fy + 1, cz - 3), (x2 - 3, fy + 1, cz + 3), M.WOOD)
        add_fill(fills, f"{label} paperweight a", (x1 + 7, fy + 2, cz - 1), (x1 + 7, fy + 2, cz - 1), M.QUARTZ)
        add_fill(fills, f"{label} paperweight b", (x2 - 7, fy + 2, cz + 1), (x2 - 7, fy + 2, cz + 1), M.QUARTZ)
        add_fill(fills, f"{label} lectern w", (x1 + 11, fy + 2, cz + 1), (x1 + 11, fy + 2, cz + 1), "minecraft:lectern")
        add_fill(fills, f"{label} lectern e", (x2 - 11, fy + 2, cz - 1), (x2 - 11, fy + 2, cz - 1), "minecraft:lectern")
        add_fill(fills, f"{label} candle a", (x1 + 4, fy + 2, cz + 2), (x1 + 4, fy + 2, cz + 2), M.LANTERN)
        add_fill(fills, f"{label} candle b", (x2 - 4, fy + 2, cz - 2), (x2 - 4, fy + 2, cz - 2), M.LANTERN)


def build_hanlin_academy_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site grading: stone base y0..1 and lawn y2..3 over the plot.
    # ------------------------------------------------------------------
    add_fill(fills, "hanlin foundation", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "hanlin lawn", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)

    # ------------------------------------------------------------------
    # 2. Perimeter white wall (白墙围合) with dark coping and corner piers.
    # ------------------------------------------------------------------
    add_fill(fills, "hanlin wall n", (WALL_X1, 4, WALL_Z1), (WALL_X2, 9, WALL_Z1 + 1), M.WHITE_TERRACOTTA)
    add_fill(fills, "hanlin wall s", (WALL_X1, 4, WALL_Z2 - 1), (WALL_X2, 9, WALL_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "hanlin wall w", (WALL_X1, 4, WALL_Z1), (WALL_X1 + 1, 9, WALL_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "hanlin wall e", (WALL_X2 - 1, 4, WALL_Z1), (WALL_X2, 9, WALL_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "hanlin coping n", (WALL_X1, 10, WALL_Z1), (WALL_X2, 10, WALL_Z1 + 1), M.DARK)
    add_fill(fills, "hanlin coping s", (WALL_X1, 10, WALL_Z2 - 1), (WALL_X2, 10, WALL_Z2), M.DARK)
    add_fill(fills, "hanlin coping w", (WALL_X1, 10, WALL_Z1), (WALL_X1 + 1, 10, WALL_Z2), M.DARK)
    add_fill(fills, "hanlin coping e", (WALL_X2 - 1, 10, WALL_Z1), (WALL_X2, 10, WALL_Z2), M.DARK)
    for tag, px, pz in (
        ("nw", WALL_X1, WALL_Z1), ("ne", WALL_X2 - 2, WALL_Z1),
        ("sw", WALL_X1, WALL_Z2 - 2), ("se", WALL_X2 - 2, WALL_Z2 - 2),
    ):
        add_fill(fills, f"hanlin pier {tag}", (px, 4, pz), (px + 2, 11, pz + 2), M.RED_WALL)
        add_fill(fills, f"hanlin pier cap {tag}", (px - 1, 12, pz - 1), (px + 3, 12, pz + 3), M.DARK)

    # ------------------------------------------------------------------
    # 3. Axial stone causeway and courtyard paving/aprons (石板甬道).
    # ------------------------------------------------------------------
    add_fill(fills, "hanlin causeway", (PATH_X1, 4, 5032), (PATH_X2, 4, 5171), M.SMOOTH)
    add_fill(fills, "hanlin court b paving", (2222, 4, 5064), (2286, 4, 5080), M.SMOOTH)
    add_fill(fills, "hanlin court c apron", (2240, 4, 5016), (2270, 4, 5042), M.SMOOTH)
    add_fill(fills, "hanlin forecourt apron", (2224, 4, 5150), (2284, 4, 5171), M.SMOOTH)

    # ------------------------------------------------------------------
    # 4. South chuihua gate (垂花门): platform, flush columns, cross beam,
    #    hanging pendant columns and a small gable roof.
    # ------------------------------------------------------------------
    add_fill(fills, "hanlin gate platform", (2236, 4, 5172), (2272, 5, 5178), M.STONE)
    add_fill(fills, "hanlin gate opening", (2244, 4, 5177), (2264, 9, 5178), M.AIR)
    add_fill(fills, "hanlin gate pier w", (2238, 4, 5174), (2241, 10, 5178), M.RED_WALL)
    add_fill(fills, "hanlin gate pier e", (2267, 4, 5174), (2270, 10, 5178), M.RED_WALL)
    add_fill(fills, "hanlin gate column w", (2242, 6, 5173), (2243, 11, 5174), M.LOG)
    add_fill(fills, "hanlin gate column e", (2265, 6, 5173), (2266, 11, 5174), M.LOG)
    add_fill(fills, "hanlin gate beam", (2240, 11, 5172), (2268, 12, 5176), M.WOOD)
    for tag, px in (("w", 2244), ("e", 2263)):
        add_fill(fills, f"hanlin gate pendant {tag} n", (px, 9, 5172), (px + 1, 10, 5173), M.LOG)
        add_fill(fills, f"hanlin gate pendant {tag} s", (px, 9, 5175), (px + 1, 10, 5176), M.LOG)
    add_fill(fills, "hanlin gate threshold", (2244, 4, 5169), (2264, 4, 5171), M.SMOOTH)
    add_fill(fills, "hanlin gate drum w", (2242, 6, 5173), (2242, 6, 5173), M.SMOOTH)
    add_fill(fills, "hanlin gate drum e", (2266, 6, 5173), (2266, 6, 5173), M.SMOOTH)

    # ------------------------------------------------------------------
    # 5. Stepped platforms for every building (built before partitions so
    #    the cross walls rise straight from the terrace edges).
    # ------------------------------------------------------------------
    add_platform_with_steps(fills, "hanlin hall platform", HALL_X1, HALL_Z1, HALL_X2, HALL_Z2, 4,
                            [(1, 0, M.STONE), (1, 2, M.SMOOTH)])
    add_platform_with_steps(fills, "hanlin pavilion platform", 2222, 5082, 2286, 5114, 4,
                            [(1, 0, M.STONE), (1, 2, M.SMOOTH)])
    add_platform_with_steps(fills, "hanlin study n platform", 2222, 5042, 2286, 5066, 4,
                            [(1, 0, M.STONE), (1, 2, M.SMOOTH)])
    add_platform_with_steps(fills, "hanlin wing w platform", 2182, 5046, 2220, 5080, 4,
                            [(1, 0, M.STONE), (1, 2, M.SMOOTH)])
    add_platform_with_steps(fills, "hanlin wing e platform", 2288, 5046, 2326, 5080, 4,
                            [(1, 0, M.STONE), (1, 2, M.SMOOTH)])
    add_platform_with_steps(fills, "hanlin duty platform", 2182, 5014, 2226, 5038, 4,
                            [(1, 0, M.STONE), (1, 2, M.SMOOTH)])
    add_platform_with_steps(fills, "hanlin gazebo platform", 2242, 5018, 2266, 5034, 4,
                            [(2, 0, M.STONE), (1, 3, M.SMOOTH)])
    add_fill(fills, "hanlin gazebo step", (2252, 4, 5035), (2256, 4, 5036), M.SMOOTH)

    # ------------------------------------------------------------------
    # 6. Cross walls between the courts with axial gate openings.
    # ------------------------------------------------------------------
    add_fill(fills, "hanlin cross wall 1 w", (2174, 4, 5082), (2243, 8, 5083), M.WHITE_TERRACOTTA)
    add_fill(fills, "hanlin cross wall 1 e", (2265, 4, 5082), (2335, 8, 5083), M.WHITE_TERRACOTTA)
    add_fill(fills, "hanlin cross coping 1 w", (2174, 9, 5082), (2243, 9, 5083), M.DARK)
    add_fill(fills, "hanlin cross coping 1 e", (2265, 9, 5082), (2335, 9, 5083), M.DARK)
    add_fill(fills, "hanlin cross lintel 1", (2242, 8, 5082), (2266, 9, 5083), M.LOG)
    add_fill(fills, "hanlin cross wall 2 w", (2174, 4, 5044), (2243, 8, 5045), M.WHITE_TERRACOTTA)
    add_fill(fills, "hanlin cross wall 2 e", (2265, 4, 5044), (2335, 8, 5045), M.WHITE_TERRACOTTA)
    add_fill(fills, "hanlin cross coping 2 w", (2174, 9, 5044), (2243, 9, 5045), M.DARK)
    add_fill(fills, "hanlin cross coping 2 e", (2265, 9, 5044), (2335, 9, 5045), M.DARK)
    add_fill(fills, "hanlin cross lintel 2", (2242, 8, 5044), (2266, 9, 5045), M.LOG)

    # ------------------------------------------------------------------
    # 7. Painting hall (画案院): open colonnade studio on the axis.
    # ------------------------------------------------------------------
    for i, cxx in enumerate((2214, 2230, 2246, 2262, 2278, 2294)):
        for j, czz in enumerate((5118, 5146)):
            add_fill(fills, f"hanlin hall col {i}{j}", (cxx, 6, czz), (cxx + 1, 12, czz + 1), M.LOG)
    for tag, cxx in (("w", 2214), ("e", 2294)):
        add_fill(fills, f"hanlin hall col mid {tag}", (cxx, 6, 5132), (cxx + 1, 12, 5133), M.LOG)
    # Long painting table with white-wool paper (宣纸) and corner legs.
    add_fill(fills, "hanlin hall table", (2228, 7, 5122), (2280, 7, 5127), M.WOOD)
    for k, (lx, lz) in enumerate(((2229, 5123), (2279, 5123), (2229, 5126), (2279, 5126))):
        add_fill(fills, f"hanlin hall table leg {k}", (lx, 6, lz), (lx, 6, lz), M.LOG)
    add_fill(fills, "hanlin hall paper", (2232, 8, 5123), (2276, 8, 5126), M.WHITE_WOOL)
    # Brush rack (笔架): fence posts, log bar, hanging brushes.
    add_fill(fills, "hanlin hall rack post a", (2240, 8, 5133), (2240, 9, 5133), M.FENCE)
    add_fill(fills, "hanlin hall rack post b", (2252, 8, 5133), (2252, 9, 5133), M.FENCE)
    add_fill(fills, "hanlin hall rack bar", (2237, 10, 5133), (2255, 10, 5133), M.LOG)
    add_fill(fills, "hanlin hall brush a", (2244, 9, 5133), (2244, 9, 5133), M.BLACK_WOOL)
    add_fill(fills, "hanlin hall brush b", (2248, 9, 5133), (2248, 9, 5133), M.BLACK_WOOL)
    # Pigment side table with wool dishes (颜料碟) and ink barrels.
    add_fill(fills, "hanlin hall side table", (2256, 7, 5134), (2276, 7, 5138), M.WOOD)
    for tag, block, dx in (
        ("red", M.RED_WOOL, 0), ("yellow", M.YELLOW_WOOL, 4), ("blue", M.BLUE_WOOL, 8),
        ("green", M.GREEN_WOOL, 12), ("pink", M.PINK_WOOL, 16),
    ):
        add_fill(fills, f"hanlin hall dish {tag}", (2258 + dx, 8, 5135), (2259 + dx, 8, 5136), block)
    add_fill(fills, "hanlin hall barrel a", (2246, 7, 5141), (2246, 7, 5141), "minecraft:barrel")
    add_fill(fills, "hanlin hall barrel b", (2249, 7, 5141), (2249, 7, 5141), "minecraft:barrel")
    add_fill(fills, "hanlin hall lamp", (2254, 12, 5132), (2254, 12, 5132), M.SEA_LANTERN)

    # ------------------------------------------------------------------
    # 8. Book pavilion (藏书小阁): two storeys, used as the second gate.
    #    Ground floor y6..10 ringed by three-tier shelves; cantilevered
    #    gallery y11..; upper study y12..16 with three-tier shelf walls.
    # ------------------------------------------------------------------
    add_hollow_box(fills, "hanlin pavilion body1", PAV_X1, 6, PAV_Z1, PAV_X2, 10, PAV_Z2, M.RED_WALL, thickness=1)
    add_fill(fills, "hanlin pavilion floor", (PAV_X1 + 1, 6, PAV_Z1 + 1), (PAV_X2 - 1, 6, PAV_Z2 - 1), M.WOOD)
    add_fill(fills, "hanlin pavilion door n", (2248, 7, PAV_Z1), (2260, 10, PAV_Z1), M.AIR)
    add_fill(fills, "hanlin pavilion door s", (2248, 7, PAV_Z2), (2260, 10, PAV_Z2), M.AIR)
    add_fill(fills, "hanlin pavilion clerestory w", (PAV_X1, 10, 5092), (PAV_X1, 10, 5104), M.GLASS)
    add_fill(fills, "hanlin pavilion clerestory e", (PAV_X2, 10, 5092), (PAV_X2, 10, 5104), M.GLASS)
    add_fill(fills, "hanlin pavilion shelf w", (2227, 7, 5087), (2228, 9, 5109), "minecraft:bookshelf")
    add_fill(fills, "hanlin pavilion shelf e", (2280, 7, 5087), (2281, 9, 5109), "minecraft:bookshelf")
    add_fill(fills, "hanlin pavilion shelf n w", (2229, 7, 5087), (2247, 9, 5088), "minecraft:bookshelf")
    add_fill(fills, "hanlin pavilion shelf n e", (2261, 7, 5087), (2279, 9, 5088), "minecraft:bookshelf")
    add_fill(fills, "hanlin pavilion shelf s w", (2229, 7, 5108), (2247, 9, 5109), "minecraft:bookshelf")
    add_fill(fills, "hanlin pavilion shelf s e", (2261, 7, 5108), (2279, 9, 5109), "minecraft:bookshelf")
    add_fill(fills, "hanlin pavilion desk w", (2232, 7, 5096), (2244, 7, 5100), M.WOOD)
    add_fill(fills, "hanlin pavilion lectern w", (2238, 8, 5098), (2238, 8, 5098), "minecraft:lectern")
    add_fill(fills, "hanlin pavilion candle w", (2233, 8, 5099), (2233, 8, 5099), M.LANTERN)
    add_fill(fills, "hanlin pavilion desk e", (2264, 7, 5096), (2276, 7, 5100), M.WOOD)
    add_fill(fills, "hanlin pavilion lectern e", (2270, 8, 5098), (2270, 8, 5098), "minecraft:lectern")
    add_fill(fills, "hanlin pavilion candle e", (2275, 8, 5099), (2275, 8, 5099), M.LANTERN)
    # Cantilevered middle floor and open gallery with fence railing.
    add_cantilevered_floor(fills, "hanlin pavilion gallery floor", PAV_X1, PAV_Z1, PAV_X2, PAV_Z2, 11, overhang=2)
    add_outline(fills, "hanlin pavilion gallery rail", 2225, 5085, 2283, 5111, 12, 12, M.FENCE, thickness=1)
    for i, (px, pz) in enumerate(((2226, 5086), (2254, 5086), (2282, 5086), (2226, 5110),
                                  (2254, 5110), (2282, 5110), (2226, 5098), (2282, 5098))):
        add_fill(fills, f"hanlin pavilion gallery post {i}", (px, 12, pz), (px, 16, pz), M.LOG)
    for pz in (5085, 5111):
        add_fill(fills, f"hanlin pavilion rail lamp {pz}", (2225, 13, pz), (2225, 13, pz), M.LANTERN)
        add_fill(fills, f"hanlin pavilion rail lamp {pz} e", (2283, 13, pz), (2283, 13, pz), M.LANTERN)
    # Upper study core with three-tier shelf walls and lattice windows.
    add_hollow_box(fills, "hanlin pavilion body2", 2232, 12, 5090, 2276, 16, 5106, M.RED_WALL, thickness=1)
    add_fill(fills, "hanlin pavilion floor2", (2233, 12, 5091), (2275, 12, 5105), M.WOOD)
    add_fill(fills, "hanlin pavilion shelf2 w", (2233, 13, 5091), (2234, 15, 5105), "minecraft:bookshelf")
    add_fill(fills, "hanlin pavilion shelf2 e", (2274, 13, 5091), (2275, 15, 5105), "minecraft:bookshelf")
    for tag, pz in (("n", 5090), ("s", 5106)):
        add_fill(fills, f"hanlin pavilion window2 {tag} w", (2240, 13, pz), (2246, 15, pz), M.GLASS)
        add_fill(fills, f"hanlin pavilion window2 {tag} e", (2262, 13, pz), (2268, 15, pz), M.GLASS)
    add_fill(fills, "hanlin pavilion desk2", (2244, 13, 5097), (2264, 13, 5101), M.WOOD)
    add_fill(fills, "hanlin pavilion lectern2", (2254, 14, 5099), (2254, 14, 5099), "minecraft:lectern")
    add_fill(fills, "hanlin pavilion candle2 a", (2246, 14, 5100), (2246, 14, 5100), M.LANTERN)
    add_fill(fills, "hanlin pavilion candle2 b", (2262, 14, 5098), (2262, 14, 5098), M.LANTERN)

    # ------------------------------------------------------------------
    # 9. Scholars' study court (学士值房三座): north main study (a walk-
    #    through hall) plus east and west wings; red walls, gable roofs,
    #    bookshelf walls, desks, lecterns and candle lanterns inside.
    # ------------------------------------------------------------------
    add_hollow_box(fills, "hanlin study n body", STUDY_N_X1, 6, STUDY_N_Z1, STUDY_N_X2, 12, STUDY_N_Z2,
                   M.RED_WALL, thickness=1)
    add_fill(fills, "hanlin study n floor", (STUDY_N_X1 + 1, 6, STUDY_N_Z1 + 1),
             (STUDY_N_X2 - 1, 6, STUDY_N_Z2 - 1), M.WOOD)
    add_fill(fills, "hanlin study n door s", (2246, 7, STUDY_N_Z2), (2262, 10, STUDY_N_Z2), M.AIR)
    add_fill(fills, "hanlin study n door n", (2246, 7, STUDY_N_Z1), (2262, 10, STUDY_N_Z1), M.AIR)
    add_fill(fills, "hanlin study n window w", (STUDY_N_X1, 8, 5050), (STUDY_N_X1, 10, 5058), M.GLASS)
    add_fill(fills, "hanlin study n window e", (STUDY_N_X2, 8, 5050), (STUDY_N_X2, 10, 5058), M.GLASS)
    _study_fittings(fills, "hanlin study n", STUDY_N_X1 + 1, STUDY_N_Z1 + 1, STUDY_N_X2 - 1, STUDY_N_Z2 - 1,
                    6, "n", desk="dual")

    for tag, (bx1, bz1, bx2, bz2, shelf, dx1, dx2, dz1, dz2) in (
        ("w", (WING_W_X1, WING_W_Z1, WING_W_X2, WING_W_Z2, "w", 2192, 2204, 5050, 5076)),
        ("e", (WING_E_X1, WING_E_Z1, WING_E_X2, WING_E_Z2, "e", 2300, 2312, 5050, 5076)),
    ):
        add_hollow_box(fills, f"hanlin wing {tag} body", bx1, 6, bz1, bx2, 11, bz2, M.RED_WALL, thickness=1)
        add_fill(fills, f"hanlin wing {tag} floor", (bx1 + 1, 6, bz1 + 1), (bx2 - 1, 6, bz2 - 1), M.WOOD)
        door_x = bx2 if tag == "w" else bx1
        add_fill(fills, f"hanlin wing {tag} door", (door_x, 7, 5059), (door_x, 10, 5067), M.AIR)
        add_fill(fills, f"hanlin wing {tag} window n", (dx1, 8, dz1), (dx2, 10, dz1), M.GLASS)
        add_fill(fills, f"hanlin wing {tag} window s", (dx1, 8, dz2), (dx2, 10, dz2), M.GLASS)
        _study_fittings(fills, f"hanlin wing {tag}", bx1 + 1, bz1 + 1, bx2 - 1, bz2 - 1, 6, shelf)

    # ------------------------------------------------------------------
    # 10. Duty court (待诏直院), the deepest yard: duty room, north-facing
    #     open gazebo (望亭) and the stone chess table.
    # ------------------------------------------------------------------
    add_hollow_box(fills, "hanlin duty body", DUTY_X1, 6, DUTY_Z1, DUTY_X2, 11, DUTY_Z2, M.RED_WALL, thickness=1)
    add_fill(fills, "hanlin duty floor", (DUTY_X1 + 1, 6, DUTY_Z1 + 1), (DUTY_X2 - 1, 6, DUTY_Z2 - 1), M.WOOD)
    add_fill(fills, "hanlin duty door", (DUTY_X2, 7, 5022), (DUTY_X2, 10, 5026), M.AIR)
    add_fill(fills, "hanlin duty window n", (2194, 8, DUTY_Z1), (2206, 10, DUTY_Z1), M.GLASS)
    add_fill(fills, "hanlin duty window w", (DUTY_X1, 8, 5024), (DUTY_X1, 10, 5028), M.GLASS)
    _study_fittings(fills, "hanlin duty", DUTY_X1 + 1, DUTY_Z1 + 1, DUTY_X2 - 1, DUTY_Z2 - 1, 6, "w")

    # Gazebo: two red columns on the open north side, low back parapet,
    # side fence rails and a gilded pyramid roof (攒尖顶).
    for tag, px in (("w", 2246), ("e", 2260)):
        add_fill(fills, f"hanlin gazebo column {tag}", (px, 6, 5022), (px + 1, 12, 5023), M.RED_WALL)
    add_fill(fills, "hanlin gazebo parapet", (2245, 6, 5030), (2263, 7, 5031), M.WHITE_TERRACOTTA)
    add_fill(fills, "hanlin gazebo rail w", (2245, 6, 5024), (2245, 7, 5029), M.FENCE)
    add_fill(fills, "hanlin gazebo rail e", (2263, 6, 5024), (2263, 7, 5029), M.FENCE)
    add_pyramid_roof(fills, "hanlin gazebo roof", GAZEBO_CX, GAZEBO_CZ, radius=8, y=13,
                     roof_block=M.ROOF_GREEN, apex_block=M.GOLD)

    # Chess table (石桌棋局): smooth-stone table on a pedestal with wool
    # stones and two stone stools.
    add_fill(fills, "hanlin chess pedestal", (2299, 4, 5023), (2301, 4, 5025), M.STONE)
    add_fill(fills, "hanlin chess table", (2298, 5, 5022), (2302, 5, 5026), M.SMOOTH)
    for tag, block, (sx, sz) in (
        ("b1", M.BLACK_WOOL, (2299, 5023)), ("w1", M.WHITE_WOOL, (2301, 5023)),
        ("b2", M.BLACK_WOOL, (2300, 5024)), ("w2", M.WHITE_WOOL, (2299, 5024)),
        ("b3", M.BLACK_WOOL, (2301, 5025)), ("w3", M.WHITE_WOOL, (2300, 5023)),
    ):
        add_fill(fills, f"hanlin chess stone {tag}", (sx, 6, sz), (sx, 6, sz), block)
    add_fill(fills, "hanlin chess stool w", (2295, 4, 5024), (2295, 5, 5024), M.SMOOTH)
    add_fill(fills, "hanlin chess stool e", (2305, 4, 5024), (2305, 5, 5024), M.SMOOTH)

    # ------------------------------------------------------------------
    # 11. Roofs (built last among the structures: their clearing passes
    #     must not erase neighbouring bodies).
    # ------------------------------------------------------------------
    add_ridge_roof(fills, "hanlin gate roof", 2238, 5170, 2270, 5176, 13, layers=2,
                   ridge_axis="x", roof_block=M.ROOF_GREEN)
    add_ridge_roof(fills, "hanlin hall roof", 2208, 5114, 2300, 5150, 13, layers=3,
                   ridge_axis="x", roof_block=M.ROOF_GREEN)
    add_ridge_roof(fills, "hanlin pavilion roof", 2224, 5084, 2284, 5112, 17, layers=2,
                   ridge_axis="x", roof_block=M.ROOF_BLUE)
    add_ridge_roof(fills, "hanlin study n roof", 2222, 5042, 2286, 5066, 13, layers=3,
                   ridge_axis="x", roof_block=M.ROOF_GREEN)
    add_ridge_roof(fills, "hanlin wing w roof", 2182, 5046, 2220, 5080, 12, layers=2,
                   ridge_axis="x", roof_block=M.ROOF_GREEN)
    add_ridge_roof(fills, "hanlin wing e roof", 2288, 5046, 2326, 5080, 12, layers=2,
                   ridge_axis="x", roof_block=M.ROOF_GREEN)
    add_ridge_roof(fills, "hanlin duty roof", 2182, 5014, 2226, 5038, 12, layers=2,
                   ridge_axis="x", roof_block=M.ROOF_GREEN)

    # ------------------------------------------------------------------
    # 12. Bamboo-and-plum garden (竹影梅枝庭院) behind a moon gate (月洞门).
    # ------------------------------------------------------------------
    add_fill(fills, "hanlin garden wall s", (2218, 4, 5149), (2219, 8, 5155), M.WHITE)
    add_fill(fills, "hanlin garden wall n", (2218, 4, 5161), (2219, 8, 5168), M.WHITE)
    add_fill(fills, "hanlin garden coping s", (2218, 9, 5149), (2219, 9, 5155), M.DARK)
    add_fill(fills, "hanlin garden coping n", (2218, 9, 5161), (2219, 9, 5168), M.DARK)
    add_fill(fills, "hanlin garden stub", (2218, 4, 5112), (2219, 8, 5115), M.WHITE)
    add_fill(fills, "hanlin garden stub coping", (2218, 9, 5112), (2219, 9, 5115), M.DARK)
    # Moon gate: round air opening ringed with white terracotta.
    add_fill(fills, "hanlin moon ring base", (2218, 4, 5156), (2219, 4, 5160), M.WHITE_TERRACOTTA)
    add_fill(fills, "hanlin moon ring 5", (2218, 5, 5155), (2219, 5, 5161), M.WHITE_TERRACOTTA)
    add_fill(fills, "hanlin moon air 5", (2218, 5, 5157), (2219, 5, 5159), M.AIR)
    add_fill(fills, "hanlin moon ring w", (2218, 6, 5155), (2219, 7, 5155), M.WHITE_TERRACOTTA)
    add_fill(fills, "hanlin moon ring e", (2218, 6, 5161), (2219, 7, 5161), M.WHITE_TERRACOTTA)
    add_fill(fills, "hanlin moon air mid", (2218, 6, 5156), (2219, 7, 5160), M.AIR)
    add_fill(fills, "hanlin moon ring 8 w", (2218, 8, 5155), (2219, 8, 5156), M.WHITE_TERRACOTTA)
    add_fill(fills, "hanlin moon ring 8 e", (2218, 8, 5160), (2219, 8, 5161), M.WHITE_TERRACOTTA)
    add_fill(fills, "hanlin moon air 8", (2218, 8, 5157), (2219, 8, 5159), M.AIR)
    add_fill(fills, "hanlin moon arch", (2218, 9, 5155), (2219, 9, 5161), M.WHITE_TERRACOTTA)
    add_fill(fills, "hanlin moon crown", (2218, 10, 5156), (2219, 10, 5160), M.WHITE_TERRACOTTA)
    # Green bamboo clumps and two plum trees.
    for i, (bx, bz) in enumerate(((2184, 5120), (2198, 5116), (2210, 5126),
                                  (2182, 5138), (2196, 5146), (2208, 5140))):
        _bamboo_cluster(fills, f"hanlin bamboo {i}", bx, bz)
    _plum_tree(fills, "hanlin plum a", 2188, 5132)
    _plum_tree(fills, "hanlin plum b", 2204, 5152)
    add_fill(fills, "hanlin garden path a", (2200, 4, 5157), (2217, 4, 5159), M.SMOOTH)
    add_fill(fills, "hanlin garden path b", (2200, 4, 5130), (2201, 4, 5158), M.SMOOTH)
    add_fill(fills, "hanlin garden stone table", (2190, 4, 5124), (2192, 5, 5125), M.SMOOTH)

    # ------------------------------------------------------------------
    # 13. Winding pool (曲水小池) with staggered stepping stones (汀步).
    # ------------------------------------------------------------------
    add_pool(fills, "hanlin pool reach a", POOL_R1_X1, POOL_R1_Z1, POOL_R1_X2, POOL_R1_Z2, 4, depth=1)
    add_pool(fills, "hanlin pool reach b", POOL_R2_X1, POOL_R2_Z1, POOL_R2_X2, POOL_R2_Z2, 4, depth=1)
    add_outline(fills, "hanlin pool rim a", POOL_R1_X1 - 2, POOL_R1_Z1 - 2, POOL_R1_X2 + 2, POOL_R1_Z2 + 2,
                4, 4, M.STONE, thickness=1)
    add_outline(fills, "hanlin pool rim b", POOL_R2_X1 - 2, POOL_R2_Z1 - 2, POOL_R2_X2 + 2, POOL_R2_Z2 + 2,
                4, 4, M.STONE, thickness=1)
    for i, (sx, sz) in enumerate(((2308, 5122), (2314, 5127), (2320, 5124), (2312, 5132),
                                  (2318, 5138), (2326, 5143), (2320, 5148))):
        add_fill(fills, f"hanlin stepping stone {i}", (sx, 4, sz), (sx + 1, 4, sz + 1), M.SMOOTH)

    # ------------------------------------------------------------------
    # 14. Lantern posts along the causeway and courtyard trees.
    # ------------------------------------------------------------------
    for x in (2238, 2270):
        for z in (5022, 5034):
            _lantern_post(fills, "hanlin lantern duty", x, z)
    for x in (2244, 2264):
        for z in (5068, 5076):
            _lantern_post(fills, "hanlin lantern court b", x, z)
    add_lantern_line(fills, "hanlin lantern forecourt w", 2244, 5156, 2244, 5166, 4, every=10)
    add_lantern_line(fills, "hanlin lantern forecourt e", 2264, 5156, 2264, 5166, 4, every=10)
    _lantern_post(fills, "hanlin lantern garden", 2212, 5158)
    _lantern_post(fills, "hanlin lantern pool", 2334, 5130)
    add_tree(fills, "hanlin cypress sw", 2232, 5162, 4, height=6, spread=2)
    add_tree(fills, "hanlin cypress se", 2276, 5162, 4, height=6, spread=2)
    add_tree(fills, "hanlin cypress court b w", 2232, 5072, 4, height=6, spread=2)
    add_tree(fills, "hanlin cypress court b e", 2276, 5072, 4, height=6, spread=2)


def main() -> None:
    run_builder(build_hanlin_academy_3d, "hanlin_academy_3d")


if __name__ == "__main__":
    main()
