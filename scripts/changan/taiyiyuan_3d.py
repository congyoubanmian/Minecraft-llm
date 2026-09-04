from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    Fill,
    Materials as M,
    add_column_grid,
    add_fill,
    add_hip_roof,
    add_hollow_box,
    add_lantern_line,
    add_outline,
    add_platform_with_steps,
    add_pyramid_roof,
    add_ridge_roof,
    run_builder,
)


"""
Taiyiyuan 3D (太医署·医药学府) - the Tang imperial medical academy and
royal pharmacy in the eastern imperial city, the state medical school and
dispensary that trained the court physicians (world's earliest recorded
state medical academy).

Location in Chang'an city local coordinates:
    Plot: x 3550..3850, z 900..1250 (strict bounds - nothing may leave
    them). The Douting Post stands 250 blocks further south (z 1500..1800),
    the Zhuque Avenue watchtowers near x 2900..3100, so nothing conflicts.
    Ground is graded to stone y0..1 + grass y2..3 (walking surface y4); the
    main structures rise from y5. Orientation follows the city convention:
    the walled compound is entered through the gate tower in the entrance
    (south) wall at the z-min edge, carrying the gold "太医署" plaque; the
    Lecture Hall (医术大堂) closes the north end of the axis at
    x 3600..3780, z 1100..1200 with its front turned to the court.

Distinctive features:
    - Rammed-earth compound wall (white terracotta + deepslate coping) with
      a bastion gate tower: arched passage, timber gate leaves, dark gable
      roof with gold ridge finials and a three-character gold name plaque
    - Lecture Hall (医术大堂): two-tier terraced platform, red walls, a log
      colonnade and a double-eave silhouette - hand-stepped hip skirt plus
      a gilded hip roof (庑殿顶) over a red upper storey
    - Bronze acupuncture man (针灸铜人) on the hall dais: a quartz figure
      with gold meridian lines on a wooden pedestal, beside the lecturer's
      lectern (讲席) and rows of student desks
    - Grand Pharmacy (百子柜药房) in the east wing: a full wall of drawer
      cabinets (wood frame, 5 rows x 8 columns of barred / coloured wool
      doors), counter with herb grinder (药碾), beam balance (药戥) and a
      charcoal burner, plus barrel / chest / bookshelf stores
    - Herb garden (百草药圃): two 3x4 grids of 24 drug beds flanking the
      axis, each bed a different "herb" (azalea / cherry leaves / coloured
      wool flower clusters), stone paths, fence rails and a wooden marker
      sign for every bed
    - Drying rack (晾药架): three layers of timber poles with six coloured
      wool medicine bags hung beneath
    - Decoction shed (煎药处) behind the pharmacy: twin stoves (barrel +
      sea-lantern fire core), a stone-ringed water vat and a firewood pile
    - Chancellor's court (署丞院) in the north-west corner: fenced yard,
      hall with bookshelf wall, medicine cabinet, stone table and stools
    - Well pavilion on four red columns under a gilded pyramid roof, a
      lantern-lined axis approach, and one blossoming apricot tree
      ("誉满杏林", cherry-leaves crown) by the path fork
"""

# ---------------------------------------------------------------------------
# Site: east imperial city medical academy plot (strict bounds).
# ---------------------------------------------------------------------------
SITE_X1, SITE_X2 = 3550, 3850
SITE_Z1, SITE_Z2 = 900, 1250

# Compound wall (outer face) and coping level.
WALL_X1, WALL_Z1 = 3565, 915
WALL_X2, WALL_Z2 = 3835, 1235
WALL_TOP_Y = 10

# Gate tower bastion, arched passage and upper gate hall (south entrance).
GB_X1, GB_Z1, GB_X2, GB_Z2 = 3660, 915, 3720, 930
ARCH_X1, ARCH_X2 = 3680, 3700
GH_X1, GH_Z1, GH_X2, GH_Z2 = 3666, 913, 3714, 932
GR_X1, GR_Z1, GR_X2, GR_Z2 = 3664, 911, 3716, 934

# Lecture hall (医术大堂), its deck, skirt, upper storey and hip roof.
TER_X1, TER_Z1, TER_X2, TER_Z2 = 3592, 1092, 3788, 1208
HALL_X1, HALL_Z1, HALL_X2, HALL_Z2 = 3600, 1100, 3780, 1200
HALL_TOP_Y = 16
DECK_Y = 17
US_X1, US_Z1, US_X2, US_Z2 = 3640, 1144, 3740, 1156
UR_X1, UR_Z1, UR_X2, UR_Z2 = 3634, 1140, 3746, 1160
ROOF_Y = 25
ROOF_LAYERS = 10

