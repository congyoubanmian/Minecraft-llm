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
    add_outline,
    add_pagoda_eave,
    add_platform_with_steps,
    add_pyramid_roof,
    add_ridge_roof,
    add_spiral_stair,
    add_tree,
    run_builder,
)


"""
Douting Post & Sifang Hostel (都亭驿·四方馆) 3D module - the central state
post station of Tang Chang'an, hub of the national courier relay (驿传) and
guesthouse for envoys of the "four quarters" (四方使节).

Location in Chang'an city local coordinates:
    Plot: x 3450..3750, z 1500..1800 (strict bounds - nothing may leave
    them). Neighbours are pre-tiled ward housing on every side (this pass
    deliberately overwrites it); the Zhuque Avenue watchtowers stand around
    x 2900..3100, so nothing may reach west of x 3350. Ground is graded to
    stone y0..1 + grass y2..3 (walking surface y4); the main structures
    rise from y5. Orientation: the walled compound is entered through the
    gate tower in the entrance (south) wall at the z-min edge, carrying the
    gold "都亭驿" plaque; the Document Hall closes the far end of the axis
    at x 3520..3680, z 1700..1780 with its front turned to the court.

Distinctive features:
    - Rammed-earth compound wall (white terracotta + deepslate coping) with
      inner buttresses and a bastion gate tower: arched passage, timber
      gate leaves, dark gable roof with gold ridge finials and a gold name
      plaque
    - Lamp-lined approach outside the gate with hitching posts and twin
      two-tier mounting blocks (上马石)
    - Document Hall (驿务大堂): two-tier terraced platform, red walls with
      a log colonnade, double-eave silhouette - hand-stepped lower hip
      skirt plus a gilded hip roof (庑殿顶) over a red upper storey
    - Courier route map wall (驿程舆图墙): white-wool map board with yellow
      frame, red relay routes and gold station nodes; document desks,
      chest counters, barrels and lecterns inside
    - Two rows of four independent guest rooms (四方客房): bed platforms
      with red blankets, chests, lattice windows, and a colour-coded
      number lantern at every door; the "Persian envoy room" adds a
      glazed-terracotta medallion, wool carpet and a gold basin
    - Eight-stall stable row (马厩八间): fence partitions, per-stall fence
      mangers, a long stone water trough, hay piles, wall hay racks and a
      hitching-post line in front
    - Post carriage (驿站马车): plank body, red-wool barrel-vault canopy,
      four 2x2 timber wheels and twin long log shafts
    - Three-stage pigeon tower (信鸽楼) in the far corner: iron-bar cote
      bands, cornices, interior spiral stair and a quartz lamp room
    - Well with stone curb, windlass and rope under a pyramid-roofed
      pavilion; fodder yard with two hay ricks against the back wall
"""

# ---------------------------------------------------------------------------
# Site: east-city central post station plot (strict bounds).
# ---------------------------------------------------------------------------
SITE_X1, SITE_X2 = 3450, 3750
SITE_Z1, SITE_Z2 = 1500, 1800

# Rammed-earth compound wall (outer face) and coping level.
WALL_X1, WALL_Z1 = 3465, 1515
WALL_X2, WALL_Z2 = 3735, 1785
WALL_TOP_Y = 10

# Gate tower bastion, arched passage and upper gate hall (entrance gate).
GB_X1, GB_Z1, GB_X2, GB_Z2 = 3572, 1511, 3628, 1524
ARCH_X1, ARCH_X2 = 3590, 3610
GH_X1, GH_Z1, GH_X2, GH_Z2 = 3578, 1509, 3622, 1526

# Document Hall (驿务大堂) and its upper storey.
TER_X1, TER_Z1, TER_X2, TER_Z2 = 3512, 1692, 3688, 1783
HALL_X1, HALL_Z1, HALL_X2, HALL_Z2 = 3520, 1700, 3680, 1780
DECK_Y = 14
US_X1, US_Z1, US_X2, US_Z2 = 3586, 1733, 3614, 1747

# Guest-room ranges: two rows of four units along the courtyard sides.
WEST_X1, WEST_X2 = 3473, 3488
EAST_X1, EAST_X2 = 3712, 3727
ROOM_Z = (1540, 1566, 1592, 1618)

