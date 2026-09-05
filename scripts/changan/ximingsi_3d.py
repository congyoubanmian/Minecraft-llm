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
    add_pagoda_eave,
    add_pagoda_openings,
    add_roof_beasts,
    add_spiral_stair,
    add_tree,
    run_builder,
)


"""
Ximing Temple 3D (西明寺·皇家译经大寺) - the great imperial translation
monastery of Tang Chang'an. Founded by imperial decree at the mid-7th
century, Ximing Temple was (after Da Ci'en) the largest scripture
translation academy (翻经院) of the capital: Xuanzang's disciple Yijing
worked here, and the monastery's scriptorium copied the sutras that
travelled the Silk Road recorded in the "Great Tang Record of the Western
Regions" (大唐西域记). State-funded, walled like a palace precinct, and
crowded with scholar-monks, copyists and foreign guests.

Location in Chang'an city local coordinates:
    Plot: x 2420..2780, z 3030..3410 (strict bounds - nothing may leave
    them; nothing may reach past z 3410 where the south ward gate stands
    at z 3419..3421, and the Jinzouyuan liaison offices far north at
    x 2450..2750, z 1750..2050 must stay untouched). Ground is graded to
    stone y0..1 + grass y2..3 (walking surface y4); all main structures
    rise from y5. The pre-tiled ward housing under the plot is
    deliberately overwritten.

Distinctive features:
    - Red perimeter wall (红墙) with a south mountain gate (山门): gate
      tower with dark piers, timber lintel, a gold "西明寺" name plaque
      of three character panels, and an overhanging gable roof (悬山顶)
    - Mahavira Hall (大雄宝殿) on a double stone terrace: double-eave
      composition - a full roof deck ring at y18, an upper red-wall
      storey, then a solid-deck hip roof (庑殿顶) with gold ridge, ridge
      beasts and upturned corners; interior holds the Three World
      Buddhas (三世佛, quartz with gold halos) on a stone altar plus two
      files of nine standing arhats (十八罗汉, quartz 1x2 with
      alternating gold scripture / iron staff)
    - Translation Academy court (翻经院) east: four long desks with
      white-wool scrolls, lecterns, two seated quartz translator statues
      with gold caps, and a scriptorium (写经房) lined with bookshelf
      walls, sutra-case chests and candle-stand lamps
    - Sutra Library (藏经阁) west: two-storey book tower with bookshelf
      rings on both floors, outer gallery railings, spiral stair and a
      gable roof (悬山顶)
    - Twin pavilions on the axis: bell pavilion with a hanging gold bell
      on an iron chain and a stele pavilion with a quartz-pillar stele,
      both four-column pyramidal roofs (攒尖金顶)
    - Five-tier dense-eave pagoda (密檐塔) in the north-west corner,
      alternating red-wall / smooth-stone bodies with pagoda eaves per
      tier and a segmented gold finial (塔刹)
    - Two monk-dormitory courts (僧房院) south and north with main house,
      side wing, courtyard well; stone-slab axis walk with lantern posts
      and two files of cypresses
"""

# ---------------------------------------------------------------------------
# Site (strict ward bounds) and perimeter wall.
# ---------------------------------------------------------------------------
SITE_X1, SITE_X2 = 2420, 2780
SITE_Z1, SITE_Z2 = 3030, 3410

WALL_X1, WALL_Z1, WALL_X2, WALL_Z2 = 2428, 3042, 2772, 3398

# South mountain gate (山门) straddling the wall's south side.
GATE_X1, GATE_Z1, GATE_X2, GATE_Z2 = 2568, 3038, 2632, 3054
GATE_PASS_X1, GATE_PASS_X2 = 2584, 2616

# Axis walk from the gate to the main hall terrace.
PATH_X1, PATH_Z1, PATH_X2, PATH_Z2 = 2588, 3040, 2612, 3196

# Twin axis pavilions.
BELL_CX, BELL_CZ = 2540, 3145
STELE_CX, STELE_CZ = 2660, 3145

# Mahavira Hall (大雄宝殿): terrace tiers, wall box, upper storey, roof.
T1_X1, T1_Z1, T1_X2, T1_Z2 = 2490, 3190, 2710, 3330
T2_X1, T2_Z1, T2_X2, T2_Z2 = 2496, 3196, 2704, 3324
HALL_X1, HALL_Z1, HALL_X2, HALL_Z2 = 2512, 3212, 2688, 3308
UP_X1, UP_Z1, UP_X2, UP_Z2 = 2540, 3238, 2660, 3282
ROOF_X1, ROOF_Z1, ROOF_X2, ROOF_Z2 = 2532, 3230, 2668, 3290

# Sutra Library (藏经阁), west courtyard.
LIB_X1, LIB_Z1, LIB_X2, LIB_Z2 = 2438, 3212, 2486, 3308
LIB_CX, LIB_CZ = 2462, 3260

# Translation Academy court (翻经院), east courtyard.
TRANS_X1, TRANS_Z1, TRANS_X2, TRANS_Z2 = 2712, 3140, 2766, 3350
SUTRA_X1, SUTRA_Z1, SUTRA_X2, SUTRA_Z2 = 2718, 3150, 2760, 3240
SCRIBE_X1, SCRIBE_Z1, SCRIBE_X2, SCRIBE_Z2 = 2718, 3256, 2760, 3336

# Five-tier pagoda, north-west corner.
PAG_CX, PAG_CZ = 2465, 3085
PAG_TIERS = (
    (9, 5, 11, M.RED_WALL),
    (8, 13, 17, M.SMOOTH),
    (7, 19, 23, M.RED_WALL),
    (6, 25, 28, M.SMOOTH),
    (5, 30, 32, M.RED_WALL),
)