# Grand pharmacy (百子柜药房) in the east wing.
PH_X1, PH_Z1, PH_X2, PH_Z2 = 3786, 970, 3830, 1090

# Decoction shed (煎药处) behind the pharmacy.
DS_X1, DS_Z1, DS_X2, DS_Z2 = 3788, 934, 3830, 962

# Chancellor's court (署丞院) in the north-west strip.
SC_X1, SC_Z1, SC_X2, SC_Z2 = 3572, 1206, 3656, 1232
HS_X1, HS_Z1, HS_X2, HS_Z2 = 3584, 1214, 3644, 1231

# Herb gardens: two 3x4 bed grids flanking the gate axis (6 x 4 = 24 beds).
BED_W, BED_D = 20, 12
WEST_COLS = (3580, 3606, 3632)
EAST_COLS = (3728, 3754, 3780)
BED_ROWS = (940, 958, 976, 994)

# Drying rack, well pavilion and apricot tree.
RK_X1, RK_X2 = 3736, 3762
RK_Z1, RK_Z2 = 1019, 1039
WELL_CX, WELL_CZ = 3620, 1036
TREE_X, TREE_Z = 3662, 1052

# Direct-string blocks used by this module.
AZALEA = "minecraft:azalea_leaves"
FLOWERING_AZALEA = "minecraft:flowering_azalea_leaves"
CHERRY = "minecraft:cherry_leaves"
BOOKSHELF = "minecraft:bookshelf"
BARREL = "minecraft:barrel"
CHEST_W = "minecraft:chest[facing=west]"
LECTERN_S = "minecraft:lectern[facing=south]"
LOG_X = "minecraft:dark_oak_log[axis=x]"

