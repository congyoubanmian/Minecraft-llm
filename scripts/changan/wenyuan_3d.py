from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    BASE_X,
    BASE_Z,
    Fill,
    Materials as M,
    add_fill,
    add_hollow_box,
    add_outline,
    add_pool,
    add_pyramid_roof,
    add_ridge_roof,
    run_builder,
)


"""
Wenyuan - Wangchuan Vistas (文人园·辋川意境) - a city private garden for
Tang literati that recreates four scenes from Wang Wei's "Wangchuan Ji"
(辋川集): Zhuli Lodge (竹里馆) hidden in a bamboo grove, the Deer
Enclosure (鹿柴), Magnolia Hollow (辛夷坞) with its blossom stream, and
the Lakeside Pavilion (临湖亭) on the central lake.

Location in Chang'an city local coordinates:
    parcel: x 2050..2400, z 1200..1550 (intra-mural ward district; may
    overwrite commoner houses - no known landmark conflicts).
    ground: stone base y0..1 with a grass cover y2..3; structures from y5.

Distinctive features:
    - No enclosure wall: the four scenes are separated softly by bamboo
      clumps, rockery groups and winding gravel walks, keeping the open
      feeling of a literati garden
    - Zhuli Lodge (竹里馆, "In a Bamboo Grove"): a raised timber platform
      ringed by an open colonnade, white walls under a gable (悬山) roof,
      a qin table with a golden zither and a lectern of poem scrolls,
      embraced by a dense grove of tall bamboo columns
    - Deer Enclosure (鹿柴, "Deer Park"): a low timber fence with a
      criss-cross rustic gate (柴扉), two recumbent sika-deer stone
      sculptures and scattered mossy rocks
    - Magnolia Hollow (辛夷坞, "Magnolia Dell"): five cherry trees in a
      ring inside a 1-wide blossom stream with pink petals adrift
    - Lakeside Pavilion (临湖亭): four red columns under a gilded pyramid
      roof (攒尖顶) on a stone pile platform in the lake centre, joined
      to the south shore by a double-bend zigzag bridge, lily pads adrift
    - Moon-Inviting Terrace (邀月台): two-tier stone platform with a low
      parapet, a sea-lantern "moon pool" inlay, a stone table and bench
    - Four andesite/moss rockery groups and a few scattered lanterns
"""


CHERRY = "minecraft:cherry_leaves"
LILY_PAD = "minecraft:lily_pad"
LECTERN = "minecraft:lectern"
CARPET = "minecraft:white_carpet"

# ---------------------------------------------------------------------------
# Site bounds (hard constraint: every fill must stay inside this parcel).
# ---------------------------------------------------------------------------
SITE_X1, SITE_X2 = 2050, 2400
SITE_Z1, SITE_Z2 = 1200, 1550

# Zhuli Lodge (竹里馆): raised timber platform in the north-west.
HUT_PLAT_X1, HUT_PLAT_Z1 = 2110, 1260
HUT_PLAT_X2, HUT_PLAT_Z2 = 2150, 1300
HUT_WALL_X1, HUT_WALL_Z1 = 2118, 1268
HUT_WALL_X2, HUT_WALL_Z2 = 2142, 1292

# Deer Enclosure (鹿柴) in the north-east.
DEER_X1, DEER_Z1 = 2305, 1208
DEER_X2, DEER_Z2 = 2392, 1288

# Magnolia Hollow (辛夷坞) in the south-east: blossom stream ring.
STREAM_X1, STREAM_Z1 = 2325, 1462
STREAM_X2, STREAM_Z2 = 2385, 1528

# Central lake and its lakeside pavilion.
LAKE_X1, LAKE_Z1, LAKE_X2, LAKE_Z2 = 2200, 1350, 2320, 1450
LAKE_WATER_Y = 1
PAV_CX, PAV_CZ = 2260, 1400

# Moon-Inviting Terrace (邀月台) west of the lake.
TERR_X1, TERR_Z1 = 2142, 1372
TERR_X2, TERR_Z2 = 2184, 1418