# Two monk-dormitory courts (僧房院).
COURT_S = (2660, 3048, 2750, 3128)
COURT_N = (2520, 3344, 2610, 3394)

LECTERN_E = "minecraft:lectern[facing=east]"
CHEST_E = "minecraft:chest[facing=east]"
CHEST_S = "minecraft:chest[facing=south]"
BOOKSHELF = "minecraft:bookshelf"
LOG_X = "minecraft:dark_oak_log[axis=x]"
QUARTZ_PILLAR_Y = "minecraft:quartz_pillar[axis=y]"

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
    ridge_block: str | None = None,
    layers: int | None = None,
) -> None:
    """Compact stepped gable (悬山顶): two stair slopes per layer plus a
    full flat ridge strip over the middle, so the roof is hole-free.
    axis 'x' = ridge runs east-west; axis 'z' = ridge runs north-south.
    """
    if axis == "x":
        n = layers if layers is not None else min(3, (z2 - z1) // 2)
        n = max(1, n)
        for i in range(n):
            add_fill(fills, f"{label} n {i}", (x1, y + i, z1 + i), (x2, y + i, z1 + i), _stair(roof_block, "south"))
            add_fill(fills, f"{label} s {i}", (x1, y + i, z2 - i), (x2, y + i, z2 - i), _stair(roof_block, "north"))
        add_fill(fills, f"{label} ridge", (x1 + 1, y + n, z1 + n), (x2 - 1, y + n, z2 - n), roof_block)
        if ridge_block:
            cz = (z1 + z2) // 2
            add_fill(fills, f"{label} gold ridge", (x1 + 2, y + n + 1, cz - 1), (x2 - 2, y + n + 1, cz + 1), ridge_block)
    else:
        n = layers if layers is not None else min(3, (x2 - x1) // 2)
        n = max(1, n)
        for i in range(n):
            add_fill(fills, f"{label} w {i}", (x1 + i, y + i, z1), (x1 + i, y + i, z2), _stair(roof_block, "east"))
            add_fill(fills, f"{label} e {i}", (x2 - i, y + i, z1), (x2 - i, y + i, z2), _stair(roof_block, "west"))
        add_fill(fills, f"{label} ridge", (x1 + n, y + n, z1 + 1), (x2 - n, y + n, z2 - 1), roof_block)
        if ridge_block:
            cx = (x1 + x2) // 2
            add_fill(fills, f"{label} gold ridge", (cx - 1, y + n + 1, z1 + 2), (cx + 1, y + n + 1, z2 - 2), ridge_block)


def _solid_hip_roof(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y: int,
    layers: int,
    roof_block: str = M.ROOF_GREEN,
    ridge_block: str = M.GOLD,
) -> None:
    """Solid-deck hip roof (庑殿顶) for the grand hall: each layer is a
    full shrinking rectangle (no open middle), with a stair skirt on the
    lower three slopes, a gold crown ridge and upturned gold corners.
    """
    add_fill(fills, f"{label} clear", (x1, y, z1), (x2, y + layers + 5, z2), M.AIR)
    for i in range(layers):
        ix1, ix2 = x1 + i, x2 - i
        iz1, iz2 = z1 + i, z2 - i
        if ix1 > ix2 or iz1 > iz2:
            break
        add_fill(fills, f"{label} deck {i}", (ix1, y + i, iz1), (ix2, y + i, iz2), roof_block)
    for i in range(min(2, layers)):
        add_fill(fills, f"{label} n skirt {i}", (x1 + i, y + i, z1 + i), (x2 - i, y + i, z1 + i), _stair(roof_block, "south"))
        add_fill(fills, f"{label} s skirt {i}", (x1 + i, y + i, z2 - i), (x2 - i, y + i, z2 - i), _stair(roof_block, "north"))
        if z1 + i + 1 <= z2 - i - 1:
            add_fill(fills, f"{label} w skirt {i}", (x1 + i, y + i, z1 + i + 1), (x1 + i, y + i, z2 - i - 1), _stair(roof_block, "east"))
            add_fill(fills, f"{label} e skirt {i}", (x2 - i, y + i, z1 + i + 1), (x2 - i, y + i, z2 - i - 1), _stair(roof_block, "west"))
    cz = (z1 + z2) // 2
    add_fill(fills, f"{label} ridge", (x1 + layers + 4, y + layers, cz - 1), (x2 - layers - 4, y + layers + 1, cz + 1), ridge_block)
    for dx, dz in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        ex = x1 - 1 if dx < 0 else x2 + 1
        ez = z1 - 1 if dz < 0 else z2 + 1
        add_fill(fills, f"{label} corner {dx},{dz}", (ex, y, ez), (ex, y + 2, ez), M.GOLD_ACCENT)


def _pavilion_roof(
    fills: list[Fill],
    label: str,
    cx: int,
    cz: int,
    radius: int,
    y: int,
    roof_block: str = M.ROOF_GREEN,
    apex_block: str = M.GOLD,
) -> None:
    """Compact pyramidal pavilion roof (攒尖顶) with a gilded finial:
    three shrinking stair rings over a sealed ceiling plus an eave slab."""
    for i in range(3):
        r = radius - i
        add_fill(fills, f"{label} n {i}", (cx - r, y + i, cz - r), (cx + r, y + i, cz - r), _stair(roof_block, "south"))
        add_fill(fills, f"{label} s {i}", (cx - r, y + i, cz + r), (cx + r, y + i, cz + r), _stair(roof_block, "north"))
        add_fill(fills, f"{label} w {i}", (cx - r, y + i, cz - r + 1), (cx - r, y + i, cz + r - 1), _stair(roof_block, "east"))
        add_fill(fills, f"{label} e {i}", (cx + r, y + i, cz - r + 1), (cx + r, y + i, cz + r - 1), _stair(roof_block, "west"))
    add_fill(fills, f"{label} apex", (cx - 1, y + 3, cz - 1), (cx + 1, y + 5, cz + 1), apex_block)
    add_outline(fills, f"{label} eave slab", cx - radius - 2, cz - radius - 2, cx + radius + 2, cz + radius + 2,
                y - 1, y - 1, f"minecraft:dark_prismarine_slab[type=bottom,waterlogged=false]", thickness=2)


def _cypress(fills: list[Fill], label: str, x: int, z: int, y: int) -> None:
    """Tall dark cypress (柏树): slim trunk with a narrow columnar crown."""
    add_fill(fills, f"{label} trunk", (x, y, z), (x, y + 8, z), M.TREE_LOG)
    add_fill(fills, f"{label} crown", (x - 2, y + 4, z - 2), (x + 2, y + 12, z + 2), M.LEAVES)


def _seated_buddha(fills: list[Fill], label: str, bx: int, bz: int, y0: int, big: bool) -> None:
    """Seated quartz Buddha on a gilded-base lotus throne facing south,
    with a tall gold halo panel (背光) rising behind. y0 = throne level.
    """
    add_fill(fills, f"{label} throne", (bx - 3, y0, bz - 2), (bx + 3, y0, bz + 2), M.GOLD_ACCENT)
    add_fill(fills, f"{label} legs", (bx - 3, y0 + 1, bz - 2), (bx + 3, y0 + 1, bz + 2), M.QUARTZ)
    if big:
        add_fill(fills, f"{label} body", (bx - 2, y0 + 2, bz - 1), (bx + 2, y0 + 5, bz + 1), M.QUARTZ)
        add_fill(fills, f"{label} head", (bx - 1, y0 + 6, bz), (bx + 1, y0 + 7, bz), M.QUARTZ)
        add_fill(fills, f"{label} halo", (bx - 4, y0 + 1, bz + 6), (bx + 4, y0 + 7, bz + 6), M.GOLD)
    else:
        add_fill(fills, f"{label} body", (bx - 2, y0 + 2, bz - 1), (bx + 2, y0 + 4, bz + 1), M.QUARTZ)
        add_fill(fills, f"{label} head", (bx - 1, y0 + 5, bz), (bx + 1, y0 + 6, bz), M.QUARTZ)
        add_fill(fills, f"{label} halo", (bx - 4, y0 + 1, bz + 6), (bx + 4, y0 + 6, bz + 6), M.GOLD)


def _arhat(fills: list[Fill], label: str, x: int, z: int, y0: int, item: str, side: int) -> None:
    """Standing arhat (罗汉): quartz body 1x2 with a held object at the
    hand, alternating between a gold scripture and an iron staff."""
    add_fill(fills, f"{label} body", (x, y0, z), (x, y0 + 1, z), M.QUARTZ)
    add_fill(fills, f"{label} item", (x + side, y0, z), (x + side, y0, z), item)


def _monk_court(fills: list[Fill], label: str, x1: int, z1: int, x2: int, z2: int, gate_west: bool, wing_east: bool) -> None:
    """One monk-dormitory court (僧房院): enclosure wall with gate, north
    main house (正房), side wing (厢房) and a courtyard well (水井)."""
    cx, cz = (x1 + x2) // 2, (z1 + z2) // 2
    add_outline(fills, f"{label} wall", x1, z1, x2, z2, 4, 9, M.WHITE_TERRACOTTA, thickness=1)
    if gate_west:
        add_fill(fills, f"{label} gate", (x1, 4, cz - 7), (x1, 7, cz + 7), M.AIR)
        add_fill(fills, f"{label} gate lintel", (x1, 8, cz - 8), (x1, 8, cz + 8), LOG_X)
    else:
        add_fill(fills, f"{label} gate", (cx - 7, 4, z1), (cx + 7, 7, z1), M.AIR)
        add_fill(fills, f"{label} gate lintel", (cx - 8, 8, z1), (cx + 8, 8, z1), LOG_X)

    # Main house (正房) along the north edge.
    mx1, mx2 = x1 + 6, x2 - 6
    mz1, mz2 = z2 - 18, z2 - 4
    add_fill(fills, f"{label} house floor", (mx1 + 1, 4, mz1 + 1), (mx2 - 1, 4, mz2 - 1), M.WOOD)
    add_hollow_box(fills, f"{label} house", mx1, 5, mz1, mx2, 10, mz2, M.RED_WALL, thickness=1)
    add_fill(fills, f"{label} house door", (cx - 4, 5, mz1), (cx + 4, 7, mz1), M.AIR)
    add_fill(fills, f"{label} house bed", (mx1 + 2, 5, mz2 - 8), (mx1 + 6, 5, mz2 - 4), M.WOOD)
    add_fill(fills, f"{label} house chest", (mx2 - 4, 5, mz1 + 3), (mx2 - 3, 6, mz1 + 3), CHEST_E)
    _gable_roof(fills, f"{label} house roof", mx1, mz1, mx2, mz2, 11, axis="x", roof_block=M.ROOF_GREEN, layers=2)

    # Side wing (厢房) along the west or east edge.
    if wing_east:
        wx1, wx2 = x2 - 15, x2 - 3
    else:
        wx1, wx2 = x1 + 3, x1 + 15
    wz1, wz2 = z1 + 18, mz1 - 6
    add_fill(fills, f"{label} wing floor", (wx1 + 1, 4, wz1 + 1), (wx2 - 1, 4, wz2 - 1), M.WOOD)
    add_hollow_box(fills, f"{label} wing", wx1, 5, wz1, wx2, 9, wz2, M.WHITE_TERRACOTTA, thickness=1)
    dmz = min(cz, wz2 - 3)
    door_x = wx1 if wing_east else wx2
    add_fill(fills, f"{label} wing door", (door_x, 5, dmz - 2), (door_x, 7, dmz + 2), M.AIR)
    _gable_roof(fills, f"{label} wing roof", wx1, wz1, wx2, wz2, 10, axis="z", roof_block=M.ROOF_BLUE, layers=2)

    # Courtyard well (水井) opposite the wing.
    if wing_east:
        ex1, ez1 = x1 + 18, z1 + 8
    else:
        ex1, ez1 = x2 - 26, z1 + 8
    add_fill(fills, f"{label} well basin", (ex1, 4, ez1), (ex1 + 8, 4, ez1 + 8), M.STONE)
    add_fill(fills, f"{label} well headroom", (ex1 + 1, 5, ez1 + 1), (ex1 + 7, 5, ez1 + 7), M.AIR)
    add_fill(fills, f"{label} well water", (ex1 + 3, 4, ez1 + 3), (ex1 + 5, 4, ez1 + 5), M.WATER)


# ---------------------------------------------------------------------------
# Main builder.
# ---------------------------------------------------------------------------
def build_ximingsi_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site grading: clear the old ward housing (mansion roofs and the
    #    ward temple reach up to y~27), then stone base + grass top.
    # ------------------------------------------------------------------
    add_fill(fills, "ximingsi clear site", (SITE_X1, 4, SITE_Z1), (SITE_X2, 8, SITE_Z2), M.AIR)
    # Tall clears over the four old mansion zones and the ward temple.
    add_fill(fills, "ximingsi clear old roof sw", (2450, 4, 3050), (2520, 24, 3110), M.AIR)
    add_fill(fills, "ximingsi clear old roof se", (2580, 4, 3050), (2650, 24, 3110), M.AIR)
    add_fill(fills, "ximingsi clear old roof nw", (2450, 4, 3190), (2520, 24, 3250), M.AIR)
    add_fill(fills, "ximingsi clear old roof ne", (2580, 4, 3190), (2650, 24, 3250), M.AIR)
    add_fill(fills, "ximingsi clear old temple", (2560, 4, 3035), (2630, 30, 3095), M.AIR)
    add_fill(fills, "ximingsi terrace stone", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "ximingsi terrace grass", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)

    # ------------------------------------------------------------------
    # 2. Red perimeter wall (寺墙) and the south mountain gate (山门).
    # ------------------------------------------------------------------
    add_outline(fills, "ximingsi wall", WALL_X1, WALL_Z1, WALL_X2, WALL_Z2, 4, 11, M.RED_WALL, thickness=2)
    # Gate tower body, passage, dark piers and timber lintel.
    add_fill(fills, "ximingsi gate tower", (GATE_X1, 4, GATE_Z1), (GATE_X2, 13, GATE_Z2), M.RED_WALL)
    add_fill(fills, "ximingsi gate passage", (GATE_PASS_X1, 4, GATE_Z1), (GATE_PASS_X2, 10, GATE_Z2), M.AIR)
    add_fill(fills, "ximingsi gate pier w", (2578, 4, 3041), (2583, 13, 3051), M.DARK)
    add_fill(fills, "ximingsi gate pier e", (2617, 4, 3041), (2622, 13, 3051), M.DARK)
    add_fill(fills, "ximingsi gate lintel", (2582, 11, 3041), (2618, 12, 3049), LOG_X)
    # "西明寺" gold plaque: dark frame plus three character panels.
    add_fill(fills, "ximingsi gate plaque frame", (2582, 7, 3035), (2618, 13, 3037), M.DARK)
    add_fill(fills, "ximingsi plaque char 1", (2585, 8, 3035), (2589, 12, 3036), M.GOLD)
    add_fill(fills, "ximingsi plaque char 2", (2596, 8, 3035), (2600, 12, 3036), M.GOLD)
    add_fill(fills, "ximingsi plaque char 3", (2607, 8, 3035), (2611, 12, 3036), M.GOLD)
    # Overhanging gable roof (悬山顶) over the gate.
    _gable_roof(fills, "ximingsi gate roof", 2564, GATE_Z1 - 2, 2636, GATE_Z2 + 2, 14,
                axis="x", roof_block=M.ROOF_DARK, ridge_block=M.GOLD, layers=2)

    # ------------------------------------------------------------------
    # 3. Axis walk (甬道): stone slabs, lantern posts, twin cypress files.
    # ------------------------------------------------------------------
    add_fill(fills, "ximingsi path pave", (PATH_X1, 3, PATH_Z1), (PATH_X2, 3, PATH_Z2), M.SMOOTH)
    add_lantern_line(fills, "ximingsi path lamp w", 2574, 3060, 2574, 3160, 4, every=60)
    add_lantern_line(fills, "ximingsi path lamp e", 2626, 3060, 2626, 3160, 4, every=60)
    for ti, (tx, tz) in enumerate([(2560, 3078), (2560, 3150), (2640, 3078), (2640, 3150)]):
        _cypress(fills, f"ximingsi cypress {ti}", tx, tz, 4)

    # ------------------------------------------------------------------
    # 4. Twin axis pavilions: bell pavilion (钟亭) west, stele pavilion
    #    (碑亭) east - four columns, pyramid roof (攒尖金顶).
    # ------------------------------------------------------------------
    for tag, px, pz in (("bell", BELL_CX, BELL_CZ), ("stele", STELE_CX, STELE_CZ)):
        add_fill(fills, f"ximingsi {tag} plinth", (px - 9, 4, pz - 9), (px + 9, 4, pz + 9), M.STONE)
        for ci, (colx, colz) in enumerate([(px - 6, pz - 6), (px + 5, pz - 6), (px - 6, pz + 5), (px + 5, pz + 5)]):
            add_fill(fills, f"ximingsi {tag} column {ci}", (colx, 5, colz), (colx + 1, 9, colz + 1), M.RED_WALL)
        add_fill(fills, f"ximingsi {tag} ceiling", (px - 6, 10, pz - 6), (px + 6, 10, pz + 6), M.LOG)
        _pavilion_roof(fills, f"ximingsi {tag} roof", px, pz, radius=6, y=11)
    # Bell: gold bell on an iron chain below the ceiling beam.
    add_fill(fills, "ximingsi bell", (BELL_CX - 1, 7, BELL_CZ - 1), (BELL_CX + 1, 8, BELL_CZ + 1), M.GOLD)
    add_fill(fills, "ximingsi bell chain", (BELL_CX, 9, BELL_CZ), (BELL_CX, 9, BELL_CZ), M.IRON_BARS)
    # Stele: gilded base, quartz-pillar shaft, dark cap.
    add_fill(fills, "ximingsi stele base", (STELE_CX - 2, 5, STELE_CZ - 2), (STELE_CX + 2, 5, STELE_CZ + 2), M.GOLD_ACCENT)
    add_fill(fills, "ximingsi stele shaft", (STELE_CX, 6, STELE_CZ), (STELE_CX, 11, STELE_CZ), QUARTZ_PILLAR_Y)
    add_fill(fills, "ximingsi stele cap", (STELE_CX - 1, 12, STELE_CZ - 1), (STELE_CX + 1, 12, STELE_CZ + 1), M.DARK)

    # ------------------------------------------------------------------
    # 5. Mahavira Hall (大雄宝殿): double stone terrace, red walls,
    #    double-eave hip roof, Buddhas and arhats inside.
    # ------------------------------------------------------------------
    add_fill(fills, "ximingsi hall tier1", (T1_X1, 5, T1_Z1), (T1_X2, 5, T1_Z2), M.STONE)
    add_fill(fills, "ximingsi hall tier2", (T2_X1, 6, T2_Z1), (T2_X2, 7, T2_Z2), M.SMOOTH)
    add_outline(fills, "ximingsi hall rail", T2_X1 + 1, T2_Z1 + 1, T2_X2 - 1, T2_Z2 - 1, 8, 8, M.FENCE, thickness=1)
    add_fill(fills, "ximingsi hall rail gap s", (2576, 8, T2_Z1 + 1), (2624, 10, T2_Z1 + 1), M.AIR)
    add_fill(fills, "ximingsi hall rail gap n", (2576, 8, T2_Z2 - 1), (2624, 10, T2_Z2 - 1), M.AIR)
    # Entrance steps south and north.
    add_fill(fills, "ximingsi hall step s1", (2574, 4, 3182), (2626, 4, 3185), M.SMOOTH)
    add_fill(fills, "ximingsi hall step s2", (2574, 5, 3186), (2626, 5, 3189), M.SMOOTH)
    add_fill(fills, "ximingsi hall step n1", (2574, 4, 3335), (2626, 4, 3338), M.SMOOTH)
    add_fill(fills, "ximingsi hall step n2", (2574, 5, 3331), (2626, 5, 3334), M.SMOOTH)
    # Red wall box (2 thick), interior air, timber floor.
    add_outline(fills, "ximingsi hall wall", HALL_X1, HALL_Z1, HALL_X2, HALL_Z2, 8, 17, M.RED_WALL, thickness=2)
    add_fill(fills, "ximingsi hall air", (HALL_X1 + 2, 9, HALL_Z1 + 2), (HALL_X2 - 2, 17, HALL_Z2 - 2), M.AIR)
    add_fill(fills, "ximingsi hall floor", (HALL_X1 + 1, 8, HALL_Z1 + 1), (HALL_X2 - 1, 8, HALL_Z2 - 1), M.WOOD)
    # Doors and windows.
    add_fill(fills, "ximingsi hall door s", (2580, 9, HALL_Z1), (2620, 12, HALL_Z1 + 1), M.AIR)
    add_fill(fills, "ximingsi hall door n", (2580, 9, HALL_Z2 - 1), (2620, 12, HALL_Z2), M.AIR)
    add_fill(fills, "ximingsi hall door e", (HALL_X2 - 1, 9, 3248), (HALL_X2, 12, 3264), M.AIR)
    add_fill(fills, "ximingsi hall win s w", (2530, 11, HALL_Z1), (2562, 14, HALL_Z1 + 1), M.GLASS)
    add_fill(fills, "ximingsi hall win s e", (2638, 11, HALL_Z1), (2670, 14, HALL_Z1 + 1), M.GLASS)
    add_fill(fills, "ximingsi hall win n w", (2530, 11, HALL_Z2 - 1), (2562, 14, HALL_Z2), M.GLASS)
    add_fill(fills, "ximingsi hall win n e", (2638, 11, HALL_Z2 - 1), (2670, 14, HALL_Z2), M.GLASS)
    add_fill(fills, "ximingsi hall win w", (HALL_X1, 11, 3244), (HALL_X1 + 1, 14, 3276), M.GLASS)
    # Interior columns flanking the central aisle.
    for ci, (colx, colz) in enumerate([(2540, 3228), (2540, 3260), (2660, 3228), (2660, 3260), (2568, 3244), (2632, 3244)]):
        add_fill(fills, f"ximingsi hall column {ci}", (colx, 9, colz), (colx + 1, 16, colz + 1), M.LOG)
    # Three World Buddhas (三世佛) on the north altar, facing south.
    add_fill(fills, "ximingsi altar", (2536, 9, 3272), (2664, 9, 3302), M.STONE)
    add_fill(fills, "ximingsi altar step", (2588, 9, 3268), (2612, 9, 3271), M.SMOOTH)
    _seated_buddha(fills, "ximingsi buddha w", 2570, 3288, 10, big=False)
    _seated_buddha(fills, "ximingsi buddha c", 2600, 3290, 10, big=True)
    _seated_buddha(fills, "ximingsi buddha e", 2630, 3288, 10, big=False)
    # Eighteen arhats (十八罗汉) in two files, items alternating.
    for i in range(9):
        az = 3220 + i * 9
        item = M.GOLD if i % 2 == 0 else M.IRON_BARS
        _arhat(fills, f"ximingsi arhat w{i}", 2534, az, 9, item, side=-1)
        _arhat(fills, f"ximingsi arhat e{i}", 2666, az, 9, item, side=1)
    # Lower eave: a full roof deck ring at y18 (重檐下檐).
    add_fill(fills, "ximingsi hall lower deck", (2508, 18, 3208), (2692, 18, 3312), M.ROOF_GREEN)
    # Upper storey and solid hip roof (庑殿顶) with beasts.
    add_outline(fills, "ximingsi hall upper", UP_X1, UP_Z1, UP_X2, UP_Z2, 19, 24, M.RED_WALL, thickness=2)
    add_fill(fills, "ximingsi hall upper air", (UP_X1 + 2, 20, UP_Z1 + 2), (UP_X2 - 2, 23, UP_Z2 - 2), M.AIR)
    add_fill(fills, "ximingsi hall upper door", (2576, 19, UP_Z1), (2624, 22, UP_Z1 + 1), M.AIR)
    add_fill(fills, "ximingsi hall upper win s", (2546, 21, UP_Z1), (2570, 23, UP_Z1 + 1), M.GLASS)
    add_fill(fills, "ximingsi hall upper win n", (2630, 21, UP_Z2 - 1), (2654, 23, UP_Z2), M.GLASS)
    _solid_hip_roof(fills, "ximingsi hall roof", ROOF_X1, ROOF_Z1, ROOF_X2, ROOF_Z2, 25, layers=8)
    add_roof_beasts(fills, "ximingsi hall beasts", ROOF_X1, ROOF_Z1, ROOF_X2, ROOF_Z2, 35, ridge_axis="x", count=3)

    # ------------------------------------------------------------------
    # 6. Sutra Library (藏经阁) west: two book storeys, gallery railings,
    #    spiral stair, gable roof.
    # ------------------------------------------------------------------
    add_fill(fills, "ximingsi lib plinth", (LIB_X1 - 2, 4, LIB_Z1 - 2), (LIB_X2 + 2, 4, LIB_Z2 - 2), M.STONE)
    add_outline(fills, "ximingsi lib s1", LIB_X1, LIB_Z1, LIB_X2, LIB_Z2, 5, 10, M.RED_WALL, thickness=1)
    add_fill(fills, "ximingsi lib s1 air", (LIB_X1 + 1, 6, LIB_Z1 + 1), (LIB_X2 - 1, 10, LIB_Z2 - 1), M.AIR)
    add_fill(fills, "ximingsi lib s1 floor", (LIB_X1 + 1, 5, LIB_Z1 + 1), (LIB_X2 - 1, 5, LIB_Z2 - 1), M.WOOD)
    add_fill(fills, "ximingsi lib door s1", (2452, 6, LIB_Z1), (2470, 9, LIB_Z1), M.AIR)
    add_fill(fills, "ximingsi lib shelf w1", (LIB_X1 + 1, 6, 3216), (LIB_X1 + 2, 8, 3304), BOOKSHELF)
    add_fill(fills, "ximingsi lib shelf e1", (LIB_X2 - 2, 6, 3216), (LIB_X2 - 1, 8, 3304), BOOKSHELF)
    add_fill(fills, "ximingsi lib shelf n1", (LIB_X1 + 3, 6, LIB_Z2 - 3), (LIB_X2 - 3, 8, LIB_Z2 - 2), BOOKSHELF)
    add_fill(fills, "ximingsi lib slab", (LIB_X1 - 2, 11, LIB_Z1 - 2), (LIB_X2 + 2, 11, LIB_Z2 + 2), M.WOOD)
    add_outline(fills, "ximingsi lib rail", LIB_X1 - 1, LIB_Z1 - 1, LIB_X2 + 1, LIB_Z2 + 1, 12, 12, M.FENCE, thickness=1)
    add_outline(fills, "ximingsi lib s2", LIB_X1, LIB_Z1, LIB_X2, LIB_Z2, 12, 16, M.RED_WALL, thickness=1)
    add_fill(fills, "ximingsi lib s2 air", (LIB_X1 + 1, 13, LIB_Z1 + 1), (LIB_X2 - 1, 16, LIB_Z2 - 1), M.AIR)
    add_fill(fills, "ximingsi lib s2 floor", (LIB_X1 + 1, 12, LIB_Z1 + 1), (LIB_X2 - 1, 12, LIB_Z2 - 1), M.WOOD)
    add_fill(fills, "ximingsi lib door s2", (2452, 13, LIB_Z1), (2470, 15, LIB_Z1), M.AIR)
    add_fill(fills, "ximingsi lib shelf w2", (LIB_X1 + 1, 13, 3216), (LIB_X1 + 2, 15, 3304), BOOKSHELF)
    add_fill(fills, "ximingsi lib shelf e2", (LIB_X2 - 2, 13, 3216), (LIB_X2 - 1, 15, 3304), BOOKSHELF)
    add_fill(fills, "ximingsi lib shelf n2", (LIB_X1 + 3, 13, LIB_Z2 - 3), (LIB_X2 - 3, 15, LIB_Z2 - 2), BOOKSHELF)
    add_spiral_stair(fills, "ximingsi lib stair", LIB_CX, LIB_CZ, radius=5, y1=6, y2=15)
    _gable_roof(fills, "ximingsi lib roof", LIB_X1, LIB_Z1, LIB_X2, LIB_Z2, 17, axis="z", roof_block=M.ROOF_GREEN)

    # ------------------------------------------------------------------
    # 7. Translation Academy court (翻经院) east: enclosure, translation
    #    hall (译经大堂) and scriptorium (写经房).
    # ------------------------------------------------------------------
    add_outline(fills, "ximingsi trans wall", TRANS_X1, TRANS_Z1, TRANS_X2, TRANS_Z2, 4, 10, M.WHITE_TERRACOTTA, thickness=1)
    add_fill(fills, "ximingsi trans gate", (TRANS_X1, 4, 3248), (TRANS_X1, 8, 3262), M.AIR)
    add_fill(fills, "ximingsi trans pier n", (TRANS_X1, 4, 3246), (TRANS_X1, 10, 3247), M.DARK)
    add_fill(fills, "ximingsi trans pier s", (TRANS_X1, 4, 3263), (TRANS_X1, 10, 3264), M.DARK)
    add_fill(fills, "ximingsi trans lintel", (TRANS_X1, 9, 3248), (TRANS_X1, 10, 3262), LOG_X)
    add_fill(fills, "ximingsi trans pave", (TRANS_X1 + 1, 3, TRANS_Z1 + 1), (TRANS_X2 - 1, 3, TRANS_Z2 - 1), M.ANDESITE)
    add_fill(fills, "ximingsi trans link", (2696, 3, 3246), (2711, 3, 3264), M.ANDESITE)
    add_fill(fills, "ximingsi hall step e", (2711, 4, 3246), (2711, 4, 3266), M.SMOOTH)

    # Translation hall (译经大堂): four long desks with white scrolls.
    add_fill(fills, "ximingsi sutra floor", (SUTRA_X1 + 1, 4, SUTRA_Z1 + 1), (SUTRA_X2 - 1, 4, SUTRA_Z2 - 1), M.WOOD)
    add_outline(fills, "ximingsi sutra hall", SUTRA_X1, SUTRA_Z1, SUTRA_X2, SUTRA_Z2, 5, 11, M.RED_WALL, thickness=1)
    add_fill(fills, "ximingsi sutra air", (SUTRA_X1 + 1, 6, SUTRA_Z1 + 1), (SUTRA_X2 - 1, 11, SUTRA_Z2 - 1), M.AIR)
    add_fill(fills, "ximingsi sutra door", (SUTRA_X1, 5, 3176), (SUTRA_X1, 8, 3194), M.AIR)
    add_fill(fills, "ximingsi sutra win w", (SUTRA_X1, 8, 3160), (SUTRA_X1, 10, 3170), M.GLASS)
    add_fill(fills, "ximingsi sutra win e", (SUTRA_X2, 8, 3214), (SUTRA_X2, 10, 3226), M.GLASS)
    _gable_roof(fills, "ximingsi sutra roof", SUTRA_X1, SUTRA_Z1, SUTRA_X2, SUTRA_Z2, 12, axis="z", roof_block=M.ROOF_GREEN, layers=2)
    for di, dz in enumerate((3162, 3178, 3194, 3210)):
        add_fill(fills, f"ximingsi sutra desk {di} base", (2726, 5, dz - 1), (2754, 5, dz + 1), M.LOG)
        add_fill(fills, f"ximingsi sutra desk {di} top", (2726, 6, dz - 1), (2754, 6, dz + 1), M.WOOD)
        add_fill(fills, f"ximingsi sutra scroll {di}", (2727, 7, dz - 1), (2753, 7, dz + 1), M.WHITE_WOOL)
    add_fill(fills, "ximingsi lectern a", (2723, 5, 3170), (2723, 5, 3170), LECTERN_E)
    add_fill(fills, "ximingsi lectern b", (2723, 5, 3202), (2723, 5, 3202), LECTERN_E)
    # Two seated translator statues (译师坐像) with gold caps.
    for si, sz in enumerate((3186, 3218)):
        add_fill(fills, f"ximingsi translator {si} stool", (2723, 5, sz), (2723, 5, sz), M.DARK)
        add_fill(fills, f"ximingsi translator {si} body", (2723, 6, sz), (2723, 8, sz), M.QUARTZ)
        add_fill(fills, f"ximingsi translator {si} head", (2723, 9, sz), (2723, 9, sz), M.QUARTZ)
        add_fill(fills, f"ximingsi translator {si} cap", (2723, 10, sz), (2723, 10, sz), M.GOLD)
    for li, lz in enumerate((3155, 3235)):
        add_fill(fills, f"ximingsi sutra lamp {li} post", (2721, 5, lz), (2721, 5, lz), M.FENCE)
        add_fill(fills, f"ximingsi sutra lamp {li} flame", (2721, 6, lz), (2721, 6, lz), M.LANTERN)

    # Scriptorium (写经房): bookshelf walls, sutra chests, candle lamps.
    add_fill(fills, "ximingsi scribe floor", (SCRIBE_X1 + 1, 4, SCRIBE_Z1 + 1), (SCRIBE_X2 - 1, 4, SCRIBE_Z2 - 1), M.WOOD)
    add_outline(fills, "ximingsi scribe hall", SCRIBE_X1, SCRIBE_Z1, SCRIBE_X2, SCRIBE_Z2, 5, 10, M.WHITE_TERRACOTTA, thickness=1)
    add_fill(fills, "ximingsi scribe air", (SCRIBE_X1 + 1, 6, SCRIBE_Z1 + 1), (SCRIBE_X2 - 1, 10, SCRIBE_Z2 - 1), M.AIR)
    add_fill(fills, "ximingsi scribe door", (SCRIBE_X1, 5, 3288), (SCRIBE_X1, 8, 3302), M.AIR)
    add_fill(fills, "ximingsi scribe win", (SCRIBE_X1, 7, 3266), (SCRIBE_X1, 9, 3280), M.GLASS)
    _gable_roof(fills, "ximingsi scribe roof", SCRIBE_X1, SCRIBE_Z1, SCRIBE_X2, SCRIBE_Z2, 11, axis="z", roof_block=M.ROOF_BLUE, layers=2)
    add_fill(fills, "ximingsi scribe shelf n", (SCRIBE_X1 + 1, 6, SCRIBE_Z2 - 3), (SCRIBE_X2 - 1, 9, SCRIBE_Z2 - 2), BOOKSHELF)
    add_fill(fills, "ximingsi scribe shelf e", (SCRIBE_X2 - 3, 6, SCRIBE_Z1 + 4), (SCRIBE_X2 - 2, 9, SCRIBE_Z2 - 4), BOOKSHELF)
    add_fill(fills, "ximingsi scribe shelf s", (SCRIBE_X1 + 1, 6, SCRIBE_Z1 + 1), (SCRIBE_X2 - 4, 9, SCRIBE_Z1 + 2), BOOKSHELF)
    add_fill(fills, "ximingsi scribe chests", (2728, 5, 3262), (2752, 6, 3262), CHEST_S)
    add_fill(fills, "ximingsi scribe desk base", (2730, 5, 3286), (2746, 5, 3288), M.LOG)
    add_fill(fills, "ximingsi scribe desk top", (2730, 6, 3286), (2746, 6, 3288), M.WOOD)
    for xi, (lx, lz) in enumerate([(2722, 3272), (2740, 3276)]):
        add_fill(fills, f"ximingsi scribe lamp {xi} post", (lx, 5, lz), (lx, 5, lz), M.FENCE)
        add_fill(fills, f"ximingsi scribe lamp {xi} flame", (lx, 6, lz), (lx, 6, lz), M.LANTERN)

    # ------------------------------------------------------------------
    # 8. Five-tier dense-eave pagoda (密檐塔), north-west corner.
    # ------------------------------------------------------------------
    add_fill(fills, "ximingsi pagoda plinth", (PAG_CX - 16, 4, PAG_CZ - 16), (PAG_CX + 16, 4, PAG_CZ + 16), M.STONE)
    for ti, (radius, y1, y2, block) in enumerate(PAG_TIERS):
        add_fill(fills, f"ximingsi pagoda body {ti}", (PAG_CX - radius, y1, PAG_CZ - radius), (PAG_CX + radius, y2, PAG_CZ + radius), block)
        if ti == 0:
            add_pagoda_openings(fills, f"ximingsi pagoda open {ti}", PAG_CX, PAG_CZ, radius, y1, y2 - y1 + 1)
        add_pagoda_eave(fills, f"ximingsi pagoda eave {ti}", PAG_CX, PAG_CZ, radius, y2 + 1, overhang=3)
    # Segmented gold finial (塔刹).
    add_fill(fills, "ximingsi pagoda finial base", (PAG_CX - 1, 34, PAG_CZ - 1), (PAG_CX + 1, 35, PAG_CZ + 1), M.GOLD)
    add_fill(fills, "ximingsi pagoda finial rod", (PAG_CX, 36, PAG_CZ), (PAG_CX, 37, PAG_CZ), M.GOLD)
    add_fill(fills, "ximingsi pagoda finial ring", (PAG_CX - 1, 38, PAG_CZ - 1), (PAG_CX + 1, 38, PAG_CZ + 1), M.GOLD)
    add_fill(fills, "ximingsi pagoda finial tip", (PAG_CX, 39, PAG_CZ), (PAG_CX, 40, PAG_CZ), M.GOLD)

    # ------------------------------------------------------------------
    # 9. Two monk-dormitory courts (僧房院), south and north.
    # ------------------------------------------------------------------
    _monk_court(fills, "ximingsi monks s", *COURT_S, gate_west=False, wing_east=False)
    _monk_court(fills, "ximingsi monks n", *COURT_N, gate_west=True, wing_east=True)

    # ------------------------------------------------------------------
    # 10. Rear and side greenery.
    # ------------------------------------------------------------------
    for gi, (gx, gz) in enumerate([(2480, 3360), (2700, 3372)]):
        add_tree(fills, f"ximingsi rear tree {gi}", gx, gz, 4, height=7, spread=2)


def main() -> None:
    run_builder(build_ximingsi_3d, "ximingsi_3d")


if __name__ == "__main__":
    main()
