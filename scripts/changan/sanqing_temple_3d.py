from __future__ import annotations

import math
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
    add_outline,
    add_pool,
    add_ridge_roof,
    add_tree,
    run_builder,
)


"""
Sanqing Temple 3D (三清殿 · 大明宫道观) - the royal Daoist temple compound
in the north-west corner of Daming Palace, seat of Tang imperial Daoism.

Location in Chang'an city local coordinates:
    Site plate (Daming Palace NW corner): x 3700..4050, z 4250..4600.
    Hard constraints: the Daming Palace east wall runs at x 4200 and the
    jacheng double-wall gallery starts at (4200, 4700) heading east -
    nothing here may touch them; the palace great-hall groups all sit at
    x <= 3340, well clear of this plot. Natural ground is about y 0..4,
    so the plate is levelled at y 0..3 and buildings rise from y 4/5.
    Sanqing Hall (三清大殿): x 3780..3980, z 4400..4560 on two stone
    terraces, hall body y 7..17 under a double-eave hip roof.
    Bagua altar (八卦坛): open-air three-tier octagonal stone altar
    centred (3880, 4312), south of the hall across a turtle pond.

Distinctive features:
    - Dark Daoist "xuan" palette: deepslate walls and roofs with gold
      trim and crying-obsidian accents, unlike Buddhist red-wall temples
    - True scanline regular octagons (8 constant sides, not a stepped
      square); adjacent altar tiers are rotated 22.5 degrees so every
      facet staggers between tiers
    - Eight bagua trigrams inlaid in two-colour wool on the top tier
      (Later-Heaven arrangement) around a taiji centre boss
    - Bronze tripod censer: iron-bar legs, smooth-stone bowl, gold ears
      and a swaying three-segment white-wool smoke plume
    - Three quartz Daoist patriarch statues with gold crowns and halos
      on dark shrine platforms, each with its own offering table
    - Xuanwu (tortoise-and-snake) stone group on the pond island
    - Alchemy yard: barrel furnace with sea-lantern fire and an iron-bar
      cage, bookshelf medicine cabinets, hanging gourds on fence posts
    - Banner poles flanking the paifang gate, twin pine rows and a
      lantern avenue along the main axis
"""

# ---------------------------------------------------------------------------
# Constants.
# ---------------------------------------------------------------------------
DARK_WALL = M.DARK_BRICKS  # deepslate bricks - the Daoist "xuan" black
ROOF = M.ROOF_DARK  # deepslate tile roofs
XUAN = "minecraft:crying_obsidian"  # deepest purple-black accent
BARREL = "minecraft:barrel"
BOOKSHELF = "minecraft:bookshelf"
SNAKE = M.ANDESITE
DARK_SLAB = "minecraft:deepslate_tile_slab[type=bottom,waterlogged=false]"

# Site plate (Daming Palace NW corner) - never build outside these bounds.
SITE_X1, SITE_Z1 = 3700, 4250
SITE_X2, SITE_Z2 = 4050, 4600
AXIS = 3880  # main processional axis of the compound

# Sanqing main hall (x 3780..3980, z 4400..4560) on two stone terraces.
HALL_X1, HALL_Z1, HALL_X2, HALL_Z2 = 3780, 4400, 3980, 4560
TERR1_X1, TERR1_Z1, TERR1_X2, TERR1_Z2 = 3764, 4386, 3996, 4576
TERR2_X1, TERR2_Z1, TERR2_X2, TERR2_Z2 = 3774, 4396, 3986, 4566

# Bagua altar: three octagonal tiers, adjacent tiers rotated 22.5 degrees.
ALTAR_CX, ALTAR_CZ = 3880, 4312
TIER1_R, TIER2_R, TIER3_R = 36, 27, 19

# Turtle-and-snake pond between the altar and the hall.
POND_X1, POND_Z1, POND_X2, POND_Z2 = 3852, 4352, 3908, 4378

# West alchemy yard (丹房).
YARD_X1, YARD_Z1, YARD_X2, YARD_Z2 = 3702, 4404, 3762, 4474
ROOM_X1, ROOM_Z1, ROOM_X2, ROOM_Z2 = 3708, 4416, 3736, 4444

