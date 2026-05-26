from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import mcschematic


OUT_DIR = Path("server/plugins/FastAsyncWorldEdit/schematics")
NAME = "tianning_pagoda_13_story"


@dataclass(frozen=True)
class Center:
    x: int = 48
    z: int = 48


class Pagoda:
    def __init__(self) -> None:
        self.schem = mcschematic.MCSchematic()
        self.center = Center()
        self.blocks = 0

    def set(self, x: int, y: int, z: int, block: str) -> None:
        self.schem.setBlock((x, y, z), block)
        self.blocks += 1

    def save(self) -> Path:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        self.schem.save(str(OUT_DIR), NAME, mcschematic.Version.JE_1_20_1)
        return OUT_DIR / f"{NAME}.schem"


def minecraft(block: str) -> str:
    return block if block.startswith("minecraft:") else f"minecraft:{block}"


STONE = minecraft("stone_bricks")
STONE_DARK = minecraft("deepslate_bricks")
TRIM = minecraft("polished_andesite")
WALL = minecraft("smooth_quartz")
WALL_ALT = minecraft("white_concrete")
WOOD = minecraft("dark_oak_planks")
WOOD_LOG_Y = minecraft("dark_oak_log[axis=y]")
WOOD_LOG_X = minecraft("dark_oak_log[axis=x]")
WOOD_LOG_Z = minecraft("dark_oak_log[axis=z]")
GOLD = minecraft("gold_block")
GLASS = minecraft("yellow_stained_glass_pane")
RED = minecraft("red_terracotta")
FENCE = minecraft("dark_oak_fence")
LANTERN = minecraft("lantern[hanging=true]")
SLAB = minecraft("dark_oak_slab[type=bottom,waterlogged=false]")
TOP_SLAB = minecraft("dark_oak_slab[type=top,waterlogged=false]")
STONE_SLAB = minecraft("stone_brick_slab[type=bottom,waterlogged=false]")
GOLD_SLAB = minecraft("cut_copper_slab[type=bottom,waterlogged=false]")


def stair(block: str, facing: str, half: str = "bottom") -> str:
    return minecraft(f"{block}[facing={facing},half={half},shape=straight,waterlogged=false]")


def oct_limit(radius: int) -> int:
    return radius + max(2, int(radius * 0.42))


def inside_octagon(dx: int, dz: int, radius: int) -> bool:
    return abs(dx) <= radius and abs(dz) <= radius and abs(dx) + abs(dz) <= oct_limit(radius)


def octagon_points(radius: int) -> list[tuple[int, int]]:
    cut = max(2, int(radius * 0.42))
    return [
        (-cut, -radius),
        (cut, -radius),
        (radius, -cut),
        (radius, cut),
        (cut, radius),
        (-cut, radius),
        (-radius, cut),
        (-radius, -cut),
    ]


def fill_octagon(p: Pagoda, y1: int, y2: int, radius: int, block: str, hollow: bool = False, thickness: int = 1) -> None:
    cx, cz = p.center.x, p.center.z
    inner = max(0, radius - thickness)
    for y in range(y1, y2 + 1):
        for x in range(cx - radius, cx + radius + 1):
            for z in range(cz - radius, cz + radius + 1):
                dx, dz = x - cx, z - cz
                if not inside_octagon(dx, dz, radius):
                    continue
                if hollow and inside_octagon(dx, dz, inner):
                    continue
                p.set(x, y, z, block)


def ring_octagon(p: Pagoda, y: int, outer: int, inner: int, block: str) -> None:
    cx, cz = p.center.x, p.center.z
    for x in range(cx - outer, cx + outer + 1):
        for z in range(cz - outer, cz + outer + 1):
            dx, dz = x - cx, z - cz
            if inside_octagon(dx, dz, outer) and not inside_octagon(dx, dz, inner):
                p.set(x, y, z, block)


def face_stair_for(dx: int, dz: int) -> str:
    if abs(dx) > abs(dz):
        return "east" if dx > 0 else "west"
    return "south" if dz > 0 else "north"


def eave(p: Pagoda, y: int, radius: int, tier: int) -> None:
    ring_octagon(p, y, radius + 4, max(1, radius - 1), SLAB)
    ring_octagon(p, y + 1, radius + 3, max(1, radius + 1), TOP_SLAB)
    ring_octagon(p, y + 2, radius + 2, max(1, radius), WOOD)

    cx, cz = p.center.x, p.center.z
    outer = radius + 5
    inner = radius + 3
    for x in range(cx - outer, cx + outer + 1):
        for z in range(cz - outer, cz + outer + 1):
            dx, dz = x - cx, z - cz
            if not inside_octagon(dx, dz, outer) or inside_octagon(dx, dz, inner):
                continue
            p.set(x, y, z, stair("dark_oak_stairs", face_stair_for(dx, dz)))

    for dx, dz in octagon_points(radius + 5):
        x, z = cx + dx, cz + dz
        p.set(x, y + 1, z, stair("dark_oak_stairs", face_stair_for(dx, dz), "top"))
        p.set(x, y + 2, z, GOLD if tier % 3 == 0 else WOOD)


def pillar(p: Pagoda, x: int, z: int, y1: int, y2: int) -> None:
    for y in range(y1, y2 + 1):
        p.set(x, y, z, WOOD_LOG_Y)
        p.set(x + 1, y, z, WOOD_LOG_Y)
        p.set(x, y, z + 1, WOOD_LOG_Y)
        p.set(x + 1, y, z + 1, WOOD_LOG_Y)


