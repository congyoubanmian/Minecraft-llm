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
    add_pool,
    add_pyramid_roof,
    add_ridge_roof,
    add_tree,
    run_builder,
)


"""
Tangchang Guan 3D (唐昌观·玉蕊花) - the Daoist abbey of Tangchang, home of
the single legendary Yurui ("jade-stamen") flower tree of Chang'an. When it
bloomed the whole city poured in to admire it, and poets - Yuan Zhen and
Bai Juyi above all - covered the abbey walls with verses.

Location in Chang'an city local coordinates:
    Plot: x 1150..1500, z 3120..3470, inside the western city. Hard
    boundary: nothing may be placed outside x 1150..1500 / z 3120..3470
    (all roof eaves and finials stay inside). Neighbours: the West Market
    qiting / taverns end at z <= 2970 to the north (no conflict);
    surrounding ward houses may be overwritten. Ground level y 0..4,
    main structures rise from y 5.

Distinctive features:
    - Site grading: stone base y0..1, lawn y2..3, white-walled precinct
      with a south mountain gate (gate tower + gable 悬山 roof + gilded
      "唐昌观" plaque)
    - Sacred Yurui tree (玉蕊神树) in the middle court at (1325, 3295):
      stout 2x2 dark-oak trunk y5..14, three-tier WHITE_WOOL + cherry
      crown (9/7/5 wide), hanging flower sprays, timber fence ring and
      four corner worship benches
    - Four radial fallen-petal paths (落花径): WHITE_WOOL / azalea-leaf
      stripes with polished-andesite kerbs
    - Sanqing Hall (三清殿) x 1240..1410, z 3370..3450: stepped platform,
      red-walled hall with doors on both faces, hip roof (庑殿顶), altar
      table, quartz Dao-Ancestor statue and divination-stick tubes (签筒)
    - Two poem-wall galleries (题诗壁廊) on the inner faces of the east
      and west precinct walls: 12 hanging wood poem boards (2x3) under a
      columned ridge roof, plus the Yuan-Bai poem stele (元白诗碑) with a
      quartz-pillar shaft and gilded cap at the corner
    - Flower-goddess shrine (花神小祠) south-east of the tree: pyramid
      roof (攒尖顶) on a small platform with white-flower offering plates
    - Sweeping-monk quarters (扫花僧舍) in the north-west corner: two
      cells, a broom rack (fence + planks) and yellow-flower brooms
    - Release pond (放生池) with lily pads, lantern-flanked walkways and
      two rows of cypresses
"""

# ---------------------------------------------------------------------------
# Site constants (local Chang'an coordinates; world = +9000/+64/+9000 via lib).
# ---------------------------------------------------------------------------
SITE_X1, SITE_Z1 = 1150, 3120
SITE_X2, SITE_Z2 = 1500, 3470

AXIS_X = 1325                        # central north-south axis of the abbey
TREE_X, TREE_Z = 1325, 3295          # sacred Yurui tree, centre of the court

GATE_X1, GATE_X2 = 1305, 1345        # south mountain gate opening

HALL_X1, HALL_Z1 = 1240, 3370        # Sanqing Hall platform
HALL_X2, HALL_Z2 = 1410, 3450
HALL_BODY_X1, HALL_BODY_Z1 = 1262, 3388
HALL_BODY_X2, HALL_BODY_Z2 = 1388, 3432

CORR_Z1, CORR_Z2 = 3230, 3430        # poem galleries along east/west walls
W_FLOOR_X1, W_FLOOR_X2 = 1153, 1173  # west gallery floor / column / boards
W_COL_X, W_BOARD_X = 1172, 1154
E_FLOOR_X1, E_FLOOR_X2 = 1477, 1497  # east gallery floor / column / boards
E_COL_X, E_BOARD_X = 1478, 1496

SHRINE_CX, SHRINE_CZ = 1385, 3351    # flower-goddess shrine centre

MONK_X1, MONK_Z1 = 1160, 3130        # sweeping-monk courtyard
MONK_X2, MONK_Z2 = 1250, 3220

