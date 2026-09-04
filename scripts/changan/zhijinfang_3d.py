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
    add_hip_roof,
    add_hollow_box,
    add_lantern_line,
    add_outline,
    add_platform_with_steps,
    add_pyramid_roof,
    add_ridge_roof,
    add_tree,
    run_builder,
)


"""
Zhijinfang 3D (织锦坊·官营织染署) - the state weaving and dyeing
workshop (织染署) of Tang Chang'an in the eastern wards, the government
silk factory whose looms and dye vats supplied the court with silks and
polychrome brocades (the centre of the Chang'an weaving industry).

Location in Chang'an city local coordinates:
    Plot: x 4850..5150, z 1100..1450 (strict bounds - nothing may leave
    them). The surrounding blocks are ordinary ward housing (safe to
    overwrite); no known landmark conflicts. Ground is graded to stone
    y0..1 + grass y2..3 (walking surface y4); the main structures rise
    from y5. The walled compound is entered through a gate tower in the
    south (z-min) wall carrying the gold "织锦署" plaque; the brocade
    display hall closes the centre of the axis and the great open loom
    shed fills the north end (x 4900..5100, z 1300..1420).

Distinctive features:
    - Loom shed (织机大坊): a huge open-sided timber work shed whose six
      treadle looms stand in one row - each with twin log posts and a
      top beam, a plank body, four iron-bar warp threads, a wood
      shuttle and a weaver's stool, the beam above carrying a rolled
      wool "silk" bolt in three colours
    - Dye vat court (染缸阵): eight stone-ringed vats in the east yard,
      each holding a different coloured wool "dye" under water, stone
      paths between them and bamboo drying poles hung with double
      layers of blue / green / red cloth
    - Long cloth-drying racks (晾布长架) in the south yard: two rows of
      posts, three layers of cross-bars and twelve staggered two-block
      thick cloth bolts in six colours
    - Silkworm house (蚕箔房): a two-storey west wing - silk-reeling
      stoves (barrel + sea-lantern fire) and a four-tier silkworm tray
      rack with white wool cocoon clusters below, chest and bookshelf
      silk store above
    - Brocade display hall (锦缎展示堂) on the axis: three smooth-stone
      stands with gold-trimmed red / gold / yellow wool brocade
      patterns, and four wool tapestries hung on wooden scroll rods
    - Dye storehouse (染料库房) in the north-east corner with a six
      barrel array and four wool pigment piles
    - Well with a gilded pyramid roof, a lantern-lined approach avenue
      and two rows of mulberry trees with wide crowns
"""

# ---------------------------------------------------------------------------
# Site: eastern ward weaving compound (strict bounds).
# ---------------------------------------------------------------------------
SITE_X1, SITE_X2 = 4850, 5150
SITE_Z1, SITE_Z2 = 1100, 1450

# Compound wall (outer face) and coping level.
WALL_X1, WALL_Z1 = 4866, 1116
WALL_X2, WALL_Z2 = 5134, 1434

# South gate tower: bastion, arched passage, upper hall, roof envelope.
GB_X1, GB_Z1, GB_X2, GB_Z2 = 4980, 1116, 5040, 1131
ARCH_X1, ARCH_X2 = 5000, 5020
GH_X1, GH_Z1, GH_X2, GH_Z2 = 4986, 1114, 5034, 1132
GR_X1, GR_Z1, GR_X2, GR_Z2 = 4984, 1112, 5036, 1134

# Loom shed (织机大坊) at the north end; six looms in one row.
SHED_X1, SHED_Z1, SHED_X2, SHED_Z2 = 4900, 1300, 5100, 1420
LOOM_Z = 1358
LOOM_XS = (4930, 4958, 4986, 5014, 5042, 5070)

# Silkworm house (蚕箔房), two-storey west wing.
SILK_X1, SILK_Z1, SILK_X2, SILK_Z2 = 4872, 1236, 4940, 1294

# Brocade display hall (锦缎展示堂) on the central axis.
TER_X1, TER_Z1, TER_X2, TER_Z2 = 4956, 1228, 5064, 1300
HALL_X1, HALL_Z1, HALL_X2, HALL_Z2 = 4962, 1232, 5058, 1296
STAND_Z1, STAND_Z2 = 1256, 1274
STAND_XS = (4980, 5010, 5040)

