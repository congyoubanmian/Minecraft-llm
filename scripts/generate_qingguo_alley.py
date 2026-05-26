from __future__ import annotations

from pathlib import Path

import mcschematic


OUT_DIR = Path("server/plugins/FastAsyncWorldEdit/schematics")
NAME = "qingguo_alley_historic_block"


class Builder:
    def __init__(self) -> None:
        self.schem = mcschematic.MCSchematic()
        self.blocks = 0

    def set(self, x: int, y: int, z: int, block: str) -> None:
        self.schem.setBlock((x, y, z), block)
        self.blocks += 1

    def fill(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, block: str) -> None:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.set(x, y, z, block)

    def save(self) -> Path:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        self.schem.save(str(OUT_DIR), NAME, mcschematic.Version.JE_1_20_1)
        return OUT_DIR / f"{NAME}.schem"


def mc(block: str) -> str:
    return block if block.startswith("minecraft:") else f"minecraft:{block}"


AIR = mc("air")
STONE = mc("stone_bricks")
MOSS = mc("mossy_stone_bricks")
PATH = mc("polished_andesite")
PATH_ALT = mc("cobblestone")
WALL = mc("white_concrete")
PLASTER = mc("smooth_quartz")
BLACK_TILE = mc("deepslate_tiles")
BLACK_SLAB = mc("deepslate_tile_slab[type=bottom,waterlogged=false]")
BLACK_TOP = mc("deepslate_tile_slab[type=top,waterlogged=false]")
DARK_WOOD = mc("dark_oak_planks")
LOG_Y = mc("dark_oak_log[axis=y]")
LOG_X = mc("dark_oak_log[axis=x]")
LOG_Z = mc("dark_oak_log[axis=z]")
WINDOW = mc("black_stained_glass_pane")
DOOR = mc("dark_oak_door")
RED = mc("red_terracotta")
GOLD = mc("gold_block")
WATER = mc("water[level=0]")
RAIL = mc("dark_oak_fence")
LANTERN = mc("lantern[hanging=true]")
GROUND = mc("grass_block")
LEAF = mc("azalea_leaves")
FLOWER = mc("flowering_azalea_leaves")
SPRUCE = mc("spruce_planks")
PODZOL = mc("podzol")


def stair(block: str, facing: str, half: str = "bottom") -> str:
    return mc(f"{block}[facing={facing},half={half},shape=straight,waterlogged=false]")


def base_terrain(b: Builder) -> None:
    b.fill(0, -1, 0, 132, -1, 64, GROUND)
    b.fill(0, 0, 0, 132, 0, 64, PATH_ALT)

    b.fill(0, 0, 4, 132, 0, 14, WATER)
    b.fill(0, -1, 3, 132, -1, 15, STONE)
    b.fill(0, 1, 3, 132, 1, 3, STONE)
    b.fill(0, 1, 15, 132, 1, 15, STONE)

    b.fill(0, 1, 17, 132, 1, 22, PATH)
    b.fill(0, 1, 39, 132, 1, 44, PATH)
    for x in range(0, 133, 4):
        b.set(x, 2, 16, RAIL)
        b.set(x, 2, 23, RAIL)
        b.set(x, 2, 38, RAIL)
        b.set(x, 2, 45, RAIL)

    for x in range(4, 129, 7):
        b.set(x, 2, 2, MOSS)
        b.set(x + 1, 2, 2, MOSS)
        b.set(x, 3, 2, LEAF if x % 14 else FLOWER)
        b.set(x + 1, 3, 2, LEAF)


def arched_bridge(b: Builder, x: int) -> None:
    b.fill(x - 7, 1, 12, x + 7, 1, 28, STONE)
    b.fill(x - 6, 2, 13, x + 6, 2, 27, STONE)
    b.fill(x - 5, 3, 14, x + 5, 3, 26, STONE)
    b.fill(x - 4, 4, 15, x + 4, 4, 25, STONE)
    b.fill(x - 3, 5, 16, x + 3, 5, 24, STONE)
    b.fill(x - 2, 6, 17, x + 2, 6, 23, STONE)

    for xx in range(x - 8, x + 9):
        b.set(xx, 3, 12, RAIL)
        b.set(xx, 3, 28, RAIL)
        if xx % 3 == 0:
            b.set(xx, 4, 12, LANTERN)
            b.set(xx, 4, 28, LANTERN)


