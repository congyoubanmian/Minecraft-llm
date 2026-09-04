from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
import os
import socket
import struct
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

# Make the repository root importable when this script is run directly.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


"""
Shared building library for Tang Chang'an architectural modules.

Provides coordinate conversion, volume-limited /fill generation, common
Tang-style primitives (platforms, columns, roofs, dougong, lanterns, trees),
and an rcon execution harness that every per-building script can reuse.
"""


# ---------------------------------------------------------------------------
# Global coordinate anchor for the whole Chang'an city.
# All per-building scripts use local coordinates relative to this origin.
# ---------------------------------------------------------------------------
BASE_X = 9000
BASE_Y = 64
BASE_Z = 9000

# Vanilla /fill limit is 32768 blocks per command.
MAX_FILL_VOLUME = 32768
# Keep each forceload window at most 8x8 chunks. Dense farm passes otherwise
# load 256 chunks at once and can drive the server below 10 TPS.
LOAD_REGION_SIZE = 128

RCON_TIMEOUT = 240
DOCKER_CONTAINER = "mc-ai-paper"
RCON_HOST = os.getenv("RCON_HOST", "127.0.0.1")
RCON_PORT = int(os.getenv("RCON_PORT", "25575"))
RCON_PASSWORD = os.getenv("RCON_PASSWORD", "minecraft-ai-builder")


# ---------------------------------------------------------------------------
# Shared city layout constants for the 6000x6000 Chang'an grid.
# ---------------------------------------------------------------------------
WARD_BLOCK_SIZE = 260
WARD_X_LINES = [520, 900, 1280, 1660, 2040, 2420, 3420, 3800, 4180, 4560, 4940, 5320]
WARD_Z_LINES = [620, 1020, 1420, 1820, 2220, 2620, 3020, 3420, 3820]


def is_ward_excluded(x: int, z: int) -> bool:
    """Return True for imperial city and market areas that should not be tiled as wards."""
    if 1800 <= x <= 4200 and z >= 4100:
        return True
    if 700 <= x <= 1800 and 2000 <= z <= 3100:
        return True
    if 4200 <= x <= 5300 and 2000 <= z <= 3100:
        return True
    return False


def iter_ward_origins() -> list[tuple[int, int]]:
    """Return all ward origin (x, z) corners, skipping excluded imperial/market zones."""
    return [
        (x, z)
        for x in WARD_X_LINES
        for z in WARD_Z_LINES
        if not is_ward_excluded(x, z)
    ]


# ---------------------------------------------------------------------------
# Tang-style material palette.
# ---------------------------------------------------------------------------
class Materials:
    # Walls & masonry
    RED_WALL = "minecraft:red_terracotta"
    RED_WALL_ALT = "minecraft:red_concrete"
    RED_GLAZED = "minecraft:red_glazed_terracotta"
    STONE = "minecraft:stone_bricks"
    MOSS_STONE = "minecraft:mossy_stone_bricks"
    CRACKED_STONE = "minecraft:cracked_stone_bricks"
    DARK = "minecraft:deepslate_tiles"
    DARK_BRICKS = "minecraft:deepslate_bricks"
    ANDESITE = "minecraft:polished_andesite"
    GRANITE = "minecraft:polished_granite"
    SMOOTH = "minecraft:smooth_stone"
    COBBLE = "minecraft:cobblestone"
    GRAY_CONCRETE = "minecraft:gray_concrete"

    # Metals / bars
    IRON_BARS = "minecraft:iron_bars"

    # Imperial accents
    GOLD = "minecraft:gold_block"
    GOLD_ACCENT = "minecraft:gilded_blackstone"
    YELLOW_GLAZED = "minecraft:yellow_glazed_terracotta"

    # Roofs (Tang green/blue glazed tile)
    ROOF_GREEN = "minecraft:dark_prismarine"
    ROOF_GREEN_SLAB = "minecraft:dark_prismarine_slab"
    ROOF_BLUE = "minecraft:prismarine_bricks"
    ROOF_BLUE_SLAB = "minecraft:prismarine_brick_slab"
    ROOF_DARK = "minecraft:deepslate_tiles"

    # Timber
    LOG = "minecraft:dark_oak_log"
    WOOD = "minecraft:dark_oak_planks"
    SPRUCE = "minecraft:spruce_planks"
    BIRCH = "minecraft:birch_planks"
    FENCE = "minecraft:dark_oak_fence"

    # Plaster / jade
    WHITE = "minecraft:white_concrete"
    WHITE_TERRACOTTA = "minecraft:white_terracotta"
    QUARTZ = "minecraft:quartz_block"

    # Windows & lights
    GLASS = "minecraft:glass_pane"
    RED_STAINED_GLASS = "minecraft:red_stained_glass_pane"
    LANTERN = "minecraft:lantern"
    SEA_LANTERN = "minecraft:sea_lantern"
    REDSTONE_LAMP = "minecraft:redstone_lamp"

    # Fabrics / market signs
    RED_WOOL = "minecraft:red_wool"
    BLUE_WOOL = "minecraft:blue_wool"
    YELLOW_WOOL = "minecraft:yellow_wool"
    GREEN_WOOL = "minecraft:green_wool"
    BLACK_WOOL = "minecraft:black_wool"
    WHITE_WOOL = "minecraft:white_wool"
    PINK_WOOL = "minecraft:pink_wool"

    # Nature
    WATER = "minecraft:water"
    LEAVES = "minecraft:oak_leaves"
    TREE_LOG = "minecraft:oak_log"
    GRASS = "minecraft:grass_block"
    DIRT = "minecraft:dirt"

    AIR = "minecraft:air"