# Stable row (south/front courtyard, west of the gate axis).
STB_X1, STB_Z1, STB_X2, STB_Z2 = 3496, 1536, 3580, 1560

# Pigeon tower footprint and centre.
PG_X1, PG_Z1, PG_X2, PG_Z2 = 3703, 1751, 3719, 1767
PG_CX, PG_CZ = 3711, 1759

# Direct-string blocks used by this module.
HAY = "minecraft:hay_block"
CHEST_E = "minecraft:chest[facing=east]"
CHEST_S = "minecraft:chest[facing=south]"
CHEST_W = "minecraft:chest[facing=west]"
LECTERN_N = "minecraft:lectern[facing=north]"
LECTERN_W = "minecraft:lectern[facing=west]"
LOG_X = "minecraft:dark_oak_log[axis=x]"

_NUM_WOOL = (M.RED_WOOL, M.YELLOW_WOOL, M.BLUE_WOOL, M.GREEN_WOOL)

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


def _guest_room(
    fills: list[Fill],
    label: str,
    x1: int,
    x2: int,
    uz: int,
    door_on_west: bool,
    num_wool: str,
) -> None:
    """One independent guest cell: shell, bed, chest, window, door lantern.

    door_on_west: the door side faces the courtyard (west row opens east,
    east row opens west). The number lantern is colour-coded per room.
    """
    add_hollow_box(fills, f"{label} shell", x1, 4, uz, x2, 8, uz + 18, M.WHITE_TERRACOTTA, thickness=1)
    add_fill(fills, f"{label} floor", (x1 + 1, 4, uz + 1), (x2 - 1, 4, uz + 17), M.WOOD)
    fx = x1 if door_on_west else x2
    add_fill(fills, f"{label} door", (fx, 4, uz + 8), (fx, 7, uz + 10), M.AIR)
    add_fill(fills, f"{label} window", (fx, 6, uz + 13), (fx, 7, uz + 16), M.GLASS)
    add_fill(fills, f"{label} room number", (fx, 8, uz + 9), (fx, 8, uz + 9), num_wool)
    px = x1 - 2 if door_on_west else x2 + 2
    add_fill(fills, f"{label} lamp post", (px, 4, uz + 9), (px, 6, uz + 9), M.FENCE)
    add_fill(fills, f"{label} lantern", (px, 7, uz + 9), (px, 7, uz + 9), M.LANTERN)
    # Bed platform against the back wall, mirror-symmetric per row.
    if door_on_west:
        bx1, bx2 = x2 - 3, x2 - 1
        add_fill(fills, f"{label} bed", (bx1, 5, uz + 2), (bx2, 5, uz + 7), M.WOOD)
        add_fill(fills, f"{label} blanket", (bx2 - 1, 6, uz + 3), (bx2, 6, uz + 6), M.RED_WOOL)
        add_fill(fills, f"{label} pillow", (bx2, 6, uz + 2), (bx2, 6, uz + 2), M.WHITE_WOOL)
        add_fill(fills, f"{label} chest", (bx1, 5, uz + 15), (bx2, 6, uz + 15), CHEST_W)
    else:
        bx1, bx2 = x1 + 1, x1 + 3
        add_fill(fills, f"{label} bed", (bx1, 5, uz + 2), (bx2, 5, uz + 7), M.WOOD)
        add_fill(fills, f"{label} blanket", (bx1, 6, uz + 3), (bx1 + 1, 6, uz + 6), M.RED_WOOL)
        add_fill(fills, f"{label} pillow", (bx1, 6, uz + 2), (bx1, 6, uz + 2), M.WHITE_WOOL)
        add_fill(fills, f"{label} chest", (bx1, 5, uz + 15), (bx2, 6, uz + 15), CHEST_E)
    # Gable roof: two stair slopes plus a dark ridge row.
    add_fill(fills, f"{label} roof w", (x1 - 2, 9, uz - 1), (x1 + 4, 9, uz + 19), _stair(M.ROOF_DARK, "east"))
    add_fill(fills, f"{label} roof e", (x2 - 4, 9, uz - 1), (x2 + 2, 9, uz + 19), _stair(M.ROOF_DARK, "west"))
    add_fill(fills, f"{label} ridge", (x1 + 5, 10, uz), (x2 - 5, 10, uz + 18), M.ROOF_DARK)