# Dye vat court (染缸阵), east yard, and the bamboo drying frame.
VAT_XS = (5084, 5098, 5112, 5126)
VAT_ZS = (1248, 1280)
BAMBOO_ZS = (1308, 1320)

# Dye storehouse (染料库房), north-east corner.
STORE_X1, STORE_Z1, STORE_X2, STORE_Z2 = 5106, 1350, 5126, 1402

# Well, drying racks and mulberry avenue.
WELL_CX, WELL_CZ = 4925, 1205
RACK_ROWS = (1152, 1172)

# Direct-string blocks used by this module.
LOG_X = "minecraft:dark_oak_log[axis=x]"
BARREL = "minecraft:barrel"
CHEST_S = "minecraft:chest[facing=south]"
BOOKSHELF = "minecraft:bookshelf"
GOLD_WOOL = "minecraft:orange_wool"
LIGHT_BLUE_WOOL = "minecraft:light_blue_wool"
LIME_WOOL = "minecraft:lime_wool"

_DYE_COLORS = (
    M.RED_WOOL, M.BLUE_WOOL, M.GREEN_WOOL, M.YELLOW_WOOL,
    M.WHITE_WOOL, M.PINK_WOOL, LIGHT_BLUE_WOOL, LIME_WOOL,
)
_LOOM_COLORS = (M.RED_WOOL, M.YELLOW_WOOL, M.BLUE_WOOL)
_RACK_COLORS = (
    M.RED_WOOL, M.YELLOW_WOOL, M.BLUE_WOOL,
    M.GREEN_WOOL, M.WHITE_WOOL, M.PINK_WOOL,
)
_TAPESTRY_COLORS = (M.RED_WOOL, GOLD_WOOL, M.BLUE_WOOL, M.GREEN_WOOL)
# (x1, y1, z row, colour index) for the twelve drying-rack cloth bolts.
_RACK_CLOTHS = (
    (
        (4897, 8, 1152, 0), (4912, 7, 1152, 1),
        (4897, 7, 1171, 2), (4912, 8, 1171, 3),
        (4933, 8, 1152, 4), (4948, 7, 1171, 5),
    ),
    (
        (5061, 7, 1152, 3), (5076, 8, 1152, 4),
        (5061, 8, 1171, 5), (5076, 7, 1171, 0),
        (5097, 7, 1152, 1), (5112, 8, 1171, 2),
    ),
)
_BAMBOO_CLOTHS = ((5110, 1308, M.BLUE_WOOL), (5119, 1308, M.GREEN_WOOL), (5110, 1320, M.RED_WOOL))


# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------
def _loom(fills: list[Fill], label: str, cx: int, cz: int, color_shift: int) -> None:
    """One treadle loom: log posts + beam, plank body, warp, shuttle,
    weaver's stool, and a three-colour wool bolt on the cloth beam."""
    # Twin upright posts and the top beam.
    add_fill(fills, f"{label} post w", (cx - 6, 4, cz - 4), (cx - 6, 13, cz - 4), M.LOG)
    add_fill(fills, f"{label} post e", (cx + 6, 4, cz - 4), (cx + 6, 13, cz - 4), M.LOG)
    add_fill(fills, f"{label} beam", (cx - 6, 13, cz - 4), (cx + 6, 13, cz - 4), LOG_X)
    # Rolled cloth bolt in three colour segments beneath the beam.
    for seg, (sx1, sx2) in enumerate(((cx - 5, cx - 2), (cx - 1, cx + 2), (cx + 3, cx + 5))):
        wool = _LOOM_COLORS[(color_shift + seg) % len(_LOOM_COLORS)]
        add_fill(fills, f"{label} bolt {seg}", (sx1, 11, cz - 4), (sx2, 12, cz - 4), wool)
    # Four warp threads hanging in front of the bolt.
    for wi, wx in enumerate((cx - 3, cx - 1, cx + 1, cx + 3)):
        add_fill(fills, f"{label} warp {wi}", (wx, 7, cz - 3), (wx, 10, cz - 3), M.IRON_BARS)
    # Plank body, shuttle and the weaver's stool.
    add_fill(fills, f"{label} body", (cx - 5, 4, cz - 1), (cx + 5, 6, cz + 1), M.WOOD)
    add_fill(fills, f"{label} shuttle", (cx - 1, 7, cz), (cx + 1, 7, cz), M.WOOD)
    add_fill(fills, f"{label} stool", (cx - 1, 4, cz + 3), (cx + 1, 5, cz + 3), M.SPRUCE)