# Tall bamboo grove around the lodge: (x, z, height).
BAMBOO_GROVE = [
    # West / north-west ring hugging the lodge.
    (2062, 1210, 9), (2074, 1212, 12), (2088, 1208, 7), (2098, 1218, 10),
    (2060, 1226, 8), (2072, 1224, 13), (2086, 1230, 9), (2096, 1236, 12),
    (2058, 1240, 11), (2070, 1238, 7), (2084, 1244, 10), (2098, 1248, 8),
    (2062, 1252, 9), (2076, 1250, 12), (2090, 1256, 8), (2060, 1262, 12),
    (2072, 1260, 7), (2086, 1264, 11), (2098, 1258, 9), (2064, 1272, 8),
    (2078, 1274, 10), (2092, 1268, 13), (2058, 1280, 11), (2070, 1282, 8),
    (2084, 1278, 12), (2096, 1286, 9), (2062, 1292, 10), (2076, 1290, 7),
    (2088, 1296, 12), (2098, 1300, 8),
    # East side of the lodge.
    (2160, 1258, 10), (2172, 1264, 8), (2184, 1256, 12), (2194, 1268, 9),
    (2162, 1276, 7), (2176, 1280, 11), (2190, 1288, 8), (2160, 1292, 12),
    (2174, 1296, 9), (2188, 1300, 7),
    # South lawn between lodge and lake.
    (2120, 1310, 9), (2134, 1314, 7), (2148, 1310, 11), (2160, 1318, 8),
    (2108, 1318, 12), (2126, 1324, 10), (2142, 1320, 7), (2154, 1330, 9),
    (2114, 1332, 8), (2132, 1336, 12), (2146, 1334, 7), (2166, 1326, 10),
]

# Gravel walk: 2-wide straight legs at y3 (top of the grass cover).
PATH_SEGMENTS = [
    (2129, 1303, 2130, 1350),  # lodge porch winding south
    (2129, 1350, 2130, 1372),  # south to the moon terrace
    (2130, 1371, 2141, 1372),  # east into the moon terrace
    (2185, 1394, 2199, 1395),  # terrace east to the lake west shore
    (2346, 1289, 2347, 1330),  # deer gate south
    (2292, 1329, 2347, 1330),  # west toward the lake north-east
    (2292, 1330, 2293, 1349),  # south to the lake north shore
    (2321, 1452, 2334, 1453),  # lake south-east toward magnolia hollow
    (2333, 1453, 2334, 1460),  # south to the blossom stream bank
]

# Scattered garden lanterns along the walks (no long lamp rows).
LANTERN_SPOTS = [
    (2134, 1330),  # bamboo walk
    (2192, 1390),  # terrace-to-lake walk
    (2255, 1446),  # zigzag bridge landing
    (2360, 1456),  # magnolia hollow ford
    (2350, 1296),  # deer enclosure path
]


def _bamboo(fills: list[Fill], x: int, z: int, height: int) -> None:
    """One tall thin bamboo: a single column of oak leaves."""
    add_fill(fills, f"wenyuan bamboo {x},{z}", (x, 4, z), (x, 4 + height - 1, z), M.LEAVES)


def _cherry_tree(fills: list[Fill], x: int, z: int) -> None:
    """Cherry blossom tree: dark trunk with a cherry-leaf crown."""
    add_fill(fills, f"wenyuan cherry trunk {x},{z}", (x, 4, z), (x, 8, z), M.LOG)
    add_fill(fills, f"wenyuan cherry crown {x},{z}", (x - 2, 7, z - 2), (x + 2, 9, z + 2), CHERRY)
    add_fill(fills, f"wenyuan cherry top {x},{z}", (x - 1, 10, z - 1), (x + 1, 10, z + 1), CHERRY)