POND_X1, POND_Z1 = 1425, 3166        # release pond
POND_X2, POND_Z2 = 1465, 3202

CHERRY = "minecraft:cherry_leaves"
AZALEA = "minecraft:azalea_leaves"
LILY_PAD = "minecraft:lily_pad"
QUARTZ_PILLAR = "minecraft:quartz_pillar[axis=y]"


# ---------------------------------------------------------------------------
# Local helpers.
# ---------------------------------------------------------------------------
def _petal_path(
    fills: list[Fill],
    label: str,
    run_lo: int, run_hi: int,
    w_lo: int, w_hi: int,
    axis: str,
) -> None:
    """Striped fallen-petal path: WHITE_WOOL / azalea leaves, stone kerbs.

    axis='z': the path runs along z (run = z range), width w = x range.
    axis='x': the path runs along x (run = x range), width w = z range.
    """
    if axis == "z":
        add_fill(fills, f"{label} kerb w", (w_lo - 1, 4, run_lo), (w_lo - 1, 4, run_hi), M.ANDESITE)
        add_fill(fills, f"{label} kerb e", (w_hi + 1, 4, run_lo), (w_hi + 1, 4, run_hi), M.ANDESITE)
    else:
        add_fill(fills, f"{label} kerb n", (run_lo, 4, w_lo - 1), (run_hi, 4, w_lo - 1), M.ANDESITE)
        add_fill(fills, f"{label} kerb s", (run_lo, 4, w_hi + 1), (run_hi, 4, w_hi + 1), M.ANDESITE)
    stripe_len = 12
    index, pos = 0, run_lo
    while pos <= run_hi:
        end = min(run_hi, pos + stripe_len - 1)
        block = M.WHITE_WOOL if index % 2 == 0 else AZALEA
        if axis == "z":
            add_fill(fills, f"{label} stripe {index}", (w_lo, 4, pos), (w_hi, 4, end), block)
        else:
            add_fill(fills, f"{label} stripe {index}", (pos, 4, w_lo), (end, 4, w_hi), block)
        pos = end + 1
        index += 1


def _poem_board(fills: list[Fill], label: str, x: int, z: int) -> None:
    """One hanging 2x3 wood poem board with a dark lintel cap."""
    add_fill(fills, f"{label} board", (x, 6, z), (x, 8, z + 1), M.WOOD)
    add_fill(fills, f"{label} cap", (x, 9, z), (x, 9, z + 1), M.DARK)


def _poem_gallery(
    fills: list[Fill],
    label: str,
    floor_x1: int, floor_x2: int,
    col_x: int, board_x: int,
    roof_x1: int, roof_x2: int,
) -> None:
    """Wall-side poem gallery: paving, log posts, boards, gable roof."""
    add_fill(fills, f"{label} floor", (floor_x1, 4, CORR_Z1), (floor_x2, 4, CORR_Z2), M.SMOOTH)
    for cz in range(CORR_Z1 + 8, CORR_Z2 - 4, 28):
        add_fill(fills, f"{label} post {cz}", (col_x, 5, cz), (col_x, 10, cz), M.LOG)
    add_fill(fills, f"{label} tie beam", (col_x, 11, CORR_Z1), (col_x, 11, CORR_Z2), M.LOG)
    for i, bz in enumerate(range(3262, 3413, 30)):
        _poem_board(fills, f"{label} poem {i}", board_x, bz)
    add_ridge_roof(fills, f"{label} roof", roof_x1, CORR_Z1 - 4, roof_x2, CORR_Z2 + 4,
                   12, layers=2, ridge_axis="z", roof_block=M.ROOF_GREEN)