_HERBS = (
    AZALEA, FLOWERING_AZALEA, CHERRY, M.RED_WOOL, M.PINK_WOOL,
    M.YELLOW_WOOL, M.BLUE_WOOL, M.GREEN_WOOL, M.WHITE_WOOL,
)
_CABINET_CELLS = (
    M.IRON_BARS, M.RED_WOOL, M.YELLOW_WOOL, M.GREEN_WOOL,
    M.BLUE_WOOL, M.WHITE_WOOL, M.PINK_WOOL, M.QUARTZ,
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
    stair_id = _ROOF_STAIRS.get(roof_block, _ROOF_STAIRS[M.ROOF_GREEN])
    return f"{stair_id}[facing={facing},half=bottom,shape=straight,waterlogged=false]"


def _herb_bed(fills: list[Fill], label: str, bx: int, bz: int, idx: int) -> None:
    """One drug bed: a block of "herb" plus a fence-post / board marker."""
    herb = _HERBS[idx % len(_HERBS)]
    add_fill(fills, f"{label} herb", (bx, 4, bz), (bx + BED_W - 1, 4, bz + BED_D - 1), herb)
    add_fill(fills, f"{label} sign post", (bx, 4, bz), (bx, 5, bz), M.FENCE)
    add_fill(fills, f"{label} sign board", (bx, 6, bz), (bx, 7, bz), M.WOOD)


def _acupuncture_figure(fills: list[Fill], label: str, cx: int, cz: int, base_y: int) -> None:
    """Bronze acupuncture man (针灸铜人): quartz figure, gold meridians."""
    add_fill(fills, f"{label} pedestal", (cx - 4, base_y, cz - 4), (cx + 4, base_y, cz + 4), M.WOOD)
    # Legs in a stance, torso, arms and head.
    add_fill(fills, f"{label} leg w", (cx - 2, base_y + 1, cz - 1), (cx - 1, base_y + 3, cz + 1), M.QUARTZ)
    add_fill(fills, f"{label} leg e", (cx + 1, base_y + 1, cz - 1), (cx + 2, base_y + 3, cz + 1), M.QUARTZ)
    add_fill(fills, f"{label} torso", (cx - 3, base_y + 4, cz - 2), (cx + 3, base_y + 5, cz + 2), M.QUARTZ)
    add_fill(fills, f"{label} arm w", (cx - 5, base_y + 4, cz - 1), (cx - 4, base_y + 5, cz + 1), M.QUARTZ)
    add_fill(fills, f"{label} arm e", (cx + 4, base_y + 4, cz - 1), (cx + 5, base_y + 5, cz + 1), M.QUARTZ)
    add_fill(fills, f"{label} head", (cx - 1, base_y + 6, cz - 1), (cx + 1, base_y + 7, cz + 1), M.QUARTZ)
    # Gold meridian lines down the chest and along the arms.
    add_fill(fills, f"{label} meridian mid", (cx, base_y + 4, cz - 2), (cx, base_y + 5, cz - 2), M.GOLD)
    add_fill(fills, f"{label} meridian w", (cx - 2, base_y + 4, cz - 2), (cx - 2, base_y + 5, cz - 2), M.GOLD)
    add_fill(fills, f"{label} meridian e", (cx + 2, base_y + 4, cz - 2), (cx + 2, base_y + 5, cz - 2), M.GOLD)
    add_fill(fills, f"{label} point w", (cx - 5, base_y + 4, cz), (cx - 5, base_y + 5, cz), M.GOLD)
    add_fill(fills, f"{label} point e", (cx + 5, base_y + 4, cz), (cx + 5, base_y + 5, cz), M.GOLD)
    # Small gold name plate on the pedestal front.
    add_fill(fills, f"{label} plate", (cx - 1, base_y + 1, cz - 4), (cx + 1, base_y + 1, cz - 4), M.GOLD)


# ---------------------------------------------------------------------------
# Main builder.
# ---------------------------------------------------------------------------
def build_taiyiyuan_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site grading: stone base, grass terrace, gate axis and service
    #    paths.
    # ------------------------------------------------------------------
    add_fill(fills, "taiyi clear site", (SITE_X1, 4, SITE_Z1), (SITE_X2, 7, SITE_Z2), M.AIR)
    add_fill(fills, "taiyi terrace stone", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "taiyi terrace grass", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)
    add_fill(fills, "taiyi approach pave", (3656, 3, 900), (3724, 3, 914), M.ANDESITE)
    add_fill(fills, "taiyi arch floor", (ARCH_X1, 3, GB_Z1), (ARCH_X2, 3, GB_Z2), M.ANDESITE)
    add_fill(fills, "taiyi axis path", (3678, 3, 931), (3702, 3, 1091), M.ANDESITE)
    add_fill(fills, "taiyi hall apron", (3660, 4, 1086), (3720, 4, 1091), M.STONE)
    add_fill(fills, "taiyi cross path", (3576, 3, 1046), (3782, 3, 1049), M.ANDESITE)
    add_fill(fills, "taiyi back path", (3660, 3, 1212), (3832, 3, 1215), M.ANDESITE)

    # ------------------------------------------------------------------
    # 2. Rammed-earth compound wall: white body, dark coping, buttresses.
    # ------------------------------------------------------------------
    add_outline(fills, "taiyi wall body", WALL_X1, WALL_Z1, WALL_X2, WALL_Z2, 4, 9, M.WHITE_TERRACOTTA, thickness=2)
    add_outline(fills, "taiyi wall coping", WALL_X1, WALL_Z1, WALL_X2, WALL_Z2, WALL_TOP_Y, WALL_TOP_Y, M.DARK, thickness=2)
    for bz in (1000, 1150):
        add_fill(fills, f"taiyi buttress w {bz}", (3567, 4, bz), (3568, 9, bz + 1), M.WHITE_TERRACOTTA)
        add_fill(fills, f"taiyi buttress e {bz}", (3832, 4, bz), (3833, 9, bz + 1), M.WHITE_TERRACOTTA)

    # ------------------------------------------------------------------
    # 3. South gate tower: bastion, arched passage, gate leaves, the gold
    #    "太医署" plaque, barred upper hall and a dark gable roof.
    # ------------------------------------------------------------------
    add_fill(fills, "taiyi gate bastion", (GB_X1, 4, GB_Z1), (GB_X2, 13, GB_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "taiyi gate arch", (ARCH_X1, 4, GB_Z1), (ARCH_X2, 11, GB_Z2), M.AIR)
    add_fill(fills, "taiyi gate lintel", (ARCH_X1 - 1, 11, GB_Z1), (ARCH_X2 + 1, 11, GB_Z2), LOG_X)
    add_fill(fills, "taiyi gate leaf w", (3680, 4, 915), (3685, 9, 916), M.WOOD)
    add_fill(fills, "taiyi gate leaf e", (3695, 4, 915), (3700, 9, 916), M.WOOD)
    add_fill(fills, "taiyi plaque frame", (3676, 11, 914), (3704, 15, 914), M.DARK)
    add_fill(fills, "taiyi plaque gold", (3680, 12, 914), (3700, 14, 914), M.GOLD)
    add_fill(fills, "taiyi plaque sep w", (3686, 12, 914), (3686, 14, 914), M.DARK)
    add_fill(fills, "taiyi plaque sep e", (3694, 12, 914), (3694, 14, 914), M.DARK)
    add_hollow_box(fills, "taiyi gate hall", GH_X1, 14, GH_Z1, GH_X2, 19, GH_Z2, M.RED_WALL, thickness=1)
    add_fill(fills, "taiyi gate bars n", (3670, 16, GH_Z1), (3710, 17, GH_Z1), M.IRON_BARS)
    add_fill(fills, "taiyi gate bars s", (3670, 16, GH_Z2), (3710, 17, GH_Z2), M.IRON_BARS)
    add_ridge_roof(fills, "taiyi gate roof", GR_X1, GR_Z1, GR_X2, GR_Z2, 20, layers=2, ridge_axis="x", roof_block=M.ROOF_DARK, ridge_block=M.GOLD)
    # Seal the two ridge-end notches the primitive leaves at the eave line.
    add_fill(fills, "taiyi gate ridge cap w", (GR_X1, 24, 922), (GR_X1 + 3, 24, 922), M.GOLD)
    add_fill(fills, "taiyi gate ridge cap e", (GR_X2 - 3, 24, 922), (GR_X2, 24, 922), M.GOLD)

    # ------------------------------------------------------------------
    # 4. Approach outside the gate: lamp posts flanking the paving.
    # ------------------------------------------------------------------
    for lx in (3662, 3718):
        for lz in (903, 910):
            add_fill(fills, f"taiyi approach lamp {lx},{lz}", (lx, 4, lz), (lx, 6, lz), M.FENCE)
            add_fill(fills, f"taiyi approach light {lx},{lz}", (lx, 7, lz), (lx, 7, lz), M.LANTERN)

    # ------------------------------------------------------------------
    # 5. Lecture hall (医术大堂): terraced platform, red walls, wood deck,
    #    hip skirt, colonnade, doors/windows, upper storey and the gilded
    #    hip roof (庑殿顶).
    # ------------------------------------------------------------------
    add_platform_with_steps(fills, "taiyi hall terrace", TER_X1, TER_Z1, TER_X2, TER_Z2, 4, [(1, 0, M.STONE), (1, 2, M.SMOOTH)])
    add_outline(fills, "taiyi hall walls", HALL_X1, HALL_Z1, HALL_X2, HALL_Z2, 6, HALL_TOP_Y, M.RED_WALL, thickness=2)
    add_fill(fills, "taiyi hall floor", (HALL_X1 + 2, 5, HALL_Z1 + 2), (HALL_X2 - 2, 5, HALL_Z2 - 2), M.WOOD)
    # Main doorway on the courtyard (south) face plus two side doors.
    add_fill(fills, "taiyi hall door main", (3676, 6, HALL_Z1), (3704, 12, HALL_Z1 + 1), M.AIR)
    add_fill(fills, "taiyi hall lintel", (3674, 13, HALL_Z1), (3706, 13, HALL_Z1 + 1), LOG_X)
    add_fill(fills, "taiyi hall door w", (3624, 6, HALL_Z1), (3638, 11, HALL_Z1 + 1), M.AIR)
    add_fill(fills, "taiyi hall door e", (3742, 6, HALL_Z1), (3756, 11, HALL_Z1 + 1), M.AIR)
    add_fill(fills, "taiyi hall window s w", (3644, 10, HALL_Z1), (3660, 13, HALL_Z1 + 1), M.GLASS)
    add_fill(fills, "taiyi hall window s e", (3720, 10, HALL_Z1), (3736, 13, HALL_Z1 + 1), M.GLASS)
    add_fill(fills, "taiyi hall window n w", (3654, 10, HALL_Z2 - 1), (3670, 13, HALL_Z2), M.GLASS)
    add_fill(fills, "taiyi hall window n e", (3710, 10, HALL_Z2 - 1), (3726, 13, HALL_Z2), M.GLASS)
    add_column_grid(fills, "taiyi hall columns", 3606, 1106, 3774, 1194, 6, HALL_TOP_Y, 85, M.LOG, column_size=1)
    # Wood deck closing the hall, then a hand-stepped hip skirt.
    add_fill(fills, "taiyi hall deck", (3596, DECK_Y, 1096), (3784, DECK_Y, 1204), M.WOOD)
    for i in range(3):
        sy = DECK_Y + 1 + i
        add_fill(fills, f"taiyi hall skirt n {i}", (3596 + i, sy, 1097 + i), (3784 - i, sy, 1097 + i), _stair(M.ROOF_GREEN, "south"))
        add_fill(fills, f"taiyi hall skirt s {i}", (3596 + i, sy, 1203 - i), (3784 - i, sy, 1203 - i), _stair(M.ROOF_GREEN, "north"))
        add_fill(fills, f"taiyi hall skirt w {i}", (3597 + i, sy, 1098 + i), (3597 + i, sy, 1202 - i), _stair(M.ROOF_GREEN, "east"))
        add_fill(fills, f"taiyi hall skirt e {i}", (3783 - i, sy, 1098 + i), (3783 - i, sy, 1202 - i), _stair(M.ROOF_GREEN, "west"))
    # Red upper storey carrying the hip roof.
    add_hollow_box(fills, "taiyi hall upper storey", US_X1, 18, US_Z1, US_X2, 24, US_Z2, M.RED_WALL, thickness=1)
    add_fill(fills, "taiyi upper win n", (3660, 19, US_Z1), (3670, 21, US_Z1), M.GLASS)
    add_fill(fills, "taiyi upper win s", (3660, 19, US_Z2), (3670, 21, US_Z2), M.GLASS)
    add_fill(fills, "taiyi upper win w", (US_X1, 19, 1146), (US_X1, 21, 1154), M.GLASS)
    add_fill(fills, "taiyi upper win e", (US_X2, 19, 1146), (US_X2, 21, 1154), M.GLASS)
    add_hip_roof(fills, "taiyi hall roof", UR_X1, UR_Z1, UR_X2, UR_Z2, ROOF_Y, layers=ROOF_LAYERS, ridge_axis="x", roof_block=M.ROOF_GREEN, ridge_block=M.GOLD)

    # ------------------------------------------------------------------
    # 6. Hall interior: teaching dais, lectern (讲席), lecturer's desk,
    #    student desk rows and the bronze acupuncture man (针灸铜人).
    # ------------------------------------------------------------------
    add_fill(fills, "taiyi dais", (3630, 6, 1166), (3750, 6, 1195), M.STONE)
    add_fill(fills, "taiyi lectern", (3676, 7, 1176), (3676, 7, 1176), LECTERN_S)
    add_fill(fills, "taiyi desk base", (3684, 7, 1172), (3700, 7, 1172 + 4), M.LOG)
    add_fill(fills, "taiyi desk top", (3684, 8, 1172), (3700, 8, 1176), M.WOOD)
    add_fill(fills, "taiyi desk scrolls", (3689, 9, 1173), (3691, 9, 1175), M.QUARTZ)
    for dz in (1120, 1140):
        for dx1, dx2 in ((3640, 3651), (3729, 3740)):
            add_fill(fills, f"taiyi student desk {dx1},{dz} base", (dx1, 6, dz), (dx2, 6, dz + 1), M.LOG)
            add_fill(fills, f"taiyi student desk {dx1},{dz} top", (dx1, 7, dz), (dx2, 7, dz + 1), M.WOOD)
    _acupuncture_figure(fills, "taiyi bronze man", 3646, 1182, 7)

    # ------------------------------------------------------------------
    # 7. Grand pharmacy (百子柜药房): east-wing shop with the full wall of
    #    drawer cabinets (5 rows x 8 columns), counter, grinder, balance,
    #    burner and stores.
    # ------------------------------------------------------------------
    add_hollow_box(fills, "taiyi pharmacy shell", PH_X1, 4, PH_Z1, PH_X2, 10, PH_Z2, M.WHITE_TERRACOTTA, thickness=1)
    add_fill(fills, "taiyi pharmacy floor", (PH_X1 + 1, 4, PH_Z1 + 1), (PH_X2 - 1, 4, PH_Z2 - 1), M.WOOD)
    add_fill(fills, "taiyi pharmacy door", (PH_X1, 5, 1020), (PH_X1, 8, 1032), M.AIR)
    add_fill(fills, "taiyi pharmacy win w n", (PH_X1, 7, 984), (PH_X1, 8, 994), M.GLASS)
    add_fill(fills, "taiyi pharmacy win w s", (PH_X1, 7, 1050), (PH_X1, 8, 1060), M.GLASS)
    add_fill(fills, "taiyi pharmacy win e n", (PH_X2, 7, 984), (PH_X2, 8, 994), M.GLASS)
    add_fill(fills, "taiyi pharmacy win e s", (PH_X2, 7, 1050), (PH_X2, 8, 1060), M.GLASS)
    add_ridge_roof(fills, "taiyi pharmacy roof", 3782, 966, 3834, 1094, 11, layers=2, ridge_axis="z", roof_block=M.ROOF_DARK, ridge_block=M.GOLD)
    add_fill(fills, "taiyi pharmacy roof seal", (3808, 14, 968), (3808, 14, 1092), M.ROOF_DARK)
    # Hundred-drawer cabinet (百子柜): wood panel + 5 x 8 cell doors.
    add_fill(fills, "taiyi cabinet panel", (3793, 5, PH_Z1 + 1), (3811, 12, PH_Z1 + 1), M.WOOD)
    for row in range(5):
        for col in range(8):
            cell = _CABINET_CELLS[(row + col) % len(_CABINET_CELLS)]
            add_fill(fills, f"taiyi cabinet cell r{row} c{col}", (3795 + 2 * col, 6 + row, PH_Z1 + 1), (3795 + 2 * col, 6 + row, PH_Z1 + 1), cell)
    # Counter and pharmacy tools in front of the cabinet wall.
    add_fill(fills, "taiyi counter base", (3790, 5, 974), (3814, 5, 975), M.LOG)
    add_fill(fills, "taiyi counter top", (3790, 6, 974), (3814, 6, 975), M.WOOD)
    add_fill(fills, "taiyi grinder trough", (3818, 5, 978), (3822, 5, 980), M.ANDESITE)
    add_fill(fills, "taiyi grinder roller", (3820, 6, 979), (3820, 6, 979), M.WOOD)
    add_fill(fills, "taiyi grinder handle w", (3817, 6, 979), (3817, 6, 979), M.LOG)
    add_fill(fills, "taiyi grinder handle e", (3823, 6, 979), (3823, 6, 979), M.LOG)
    add_fill(fills, "taiyi balance beam", (3796, 7, 974), (3802, 7, 974), LOG_X)
    add_fill(fills, "taiyi balance weight w", (3795, 7, 974), (3795, 7, 974), M.GOLD)
    add_fill(fills, "taiyi balance weight e", (3803, 7, 974), (3803, 7, 974), M.GOLD)
    add_fill(fills, "taiyi burner", (3810, 7, 975), (3810, 7, 975), BARREL)
    add_fill(fills, "taiyi burner fire", (3810, 8, 975), (3810, 8, 975), M.SEA_LANTERN)
    add_fill(fills, "taiyi store barrels", (3829, 5, 992), (3829, 6, 1022), BARREL)
    add_fill(fills, "taiyi store bookshelf", (3829, 5, 1026), (3829, 7, 1038), BOOKSHELF)
    add_fill(fills, "taiyi store chests", (3829, 5, 1042), (3829, 6, 1056), CHEST_W)

    # ------------------------------------------------------------------
    # 8. Herb garden (百草药圃): two 3x4 bed grids flanking the axis, with
    #    stone paths, fence rails, gates and one marker sign per bed.
    # ------------------------------------------------------------------
    for gi, (cols, gx1, gx2) in enumerate(((WEST_COLS, 3578, 3653), (EAST_COLS, 3726, 3801))):
        add_outline(fills, f"taiyi garden fence {gi}", gx1, 938, gx2, 1007, 4, 5, M.FENCE, thickness=1)
        add_fill(fills, f"taiyi garden gate {gi}", (gx2 if gi == 0 else gx1, 4, 968), (gx2 if gi == 0 else gx1, 5, 976), M.AIR)
        add_fill(fills, f"taiyi garden path v1 {gi}", (cols[0] + BED_W + 2, 3, 940), (cols[0] + BED_W + 5, 3, 1005), M.ANDESITE)
        add_fill(fills, f"taiyi garden path v2 {gi}", (cols[1] + BED_W + 2, 3, 940), (cols[1] + BED_W + 5, 3, 1005), M.ANDESITE)
        for ri, gz in ((0, 953), (1, 971), (2, 989)):
            add_fill(fills, f"taiyi garden path h {gi},{ri}", (cols[0], 3, gz), (cols[2] + BED_W - 1, 3, gz + 3), M.ANDESITE)
        idx = gi * 12
        for row, bz in enumerate(BED_ROWS):
            for col, bx in enumerate(cols):
                _herb_bed(fills, f"taiyi bed {idx}", bx, bz, idx)
                idx += 1

    # ------------------------------------------------------------------
    # 9. Drying rack (晾药架): three pole layers, six wool medicine bags.
    # ------------------------------------------------------------------
    for px in (RK_X1 + 1, RK_X2 - 1):
        for pz in (RK_Z1, RK_Z2):
            add_fill(fills, f"taiyi rack post {px},{pz}", (px, 4, pz), (px, 9, pz), M.LOG)
    for py in (7, 8, 9):
        add_fill(fills, f"taiyi rack pole n {py}", (RK_X1 + 1, py, RK_Z1), (RK_X2 - 1, py, RK_Z1), LOG_X)
        add_fill(fills, f"taiyi rack pole s {py}", (RK_X1 + 1, py, RK_Z2), (RK_X2 - 1, py, RK_Z2), LOG_X)
    for bi, (bx, wool) in enumerate(((3743, M.RED_WOOL), (3749, M.YELLOW_WOOL), (3755, M.GREEN_WOOL))):
        add_fill(fills, f"taiyi rack bag n {bi}", (bx, 5, RK_Z1), (bx, 6, RK_Z1), wool)
    for bi, (bx, wool) in enumerate(((3743, M.BLUE_WOOL), (3749, M.WHITE_WOOL), (3755, M.PINK_WOOL))):
        add_fill(fills, f"taiyi rack bag s {bi}", (bx, 5, RK_Z2), (bx, 6, RK_Z2), wool)

    # ------------------------------------------------------------------
    # 10. Decoction shed (煎药处): twin stoves, water vat, firewood pile.
    # ------------------------------------------------------------------
    add_fill(fills, "taiyi shed pave", (DS_X1, 3, DS_Z1), (DS_X2, 3, DS_Z2), M.ANDESITE)
    add_fill(fills, "taiyi shed back wall", (DS_X1, 4, DS_Z1), (DS_X2, 8, DS_Z1 + 1), M.WOOD)
    add_fill(fills, "taiyi shed post w", (DS_X1 + 1, 4, DS_Z2 - 1), (DS_X1 + 1, 8, DS_Z2 - 1), M.LOG)
    add_fill(fills, "taiyi shed post e", (DS_X2 - 1, 4, DS_Z2 - 1), (DS_X2 - 1, 8, DS_Z2 - 1), M.LOG)
    add_fill(fills, "taiyi shed roof", (DS_X1 - 2, 9, DS_Z1 - 2), (DS_X2 + 2, 9, DS_Z2 + 2), M.ROOF_DARK)
    for sx in (3796, 3812):
        add_fill(fills, f"taiyi stove {sx}", (sx, 4, 944), (sx, 4, 944), BARREL)
        add_fill(fills, f"taiyi stove fire {sx}", (sx, 5, 944), (sx, 5, 944), M.SEA_LANTERN)
    add_outline(fills, "taiyi vat ring", 3798, 950, 3803, 955, 4, 5, M.SMOOTH, thickness=1)
    add_fill(fills, "taiyi vat water", (3799, 4, 951), (3802, 4, 954), M.WATER)
    add_fill(fills, "taiyi firewood base", (3818, 4, 948), (3828, 4, 951), LOG_X)
    add_fill(fills, "taiyi firewood top", (3820, 5, 949), (3826, 5, 950), LOG_X)

    # ------------------------------------------------------------------
    # 11. Chancellor's court (署丞院): fenced yard, hall with medicine
    #     bookshelf, cabinet, stone table and stools.
    # ------------------------------------------------------------------
    add_outline(fills, "taiyi court fence", SC_X1, SC_Z1, SC_X2, SC_Z2, 4, 6, M.FENCE, thickness=1)
    add_fill(fills, "taiyi court gate", (SC_X2, 4, 1216), (SC_X2, 6, 1220), M.AIR)
    add_hollow_box(fills, "taiyi court house", HS_X1, 4, HS_Z1, HS_X2, 9, HS_Z2, M.WHITE_TERRACOTTA, thickness=1)
    add_fill(fills, "taiyi court floor", (HS_X1 + 1, 4, HS_Z1 + 1), (HS_X2 - 1, 4, HS_Z2 - 1), M.WOOD)
    add_fill(fills, "taiyi court door", (3608, 5, HS_Z1), (3616, 7, HS_Z1), M.AIR)
    add_fill(fills, "taiyi court window s", (3626, 6, HS_Z1), (3636, 7, HS_Z1), M.GLASS)
    add_fill(fills, "taiyi court window w", (HS_X1, 6, 1220), (HS_X1, 7, 1226), M.GLASS)
    add_fill(fills, "taiyi court roof w", (HS_X1 - 2, 10, HS_Z1 - 1), (HS_X1 + 4, 10, HS_Z2 + 1), _stair(M.ROOF_DARK, "east"))
    add_fill(fills, "taiyi court roof e", (HS_X2 - 4, 10, HS_Z1 - 1), (HS_X2 + 2, 10, HS_Z2 + 1), _stair(M.ROOF_DARK, "west"))
    add_fill(fills, "taiyi court ridge", (HS_X1 + 5, 11, HS_Z1), (HS_X2 - 5, 11, HS_Z2 - 1), M.ROOF_DARK)
    add_fill(fills, "taiyi court bookshelf", (3586, 5, HS_Z2 - 1), (3620, 7, HS_Z2 - 1), BOOKSHELF)
    add_fill(fills, "taiyi court barrels", (3624, 5, HS_Z2 - 1), (3634, 6, HS_Z2 - 1), BARREL)
    add_fill(fills, "taiyi court cabinet", (3636, 5, 1228), (3642, 7, HS_Z2 - 1), M.WOOD)
    add_fill(fills, "taiyi cabinet top", (3636, 8, 1228), (3642, 8, HS_Z2 - 1), M.QUARTZ)
    add_fill(fills, "taiyi stone table base", (3600, 5, 1220), (3608, 5, 1222), M.ANDESITE)
    add_fill(fills, "taiyi stone table top", (3600, 6, 1220), (3608, 6, 1222), M.SMOOTH)
    add_fill(fills, "taiyi mortar", (3604, 7, 1221), (3604, 7, 1221), M.GOLD)
    add_fill(fills, "taiyi stool w", (3598, 5, 1221), (3598, 5, 1221), M.QUARTZ)
    add_fill(fills, "taiyi stool e", (3610, 5, 1221), (3610, 5, 1221), M.QUARTZ)

    # ------------------------------------------------------------------
    # 12. Well pavilion (井亭): stone-curbed well under a pyramid roof on
    #     four red columns.
    # ------------------------------------------------------------------
    for ci, (cx0, cz0) in enumerate(((3616, 1032), (3624, 1032), (3616, 1040), (3624, 1040))):
        add_fill(fills, f"taiyi well column {ci}", (cx0, 4, cz0), (cx0, 9, cz0), M.RED_WALL)
    add_outline(fills, "taiyi well curb", 3617, 1033, 3623, 1039, 4, 5, M.STONE, thickness=1)
    add_fill(fills, "taiyi well water", (3618, 4, 1034), (3622, 4, 1038), M.WATER)
    add_pyramid_roof(fills, "taiyi well roof", WELL_CX, WELL_CZ, radius=4, y=10, roof_block=M.ROOF_GREEN, apex_block=M.GOLD)

    # ------------------------------------------------------------------
    # 13. Apricot tree (誉满杏林) and the lantern-lined axis approach.
    # ------------------------------------------------------------------
    add_fill(fills, "taiyi apricot trunk", (TREE_X, 4, TREE_Z), (TREE_X, 11, TREE_Z), "minecraft:oak_log")
    add_fill(fills, "taiyi apricot crown", (TREE_X - 5, 10, TREE_Z - 5), (TREE_X + 5, 14, TREE_Z + 5), CHERRY)
    add_fill(fills, "taiyi apricot bloom", (TREE_X - 3, 15, TREE_Z - 3), (TREE_X + 3, 15, TREE_Z + 3), CHERRY)
    add_lantern_line(fills, "taiyi axis lantern w", 3672, 945, 3672, 1065, 4, 60)
    add_lantern_line(fills, "taiyi axis lantern e", 3708, 945, 3708, 1065, 4, 60)


def main() -> None:
    run_builder(build_taiyiyuan_3d, "taiyiyuan_3d")


if __name__ == "__main__":
    main()
