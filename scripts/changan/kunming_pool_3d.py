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
    add_hip_roof,
    add_hollow_box,
    add_lantern_line,
    add_outline,
    add_pagoda_eave,
    add_platform_with_steps,
    add_pool,
    add_pyramid_roof,
    add_spiral_stair,
    add_tree,
    run_builder,
)


"""
Kunming Pool 3D (昆明池·汉唐水军操练湖) - the great Han/Tang naval review
lake in the far western suburbs of Chang'an. Dug in 120 BC by Emperor Wu
of Han to drill his navy (水军操练) and still preserved under the Tang,
it was the largest water body around the capital, ringed by the famous
stone whale (石鲸) rising from the centre and the Weaver Girl and Ox-herd
stone statues (牵牛·织女石像) gazing at each other from opposite banks.

Location in Chang'an city local coordinates:
    West far-suburb plot: x -1650..-1050, z 150..750 (empty land).
    Kunming Pool (昆明池): x -1550..-1150, z 250..650, water surface y=1.
    Stone Whale (石鲸): breaching at (-1350, 380), lake centre-north.
    Yuzhang Terrace (豫章台): north-shore review stand,
    x -1450..-1290, z 260..320, three tiers + two-storey pavilion.
    Weaver Girl statue (织女) + Shipou Shrine (石婆庙): east bank.
    Ox-herd statue (牵牛) + Shiye Shrine (石爷庙): west bank.
    Two tower ships (楼船): (-1300, 500) and (-1450, 560).
    Lake islet with pavilion: (-1420, 470), stone bridge to the north.

Distinctive features:
    - Levelled lake basin (stone base + grass topping) with the pool
      carved out and flooded to y=1, ringed by a smooth stone quay
    - The Stone Whale: a 26-block segmented stone leviathan half in the
      water, with tapered body sections, dorsal fin, upturned fluke,
      brow ridge, black eye sockets and a glowing blowhole spout
    - Weaver Girl (east) and Ox-herd (west) seated quartz statues on
      stone pedestals facing each other across the water, each with a
      small shrine hall under a gilded pyramid roof (石婆庙/石爷庙)
    - Yuzhang Terrace: three-tiered stone grand stand driven into the
      north shore, two-storey red-wall pavilion with cantilevered
      gallery, twin spiral stairs, hip roof (庑殿顶) and a big
      south-facing review deck over the water
    - Two Han-style tower ships: broad log hulls with hollowed holds,
      gilded beast-head bows, two cabin storeys under double eave rings
      (重檐), mast, yard, wool sails and gold pennants
    - Water-drill buoy formations (水操演兵场): fence posts with blue,
      red and yellow wool flags marking fleet positions
    - Lake islet with a columned pavilion under a pyramid roof, joined
      to the north shore by a 139-block stone bridge on piers
"""

# Whole plot (levelled). West far-suburb belt; every fill stays inside.
SITE_X1, SITE_Z1 = -1650, 150
SITE_X2, SITE_Z2 = -1050, 750

WATER_Y = 1

# Kunming Pool and its stone quay rim.
POOL_X1, POOL_Z1 = -1550, 250
POOL_X2, POOL_Z2 = -1150, 650

# Stone Whale (石鲸), head east, tail west, half submerged.
WHALE_X1, WHALE_X2 = -1363, -1338
WHALE_CZ = 380

# Yuzhang Terrace (豫章台) on the north shore.
YT_X1, YT_Z1 = -1450, 260
YT_X2, YT_Z2 = -1290, 320
YT_CX = -1370

# Weaver Girl / Ox-herd statues and their shrines.
WEAVER_X, WEAVER_Z = -1120, 460    # 织女, east bank, facing west
OXHERD_X, OXHERD_Z = -1580, 460    # 牵牛, west bank, facing east
SHIPO_X, SHIPO_Z = -1120, 520      # 石婆庙 (Weaver Girl's shrine)
SHIYE_X, SHIYE_Z = -1580, 520      # 石爷庙 (Ox-herd's shrine)

# Han tower ships (楼船).
SHIP1_CX, SHIP1_CZ = -1300, 500
SHIP2_CX, SHIP2_CZ = -1450, 560

# Lake islet, pavilion and the bridge to the north shore.
ISLE_CX, ISLE_CZ = -1420, 470