def _monk_cell(
    fills: list[Fill],
    label: str,
    x1: int, z1: int, x2: int, z2: int,
) -> None:
    """One sweeping-monk cell: plank floor, red walls, bed, cushion, roof."""
    add_hollow_box(fills, f"{label} body", x1, 5, z1, x2, 11, z2, M.RED_WALL, thickness=1)
    add_fill(fills, f"{label} floor", (x1 + 1, 5, z1 + 1), (x2 - 1, 5, z2 - 1), M.WOOD)
    add_fill(fills, f"{label} door", (x1 + 12, 6, z2), (x1 + 22, 9, z2), M.AIR)
    add_fill(fills, f"{label} window", (x1 + 10, 7, z1), (x1 + 24, 9, z1), M.GLASS)
    add_fill(fills, f"{label} bed", (x1 + 3, 6, z1 + 2), (x1 + 7, 7, z1 + 10), M.WOOD)
    add_fill(fills, f"{label} cushion", (x1 + 16, 6, z1 + 8), (x1 + 18, 6, z1 + 10), M.PINK_WOOL)
    add_fill(fills, f"{label} lamp", (x2 - 4, 10, z2 - 4), (x2 - 4, 10, z2 - 4), M.SEA_LANTERN)
    add_ridge_roof(fills, f"{label} roof", x1 - 3, z1 - 3, x2 + 3, z2 + 3,
                   12, layers=1, ridge_axis="x", roof_block=M.ROOF_GREEN)