def roof_gable_x(b: Builder, x1: int, x2: int, z1: int, z2: int, y: int) -> None:
    width = z2 - z1
    layers = width // 2 + 1
    for layer in range(layers):
        zl = z1 + layer
        zr = z2 - layer
        yy = y + layer
        b.fill(x1 - 1, yy, zl, x2 + 1, yy, zl, BLACK_TILE)
        b.fill(x1 - 1, yy, zr, x2 + 1, yy, zr, BLACK_TILE)
        b.fill(x1 + 1, yy, zl + 1, x2 - 1, yy, zr - 1, BLACK_TOP)

    b.fill(x1 - 2, y - 1, z1 - 1, x2 + 2, y - 1, z1, BLACK_SLAB)
    b.fill(x1 - 2, y - 1, z2, x2 + 2, y - 1, z2 + 1, BLACK_SLAB)
    b.fill(x1 - 2, y - 1, z1, x1 - 1, y - 1, z2, BLACK_SLAB)
    b.fill(x2 + 1, y - 1, z1, x2 + 2, y - 1, z2, BLACK_SLAB)


def window(b: Builder, x: int, z: int, y: int, face: str) -> None:
    if face in {"north", "south"}:
        b.fill(x - 1, y, z, x + 1, y + 1, z, WINDOW)
        b.fill(x - 2, y - 1, z, x + 2, y - 1, z, DARK_WOOD)
        b.fill(x - 2, y + 2, z, x + 2, y + 2, z, DARK_WOOD)
        b.fill(x - 2, y, z, x - 2, y + 1, z, DARK_WOOD)
        b.fill(x + 2, y, z, x + 2, y + 1, z, DARK_WOOD)
    else:
        b.fill(x, y, z - 1, x, y + 1, z + 1, WINDOW)
        b.fill(x, y - 1, z - 2, x, y - 1, z + 2, DARK_WOOD)
        b.fill(x, y + 2, z - 2, x, y + 2, z + 2, DARK_WOOD)
        b.fill(x, y, z - 2, x, y + 1, z - 2, DARK_WOOD)
        b.fill(x, y, z + 2, x, y + 1, z + 2, DARK_WOOD)