def _rockery(fills: list[Fill], tag: str, x: int, z: int) -> None:
    """A small stacked-stone rockery: mossy base, andesite body, peak."""
    add_fill(fills, f"wenyuan rockery {tag} base", (x, 4, z), (x + 2, 4, z + 1), M.MOSS_STONE)
    add_fill(fills, f"wenyuan rockery {tag} body", (x, 5, z), (x + 1, 6, z + 1), M.ANDESITE)
    add_fill(fills, f"wenyuan rockery {tag} peak", (x, 7, z), (x, 8, z), M.ANDESITE)
    add_fill(fills, f"wenyuan rockery {tag} accent", (x + 3, 4, z + 1), (x + 3, 4, z + 1), M.MOSS_STONE)


def _garden_lamp(fills: list[Fill], x: int, z: int) -> None:
    """Low garden lantern: smooth stone base with a lantern on top."""
    add_fill(fills, f"wenyuan lamp base {x},{z}", (x, 4, z), (x, 4, z), M.SMOOTH)
    add_fill(fills, f"wenyuan lamp light {x},{z}", (x, 5, z), (x, 5, z), M.LANTERN)


def _deer(fills: list[Fill], tag: str, x: int, z: int, facing: str) -> None:
    """Recumbent sika-deer stone sculpture: folded legs, body, neck,
    head and antlers. facing 'west' = head toward -x, 'east' = +x."""
    if facing == "west":
        leg_z1, leg_z2 = x + 8, x  # body runs from head (low x) to rump (high x)
        body_x1, body_x2 = x, x + 8
        rump_x1, rump_x2 = x + 6, x + 8
        neck_x1, neck_x2 = x, x + 1
        head_x1, head_x2 = x - 2, x
        tail_x = x + 9
        antler_a = (x - 2, z, x - 2, z + 1)
        antler_b = (x, z + 2, x, z + 2)
    else:
        body_x1, body_x2 = x, x + 8
        rump_x1, rump_x2 = x, x + 2
        neck_x1, neck_x2 = x + 7, x + 8
        head_x1, head_x2 = x + 8, x + 10
        tail_x = x - 1
        antler_a = (x + 10, z, x + 10, z + 1)
        antler_b = (x + 8, z + 2, x + 8, z + 2)
    # Folded legs (quartz) beneath the body.
    add_fill(fills, f"wenyuan deer {tag} legs", (body_x1, 4, z), (body_x2, 4, z + 2), M.QUARTZ)
    # Barrel body in white terracotta.
    add_fill(fills, f"wenyuan deer {tag} body", (body_x1, 5, z), (body_x2, 6, z + 2), M.WHITE_TERRACOTTA)
    # Raised rump of the lying pose.
    add_fill(fills, f"wenyuan deer {tag} rump", (rump_x1, 5, z - 1), (rump_x2, 7, z + 3), M.WHITE_TERRACOTTA)
    # Neck rising at the front.
    add_fill(fills, f"wenyuan deer {tag} neck", (neck_x1, 6, z), (neck_x2, 8, z + 2), M.WHITE_TERRACOTTA)
    # Head with quartz muzzle.
    add_fill(fills, f"wenyuan deer {tag} head", (head_x1, 8, z), (head_x2, 9, z + 2), M.QUARTZ)
    # Antlers.
    add_fill(fills, f"wenyuan deer {tag} antler a", (antler_a[0], 10, antler_a[1]), (antler_a[2], 11, antler_a[3]), M.QUARTZ)
    add_fill(fills, f"wenyuan deer {tag} antler b", (antler_b[0], 10, antler_b[1]), (antler_b[2], 11, antler_b[3]), M.QUARTZ)
    # Short tail.
    add_fill(fills, f"wenyuan deer {tag} tail", (tail_x, 6, z + 1), (tail_x, 6, z + 1), M.WHITE_TERRACOTTA)