def build_tangchang_guan_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site grading: stone base y0..1, lawn y2..3, white precinct wall
    #    (stone plinth y4, white body y5..10, dark coping y11).
    # ------------------------------------------------------------------
    add_fill(fills, "tangchang foundation", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "tangchang lawn", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)
    add_fill(fills, "tangchang plinth n", (SITE_X1, 4, SITE_Z1), (SITE_X2, 4, SITE_Z1 + 2), M.STONE)
    add_fill(fills, "tangchang plinth s", (SITE_X1, 4, SITE_Z2 - 2), (SITE_X2, 4, SITE_Z2), M.STONE)
    add_fill(fills, "tangchang plinth w", (SITE_X1, 4, SITE_Z1), (SITE_X1 + 2, 4, SITE_Z2), M.STONE)
    add_fill(fills, "tangchang plinth e", (SITE_X2 - 2, 4, SITE_Z1), (SITE_X2, 4, SITE_Z2), M.STONE)
    add_fill(fills, "tangchang wall n", (SITE_X1, 5, SITE_Z1), (SITE_X2, 10, SITE_Z1 + 2), M.WHITE_TERRACOTTA)
    add_fill(fills, "tangchang wall s", (SITE_X1, 5, SITE_Z2 - 2), (SITE_X2, 10, SITE_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "tangchang wall w", (SITE_X1, 5, SITE_Z1), (SITE_X1 + 2, 10, SITE_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "tangchang wall e", (SITE_X2 - 2, 5, SITE_Z1), (SITE_X2, 10, SITE_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "tangchang coping n", (SITE_X1, 11, SITE_Z1), (SITE_X2, 11, SITE_Z1 + 2), M.DARK)
    add_fill(fills, "tangchang coping s", (SITE_X1, 11, SITE_Z2 - 2), (SITE_X2, 11, SITE_Z2), M.DARK)
    add_fill(fills, "tangchang coping w", (SITE_X1, 11, SITE_Z1), (SITE_X1 + 2, 11, SITE_Z2), M.DARK)
    add_fill(fills, "tangchang coping e", (SITE_X2 - 2, 11, SITE_Z1), (SITE_X2, 11, SITE_Z2), M.DARK)

    # South mountain gate: opening, landing, gilded "唐昌观" plaque, gate
    # tower with railing deck and a gable (悬山) roof.
    add_fill(fills, "tangchang gate opening", (GATE_X1, 4, SITE_Z2 - 2), (GATE_X2, 10, SITE_Z2), M.AIR)
    add_fill(fills, "tangchang gate landing", (GATE_X1, 4, 3461), (GATE_X2, 4, 3467), M.SMOOTH)
    add_fill(fills, "tangchang gate plaque", (1312, 8, SITE_Z2), (1338, 9, SITE_Z2), M.GOLD)
    add_fill(fills, "tangchang gate plaque sill", (1310, 7, SITE_Z2), (1340, 7, SITE_Z2), M.DARK)
    add_fill(fills, "tangchang gate plaque cap", (1310, 10, SITE_Z2), (1340, 10, SITE_Z2), M.DARK)
    add_fill(fills, "tangchang gate lamp w", (1307, 9, SITE_Z2 - 2), (1307, 9, SITE_Z2 - 2), M.LANTERN)
    add_fill(fills, "tangchang gate lamp e", (1343, 9, SITE_Z2 - 2), (1343, 9, SITE_Z2 - 2), M.LANTERN)
    add_fill(fills, "tangchang gate deck", (1298, 10, 3462), (1352, 10, 3468), M.WOOD)
    add_fill(fills, "tangchang gate rail n", (1298, 11, 3462), (1352, 11, 3462), M.FENCE)
    add_fill(fills, "tangchang gate rail s", (1298, 11, 3468), (1352, 11, 3468), M.FENCE)
    add_fill(fills, "tangchang gate body", (1298, 11, 3462), (1352, 13, 3468), M.RED_WALL)
    add_ridge_roof(fills, "tangchang gate roof", 1296, 3460, 1354, 3468, 14,
                   layers=1, ridge_axis="x", roof_block=M.ROOF_GREEN)

    # ------------------------------------------------------------------
    # 2. Axial causeway from the gate to the hall forecourt, with
    #    flanking lantern posts.
    # ------------------------------------------------------------------
    add_fill(fills, "tangchang causeway", (1317, 4, 3454), (1333, 4, 3467), M.SMOOTH)
    add_lantern_line(fills, "tangchang forecourt lantern w", 1314, 3458, 1314, 3464, 4, every=10)
    add_lantern_line(fills, "tangchang forecourt lantern e", 1336, 3458, 1336, 3464, 4, every=10)

    # ------------------------------------------------------------------
    # 3. The sacred Yurui tree (玉蕊神树): andesite plinth, stout 2x2
    #    trunk y5..14, three-tier white chenille crown (9/7/5 wide) with
    #    hanging sprays, fallen-petal carpet, fence ring and four
    #    worship benches.
    # ------------------------------------------------------------------
    add_fill(fills, "tangchang petal carpet", (1320, 4, 3290), (1330, 4, 3300), M.WHITE_WOOL)
    for dz in (-4, -2, 0, 2, 4):
        add_fill(fills, f"tangchang petal carpet stripe {dz}",
                 (1320, 4, TREE_Z + dz), (1330, 4, TREE_Z + dz), CHERRY)
    add_fill(fills, "tangchang tree plinth", (1322, 4, 3291), (1328, 4, 3297), M.ANDESITE)
    add_fill(fills, "tangchang tree trunk", (TREE_X - 1, 5, TREE_Z - 1), (TREE_X, 14, TREE_Z), M.LOG)
    # Crown tier 1 (9x9, y13..14): rows of wool, cross columns of cherry.
    for i, dz in enumerate(range(-4, 5)):
        block = M.WHITE_WOOL if i % 2 == 0 else CHERRY
        add_fill(fills, f"tangchang crown l1 row {dz}",
                 (TREE_X - 4, 13, TREE_Z + dz), (TREE_X + 4, 13, TREE_Z + dz), block)
    for i, dx in enumerate(range(-4, 5)):
        block = CHERRY if i % 2 == 0 else M.WHITE_WOOL
        add_fill(fills, f"tangchang crown l1 col {dx}",
                 (TREE_X + dx, 14, TREE_Z - 4), (TREE_X + dx, 14, TREE_Z + 4), block)
    # Crown tier 2 (7x7, y15..16).
    for i, dz in enumerate(range(-3, 4)):
        block = M.WHITE_WOOL if i % 2 == 0 else CHERRY
        add_fill(fills, f"tangchang crown l2 row {dz}",
                 (TREE_X - 3, 15, TREE_Z + dz), (TREE_X + 3, 15, TREE_Z + dz), block)
    for i, dx in enumerate(range(-3, 4)):
        block = CHERRY if i % 2 == 0 else M.WHITE_WOOL
        add_fill(fills, f"tangchang crown l2 col {dx}",
                 (TREE_X + dx, 16, TREE_Z - 3), (TREE_X + dx, 16, TREE_Z + 3), block)
    # Crown tier 3 (5x5, y17..18) plus cap and apex.
    for i, dz in enumerate(range(-2, 3)):
        block = M.WHITE_WOOL if i % 2 == 0 else CHERRY
        add_fill(fills, f"tangchang crown l3 row {dz}",
                 (TREE_X - 2, 17, TREE_Z + dz), (TREE_X + 2, 17, TREE_Z + dz), block)
    for i, dx in enumerate(range(-2, 3)):
        block = CHERRY if i % 2 == 0 else M.WHITE_WOOL
        add_fill(fills, f"tangchang crown l3 col {dx}",
                 (TREE_X + dx, 18, TREE_Z - 2), (TREE_X + dx, 18, TREE_Z + 2), block)
    add_fill(fills, "tangchang crown cap", (TREE_X - 1, 19, TREE_Z - 1), (TREE_X + 1, 19, TREE_Z + 1), M.WHITE_WOOL)
    add_fill(fills, "tangchang crown apex", (TREE_X, 20, TREE_Z), (TREE_X, 20, TREE_Z), CHERRY)
    # Hanging flower sprays at the four crown corners (three drops + tip).
    for i, (bx, bz) in enumerate(((1321, 3291), (1329, 3291), (1321, 3299), (1329, 3299))):
        spray = CHERRY if i % 2 == 0 else M.LEAVES
        add_fill(fills, f"tangchang tree spray {i}", (bx, 10, bz), (bx, 12, bz), spray)
        add_fill(fills, f"tangchang tree spray tip {i}", (bx, 9, bz), (bx, 9, bz), M.WHITE_WOOL)
    # Timber fence ring with a south viewing gap.
    add_outline(fills, "tangchang tree fence", TREE_X - 8, TREE_Z - 8, TREE_X + 8, TREE_Z + 8,
                4, 7, M.FENCE, thickness=1)
    add_fill(fills, "tangchang tree fence gap", (1323, 4, 3303), (1327, 7, 3303), M.AIR)
    # Four corner worship benches (四方朝拜石座) facing the tree.
    for i, (bx1, bz1, bx2, bz2, back_z) in enumerate((
        (1300, 3270, 1308, 3272, 3270),
        (1342, 3270, 1350, 3272, 3270),
        (1300, 3318, 1308, 3320, 3320),
        (1342, 3318, 1350, 3320, 3320),
    )):
        add_fill(fills, f"tangchang worship bench {i}", (bx1, 4, bz1), (bx2, 5, bz2), M.ANDESITE)
        add_fill(fills, f"tangchang worship back {i}", (bx1, 6, back_z), (bx2, 6, back_z), M.SMOOTH)

    # ------------------------------------------------------------------
    # 4. Four radial fallen-petal paths (落花径) with andesite kerbs.
    # ------------------------------------------------------------------
    _petal_path(fills, "tangchang petal path n", 3202, 3284, 1323, 1327, "z")
    _petal_path(fills, "tangchang petal path s", 3306, 3362, 1323, 1327, "z")
    _petal_path(fills, "tangchang petal path w", 1234, 1316, 3293, 3297, "x")
    _petal_path(fills, "tangchang petal path e", 1334, 1416, 3293, 3297, "x")

    # ------------------------------------------------------------------
    # 5. Sanqing Hall (三清殿): stepped platform, red hall body with
    #    doors on both faces, interior altar / statue / stick tubes, and
    #    a hip roof (庑殿顶).
    # ------------------------------------------------------------------
    add_platform_with_steps(fills, "tangchang hall platform", HALL_X1, HALL_Z1, HALL_X2, HALL_Z2, 4,
                            [(2, 0, M.STONE), (1, 4, M.SMOOTH)])
    add_fill(fills, "tangchang hall step s1", (1300, 5, 3451), (1350, 5, 3453), M.SMOOTH)
    add_fill(fills, "tangchang hall step s2", (1300, 4, 3454), (1350, 4, 3456), M.SMOOTH)
    add_fill(fills, "tangchang hall step n1", (1300, 5, 3367), (1350, 5, 3369), M.SMOOTH)
    add_fill(fills, "tangchang hall step n2", (1300, 4, 3364), (1350, 4, 3366), M.SMOOTH)
    add_hollow_box(fills, "tangchang hall body",
                   HALL_BODY_X1, 7, HALL_BODY_Z1, HALL_BODY_X2, 16, HALL_BODY_Z2,
                   M.RED_WALL, thickness=1)
    add_fill(fills, "tangchang hall floor", (1263, 7, 3389), (1387, 7, 3431), M.SMOOTH)
    # Hall columns: corners, quarter points and east/west midpoints.
    for i, (px, pz) in enumerate((
        (1262, 3388), (1288, 3388), (1362, 3388), (1388, 3388),
        (1262, 3431), (1288, 3431), (1362, 3431), (1388, 3431),
        (1262, 3410), (1388, 3410),
    )):
        add_fill(fills, f"tangchang hall col {i}", (px, 7, pz), (px + 1, 16, pz + 1), M.LOG)
    # Doors north (tree court) and south (gate forecourt), plaque, windows.
    add_fill(fills, "tangchang hall door s", (1310, 8, 3432), (1340, 12, 3432), M.AIR)
    add_fill(fills, "tangchang hall door n", (1310, 8, 3388), (1340, 12, 3388), M.AIR)
    add_fill(fills, "tangchang hall plaque", (1315, 13, 3432), (1335, 14, 3432), M.GOLD)
    add_fill(fills, "tangchang hall window w", (1262, 9, 3394), (1262, 12, 3406), M.GLASS)
    add_fill(fills, "tangchang hall window e", (1388, 9, 3394), (1388, 12, 3406), M.GLASS)
    add_fill(fills, "tangchang hall window s w", (1270, 9, 3432), (1286, 12, 3432), M.GLASS)
    add_fill(fills, "tangchang hall window s e", (1364, 9, 3432), (1380, 12, 3432), M.GLASS)
    add_fill(fills, "tangchang hall window n w", (1270, 9, 3388), (1286, 12, 3388), M.GLASS)
    add_fill(fills, "tangchang hall window n e", (1364, 9, 3388), (1380, 12, 3388), M.GLASS)
    # Interior: altar table, quartz Dao-Ancestor statue, stick tubes, lamps.
    add_fill(fills, "tangchang statue pedestal", (1322, 8, 3391), (1326, 8, 3395), M.DARK)
    add_fill(fills, "tangchang statue body", (1323, 9, 3392), (1325, 14, 3394), QUARTZ_PILLAR)
    add_fill(fills, "tangchang statue head", (1323, 15, 3392), (1325, 15, 3394), M.GOLD)
    add_fill(fills, "tangchang altar top", (1318, 9, 3400), (1330, 9, 3402), M.WOOD)
    add_fill(fills, "tangchang altar leg w", (1319, 8, 3401), (1319, 8, 3401), M.LOG)
    add_fill(fills, "tangchang altar leg e", (1329, 8, 3401), (1329, 8, 3401), M.LOG)
    add_fill(fills, "tangchang altar offering", (1323, 10, 3401), (1324, 10, 3401), M.GOLD)
    add_fill(fills, "tangchang stick tube a", (1336, 8, 3394), (1336, 8, 3394), "minecraft:barrel")
    add_fill(fills, "tangchang stick tube a sticks", (1336, 9, 3394), (1336, 11, 3394), M.IRON_BARS)
    add_fill(fills, "tangchang stick tube b", (1339, 8, 3396), (1339, 8, 3396), "minecraft:barrel")
    add_fill(fills, "tangchang stick tube b sticks", (1339, 9, 3396), (1339, 11, 3396), M.IRON_BARS)
    add_fill(fills, "tangchang hall lamp sw", (1268, 15, 3394), (1268, 15, 3394), M.SEA_LANTERN)
    add_fill(fills, "tangchang hall lamp ne", (1382, 15, 3426), (1382, 15, 3426), M.SEA_LANTERN)
    add_hip_roof(fills, "tangchang hall roof", 1256, 3382, 1394, 3438, 17,
                 layers=8, ridge_axis="x", roof_block=M.ROOF_GREEN)

    # ------------------------------------------------------------------
    # 6. Poem-wall galleries (题诗壁廊) inside the east and west walls,
    #    plus the Yuan-Bai poem stele (元白诗碑) at the corner.
    # ------------------------------------------------------------------
    _poem_gallery(fills, "tangchang poem gallery w",
                  W_FLOOR_X1, W_FLOOR_X2, W_COL_X, W_BOARD_X, 1152, 1174)
    _poem_gallery(fills, "tangchang poem gallery e",
                  E_FLOOR_X1, E_FLOOR_X2, E_COL_X, E_BOARD_X, 1476, 1498)
    add_fill(fills, "tangchang yuanbai stele base", (1487, 4, 3157), (1489, 4, 3159), M.DARK)
    add_fill(fills, "tangchang yuanbai stele shaft", (1487, 5, 3157), (1488, 12, 3158), QUARTZ_PILLAR)
    add_fill(fills, "tangchang yuanbai stele cap", (1486, 13, 3156), (1490, 13, 3160), M.GOLD)
    add_fill(fills, "tangchang yuanbai stele finial", (1487, 14, 3157), (1489, 14, 3159), M.GOLD)

    # ------------------------------------------------------------------
    # 7. Flower-goddess shrine (花神小祠) south-east of the tree: stone
    #    platform, red columns, pyramid roof, figure and white-flower
    #    offering plates.
    # ------------------------------------------------------------------
    add_fill(fills, "tangchang shrine platform", (1372, 4, 3338), (1398, 5, 3364), M.STONE)
    add_fill(fills, "tangchang shrine step", (1380, 4, 3365), (1390, 4, 3367), M.SMOOTH)
    add_fill(fills, "tangchang shrine floor", (1375, 6, 3341), (1395, 6, 3361), M.WOOD)
    for i, (px, pz) in enumerate(((1379, 3345), (1391, 3345), (1379, 3357), (1391, 3357))):
        add_fill(fills, f"tangchang shrine col {i}", (px, 7, pz), (px + 1, 12, pz + 1), M.RED_WALL)
    add_fill(fills, "tangchang shrine pedestal", (1384, 7, 3350), (1386, 7, 3352), M.SMOOTH)
    add_fill(fills, "tangchang shrine figure", (1385, 8, 3351), (1385, 10, 3351), M.WHITE_WOOL)
    add_fill(fills, "tangchang shrine figure head", (1385, 11, 3351), (1385, 11, 3351), M.PINK_WOOL)
    add_pyramid_roof(fills, "tangchang shrine roof", SHRINE_CX, SHRINE_CZ, 6, 13,
                     roof_block=M.ROOF_GREEN, apex_block=M.GOLD)
    for i, (ox, oz) in enumerate(((1378, 3358), (1384, 3359), (1389, 3358))):
        add_fill(fills, f"tangchang shrine offering {i}", (ox, 7, oz), (ox + 1, 7, oz + 1), M.WHITE_WOOL)

    # ------------------------------------------------------------------
    # 8. Sweeping-monk quarters (扫花僧舍) in the north-west corner:
    #    walled yard, two cells, broom rack and flower brooms.
    # ------------------------------------------------------------------
    add_fill(fills, "tangchang monk yard paving", (MONK_X1 + 2, 4, MONK_Z1 + 2),
             (MONK_X2 - 2, 4, MONK_Z2 - 2), M.SMOOTH)
    add_fill(fills, "tangchang monk yard wall n", (MONK_X1, 5, MONK_Z1), (MONK_X2, 8, MONK_Z1 + 1), M.WHITE_TERRACOTTA)
    add_fill(fills, "tangchang monk yard wall s", (MONK_X1, 5, MONK_Z2 - 1), (MONK_X2, 8, MONK_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "tangchang monk yard wall w", (MONK_X1, 5, MONK_Z1), (MONK_X1 + 1, 8, MONK_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "tangchang monk yard wall e", (MONK_X2 - 1, 5, MONK_Z1), (MONK_X2, 8, MONK_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "tangchang monk yard coping n", (MONK_X1, 9, MONK_Z1), (MONK_X2, 9, MONK_Z1 + 1), M.DARK)
    add_fill(fills, "tangchang monk yard coping s", (MONK_X1, 9, MONK_Z2 - 1), (MONK_X2, 9, MONK_Z2), M.DARK)
    add_fill(fills, "tangchang monk yard coping w", (MONK_X1, 9, MONK_Z1), (MONK_X1 + 1, 9, MONK_Z2), M.DARK)
    add_fill(fills, "tangchang monk yard coping e", (MONK_X2 - 1, 9, MONK_Z1), (MONK_X2, 9, MONK_Z2), M.DARK)
    add_fill(fills, "tangchang monk yard gate", (1196, 5, MONK_Z2 - 1), (1214, 8, MONK_Z2), M.AIR)
    add_fill(fills, "tangchang monk yard lintel", (1194, 9, MONK_Z2 - 1), (1216, 9, MONK_Z2), M.GOLD)
    _monk_cell(fills, "tangchang monk cell a", 1170, 3142, 1204, 3166)
    _monk_cell(fills, "tangchang monk cell b", 1170, 3184, 1204, 3208)
    # Broom rack and two yellow-flower brooms.
    add_fill(fills, "tangchang broom rack post w", (1216, 5, 3134), (1216, 8, 3134), M.FENCE)
    add_fill(fills, "tangchang broom rack post e", (1234, 5, 3134), (1234, 8, 3134), M.FENCE)
    add_fill(fills, "tangchang broom rack bar", (1213, 9, 3134), (1237, 9, 3134), M.WOOD)
    add_fill(fills, "tangchang broom a head", (1222, 5, 3137), (1222, 5, 3137), M.YELLOW_WOOL)
    add_fill(fills, "tangchang broom a handle", (1222, 6, 3137), (1222, 9, 3137), M.LOG)
    add_fill(fills, "tangchang broom b head", (1228, 5, 3137), (1228, 5, 3137), M.YELLOW_WOOL)
    add_fill(fills, "tangchang broom b handle", (1228, 6, 3137), (1228, 9, 3137), M.LOG)

    # ------------------------------------------------------------------
    # 9. Release pond (放生池) with stone rim and lily pads.
    # ------------------------------------------------------------------
    add_pool(fills, "tangchang release pond", POND_X1, POND_Z1, POND_X2, POND_Z2, 4, depth=1)
    add_outline(fills, "tangchang pond rim", POND_X1 - 2, POND_Z1 - 2, POND_X2 + 2, POND_Z2 + 2,
                4, 4, M.STONE, thickness=1)
    for i, (lx, lz) in enumerate(((1432, 3174), (1440, 3182), (1448, 3190), (1436, 3196), (1454, 3176))):
        add_fill(fills, f"tangchang lily pad {i}", (lx, 5, lz), (lx, 5, lz), LILY_PAD)

    # ------------------------------------------------------------------
    # 10. Lantern-flanked walkways in the north court and two rows of
    #     cypresses.
    # ------------------------------------------------------------------
    add_lantern_line(fills, "tangchang court lantern w", 1314, 3160, 1314, 3280, 4, every=30)
    add_lantern_line(fills, "tangchang court lantern e", 1336, 3160, 1336, 3280, 4, every=30)
    for i, tz in enumerate((3160, 3192, 3224, 3256, 3288)):
        add_tree(fills, f"tangchang cypress w{i}", 1298, tz, 4, height=7, spread=2)
        add_tree(fills, f"tangchang cypress e{i}", 1352, tz, 4, height=7, spread=2)


def main() -> None:
    run_builder(build_tangchang_guan_3d, "tangchang_guan_3d")


if __name__ == "__main__":
    main()