# South paifang gate and flanking banner poles.
GATE_X1, GATE_X2 = 3850, 3910
GATE_Z1, GATE_Z2 = 4253, 4261
POLE_XS = (3844, 3916)

# Later-Heaven bagua: (dx, dz, name, yao bits bottom line first, 1 = yang).
# In this project's convention south is -z, so Li (fire) sits at dz = -13.
TRIGRAM_LAYOUT = [
    (0, -13, "li", (1, 0, 1)),
    (-9, -9, "kun", (0, 0, 0)),
    (-13, 0, "dui", (1, 1, 0)),
    (-9, 9, "qian", (1, 1, 1)),
    (0, 13, "kan", (0, 1, 0)),
    (9, 9, "gen", (0, 0, 1)),
    (13, 0, "zhen", (1, 0, 0)),
    (9, -9, "xun", (0, 1, 1)),
]


# ---------------------------------------------------------------------------
# Local primitives.
# ---------------------------------------------------------------------------
def _octagon(
    fills: list[Fill],
    label: str,
    cx: int,
    cz: int,
    radius: int,
    rot_deg: float,
    y1: int,
    y2: int,
    block: str,
    step: int = 2,
) -> None:
    """Scanline-fill a regular octagon whose 8 sides stay true at any size.

    Vertices sit at rot_deg + k*45 degrees on the circle of `radius`;
    neighbouring tiers built with rot differing by 22.5 degrees stagger
    every facet, giving the classic alternating altar look.
    """
    verts = [
        (
            radius * math.cos(math.radians(rot_deg + k * 45)),
            radius * math.sin(math.radians(rot_deg + k * 45)),
        )
        for k in range(8)
    ]
    z_lo = int(math.floor(min(v[1] for v in verts)))
    z_hi = int(math.ceil(max(v[1] for v in verts)))
    for dz in range(z_lo, z_hi + 1, step):
        xs: list[float] = []
        for k in range(8):
            xa, za = verts[k]
            xb, zb = verts[(k + 1) % 8]
            if za > zb:
                xa, za, xb, zb = xb, zb, xa, za
            if za <= dz <= zb:
                if zb == za:
                    xs.extend((xa, xb))
                else:
                    t = (dz - za) / (zb - za)
                    xs.append(xa + t * (xb - xa))
        if not xs:
            continue
        x_lo = int(math.floor(min(xs)))
        x_hi = int(math.ceil(max(xs)))
        add_fill(
            fills,
            f"{label} row {dz}",
            (cx + x_lo, y1, cz + dz),
            (cx + x_hi, y2, cz + dz + step - 1),
            block,
        )


def _trigram(fills: list[Fill], label: str, tx: int, tz: int, bits: tuple[int, ...], y: int) -> None:
    """Flat three-yao trigram in two wool colours; bits run bottom to top.

    Yang yao is one solid yellow bar, yin yao is a split black pair.
    """
    for level, yang in enumerate(bits):
        z = tz + 2 - level * 2
        if yang:
            add_fill(fills, f"{label} yao{level} yang", (tx - 2, y, z), (tx + 2, y, z), M.YELLOW_WOOL)
        else:
            add_fill(fills, f"{label} yao{level} yin a", (tx - 2, y, z), (tx - 1, y, z), M.BLACK_WOOL)
            add_fill(fills, f"{label} yao{level} yin b", (tx + 1, y, z), (tx + 2, y, z), M.BLACK_WOOL)


def _dark_stair(facing: str) -> str:
    return f"minecraft:deepslate_tile_stairs[facing={facing},half=bottom,shape=straight,waterlogged=false]"


