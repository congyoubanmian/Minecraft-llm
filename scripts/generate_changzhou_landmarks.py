from __future__ import annotations

from pathlib import Path

import mcschematic


OUT_DIR = Path("server/plugins/FastAsyncWorldEdit/schematics")


def mc(block: str) -> str:
    return block if block.startswith("minecraft:") else f"minecraft:{block}"


AIR = mc("air")
STONE = mc("stone_bricks")
MOSS = mc("mossy_stone_bricks")
ANDESITE = mc("polished_andesite")
QUARTZ = mc("smooth_quartz")
WHITE = mc("white_concrete")
YELLOW = mc("yellow_concrete")
RED = mc("red_terracotta")
GOLD = mc("gold_block")
BLACK = mc("deepslate_tiles")
BLACK_SLAB = mc("deepslate_tile_slab[type=bottom,waterlogged=false]")
BLACK_TOP = mc("deepslate_tile_slab[type=top,waterlogged=false]")
WOOD = mc("dark_oak_planks")
SPRUCE = mc("spruce_planks")
LOG_Y = mc("dark_oak_log[axis=y]")
LOG_X = mc("dark_oak_log[axis=x]")
LOG_Z = mc("dark_oak_log[axis=z]")
GLASS = mc("light_blue_stained_glass")
PANE = mc("black_stained_glass_pane")
WATER = mc("water[level=0]")
GRASS = mc("grass_block")
PATH = mc("stone_bricks")
DIRT = mc("coarse_dirt")
SAND = mc("sandstone")
TERRACOTTA = mc("orange_terracotta")
BONE = mc("bone_block")
COPPER = mc("oxidized_copper")
LANTERN = mc("lantern[hanging=true]")
FENCE = mc("dark_oak_fence")
LEAF = mc("azalea_leaves")
PINK = mc("pink_wool")
FLOWER = mc("flowering_azalea_leaves")
RED_WOOL = mc("red_wool")
WHITE_WOOL = mc("white_wool")
BLACK_CONCRETE = mc("black_concrete")
SEA_LANTERN = mc("sea_lantern")
STONE_WALL = mc("stone_brick_wall")
DEEPSLATE_WALL = mc("deepslate_tile_wall")
TRAPDOOR = mc("dark_oak_trapdoor[facing=north,half=bottom,open=false,waterlogged=false]")


def stair(block: str, facing: str, half: str = "bottom") -> str:
    return mc(f"{block}[facing={facing},half={half},shape=straight,waterlogged=false]")


class Build:
    def __init__(self, name: str) -> None:
        self.name = name
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
        self.schem.save(str(OUT_DIR), self.name, mcschematic.Version.JE_1_20_1)
        return OUT_DIR / f"{self.name}.schem"


def ground(b: Build, sx: int, sz: int, block: str = GRASS) -> None:
    b.fill(0, -1, 0, sx, -1, sz, block)
    b.fill(0, 0, 0, sx, 0, sz, mc("dirt_path"))


def circle(b: Build, cx: int, y: int, cz: int, r: int, block: str, hollow: bool = False) -> None:
    inner = max(0, r - 1)
    for x in range(cx - r, cx + r + 1):
        for z in range(cz - r, cz + r + 1):
            d = (x - cx) * (x - cx) + (z - cz) * (z - cz)
            if d <= r * r and (not hollow or d >= inner * inner):
                b.set(x, y, z, block)


def cylinder(b: Build, cx: int, y1: int, cz: int, r: int, h: int, block: str, hollow: bool = False) -> None:
    for y in range(y1, y1 + h):
        circle(b, cx, y, cz, r, block, hollow)