def _edge_columns(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y1: int, y2: int,
) -> None:
    """Dark-oak columns on the four corners and edge midpoints of a storey."""
    mx, mz = (x1 + x2) // 2, (z1 + z2) // 2
    posts = [
        (x1, z1), (x2 - 1, z1), (x1, z2 - 1), (x2 - 1, z2 - 1),
        (mx - 1, z1), (mx - 1, z2 - 1),
        (x1, mz - 1), (x2 - 1, mz - 1),
    ]
    for i, (px, pz) in enumerate(posts):
        add_fill(fills, f"{label} col {i}", (px, y1, pz), (px + 1, y2, pz + 1), M.LOG)


def _stone_statue(fills: list[Fill], label: str, sx: int, sz: int, face_dx: int) -> None:
    """Seated Han-style stone figure (石人坐像); face_dx -1 = faces west."""
    add_fill(fills, f"{label} pedestal", (sx - 2, 4, sz - 2), (sx + 2, 5, sz + 2), M.STONE)
    add_fill(fills, f"{label} torso", (sx - 1, 6, sz - 1), (sx + 1, 7, sz + 1), M.QUARTZ)
    add_fill(fills, f"{label} lap", (sx + 2 * face_dx, 6, sz - 1), (sx + 2 * face_dx, 6, sz + 1), M.WHITE_TERRACOTTA)
    add_fill(fills, f"{label} head", (sx - 1, 8, sz - 1), (sx + 1, 9, sz + 1), M.QUARTZ)
    add_fill(fills, f"{label} hair bun", (sx, 10, sz), (sx, 10, sz), M.BLACK_WOOL)
    add_fill(fills, f"{label} offering slab", (sx + 4 * face_dx, 4, sz - 1), (sx + 4 * face_dx, 4, sz + 1), M.SMOOTH)


def _shrine(fills: list[Fill], label: str, tx: int, tz: int) -> None:
    """Small bank shrine (石婆庙/石爷庙): red hall on a stone pad under a
    gilded pyramid roof (攒尖顶), door opening towards the statue."""
    add_fill(fills, f"{label} platform", (tx - 6, 4, tz - 6), (tx + 6, 4, tz + 6), M.SMOOTH)
    add_fill(fills, f"{label} steps", (tx - 2, 4, tz - 8), (tx + 2, 4, tz - 7), M.SMOOTH)
    add_hollow_box(fills, f"{label} hall", tx - 4, 5, tz - 4, tx + 4, 8, tz + 4, M.RED_WALL, thickness=1)
    add_fill(fills, f"{label} door", (tx - 1, 5, tz - 4), (tx + 1, 7, tz - 4), M.AIR)
    add_pyramid_roof(fills, f"{label} roof", tx, tz, radius=5, y=9, roof_block=M.ROOF_GREEN, apex_block=M.GOLD)
    add_fill(fills, f"{label} censer", (tx + 2, 5, tz - 5), (tx + 2, 6, tz - 5), M.STONE)
    add_fill(fills, f"{label} censer incense", (tx + 2, 7, tz - 5), (tx + 2, 7, tz - 5), M.LANTERN)