def house(b: Builder, x1: int, z1: int, width: int, depth: int, floors: int, courtyard: bool = False) -> None:
    x2 = x1 + width - 1
    z2 = z1 + depth - 1
    height = 5 + (floors - 1) * 4

    b.fill(x1, 1, z1, x2, 1, z2, STONE)
    b.fill(x1, 2, z1, x2, height, z2, WALL)
    b.fill(x1 + 1, 2, z1 + 1, x2 - 1, height, z2 - 1, AIR)

    for x in (x1, x2):
        for z in (z1, z2):
            b.fill(x, 2, z, x, height + 1, z, LOG_Y)
    b.fill(x1, 5, z1, x2, 5, z1, LOG_X)
    b.fill(x1, 5, z2, x2, 5, z2, LOG_X)
    b.fill(x1, 5, z1, x1, 5, z2, LOG_Z)
    b.fill(x2, 5, z1, x2, 5, z2, LOG_Z)
    if floors == 2:
        b.fill(x1, 9, z1, x2, 9, z1, LOG_X)
        b.fill(x1, 9, z2, x2, 9, z2, LOG_X)

    door_x = x1 + width // 2
    if z1 < 30:
        b.fill(door_x - 1, 2, z2, door_x, 4, z2, DOOR)
        for wx in range(x1 + 4, x2 - 2, 7):
            window(b, wx, z2, 3, "south")
            if floors == 2:
                window(b, wx, z2, 7, "south")
    else:
        b.fill(door_x - 1, 2, z1, door_x, 4, z1, DOOR)
        for wx in range(x1 + 4, x2 - 2, 7):
            window(b, wx, z1, 3, "north")
            if floors == 2:
                window(b, wx, z1, 7, "north")

    roof_gable_x(b, x1, x2, z1, z2, height + 1)

    if courtyard and width >= 18 and depth >= 14:
        b.fill(x1 + 5, 2, z1 + 5, x2 - 5, 5, z2 - 5, AIR)
        b.fill(x1 + 5, 1, z1 + 5, x2 - 5, 1, z2 - 5, PATH)
        b.fill(x1 + width // 2 - 1, 2, z1 + depth // 2 - 1, x1 + width // 2 + 1, 4, z1 + depth // 2 + 1, LEAF)


def paifang(b: Builder, x: int, z: int) -> None:
    for px in [x - 7, x - 3, x + 3, x + 7]:
        b.fill(px, 1, z, px + 1, 11, z + 1, STONE)
        b.fill(px, 2, z, px + 1, 8, z + 1, LOG_Y)
    b.fill(x - 10, 10, z, x + 10, 11, z + 1, DARK_WOOD)
    b.fill(x - 8, 12, z, x + 8, 13, z + 1, RED)
    b.fill(x - 5, 14, z, x + 5, 14, z + 1, GOLD)
    b.fill(x - 12, 15, z - 1, x + 12, 15, z + 2, BLACK_TILE)
    for xx in range(x - 13, x + 14):
        b.set(xx, 14, z - 2, stair("deepslate_tile_stairs", "north"))
        b.set(xx, 14, z + 3, stair("deepslate_tile_stairs", "south"))
    b.fill(x - 3, 9, z - 1, x + 3, 9, z + 2, GOLD)
    for px in [x - 9, x + 9]:
        b.set(px, 12, z - 1, LANTERN)
        b.set(px, 12, z + 2, LANTERN)


def dock_and_boats(b: Builder) -> None:
    for x in range(18, 120, 24):
        b.fill(x, 1, 15, x + 8, 1, 18, DARK_WOOD)
        for px in [x, x + 8]:
            b.fill(px, 1, 15, px, 3, 15, LOG_Y)
        b.fill(x + 2, 1, 7, x + 7, 1, 10, SPRUCE)
        b.fill(x + 3, 2, 8, x + 6, 2, 9, AIR)


def street_details(b: Builder) -> None:
    for x in range(10, 126, 12):
        b.set(x, 2, 24, LOG_Y)
        b.set(x, 3, 24, LOG_Y)
        b.set(x, 4, 24, LANTERN)
        b.set(x, 2, 37, LOG_Y)
        b.set(x, 3, 37, LOG_Y)
        b.set(x, 4, 37, LANTERN)

    for x in range(15, 120, 20):
        b.fill(x, 1, 26, x + 4, 1, 30, MOSS)
        b.fill(x + 1, 2, 27, x + 3, 3, 29, LEAF if x % 40 else FLOWER)
        b.fill(x, 1, 32, x + 3, 1, 35, PODZOL)
        b.fill(x + 1, 2, 33, x + 2, 4, 34, LEAF)


def build() -> tuple[Path, int]:
    b = Builder()
    base_terrain(b)
    paifang(b, 12, 30)
    paifang(b, 120, 30)
    arched_bridge(b, 52)
    arched_bridge(b, 98)
    dock_and_boats(b)

    x = 4
    specs = [
        (16, 12, 1, False),
        (20, 16, 2, True),
        (14, 11, 1, False),
        (24, 17, 2, True),
        (18, 12, 1, False),
        (22, 15, 2, True),
    ]
    for width, depth, floors, courtyard in specs:
        house(b, x, 24 - depth, width, depth, floors, courtyard)
        x += width + 3

    x = 6
    specs2 = [
        (18, 14, 2, True),
        (16, 11, 1, False),
        (23, 15, 2, True),
        (14, 12, 1, False),
        (21, 16, 2, True),
        (18, 13, 1, False),
    ]
    for width, depth, floors, courtyard in specs2:
        house(b, x, 37, width, depth, floors, courtyard)
        x += width + 3

    street_details(b)
    return b.save(), b.blocks


if __name__ == "__main__":
    path, blocks = build()
    print(path)
    print(f"blocks_written={blocks}")