# ---------------------------------------------------------------------------
# Low-level primitives.
# ---------------------------------------------------------------------------
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
    """Split a large box into vanilla-sized /fill commands."""
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
    x1: int, z1: int,
    x2: int, z2: int,
    y1: int, y2: int,
    block: str,
    thickness: int = 1,
) -> None:
    add_fill(fills, f"{label} n", (x1, y1, z1), (x2, y2, z1 + thickness - 1), block)
    add_fill(fills, f"{label} s", (x1, y1, z2 - thickness + 1), (x2, y2, z2), block)
    add_fill(fills, f"{label} w", (x1, y1, z1), (x1 + thickness - 1, y2, z2), block)
    add_fill(fills, f"{label} e", (x2 - thickness + 1, y1, z1), (x2, y2, z2), block)


def add_hollow_box(
    fills: list[Fill],
    label: str,
    x1: int, y1: int, z1: int,
    x2: int, y2: int, z2: int,
    wall_block: str,
    thickness: int = 1,
) -> None:
    add_fill(fills, f"{label} wall", (x1, y1, z1), (x2, y2, z2), wall_block)
    ix1, iy1, iz1 = x1 + thickness, y1 + thickness, z1 + thickness
    ix2, iy2, iz2 = x2 - thickness, y2 - thickness, z2 - thickness
    if ix1 <= ix2 and iy1 <= iy2 and iz1 <= iz2:
        add_fill(fills, f"{label} air", (ix1, iy1, iz1), (ix2, iy2, iz2), Materials.AIR)


def add_box_frame(
    fills: list[Fill],
    label: str,
    x1: int, y1: int, z1: int,
    x2: int, y2: int, z2: int,
    block: str,
    thickness: int = 1,
) -> None:
    """Frame only: top/bottom ring + four vertical edges."""
    # Top and bottom plates
    add_fill(fills, f"{label} bottom", (x1, y1, z1), (x2, y1, z2), block)
    add_fill(fills, f"{label} top", (x1, y2, z1), (x2, y2, z2), block)
    # Four vertical edges
    add_fill(fills, f"{label} edge nw", (x1, y1, z1), (x1 + thickness - 1, y2, z1 + thickness - 1), block)
    add_fill(fills, f"{label} edge ne", (x2 - thickness + 1, y1, z1), (x2, y2, z1 + thickness - 1), block)
    add_fill(fills, f"{label} edge sw", (x1, y1, z2 - thickness + 1), (x1 + thickness - 1, y2, z2), block)
    add_fill(fills, f"{label} edge se", (x2 - thickness + 1, y1, z2 - thickness + 1), (x2, y2, z2), block)