def _tower_ship(fills: list[Fill], label: str, cx: int, cz: int, sail_block: str, eave_block: str) -> None:
    """Han-style tower ship (楼船): broad hull with hollowed hold, gilded
    beast-head bow, two cabin storeys under double eave rings (重檐),
    mast, yard, wool sail and a gold pennant."""
    hx1, hx2 = cx - 16, cx + 16
    hz1, hz2 = cz - 7, cz + 7
    # Hull shell, pointed bow, hollowed hold and plank deck.
    add_fill(fills, f"{label} hull", (hx1, 0, hz1), (cx + 12, 2, hz2), M.LOG)
    add_fill(fills, f"{label} hull bow", (cx + 13, 0, cz - 5), (cx + 15, 2, cz + 5), M.LOG)
    add_fill(fills, f"{label} hull bow tip", (cx + 16, 0, cz - 2), (cx + 16, 1, cz + 2), M.LOG)
    add_fill(fills, f"{label} hold", (cx - 14, 1, cz - 5), (cx + 10, 2, cz + 5), M.AIR)
    add_fill(fills, f"{label} deck", (hx1, 3, hz1), (hx2, 3, hz2), M.WOOD)
    add_outline(fills, f"{label} rail", hx1, hz1, hx2, hz2, 4, 4, M.FENCE, thickness=1)
    # Gilded beast head (船首兽首) with black eyes and horns.
    add_fill(fills, f"{label} beast head", (cx + 13, 4, cz - 2), (cx + 15, 6, cz + 2), M.GOLD)
    add_fill(fills, f"{label} beast snout", (cx + 16, 5, cz - 1), (cx + 16, 6, cz + 1), M.GOLD)
    add_fill(fills, f"{label} beast eye n", (cx + 16, 6, cz - 1), (cx + 16, 6, cz - 1), M.BLACK_WOOL)
    add_fill(fills, f"{label} beast eye s", (cx + 16, 6, cz + 1), (cx + 16, 6, cz + 1), M.BLACK_WOOL)
    add_fill(fills, f"{label} beast horn n", (cx + 14, 7, cz - 2), (cx + 14, 7, cz - 2), M.GOLD)
    add_fill(fills, f"{label} beast horn s", (cx + 14, 7, cz + 2), (cx + 14, 7, cz + 2), M.GOLD)
    # Storey 1 cabin with door and lattice windows.
    add_hollow_box(fills, f"{label} cabin1", cx - 10, 4, cz - 5, cx + 8, 9, cz + 5, M.RED_WALL, thickness=1)
    add_fill(fills, f"{label} cabin1 door", (cx - 1, 5, cz + 5), (cx + 1, 7, cz + 5), M.AIR)
    add_fill(fills, f"{label} cabin1 win s w", (cx - 8, 6, cz + 5), (cx - 4, 7, cz + 5), M.GLASS)
    add_fill(fills, f"{label} cabin1 win s e", (cx + 4, 6, cz + 5), (cx + 8, 7, cz + 5), M.GLASS)
    add_fill(fills, f"{label} cabin1 win n", (cx - 6, 6, cz - 5), (cx + 6, 7, cz - 5), M.GLASS)
    add_fill(fills, f"{label} cabin1 win e", (cx + 8, 6, cz - 3), (cx + 8, 7, cz + 3), M.GLASS)
    # Lower eave ring (重檐下檐) hugging the first cabin roof.
    add_pagoda_eave(fills, f"{label} lower eave", cx - 1, cz, radius=8, y=10, overhang=2, roof_block=eave_block)
    add_fill(fills, f"{label} cabin1 roof", (cx - 7, 10, cz - 4), (cx + 5, 10, cz + 4), M.WOOD)
    # Storey 2 cabin.
    add_hollow_box(fills, f"{label} cabin2", cx - 7, 11, cz - 4, cx + 5, 15, cz + 4, M.RED_WALL, thickness=1)
    add_fill(fills, f"{label} cabin2 door", (cx - 7, 12, cz - 1), (cx - 7, 13, cz + 1), M.AIR)
    add_fill(fills, f"{label} cabin2 win s", (cx - 3, 12, cz + 4), (cx + 1, 13, cz + 4), M.GLASS)
    add_fill(fills, f"{label} cabin2 win n", (cx - 3, 12, cz - 4), (cx + 1, 13, cz - 4), M.GLASS)
    add_fill(fills, f"{label} cabin2 win e", (cx + 5, 12, cz - 2), (cx + 5, 13, cz + 2), M.GLASS)
    # Upper eave ring (重檐上檐) and a stepped cap with gilded finial.
    add_pagoda_eave(fills, f"{label} upper eave", cx - 1, cz, radius=6, y=16, overhang=2, roof_block=eave_block)
    add_fill(fills, f"{label} cap 1", (cx - 5, 17, cz - 3), (cx + 3, 17, cz + 3), M.ROOF_GREEN)
    add_fill(fills, f"{label} cap 2", (cx - 3, 18, cz - 2), (cx + 1, 18, cz + 2), M.ROOF_GREEN)
    add_fill(fills, f"{label} cap 3", (cx - 1, 19, cz - 1), (cx + 1, 19, cz + 1), M.ROOF_GREEN)
    add_fill(fills, f"{label} cap finial", (cx - 1, 20, cz), (cx - 1, 20, cz), M.GOLD)
    # Mast, yard, hanging sail and pennant forward of the cabins.
    add_fill(fills, f"{label} mast", (cx - 13, 4, cz), (cx - 13, 22, cz), M.LOG)
    add_fill(fills, f"{label} yard", (cx - 13, 20, cz - 5), (cx - 13, 20, cz + 5), "minecraft:dark_oak_log[axis=z]")
    add_fill(fills, f"{label} sail", (cx - 13, 9, cz - 4), (cx - 13, 18, cz + 4), sail_block)
    add_fill(fills, f"{label} pennant", (cx - 13, 23, cz), (cx - 13, 23, cz), M.GOLD)