# ---------------------------------------------------------------------------
# Main builder.
# ---------------------------------------------------------------------------
def build_douting_post_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site grading: stone + grass terrace, then the gate axis path and
    #    an east-west service path across the courtyard.
    # ------------------------------------------------------------------
    add_fill(fills, "douting clear site", (SITE_X1, 4, SITE_Z1), (SITE_X2, 7, SITE_Z2), M.AIR)
    add_fill(fills, "douting terrace stone", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "douting terrace grass", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)
    add_fill(fills, "douting axis path", (3588, 3, 1524), (3612, 3, 1691), M.ANDESITE)
    add_fill(fills, "douting cross path", (3500, 3, 1656), (3700, 3, 1658), M.ANDESITE)

    # ------------------------------------------------------------------
    # 2. Rammed-earth compound wall: white body, dark coping, buttresses.
    # ------------------------------------------------------------------
    add_outline(fills, "douting wall body", WALL_X1, WALL_Z1, WALL_X2, WALL_Z2, 4, 9, M.WHITE_TERRACOTTA, thickness=2)
    add_outline(fills, "douting wall coping", WALL_X1, WALL_Z1, WALL_X2, WALL_Z2, WALL_TOP_Y, WALL_TOP_Y, M.DARK, thickness=2)
    for bx in (3520, 3680):
        add_fill(fills, f"douting buttress n {bx}", (bx, 4, 1517), (bx + 1, 9, 1518), M.WHITE_TERRACOTTA)
    for bx in (3490, 3710):
        add_fill(fills, f"douting buttress s {bx}", (bx, 4, 1782), (bx + 1, 9, 1783), M.WHITE_TERRACOTTA)
    for bz in (1600, 1700):
        add_fill(fills, f"douting buttress w {bz}", (3467, 4, bz), (3468, 9, bz + 1), M.WHITE_TERRACOTTA)
        add_fill(fills, f"douting buttress e {bz}", (3732, 4, bz), (3733, 9, bz + 1), M.WHITE_TERRACOTTA)

    # ------------------------------------------------------------------
    # 3. South gate tower: bastion, arched passage, gate leaves, gold
    #    name plaque, barred upper hall and a dark gable roof.
    # ------------------------------------------------------------------
    add_fill(fills, "douting gate bastion", (GB_X1, 4, GB_Z1), (GB_X2, 13, GB_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "douting gate arch", (ARCH_X1, 4, GB_Z1), (ARCH_X2, 11, GB_Z2), M.AIR)
    add_fill(fills, "douting gate lintel", (ARCH_X1 - 1, 11, GB_Z1), (ARCH_X2 + 1, 11, GB_Z2), LOG_X)
    add_fill(fills, "douting gate leaf w", (3590, 4, 1512), (3595, 9, 1513), M.WOOD)
    add_fill(fills, "douting gate leaf e", (3605, 4, 1522), (3610, 9, 1523), M.WOOD)
    add_fill(fills, "douting gate plaque frame", (3588, 12, 1510), (3612, 15, 1510), M.DARK)
    add_fill(fills, "douting gate plaque gold", (3592, 13, 1510), (3608, 14, 1510), M.GOLD)
    add_hollow_box(fills, "douting gate hall", GH_X1, 14, GH_Z1, GH_X2, 19, GH_Z2, M.RED_WALL, thickness=1)
    add_fill(fills, "douting gate bars n", (3582, 16, GH_Z1), (3618, 17, GH_Z1), M.IRON_BARS)
    add_fill(fills, "douting gate bars s", (3582, 16, GH_Z2), (3618, 17, GH_Z2), M.IRON_BARS)
    add_fill(fills, "douting gate bars w", (GH_X1, 16, 1513), (GH_X1, 17, 1522), M.IRON_BARS)
    add_fill(fills, "douting gate bars e", (GH_X2, 16, 1513), (GH_X2, 17, 1522), M.IRON_BARS)
    add_ridge_roof(fills, "douting gate roof", 3576, 1507, 3624, 1528, 20, layers=2, ridge_axis="x", roof_block=M.ROOF_DARK, ridge_block=M.GOLD)
    # Seal the two ridge-end notches the primitive leaves at the eave line.
    add_fill(fills, "douting gate ridge cap w", (3576, 24, 1517), (3579, 24, 1517), M.GOLD)
    add_fill(fills, "douting gate ridge cap e", (3621, 24, 1517), (3624, 24, 1517), M.GOLD)

    # ------------------------------------------------------------------
    # 4. Approach outside the gate: paving, lamps, hitching posts and
    #    mounting blocks (上马石).
    # ------------------------------------------------------------------
    add_fill(fills, "douting approach pave", (3570, 3, 1500), (3630, 3, 1510), M.ANDESITE)
    for lx in (3572, 3628):
        for lz in (1503, 1508):
            add_fill(fills, f"douting approach lamp {lx},{lz}", (lx, 4, lz), (lx, 6, lz), M.FENCE)
            add_fill(fills, f"douting approach lamp light {lx},{lz}", (lx, 7, lz), (lx, 7, lz), M.LANTERN)
    for hx in (3550, 3558, 3642, 3650):
        add_fill(fills, f"douting hitch post {hx}", (hx, 4, 1505), (hx, 7, 1505), M.FENCE)
    add_fill(fills, "douting mounting block w", (3556, 4, 1502), (3559, 4, 1505), M.ANDESITE)
    add_fill(fills, "douting mounting block w top", (3557, 5, 1503), (3558, 5, 1504), M.STONE)
    add_fill(fills, "douting mounting block e", (3641, 4, 1502), (3644, 4, 1505), M.ANDESITE)
    add_fill(fills, "douting mounting block e top", (3642, 5, 1503), (3643, 5, 1504), M.STONE)

    # ------------------------------------------------------------------
    # 5. Document Hall (驿务大堂): terraced platform, red walls, deck,
    #    lower hip skirt, colonnade, doors/windows, upper storey and the
    #    gilded hip roof (庑殿顶).
    # ------------------------------------------------------------------
    add_platform_with_steps(fills, "douting hall terrace", TER_X1, TER_Z1, TER_X2, TER_Z2, 4, [(1, 0, M.STONE), (1, 2, M.SMOOTH)])
    add_outline(fills, "douting hall walls", HALL_X1, HALL_Z1, HALL_X2, HALL_Z2, 6, DECK_Y, M.RED_WALL, thickness=2)
    add_fill(fills, "douting hall floor", (HALL_X1 + 2, 5, HALL_Z1 + 2), (HALL_X2 - 2, 5, HALL_Z2 - 2), M.WOOD)
    add_fill(fills, "douting hall deck", (3516, DECK_Y, 1696), (3684, DECK_Y, 1782), M.WOOD)
    for i in range(4):
        sy = DECK_Y + 1 + i
        add_fill(fills, f"douting hall skirt n {i}", (3516 + i, sy, 1697 + i), (3684 - i, sy, 1697 + i), _stair(M.ROOF_GREEN, "south"))
        add_fill(fills, f"douting hall skirt s {i}", (3516 + i, sy, 1782 - i), (3684 - i, sy, 1782 - i), _stair(M.ROOF_GREEN, "north"))
        add_fill(fills, f"douting hall skirt w {i}", (3516 + i, sy, 1698 + i), (3516 + i, sy, 1781 - i), _stair(M.ROOF_GREEN, "east"))
        add_fill(fills, f"douting hall skirt e {i}", (3684 - i, sy, 1698 + i), (3684 - i, sy, 1781 - i), _stair(M.ROOF_GREEN, "west"))
    add_column_grid(fills, "douting hall columns", 3522, 1702, 3678, 1778, 6, 13, 40, M.LOG, column_size=1)
    # Three doorways and lattice windows on the courtyard (north) face.
    add_fill(fills, "douting hall door main", (3592, 6, HALL_Z1), (3608, 11, HALL_Z1 + 1), M.AIR)
    add_fill(fills, "douting hall door w", (3544, 6, HALL_Z1), (3554, 10, HALL_Z1 + 1), M.AIR)
    add_fill(fills, "douting hall door e", (3646, 6, HALL_Z1), (3656, 10, HALL_Z1 + 1), M.AIR)
    add_fill(fills, "douting hall window n w", (3566, 9, HALL_Z1), (3578, 12, HALL_Z1 + 1), M.GLASS)
    add_fill(fills, "douting hall window n e", (3622, 9, HALL_Z1), (3634, 12, HALL_Z1 + 1), M.GLASS)
    add_fill(fills, "douting hall window s w", (3560, 9, HALL_Z2 - 1), (3572, 12, HALL_Z2), M.GLASS)
    add_fill(fills, "douting hall window s e", (3628, 9, HALL_Z2 - 1), (3640, 12, HALL_Z2), M.GLASS)
    # Red upper storey carrying the hip roof.
    add_hollow_box(fills, "douting hall upper storey", US_X1, 15, US_Z1, US_X2, 20, US_Z2, M.RED_WALL, thickness=1)
    add_fill(fills, "douting hall upper win n", (3594, 16, US_Z1), (3606, 18, US_Z1), M.GLASS)
    add_fill(fills, "douting hall upper win s", (3594, 16, US_Z2), (3606, 18, US_Z2), M.GLASS)
    add_fill(fills, "douting hall upper win w", (US_X1, 16, 1738), (US_X1, 18, 1742), M.GLASS)
    add_fill(fills, "douting hall upper win e", (US_X2, 16, 1738), (US_X2, 18, 1742), M.GLASS)
    add_hip_roof(fills, "douting hall upper roof", 3582, 1731, 3618, 1749, 21, layers=9, ridge_axis="x", roof_block=M.ROOF_GREEN, ridge_block=M.GOLD)

    # ------------------------------------------------------------------
    # 6. Hall interior: courier route map wall (驿程舆图墙) and document
    #    furniture - desk, chest counters, barrels, lecterns.
    # ------------------------------------------------------------------
    add_fill(fills, "douting map board", (3550, 7, 1778), (3650, 15, 1778), M.WHITE_WOOL)
    add_fill(fills, "douting map frame top", (3550, 15, 1778), (3650, 15, 1778), M.YELLOW_WOOL)
    add_fill(fills, "douting map frame bottom", (3550, 7, 1778), (3650, 7, 1778), M.YELLOW_WOOL)
    add_fill(fills, "douting map frame w", (3550, 8, 1778), (3550, 14, 1778), M.YELLOW_WOOL)
    add_fill(fills, "douting map frame e", (3650, 8, 1778), (3650, 14, 1778), M.YELLOW_WOOL)
    add_fill(fills, "douting map route trunk", (3553, 11, 1778), (3647, 11, 1778), M.RED_WOOL)
    add_fill(fills, "douting map route v1", (3577, 8, 1778), (3577, 14, 1778), M.RED_WOOL)
    add_fill(fills, "douting map route v2", (3623, 8, 1778), (3623, 14, 1778), M.RED_WOOL)
    add_fill(fills, "douting map route spur nw", (3556, 13, 1778), (3576, 13, 1778), M.RED_WOOL)
    add_fill(fills, "douting map route spur se", (3624, 9, 1778), (3644, 9, 1778), M.RED_WOOL)
    add_fill(fills, "douting map node w", (3552, 10, 1778), (3554, 12, 1778), M.GOLD)
    add_fill(fills, "douting map node e", (3646, 10, 1778), (3648, 12, 1778), M.GOLD)
    add_fill(fills, "douting map node v1", (3576, 10, 1778), (3578, 12, 1778), M.GOLD)
    add_fill(fills, "douting map node v2", (3622, 10, 1778), (3624, 12, 1778), M.GOLD)
    add_fill(fills, "douting desk base", (3586, 6, 1706), (3614, 6, 1712), M.LOG)
    add_fill(fills, "douting desk top", (3586, 7, 1706), (3614, 7, 1712), M.WOOD)
    add_fill(fills, "douting desk scrolls", (3592, 8, 1708), (3596, 8, 1710), M.QUARTZ)
    add_fill(fills, "douting desk seal", (3604, 8, 1709), (3604, 8, 1709), M.GOLD)
    add_fill(fills, "douting chests n", (3526, 6, 1703), (3560, 7, 1704), CHEST_S)
    add_fill(fills, "douting barrels n", (3564, 6, 1703), (3584, 7, 1704), "minecraft:barrel")
    add_fill(fills, "douting chests w", (3523, 6, 1710), (3523, 7, 1744), CHEST_E)
    add_fill(fills, "douting lectern a", (3600, 6, 1718), (3600, 6, 1718), LECTERN_N)
    add_fill(fills, "douting lectern b", (3620, 6, 1724), (3620, 6, 1724), LECTERN_W)

    # ------------------------------------------------------------------
    # 7. Guest ranges (四方客房): two rows of four cells, colour-coded
    #    door lanterns; unit e0 is the Persian envoy room (波斯使节房).
    # ------------------------------------------------------------------
    for i, uz in enumerate(ROOM_Z):
        _guest_room(fills, f"douting guest w{i}", WEST_X1, WEST_X2, uz, False, _NUM_WOOL[i])
        _guest_room(fills, f"douting guest e{i}", EAST_X1, EAST_X2, uz, True, _NUM_WOOL[i])
    # Persian envoy room dressing: carpet, glazed medallion, gold basin.
    add_fill(fills, "douting persian carpet", (3716, 4, 1544), (3723, 4, 1554), M.RED_WOOL)
    add_fill(fills, "douting persian carpet inner", (3718, 4, 1546), (3721, 4, 1552), M.YELLOW_WOOL)
    add_fill(fills, "douting persian medallion lo", (3719, 5, 1558), (3721, 5, 1558), M.RED_GLAZED)
    add_fill(fills, "douting persian medallion mid", (3718, 6, 1558), (3722, 6, 1558), M.YELLOW_GLAZED)
    add_fill(fills, "douting persian medallion hi", (3719, 7, 1558), (3721, 7, 1558), M.RED_GLAZED)
    add_fill(fills, "douting persian basin", (3713, 5, 1542), (3714, 5, 1543), M.GOLD)

    # ------------------------------------------------------------------
    # 8. Stable row (马厩八间): timber shed, fence partitions, mangers,
    #    long water trough, hay piles, hay racks, hitching line.
    # ------------------------------------------------------------------
    add_fill(fills, "douting stable pave", (STB_X1, 3, STB_Z1), (STB_X2, 3, STB_Z2), M.ANDESITE)
    add_fill(fills, "douting stable back wall", (STB_X1, 4, STB_Z1), (STB_X2, 8, STB_Z1 + 1), M.WOOD)
    add_fill(fills, "douting stable end w", (STB_X1, 4, STB_Z1 + 2), (STB_X1 + 1, 8, STB_Z2), M.WOOD)
    add_fill(fills, "douting stable end e", (STB_X2 - 1, 4, STB_Z1 + 2), (STB_X2, 8, STB_Z2), M.WOOD)
    for sx in (3500, 3515, 3530, 3545, 3560, 3575):
        add_fill(fills, f"douting stable post {sx}", (sx, 4, STB_Z2), (sx, 8, STB_Z2), M.LOG)
    add_fill(fills, "douting stable beam", (STB_X1, 9, STB_Z2), (STB_X2, 9, STB_Z2), LOG_X)
    add_fill(fills, "douting stable roof", (STB_X1 - 2, 10, STB_Z1 - 2), (STB_X2 + 2, 10, STB_Z2 + 2), HAY)
    stalls = (
        (3498, 3506), (3508, 3517), (3519, 3528), (3530, 3539),
        (3541, 3550), (3552, 3561), (3563, 3572), (3574, 3578),
    )
    for dx in (3507, 3518, 3529, 3540, 3551, 3562, 3573):
        add_fill(fills, f"douting stall divider {dx}", (dx, 4, STB_Z1 + 2), (dx, 8, STB_Z2 - 1), M.FENCE)
    for si, (a, b) in enumerate(stalls):
        add_fill(fills, f"douting stall manger {si}", (a + 1, 4, 1539), (b - 1, 5, 1539), M.FENCE)
        add_fill(fills, f"douting stall hay pile {si}", (a + 1, 4, 1552), (a + 2, 5, 1553), HAY)
    for si in (0, 2, 4, 6):
        a, _ = stalls[si]
        add_fill(fills, f"douting stall hay rack {si}", (a + 3, 6, 1538), (a + 6, 7, 1538), HAY)
    add_fill(fills, "douting trough lip n", (3498, 4, 1542), (3578, 4, 1542), M.SMOOTH)
    add_fill(fills, "douting trough lip s", (3498, 4, 1544), (3578, 4, 1544), M.SMOOTH)
    add_fill(fills, "douting trough end w", (3497, 4, 1543), (3497, 4, 1543), M.SMOOTH)
    add_fill(fills, "douting trough end e", (3579, 4, 1543), (3579, 4, 1543), M.SMOOTH)
    add_fill(fills, "douting trough water", (3498, 4, 1543), (3578, 4, 1543), M.WATER)
    for hx in (3502, 3514, 3526, 3538, 3550, 3562, 3574):
        add_fill(fills, f"douting stable hitch {hx}", (hx, 4, 1564), (hx, 7, 1564), M.FENCE)

    # ------------------------------------------------------------------
    # 9. Post carriage (驿站马车): wheels, plank body, red-wool barrel
    #    vault, twin log shafts pointing at the gate axis.
    # ------------------------------------------------------------------
    for wi, (wx, wz) in enumerate(((3628, 1619), (3628, 1632), (3647, 1619), (3647, 1632))):
        add_fill(fills, f"douting cart wheel {wi}", (wx, 4, wz), (wx + 1, 5, wz + 1), M.WOOD)
    add_hollow_box(fills, "douting cart body", 3630, 6, 1619, 3646, 9, 1633, M.WOOD, thickness=1)
    add_fill(fills, "douting cart bench", (3631, 7, 1624), (3632, 7, 1628), M.WOOD)
    add_fill(fills, "douting cart canopy 1", (3629, 10, 1618), (3647, 10, 1634), M.RED_WOOL)
    add_fill(fills, "douting cart canopy 2", (3631, 11, 1620), (3645, 11, 1632), M.RED_WOOL)
    add_fill(fills, "douting cart canopy 3", (3633, 12, 1622), (3643, 12, 1630), M.RED_WOOL)
    add_fill(fills, "douting cart shaft n", (3614, 6, 1623), (3629, 6, 1623), LOG_X)
    add_fill(fills, "douting cart shaft s", (3614, 6, 1629), (3629, 6, 1629), LOG_X)

    # ------------------------------------------------------------------
    # 10. Well and pavilion: stone curb, water, windlass (辘轳) and a
    #     pyramid-roofed pavilion on four red columns.
    # ------------------------------------------------------------------
    for ci, (cx0, cz0) in enumerate(((3551, 1639), (3561, 1639), (3551, 1649), (3561, 1649))):
        add_fill(fills, f"douting well column {ci}", (cx0, 4, cz0), (cx0, 9, cz0), M.RED_WALL)
    add_outline(fills, "douting well curb", 3553, 1641, 3559, 1647, 4, 5, M.STONE, thickness=1)
    add_fill(fills, "douting well water", (3554, 2, 1642), (3558, 4, 1646), M.WATER)
    add_fill(fills, "douting windlass post w", (3551, 4, 1644), (3551, 10, 1644), M.LOG)
    add_fill(fills, "douting windlass post e", (3561, 4, 1644), (3561, 10, 1644), M.LOG)
    add_fill(fills, "douting windlass bar", (3551, 10, 1644), (3561, 10, 1644), LOG_X)
    add_fill(fills, "douting windlass crank", (3560, 9, 1644), (3560, 11, 1644), M.FENCE)
    add_fill(fills, "douting well rope", (3556, 6, 1644), (3556, 9, 1644), M.IRON_BARS)
    add_pyramid_roof(fills, "douting well roof", 3556, 1644, radius=5, y=10, roof_block=M.ROOF_GREEN, apex_block=M.GOLD)

    # ------------------------------------------------------------------
    # 11. Pigeon tower (信鸽楼): three stages, iron-bar cote bands,
    #     cornices, spiral stair, quartz lamp room and gold spike.
    # ------------------------------------------------------------------
    add_fill(fills, "douting pigeon plinth", (3700, 4, 1748), (3722, 5, 1770), M.STONE)
    add_hollow_box(fills, "douting pigeon s1", PG_X1, 6, PG_Z1, PG_X2, 10, PG_Z2, M.WHITE_TERRACOTTA, thickness=1)
    add_fill(fills, "douting pigeon door", (PG_X1, 6, 1756), (PG_X1, 9, 1760), M.AIR)
    add_outline(fills, "douting pigeon cornice 1", 3701, 1749, 3721, 1769, 11, 11,
                "minecraft:dark_prismarine_slab[type=bottom,waterlogged=false]", thickness=1)
    add_hollow_box(fills, "douting pigeon s2", 3705, 12, 1753, 3717, 14, 1765, M.RED_WALL, thickness=1)
    add_fill(fills, "douting pigeon win n", (3708, 13, 1753), (3714, 13, 1753), M.GLASS)
    add_fill(fills, "douting pigeon win s", (3708, 13, 1765), (3714, 13, 1765), M.GLASS)
    add_hollow_box(fills, "douting pigeon s3", 3706, 15, 1754, 3716, 17, 1764, M.WHITE_TERRACOTTA, thickness=1)
    add_fill(fills, "douting pigeon cote n", (3706, 16, 1754), (3716, 16, 1754), M.IRON_BARS)
    add_fill(fills, "douting pigeon cote s", (3706, 16, 1764), (3716, 16, 1764), M.IRON_BARS)
    add_fill(fills, "douting pigeon cote w", (3706, 16, 1755), (3706, 16, 1763), M.IRON_BARS)
    add_fill(fills, "douting pigeon cote e", (3716, 16, 1755), (3716, 16, 1763), M.IRON_BARS)
    # Spiral stair last so no hollow-box AIR interior can cut its steps.
    add_spiral_stair(fills, "douting pigeon stair a", PG_CX, PG_CZ, 4, 6, 13, M.SMOOTH)
    add_spiral_stair(fills, "douting pigeon stair b", PG_CX, PG_CZ, 4, 10, 17, M.SMOOTH)
    add_pagoda_eave(fills, "douting pigeon cornice 2", PG_CX, PG_CZ, radius=7, y=18, overhang=2, roof_block=M.ROOF_GREEN)
    add_hollow_box(fills, "douting pigeon lamp room", 3708, 19, 1756, 3714, 20, 1762, M.QUARTZ, thickness=1)
    add_fill(fills, "douting pigeon lamp core", (3709, 19, 1757), (3713, 20, 1761), M.SEA_LANTERN)
    add_fill(fills, "douting pigeon lamp door", (3708, 19, 1759), (3708, 20, 1759), M.AIR)
    add_fill(fills, "douting pigeon spike", (3711, 21, 1759), (3711, 22, 1759), M.GOLD)

    # ------------------------------------------------------------------
    # 12. Fodder yard against the back wall and courtyard trees.
    # ------------------------------------------------------------------
    add_fill(fills, "douting fodder rick 1", (3478, 4, 1764), (3484, 5, 1770), HAY)
    add_fill(fills, "douting fodder rick 1 cap", (3480, 6, 1766), (3482, 6, 1768), HAY)
    add_fill(fills, "douting fodder rick 2", (3494, 4, 1740), (3500, 5, 1746), HAY)
    add_fill(fills, "douting fodder rick 2 cap", (3496, 6, 1742), (3498, 6, 1744), HAY)
    add_outline(fills, "douting fodder pen", 3476, 1762, 3486, 1772, 4, 4, M.FENCE, thickness=1)
    for ti, (tx, tz) in enumerate(((3502, 1672), (3694, 1672))):
        add_tree(fills, f"douting courtyard tree {ti}", tx, tz, 4, height=7, spread=2)


def main() -> None:
    run_builder(build_douting_post_3d, "douting_post_3d")


if __name__ == "__main__":
    main()