def roof_gable_x(b: Build, x1: int, x2: int, z1: int, z2: int, y: int, roof: str = BLACK) -> None:
    for layer in range((z2 - z1) // 2 + 1):
        zl = z1 + layer
        zr = z2 - layer
        yy = y + layer
        b.fill(x1 - 1, yy, zl, x2 + 1, yy, zl, roof)
        b.fill(x1 - 1, yy, zr, x2 + 1, yy, zr, roof)
        if zr - zl > 1:
            b.fill(x1 + 1, yy, zl + 1, x2 - 1, yy, zr - 1, BLACK_TOP)
    b.fill(x1 - 2, y - 1, z1 - 1, x2 + 2, y - 1, z1, BLACK_SLAB)
    b.fill(x1 - 2, y - 1, z2, x2 + 2, y - 1, z2 + 1, BLACK_SLAB)


def window_front(b: Build, x: int, y: int, z: int, w: int = 2, h: int = 2) -> None:
    b.fill(x, y, z, x + w - 1, y + h - 1, z, PANE)
    b.fill(x - 1, y - 1, z, x + w, y - 1, z, WOOD)
    b.fill(x - 1, y + h, z, x + w, y + h, z, WOOD)
    b.fill(x - 1, y, z, x - 1, y + h - 1, z, WOOD)
    b.fill(x + w, y, z, x + w, y + h - 1, z, WOOD)


def plum_tree(b: Build, x: int, z: int) -> None:
    b.fill(x, 1, z, x, 4, z, LOG_Y)
    for dx in range(-3, 4):
        for dz in range(-3, 4):
            if abs(dx) + abs(dz) <= 4:
                b.set(x + dx, 5 + (abs(dx) + abs(dz)) % 2, z + dz, PINK if (dx + dz) % 3 else FLOWER)


def lamp_post(b: Build, x: int, z: int, y: int = 1) -> None:
    b.fill(x, y, z, x, y + 3, z, DEEPSLATE_WALL)
    b.set(x, y + 4, z, LANTERN)


def flag(b: Build, x: int, z: int, y: int, color: str = RED_WOOL) -> None:
    b.fill(x, y, z, x, y + 6, z, LOG_Y)
    for yy in range(y + 4, y + 7):
        b.fill(x + 1, yy, z, x + 4, yy, z, color)
    b.set(x + 5, y + 5, z, GOLD)


def plaque(b: Build, x1: int, y: int, z: int, width: int, text_color: str = GOLD) -> None:
    b.fill(x1, y, z, x1 + width - 1, y + 1, z, text_color)
    for x in range(x1 + 1, x1 + width - 1, 3):
        b.set(x, y, z - 1, BLACK_CONCRETE)


def hongmei_wenbi() -> tuple[Path, int]:
    b = Build("hongmei_park_wenbi_tower")
    ground(b, 105, 88)
    b.fill(2, 0, 2, 103, 0, 86, mc("grass_block"))
    b.fill(6, 0, 48, 98, 0, 54, ANDESITE)
    b.fill(20, 0, 16, 78, 0, 36, WATER)
    for x in range(18, 81):
        b.set(x, 1, 15, STONE)
        b.set(x, 1, 37, STONE)
    for x in range(10, 95, 12):
        plum_tree(b, x, 64 + (x // 12) % 14)
    for x in range(12, 96, 14):
        lamp_post(b, x, 56)

    # Wenbi Tower, a slender 7-story brick/wood tower.
    cx, cz = 34, 38
    radii = [9, 8, 8, 7, 6, 5, 4]
    y = 1
    for idx, r in enumerate(radii):
        cylinder(b, cx, y, cz, r, 4, RED, hollow=True)
        cylinder(b, cx, y + 1, cz, max(2, r - 3), 1, AIR)
        for dx, dz in [(0, -r), (r, 0), (0, r), (-r, 0)]:
            b.fill(cx + dx, y, cz + dz, cx + dx, y + 4, cz + dz, LOG_Y)
        window_front(b, cx - 1, y + 2, cz - r, 3, 2)
        circle(b, cx, y + 4, cz, r + 2, BLACK_SLAB)
        circle(b, cx, y + 5, cz, r + 1, BLACK)
        if idx % 2 == 0:
            b.set(cx, y + 5, cz - r - 2, LANTERN)
        y += 6
    cylinder(b, cx, y, cz, 3, 3, GOLD)
    b.fill(cx, y + 3, cz, cx, y + 9, cz, mc("lightning_rod[facing=up,waterlogged=false]"))
    plaque(b, cx - 5, 8, cz - 11, 10)

    # Hongmei Pavilion: yellow walls, black tiles, small courtyard.
    b.fill(62, 1, 26, 93, 1, 58, STONE)
    b.fill(66, 2, 31, 89, 8, 53, YELLOW)
    b.fill(67, 2, 32, 88, 8, 52, AIR)
    for x in [66, 89]:
        for z in [31, 53]:
            b.fill(x, 2, z, x, 9, z, LOG_Y)
    for x in range(70, 86, 6):
        window_front(b, x, 4, 31, 3, 3)
    b.fill(75, 2, 31, 79, 5, 31, mc("dark_oak_door"))
    roof_gable_x(b, 64, 91, 29, 55, 9)
    b.fill(60, 1, 22, 95, 3, 24, YELLOW)
    b.fill(60, 1, 60, 95, 3, 62, YELLOW)
    b.fill(60, 1, 22, 62, 3, 62, YELLOW)
    b.fill(93, 1, 22, 95, 3, 62, YELLOW)
    b.fill(66, 4, 24, 89, 4, 24, RED)
    plaque(b, 73, 7, 30, 9)
    for x in [64, 91]:
        lamp_post(b, x, 27)
        lamp_post(b, x, 58)
    return b.save(), b.blocks


def dinosaur_park() -> tuple[Path, int]:
    b = Build("china_dinosaur_park_gate")
    ground(b, 130, 95, mc("coarse_dirt"))
    b.fill(0, 0, 0, 130, 0, 95, mc("green_concrete"))
    b.fill(8, 0, 43, 122, 0, 52, ANDESITE)
    b.fill(14, 1, 34, 116, 2, 62, STONE)

    # Biomorphic museum shell.
    for y in range(3, 18):
        inset = max(0, (y - 3) // 2)
        b.fill(24 + inset, y, 28 + inset, 106 - inset, y, 68 - inset, COPPER if y % 3 else GLASS)
    b.fill(30, 4, 27, 100, 15, 27, GLASS)
    b.fill(50, 3, 26, 80, 8, 26, AIR)
    for x in range(30, 104, 7):
        b.fill(x, 2, 26, x + 2, 16, 26, mc("black_concrete"))

    # Entrance arch teeth.
    b.fill(43, 2, 22, 87, 4, 28, STONE)
    for x in range(46, 86, 5):
        b.fill(x, 5, 24, x + 2, 8, 26, BONE)
        b.set(x + 1, 9, 25, stair("quartz_stairs", "south"))
    plaque(b, 52, 9, 21, 26, TERRACOTTA)

    # Dinosaur-head gate: skull silhouette around the entry.
    b.fill(42, 9, 18, 88, 16, 25, BONE)
    b.fill(50, 10, 17, 80, 14, 25, AIR)
    for x in range(47, 84, 6):
        b.fill(x, 8, 18, x + 2, 10, 20, BONE)
    b.fill(48, 13, 17, 55, 15, 17, BLACK_CONCRETE)
    b.fill(75, 13, 17, 82, 15, 17, BLACK_CONCRETE)

    # Dinosaur skeleton landmark.
    base_y = 5
    for x in range(22, 78):
        b.set(x, base_y + (x - 22) // 8 % 3, 78, BONE)
    for x in [30, 44, 58, 70]:
        b.fill(x, 1, 78, x, base_y + 5, 78, BONE)
        b.fill(x, 1, 82, x, base_y + 3, 82, BONE)
        b.fill(x, base_y + 2, 78, x, base_y + 2, 82, BONE)
    for x in range(80, 95):
        b.set(x, base_y + 7 + (x - 80) // 4, 78, BONE)
    circle(b, 99, base_y + 12, 78, 4, BONE)
    for x in range(12, 22):
        b.set(x, base_y + 3, 78 + (x - 12) // 3, BONE)
    for x in range(24, 76, 4):
        b.fill(x, base_y + 1, 76, x, base_y + 4, 76, BONE)
        b.fill(x, base_y + 1, 80, x, base_y + 4, 80, BONE)
    b.fill(92, base_y + 12, 74, 95, base_y + 14, 74, BONE)
    b.fill(92, base_y + 12, 82, 95, base_y + 14, 82, BONE)

    # Volcano/rock feature.
    for y in range(1, 14):
        r = max(2, 12 - y)
        circle(b, 112, y, 18, r, TERRACOTTA if y < 10 else RED)
    b.fill(109, 14, 15, 115, 16, 21, mc("lava[level=0]"))

    # Jungle planting.
    for x in range(10, 122, 14):
        for z in [12, 84]:
            b.fill(x, 1, z, x, 6, z, mc("jungle_log[axis=y]"))
            for dx in range(-3, 4):
                for dz in range(-3, 4):
                    if abs(dx) + abs(dz) <= 4:
                        b.set(x + dx, 7, z + dz, mc("jungle_leaves"))
    for x in range(16, 124, 18):
        lamp_post(b, x, 38)
        lamp_post(b, x, 57)
    return b.save(), b.blocks


def yancheng() -> tuple[Path, int]:
    b = Build("yancheng_spring_autumn_city")
    ground(b, 136, 116, mc("grass_block"))
    cx, cz = 68, 58
    # Three city walls and moats, simplified from the three-wall/three-river layout.
    for r, wall, water in [(54, 50, 47), (36, 33, 30), (20, 18, 15)]:
        for x in range(cx - r, cx + r + 1):
            for z in range(cz - r, cz + r + 1):
                dx, dz = abs(x - cx), abs(z - cz)
                d = max(dx, dz)
                if water <= d <= wall:
                    b.set(x, 0, z, WATER)
                if wall < d <= r:
                    b.set(x, 1, z, DIRT)
                    if d in {r - 1, r}:
                        b.set(x, 2, z, MOSS)

    # Main Spring-Autumn gate.
    b.fill(53, 1, 2, 83, 4, 10, STONE)
    b.fill(56, 5, 4, 80, 11, 9, RED)
    b.fill(63, 2, 1, 73, 8, 10, AIR)
    b.fill(49, 1, 6, 54, 13, 13, STONE)
    b.fill(82, 1, 6, 87, 13, 13, STONE)
    roof_gable_x(b, 47, 89, 2, 15, 14, BLACK)
    b.fill(58, 10, 1, 78, 10, 2, GOLD)
    plaque(b, 58, 12, 1, 20)
    for x in [46, 90]:
        flag(b, x, 4, 14)

    # Inner palace/watchtower.
    b.fill(47, 1, 45, 89, 2, 71, STONE)
    b.fill(52, 3, 49, 84, 13, 67, RED)
    b.fill(53, 3, 50, 83, 13, 66, AIR)
    for x in range(56, 82, 7):
        window_front(b, x, 6, 49, 3, 3)
    roof_gable_x(b, 49, 87, 46, 70, 14, BLACK)
    for x, z in [(42, 40), (94, 40), (42, 76), (94, 76)]:
        b.fill(x, 1, z, x + 4, 12, z + 4, STONE)
        roof_gable_x(b, x - 1, x + 5, z - 1, z + 5, 13, BLACK)
        flag(b, x + 2, z + 2, 14)

    # War chariots and wooden bridges.
    for x, z in [(28, 58), (108, 58), (68, 28), (68, 88)]:
        b.fill(x - 4, 1, z - 2, x + 4, 1, z + 2, WOOD)
        b.fill(x - 3, 2, z - 1, x + 3, 3, z + 1, RED)
        for wx, wz in [(x - 5, z - 3), (x + 5, z - 3), (x - 5, z + 3), (x + 5, z + 3)]:
            circle(b, wx, 1, wz, 2, BLACK, hollow=True)
    b.fill(62, 1, 0, 74, 1, 47, WOOD)
    b.fill(63, 2, 0, 73, 2, 47, SPRUCE)
    return b.save(), b.blocks


def grand_theatre() -> tuple[Path, int]:
    b = Build("changzhou_grand_theatre_culture_plaza")
    ground(b, 126, 88, mc("smooth_stone"))
    b.fill(4, 0, 4, 122, 0, 84, mc("smooth_stone"))
    b.fill(10, 0, 62, 116, 0, 76, WATER)
    for x in range(0, 127, 8):
        b.fill(x, 1, 40, x + 3, 1, 43, mc("sea_lantern"))

    # Curved theatre shell approximated with staggered white ribs.
    for i in range(18):
        x1 = 18 + i * 3
        height = 12 + min(i, 17 - i)
        b.fill(x1, 1, 20 + i // 3, x1 + 1, height, 62 - i // 3, QUARTZ)
        b.fill(x1 + 1, height, 22 + i // 3, x1 + 4, height + 1, 60 - i // 3, QUARTZ)
    b.fill(24, 2, 25, 100, 11, 57, GLASS)
    b.fill(28, 3, 24, 96, 8, 24, mc("black_stained_glass"))
    b.fill(46, 1, 16, 78, 3, 24, ANDESITE)
    plaque(b, 48, 5, 15, 28, SEA_LANTERN)

    # Culture plaza towers.
    for x, h in [(12, 20), (104, 18), (112, 23)]:
        b.fill(x, 1, 12, x + 7, h, 20, GLASS)
        for y in range(3, h, 4):
            b.fill(x, y, 11, x + 7, y, 11, mc("white_concrete"))
    # Light strips, reflection pools, and public-art rings.
    for z in [8, 80]:
        for x in range(8, 120, 8):
            b.fill(x, 1, z, x + 3, 1, z + 1, SEA_LANTERN)
    for cx, cz, r in [(30, 70, 7), (64, 70, 9), (98, 70, 7)]:
        circle(b, cx, 1, cz, r, mc("white_concrete"), hollow=True)
        circle(b, cx, 2, cz, max(2, r - 3), SEA_LANTERN, hollow=True)
    b.fill(18, 1, 64, 108, 1, 74, mc("light_blue_stained_glass"))
    return b.save(), b.blocks


def dongpo_park() -> tuple[Path, int]:
    b = Build("dongpo_park_ancient_ferry")
    ground(b, 116, 92, mc("grass_block"))
    b.fill(0, 0, 8, 116, 0, 26, WATER)
    b.fill(0, 0, 27, 116, 0, 31, ANDESITE)
    for x in range(6, 112, 8):
        b.set(x, 1, 27, FENCE)
        b.set(x, 1, 31, FENCE)

    # Ancient ferry dock and boat.
    b.fill(36, 1, 26, 72, 1, 40, WOOD)
    for x in [36, 44, 52, 60, 68, 72]:
        b.fill(x, 1, 25, x, 4, 25, LOG_Y)
    b.fill(46, 1, 12, 64, 1, 19, SPRUCE)
    b.fill(50, 2, 14, 60, 2, 17, AIR)
    b.fill(54, 2, 10, 56, 8, 10, mc("white_wool"))
    b.fill(44, 2, 11, 66, 3, 11, FENCE)

    # Dongpo-style pavilion and stele corridor.
    b.fill(42, 1, 48, 75, 1, 72, STONE)
    b.fill(48, 2, 54, 69, 8, 66, RED)
    b.fill(49, 2, 55, 68, 8, 65, AIR)
    for x in [48, 69]:
        for z in [54, 66]:
            b.fill(x, 2, z, x, 10, z, LOG_Y)
    roof_gable_x(b, 45, 72, 51, 69, 10, BLACK)
    plaque(b, 53, 8, 53, 12)
    b.fill(30, 1, 74, 88, 3, 78, STONE)
    for x in range(34, 86, 6):
        b.fill(x, 4, 75, x + 2, 8, 77, mc("chiseled_stone_bricks"))
        b.set(x + 1, 9, 76, GOLD if x % 12 == 0 else BLACK_CONCRETE)
    # Dongpo statue silhouette and poem wall.
    b.fill(20, 1, 52, 28, 1, 60, STONE)
    b.fill(24, 2, 56, 24, 8, 56, BLACK_CONCRETE)
    b.fill(22, 5, 55, 26, 6, 57, BLACK_CONCRETE)
    b.fill(23, 9, 56, 25, 11, 56, BLACK_CONCRETE)
    b.fill(12, 1, 74, 26, 5, 78, WHITE)
    for x in range(14, 25, 3):
        b.fill(x, 2, 73, x, 4, 73, BLACK_CONCRETE)
    for x in range(10, 108, 16):
        plum_tree(b, x, 54 + (x // 16) % 22)
        lamp_post(b, x, 34)
    return b.save(), b.blocks


GENERATORS = [
    hongmei_wenbi,
    dinosaur_park,
    yancheng,
    grand_theatre,
    dongpo_park,
]


if __name__ == "__main__":
    for gen in GENERATORS:
        path, blocks = gen()
        print(f"{path} blocks_written={blocks}")