# ---------------------------------------------------------------------------
# Architectural primitives.
# ---------------------------------------------------------------------------
def add_platform_with_steps(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    base_y: int,
    tiers: list[tuple[int, int, str]],
) -> None:
    """
    Build a stepped platform. tiers is a list of (height, inset, block).
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
    column_block: str = Materials.LOG,
    column_size: int = 2,
) -> None:
    xs = list(range(x1, x2 + 1, spacing))
    zs = list(range(z1, z2 + 1, spacing))
    for x in xs:
        for z in zs:
            if x1 < x < x2 and z1 < z < z2:
                add_fill(
                    fills,
                    f"{label} col {x},{z}",
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
    roof_block: str = Materials.ROOF_GREEN,
    ridge_block: str = Materials.GOLD,
    eave_block: str | None = None,
) -> None:
    """Replace the old roof volume with a thin directional stair roof."""
    if layers < 1:
        return

    variants = {
        Materials.ROOF_GREEN: ("minecraft:dark_prismarine_stairs", "minecraft:dark_prismarine_slab"),
        Materials.ROOF_BLUE: ("minecraft:prismarine_brick_stairs", "minecraft:prismarine_brick_slab"),
        Materials.ROOF_DARK: ("minecraft:deepslate_tile_stairs", "minecraft:deepslate_tile_slab"),
    }
    stair_id, slab_id = variants.get(roof_block, variants[Materials.ROOF_GREEN])
    steps = max(3, layers * 2)
    ridge_y = y + steps

    # Clearing is deliberate: this pass replaces previous flat or malformed roofs.
    add_fill(fills, f"{label} clear old roof", (x1, y, z1), (x2, ridge_y + 6, z2), Materials.AIR)

    def stair(facing: str) -> str:
        return f"{stair_id}[facing={facing},half=bottom,shape=straight,waterlogged=false]"

    slab = f"{slab_id}[type=bottom,waterlogged=false]"
    cx, cz = (x1 + x2) // 2, (z1 + z2) // 2
    if ridge_axis == "z":
        run = max(1, math.ceil((cx - x1) / steps))
        for i in range(steps):
            wy = y + i
            wx1 = x1 + i * run
            wx2 = min(cx - 1, wx1 + run - 1)
            ex2 = x2 - i * run
            ex1 = max(cx + 1, ex2 - run + 1)
            if wx1 <= wx2:
                add_fill(fills, f"{label} west slope {i}", (wx1, wy, z1), (wx2, wy, z2), stair("east"))
            if ex1 <= ex2:
                add_fill(fills, f"{label} east slope {i}", (ex1, wy, z1), (ex2, wy, z2), stair("west"))
            if i and i % 4 == 0:
                add_fill(fills, f"{label} west purlin {i}", (wx1, wy - 1, z1 + 2), (wx1, wy - 1, z2 - 2), "minecraft:dark_oak_log[axis=z]")
                add_fill(fills, f"{label} east purlin {i}", (ex2, wy - 1, z1 + 2), (ex2, wy - 1, z2 - 2), "minecraft:dark_oak_log[axis=z]")
        add_fill(fills, f"{label} west eave", (x1 - 2, y - 1, z1 - 3), (x1 + 2, y - 1, z2 + 3), slab)
        add_fill(fills, f"{label} east eave", (x2 - 2, y - 1, z1 - 3), (x2 + 2, y - 1, z2 + 3), slab)
        add_fill(fills, f"{label} ridge", (cx - 1, ridge_y, z1 + 4), (cx + 1, ridge_y + 1, z2 - 4), ridge_block)
        for rz in (z1 + 4, z2 - 4):
            add_fill(fills, f"{label} ridge finial {rz}", (cx - 2, ridge_y + 2, rz - 1), (cx + 2, ridge_y + 5, rz + 1), ridge_block)
    else:
        run = max(1, math.ceil((cz - z1) / steps))
        for i in range(steps):
            wy = y + i
            nz1 = z1 + i * run
            nz2 = min(cz - 1, nz1 + run - 1)
            sz2 = z2 - i * run
            sz1 = max(cz + 1, sz2 - run + 1)
            if nz1 <= nz2:
                add_fill(fills, f"{label} north slope {i}", (x1, wy, nz1), (x2, wy, nz2), stair("south"))
            if sz1 <= sz2:
                add_fill(fills, f"{label} south slope {i}", (x1, wy, sz1), (x2, wy, sz2), stair("north"))
            if i and i % 4 == 0:
                add_fill(fills, f"{label} north purlin {i}", (x1 + 2, wy - 1, nz1), (x2 - 2, wy - 1, nz1), "minecraft:dark_oak_log[axis=x]")
                add_fill(fills, f"{label} south purlin {i}", (x1 + 2, wy - 1, sz2), (x2 - 2, wy - 1, sz2), "minecraft:dark_oak_log[axis=x]")
        add_fill(fills, f"{label} north eave", (x1 - 3, y - 1, z1 - 2), (x2 + 3, y - 1, z1 + 2), slab)
        add_fill(fills, f"{label} south eave", (x1 - 3, y - 1, z2 - 2), (x2 + 3, y - 1, z2 + 2), slab)
        add_fill(fills, f"{label} ridge", (x1 + 4, ridge_y, cz - 1), (x2 - 4, ridge_y + 1, cz + 1), ridge_block)
        for rx in (x1 + 4, x2 - 4):
            add_fill(fills, f"{label} ridge finial {rx}", (rx - 1, ridge_y + 2, cz - 2), (rx + 1, ridge_y + 5, cz + 2), ridge_block)


def add_dougong_brackets(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y: int,
    spacing: int = 28,
    bracket_block: str = Materials.WOOD,
) -> None:
    """Add compact edge brackets instead of full beams through the building."""
    xs = list(range(x1, x2 + 1, spacing))
    zs = list(range(z1, z2 + 1, spacing))
    for x in xs:
        add_fill(fills, f"{label} dg north x{x}", (x - 2, y, z1 - 3), (x + 2, y + 2, z1 + 2), bracket_block)
        add_fill(fills, f"{label} dg south x{x}", (x - 2, y, z2 - 2), (x + 2, y + 2, z2 + 3), bracket_block)
    for z in zs:
        add_fill(fills, f"{label} dg west z{z}", (x1 - 3, y, z - 2), (x1 + 2, y + 2, z + 2), bracket_block)
        add_fill(fills, f"{label} dg east z{z}", (x2 - 2, y, z - 2), (x2 + 3, y + 2, z + 2), bracket_block)


def add_pagoda_eave(
    fills: list[Fill],
    label: str,
    cx: int,
    cz: int,
    radius: int,
    y: int,
    overhang: int = 3,
    roof_block: str = Materials.ROOF_GREEN,
) -> None:
    """Four directional stair eaves for one square pagoda tier."""
    variants = {
        Materials.ROOF_GREEN: ("minecraft:dark_prismarine_stairs", "minecraft:dark_prismarine_slab"),
        Materials.ROOF_BLUE: ("minecraft:prismarine_brick_stairs", "minecraft:prismarine_brick_slab"),
        Materials.ROOF_DARK: ("minecraft:deepslate_tile_stairs", "minecraft:deepslate_tile_slab"),
    }
    stair_id, slab_id = variants.get(roof_block, variants[Materials.ROOF_GREEN])
    outer = radius + overhang

    def stair(facing: str) -> str:
        return f"{stair_id}[facing={facing},half=bottom,shape=straight,waterlogged=false]"

    slab = f"{slab_id}[type=bottom,waterlogged=false]"
    add_fill(fills, f"{label} north", (cx - outer, y, cz - outer), (cx + outer, y, cz - radius), stair("south"))
    add_fill(fills, f"{label} south", (cx - outer, y, cz + radius), (cx + outer, y, cz + outer), stair("north"))
    add_fill(fills, f"{label} west", (cx - outer, y, cz - radius + 1), (cx - radius, y, cz + radius - 1), stair("east"))
    add_fill(fills, f"{label} east", (cx + radius, y, cz - radius + 1), (cx + outer, y, cz + radius - 1), stair("west"))
    add_outline(fills, f"{label} slab", cx - outer - 1, cz - outer - 1, cx + outer + 1, cz + outer + 1, y + 1, y + 1, slab, thickness=1)
    for dx, dz in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        x, z = cx + dx * (outer + 1), cz + dz * (outer + 1)
        add_fill(fills, f"{label} corner {dx},{dz}", (x, y + 1, z), (x, y + 3, z), Materials.GOLD_ACCENT)


def add_pagoda_openings(
    fills: list[Fill], label: str, cx: int, cz: int, radius: int, y: int, height: int
) -> None:
    """Carve framed openings through all four faces of a pagoda tier."""
    half_width = max(2, min(5, radius // 5))
    top = max(y + 2, y + height - 2)
    for z, suffix in ((cz - radius, "north"), (cz + radius, "south")):
        add_fill(fills, f"{label} {suffix} opening", (cx - half_width, y + 1, z - 1), (cx + half_width, top, z + 1), Materials.AIR)
        add_fill(fills, f"{label} {suffix} lintel", (cx - half_width - 1, top + 1, z), (cx + half_width + 1, top + 2, z), "minecraft:dark_oak_log[axis=x]")
    for x, suffix in ((cx - radius, "west"), (cx + radius, "east")):
        add_fill(fills, f"{label} {suffix} opening", (x - 1, y + 1, cz - half_width), (x + 1, top, cz + half_width), Materials.AIR)
        add_fill(fills, f"{label} {suffix} lintel", (x, top + 1, cz - half_width - 1), (x, top + 2, cz + half_width + 1), "minecraft:dark_oak_log[axis=z]")


_ROOF_VARIANTS = {
    Materials.ROOF_GREEN: ("minecraft:dark_prismarine_stairs", "minecraft:dark_prismarine_slab"),
    Materials.ROOF_BLUE: ("minecraft:prismarine_brick_stairs", "minecraft:prismarine_brick_slab"),
    Materials.ROOF_DARK: ("minecraft:deepslate_tile_stairs", "minecraft:deepslate_tile_slab"),
}


def add_hip_roof(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y: int,
    layers: int,
    ridge_axis: str = "z",
    roof_block: str = Materials.ROOF_GREEN,
    ridge_block: str = Materials.GOLD,
) -> None:
    """Add a hip roof (庑殿顶): four inward-rising stair slopes plus a ridge.

    Each layer steps one block inward on all four sides, so the corners form
    the diagonal hip lines naturally. `layers` should be about half the short
    axis. ridge_axis: 'z' = ridge runs north-south, 'x' = east-west.
    Stairs ascend toward the ridge, matching add_ridge_roof's convention.
    """
    if layers < 1:
        return
    stair_id, slab_id = _ROOF_VARIANTS.get(roof_block, _ROOF_VARIANTS[Materials.ROOF_GREEN])

    def stair(facing: str) -> str:
        return f"{stair_id}[facing={facing},half=bottom,shape=straight,waterlogged=false]"

    slab = f"{slab_id}[type=bottom,waterlogged=false]"
    top_y = y + layers
    # Clearing is deliberate: this pass replaces any previous roof volume.
    add_fill(fills, f"{label} clear old roof", (x1, y, z1), (x2, top_y + 6, z2), Materials.AIR)

    for i in range(layers):
        wy = y + i
        ix1, ix2 = x1 + i, x2 - i
        iz1, iz2 = z1 + i, z2 - i
        if ix1 > ix2 or iz1 > iz2:
            break
        add_fill(fills, f"{label} north slope {i}", (ix1, wy, iz1), (ix2, wy, iz1), stair("south"))
        add_fill(fills, f"{label} south slope {i}", (ix1, wy, iz2), (ix2, wy, iz2), stair("north"))
        if iz1 + 1 <= iz2 - 1:
            add_fill(fills, f"{label} west slope {i}", (ix1, wy, iz1 + 1), (ix1, wy, iz2 - 1), stair("east"))
            add_fill(fills, f"{label} east slope {i}", (ix2, wy, iz1 + 1), (ix2, wy, iz2 - 1), stair("west"))

    cx = (x1 + x2) // 2
    cz = (z1 + z2) // 2
    if ridge_axis == "z":
        add_fill(fills, f"{label} ridge", (cx - 1, top_y, z1 + layers), (cx + 1, top_y + 1, z2 - layers), ridge_block)
        for rz in (z1 + layers, z2 - layers):
            add_fill(fills, f"{label} ridge finial {rz}", (cx - 2, top_y + 2, rz - 1), (cx + 2, top_y + 5, rz + 1), ridge_block)
    else:
        add_fill(fills, f"{label} ridge", (x1 + layers, top_y, cz - 1), (x2 - layers, top_y + 1, cz + 1), ridge_block)
        for rx in (x1 + layers, x2 - layers):
            add_fill(fills, f"{label} ridge finial {rx}", (rx - 1, top_y + 2, cz - 2), (rx + 1, top_y + 5, cz + 2), ridge_block)

    # Overhanging eave slab ring and upturned corner accents.
    add_outline(fills, f"{label} eave slab", x1 - 2, z1 - 2, x2 + 2, z2 + 2, y - 1, y - 1, slab, thickness=2)
    for dx, dz in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        ex = x1 - 2 if dx < 0 else x2 + 2
        ez = z1 - 2 if dz < 0 else z2 + 2
        add_fill(fills, f"{label} upturned corner {dx},{dz}", (ex, y, ez), (ex, y + 2, ez), Materials.GOLD_ACCENT)


def add_pyramid_roof(
    fills: list[Fill],
    label: str,
    cx: int,
    cz: int,
    radius: int,
    y: int,
    roof_block: str = Materials.ROOF_GREEN,
    apex_block: str = Materials.GOLD,
) -> None:
    """Add a pyramidal pavilion roof (攒尖顶): four slopes meeting at an apex.

    Square footprint of half-width `radius` at eave level y, shrinking one
    block per layer until the slopes meet, then a small gilded finial.
    """
    if radius < 1:
        return
    stair_id, slab_id = _ROOF_VARIANTS.get(roof_block, _ROOF_VARIANTS[Materials.ROOF_GREEN])

    def stair(facing: str) -> str:
        return f"{stair_id}[facing={facing},half=bottom,shape=straight,waterlogged=false]"

    slab = f"{slab_id}[type=bottom,waterlogged=false]"
    for i in range(radius):
        wy = y + i
        r = radius - i
        add_fill(fills, f"{label} north slope {i}", (cx - r, wy, cz - r), (cx + r, wy, cz - r), stair("south"))
        add_fill(fills, f"{label} south slope {i}", (cx - r, wy, cz + r), (cx + r, wy, cz + r), stair("north"))
        if r > 1:
            add_fill(fills, f"{label} west slope {i}", (cx - r, wy, cz - r + 1), (cx - r, wy, cz + r - 1), stair("east"))
            add_fill(fills, f"{label} east slope {i}", (cx + r, wy, cz - r + 1), (cx + r, wy, cz + r - 1), stair("west"))
    add_fill(fills, f"{label} apex", (cx - 1, y + radius, cz - 1), (cx + 1, y + radius + 2, cz + 1), apex_block)

    add_outline(fills, f"{label} eave slab", cx - radius - 2, cz - radius - 2, cx + radius + 2, cz + radius + 2, y - 1, y - 1, slab, thickness=2)
    for dx, dz in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        ex = cx + dx * (radius + 2)
        ez = cz + dz * (radius + 2)
        add_fill(fills, f"{label} upturned corner {dx},{dz}", (ex, y, ez), (ex, y + 2, ez), Materials.GOLD_ACCENT)


def add_stair_run(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    start_y: int,
    steps: int,
    direction: str,
    block: str = Materials.SMOOTH,
) -> None:
    """Ramp/stair run projecting from a platform. direction: 'south' or 'north'."""
    for i in range(steps):
        if direction == "south":
            add_fill(fills, f"{label} step {i}", (x1 - i * 3, start_y + i, z1 - i * 6), (x2 + i * 3, start_y + i, z1 - i * 6 + 4), block)
        elif direction == "north":
            add_fill(fills, f"{label} step {i}", (x1 - i * 3, start_y + i, z2 + i * 6 - 4), (x2 + i * 3, start_y + i, z2 + i * 6), block)


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
            add_fill(fills, f"{label} post {z}", (x1 - 1, y, z - 1), (x1 + 1, y + 5, z + 1), Materials.LOG)
            add_fill(fills, f"{label} lamp {z}", (x1 - 1, y + 6, z - 1), (x1 + 1, y + 6, z + 1), Materials.SEA_LANTERN)
    elif z1 == z2:
        for x in range(min(x1, x2), max(x1, x2) + 1, every):
            add_fill(fills, f"{label} post {x}", (x - 1, y, z1 - 1), (x + 1, y + 5, z1 + 1), Materials.LOG)
            add_fill(fills, f"{label} lamp {x}", (x - 1, y + 6, z1 - 1), (x + 1, y + 6, z1 + 1), Materials.SEA_LANTERN)


def add_tree(fills: list[Fill], label: str, x: int, z: int, y: int, height: int = 7, spread: int = 2) -> None:
    """A simple cubic tree."""
    add_fill(fills, f"{label} trunk", (x, y, z), (x, y + height, z), Materials.TREE_LOG)
    add_fill(fills, f"{label} leaves", (x - spread, y + height - 1, z - spread), (x + spread, y + height + 2, z + spread), Materials.LEAVES)


def add_pool(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y: int,
    depth: int = 2,
    floor_block: str = Materials.SMOOTH,
) -> None:
    """Rectangular pool with water and a smooth floor."""
    add_fill(fills, f"{label} floor", (x1, y - depth, z1), (x2, y - 1, z2), floor_block)
    add_fill(fills, f"{label} water", (x1, y, z1), (x2, y, z2), Materials.WATER)


def add_pond_with_island(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y: int,
) -> None:
    """Pool with a small central island and a pavilion base."""
    add_pool(fills, label, x1, z1, x2, z2, y)
    cx, cz = (x1 + x2) // 2, (z1 + z2) // 2
    add_fill(fills, f"{label} island", (cx - 6, y, cz - 6), (cx + 6, y + 1, cz + 6), Materials.GRASS)
    add_fill(fills, f"{label} pavilion base", (cx - 3, y + 2, cz - 3), (cx + 3, y + 3, cz + 3), Materials.WHITE)


# ---------------------------------------------------------------------------
# 3D building primitives.
# ---------------------------------------------------------------------------
def add_staircase(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y1: int, y2: int,
    direction: str,
    block: str = Materials.SMOOTH,
) -> None:
    """Add a straight staircase between two points at different heights.

    direction: 'north' | 'south' | 'east' | 'west' - the upward travel direction.
    The staircase runs from (x1,z1) at y1 to (x2,z2) at y2.
    """
    if direction in ("north", "south"):
        width = abs(x2 - x1)
        steps = max(1, abs(z2 - z1))
        height = y2 - y1
        step_h = max(1, height // steps) if steps else 1
        for i in range(steps):
            z = min(z1, z2) + i if direction == "north" else max(z1, z2) - i
            y = y1 + (i * step_h)
            add_fill(fills, f"{label} step {i}", (min(x1, x2), y, z), (max(x1, x2), y, z), block)
    else:
        width = abs(z2 - z1)
        steps = max(1, abs(x2 - x1))
        height = y2 - y1
        step_h = max(1, height // steps) if steps else 1
        for i in range(steps):
            x = min(x1, x2) + i if direction == "east" else max(x1, x2) - i
            y = y1 + (i * step_h)
            add_fill(fills, f"{label} step {i}", (x, y, min(z1, z2)), (x, y, max(z1, z2)), block)


def add_spiral_stair(
    fills: list[Fill],
    label: str,
    cx: int, cz: int,
    radius: int,
    y1: int, y2: int,
    block: str = Materials.SMOOTH,
) -> None:
    """Add a square spiral staircase inside a tower.

    Four straight runs arranged around a square, climbing y1 -> y2.
    """
    total_rise = y2 - y1
    runs = 8
    rise_per_run = max(1, total_rise // runs)
    for i in range(runs):
        y = y1 + i * rise_per_run
        side = i % 4
        if side == 0:  # north side, climb east->west
            add_fill(fills, f"{label} spiral {i}", (cx - radius, y, cz - radius), (cx + radius, y, cz - radius), block)
        elif side == 1:  # west side, climb north->south
            add_fill(fills, f"{label} spiral {i}", (cx - radius, y, cz - radius), (cx - radius, y, cz + radius), block)
        elif side == 2:  # south side, climb west->east
            add_fill(fills, f"{label} spiral {i}", (cx - radius, y, cz + radius), (cx + radius, y, cz + radius), block)
        else:  # east side, climb south->north
            add_fill(fills, f"{label} spiral {i}", (cx + radius, y, cz - radius), (cx + radius, y, cz + radius), block)


def add_cantilevered_floor(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y: int,
    overhang: int,
    block: str = Materials.WOOD,
    support_block: str = Materials.LOG,
) -> None:
    """Add a floor slab that overhangs its supporting columns.

    The floor spans (x1,z1)-(x2,z2) at height y, with an extra overhang on all sides.
    Supports are placed at the inset corners and midpoints.
    """
    # Overhanging floor plate
    add_fill(
        fills, f"{label} slab",
        (x1 - overhang, y, z1 - overhang),
        (x2 + overhang, y, z2 + overhang),
        block,
    )
    # Corner supports
    for sx in (x1, x2):
        for sz in (z1, z2):
            add_fill(fills, f"{label} support {sx},{sz}", (sx, y - 1, sz), (sx, y - 1, sz), support_block)


def add_arch_bridge(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y: int,
    span: int,
    height: int,
    block: str = Materials.STONE,
) -> None:
    """Add a multi-arch stone bridge with deck, piers, and railings.

    The bridge runs from (x1,z1) to (x2,z2) at deck height y.
    span: approximate length of each arch bay.
    height: arch rise below the deck.
    """
    if x1 == x2:
        # Bridge runs north-south
        length = abs(z2 - z1)
        min_z, max_z = sorted((z1, z2))
        # Deck
        add_fill(fills, f"{label} deck", (x1 - 3, y, min_z), (x1 + 3, y, max_z), block)
        # Railings
        add_fill(fills, f"{label} rail w", (x1 - 4, y + 1, min_z), (x1 - 4, y + 2, max_z), block)
        add_fill(fills, f"{label} rail e", (x1 + 4, y + 1, min_z), (x1 + 4, y + 2, max_z), block)
        # Piers
        for z in range(min_z + span, max_z - span + 1, span * 2):
            add_fill(fills, f"{label} pier {z}", (x1 - 2, y - height, z - 2), (x1 + 2, y - 1, z + 2), block)
            # Arch void beneath (approximate with air pockets)
            add_fill(fills, f"{label} arch {z}", (x1 - 1, y - height + 1, z - 3), (x1 + 1, y - 1, z + 3), Materials.AIR)
    else:
        # Bridge runs east-west
        min_x, max_x = sorted((x1, x2))
        add_fill(fills, f"{label} deck", (min_x, y, z1 - 3), (max_x, y, z1 + 3), block)
        add_fill(fills, f"{label} rail n", (min_x, y + 1, z1 - 4), (max_x, y + 2, z1 - 4), block)
        add_fill(fills, f"{label} rail s", (min_x, y + 1, z1 + 4), (max_x, y + 2, z1 + 4), block)
        for x in range(min_x + span, max_x - span + 1, span * 2):
            add_fill(fills, f"{label} pier {x}", (x - 2, y - height, z1 - 2), (x + 2, y - 1, z1 + 2), block)
            add_fill(fills, f"{label} arch {x}", (x - 3, y - height + 1, z1 - 1), (x + 3, y - 1, z1 + 1), Materials.AIR)


def add_underground_room(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y_floor: int,
    y_ceiling: int,
    block: str = Materials.STONE,
) -> None:
    """Carve an underground room with floor, ceiling, and walls.

    The room interior is hollowed out between y_floor and y_ceiling.
    """
    # Clear interior
    add_fill(fills, f"{label} hollow", (x1 + 1, y_floor, z1 + 1), (x2 - 1, y_ceiling, z2 - 1), Materials.AIR)
    # Floor
    add_fill(fills, f"{label} floor", (x1, y_floor - 1, z1), (x2, y_floor - 1, z2), block)
    # Ceiling
    add_fill(fills, f"{label} ceiling", (x1, y_ceiling + 1, z1), (x2, y_ceiling + 1, z2), block)
    # Walls
    add_outline(fills, f"{label} walls", x1, z1, x2, z2, y_floor, y_ceiling, block, thickness=1)


def add_dougong_cluster(
    fills: list[Fill],
    label: str,
    x: int, z: int,
    y: int,
    tiers: int = 3,
    block: str = Materials.WOOD,
) -> None:
    """Add a compact multi-tier dougong bracket cluster.

    Each tier projects further outward, creating a stepped pyramid effect.
    """
    for t in range(tiers):
        size = 1 + t * 2
        add_fill(
            fills, f"{label} tier {t}",
            (x - size, y + t * 2, z - size),
            (x + size, y + t * 2 + 1, z + size),
            block,
        )


# ---------------------------------------------------------------------------
# Detail-enrichment primitives (overlay passes on existing buildings).
# ---------------------------------------------------------------------------
def add_roof_beasts(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y: int,
    ridge_axis: str = "z",
    count: int = 5,
) -> None:
    """Walking-beast statues along a main ridge (正脊走兽).

    Places `count` statues evenly between the ridge ends (4-block inset),
    alternating gold / gilded blackstone / white terracotta. Each statue
    is a dark base with a two-block body and a head, standing on `y`
    (callers pass the first free block above the ridge).
    """
    if count < 1:
        return
    cx, cz = (x1 + x2) // 2, (z1 + z2) // 2
    palettes = [Materials.GOLD, Materials.GOLD_ACCENT, Materials.WHITE_TERRACOTTA]
    spots = []
    if ridge_axis == "z":
        for i in range(count):
            z = z1 + 4 + int(i * max(1, (z2 - z1 - 8)) / max(1, count - 1))
            spots.append((cx, min(z, z2 - 4)))
    else:
        for i in range(count):
            x = x1 + 4 + int(i * max(1, (x2 - x1 - 8)) / max(1, count - 1))
            spots.append((min(x, x2 - 4), cz))
    for i, (x, z) in enumerate(spots):
        body = palettes[i % len(palettes)]
        add_fill(fills, f"{label} beast {i} base", (x, y, z), (x, y, z), Materials.DARK)
        add_fill(fills, f"{label} beast {i} body", (x, y + 1, z), (x, y + 2, z), body)
        add_fill(fills, f"{label} beast {i} head", (x, y + 3, z), (x, y + 3, z), body)


def add_eave_bells(
    fills: list[Fill],
    label: str,
    corners: list[tuple[int, int, int]],
) -> None:
    """Wind bells under eave corners (檐角风铃).

    `corners` lists (x, y, z) bell positions; each bell is a gold block
    with a two-block iron chain rising above it toward the eave.
    """
    for i, (x, y, z) in enumerate(corners):
        add_fill(fills, f"{label} bell {i}", (x, y, z), (x, y, z), Materials.GOLD)
        add_fill(fills, f"{label} chain {i}", (x, y + 1, z), (x, y + 2, z), Materials.IRON_BARS)


def add_balustrade(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y: int,
    post_block: str = Materials.RED_WALL,
    head_block: str = Materials.WHITE_TERRACOTTA,
    post_every: int = 6,
) -> None:
    """Balustrade with ornamental posts (望柱栏板).

    Fence rail along the rectangle outline at `y`, with posts every
    `post_every` blocks and at the four corners, each topped by a head
    block (lotus white / lion smooth).
    """
    add_outline(fills, f"{label} rail", x1, z1, x2, z2, y, y, Materials.FENCE, thickness=1)
    xs = sorted(set(list(range(x1, x2 + 1, post_every)) + [x1, x2]))
    zs = sorted(set(list(range(z1, z2 + 1, post_every)) + [z1, z2]))
    for x in xs:
        for z in (z1, z2):
            add_fill(fills, f"{label} post {x},{z}", (x, y + 1, z), (x, y + 1, z), post_block)
            add_fill(fills, f"{label} head {x},{z}", (x, y + 2, z), (x, y + 2, z), head_block)
    for z in zs:
        for x in (x1, x2):
            add_fill(fills, f"{label} post {x},{z}", (x, y + 1, z), (x, y + 1, z), post_block)
            add_fill(fills, f"{label} head {x},{z}", (x, y + 2, z), (x, y + 2, z), head_block)


def add_door_studs(
    fills: list[Fill],
    label: str,
    plane_axis: str,
    plane_pos: int,
    u1: int, u2: int,
    y1: int, y2: int,
    stud_block: str = Materials.GOLD,
    step: int = 2,
) -> None:
    """Door-stud array on a vertical wall/door face (门钉).

    plane_axis 'x': the face lies in the plane x=plane_pos (door faces
    east/west) and u runs along z; plane_axis 'z': face at z=plane_pos
    (door faces north/south) and u runs along x. Studs are single blocks
    spaced by `step` between (u1..u2, y1..y2).
    """
    for u in range(u1, u2 + 1, step):
        for y in range(y1, y2 + 1, step):
            if plane_axis == "x":
                add_fill(fills, f"{label} stud {u},{y}", (plane_pos, y, u), (plane_pos, y, u), stud_block)
            else:
                add_fill(fills, f"{label} stud {u},{y}", (u, y, plane_pos), (u, y, plane_pos), stud_block)


def add_pixel_mural(
    fills: list[Fill],
    label: str,
    art: list[str],
    palette: dict[str, str],
    x: int, y: int, z: int,
    axis: str = "x",
    flip: bool = False,
) -> None:
    """Pixel-art mural painted on a vertical plane (像素壁画).

    `art` is a list of equal-length strings, top row first; `palette`
    maps each character to a block id, '.' skips (leaves the wall behind).
    axis='x': the mural hangs in the plane z=z and runs along +x
    (left-to-right unless flip); axis='z': plane x=x running along +z.
    `y` is the top row's height.
    """
    width = max((len(row) for row in art), default=0)
    for r, row in enumerate(art):
        for c, ch in enumerate(row):
            block = palette.get(ch)
            if not block:
                continue
            yy = y - r
            if axis == "x":
                xx = x + (width - 1 - c if flip else c)
                add_fill(fills, f"{label} px {r},{c}", (xx, yy, z), (xx, yy, z), block)
            else:
                zz = z + (width - 1 - c if flip else c)
                add_fill(fills, f"{label} px {r},{c}", (x, yy, zz), (x, yy, zz), block)


# ---------------------------------------------------------------------------
# Execution helpers.
# ---------------------------------------------------------------------------
class _RconClient:
    def __init__(self, timeout: float) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(timeout)
        self.sock.connect((RCON_HOST, RCON_PORT))
        self.request_id = 100
        self._authenticate()

    @staticmethod
    def _packet(request_id: int, packet_type: int, body: str) -> bytes:
        payload = body.encode("utf-8") + b"\x00\x00"
        return struct.pack("<iii", 8 + len(payload), request_id, packet_type) + payload

    def _read(self) -> tuple[int, int, str]:
        raw_length = self._recv_exact(4)
        (length,) = struct.unpack("<i", raw_length)
        body = self._recv_exact(length)
        request_id, packet_type = struct.unpack("<ii", body[:8])
        return request_id, packet_type, body[8:-2].decode("utf-8", "replace")

    def _recv_exact(self, size: int) -> bytes:
        data = b""
        while len(data) < size:
            chunk = self.sock.recv(size - len(data))
            if not chunk:
                raise ConnectionError("RCON connection closed")
            data += chunk
        return data

    def _authenticate(self) -> None:
        self.sock.sendall(self._packet(1, 3, RCON_PASSWORD))
        while True:
            request_id, packet_type, _ = self._read()
            if packet_type == 2:
                if request_id == -1:
                    raise ConnectionError("RCON authentication failed")
                return

    def command(self, command: str) -> str:
        request_id = self.request_id
        self.request_id += 1
        self.sock.sendall(self._packet(request_id, 2, command))
        output = ""
        while True:
            response_id, packet_type, payload = self._read()
            if packet_type == 0:
                output += payload
            if response_id == request_id:
                return output

    def close(self) -> None:
        self.sock.close()


_rcon_client: _RconClient | None = None


def rcon(command: str, timeout: int = RCON_TIMEOUT) -> str:
    global _rcon_client
    for attempt in range(3):
        try:
            if _rcon_client is None:
                _rcon_client = _RconClient(float(timeout))
            return _rcon_client.command(command).strip()
        except (ConnectionError, OSError, socket.timeout):
            if _rcon_client is not None:
                _rcon_client.close()
                _rcon_client = None
            if attempt == 2:
                raise
            time.sleep(1)
    raise RuntimeError("unreachable")


def chunk_coords(x: int, z: int) -> tuple[int, int]:
    return x >> 4, z >> 4


def split_fill_by_load_region(fill: Fill) -> list[Fill]:
    """Clip one fill to bounded regions that the server can load smoothly."""
    min_x, max_x = sorted((fill.x1, fill.x2))
    min_y, max_y = sorted((fill.y1, fill.y2))
    min_z, max_z = sorted((fill.z1, fill.z2))
    pieces: list[Fill] = []
    for rx in range(min_x // LOAD_REGION_SIZE, max_x // LOAD_REGION_SIZE + 1):
        region_x1 = rx * LOAD_REGION_SIZE
        region_x2 = region_x1 + LOAD_REGION_SIZE - 1
        sx, ex = max(min_x, region_x1), min(max_x, region_x2)
        for rz in range(min_z // LOAD_REGION_SIZE, max_z // LOAD_REGION_SIZE + 1):
            region_z1 = rz * LOAD_REGION_SIZE
            region_z2 = region_z1 + LOAD_REGION_SIZE - 1
            sz, ez = max(min_z, region_z1), min(max_z, region_z2)
            pieces.append(Fill(fill.label, sx, min_y, sz, ex, max_y, ez, fill.block))
    return pieces


def group_fills_by_load_region(fills: list[Fill]) -> dict[tuple[int, int], list[Fill]]:
    groups: dict[tuple[int, int], list[Fill]] = defaultdict(list)
    for fill in fills:
        for piece in split_fill_by_load_region(fill):
            groups[(piece.x1 // LOAD_REGION_SIZE, piece.z1 // LOAD_REGION_SIZE)].append(piece)
    return dict(groups)


def validate_fills(fills: list[Fill]) -> dict[str, int]:
    oversized = 0
    invalid_height = 0
    for fill in fills:
        volume = (
            (abs(fill.x2 - fill.x1) + 1)
            * (abs(fill.y2 - fill.y1) + 1)
            * (abs(fill.z2 - fill.z1) + 1)
        )
        if volume > MAX_FILL_VOLUME:
            oversized += 1
        if min(fill.y1, fill.y2) < -64 or max(fill.y1, fill.y2) > 319:
            invalid_height += 1
    return {"oversized": oversized, "invalid_height": invalid_height}


def execute_fill(fill: Fill, timeout: int, use_forceload: bool) -> str:
    if not use_forceload:
        return rcon(
            f"fill {fill.x1} {fill.y1} {fill.z1} {fill.x2} {fill.y2} {fill.z2} {fill.block}",
            timeout,
        )

    pieces = split_fill_by_load_region(fill)
    outputs: list[str] = []
    for piece in pieces:
        min_x, max_x = sorted((piece.x1, piece.x2))
        min_z, max_z = sorted((piece.z1, piece.z2))
        rcon(f"forceload add {min_x} {min_z} {max_x} {max_z}", timeout)
        try:
            outputs.append(
                rcon(
                    f"fill {piece.x1} {piece.y1} {piece.z1} {piece.x2} {piece.y2} {piece.z2} {piece.block}",
                    timeout,
                )
            )
        finally:
            rcon(f"forceload remove {min_x} {min_z} {max_x} {max_z}", timeout)
    if len(outputs) == 1:
        return outputs[0]
    return f"{len(outputs)} loaded pieces; last: {outputs[-1] if outputs else ''}"


def run_builder(
    builder: Callable[[list[Fill]], None],
    section_name: str,
) -> None:
    """Common CLI harness used by every per-building script."""
    parser = argparse.ArgumentParser(description=f"Build {section_name} in Chang'an city.")
    parser.add_argument("--execute", action="store_true", help="Actually send commands to the server.")
    parser.add_argument("--start", type=int, default=0, help="0-based fill offset.")
    parser.add_argument("--limit", type=int, default=None, help="Only process N fills.")
    parser.add_argument("--delay-ms", type=int, default=60, help="Delay between /fill commands.")
    parser.add_argument("--report-every", type=int, default=100)
    parser.add_argument("--timeout", type=int, default=RCON_TIMEOUT)
    parser.add_argument("--no-forceload", action="store_true", help="Skip forceload (only if chunks already loaded).")
    args = parser.parse_args()

    if args.start < 0:
        parser.error("--start must be >= 0")
    if args.limit is not None and args.limit < 0:
        parser.error("--limit must be >= 0")
    if args.delay_ms < 0:
        parser.error("--delay-ms must be >= 0")
    if args.report_every <= 0:
        parser.error("--report-every must be > 0")

    fills: list[Fill] = []
    builder(fills)
    validation = validate_fills(fills)

    selected = fills[args.start :]
    if args.limit is not None:
        selected = selected[: args.limit]

    print(
        json.dumps(
            {
                "section": section_name,
                "total_fills": len(fills),
                "selected_fills": len(selected),
                "start": args.start,
                "execute": args.execute,
                "validation": validation,
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )

    if not args.execute:
        return
    if any(validation.values()):
        raise SystemExit("fill validation failed")

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