def build_kunming_pool_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 0. Level the whole lake plain first (stone base y0..1, grass y2..3),
    #    mirroring the levelled-plain passes of the other modules.
    # ------------------------------------------------------------------
    add_fill(fills, "kunming plain base", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "kunming plain grass", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)

    # ------------------------------------------------------------------
    # 1. Kunming Pool (昆明池): carve the basin out of the levelled
    #    ground, lay the stone bed, flood to y=1, then pave the stone
    #    quay rim (环湖石岸) around the water edge.
    # ------------------------------------------------------------------
    add_fill(fills, "kunming pool carve", (POOL_X1, 2, POOL_Z1), (POOL_X2, 3, POOL_Z2), M.AIR)
    add_pool(fills, "kunming pool", POOL_X1, POOL_Z1, POOL_X2, POOL_Z2, WATER_Y, depth=2)
    add_fill(fills, "kunming quay n", (POOL_X1 - 3, 2, POOL_Z1 - 3), (POOL_X2 + 3, 3, POOL_Z1 - 1), M.SMOOTH)
    add_fill(fills, "kunming quay s", (POOL_X1 - 3, 2, POOL_Z2 + 1), (POOL_X2 + 3, 3, POOL_Z2 + 3), M.SMOOTH)
    add_fill(fills, "kunming quay w", (POOL_X1 - 3, 2, POOL_Z1), (POOL_X1 - 1, 3, POOL_Z2), M.SMOOTH)
    add_fill(fills, "kunming quay e", (POOL_X2 + 1, 2, POOL_Z1), (POOL_X2 + 3, 3, POOL_Z2), M.SMOOTH)

    # ------------------------------------------------------------------
    # 2. The Stone Whale (石鲸): the pool's famous leviathan breaching
    #    north-centre, built as tapering stone sections rising out of
    #    the water, with fins, eye sockets and a glowing spout.
    # ------------------------------------------------------------------
    wx1, wx2, wcz = WHALE_X1, WHALE_X2, WHALE_CZ
    add_fill(fills, "kunming whale belly", (wx1, -1, wcz - 5), (wx2, 0, wcz + 5), M.MOSS_STONE)
    # Tail: narrow stock, upthrust section and a vertical fluke plate.
    add_fill(fills, "kunming whale tail stock", (wx1, 2, wcz - 2), (wx1 + 4, 3, wcz + 2), M.STONE)
    add_fill(fills, "kunming whale fluke rise", (wx1 - 3, 2, wcz - 2), (wx1, 5, wcz + 2), M.STONE)
    add_fill(fills, "kunming whale fluke plate", (wx1 - 6, 5, wcz - 3), (wx1 - 4, 6, wcz + 3), M.MOSS_STONE)
    add_fill(fills, "kunming whale fluke tip n", (wx1 - 6, 7, wcz - 3), (wx1 - 6, 7, wcz - 2), M.MOSS_STONE)
    add_fill(fills, "kunming whale fluke tip s", (wx1 - 6, 7, wcz + 2), (wx1 - 6, 7, wcz + 3), M.MOSS_STONE)
    # Segmented body: broad mid-section, smooth back, shoulders.
    add_fill(fills, "kunming whale body", (wx1 + 4, 2, wcz - 4), (wx2 - 10, 4, wcz + 4), M.STONE)
    add_fill(fills, "kunming whale back", (wx1 + 6, 5, wcz - 3), (wx2 - 12, 5, wcz + 3), M.STONE)
    add_fill(fills, "kunming whale shoulders", (wx2 - 10, 2, wcz - 3), (wx2 - 2, 5, wcz + 3), M.STONE)
    add_fill(fills, "kunming whale head top", (wx2 - 9, 6, wcz - 2), (wx2 - 4, 6, wcz + 2), M.STONE)
    # Head: brow ridge, tapering snout, dark mouth line, eye sockets.
    add_fill(fills, "kunming whale brow", (wx2 - 3, 4, wcz - 3), (wx2 - 3, 5, wcz + 3), M.STONE)
    add_fill(fills, "kunming whale snout", (wx2 - 2, 2, wcz - 2), (wx2, 4, wcz + 2), M.MOSS_STONE)
    add_fill(fills, "kunming whale mouth", (wx2, 2, wcz - 1), (wx2, 2, wcz + 1), M.BLACK_WOOL)
    add_fill(fills, "kunming whale eye n", (wx2 - 3, 5, wcz - 3), (wx2 - 3, 5, wcz - 3), M.BLACK_WOOL)
    add_fill(fills, "kunming whale eye s", (wx2 - 3, 5, wcz + 3), (wx2 - 3, 5, wcz + 3), M.BLACK_WOOL)
    # Dorsal fin and a sea-lantern blowhole spout.
    add_fill(fills, "kunming whale fin base", (-1353, 6, 379), (-1351, 6, 381), M.STONE)
    add_fill(fills, "kunming whale fin mid", (-1353, 7, 380), (-1352, 7, 380), M.STONE)
    add_fill(fills, "kunming whale fin tip", (-1353, 8, 380), (-1352, 8, 380), M.STONE)
    add_fill(fills, "kunming whale spout", (-1344, 7, 380), (-1344, 7, 380), M.SEA_LANTERN)

    # ------------------------------------------------------------------
    # 3. Yuzhang Terrace (豫章台): the north-shore naval review grand
    #    stand. Three stone tiers driven into the lake, a two-storey
    #    red-wall pavilion with cantilevered gallery, twin spiral
    #    stairs, hip roof (庑殿顶) and a big south-facing deck.
    # ------------------------------------------------------------------
    add_platform_with_steps(
        fills, "kunming yuzhang platform",
        YT_X1, YT_Z1, YT_X2, YT_Z2, 1,
        [(4, 0, M.STONE), (2, 8, M.STONE), (2, 16, M.SMOOTH)],
    )
    # Entrance causeway across the lake's north edge + quay entry step.
    add_fill(fills, "kunming yuzhang causeway", (-1400, 2, 250), (-1340, 4, 259), M.SMOOTH)
    add_fill(fills, "kunming yuzhang entry step", (-1395, 3, 248), (-1345, 4, 249), M.SMOOTH)
    # Storey 1 (y 9..16): red walls, edge columns, doors, windows.
    yt_x1, yt_z1, yt_x2, yt_z2 = -1400, 276, -1340, 288
    add_hollow_box(fills, "kunming yuzhang storey1", yt_x1, 9, yt_z1, yt_x2, 16, yt_z2, M.RED_WALL, thickness=1)
    _edge_columns(fills, "kunming yuzhang storey1", yt_x1, yt_z1, yt_x2, yt_z2, 9, 16)
    add_fill(fills, "kunming yuzhang door s", (-1376, 10, 288), (-1364, 13, 288), M.AIR)
    add_fill(fills, "kunming yuzhang door n", (-1375, 10, 276), (-1365, 13, 276), M.AIR)
    add_fill(fills, "kunming yuzhang win s w", (-1396, 11, 288), (-1384, 14, 288), M.GLASS)
    add_fill(fills, "kunming yuzhang win s e", (-1356, 11, 288), (-1344, 14, 288), M.GLASS)
    add_fill(fills, "kunming yuzhang win n w", (-1396, 11, 276), (-1384, 14, 276), M.GLASS)
    add_fill(fills, "kunming yuzhang win n e", (-1356, 11, 276), (-1344, 14, 276), M.GLASS)
    add_fill(fills, "kunming yuzhang win w", (yt_x1, 11, 280), (yt_x1, 14, 284), M.GLASS)
    add_fill(fills, "kunming yuzhang win e", (yt_x2, 11, 280), (yt_x2, 14, 284), M.GLASS)
    # Cantilevered gallery balcony (悬挑平座) with fence railing.
    add_cantilevered_floor(fills, "kunming yuzhang gallery", yt_x1, yt_z1, yt_x2, yt_z2, y=17, overhang=3, block=M.WOOD)
    add_outline(fills, "kunming yuzhang gallery rail", yt_x1 - 3, yt_z1 - 3, yt_x2 + 3, yt_z2 + 3, 18, 18, M.FENCE, thickness=1)
    # Storey 2 (y 18..24) with windows and a south door.
    add_hollow_box(fills, "kunming yuzhang storey2", -1386, 18, 279, -1354, 24, 287, M.RED_WALL, thickness=1)
    add_fill(fills, "kunming yuzhang s2 door s", (-1372, 19, 287), (-1368, 21, 287), M.AIR)
    add_fill(fills, "kunming yuzhang s2 win s w", (-1384, 20, 287), (-1378, 22, 287), M.GLASS)
    add_fill(fills, "kunming yuzhang s2 win s e", (-1362, 20, 287), (-1356, 22, 287), M.GLASS)
    add_fill(fills, "kunming yuzhang s2 win n", (-1380, 20, 279), (-1360, 22, 279), M.GLASS)
    add_fill(fills, "kunming yuzhang s2 win w", (-1386, 20, 281), (-1386, 22, 285), M.GLASS)
    add_fill(fills, "kunming yuzhang s2 win e", (-1354, 20, 281), (-1354, 22, 285), M.GLASS)
    # Twin spiral stairs linking the storeys.
    add_spiral_stair(fills, "kunming yuzhang stair1", YT_CX, 282, radius=4, y1=9, y2=15, block=M.SMOOTH)
    add_spiral_stair(fills, "kunming yuzhang stair2", YT_CX, 283, radius=3, y1=19, y2=23, block=M.SMOOTH)
    # Hip roof (庑殿顶) over the upper storey.
    add_hip_roof(fills, "kunming yuzhang hip roof", -1386, 279, -1354, 287, y=25, layers=5, ridge_axis="x", roof_block=M.ROOF_GREEN)
    # Grand south deck (南向大露台): rails with a gap at the steps,
    # then descending steps to the lower tiers.
    add_fill(fills, "kunming yuzhang deck rail s w", (-1434, 9, 304), (-1380, 9, 304), M.FENCE)
    add_fill(fills, "kunming yuzhang deck rail s e", (-1360, 9, 304), (-1306, 9, 304), M.FENCE)
    add_fill(fills, "kunming yuzhang deck rail w", (-1434, 9, 290), (-1434, 9, 304), M.FENCE)
    add_fill(fills, "kunming yuzhang deck rail e", (-1306, 9, 290), (-1306, 9, 304), M.FENCE)
    add_fill(fills, "kunming yuzhang deck step 1", (-1378, 7, 305), (-1362, 7, 305), M.SMOOTH)
    add_fill(fills, "kunming yuzhang deck step 2", (-1378, 5, 313), (-1362, 5, 313), M.SMOOTH)

    # ------------------------------------------------------------------
    # 4. Weaver Girl and Ox-herd statues (牵牛·织女石像) on the east and
    #    west banks, gazing at each other across the water, each with
    #    its small shrine (石婆庙 / 石爷庙).
    # ------------------------------------------------------------------
    _stone_statue(fills, "kunming weaver statue", WEAVER_X, WEAVER_Z, face_dx=-1)
    _stone_statue(fills, "kunming oxherd statue", OXHERD_X, OXHERD_Z, face_dx=+1)
    _shrine(fills, "kunming shipou shrine", SHIPO_X, SHIPO_Z)
    _shrine(fills, "kunming shiye shrine", SHIYE_X, SHIYE_Z)

    # ------------------------------------------------------------------
    # 5. Han tower ships (汉式楼船): two multi-storey war boats riding
    #    at anchor in the open lake, ready for the water review.
    # ------------------------------------------------------------------
    _tower_ship(fills, "kunming ship 1", SHIP1_CX, SHIP1_CZ, M.WHITE_WOOL, M.ROOF_GREEN)
    _tower_ship(fills, "kunming ship 2", SHIP2_CX, SHIP2_CZ, M.BLUE_WOOL, M.ROOF_BLUE)

    # ------------------------------------------------------------------
    # 6. Water-drill buoy formations (水操演兵场浮标): fence posts with
    #    wool flags marking the fleet's drill positions on the water.
    # ------------------------------------------------------------------
    for i, bx in enumerate((-1250, -1230, -1210, -1190)):
        add_fill(fills, f"kunming buoy blue line {i}", (bx, 2, 340), (bx, 4, 340), M.FENCE)
        add_fill(fills, f"kunming buoy blue flag {i}", (bx, 5, 340), (bx, 5, 340), M.BLUE_WOOL)
    for i, bx in enumerate((-1250, -1230, -1210, -1190)):
        add_fill(fills, f"kunming buoy red line {i}", (bx, 2, 400), (bx, 4, 400), M.FENCE)
        add_fill(fills, f"kunming buoy red flag {i}", (bx, 5, 400), (bx, 5, 400), M.RED_WOOL)
    for i, (bx, bz) in enumerate(((-1515, 430), (-1495, 410), (-1495, 450), (-1475, 390), (-1475, 470))):
        add_fill(fills, f"kunming buoy wedge {i}", (bx, 2, bz), (bx, 4, bz), M.FENCE)
        add_fill(fills, f"kunming buoy wedge flag {i}", (bx, 5, bz), (bx, 5, bz), M.YELLOW_WOOL)

    # ------------------------------------------------------------------
    # 7. Lake islet (湖心岛) with a small columned pavilion, joined to
    #    the north shore by a low stone bridge on piers.
    # ------------------------------------------------------------------
    icx, icz = ISLE_CX, ISLE_CZ
    add_fill(fills, "kunming isle base", (icx - 12, -1, icz - 12), (icx + 12, 0, icz + 12), M.MOSS_STONE)
    add_fill(fills, "kunming isle mound", (icx - 11, 1, icz - 11), (icx + 11, 2, icz + 11), M.STONE)
    add_fill(fills, "kunming isle grass", (icx - 10, 3, icz - 10), (icx + 10, 3, icz + 10), M.GRASS)
    add_fill(fills, "kunming isle pad", (icx - 4, 4, icz - 4), (icx + 4, 4, icz + 4), M.SMOOTH)
    add_outline(fills, "kunming isle rail", icx - 4, icz - 4, icx + 4, icz + 4, 5, 5, M.FENCE, thickness=1)
    for i, (px, pz) in enumerate(((icx - 3, icz - 3), (icx + 3, icz - 3), (icx - 3, icz + 3), (icx + 3, icz + 3))):
        add_fill(fills, f"kunming isle column {i}", (px, 5, pz), (px, 9, pz), M.RED_WALL)
    add_fill(fills, "kunming isle lamp", (icx, 5, icz), (icx, 5, icz), M.LANTERN)
    add_pyramid_roof(fills, "kunming isle roof", icx, icz, radius=5, y=10, roof_block=M.ROOF_GREEN, apex_block=M.GOLD)
    # Stone bridge from the islet north to the Yuzhang Terrace platform.
    add_fill(fills, "kunming bridge deck", (-1422, 3, 321), (-1418, 3, 459), M.SMOOTH)
    add_fill(fills, "kunming bridge rail w", (-1423, 4, 321), (-1423, 4, 459), M.FENCE)
    add_fill(fills, "kunming bridge rail e", (-1417, 4, 321), (-1417, 4, 459), M.FENCE)
    for pz in (335, 365, 395, 425, 455):
        add_fill(fills, f"kunming bridge pier {pz}", (-1421, -1, pz - 1), (-1419, 2, pz + 1), M.STONE)
    add_fill(fills, "kunming bridge head step", (-1422, 4, 316), (-1418, 4, 320), M.SMOOTH)

    # ------------------------------------------------------------------
    # 8. Shore dressing: lantern lines on all four banks, trees and a
    #    stele naming the pool on the north-west shore.
    # ------------------------------------------------------------------
    add_lantern_line(fills, "kunming shore lantern n", -1540, 240, -1160, 240, y=4, every=80)
    add_lantern_line(fills, "kunming shore lantern s", -1540, 660, -1160, 660, y=4, every=100)
    add_lantern_line(fills, "kunming shore lantern w", -1560, 260, -1560, 640, y=4, every=100)
    add_lantern_line(fills, "kunming shore lantern e", -1140, 260, -1140, 640, y=4, every=100)
    for tx in (-1520, -1420, -1320, -1220):
        add_tree(fills, f"kunming shore tree n {tx}", tx, 228, y=4)
    for tx in (-1500, -1350, -1200):
        add_tree(fills, f"kunming shore tree s {tx}", tx, 668, y=4)
    for tz in (350, 550):
        add_tree(fills, f"kunming shore tree w {tz}", -1570, tz, y=4)
        add_tree(fills, f"kunming shore tree e {tz}", -1130, tz, y=4)
    add_fill(fills, "kunming stele base", (-1472, 4, 232), (-1470, 4, 234), M.STONE)
    add_fill(fills, "kunming stele pillar", (-1471, 5, 233), (-1471, 10, 233), M.WHITE_TERRACOTTA)
    add_fill(fills, "kunming stele cap", (-1471, 11, 233), (-1471, 11, 233), M.GOLD)


def main() -> None:
    run_builder(build_kunming_pool_3d, "kunming_pool_3d")


if __name__ == "__main__":
    main()
