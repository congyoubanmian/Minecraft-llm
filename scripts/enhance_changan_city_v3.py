from __future__ import annotations

import argparse
import json
import subprocess
import time
from dataclasses import dataclass


"""
Enhance Chang'an city v3 - finer architectural details on top of v1/v2 skeleton.

This script adds Tang-style refinements to key districts without replacing the
existing 6000x6000 grid.  It sends vanilla /fill commands through rcon-cli in
small chunks so the Paper server stays responsive.

Run a dry-run first:
    .venv/bin/python scripts/enhance_changan_city_v3.py --section palace
Then execute in batches:
    .venv/bin/python scripts/enhance_changan_city_v3.py --section palace --execute --limit 300
"""


BOT_USERNAME = "BuilderBot"
RCON_TIMEOUT = 240

BASE_X = 9000
BASE_Y = 64
BASE_Z = 9000

# Vanilla /fill volume limit is 32768 blocks.
MAX_FILL_VOLUME = 32768

# Materials
RED_WALL = "minecraft:red_terracotta"
RED_WALL_ALT = "minecraft:red_concrete"
GOLD = "minecraft:gold_block"
GOLD_ACCENT = "minecraft:gilded_blackstone"
ROOF_GREEN = "minecraft:dark_prismarine"
ROOF_GREEN_SLAB = "minecraft:dark_prismarine_slab"
ROOF_BLUE = "minecraft:prismarine_bricks"
STONE = "minecraft:stone_bricks"
MOSS_STONE = "minecraft:mossy_stone_bricks"
WHITE = "minecraft:white_concrete"
WHITE_TERRACOTTA = "minecraft:white_terracotta"
ANDESITE = "minecraft:polished_andesite"
SMOOTH = "minecraft:smooth_stone"
DARK = "minecraft:deepslate_tiles"
WOOD = "minecraft:dark_oak_planks"
LOG = "minecraft:dark_oak_log"
SPRUCE = "minecraft:spruce_planks"
GLASS = "minecraft:glass_pane"
LANTERN = "minecraft:lantern"
SEA_LANTERN = "minecraft:sea_lantern"
RED_WOOL = "minecraft:red_wool"
BLUE_WOOL = "minecraft:blue_wool"
YELLOW_WOOL = "minecraft:yellow_wool"
GREEN_WOOL = "minecraft:green_wool"
BLACK_WOOL = "minecraft:black_wool"
WATER = "minecraft:water"
LEAVES = "minecraft:oak_leaves"
TREE_LOG = "minecraft:oak_log"


@dataclass(frozen=True)
class Fill:
    label: str
    x1: int
    y1: int
    z1: int
    x2: int
    y2: int
    z2: int
    block: str


def w(x: int, y: int, z: int) -> tuple[int, int, int]:
    """Convert local city coordinates to world coordinates."""
    return BASE_X + x, BASE_Y + y, BASE_Z + z