# ---------------------------------------------------------------------------
# Builder.
# ---------------------------------------------------------------------------
def build_sanqing_temple_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site levelling: stone plate y0..1, grass y2..3, dark axis avenue.
    # ------------------------------------------------------------------
    add_fill(fills, "sanqing site stone", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "sanqing site grass", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)
    add_fill(fills, "sanqing avenue", (AXIS - 14, 3, 4252), (AXIS + 14, 3, 4386), DARK_WALL)
    add_fill(fills, "sanqing avenue gold spine", (AXIS - 1, 3, 4252), (AXIS + 1, 3, 4386), M.GOLD)
    for zc in (4284, 4320, 4356):
        add_fill(fills, f"sanqing avenue obsidian {zc}", (AXIS - 1, 3, zc - 1), (AXIS + 1, 3, zc + 1), XUAN)
    add_fill(fills, "sanqing west lane", (3744, 3, 4340), (3756, 3, 4470), DARK_WALL)
    add_fill(fills, "sanqing hall court paving", (AXIS - 14, 3, 4378), (AXIS + 14, 3, 4386), M.SMOOTH)
    add_fill(fills, "sanqing pad s", (AXIS - 4, 3, 4268), (AXIS + 4, 3, 4273), XUAN)
    add_fill(fills, "sanqing pad e", (3916, 3, ALTAR_CZ - 4), (3920, 3, ALTAR_CZ + 4), XUAN)
    add_fill(fills, "sanqing pad w", (3840, 3, ALTAR_CZ - 4), (3844, 3, ALTAR_CZ + 4), XUAN)

    # ------------------------------------------------------------------
    # 2. West alchemy yard (丹房): walled court, furnace room, herb cabinets.
    # ------------------------------------------------------------------
    add_outline(fills, "sanqing yard wall", YARD_X1, YARD_Z1, YARD_X2, YARD_Z2, 4, 7, DARK_WALL, thickness=1)
    add_outline(fills, "sanqing yard wall cap", YARD_X1, YARD_Z1, YARD_X2, YARD_Z2, 8, 8, M.GOLD_ACCENT, thickness=1)
    add_fill(fills, "sanqing yard gate", (3746, 4, YARD_Z1), (3752, 7, YARD_Z1), M.AIR)
    add_hollow_box(fills, "sanqing alchemy room", ROOM_X1, 4, ROOM_Z1, ROOM_X2, 10, ROOM_Z2, DARK_WALL, thickness=1)
    add_fill(fills, "sanqing alchemy floor", (ROOM_X1 + 1, 4, ROOM_Z1 + 1), (ROOM_X2 - 1, 4, ROOM_Z2 - 1), M.SMOOTH)
    add_fill(fills, "sanqing alchemy door", (ROOM_X2, 5, 4426), (ROOM_X2, 7, 4430), M.AIR)
    add_fill(fills, "sanqing alchemy window w", (3712, 6, ROOM_Z1), (3720, 8, ROOM_Z1), M.GLASS)
    add_fill(fills, "sanqing alchemy window e", (3724, 6, ROOM_Z1), (3732, 8, ROOM_Z1), M.GLASS)
    add_ridge_roof(
        fills, "sanqing alchemy roof",
        ROOM_X1 - 2, ROOM_Z1 - 2, ROOM_X2 + 2, ROOM_Z2 + 2,
        11, layers=2, ridge_axis="x", roof_block=ROOF, ridge_block=M.GOLD,
    )
    # Elixir furnace: dark plinth, barrel pot, sea-lantern fire, iron cage.
    fx, fz = 3723, 4437
    add_fill(fills, "sanqing furnace plinth", (fx - 1, 5, fz - 1), (fx + 1, 5, fz + 1), DARK_WALL)
    add_fill(fills, "sanqing furnace pot", (fx, 6, fz), (fx, 6, fz), BARREL)
    add_fill(fills, "sanqing furnace fire", (fx, 7, fz), (fx, 7, fz), M.SEA_LANTERN)
    add_fill(fills, "sanqing furnace cage", (fx - 1, 6, fz - 1), (fx + 1, 6, fz + 1), M.IRON_BARS)
    # Medicine cabinets along the back wall.
    add_fill(fills, "sanqing medicine cabinet", (3712, 5, ROOM_Z2 - 1), (3722, 6, ROOM_Z2 - 1), BOOKSHELF)
    # Hanging gourds under the north eave.
    for i, gx in enumerate((3712, 3720, 3728)):
        add_fill(fills, f"sanqing gourd string {i}", (gx, 8, ROOM_Z1 - 3), (gx, 9, ROOM_Z1 - 3), M.FENCE)
        add_fill(fills, f"sanqing gourd {i}", (gx, 7, ROOM_Z1 - 3), (gx, 7, ROOM_Z1 - 3), M.LEAVES)

    # ------------------------------------------------------------------
    # 3. Xuanwu pond (龟蛇池): water, island, tortoise shell and snake coil.
    # ------------------------------------------------------------------
    add_pool(fills, "sanqing turtle pond", POND_X1, POND_Z1, POND_X2, POND_Z2, 3, depth=1, floor_block=M.SMOOTH)
    add_outline(fills, "sanqing pond rim", POND_X1 - 2, POND_Z1 - 2, POND_X2 + 2, POND_Z2 + 2, 3, 4, DARK_WALL, thickness=1)
    add_fill(fills, "sanqing turtle island", (3870, 3, 4354), (3890, 3, 4374), M.SMOOTH)
    add_fill(fills, "sanqing turtle island top", (3872, 4, 4356), (3888, 4, 4372), M.SMOOTH)
    # True octagonal shell (8 constant sides).
    _octagon(fills, "sanqing turtle shell", 3880, 4365, 6, 0, 5, 5, M.SMOOTH, step=2)
    add_fill(fills, "sanqing shell boss", (3879, 6, 4364), (3881, 6, 4366), M.MOSS_STONE)
    add_fill(fills, "sanqing turtle head", (3879, 5, 4357), (3880, 6, 4358), M.SMOOTH)
    add_fill(fills, "sanqing turtle tail", (3880, 5, 4372), (3880, 5, 4373), M.SMOOTH)
    for i, (lx, lz) in enumerate(((3873, 4362), (3873, 4367), (3887, 4362), (3887, 4367))):
        add_fill(fills, f"sanqing turtle leg {i}", (lx, 5, lz), (lx, 5, lz + 1), M.SMOOTH)
    # Snake coiling around the shell and rearing toward the altar.
    snake_path = [
        (3872, 4361, 5), (3871, 4365, 5), (3872, 4369, 5), (3875, 4372, 5),
        (3879, 4373, 5), (3883, 4373, 5), (3886, 4371, 5), (3889, 4368, 6),
        (3889, 4364, 6), (3887, 4360, 6), (3886, 4358, 7), (3884, 4357, 7),
    ]
    for i, (sx, sz, sy) in enumerate(snake_path):
        add_fill(fills, f"sanqing snake body {i}", (sx, sy, sz), (sx, sy, sz), SNAKE)
    add_fill(fills, "sanqing snake head", (3883, 7, 4356), (3883, 8, 4356), SNAKE)

    # ------------------------------------------------------------------
    # 4. Bagua altar (八卦坛): three scanline octagon tiers, 22.5-degree
    #    stagger, wool trigrams, taiji boss, four cardinal stair aprons.
    # ------------------------------------------------------------------
    _octagon(fills, "sanqing bagua tier1", ALTAR_CX, ALTAR_CZ, TIER1_R, 22.5, 4, 4, DARK_WALL, step=3)
    _octagon(fills, "sanqing bagua tier2", ALTAR_CX, ALTAR_CZ, TIER2_R, 0, 4, 5, M.ANDESITE, step=2)
    _octagon(fills, "sanqing bagua tier3", ALTAR_CX, ALTAR_CZ, TIER3_R, 22.5, 4, 6, M.SMOOTH, step=2)
    # Gilded posts on the eight tier-1 vertices.
    for k in range(8):
        ang = math.radians(22.5 + k * 45)
        px = ALTAR_CX + int(round(TIER1_R * math.cos(ang)))
        pz = ALTAR_CZ + int(round(TIER1_R * math.sin(ang)))
        add_fill(fills, f"sanqing altar post {k}", (px, 5, pz), (px, 6, pz), M.GOLD_ACCENT)
    # Taiji boss: two-colour disk with gold / obsidian eyes.
    for dz in range(-3, 4):
        half = int((9 - dz * dz) ** 0.5)
        block = M.WHITE_WOOL if dz <= 0 else M.BLACK_WOOL
        add_fill(fills, f"sanqing taiji row {dz}", (ALTAR_CX - half, 7, ALTAR_CZ + dz), (ALTAR_CX + half, 7, ALTAR_CZ + dz), block)
    add_fill(fills, "sanqing taiji eye a", (ALTAR_CX - 1, 7, ALTAR_CZ - 1), (ALTAR_CX - 1, 7, ALTAR_CZ - 1), M.GOLD)
    add_fill(fills, "sanqing taiji eye b", (ALTAR_CX + 1, 7, ALTAR_CZ + 1), (ALTAR_CX + 1, 7, ALTAR_CZ + 1), XUAN)
    # Eight trigrams in the eight directions on the top tier.
    for dx, dz, name, bits in TRIGRAM_LAYOUT:
        _trigram(fills, f"sanqing trigram {name}", ALTAR_CX + dx, ALTAR_CZ + dz, bits, 7)
    # Four cardinal stair aprons: y5 step onto tier2, y6 step onto tier3.
    add_fill(fills, "sanqing altar stair s lower", (AXIS - 3, 5, 4282), (AXIS + 3, 5, 4284), M.SMOOTH)
    add_fill(fills, "sanqing altar stair s upper", (AXIS - 3, 6, 4291), (AXIS + 3, 6, 4293), M.SMOOTH)
    add_fill(fills, "sanqing altar stair n lower", (AXIS - 3, 5, 4340), (AXIS + 3, 5, 4342), M.SMOOTH)
    add_fill(fills, "sanqing altar stair n upper", (AXIS - 3, 6, 4331), (AXIS + 3, 6, 4333), M.SMOOTH)
    add_fill(fills, "sanqing altar stair e lower", (3908, 5, ALTAR_CZ - 3), (3910, 5, ALTAR_CZ + 3), M.SMOOTH)
    add_fill(fills, "sanqing altar stair e upper", (3899, 6, ALTAR_CZ - 3), (3901, 6, ALTAR_CZ + 3), M.SMOOTH)
    add_fill(fills, "sanqing altar stair w lower", (3850, 5, ALTAR_CZ - 3), (3852, 5, ALTAR_CZ + 3), M.SMOOTH)
    add_fill(fills, "sanqing altar stair w upper", (3859, 6, ALTAR_CZ - 3), (3861, 6, ALTAR_CZ + 3), M.SMOOTH)

    # ------------------------------------------------------------------
    # 5. Bronze incense censer (焚香大炉): tripod ding east of the altar.
    # ------------------------------------------------------------------
    add_fill(fills, "sanqing censer plinth", (3938, 4, 4305), (3952, 4, 4319), DARK_WALL)
    for i, (lx, lz) in enumerate(((3941, 4308), (3941, 4316), (3949, 4312))):
        add_fill(fills, f"sanqing censer leg {i}", (lx, 5, lz), (lx, 8, lz), M.IRON_BARS)
    _octagon(fills, "sanqing censer body", 3945, 4312, 4, 22.5, 9, 12, M.SMOOTH, step=2)
    add_fill(fills, "sanqing censer coal", (3944, 12, 4311), (3945, 12, 4312), M.SEA_LANTERN)
    add_fill(fills, "sanqing censer ear n", (3945, 13, 4308), (3945, 14, 4308), M.GOLD)
    add_fill(fills, "sanqing censer ear s", (3945, 13, 4316), (3945, 14, 4316), M.GOLD)
    # Three-segment smoke plume swaying as it rises.
    add_fill(fills, "sanqing censer smoke 1", (3945, 13, 4312), (3945, 15, 4312), M.WHITE_WOOL)
    add_fill(fills, "sanqing censer smoke 2", (3946, 16, 4312), (3946, 18, 4312), M.WHITE_WOOL)
    add_fill(fills, "sanqing censer smoke 3", (3946, 19, 4313), (3946, 21, 4313), M.WHITE_WOOL)

    # ------------------------------------------------------------------
    # 6. Sanqing Hall (三清大殿): two terraces, dark hall y7..17, shrines,
    #    lower double eave ring, upper body, great hip roof.
    # ------------------------------------------------------------------
    add_fill(fills, "sanqing hall terrace1", (TERR1_X1, 4, TERR1_Z1), (TERR1_X2, 5, TERR1_Z2), M.STONE)
    add_fill(fills, "sanqing hall terrace2", (TERR2_X1, 6, TERR2_Z1), (TERR2_X2, 6, TERR2_Z2), M.SMOOTH)
    add_fill(fills, "sanqing hall stair s a", (AXIS - 8, 5, 4382), (AXIS + 8, 5, 4385), M.SMOOTH)
    add_fill(fills, "sanqing hall stair s b", (AXIS - 8, 4, 4379), (AXIS + 8, 4, 4379 + 2), M.SMOOTH)
    add_fill(fills, "sanqing hall stair e a", (3997, 5, 4470), (4000, 5, 4486), M.SMOOTH)
    add_fill(fills, "sanqing hall stair e b", (4001, 4, 4470), (4004, 4, 4486), M.SMOOTH)

    # Hall body: dark walls, interior, floor, ceiling, gold frieze.
    add_outline(fills, "sanqing hall wall", HALL_X1, HALL_Z1, HALL_X2, HALL_Z2, 7, 17, DARK_WALL, thickness=1)
    add_fill(fills, "sanqing hall air", (HALL_X1 + 1, 8, HALL_Z1 + 1), (HALL_X2 - 1, 17, HALL_Z2 - 1), M.AIR)
    add_fill(fills, "sanqing hall floor", (HALL_X1 + 1, 7, HALL_Z1 + 1), (HALL_X2 - 1, 7, HALL_Z2 - 1), M.ANDESITE)
    add_fill(fills, "sanqing hall ceiling", (HALL_X1, 18, HALL_Z1), (HALL_X2, 18, HALL_Z2), M.WOOD)
    add_fill(fills, "sanqing hall door s", (AXIS - 14, 8, HALL_Z1), (AXIS + 14, 12, HALL_Z1), M.AIR)
    add_fill(fills, "sanqing hall door frame w", (AXIS - 15, 8, HALL_Z1), (AXIS - 15, 12, HALL_Z1), M.GOLD_ACCENT)
    add_fill(fills, "sanqing hall door frame e", (AXIS + 15, 8, HALL_Z1), (AXIS + 15, 12, HALL_Z1), M.GOLD_ACCENT)
    add_fill(fills, "sanqing hall door lintel", (AXIS - 15, 13, HALL_Z1), (AXIS + 15, 13, HALL_Z1), M.GOLD)
    add_fill(fills, "sanqing hall door n", (AXIS - 10, 8, HALL_Z2), (AXIS + 10, 12, HALL_Z2), M.AIR)
    add_fill(fills, "sanqing hall window s w", (3810, 10, HALL_Z1), (3840, 13, HALL_Z1), M.GLASS)
    add_fill(fills, "sanqing hall window s e", (3920, 10, HALL_Z1), (3950, 13, HALL_Z1), M.GLASS)
    add_fill(fills, "sanqing hall window n w", (3810, 10, HALL_Z2), (3840, 13, HALL_Z2), M.GLASS)
    add_fill(fills, "sanqing hall window n e", (3920, 10, HALL_Z2), (3950, 13, HALL_Z2), M.GLASS)
    add_fill(fills, "sanqing hall window w", (HALL_X1, 10, 4420), (HALL_X1, 13, 4455), M.GLASS)
    add_fill(fills, "sanqing hall window e", (HALL_X2, 10, 4505), (HALL_X2, 13, 4540), M.GLASS)
    add_outline(fills, "sanqing hall frieze", HALL_X1, HALL_Z1, HALL_X2, HALL_Z2, 16, 17, M.GOLD_ACCENT, thickness=1)
    for cx in (3788, 3834, 3926, 3972):
        add_fill(fills, f"sanqing hall col s {cx}", (cx, 7, HALL_Z1), (cx + 1, 15, HALL_Z1 + 1), M.LOG)
        add_fill(fills, f"sanqing hall col n {cx}", (cx, 7, HALL_Z2 - 1), (cx + 1, 15, HALL_Z2), M.LOG)
    for cz in (4412, 4480, 4548):
        add_fill(fills, f"sanqing hall col w {cz}", (HALL_X1, 7, cz), (HALL_X1 + 1, 15, cz + 1), M.LOG)
        add_fill(fills, f"sanqing hall col e {cz}", (HALL_X2 - 1, 7, cz), (HALL_X2, 15, cz + 1), M.LOG)

    # Three Daoist patriarch shrines (三清) facing the south door.
    for i, sx in enumerate((3830, 3880, 3930)):
        add_fill(fills, f"sanqing shrine platform {i}", (sx - 5, 8, 4537), (sx + 5, 9, 4555), DARK_WALL)
        add_fill(fills, f"sanqing shrine step {i}", (sx - 2, 8, 4534), (sx + 2, 8, 4536), DARK_WALL)
        add_fill(fills, f"sanqing patriarch robe {i}", (sx - 2, 10, 4542), (sx + 2, 10, 4551), M.QUARTZ)
        add_fill(fills, f"sanqing patriarch torso {i}", (sx - 1, 11, 4544), (sx + 1, 13, 4550), M.QUARTZ)
        add_fill(fills, f"sanqing patriarch arm w {i}", (sx - 2, 11, 4545), (sx - 2, 12, 4549), M.QUARTZ)
        add_fill(fills, f"sanqing patriarch arm e {i}", (sx + 2, 11, 4545), (sx + 2, 12, 4549), M.QUARTZ)
        add_fill(fills, f"sanqing patriarch head {i}", (sx - 1, 14, 4546), (sx + 1, 15, 4548), M.QUARTZ)
        add_fill(fills, f"sanqing patriarch crown {i}", (sx - 1, 16, 4546), (sx + 1, 17, 4548), M.GOLD)
        add_fill(fills, f"sanqing patriarch halo {i}", (sx - 2, 13, 4551), (sx + 2, 16, 4551), M.GOLD_ACCENT)
        add_fill(fills, f"sanqing patriarch tablet {i}", (sx, 11, 4543), (sx, 11, 4543), M.GOLD)
        add_fill(fills, f"sanqing offering top {i}", (sx - 3, 9, 4528), (sx + 3, 9, 4530), M.WOOD)
        add_fill(fills, f"sanqing offering leg w {i}", (sx - 3, 8, 4528), (sx - 3, 8, 4528), M.LOG)
        add_fill(fills, f"sanqing offering leg e {i}", (sx + 3, 8, 4530), (sx + 3, 8, 4530), M.LOG)
        add_fill(fills, f"sanqing offering gifts {i}", (sx - 1, 10, 4529), (sx + 1, 10, 4529), M.GOLD)

    # Lower double-eave ring (重檐下檐): four stair bands, slab ring, corners.
    add_fill(fills, "sanqing eave band n", (3770, 18, 4392), (3990, 18, 4399), _dark_stair("south"))
    add_fill(fills, "sanqing eave band s", (3770, 18, 4563), (3990, 18, 4570), _dark_stair("north"))
    add_fill(fills, "sanqing eave band w", (3770, 18, 4400), (3777, 18, 4562), _dark_stair("east"))
    add_fill(fills, "sanqing eave band e", (3983, 18, 4400), (3990, 18, 4562), _dark_stair("west"))
    add_outline(fills, "sanqing eave slab", 3768, 4390, 3992, 4572, 17, 17, DARK_SLAB, thickness=2)
    for i, (kx, kz) in enumerate(((3768, 4390), (3992, 4390), (3768, 4572), (3992, 4572))):
        add_fill(fills, f"sanqing eave corner {i}", (kx, 18, kz), (kx, 20, kz), M.GOLD_ACCENT)

    # Upper body and the great hip roof (庑殿顶).
    add_hollow_box(fills, "sanqing hall upper", 3810, 19, 4425, 3950, 25, 4535, DARK_WALL, thickness=1)
    add_fill(fills, "sanqing hall upper ceiling", (3811, 25, 4426), (3949, 25, 4534), M.WOOD)
    for i, (ux, uz) in enumerate(((3810, 4425), (3949, 4425), (3810, 4534), (3949, 4534))):
        add_fill(fills, f"sanqing upper col {i}", (ux, 19, uz), (ux + 1, 25, uz + 1), M.LOG)
    add_outline(fills, "sanqing upper frieze", 3810, 4425, 3950, 4535, 24, 24, M.GOLD_ACCENT, thickness=1)
    add_fill(fills, "sanqing upper window s", (3850, 21, 4425), (3910, 23, 4425), M.GLASS)
    add_fill(fills, "sanqing upper window n", (3850, 21, 4535), (3910, 23, 4535), M.GLASS)
    add_hip_roof(
        fills, "sanqing hall main roof",
        3802, 4417, 3958, 4543,
        26, layers=8, ridge_axis="z", roof_block=ROOF, ridge_block=M.GOLD,
    )

    # ------------------------------------------------------------------
    # 7. South paifang gate (南门牌楼): twin columns, lintel, xuanshan roof.
    # ------------------------------------------------------------------
    add_fill(fills, "sanqing gate column w", (3856, 4, 4256), (3857, 12, 4257), DARK_WALL)
    add_fill(fills, "sanqing gate column e", (3903, 4, 4256), (3904, 12, 4257), DARK_WALL)
    add_ridge_roof(
        fills, "sanqing gate roof",
        GATE_X1, GATE_Z1, GATE_X2, GATE_Z2,
        14, layers=2, ridge_axis="x", roof_block=ROOF, ridge_block=M.GOLD,
    )
    add_fill(fills, "sanqing gate lintel", (3852, 12, 4254), (3908, 13, 4258), M.GOLD_ACCENT)
    add_fill(fills, "sanqing gate plaque", (3872, 11, 4252), (3888, 13, 4252), DARK_WALL)
    add_fill(fills, "sanqing gate plaque seal", (3879, 11, 4251), (3881, 13, 4251), XUAN)

    # ------------------------------------------------------------------
    # 8. Dao banner poles (道幡) flanking the gate.
    # ------------------------------------------------------------------
    for i, px in enumerate(POLE_XS):
        add_fill(fills, f"sanqing banner pole {i}", (px, 4, 4257), (px, 14, 4257), M.LOG)
        add_fill(fills, f"sanqing banner pole top {i}", (px, 15, 4257), (px, 16, 4257), M.GOLD)
        add_fill(fills, f"sanqing banner a {i}", (px + 1, 12, 4257), (px + 2, 14, 4257), M.RED_WOOL)
        add_fill(fills, f"sanqing banner b {i}", (px + 1, 8, 4257), (px + 2, 10, 4257), M.YELLOW_WOOL)
        add_fill(fills, f"sanqing banner c {i}", (px + 1, 4, 4257), (px + 2, 6, 4257), M.RED_WOOL)

    # ------------------------------------------------------------------
    # 9. Pines and lantern avenue (灯柱甬道).
    # ------------------------------------------------------------------
    pines = [
        (3846, 4356), (3846, 4370), (3914, 4356), (3914, 4370),
        (3826, 4296), (3826, 4328), (3934, 4296), (3934, 4328),
        (3860, 4270), (3900, 4270),
        (3742, 4486), (3742, 4512), (3742, 4538),
        (4018, 4486), (4018, 4512), (4018, 4538),
    ]
    for i, (tx, tz) in enumerate(pines):
        add_tree(fills, f"sanqing pine {i}", tx, tz, 4, height=8, spread=2)
    lamps = (
        (3864, 4266), (3896, 4266), (3864, 4273), (3896, 4273),
        (3848, 4382), (3912, 4382),
    )
    for i, (lx, lz) in enumerate(lamps):
        add_fill(fills, f"sanqing lamp post {i}", (lx, 4, lz), (lx, 9, lz), M.LOG)
        add_fill(fills, f"sanqing lamp {i}", (lx, 10, lz), (lx, 10, lz), M.LANTERN)


def main() -> None:
    run_builder(build_sanqing_temple_3d, "sanqing_temple_3d")


if __name__ == "__main__":
    main()