def build_wenyuan_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site preparation: stone base y0..1 plus grass cover y2..3.
    #    No enclosure wall - soft bamboo / rockery / path separation only.
    # ------------------------------------------------------------------
    add_fill(fills, "wenyuan site stone base", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "wenyuan site grass cover", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)

    # ------------------------------------------------------------------
    # 2. Central lake (湖心): water surface y1, two blocks deep.
    # ------------------------------------------------------------------
    add_fill(fills, "wenyuan lake clear", (LAKE_X1, 2, LAKE_Z1), (LAKE_X2, 3, LAKE_Z2), M.AIR)
    add_pool(fills, "wenyuan lake", LAKE_X1, LAKE_Z1, LAKE_X2, LAKE_Z2, LAKE_WATER_Y, depth=2, floor_block=M.SMOOTH)
    add_outline(fills, "wenyuan lake embankment", LAKE_X1, LAKE_Z1, LAKE_X2, LAKE_Z2, 2, 3, M.STONE, thickness=2)

    # ------------------------------------------------------------------
    # 3. Lakeside Pavilion (临湖亭) on a stone pile platform at the lake
    #    centre: four red columns under a gilded pyramid roof (攒尖顶).
    # ------------------------------------------------------------------
    for px in (PAV_CX - 7, PAV_CX + 5):
        for pz in (PAV_CZ - 7, PAV_CZ + 5):
            add_fill(fills, f"wenyuan lake pavilion pile {px},{pz}", (px, 0, pz), (px + 1, 1, pz + 1), M.STONE)
    add_fill(fills, "wenyuan lake pavilion platform", (PAV_CX - 7, 2, PAV_CZ - 7), (PAV_CX + 7, 3, PAV_CZ + 7), M.STONE)
    add_fill(fills, "wenyuan lake pavilion motif", (PAV_CX - 1, 3, PAV_CZ - 1), (PAV_CX + 1, 3, PAV_CZ + 1), M.GOLD)
    # Railing on three sides; the south side stays open for the bridge.
    add_fill(fills, "wenyuan lake pavilion rail n", (PAV_CX - 7, 4, PAV_CZ - 7), (PAV_CX + 7, 4, PAV_CZ - 7), M.FENCE)
    add_fill(fills, "wenyuan lake pavilion rail w", (PAV_CX - 7, 4, PAV_CZ - 6), (PAV_CX - 7, 4, PAV_CZ + 7), M.FENCE)
    add_fill(fills, "wenyuan lake pavilion rail e", (PAV_CX + 7, 4, PAV_CZ - 6), (PAV_CX + 7, 4, PAV_CZ + 7), M.FENCE)
    for px in (PAV_CX - 6, PAV_CX + 5):
        for pz in (PAV_CZ - 6, PAV_CZ + 5):
            add_fill(fills, f"wenyuan lake pavilion column {px},{pz}", (px, 4, pz), (px + 1, 10, pz + 1), M.RED_WALL)
    add_pyramid_roof(fills, "wenyuan lake pavilion roof", PAV_CX, PAV_CZ, radius=7, y=11, roof_block=M.ROOF_GREEN, apex_block=M.GOLD)

    # ------------------------------------------------------------------
    # 4. Double-bend zigzag bridge (曲桥双折) from the south shore.
    # ------------------------------------------------------------------
    # Leg 1: south-east straight run from the shore.
    add_fill(fills, "wenyuan bridge leg1 deck", (2259, 3, 1430), (2261, 3, 1450), M.WOOD)
    add_fill(fills, "wenyuan bridge leg1 rail w", (2258, 4, 1431), (2258, 4, 1450), M.FENCE)
    add_fill(fills, "wenyuan bridge leg1 rail e", (2262, 4, 1431), (2262, 4, 1450), M.FENCE)
    add_fill(fills, "wenyuan bridge leg1 pile", (2259, 0, 1440), (2260, 2, 1441), M.LOG)
    # Leg 2: first bend, running west.
    add_fill(fills, "wenyuan bridge leg2 deck", (2248, 3, 1427), (2263, 3, 1429), M.WOOD)
    add_fill(fills, "wenyuan bridge leg2 rail n", (2252, 4, 1426), (2263, 4, 1426), M.FENCE)
    add_fill(fills, "wenyuan bridge leg2 rail s w", (2248, 4, 1430), (2257, 4, 1430), M.FENCE)
    add_fill(fills, "wenyuan bridge leg2 rail s e", (2263, 4, 1430), (2263, 4, 1430), M.FENCE)
    add_fill(fills, "wenyuan bridge leg2 pile", (2255, 0, 1427), (2256, 2, 1428), M.LOG)
    # Leg 3: second bend, running north to the pavilion.
    add_fill(fills, "wenyuan bridge leg3 deck", (2249, 3, 1407), (2251, 3, 1426), M.WOOD)
    add_fill(fills, "wenyuan bridge leg3 rail w", (2248, 4, 1407), (2248, 4, 1425), M.FENCE)
    add_fill(fills, "wenyuan bridge leg3 rail e", (2252, 4, 1407), (2252, 4, 1425), M.FENCE)
    add_fill(fills, "wenyuan bridge leg3 pile", (2250, 0, 1414), (2251, 2, 1415), M.LOG)

    # ------------------------------------------------------------------
    # 5. Lily pads adrift on the lake.
    # ------------------------------------------------------------------
    for i, (lx, lz) in enumerate([
        (2225, 1370), (2216, 1402), (2244, 1420), (2280, 1378),
        (2300, 1432), (2290, 1362), (2266, 1440), (2308, 1398),
    ]):
        add_fill(fills, f"wenyuan lily pad {i}", (lx, LAKE_WATER_Y, lz), (lx, LAKE_WATER_Y, lz), LILY_PAD)

    # ------------------------------------------------------------------
    # 6. Gravel walks (碎石曲径) linking the four scenes.
    # ------------------------------------------------------------------
    for i, (x1, z1, x2, z2) in enumerate(PATH_SEGMENTS):
        add_fill(fills, f"wenyuan walk {i}", (x1, 3, z1), (x2, 3, z2), M.ANDESITE)

    # ------------------------------------------------------------------
    # 7. Zhuli Lodge (竹里馆): raised timber platform, veranda colonnade,
    #    white walls, gable roof, qin table and poetry lectern.
    # ------------------------------------------------------------------
    add_fill(fills, "wenyuan hut platform", (HUT_PLAT_X1, 4, HUT_PLAT_Z1), (HUT_PLAT_X2, 5, HUT_PLAT_Z2), M.WOOD)
    add_fill(fills, "wenyuan hut floor", (HUT_WALL_X1 + 1, 5, HUT_WALL_Z1 + 1), (HUT_WALL_X2 - 1, 5, HUT_WALL_Z2 - 1), M.SMOOTH)
    add_outline(fills, "wenyuan hut apron", HUT_PLAT_X1 - 2, HUT_PLAT_Z1 - 2, HUT_PLAT_X2 + 2, HUT_PLAT_Z2 + 2, 4, 4, M.SMOOTH, thickness=1)
    add_fill(fills, "wenyuan hut step", (2126, 4, HUT_PLAT_Z2 + 1), (2134, 4, HUT_PLAT_Z2 + 2), M.WOOD)
    # White-walled hall.
    add_hollow_box(fills, "wenyuan hut walls", HUT_WALL_X1, 6, HUT_WALL_Z1, HUT_WALL_X2, 11, HUT_WALL_Z2, M.WHITE_TERRACOTTA, thickness=1)
    add_fill(fills, "wenyuan hut interior", (HUT_WALL_X1 + 1, 6, HUT_WALL_Z1 + 1), (HUT_WALL_X2 - 1, 10, HUT_WALL_Z2 - 1), M.AIR)
    add_fill(fills, "wenyuan hut door s", (2126, 6, HUT_WALL_Z2), (2134, 9, HUT_WALL_Z2), M.AIR)
    add_fill(fills, "wenyuan hut door e", (HUT_WALL_X2, 6, 1276), (HUT_WALL_X2, 9, 1284), M.AIR)
    add_fill(fills, "wenyuan hut window n", (2124, 8, HUT_WALL_Z1), (2136, 9, HUT_WALL_Z1), M.GLASS)
    add_fill(fills, "wenyuan hut window w", (HUT_WALL_X1, 8, 1274), (HUT_WALL_X1, 9, 1286), M.GLASS)
    # Veranda colonnade around the platform edge.
    for hx in range(HUT_PLAT_X1, HUT_PLAT_X2 + 1, 10):
        add_fill(fills, f"wenyuan hut post n {hx}", (hx, 6, HUT_PLAT_Z1), (hx, 8, HUT_PLAT_Z1), M.LOG)
        add_fill(fills, f"wenyuan hut post s {hx}", (hx, 6, HUT_PLAT_Z2), (hx, 8, HUT_PLAT_Z2), M.LOG)
    for hz in range(HUT_PLAT_Z1 + 10, HUT_PLAT_Z2, 10):
        add_fill(fills, f"wenyuan hut post w {hz}", (HUT_PLAT_X1, 6, hz), (HUT_PLAT_X1, 8, hz), M.LOG)
        add_fill(fills, f"wenyuan hut post e {hz}", (HUT_PLAT_X2, 6, hz), (HUT_PLAT_X2, 8, hz), M.LOG)
    add_outline(fills, "wenyuan hut rail", HUT_PLAT_X1, HUT_PLAT_Z1, HUT_PLAT_X2, HUT_PLAT_Z2, 6, 6, M.FENCE, thickness=1)
    # Gable roof (悬山顶), ridge running east-west.
    add_ridge_roof(fills, "wenyuan hut roof", HUT_PLAT_X1 - 2, HUT_PLAT_Z1 - 2, HUT_PLAT_X2 + 2, HUT_PLAT_Z2 + 2, 12, layers=2, ridge_axis="x", roof_block=M.ROOF_DARK)
    # Qin table (琴台): log legs, plank board, golden zither.
    add_fill(fills, "wenyuan qin table legs", (2126, 6, 1284), (2127, 6, 1285), M.LOG)
    add_fill(fills, "wenyuan qin table board", (2125, 7, 1283), (2128, 7, 1286), M.WOOD)
    add_fill(fills, "wenyuan qin zither", (2126, 8, 1284), (2127, 8, 1285), M.GOLD)
    # Poetry lectern and a reading mat.
    add_fill(fills, "wenyuan hut lectern", (2136, 6, 1276), (2136, 6, 1276), LECTERN)
    add_fill(fills, "wenyuan hut mat", (2132, 6, 1274), (2134, 6, 1276), CARPET)

    # ------------------------------------------------------------------
    # 8. Bamboo grove (竹里馆竹林): tall thin leaf columns, high and low.
    # ------------------------------------------------------------------
    for gx, gz, gh in BAMBOO_GROVE:
        _bamboo(fills, gx, gz, gh)
    # Mossy ground carpet inside the densest part of the grove.
    add_fill(fills, "wenyuan grove moss w", (2066, 3, 1244), (2090, 3, 1286), M.MOSS_STONE)
    add_fill(fills, "wenyuan grove moss n", (2078, 3, 1216), (2094, 3, 1240), M.MOSS_STONE)

    # ------------------------------------------------------------------
    # 9. Deer Enclosure (鹿柴): low timber fence, criss-cross rustic gate,
    #    two recumbent sika-deer sculptures, mossy rocks.
    # ------------------------------------------------------------------
    add_outline(fills, "wenyuan deer fence", DEER_X1, DEER_Z1, DEER_X2, DEER_Z2, 4, 5, M.FENCE, thickness=1)
    # Gate opening in the south run, framed by log posts and a lintel.
    add_fill(fills, "wenyuan deer gate opening", (2344, 4, DEER_Z2), (2351, 5, DEER_Z2), M.AIR)
    add_fill(fills, "wenyuan deer gate post w", (2344, 4, DEER_Z2), (2344, 6, DEER_Z2), M.LOG)
    add_fill(fills, "wenyuan deer gate post e", (2351, 4, DEER_Z2), (2351, 6, DEER_Z2), M.LOG)
    add_fill(fills, "wenyuan deer gate lintel", (2344, 6, DEER_Z2), (2351, 6, DEER_Z2), M.WOOD)
    # Criss-cross wattle leaves (交错柴扉) as two zigzag diagonals.
    add_fill(fills, "wenyuan deer gate weave a1", (2344, 4, DEER_Z2), (2345, 4, DEER_Z2), M.FENCE)
    add_fill(fills, "wenyuan deer gate weave a2", (2346, 5, DEER_Z2), (2347, 5, DEER_Z2), M.FENCE)
    add_fill(fills, "wenyuan deer gate weave a3", (2348, 4, DEER_Z2), (2349, 4, DEER_Z2), M.FENCE)
    add_fill(fills, "wenyuan deer gate weave a4", (2350, 5, DEER_Z2), (2351, 5, DEER_Z2), M.FENCE)
    add_fill(fills, "wenyuan deer gate weave b1", (2344, 5, DEER_Z2), (2345, 5, DEER_Z2), M.FENCE)
    add_fill(fills, "wenyuan deer gate weave b2", (2346, 4, DEER_Z2), (2347, 4, DEER_Z2), M.FENCE)
    add_fill(fills, "wenyuan deer gate weave b3", (2348, 5, DEER_Z2), (2349, 5, DEER_Z2), M.FENCE)
    add_fill(fills, "wenyuan deer gate weave b4", (2350, 4, DEER_Z2), (2351, 4, DEER_Z2), M.FENCE)
    # Two recumbent sika deer.
    _deer(fills, "west", 2324, 1246, "west")
    _deer(fills, "east", 2364, 1260, "east")
    # Mossy accent rocks (苔石点石).
    add_fill(fills, "wenyuan deer moss 1", (2316, 4, 1224), (2317, 4, 1225), M.MOSS_STONE)
    add_fill(fills, "wenyuan deer moss 2", (2320, 4, 1270), (2321, 4, 1270), M.MOSS_STONE)
    add_fill(fills, "wenyuan deer moss 3", (2378, 4, 1226), (2379, 4, 1227), M.COBBLE)
    add_fill(fills, "wenyuan deer moss 4", (2384, 4, 1264), (2384, 5, 1264), M.MOSS_STONE)
    add_fill(fills, "wenyuan deer moss 5", (2330, 4, 1216), (2330, 4, 1216), M.COBBLE)

    # ------------------------------------------------------------------
    # 10. Magnolia Hollow (辛夷坞): blossom stream ringing the dell,
    #     five cherry trees, pink petals adrift, two fords.
    # ------------------------------------------------------------------
    for tag, (x1, z1, x2, z2) in {
        "n": (STREAM_X1, STREAM_Z1, STREAM_X2, STREAM_Z1),
        "s": (STREAM_X1, STREAM_Z2, STREAM_X2, STREAM_Z2),
        "w": (STREAM_X1, STREAM_Z1 + 1, STREAM_X1, STREAM_Z2 - 1),
        "e": (STREAM_X2, STREAM_Z1 + 1, STREAM_X2, STREAM_Z2 - 1),
    }.items():
        add_fill(fills, f"wenyuan stream {tag} bed", (x1, 2, z1), (x2, 2, z2), M.SMOOTH)
        add_fill(fills, f"wenyuan stream {tag} water", (x1, 3, z1), (x2, 3, z2), M.WATER)
    # Stepping-stone fords across the stream.
    add_fill(fills, "wenyuan stream ford n", (2354, 3, STREAM_Z1), (2356, 3, STREAM_Z1), M.SMOOTH)
    add_fill(fills, "wenyuan stream ford s", (2350, 3, STREAM_Z2), (2352, 3, STREAM_Z2), M.SMOOTH)
    # Five cherry trees in a ring around the dell.
    for tx, tz in [(2355, 1479), (2340, 1490), (2346, 1508), (2364, 1508), (2370, 1490)]:
        _cherry_tree(fills, tx, tz)
    # Mossy boulder at the dell's heart.
    add_fill(fills, "wenyuan dell boulder", (2354, 4, 1494), (2355, 5, 1495), M.MOSS_STONE)
    add_fill(fills, "wenyuan dell boulder cap", (2356, 4, 1495), (2356, 4, 1495), M.ANDESITE)
    # Pink petals adrift on the blossom stream.
    for i, (px, pz) in enumerate([
        (2340, STREAM_Z1), (2370, STREAM_Z1), (STREAM_X1, 1480), (STREAM_X2, 1495),
        (2340, STREAM_Z2), (2368, STREAM_Z2), (STREAM_X1, 1510), (STREAM_X2, 1470),
    ]):
        add_fill(fills, f"wenyuan stream petal {i}", (px, 3, pz), (px, 3, pz), M.PINK_WOOL)

    # ------------------------------------------------------------------
    # 11. Moon-Inviting Terrace (邀月台): two-tier stone platform with a
    #     low parapet, moon-pool inlay, stone table and bench.
    # ------------------------------------------------------------------
    add_fill(fills, "wenyuan terrace tier1", (TERR_X1, 4, TERR_Z1), (TERR_X2, 5, TERR_Z2), M.STONE)
    add_fill(fills, "wenyuan terrace tier2", (TERR_X1 + 6, 6, TERR_Z1 + 6), (TERR_X2 - 6, 7, TERR_Z2 - 6), M.STONE)
    add_outline(fills, "wenyuan terrace parapet", TERR_X1 + 6, TERR_Z1 + 6, TERR_X2 - 6, TERR_Z2 - 6, 8, 8, M.QUARTZ, thickness=1)
    add_fill(fills, "wenyuan terrace parapet gate", (2158, 8, TERR_Z1 + 6), (2168, 8, TERR_Z1 + 6), M.AIR)
    add_fill(fills, "wenyuan terrace steps", (2159, 6, TERR_Z1 + 1), (2167, 6, TERR_Z1 + 5), M.SMOOTH)
    add_fill(fills, "wenyuan terrace moon pool", (2152, 7, 1384), (2154, 7, 1386), M.SEA_LANTERN)
    add_fill(fills, "wenyuan terrace table", (2160, 8, 1392), (2161, 8, 1393), M.SMOOTH)
    add_fill(fills, "wenyuan terrace bench", (2160, 8, 1396), (2162, 8, 1396), M.SMOOTH)

    # ------------------------------------------------------------------
    # 12. Rockery groups (叠石小品) between the scenes.
    # ------------------------------------------------------------------
    _rockery(fills, "nw", 2205, 1310)  # lodge -> lake north
    _rockery(fills, "ne", 2270, 1320)  # deer walk -> lake north-east
    _rockery(fills, "sw", 2160, 1455)  # terrace -> south lawn
    _rockery(fills, "se", 2340, 1440)  # lake -> magnolia hollow

    # ------------------------------------------------------------------
    # 13. Scattered garden lanterns (no lamp rows, keeping it wild).
    # ------------------------------------------------------------------
    for lx, lz in LANTERN_SPOTS:
        _garden_lamp(fills, lx, lz)

    # ------------------------------------------------------------------
    # 14. Bamboo clumps as soft scene separators.
    # ------------------------------------------------------------------
    _bamboo(fills, 2225, 1338, 6)
    _bamboo(fills, 2226, 1338, 9)
    _bamboo(fills, 2295, 1338, 7)
    _bamboo(fills, 2296, 1338, 10)
    _bamboo(fills, 2317, 1458, 6)
    _bamboo(fills, 2318, 1458, 8)


def main() -> None:
    fills: list[Fill] = []
    build_wenyuan_3d(fills)
    for f in fills:
        xs = sorted((f.x1, f.x2))
        zs = sorted((f.z1, f.z2))
        if xs[0] < BASE_X + SITE_X1 or xs[1] > BASE_X + SITE_X2:
            raise SystemExit(f"fill out of x bounds: {f}")
        if zs[0] < BASE_Z + SITE_Z1 or zs[1] > BASE_Z + SITE_Z2:
            raise SystemExit(f"fill out of z bounds: {f}")
    run_builder(build_wenyuan_3d, "wenyuan_3d")


if __name__ == "__main__":
    main()