def windows_on_cardinal_faces(p: Pagoda, y: int, radius: int, tier: int) -> None:
    cx, cz = p.center.x, p.center.z
    window_y = [y + 2, y + 3]
    width = max(2, min(5, radius // 5))
    offsets = [-radius // 3, 0, radius // 3] if radius >= 16 else [-radius // 4, radius // 4]

    for offset in offsets:
        for yy in window_y:
            for w in range(-width // 2, width // 2 + 1):
                p.set(cx + offset + w, yy, cz - radius, GLASS)
                p.set(cx + offset + w, yy, cz + radius, GLASS)
                p.set(cx - radius, yy, cz + offset + w, GLASS)
                p.set(cx + radius, yy, cz + offset + w, GLASS)
        for w in range(-width // 2 - 1, width // 2 + 2):
            p.set(cx + offset + w, y + 1, cz - radius, WOOD)
            p.set(cx + offset + w, y + 4, cz - radius, WOOD)
            p.set(cx + offset + w, y + 1, cz + radius, WOOD)
            p.set(cx + offset + w, y + 4, cz + radius, WOOD)
            p.set(cx - radius, y + 1, cz + offset + w, WOOD)
            p.set(cx - radius, y + 4, cz + offset + w, WOOD)
            p.set(cx + radius, y + 1, cz + offset + w, WOOD)
            p.set(cx + radius, y + 4, cz + offset + w, WOOD)

    if tier % 2 == 0:
        for dx, dz in [(0, -radius - 1), (0, radius + 1), (-radius - 1, 0), (radius + 1, 0)]:
            p.set(cx + dx, y + 3, cz + dz, LANTERN)


def rail(p: Pagoda, y: int, radius: int) -> None:
    cx, cz = p.center.x, p.center.z
    r = radius + 2
    for x in range(cx - r, cx + r + 1):
        for z in range(cz - r, cz + r + 1):
            dx, dz = x - cx, z - cz
            if inside_octagon(dx, dz, r) and not inside_octagon(dx, dz, r - 1):
                if (x + z) % 3 == 0:
                    p.set(x, y, z, FENCE)


def tier(p: Pagoda, index: int, y: int, radius: int) -> None:
    wall = WALL if index % 2 == 0 else WALL_ALT
    fill_octagon(p, y, y, radius, WOOD)
    fill_octagon(p, y + 1, y + 5, radius, wall, hollow=True, thickness=2)
    fill_octagon(p, y + 1, y + 1, max(2, radius - 2), WOOD)
    ring_octagon(p, y + 5, radius, max(1, radius - 2), TRIM)

    cx, cz = p.center.x, p.center.z
    for dx, dz in octagon_points(radius):
        pillar(p, cx + dx, cz + dz, y + 1, y + 6)

    windows_on_cardinal_faces(p, y, radius, index)
    rail(p, y + 6, radius)
    eave(p, y + 6, radius, index)

    if index in {0, 4, 8, 12}:
        for dx, dz in [(0, -radius - 2), (0, radius + 2), (-radius - 2, 0), (radius + 2, 0)]:
            p.set(cx + dx, y + 6, cz + dz, GOLD)


def mini_pagoda(p: Pagoda, cx: int, cz: int) -> None:
    fill_center = Center(cx, cz)
    old = p.center
    p.center = fill_center
    fill_octagon(p, 2, 3, 3, STONE)
    fill_octagon(p, 4, 6, 2, WALL, hollow=True)
    ring_octagon(p, 7, 4, 1, SLAB)
    fill_octagon(p, 8, 9, 1, GOLD)
    p.center = old


def base(p: Pagoda) -> None:
    fill_octagon(p, 0, 2, 38, STONE)
    ring_octagon(p, 3, 39, 30, STONE_SLAB)
    fill_octagon(p, 4, 5, 31, TRIM)
    fill_octagon(p, 6, 6, 28, WOOD)

    cx, cz = p.center.x, p.center.z
    for step in range(5):
        z1 = cz - 45 + step * 2
        z2 = cz - 40 + step * 2
        for x in range(cx - 12 + step, cx + 13 - step):
            for z in range(z1, z2 + 1):
                p.set(x, step, z, STONE)

    for dx, dz in [(0, -34), (0, 34), (-34, 0), (34, 0), (-24, -24), (24, -24), (-24, 24), (24, 24)]:
        mini_pagoda(p, cx + dx, cz + dz)

    for x in range(cx - 7, cx + 8):
        for z in range(cz - 31, cz - 27):
            p.set(x, 7, z, RED)
    for x in range(cx - 4, cx + 5):
        p.set(x, 11, cz - 31, GOLD)


def spire(p: Pagoda, y: int) -> None:
    fill_octagon(p, y, y + 1, 8, GOLD)
    ring_octagon(p, y + 2, 10, 6, GOLD_SLAB)
    fill_octagon(p, y + 3, y + 5, 5, GOLD)
    fill_octagon(p, y + 6, y + 8, 3, GOLD)
    fill_octagon(p, y + 9, y + 13, 1, GOLD)
    cx, cz = p.center.x, p.center.z
    for yy in range(y + 14, y + 19):
        p.set(cx, yy, cz, minecraft("lightning_rod[facing=up,waterlogged=false]"))


def build() -> tuple[Path, int]:
    p = Pagoda()
    base(p)

    radii = [28, 27, 26, 25, 24, 22, 21, 20, 18, 17, 15, 14, 12]
    y = 7
    for index, radius in enumerate(radii):
        tier(p, index, y, radius)
        y += 8

    spire(p, y + 1)
    return p.save(), p.blocks


if __name__ == "__main__":
    path, blocks = build()
    print(path)
    print(f"blocks_written={blocks}")