# ---------------------------------------------------------------------------
# Main builder.
# ---------------------------------------------------------------------------
def build_zhijinfang_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site grading: stone base, grass terrace, gate axis and work paths.
    # ------------------------------------------------------------------
    add_fill(fills, "zhijin clear site", (SITE_X1, 4, SITE_Z1), (SITE_X2, 7, SITE_Z2), M.AIR)
    add_fill(fills, "zhijin terrace stone", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "zhijin terrace grass", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)
    add_fill(fills, "zhijin approach pave", (4982, 3, 1100), (5038, 3, 1115), M.ANDESITE)
    add_fill(fills, "zhijin arch floor", (ARCH_X1, 3, GB_Z1), (ARCH_X2, 3, GB_Z2), M.ANDESITE)
    add_fill(fills, "zhijin axis path", (4998, 3, 1131), (5022, 3, 1229), M.ANDESITE)
    add_fill(fills, "zhijin shed pave", (SHED_X1, 3, SHED_Z1), (SHED_X2, 3, SHED_Z2), M.ANDESITE)
    add_fill(fills, "zhijin shed lane", (4998, 3, SHED_Z1), (5022, 3, SHED_Z2), M.SMOOTH)
    add_fill(fills, "zhijin vat court pave", (5078, 3, 1236), (5130, 3, 1296), M.ANDESITE)
    add_fill(fills, "zhijin vat path h", (5060, 3, 1262), (5130, 3, 1265), M.SMOOTH)
    add_fill(fills, "zhijin vat path v", (5090, 3, 1238), (5093, 3, 1294), M.SMOOTH)
    add_fill(fills, "zhijin bamboo court pave", (5104, 3, 1304), (5130, 3, 1346), M.ANDESITE)

    # ------------------------------------------------------------------
    # 2. Rammed-earth compound wall: white body, dark coping, buttresses.
    # ------------------------------------------------------------------
    add_outline(fills, "zhijin wall body", WALL_X1, WALL_Z1, WALL_X2, WALL_Z2, 4, 9, M.WHITE_TERRACOTTA, thickness=2)
    add_outline(fills, "zhijin wall coping", WALL_X1, WALL_Z1, WALL_X2, WALL_Z2, 10, 10, M.DARK, thickness=2)
    for bz in (1250, 1380):
        add_fill(fills, f"zhijin buttress w {bz}", (4868, 4, bz), (4869, 9, bz + 1), M.WHITE_TERRACOTTA)
        add_fill(fills, f"zhijin buttress e {bz}", (5131, 4, bz), (5132, 9, bz + 1), M.WHITE_TERRACOTTA)

    # ------------------------------------------------------------------
    # 3. South gate tower: bastion, arched passage, gate leaves, the gold
    #    "织锦署" plaque, barred upper hall and a dark gable roof.
    # ------------------------------------------------------------------
    add_fill(fills, "zhijin gate bastion", (GB_X1, 4, GB_Z1), (GB_X2, 13, GB_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "zhijin gate arch", (ARCH_X1, 4, GB_Z1), (ARCH_X2, 11, GB_Z2), M.AIR)
    add_fill(fills, "zhijin gate lintel", (ARCH_X1 - 1, 11, GB_Z1), (ARCH_X2 + 1, 11, GB_Z2), LOG_X)
    add_fill(fills, "zhijin gate leaf w", (5000, 4, 1116), (5005, 9, 1117), M.WOOD)
    add_fill(fills, "zhijin gate leaf e", (5015, 4, 1116), (5020, 9, 1117), M.WOOD)
    add_fill(fills, "zhijin plaque frame", (4986, 11, 1115), (5034, 15, 1115), M.DARK)
    add_fill(fills, "zhijin plaque gold", (4990, 12, 1115), (5030, 14, 1115), M.GOLD)
    add_fill(fills, "zhijin plaque sep w", (5000, 12, 1115), (5000, 14, 1115), M.DARK)
    add_fill(fills, "zhijin plaque sep e", (5020, 12, 1115), (5020, 14, 1115), M.DARK)
    add_hollow_box(fills, "zhijin gate hall", GH_X1, 14, GH_Z1, GH_X2, 19, GH_Z2, M.RED_WALL, thickness=1)
    add_fill(fills, "zhijin gate bars n", (4990, 16, GH_Z1), (5030, 17, GH_Z1), M.IRON_BARS)
    add_ridge_roof(fills, "zhijin gate roof", GR_X1, GR_Z1, GR_X2, GR_Z2, 20, layers=2, ridge_axis="x", roof_block=M.ROOF_DARK, ridge_block=M.GOLD)
    # Seal the two ridge-end notches the primitive leaves at the eave line.
    add_fill(fills, "zhijin gate ridge cap w", (GR_X1, 24, 1123), (GR_X1 + 3, 24, 1123), M.GOLD)
    add_fill(fills, "zhijin gate ridge cap e", (GR_X2 - 3, 24, 1123), (GR_X2, 24, 1123), M.GOLD)
    for lx in (4986, 5034):
        add_fill(fills, f"zhijin approach lamp {lx}", (lx, 4, 1108), (lx, 6, 1108), M.FENCE)
        add_fill(fills, f"zhijin approach light {lx}", (lx, 7, 1108), (lx, 7, 1108), M.LANTERN)

    # ------------------------------------------------------------------
    # 4. Loom shed (织机大坊): open-sided work shed with perimeter posts,
    #    a great dark gable roof, and six looms in one row.
    # ------------------------------------------------------------------
    for cx in (4902, 4930, 4958, 4986, 5014, 5042, 5070, 5098):
        for cz in (1302, 1418):
            add_fill(fills, f"zhijin shed column {cx},{cz}", (cx, 4, cz), (cx, 14, cz), M.LOG)
    for cz in (1330, 1386):
        for cx in (4902, 5098):
            add_fill(fills, f"zhijin shed column {cx},{cz}", (cx, 4, cz), (cx, 14, cz), M.LOG)
    add_ridge_roof(fills, "zhijin shed roof", 4898, SHED_Z1, 5102, SHED_Z2, 15, layers=3, ridge_axis="x", roof_block=M.ROOF_DARK, ridge_block=M.GOLD)
    for li, cx in enumerate(LOOM_XS):
        _loom(fills, f"zhijin loom {li}", cx, LOOM_Z, li)

    # ------------------------------------------------------------------
    # 5. Silkworm house (蚕箔房): two-storey west wing - reeling stoves
    #    and cocoon tray racks below, the silk store above.
    # ------------------------------------------------------------------
    add_hollow_box(fills, "zhijin silkworm shell", SILK_X1, 4, SILK_Z1, SILK_X2, 11, SILK_Z2, M.WHITE_TERRACOTTA, thickness=1)
    add_fill(fills, "zhijin silkworm floor", (SILK_X1 + 1, 4, SILK_Z1 + 1), (SILK_X2 - 1, 4, SILK_Z2 - 1), M.WOOD)
    add_fill(fills, "zhijin silkworm door", (4898, 5, SILK_Z1), (4906, 8, SILK_Z1), M.AIR)
    add_fill(fills, "zhijin silkworm win s", (4876, 7, SILK_Z1), (4888, 8, SILK_Z1), M.GLASS)
    add_fill(fills, "zhijin silkworm win e", (SILK_X2, 7, 1250), (SILK_X2, 8, 1262), M.GLASS)
    # Silk-reeling stoves: barrel over a glowing sea-lantern core.
    for ri, sx in enumerate((4880, 4884)):
        add_fill(fills, f"zhijin reeling stove {ri}", (sx, 5, 1246), (sx, 5, 1246), BARREL)
        add_fill(fills, f"zhijin reeling fire {ri}", (sx, 6, 1246), (sx, 6, 1246), M.SEA_LANTERN)
    # Silkworm tray rack: four stepped thin trays with cocoon clusters.
    add_fill(fills, "zhijin tray 1", (4900, 5, 1250), (4924, 5, 1253), M.WOOD)
    add_fill(fills, "zhijin tray 2", (4901, 6, 1251), (4923, 6, 1252), M.WOOD)
    add_fill(fills, "zhijin tray 3", (4902, 7, 1251), (4922, 7, 1252), M.WOOD)
    add_fill(fills, "zhijin tray 4", (4903, 8, 1251), (4921, 8, 1252), M.WOOD)
    add_fill(fills, "zhijin cocoons", (4906, 9, 1251), (4918, 9, 1252), M.WHITE_WOOL)
    add_fill(fills, "zhijin cocoon basket", (4894, 5, 1250), (4900, 5, 1251), M.WHITE_WOOL)
    # Gentle interior steps up to the silk store (one fill per step).
    for step in range(7):
        add_fill(fills, f"zhijin silkworm step {step}", (4874 + step, 5 + step, 1286), (4874 + step, 5 + step, 1288), M.WOOD)
    # Second floor slab, leaving the stairwell open at the west end.
    add_fill(fills, "zhijin silkworm slab", (4882, 12, SILK_Z1 + 1), (SILK_X2 - 1, 12, SILK_Z2 - 1), M.WOOD)
    add_fill(fills, "zhijin silkworm slab w", (SILK_X1 + 1, 12, SILK_Z1 + 1), (4881, 12, 1284), M.WOOD)
    add_hollow_box(fills, "zhijin silkworm upper", SILK_X1, 13, SILK_Z1, SILK_X2, 18, SILK_Z2, M.WHITE_TERRACOTTA, thickness=1)
    add_fill(fills, "zhijin silk store chest", (4886, 13, SILK_Z1 + 1), (4892, 13, SILK_Z1 + 1), CHEST_S)
    add_fill(fills, "zhijin silk store shelves", (4898, 13, SILK_Z1 + 1), (4930, 15, SILK_Z1 + 1), BOOKSHELF)
    add_fill(fills, "zhijin upper win s", (4876, 15, SILK_Z1), (4888, 16, SILK_Z1), M.GLASS)
    add_fill(fills, "zhijin upper win e", (SILK_X2, 15, 1250), (SILK_X2, 16, 1262), M.GLASS)
    add_ridge_roof(fills, "zhijin silkworm roof", 4869, SILK_Z1 - 3, 4943, SILK_Z2 + 3, 19, layers=2, ridge_axis="x", roof_block=M.ROOF_DARK, ridge_block=M.GOLD)

    # ------------------------------------------------------------------
    # 6. Brocade display hall (锦缎展示堂): terraced platform, red walls,
    #    three brocade stands and hung tapestries under a green hip roof.
    # ------------------------------------------------------------------
    add_platform_with_steps(fills, "zhijin hall terrace", TER_X1, TER_Z1, TER_X2, TER_Z2, 4, [(1, 0, M.STONE), (1, 2, M.SMOOTH)])
    add_fill(fills, "zhijin hall floor", (HALL_X1 + 2, 5, HALL_Z1 + 2), (HALL_X2 - 2, 5, HALL_Z2 - 2), M.WOOD)
    add_outline(fills, "zhijin hall walls", HALL_X1, HALL_Z1, HALL_X2, HALL_Z2, 6, 14, M.RED_WALL, thickness=2)
    add_fill(fills, "zhijin hall door s", (4996, 6, HALL_Z1), (5024, 11, HALL_Z1 + 1), M.AIR)
    add_fill(fills, "zhijin hall lintel s", (4994, 12, HALL_Z1), (5026, 12, HALL_Z1 + 1), LOG_X)
    add_fill(fills, "zhijin hall door n", (4996, 6, HALL_Z2 - 1), (5024, 11, HALL_Z2), M.AIR)
    add_fill(fills, "zhijin hall lintel n", (4994, 12, HALL_Z2 - 1), (5026, 12, HALL_Z2), LOG_X)
    add_fill(fills, "zhijin hall win s w", (4968, 10, HALL_Z1), (4988, 13, HALL_Z1 + 1), M.GLASS)
    add_fill(fills, "zhijin hall win s e", (5032, 10, HALL_Z1), (5052, 13, HALL_Z1 + 1), M.GLASS)
    # Three display stands: smooth stone block, gold border, brocade cloth.
    for si, cx in enumerate(STAND_XS):
        add_fill(fills, f"zhijin stand {si} base", (cx - 8, 6, STAND_Z1), (cx + 8, 7, STAND_Z2), M.SMOOTH)
        add_outline(fills, f"zhijin stand {si} gold border", cx - 8, STAND_Z1, cx + 8, STAND_Z2, 8, 8, M.GOLD, thickness=1)
        add_fill(fills, f"zhijin stand {si} brocade", (cx - 7, 8, STAND_Z1 + 1), (cx + 7, 8, STAND_Z2 - 1), M.RED_WOOL)
        add_fill(fills, f"zhijin stand {si} brocade gold", (cx - 7, 8, 1265), (cx + 7, 8, 1265), GOLD_WOOL)
        add_fill(fills, f"zhijin stand {si} brocade yellow", (cx + 3, 8, STAND_Z1 + 1), (cx + 3, 8, STAND_Z2 - 1), M.YELLOW_WOOL)
    # Four wool tapestries on wooden scroll rods along the side walls.
    for ti, (tx, tz1) in enumerate(((HALL_X1 + 2, 1240), (HALL_X1 + 2, 1276), (HALL_X2 - 2, 1240), (HALL_X2 - 2, 1276))):
        add_fill(fills, f"zhijin tapestry {ti} rod top", (tx, 12, tz1), (tx, 12, tz1 + 14), LOG_X)
        add_fill(fills, f"zhijin tapestry {ti} cloth", (tx, 8, tz1), (tx, 11, tz1 + 14), _TAPESTRY_COLORS[ti])
        add_fill(fills, f"zhijin tapestry {ti} rod bottom", (tx, 7, tz1), (tx, 7, tz1 + 14), LOG_X)
    add_hip_roof(fills, "zhijin hall roof", 4958, 1229, 5062, 1299, 15, layers=6, ridge_axis="x", roof_block=M.ROOF_GREEN, ridge_block=M.GOLD)

    # ------------------------------------------------------------------
    # 7. Dye vat court (染缸阵): eight stone-ringed vats of coloured dye
    #    and a bamboo drying frame with double-layer cloth bolts.
    # ------------------------------------------------------------------
    vi = 0
    for vz in VAT_ZS:
        for vx in VAT_XS:
            add_fill(fills, f"zhijin vat {vi} ring", (vx - 2, 4, vz - 2), (vx + 2, 5, vz + 2), M.SMOOTH)
            add_fill(fills, f"zhijin vat {vi} dye", (vx - 1, 4, vz - 1), (vx + 1, 4, vz + 1), _DYE_COLORS[vi])
            add_fill(fills, f"zhijin vat {vi} water", (vx - 1, 5, vz - 1), (vx + 1, 5, vz + 1), M.WATER)
            vi += 1
    # Bamboo drying poles and cross bars, hung with double-layer cloth.
    for px, pz in ((5106, BAMBOO_ZS[0]), (5106, BAMBOO_ZS[1]), (5128, BAMBOO_ZS[0]), (5128, BAMBOO_ZS[1])):
        add_fill(fills, f"zhijin bamboo pole {px},{pz}", (px, 4, pz), (px, 9, pz), M.LOG)
    for bz in BAMBOO_ZS:
        add_fill(fills, f"zhijin bamboo bar {bz}", (5106, 10, bz), (5128, 10, bz), LOG_X)
    for bi, (bx, bz, wool) in enumerate(_BAMBOO_CLOTHS):
        add_fill(fills, f"zhijin bamboo cloth {bi} front", (bx, 6, bz), (bx + 6, 9, bz), wool)
        add_fill(fills, f"zhijin bamboo cloth {bi} back", (bx, 6, bz + 1), (bx + 6, 8, bz + 1), wool)

    # ------------------------------------------------------------------
    # 8. Long drying racks (晾布长架): south yard, two post rows, three
    #    cross-bar layers, twelve staggered double-thickness cloth bolts.
    # ------------------------------------------------------------------
    for si, (rx1, rx2) in enumerate(((4892, 4964), (5056, 5128))):
        for px in (rx1, (rx1 + rx2) // 2, rx2):
            for pz in RACK_ROWS:
                add_fill(fills, f"zhijin rack post {si} {px},{pz}", (px, 4, pz), (px, 12, pz), M.LOG)
        for by in (7, 9, 11):
            add_fill(fills, f"zhijin rack bar {si} n {by}", (rx1, by, RACK_ROWS[0]), (rx2, by, RACK_ROWS[0]), LOG_X)
            add_fill(fills, f"zhijin rack bar {si} s {by}", (rx1, by, RACK_ROWS[1]), (rx2, by, RACK_ROWS[1]), LOG_X)
        for ci, (bx, by, bz, col) in enumerate(_RACK_CLOTHS[si]):
            add_fill(fills, f"zhijin rack cloth {si} {ci}", (bx, by, bz), (bx + 8, by + 2, bz + 1), _RACK_COLORS[col])

    # ------------------------------------------------------------------
    # 9. Dye storehouse (染料库房): north-east corner shed with a barrel
    #    array and wool pigment piles.
    # ------------------------------------------------------------------
    add_hollow_box(fills, "zhijin store shell", STORE_X1, 4, STORE_Z1, STORE_X2, 10, STORE_Z2, M.WHITE_TERRACOTTA, thickness=1)
    add_fill(fills, "zhijin store floor", (STORE_X1 + 1, 4, STORE_Z1 + 1), (STORE_X2 - 1, 4, STORE_Z2 - 1), M.WOOD)
    add_fill(fills, "zhijin store door", (5110, 5, STORE_Z1), (5118, 8, STORE_Z1), M.AIR)
    add_ridge_roof(fills, "zhijin store roof", STORE_X1 - 3, STORE_Z1 - 3, STORE_X2 + 3, STORE_Z2 + 3, 11, layers=2, ridge_axis="z", roof_block=M.ROOF_DARK, ridge_block=M.GOLD)
    add_fill(fills, "zhijin dye barrels", (5108, 5, 1354), (5109, 5, 1356), BARREL)
    add_fill(fills, "zhijin dye pile red", (5112, 5, 1354), (5113, 6, 1355), M.RED_WOOL)
    add_fill(fills, "zhijin dye pile yellow", (5116, 5, 1354), (5117, 6, 1355), M.YELLOW_WOOL)
    add_fill(fills, "zhijin dye pile green", (5120, 5, 1354), (5121, 6, 1355), M.GREEN_WOOL)
    add_fill(fills, "zhijin dye pile blue", (5112, 5, 1360), (5113, 6, 1361), M.BLUE_WOOL)

    # ------------------------------------------------------------------
    # 10. Well (水井): stone-curbed well under a gilded pyramid roof.
    # ------------------------------------------------------------------
    for wi, (wx, wz) in enumerate(((4921, 1201), (4929, 1201), (4921, 1209), (4929, 1209))):
        add_fill(fills, f"zhijin well column {wi}", (wx, 4, wz), (wx, 10, wz), M.RED_WALL)
    add_outline(fills, "zhijin well curb", 4922, 1202, 4928, 1208, 4, 5, M.STONE, thickness=1)
    add_fill(fills, "zhijin well water", (4923, 4, 1203), (4927, 4, 1207), M.WATER)
    add_pyramid_roof(fills, "zhijin well roof", WELL_CX, WELL_CZ, radius=4, y=11, roof_block=M.ROOF_GREEN, apex_block=M.GOLD)

    # ------------------------------------------------------------------
    # 11. Mulberry avenue (桑树两列) and the lantern-lined axis approach.
    # ------------------------------------------------------------------
    for ti, (tx, tz) in enumerate((
        (4980, 1142), (4980, 1172), (4980, 1202),
        (5040, 1142), (5040, 1172), (5040, 1202),
    )):
        add_tree(fills, f"zhijin mulberry {ti}", tx, tz, 4, height=8, spread=4)
    add_lantern_line(fills, "zhijin axis lantern w", 4994, 1136, 4994, 1226, 4, 45)
    add_lantern_line(fills, "zhijin axis lantern e", 5026, 1136, 5026, 1226, 4, 45)


def main() -> None:
    run_builder(build_zhijinfang_3d, "zhijinfang_3d")


if __name__ == "__main__":
    main()