def split_fill(label: str, a: tuple[int, int, int], b: tuple[int, int, int], block: str) -> list[Fill]:
    x1, y1, z1 = w(*a)
    x2, y2, z2 = w(*b)
    min_x, max_x = sorted((x1, x2))
    min_y, max_y = sorted((y1, y2))
    min_z, max_z = sorted((z1, z2))
    height = max_y - min_y + 1
    fills: list[Fill] = []
    max_width = min(max_x - min_x + 1, max(1, MAX_FILL_VOLUME // height))
    for sx in range(min_x, max_x + 1, max_width):
        ex = min(max_x, sx + max_width - 1)
        width = ex - sx + 1
        max_depth = max(1, MAX_FILL_VOLUME // (width * height))
        for sz in range(min_z, max_z + 1, max_depth):
            ez = min(max_z, sz + max_depth - 1)
            fills.append(Fill(label, sx, min_y, sz, ex, max_y, ez, block))
    return fills


def add_fill(fills: list[Fill], label: str, a: tuple[int, int, int], b: tuple[int, int, int], block: str) -> None:
    fills.extend(split_fill(label, a, b, block))


def add_outline(
    fills: list[Fill],
    label: str,
    x1: int,
    z1: int,
    x2: int,
    z2: int,
    y1: int,
    y2: int,
    block: str,
    thickness: int,
) -> None:
    add_fill(fills, f"{label} north", (x1, y1, z1), (x2, y2, z1 + thickness - 1), block)
    add_fill(fills, f"{label} south", (x1, y1, z2 - thickness + 1), (x2, y2, z2), block)
    add_fill(fills, f"{label} west", (x1, y1, z1), (x1 + thickness - 1, y2, z2), block)
    add_fill(fills, f"{label} east", (x2 - thickness + 1, y1, z1), (x2, y2, z2), block)


def add_hollow_box(
    fills: list[Fill],
    label: str,
    x1: int, y1: int, z1: int,
    x2: int, y2: int, z2: int,
    wall_block: str,
    thickness: int = 1,
) -> None:
    """Fill a box, leaving a smaller hollow core."""
    add_fill(fills, f"{label} outer", (x1, y1, z1), (x2, y2, z2), wall_block)
    ix1, iy1, iz1 = x1 + thickness, y1 + thickness, z1 + thickness
    ix2, iy2, iz2 = x2 - thickness, y2 - thickness, z2 - thickness
    if ix1 <= ix2 and iy1 <= iy2 and iz1 <= iz2:
        add_fill(fills, f"{label} inner air", (ix1, iy1, iz1), (ix2, iy2, iz2), "minecraft:air")


def add_platform_with_steps(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    base_y: int,
    tiers: list[tuple[int, int, str]],
) -> None:
    """
    Build a stepped platform.  tiers is a list of (height, inset, block).
    Each tier stacks on top of the previous one, inset from all sides.
    """
    y = base_y
    for index, (height, inset, block) in enumerate(tiers):
        add_fill(
            fills,
            f"{label} tier {index}",
            (x1 + inset, y, z1 + inset),
            (x2 - inset, y + height - 1, z2 - inset),
            block,
        )
        y += height


def add_column_grid(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y1: int, y2: int,
    spacing: int,
    column_block: str = LOG,
    column_size: int = 2,
) -> None:
    """Place columns on a regular grid inside the footprint."""
    xs = list(range(x1, x2 + 1, spacing))
    zs = list(range(z1, z2 + 1, spacing))
    for x in xs:
        for z in zs:
            if x1 < x < x2 and z1 < z < z2:
                add_fill(
                    fills,
                    f"{label} column at {x},{z}",
                    (x, y1, z),
                    (x + column_size - 1, y2, z + column_size - 1),
                    column_block,
                )


def add_ridge_roof(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y: int,
    layers: int,
    ridge_axis: str = "z",
    roof_block: str = ROOF_GREEN,
    ridge_block: str = GOLD,
) -> None:
    """
    Build a Chinese-style hip/gable roof by stacking shrinking rectangles.
    ridge_axis: 'x' or 'z' determines which direction the ridge runs.
    """
    for i in range(layers):
        inset = i * 10
        if ridge_axis == "z":
            rx1, rz1 = x1 + inset, z1 + inset
            rx2, rz2 = x2 - inset, z2 - inset
        else:
            rx1, rz1 = x1 + inset, z1 + inset
            rx2, rz2 = x2 - inset, z2 - inset
        if rx1 >= rx2 or rz1 >= rz2:
            break
        add_fill(fills, f"{label} roof layer {i}", (rx1, y + i * 2, rz1), (rx2, y + i * 2 + 1, rz2), roof_block)
    # Central ridge
    if ridge_axis == "z":
        mx = (x1 + x2) // 2
        add_fill(fills, f"{label} ridge", (mx - 2, y + layers * 2, z1 + 18), (mx + 2, y + layers * 2 + 3, z2 - 18), ridge_block)
    else:
        mz = (z1 + z2) // 2
        add_fill(fills, f"{label} ridge", (x1 + 18, y + layers * 2, mz - 2), (x2 - 18, y + layers * 2 + 3, mz + 2), ridge_block)


def add_dougong_brackets(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y: int,
    spacing: int = 28,
    bracket_block: str = WOOD,
) -> None:
    """
    Simulate dougong (corbel brackets) as small projections under the eaves.
    """
    xs = list(range(x1, x2 + 1, spacing))
    zs = list(range(z1, z2 + 1, spacing))
    for x in xs:
        add_fill(fills, f"{label} dougong x={x}", (x - 2, y, z1 - 2), (x + 2, y, z2 + 2), bracket_block)
    for z in zs:
        add_fill(fills, f"{label} dougong z={z}", (x1 - 2, y, z - 2), (x2 + 2, y, z + 2), bracket_block)


def add_lantern_line(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y: int,
    every: int,
) -> None:
    """Place lantern posts along a straight line."""
    if x1 == x2:
        for z in range(min(z1, z2), max(z1, z2) + 1, every):
            add_fill(fills, f"{label} post {z}", (x1 - 1, y, z - 1), (x1 + 1, y + 5, z + 1), LOG)
            add_fill(fills, f"{label} lamp {z}", (x1 - 1, y + 6, z - 1), (x1 + 1, y + 6, z + 1), SEA_LANTERN)
    elif z1 == z2:
        for x in range(min(x1, x2), max(x1, x2) + 1, every):
            add_fill(fills, f"{label} post {x}", (x - 1, y, z1 - 1), (x + 1, y + 5, z1 + 1), LOG)
            add_fill(fills, f"{label} lamp {x}", (x - 1, y + 6, z1 - 1), (x + 1, y + 6, z1 + 1), SEA_LANTERN)


def add_tree(fills: list[Fill], label: str, x: int, z: int, y: int, height: int = 7) -> None:
    """A simple cubic tree."""
    add_fill(fills, f"{label} trunk", (x, y, z), (x, y + height, z), TREE_LOG)
    add_fill(fills, f"{label} leaves", (x - 2, y + height - 1, z - 2), (x + 2, y + height + 2, z + 2), LEAVES)


# ---------------------------------------------------------------------------
# District builders
# ---------------------------------------------------------------------------

def build_palace_enhancements(fills: list[Fill]) -> None:
    """
    Add finer detail to the palace city (2140,4750)-(3860,5780).
    Hanyuan, Xuanzheng, Taiji halls get triple platforms, dougong, and ridge roofs.
    Palace walls are raised and given crenellations.
    """
    halls = [
        ("hanyuan_dian", 2660, 5180, 3340, 5480, 56),
        ("xuanzheng_dian", 2740, 4880, 3260, 5080, 44),
        ("taiji_dian", 2360, 5200, 2620, 5480, 40),
    ]

    for label, x1, z1, x2, z2, hall_height in halls:
        # Triple stone platform (taiji-style terraces)
        add_platform_with_steps(
            fills, f"{label} platform",
            x1 - 38, z1 - 38, x2 + 38, z2 + 38,
            1,
            [
                (3, 0, ANDESITE),      # lowest terrace
                (3, 6, SMOOTH),        # middle terrace
                (2, 12, ANDESITE),     # top terrace
            ],
        )

        # Main hall body on top of platform
        platform_top = 1 + 3 + 3 + 2  # = 9
        add_hollow_box(
            fills, f"{label} body",
            x1, platform_top, z1,
            x2, platform_top + hall_height, z2,
            RED_WALL, thickness=2,
        )

        # Column grid on the exterior (read as timber columns)
        add_column_grid(
            fills, f"{label} columns",
            x1, z1, x2, z2,
            platform_top, platform_top + hall_height - 2,
            spacing=28,
            column_block=RED_WALL_ALT,
            column_size=2,
        )

        # Door/window voids on front (south) facade
        mid_x = (x1 + x2) // 2
        add_fill(fills, f"{label} main door", (mid_x - 12, platform_top + 1, z1 - 3), (mid_x + 12, platform_top + 10, z1 + 2), "minecraft:air")
        add_fill(fills, f"{label} door frame", (mid_x - 14, platform_top + 1, z1 - 4), (mid_x + 14, platform_top + 12, z1 - 2), GOLD)

        # Side windows
        for wx in range(x1 + 24, x2 - 20, 36):
            add_fill(fills, f"{label} window {wx}", (wx, platform_top + 8, z1 - 2), (wx + 8, platform_top + 16, z1 + 1), "minecraft:air")
            add_fill(fills, f"{label} window frame {wx}", (wx - 1, platform_top + 7, z1 - 3), (wx + 9, platform_top + 17, z1 - 2), WOOD)

        # Dougong bracket layer under the eaves
        dougong_y = platform_top + hall_height + 1
        add_dougong_brackets(fills, f"{label} dougong", x1 - 6, z1 - 6, x2 + 6, z2 + 6, dougong_y, spacing=28)

        # Double-eave roof
        add_ridge_roof(
            fills, f"{label} roof",
            x1 - 30, z1 - 30, x2 + 30, z2 + 30,
            dougong_y + 1,
            layers=5,
            ridge_axis="z",
            roof_block=ROOF_GREEN,
            ridge_block=GOLD,
        )

        # Secondary lower roof (eave) around the first roof base
        add_outline(
            fills, f"{label} lower eave",
            x1 - 24, z1 - 24, x2 + 24, z2 + 24,
            dougong_y, dougong_y + 1,
            ROOF_GREEN,
            thickness=3,
        )

        # Corner ornaments (chiwen / guardian beasts)
        for cx, cz in [(x1 - 30, z1 - 30), (x2 + 30, z1 - 30), (x1 - 30, z2 + 30), (x2 + 30, z2 + 30)]:
            add_fill(fills, f"{label} corner ornament {cx},{cz}", (cx - 2, dougong_y + 10, cz - 2), (cx + 2, dougong_y + 14, cz + 2), GOLD)

    # Central red carpet axis from Chengtian Gate to Taiji Hall
    add_fill(fills, "palace axis red carpet", (2978, 2, 4100), (3022, 2, 5480), RED_WOOL)
    add_lantern_line(fills, "palace axis west lamps", 2958, 4140, 2958, 5440, 3, 60)
    add_lantern_line(fills, "palace axis east lamps", 3042, 4140, 3042, 5440, 3, 60)

    # Palace wall crenellations (along imperial city boundary 1800,4100-4200,5820)
    # Add a raised crenellation strip on top of the existing wall.
    wall_top = 23
    for x in range(1800, 4201, 12):
        # North and south walls
        add_fill(fills, f"palace wall crenel n {x}", (x, wall_top, 4100), (x + 4, wall_top + 2, 4104), DARK)
        add_fill(fills, f"palace wall crenel s {x}", (x, wall_top, 5816), (x + 4, wall_top + 2, 5820), DARK)
    for z in range(4100, 5821, 12):
        add_fill(fills, f"palace wall crenel w {z}", (1800, wall_top, z), (1804, wall_top + 2, z + 4), DARK)
        add_fill(fills, f"palace wall crenel e {z}", (4196, wall_top, z), (4200, wall_top + 2, z + 4), DARK)


def build_gate_enhancements(fills: list[Fill]) -> None:
    """
    Add gate towers, barbicans, and plaques to the 12 city gates.
    South gates: Yanping, Zhuque, Qixia.
    North gates: mirrored.
    East/West gates: Kaiyuan, Jinguang, Yanshou.
    """
    south_names = [(1200, "yanping"), (3000, "zhuque"), (4800, "qixia")]
    east_west_names = [(1500, "kaiyuan"), (3000, "jinguang"), (4500, "yanshou")]

    def add_south_gate_details(label: str, cx: int) -> None:
        # Gate tower on top of existing gatehouse
        add_hollow_box(fills, f"{label} tower", cx - 40, 39, -44, cx + 40, 62, 44, RED_WALL, thickness=2)
        # Tower roof
        add_ridge_roof(fills, f"{label} tower roof", cx - 48, -52, cx + 48, 52, 63, layers=4, ridge_axis="z")
        # Side watch towers
        for ox in (cx - 150, cx + 150):
            add_hollow_box(fills, f"{label} watch tower {ox}", ox - 18, 1, -28, ox + 18, 50, 28, STONE, thickness=2)
            add_ridge_roof(fills, f"{label} watch roof {ox}", ox - 24, -34, ox + 24, 34, 51, layers=4, ridge_axis="z")
        # Plaque above gate opening
        add_fill(fills, f"{label} plaque board", (cx - 20, 32, -35), (cx + 20, 36, -32), GOLD)
        add_fill(fills, f"{label} plaque text", (cx - 12, 33, -36), (cx + 12, 35, -36), BLACK_WOOL)
        # Barbican (outer half-moon wall)
        add_outline(fills, f"{label} barbican", cx - 90, 80, cx + 90, 180, 1, 10, STONE, thickness=4)

    def add_east_west_gate_details(label: str, cz: int) -> None:
        add_hollow_box(fills, f"{label} tower", -44, 39, cz - 40, 44, 62, cz + 40, RED_WALL, thickness=2)
        add_ridge_roof(fills, f"{label} tower roof", -52, cz - 48, 52, cz + 48, 63, layers=4, ridge_axis="x")
        for oz in (cz - 150, cz + 150):
            add_hollow_box(fills, f"{label} watch tower {oz}", -28, 1, oz - 18, 28, 50, oz + 18, STONE, thickness=2)
            add_ridge_roof(fills, f"{label} watch roof {oz}", -34, oz - 24, 34, oz + 24, 51, layers=4, ridge_axis="x")
        add_fill(fills, f"{label} plaque board", (-35, 32, cz - 20), (-32, 36, cz + 20), GOLD)
        add_fill(fills, f"{label} plaque text", (-36, 33, cz - 12), (-36, 35, cz + 12), BLACK_WOOL)
        add_outline(fills, f"{label} barbican", 80, cz - 90, 180, cz + 90, 1, 10, STONE, thickness=4)

    for cx, name in south_names:
        add_south_gate_details(f"gate_{name}", cx)
        add_south_gate_details(f"gate_north_{name}", cx)  # north side mirror

    for cz, name in east_west_names:
        add_east_west_gate_details(f"gate_{name}", cz)
        add_east_west_gate_details(f"gate_east_{name}", cz)


def build_market_enhancements(fills: list[Fill]) -> None:
    """
    Add distinct shop types, signage, and central plaza features to East/West Markets.
    """
    markets = [
        ("west_market", 760, 2060, 1760, 3060),
        ("east_market", 4240, 2060, 5240, 3060),
    ]

    shop_types = [
        ("tavern", RED_WOOL, RED_WOOL),
        ("cloth", BLUE_WOOL, BLUE_WOOL),
        ("tea", YELLOW_WOOL, YELLOW_WOOL),
        ("iron", SMOOTH, DARK),
        ("inn", SPRUCE, WOOD),
    ]

    for label, x1, z1, x2, z2 in markets:
        mid_x = (x1 + x2) // 2
        mid_z = (z1 + z2) // 2

        # Central market tower / market office
        add_hollow_box(fills, f"{label} market tower", mid_x - 28, 1, mid_z - 28, mid_x + 28, 28, mid_z + 28, WOOD, thickness=2)
        add_ridge_roof(fills, f"{label} market tower roof", mid_x - 34, mid_z - 34, mid_x + 34, mid_z + 34, 29, layers=3, ridge_axis="z")

        # Main cross streets with drainage channel
        add_fill(fills, f"{label} main street x", (x1 + 60, 2, mid_z - 12), (x2 - 60, 2, mid_z + 12), SMOOTH)
        add_fill(fills, f"{label} main street z", (mid_x - 12, 2, z1 + 60), (mid_x + 12, 2, z2 - 60), SMOOTH)

        # Shops along streets
        index = 0
        for x in range(x1 + 80, x2 - 130, 110):
            for z in range(z1 + 80, z2 - 80, 90):
                if abs(x - mid_x) < 40 and abs(z - mid_z) < 40:
                    continue  # leave central plaza open
                shop_type, wall_block, sign_block = shop_types[index % len(shop_types)]
                sx = x
                sz = z
                # Two-storey shop block
                add_hollow_box(fills, f"{label} {shop_type} {index}", sx, 2, sz, sx + 42, 14, sz + 28, wall_block, thickness=1)
                # Roof
                add_ridge_roof(fills, f"{label} {shop_type} {index} roof", sx - 4, sz - 4, sx + 46, sz + 32, 15, layers=2, ridge_axis="z")
                # Signboard
                add_fill(fills, f"{label} {shop_type} {index} sign", (sx + 8, 10, sz - 1), (sx + 34, 13, sz - 1), sign_block)
                index += 1

        # Wells and banners in plaza
        for dx, dz in [(-50, -50), (50, -50), (-50, 50), (50, 50)]:
            add_fill(fills, f"{label} well {dx},{dz}", (mid_x + dx - 6, 2, mid_z + dz - 6), (mid_x + dx + 6, 2, mid_z + dz + 6), ANDESITE)
            add_fill(fills, f"{label} well water {dx},{dz}", (mid_x + dx - 4, 2, mid_z + dz - 4), (mid_x + dx + 4, 2, mid_z + dz + 4), WATER)
            add_fill(fills, f"{label} banner pole {dx},{dz}", (mid_x + dx - 1, 2, mid_z + dz - 20), (mid_x + dx + 1, 20, mid_z + dz - 20), LOG)
            add_fill(fills, f"{label} banner cloth {dx},{dz}", (mid_x + dx + 2, 12, mid_z + dz - 28), (mid_x + dx + 2, 19, mid_z + dz - 12), RED_WOOL)


def build_ward_enhancements(fills: list[Fill]) -> None:
    """
    Upgrade ward gates to paifang-style arches and add courtyard buildings inside selected wards.
    """
    x_lines = [520, 900, 1280, 1660, 2040, 2420, 3420, 3800, 4180, 4560, 4940, 5320]
    z_lines = [620, 1020, 1420, 1820, 2220, 2620, 3020, 3420, 3820]

    index = 0
    for x in x_lines:
        for z in z_lines:
            # Skip imperial city and market areas
            if 1800 <= x <= 4200 and z >= 4100:
                continue
            if 700 <= x <= 1800 and 2000 <= z <= 3100:
                continue
            if 4200 <= x <= 5300 and 2000 <= z <= 3100:
                continue

            gate_x = x + 130

            # Paifang-style gate: two pillars and a beam
            add_fill(fills, f"ward {index} paifang left", (gate_x - 18, 2, z - 3), (gate_x - 13, 18, z + 3), RED_WALL)
            add_fill(fills, f"ward {index} paifang right", (gate_x + 13, 2, z - 3), (gate_x + 18, 18, z + 3), RED_WALL)
            add_fill(fills, f"ward {index} paifang beam", (gate_x - 22, 18, z - 4), (gate_x + 22, 22, z + 4), WOOD)
            add_ridge_roof(fills, f"ward {index} paifang roof", gate_x - 26, z - 6, gate_x + 26, z + 6, 23, layers=2, ridge_axis="z")

            # Interior building for every 4th ward (temples / mansions)
            if index % 4 == 0:
                bx = x + 65
                bz = z + 70
                add_hollow_box(fills, f"ward {index} mansion", bx, 2, bz, bx + 130, 18, bz + 80, WHITE, thickness=1)
                add_ridge_roof(fills, f"ward {index} mansion roof", bx - 6, bz - 6, bx + 136, bz + 86, 19, layers=3, ridge_axis="z")
                add_fill(fills, f"ward {index} courtyard", (bx + 20, 1, bz + 90), (bx + 110, 1, bz + 130), SMOOTH)
                add_fill(fills, f"ward {index} front gate", (bx + 55, 2, z + 5), (bx + 75, 8, z + 10), RED_WALL)

            index += 1


def build_landmark_enhancements(fills: list[Fill]) -> None:
    """
    Upgrade Giant/Small Wild Goose Pagodas to multi-tier pagodas and add temple courtyards.
    """
    pagodas = [
        ("giant_wild_goose_pagoda", 4580, 3860, 44, 92, 7),
        ("small_wild_goose_pagoda", 1320, 3700, 34, 70, 13),
    ]

    for label, cx, cz, radius, height, tiers in pagodas:
        y = 1
        current_radius = radius
        for tier in range(tiers):
            tier_height = max(5, height // tiers)
            # Square body (Minecraft-friendly)
            r = current_radius
            add_hollow_box(fills, f"{label} tier {tier}", cx - r, y, cz - r, cx + r, y + tier_height, cz + r, WHITE, thickness=2)
            # Eave projection
            add_outline(fills, f"{label} tier {tier} eave", cx - r - 4, cz - r - 4, cx + r + 4, cz + r + 4, y + tier_height, y + tier_height + 1, ROOF_GREEN, thickness=2)
            y += tier_height + 2
            current_radius = max(6, current_radius - 3)

        # Spire
        add_fill(fills, f"{label} spire", (cx - 2, y, cz - 2), (cx + 2, y + 18, cz + 2), GOLD)

    # Temple courtyards around the pagodas
    for label, cx, cz, *_ in pagodas:
        # Outer wall
        add_outline(fills, f"{label} temple wall", cx - 90, cz - 90, cx + 90, cz + 90, 1, 6, RED_WALL, thickness=2)
        # Gate
        add_fill(fills, f"{label} temple gate", (cx - 14, 1, cz - 92), (cx + 14, 12, cz - 88), RED_WALL)
        add_ridge_roof(fills, f"{label} temple gate roof", cx - 18, cz - 96, cx + 18, cz - 84, 13, layers=2, ridge_axis="z")
        # Incense burner
        add_fill(fills, f"{label} incense burner", (cx - 4, 2, cz - 40), (cx + 4, 6, cz - 32), GOLD)


def build_street_enhancements(fills: list[Fill]) -> None:
    """
    Add street lamps, trees, and ceremonial archways along main avenues.
    """
    # Zhuque Avenue central median and lamps
    add_fill(fills, "zhuque avenue median", (2994, 3, 0), (3006, 3, 5999), ANDESITE)
    add_lantern_line(fills, "zhuque avenue west lamps", 2960, 0, 2960, 5999, 3, 80)
    add_lantern_line(fills, "zhuque avenue east lamps", 3040, 0, 3040, 5999, 3, 80)

    # Trees along other avenues
    avenue_xs = [900, 1800, 3000, 4200, 5100]
    for x in avenue_xs:
        for z in range(100, 5900, 120):
            add_tree(fills, f"avenue x={x} z={z}", x - 45, z, 2)
            add_tree(fills, f"avenue x={x} z={z} east", x + 45, z, 2)

    avenue_zs = [900, 1700, 2500, 3300, 4100, 5000]
    for z in avenue_zs:
        for x in range(100, 5900, 120):
            add_tree(fills, f"avenue z={z} x={x}", x, z - 45, 2)
            add_tree(fills, f"avenue z={z} x={x} south", x, z + 45, 2)

    # Ceremonial archways (fang) at major intersections
    intersections = [
        (3000, 3000),
        (1200, 3000),
        (4800, 3000),
        (3000, 1500),
        (3000, 4800),
    ]
    for idx, (ix, iz) in enumerate(intersections):
        # Four pillars
        for dx, dz in [(-18, -4), (18, -4), (-18, 4), (18, 4)]:
            add_fill(fills, f"archway {idx} pillar {dx},{dz}", (ix + dx, 2, iz + dz), (ix + dx + 3, 22, iz + dz + 3), RED_WALL)
        # Beam
        add_fill(fills, f"archway {idx} beam", (ix - 24, 22, iz - 6), (ix + 24, 26, iz + 6), WOOD)
        add_ridge_roof(fills, f"archway {idx} roof", ix - 28, iz - 8, ix + 28, iz + 8, 27, layers=2, ridge_axis="z")


# ---------------------------------------------------------------------------
# Execution helpers
# ---------------------------------------------------------------------------

def rcon(command: str, timeout: int) -> str:
    return subprocess.check_output(
        ["docker", "exec", "mc-ai-paper", "rcon-cli", command],
        text=True,
        timeout=timeout,
    ).strip()


def chunk_coords(x: int, z: int) -> tuple[int, int]:
    return x >> 4, z >> 4


def execute_fill(fill: Fill, timeout: int, use_forceload: bool) -> str:
    if use_forceload:
        corners = sorted(
            {
                chunk_coords(fill.x1, fill.z1),
                chunk_coords(fill.x1, fill.z2),
                chunk_coords(fill.x2, fill.z1),
                chunk_coords(fill.x2, fill.z2),
            }
        )
        for cx, cz in corners:
            rcon(f"forceload add {cx * 16} {cz * 16}", timeout)
    else:
        corners = []
    try:
        return rcon(
            f"fill {fill.x1} {fill.y1} {fill.z1} {fill.x2} {fill.y2} {fill.z2} {fill.block}",
            timeout,
        )
    finally:
        for cx, cz in corners:
            rcon(f"forceload remove {cx * 16} {cz * 16}", timeout)


SECTION_BUILDERS = {
    "palace": build_palace_enhancements,
    "gates": build_gate_enhancements,
    "markets": build_market_enhancements,
    "wards": build_ward_enhancements,
    "landmarks": build_landmark_enhancements,
    "streets": build_street_enhancements,
    "all": None,  # special-cased below
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Add finer Tang-style details to Chang'an city.")
    parser.add_argument(
        "--section",
        choices=list(SECTION_BUILDERS.keys()),
        default="all",
        help="Which district to enhance.",
    )
    parser.add_argument("--execute", action="store_true", help="Actually send commands to the server.")
    parser.add_argument("--start", type=int, default=0, help="0-based fill offset.")
    parser.add_argument("--limit", type=int, default=None, help="Only process N fills.")
    parser.add_argument("--delay-ms", type=int, default=60, help="Delay between /fill commands.")
    parser.add_argument("--report-every", type=int, default=100)
    parser.add_argument("--timeout", type=int, default=RCON_TIMEOUT)
    parser.add_argument("--no-forceload", action="store_true", help="Skip forceload (only if chunks already loaded).")
    args = parser.parse_args()

    fills: list[Fill] = []
    if args.section == "all":
        for builder in SECTION_BUILDERS.values():
            if builder is not None:
                builder(fills)
    else:
        SECTION_BUILDERS[args.section](fills)

    selected = fills[args.start :]
    if args.limit is not None:
        selected = selected[: args.limit]

    print(
        json.dumps(
            {
                "section": args.section,
                "total_fills": len(fills),
                "selected_fills": len(selected),
                "start": args.start,
                "execute": args.execute,
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )

    if not args.execute:
        return

    rcon("gamerule randomTickSpeed 0", args.timeout)
    rcon("weather clear", args.timeout)
    for index, fill in enumerate(selected, start=1):
        output = execute_fill(fill, args.timeout, not args.no_forceload)
        if args.delay_ms:
            time.sleep(args.delay_ms / 1000)
        if index % args.report_every == 0 or index == len(selected):
            print(
                json.dumps(
                    {
                        "done": index,
                        "total": len(selected),
                        "absolute_fill": args.start + index,
                        "label": fill.label,
                        "sample": f"{fill.x1} {fill.y1} {fill.z1} {fill.x2} {fill.y2} {fill.z2} {fill.block}",
                        "result": output[:160],
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )


if __name__ == "__main__":
    main()
