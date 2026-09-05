from __future__ import annotations

"""
Neiyuan Imperial Garden - Stables & Archery Run (内苑·马厩射圃) 3D module.

中文名: 大明宫内苑·马厩射圃 - the emperor's leisure ground at his own
doorstep: imperial stables, an archery run, a flower house and a lotus
lake inside the north-east inner garden of the Daming Palace.

Location in Chang'an city local coordinates:
    Plot: x 3650 .. 3940, z 4820 .. 5180 (NE corner of the Daming Palace
    inner garden). Ground y 0-4 is graded (stone base + lawn) and all main
    structures rise from y 5.
    Neighbour avoidance: the Taiji drum tower (3600, 4700) stands about
    120 blocks north-west of the plot, Sanqing Hall (z <= 4600) lies more
    than 220 blocks further north, and the Jiacheng double-wall corridor
    runs at x >= 4200 east of the plot - none are touched. Every fill in
    this module stays strictly inside x 3650..3940 / z 4820..5180; ward
    housing may overlap the plot.

Distinctive features:
    - Graded site (y0-1 stone, y2-3 lawn) ringed by a white garden wall
      with a south gate tower carrying a gilded "内苑" name plaque
    - Imperial stables: a 12-stall row (fence partitions, stone/water
      troughs, hay racks, hitching posts) under a green ridge roof with
      three glazed ventilation monitors, fronted by a rounded sand
      training yard with slalom poles and a rail jump
    - Archery run (射圃): three sand lanes, three framed targets (white
      terracotta face + red wool bullseye + gold pin), wooden bow racks,
      two rows of viewing seats and a low enclosure wall
    - Central lake (x 3720..3800, z 4950..5050, water y0..1) with a stone
      pile-platform water pavilion (four red columns, gilded pyramid
      roof), zig-zag stepping stones and lily pads
    - North greenhouse: timber-framed glass gable roof, two-tier flower
      benches holding eight coloured-wool flower pots, outdoor flower beds
    - NE imperial storehouse with chest benches, barrel stacks and scroll
      racks; SW deer paddock with two reclining quartz deer and a hay
      trough
    - Lantern-lined avenues alternating willows and cypresses
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    Fill,
    Materials as M,
    add_fill,
    add_lantern_line,
    add_outline,
    add_pixel_mural,
    add_pyramid_roof,
    add_ridge_roof,
    run_builder,
)


# ---------------------------------------------------------------------------
# Site bounds (hard limits - never build outside).
# ---------------------------------------------------------------------------
SITE_X1, SITE_Z1 = 3650, 4820
SITE_X2, SITE_Z2 = 3940, 5180

WALL_X1, WALL_Z1 = 3656, 4826
WALL_X2, WALL_Z2 = 3934, 5174
WALL_TOP = 12

SLAB = "minecraft:smooth_stone_slab[type=bottom,waterlogged=false]"
SAND = "minecraft:sand"
HAY = "minecraft:hay_block"
GLASS_BLOCK = "minecraft:glass"
LILY = "minecraft:lily_pad"
SPRUCE_LEAVES = "minecraft:spruce_leaves"
CHEST = "minecraft:chest"
BARREL = "minecraft:barrel"

# Imperial stables (west side): 12 stalls on a 5-block z pitch.
STB_X1, STB_Z1 = 3662, 4839
STB_X2, STB_Z2 = 3692, 4901
STALL_Z0 = 4840
STALL_PITCH = 5
STALL_N = 12

# Training yard east of the stables.
YD_X1, YD_Z1 = 3698, 4834
YD_X2, YD_Z2 = 3776, 4896

# Archery run (east side).
AR_X1, AR_Z1 = 3816, 4918
AR_X2, AR_Z2 = 3930, 5072
AR_TARGET_Z = 4929
AR_SHOOT_Z = 5057
AR_LANES = (3831, 3851, 3871)

# Central lake + water pavilion.
LK_X1, LK_Z1 = 3720, 4950
LK_X2, LK_Z2 = 3800, 5050
PAV_CX, PAV_CZ = 3760, 5000

# Greenhouse (north side).
GH_X1, GH_Z1 = 3796, 4836
GH_X2, GH_Z2 = 3852, 4900
GH_RX = (GH_X1 + GH_X2) // 2

# Imperial storehouse (NE corner).
WH_X1, WH_Z1 = 3884, 4834
WH_X2, WH_Z2 = 3928, 4890

# Deer paddock (SW corner).
DP_X1, DP_Z1 = 3658, 5078
DP_X2, DP_Z2 = 3712, 5168

# South avenue.
AV_X1, AV_X2 = 3746, 3774

# Gilded plaque calligraphy for the gate (stylised 内 + 苑, 5x6 each).
NEI_GLYPH = [
    "#####",
    "#.#.#",
    "#.#.#",
    "#.#.#",
    "##.##",
]
YUAN_GLYPH = [
    "#.#.#",
    "#####",
    "#...#",
    "#.###",
    "#####",
]
PLAQUE_ART = [nei + "...." + yuan for nei, yuan in zip(NEI_GLYPH, YUAN_GLYPH)]


def _willow(fills: list[Fill], x: int, z: int) -> None:
    """Weeping willow: trunk, tall crown and a drooping leaf skirt."""
    add_fill(fills, f"neiyuan willow trunk {x},{z}", (x, 4, z), (x, 9, z), M.TREE_LOG)
    add_fill(fills, f"neiyuan willow crown {x},{z}", (x - 3, 8, z - 3), (x + 3, 12, z + 3), M.LEAVES)
    add_fill(fills, f"neiyuan willow skirt {x},{z}", (x - 4, 7, z - 4), (x + 4, 7, z + 4), M.LEAVES)


def _cypress(fills: list[Fill], x: int, z: int) -> None:
    """Narrow dark cypress column."""
    add_fill(fills, f"neiyuan cypress trunk {x},{z}", (x, 4, z), (x, 6, z), M.TREE_LOG)
    add_fill(fills, f"neiyuan cypress body {x},{z}", (x - 1, 6, z - 1), (x + 1, 15, z + 1), SPRUCE_LEAVES)
    add_fill(fills, f"neiyuan cypress tip {x},{z}", (x, 16, z), (x, 18, z), SPRUCE_LEAVES)


def _vent_monitor(fills: list[Fill], zc: int) -> None:
    """One ridge ventilation monitor (气楼) on the stable roof."""
    add_fill(fills, f"neiyuan stable vent base {zc}", (3674, 18, zc - 3), (3680, 19, zc + 3), M.WOOD)
    add_fill(fills, f"neiyuan stable vent light {zc}", (3675, 20, zc - 2), (3679, 20, zc + 2), GLASS_BLOCK)
    add_fill(fills, f"neiyuan stable vent cap {zc}", (3673, 21, zc - 4), (3681, 21, zc + 4), M.SMOOTH)
    add_fill(fills, f"neiyuan stable vent finial {zc}", (3676, 22, zc - 1), (3678, 23, zc + 1), M.GOLD)


def _archery_target(fills: list[Fill], cx: int) -> None:
    """One framed target: wood posts, white face, red bullseye, gold pin."""
    z = AR_TARGET_Z
    add_fill(fills, f"neiyuan target base {cx}", (cx - 5, 4, z - 2), (cx + 5, 4, z), M.SMOOTH)
    add_fill(fills, f"neiyuan target post w {cx}", (cx - 5, 5, z - 1), (cx - 5, 11, z - 1), M.WOOD)
    add_fill(fills, f"neiyuan target post e {cx}", (cx + 5, 5, z - 1), (cx + 5, 11, z - 1), M.WOOD)
    add_fill(fills, f"neiyuan target face {cx}", (cx - 4, 5, z), (cx + 4, 10, z), M.WHITE_TERRACOTTA)
    add_fill(fills, f"neiyuan target ring {cx}", (cx - 1, 7, z), (cx + 1, 9, z), M.RED_WOOL)
    add_fill(fills, f"neiyuan target pin {cx}", (cx, 8, z), (cx, 8, z), M.GOLD)


def _bow_rack(fills: list[Fill], x: int, z: int) -> None:
    """Bow rack: two fence posts carrying a wooden bow arc."""
    add_fill(fills, f"neiyuan bow rack post w {x}", (x - 1, 4, z), (x - 1, 7, z), M.FENCE)
    add_fill(fills, f"neiyuan bow rack post e {x}", (x + 1, 4, z), (x + 1, 7, z), M.FENCE)
    add_fill(fills, f"neiyuan bow arc {x}", (x - 2, 8, z), (x + 2, 8, z), M.WOOD)


def _flower_bed(fills: list[Fill], cx: int, cz: int) -> None:
    """Raised outdoor flower bed with striped wool blooms."""
    add_fill(fills, f"neiyuan flower bed base {cx},{cz}", (cx - 5, 4, cz - 4), (cx + 5, 4, cz + 4), M.GRASS)
    add_fill(fills, f"neiyuan flower bed pink {cx},{cz}", (cx - 4, 5, cz - 2), (cx + 4, 5, cz - 2), M.PINK_WOOL)
    add_fill(fills, f"neiyuan flower bed red {cx},{cz}", (cx - 4, 5, cz), (cx + 4, 5, cz), M.RED_WOOL)
    add_fill(fills, f"neiyuan flower bed yellow {cx},{cz}", (cx - 4, 5, cz + 2), (cx + 4, 5, cz + 2), M.YELLOW_WOOL)


def build_neiyuan_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site grading, perimeter garden wall and the south gate tower.
    # ------------------------------------------------------------------
    add_fill(fills, "neiyuan site stone base", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "neiyuan site lawn", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)

    add_outline(fills, "neiyuan wall", WALL_X1, WALL_Z1, WALL_X2, WALL_Z2, 4, WALL_TOP, M.WHITE, thickness=2)
    add_outline(fills, "neiyuan wall cap", WALL_X1, WALL_Z1, WALL_X2, WALL_Z2, WALL_TOP + 1, WALL_TOP + 1, SLAB, thickness=2)

    # South gate: carved opening, flanking posts, lintel, gilded plaque.
    add_fill(fills, "neiyuan gate threshold", (3748, 4, 5170), (3772, 4, 5176), M.GRANITE)
    add_fill(fills, "neiyuan gate opening", (3750, 4, 5171), (3770, 9, 5177), M.AIR)
    add_fill(fills, "neiyuan gate post w", (3744, 4, 5168), (3749, 18, 5178), M.RED_WALL)
    add_fill(fills, "neiyuan gate post e", (3771, 4, 5168), (3776, 18, 5178), M.RED_WALL)
    add_fill(fills, "neiyuan gate lintel", (3750, 10, 5168), (3770, 11, 5178), M.WOOD)
    add_fill(fills, "neiyuan gate plaque", (3749, 10, 5179), (3771, 18, 5179), M.GOLD)
    add_pixel_mural(fills, "neiyuan gate plaque glyph", PLAQUE_ART, {"#": M.BLACK_WOOL}, 3753, 17, 5179, axis="x")
    add_ridge_roof(fills, "neiyuan gate roof", 3742, 5166, 3778, 5178, 19, layers=2, ridge_axis="x")

    # ------------------------------------------------------------------
    # 2. Imperial stables (御马厩): 12 stalls, troughs, hay, hitching posts.
    # ------------------------------------------------------------------
    add_fill(fills, "neiyuan stable floor", (STB_X1, 4, STB_Z1), (STB_X2, 4, STB_Z2), M.SMOOTH)
    add_fill(fills, "neiyuan stable back wall", (STB_X1, 5, STB_Z1), (STB_X1 + 1, 10, STB_Z2), M.STONE)
    add_fill(fills, "neiyuan stable end wall n", (STB_X1, 5, STB_Z1), (STB_X2, 10, STB_Z1), M.WOOD)
    add_fill(fills, "neiyuan stable end wall s", (STB_X1, 5, STB_Z2), (STB_X2, 10, STB_Z2), M.WOOD)
    add_fill(fills, "neiyuan stable air", (3664, 5, 4841), (3690, 10, 4899), M.AIR)

    for i in range(1, STALL_N):
        zb = STALL_Z0 + i * STALL_PITCH
        add_fill(fills, f"neiyuan stall divider {zb}", (3669, 4, zb), (3672, 8, zb), M.FENCE)
    for i in range(STALL_N):
        z1 = STALL_Z0 + 1 + i * STALL_PITCH
        add_fill(fills, f"neiyuan stall hay {z1}", (3664, 5, z1), (3665, 7, z1 + 3), HAY)
        add_fill(fills, f"neiyuan stall hitch {z1}", (3673, 4, z1 + 1), (3673, 7, z1 + 1), M.LOG)
    add_fill(fills, "neiyuan stable trough stone", (3666, 4, 4841), (3668, 4, 4899), M.SMOOTH)
    add_fill(fills, "neiyuan stable trough water", (3667, 5, 4841), (3668, 5, 4899), M.WATER)

    add_ridge_roof(fills, "neiyuan stable roof", 3660, 4837, 3694, 4903, 11, layers=3, ridge_axis="z")
    for pz in (4842, 4860, 4878, 4896):
        add_fill(fills, f"neiyuan stable front post {pz}", (3691, 5, pz), (3692, 10, pz + 1), M.LOG)
    add_fill(fills, "neiyuan stable front lintel", (3691, 11, STB_Z1), (3692, 11, STB_Z2), M.WOOD)
    for zc in (4855, 4870, 4885):
        _vent_monitor(fills, zc)

    # ------------------------------------------------------------------
    # 3. Training yard (驯马场): rounded fence ring on sand.
    # ------------------------------------------------------------------
    add_fill(fills, "neiyuan yard sand", (YD_X1, 4, YD_Z1), (YD_X2, 4, YD_Z2), SAND)
    add_outline(fills, "neiyuan yard fence", YD_X1, YD_Z1, YD_X2, YD_Z2, 4, 6, M.FENCE)
    for cx, cz in ((3700, 4836), (3774, 4836), (3700, 4894), (3774, 4894)):
        add_fill(fills, f"neiyuan yard corner {cx},{cz}", (cx, 4, cz), (cx, 6, cz), M.FENCE)
    add_fill(fills, "neiyuan yard gate", (YD_X1, 4, 4862), (YD_X1, 6, 4866), M.AIR)
    for px, pz in ((3708, 4844), (3724, 4856), (3740, 4844)):
        add_fill(fills, f"neiyuan yard slalom {px}", (px, 4, pz), (px + 1, 9, pz + 1), M.LOG)
    add_fill(fills, "neiyuan jump post w", (3744, 4, 4880), (3744, 5, 4880), M.FENCE)
    add_fill(fills, "neiyuan jump post e", (3760, 4, 4880), (3760, 5, 4880), M.FENCE)
    add_fill(fills, "neiyuan jump bar", (3744, 6, 4880), (3760, 6, 4880), M.RED_WOOL)

    # ------------------------------------------------------------------
    # 4. Archery run (射圃): lanes, targets, bow racks, seats, low wall.
    # ------------------------------------------------------------------
    add_outline(fills, "neiyuan range wall", AR_X1, AR_Z1, AR_X2, AR_Z2, 4, 6, M.STONE)
    add_fill(fills, "neiyuan range gate", (AR_X1, 4, 4962), (AR_X1, 6, 4970), M.AIR)
    for i, cx in enumerate(AR_LANES):
        add_fill(fills, f"neiyuan lane {i}", (cx - 5, 4, 4934), (cx + 5, 4, AR_SHOOT_Z + 1), SAND)
    add_fill(fills, "neiyuan shooting line", (3822, 4, AR_SHOOT_Z - 1), (3880, 4, AR_SHOOT_Z + 1), M.GRANITE)
    for cx in AR_LANES:
        _archery_target(fills, cx)
    for rx in (3830, 3851, 3872):
        _bow_rack(fills, rx, AR_SHOOT_Z + 5)
    add_fill(fills, "neiyuan seat row a", (3818, 4, 4956), (3820, 5, 5048), M.WOOD)
    add_fill(fills, "neiyuan seat row b", (3822, 4, 4956), (3824, 5, 5048), M.WOOD)
    add_fill(fills, "neiyuan seat back a", (3817, 6, 4956), (3817, 6, 5048), M.FENCE)
    add_fill(fills, "neiyuan seat back b", (3821, 6, 4956), (3821, 6, 5048), M.FENCE)
    add_fill(fills, "neiyuan seat cushion a", (3818, 6, 4958), (3820, 6, 5046), M.RED_WOOL)
    add_fill(fills, "neiyuan seat cushion b", (3822, 6, 4958), (3824, 6, 5046), M.RED_WOOL)
    add_fill(fills, "neiyuan range flag pole", (3924, 4, 4934), (3924, 14, 4934), M.LOG)
    add_fill(fills, "neiyuan range flag", (3922, 10, 4934), (3926, 13, 4934), M.RED_WOOL)

    # ------------------------------------------------------------------
    # 5. Central lake (水景) with pile-platform pavilion and stepping stones.
    # ------------------------------------------------------------------
    add_fill(fills, "neiyuan lake clear", (3722, 2, 4952), (3798, 3, 5048), M.AIR)
    add_fill(fills, "neiyuan lake floor", (3721, -1, 4951), (3799, -1, 5049), M.SMOOTH)
    add_fill(fills, "neiyuan lake water", (3721, 0, 4951), (3799, 1, 5049), M.WATER)
    add_outline(fills, "neiyuan lake curb", LK_X1, LK_Z1, LK_X2, LK_Z2, 2, 3, M.SMOOTH)

    # Water pavilion on stone piles: platform, rails, columns, gilded roof.
    for px in (3753, 3766):
        for pz in (4993, 5006):
            add_fill(fills, f"neiyuan pavilion pile {px},{pz}", (px, 0, pz), (px + 1, 1, pz + 1), M.STONE)
    add_fill(fills, "neiyuan pavilion platform", (3752, 2, 4992), (3768, 3, 5008), M.STONE)
    add_fill(fills, "neiyuan pavilion floor", (3752, 3, 4992), (3768, 3, 5008), M.SMOOTH)
    add_fill(fills, "neiyuan pavilion rail n", (3752, 4, 4992), (3768, 4, 4992), M.FENCE)
    add_fill(fills, "neiyuan pavilion rail w", (3752, 4, 4992), (3752, 4, 5008), M.FENCE)
    add_fill(fills, "neiyuan pavilion rail e", (3768, 4, 4992), (3768, 4, 5008), M.FENCE)
    add_fill(fills, "neiyuan pavilion rail s", (3752, 4, 5008), (3768, 4, 5008), M.FENCE)
    add_fill(fills, "neiyuan pavilion rail gap", (3758, 4, 5008), (3762, 4, 5008), M.AIR)
    for px in (3754, 3765):
        for pz in (4994, 5005):
            add_fill(fills, f"neiyuan pavilion column {px},{pz}", (px, 4, pz), (px + 1, 10, pz + 1), M.RED_WALL)
    add_fill(fills, "neiyuan pavilion beam", (3753, 11, 4993), (3767, 11, 5007), M.WOOD)
    add_pyramid_roof(fills, "neiyuan pavilion roof", PAV_CX, PAV_CZ, radius=8, y=12, roof_block=M.ROOF_GREEN, apex_block=M.GOLD)
    for lx, lz in ((3753, 4993), (3767, 5007)):
        add_fill(fills, f"neiyuan pavilion lamp post {lx},{lz}", (lx, 4, lz), (lx, 9, lz), M.LOG)
        add_fill(fills, f"neiyuan pavilion lamp {lx},{lz}", (lx, 10, lz), (lx, 10, lz), M.SEA_LANTERN)

    # Zig-zag stepping stones (汀步) from both banks to the pavilion.
    for i, sz in enumerate((5044, 5036, 5028, 5012)):
        sx = 3758 if i % 2 == 0 else 3762
        add_fill(fills, f"neiyuan stepping s {sz}", (sx, 1, sz), (sx + 1, 2, sz + 1), M.SMOOTH)
    for i, sz in enumerate((4988, 4980, 4964, 4956)):
        sx = 3762 if i % 2 == 0 else 3758
        add_fill(fills, f"neiyuan stepping n {sz}", (sx, 1, sz), (sx + 1, 2, sz + 1), M.SMOOTH)
    for i, (lx, lz) in enumerate(((3734, 4972), (3786, 5028), (3742, 5034))):
        add_fill(fills, f"neiyuan lily {i}", (lx, 2, lz), (lx, 2, lz), LILY)

    # ------------------------------------------------------------------
    # 6. Greenhouse (花房): timber frame, glass roof, two-tier flower racks.
    # ------------------------------------------------------------------
    add_fill(fills, "neiyuan greenhouse floor", (GH_X1, 4, GH_Z1), (GH_X2, 4, GH_Z2), M.SMOOTH)
    add_outline(fills, "neiyuan greenhouse sill", GH_X1, GH_Z1, GH_X2, GH_Z2, 5, 5, M.WOOD)
    add_outline(fills, "neiyuan greenhouse glazing", GH_X1, GH_Z1, GH_X2, GH_Z2, 6, 11, M.GLASS)
    for px in (GH_X1, GH_RX, GH_X2):
        for pz in (GH_Z1, GH_Z2):
            add_fill(fills, f"neiyuan greenhouse col {px},{pz}", (px, 5, pz), (px + 1, 11, pz + 1), M.LOG)
    add_fill(fills, "neiyuan greenhouse door", (3816, 5, GH_Z2), (3822, 11, GH_Z2), M.AIR)
    add_fill(fills, "neiyuan greenhouse threshold", (3815, 4, GH_Z2), (3823, 4, GH_Z2 + 2), M.GRANITE)
    add_fill(fills, "neiyuan greenhouse ridge post", (3823, 12, 4867), (3825, 17, 4869), M.WOOD)
    for i in range(7):
        y = 12 + i
        wx = GH_X1 + 4 * i
        add_fill(fills, f"neiyuan greenhouse roof w {i}", (wx, y, GH_Z1), (wx + 3, y, GH_Z2), GLASS_BLOCK)
        ex = GH_X2 - 4 * i
        add_fill(fills, f"neiyuan greenhouse roof e {i}", (ex - 3, y, GH_Z1), (ex, y, GH_Z2), GLASS_BLOCK)
    add_fill(fills, "neiyuan greenhouse ridge beam", (3819, 18, GH_Z1), (3829, 19, GH_Z2), M.WOOD)
    for gz in (GH_Z1, GH_Z2):
        add_fill(fills, f"neiyuan greenhouse gable {gz}", (3808, 13, gz), (3840, 15, gz), M.WOOD)

    # Two-tier flower benches with eight coloured-wool pots.
    add_fill(fills, "neiyuan potting bench lower", (3800, 5, 4844), (3806, 5, 4892), M.WOOD)
    add_fill(fills, "neiyuan potting bench upper", (3800, 9, 4848), (3806, 9, 4888), M.WOOD)
    for pz in (4848, 4888):
        add_fill(fills, f"neiyuan bench post {pz}", (3800, 6, pz), (3800, 8, pz), M.LOG)
    lower_pots = (
        (3802, 4852, M.RED_WOOL),
        (3805, 4862, M.PINK_WOOL),
        (3802, 4872, M.YELLOW_WOOL),
        (3805, 4882, M.WHITE_WOOL),
    )
    for px, pz, wool in lower_pots:
        add_fill(fills, f"neiyuan flower pot low {px},{pz}", (px, 6, pz), (px, 6, pz), wool)
        add_fill(fills, f"neiyuan flower bloom low {px},{pz}", (px, 7, pz), (px, 7, pz), M.LEAVES)
    upper_pots = (
        (3803, 4856, M.BLUE_WOOL),
        (3804, 4868, M.GREEN_WOOL),
        (3802, 4880, "minecraft:lime_wool"),
        (3805, 4886, "minecraft:purple_wool"),
    )
    for px, pz, wool in upper_pots:
        add_fill(fills, f"neiyuan flower pot up {px},{pz}", (px, 10, pz), (px, 10, pz), wool)
        add_fill(fills, f"neiyuan flower bloom up {px},{pz}", (px, 11, pz), (px, 11, pz), M.LEAVES)
    _flower_bed(fills, 3810, 4910)
    _flower_bed(fills, 3838, 4910)

    # ------------------------------------------------------------------
    # 7. Imperial storehouse (御库) in the NE corner.
    # ------------------------------------------------------------------
    add_fill(fills, "neiyuan storehouse floor", (WH_X1, 4, WH_Z1), (WH_X2, 4, WH_Z2), M.SMOOTH)
    add_outline(fills, "neiyuan storehouse walls", WH_X1, WH_Z1, WH_X2, WH_Z2, 5, 11, M.RED_WALL)
    add_fill(fills, "neiyuan storehouse air", (WH_X1 + 2, 5, WH_Z1 + 2), (WH_X2 - 2, 11, WH_Z2 - 2), M.AIR)
    add_fill(fills, "neiyuan storehouse door", (3902, 5, WH_Z2), (3910, 8, WH_Z2), M.AIR)
    add_ridge_roof(fills, "neiyuan storehouse roof", WH_X1 - 2, WH_Z1 - 2, WH_X2 + 2, WH_Z2 + 2, 12, layers=3, ridge_axis="z")
    add_fill(fills, "neiyuan store bench", (3888, 5, 4840), (3900, 5, 4844), M.WOOD)
    add_fill(fills, "neiyuan store chests a", (3888, 6, 4840), (3900, 6, 4844), CHEST)
    add_fill(fills, "neiyuan store chests b", (3906, 5, 4840), (3918, 6, 4844), CHEST)
    add_fill(fills, "neiyuan store barrels", (3888, 5, 4856), (3894, 7, 4862), BARREL)
    add_fill(fills, "neiyuan scroll rack post n", (3886, 5, 4866), (3886, 10, 4866), M.FENCE)
    add_fill(fills, "neiyuan scroll rack post s", (3886, 5, 4876), (3886, 10, 4876), M.FENCE)
    add_fill(fills, "neiyuan scroll shelf a", (3886, 7, 4866), (3888, 7, 4876), M.WOOD)
    add_fill(fills, "neiyuan scroll shelf b", (3886, 9, 4866), (3888, 9, 4876), M.WOOD)
    add_fill(fills, "neiyuan scroll rolls", (3887, 8, 4867), (3887, 8, 4875), M.WHITE_TERRACOTTA)
    add_fill(fills, "neiyuan store lamp a", (3890, 11, 4840), (3890, 11, 4840), M.SEA_LANTERN)
    add_fill(fills, "neiyuan store lamp b", (3922, 11, 4884), (3922, 11, 4884), M.SEA_LANTERN)

    # ------------------------------------------------------------------
    # 8. Deer paddock (鹿苑) in the SW corner.
    # ------------------------------------------------------------------
    add_outline(fills, "neiyuan deer fence", DP_X1, DP_Z1, DP_X2, DP_Z2, 4, 6, M.FENCE)
    add_fill(fills, "neiyuan deer gate", (DP_X2, 4, 5120), (DP_X2, 6, 5126), M.AIR)
    # Reclining stag, head to the west.
    add_fill(fills, "neiyuan stag body", (3676, 4, 5110), (3686, 5, 5113), M.QUARTZ)
    add_fill(fills, "neiyuan stag shoulder", (3676, 6, 5110), (3678, 6, 5113), M.QUARTZ)
    add_fill(fills, "neiyuan stag neck", (3673, 5, 5111), (3674, 8, 5112), M.QUARTZ)
    add_fill(fills, "neiyuan stag head", (3670, 7, 5111), (3672, 8, 5112), M.QUARTZ)
    add_fill(fills, "neiyuan stag antlers", (3670, 9, 5110), (3671, 10, 5113), M.GOLD_ACCENT)
    add_fill(fills, "neiyuan stag tail", (3687, 5, 5111), (3687, 6, 5112), M.QUARTZ)
    # Grazing doe, head down at the east end.
    add_fill(fills, "neiyuan doe body", (3690, 4, 5140), (3698, 5, 5143), M.QUARTZ)
    add_fill(fills, "neiyuan doe neck", (3699, 4, 5141), (3700, 6, 5142), M.QUARTZ)
    add_fill(fills, "neiyuan doe head", (3701, 4, 5141), (3702, 5, 5142), M.QUARTZ)
    add_fill(fills, "neiyuan deer trough base", (3666, 4, 5088), (3674, 4, 5090), M.SMOOTH)
    add_fill(fills, "neiyuan deer trough hay", (3666, 5, 5088), (3674, 5, 5090), HAY)
    add_fill(fills, "neiyuan deer shrub", (3662, 4, 5150), (3664, 5, 5152), M.LEAVES)

    # ------------------------------------------------------------------
    # 9. Avenues, lantern posts, alternating willows and cypresses.
    # ------------------------------------------------------------------
    add_fill(fills, "neiyuan avenue paving", (AV_X1, 4, 5050), (AV_X2, 4, 5172), M.GRANITE)
    add_fill(fills, "neiyuan cross path", (3666, 4, 4936), (3812, 4, 4944), M.GRANITE)
    add_fill(fills, "neiyuan greenhouse path", (3821, 4, 4902), (3827, 4, 4936), M.GRANITE)
    add_lantern_line(fills, "neiyuan avenue lantern w", 3742, 5060, 3742, 5160, 4, 25)
    add_lantern_line(fills, "neiyuan avenue lantern e", 3778, 5060, 3778, 5160, 4, 25)
    add_lantern_line(fills, "neiyuan path lantern", 3670, 4934, 3810, 4934, 4, 40)
    for tx, tz in ((3734, 5084), (3708, 4986), (3672, 4990), (3810, 5030)):
        _willow(fills, tx, tz)
    for tx, tz in ((3740, 5132), (3670, 5030), (3782, 5102), (3812, 4980), (3668, 4952)):
        _cypress(fills, tx, tz)


def main() -> None:
    run_builder(build_neiyuan_3d, "neiyuan_3d")


if __name__ == "__main__":
    main()
