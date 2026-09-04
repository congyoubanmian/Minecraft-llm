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
    add_platform_with_steps,
    add_pool,
    add_pyramid_roof,
    add_ridge_roof,
    add_tree,
    run_builder,
)


"""
Jingjiao Stele Garden 3D (义宁坊·大秦景教碑碑园) - a memorial garden for the
"Nestorian Stele" 大秦景教流行中国碑 (carved AD 781, Tang Jianzhong 2nd year),
the celebrated stele recording the arrival of the Church of the East (景教,
the "Luminous Religion") in Tang Chang'an, erected in Yining Ward where the
Da Qin monastery stood.

Location in Chang'an city local coordinates:
    Yining Ward (义宁坊): x 700..1000, z 3150..3450, ground y 0..4, main
    structures rise from y 5. The Nestorian Da Qin Monastery (景教十字寺,
    foreign_temples.py, x 1400..1800 / z 2000..2400) stands to the
    north-east across the ward grid - this stele garden echoes its
    white-stone walls and gilded crosses as a companion landmark.
    Neighbours respected: West Market ward buildings end at z 3100
    (untouched to the north), Tangchang Abbey starts at x 1150 (never
    crossed); ward housing beneath may be overwritten.

Distinctive features:
    - Stele pavilion (碑亭) on the central axis: four red columns carrying
      a gilded pyramid roof (攒尖金顶) over the giant Nestorian stele - a
      3x3x11 quartz-pillar shaft on a dark turtle pedestal (龟趺), crowned
      with a 5x5 gold cross set in white-terracotta cloud corners (云纹)
    - Cross-and-pearl screen wall (十字连珠纹照壁) directly north of the
      pavilion: white stone panel with a great gold cross, a ring of
      yellow "pearl" beads and mirrored azalea-leaf scroll vines (卷草纹)
    - Missionary graveyard (传教士墓园) west of the axis: nine small
      3x1x5 quartz steles on smooth-stone feet in two diagonal ranks,
      two bearing small gold cross crowns
    - Scripture hall (经卷堂) east of the axis: bookshelf scripture walls,
      a chest cabinet of sutra cases, a lectern translation desk and a
      long work table
    - Chapel (礼拜小堂) at the north end of the axis: white-stone walls,
      timber trusses under an overhanging gable roof (悬山顶), a round
      east window of glass and a small gold cross on the door lintel
    - Silk Road caravaneer rest stop outside the south gate: stone water
      trough, two hitching posts and a half-open thatched lean-to
    - White-stone perimeter wall with a twin-column south gate, cypress
      rows, a lantern-lined causeway and an ink pool with a stone rim
"""

# ---------------------------------------------------------------------------
# Site constants (local Chang'an coordinates; world = +9000/+64/+9000 via lib).
# ---------------------------------------------------------------------------
SITE_X1, SITE_Z1 = 700, 3150
SITE_X2, SITE_Z2 = 1000, 3450

# White-stone perimeter wall (白石矮墙) lines inside the ward.
GARDEN_X1, GARDEN_Z1 = 740, 3180
GARDEN_X2, GARDEN_Z2 = 959, 3419
GATE_X1, GATE_X2 = 838, 862  # south gate opening on the axis

# Central north-south axis and paved causeway.
AXIS_X = 850
PATH_X1, PATH_X2 = 842, 858

# Stele pavilion (碑亭) terrace and centre.
PAV_CX, PAV_CZ = 850, 3290
PAV_X1, PAV_Z1 = 818, 3258
PAV_X2, PAV_Z2 = 882, 3322

# Cross-and-pearl screen wall (十字连珠纹照壁) north of the pavilion.
SCREEN_X1, SCREEN_Z1 = 830, 3234
SCREEN_X2, SCREEN_Z2 = 870, 3236

# Chapel (礼拜小堂) at the north end of the axis.
CHAPEL_X1, CHAPEL_Z1 = 822, 3172
CHAPEL_X2, CHAPEL_Z2 = 878, 3220

# Scripture hall (经卷堂) east of the axis.
HALL_X1, HALL_Z1 = 892, 3272
HALL_X2, HALL_Z2 = 948, 3318

# Missionary graveyard (传教士墓园) west of the axis.
GRAVE_X1, GRAVE_Z1 = 754, 3212
GRAVE_X2, GRAVE_Z2 = 806, 3258

# Ink pool (墨池) south-east of the pavilion.
POOL_X1, POOL_Z1 = 892, 3352
POOL_X2, POOL_Z2 = 936, 3378

# Syriac / Nestorian accent blocks.
QUARTZ_PILLAR = "minecraft:quartz_pillar[axis=y]"
AZALEA_LEAVES = "minecraft:azalea_leaves"
BOOKSHELF = "minecraft:bookshelf"
CHEST = "minecraft:chest"
LECTERN = "minecraft:lectern"


def _missionary_stele(
    fills: list[Fill],
    label: str,
    x: int,
    z: int,
    with_cross: bool,
) -> None:
    """One missionary gravestone: smooth foot, 3x1x5 quartz slab, optional cross."""
    add_fill(fills, f"{label} foot", (x, 4, z), (x + 2, 4, z), M.SMOOTH)
    add_fill(fills, f"{label} slab", (x, 5, z), (x + 2, 9, z), M.QUARTZ)
    if with_cross:
        add_fill(fills, f"{label} cross v", (x + 1, 10, z), (x + 1, 11, z), M.GOLD)
        add_fill(fills, f"{label} cross h", (x, 11, z), (x + 2, 11, z), M.GOLD)


def build_jingjiao_bei_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site grading: stone base y0..1, lawn y2..3, white-stone perimeter
    #    wall with a twin-column south gate on the axis.
    # ------------------------------------------------------------------
    add_fill(fills, "jingjiao foundation", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "jingjiao lawn", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)
    add_fill(fills, "jingjiao wall n", (GARDEN_X1, 4, GARDEN_Z1), (GARDEN_X2, 6, GARDEN_Z1), M.QUARTZ)
    add_fill(fills, "jingjiao wall s", (GARDEN_X1, 4, GARDEN_Z2), (GARDEN_X2, 6, GARDEN_Z2), M.QUARTZ)
    add_fill(fills, "jingjiao wall w", (GARDEN_X1, 4, GARDEN_Z1), (GARDEN_X1, 6, GARDEN_Z2), M.QUARTZ)
    add_fill(fills, "jingjiao wall e", (GARDEN_X2, 4, GARDEN_Z1), (GARDEN_X2, 6, GARDEN_Z2), M.QUARTZ)
    add_fill(fills, "jingjiao coping n", (GARDEN_X1, 7, GARDEN_Z1), (GARDEN_X2, 7, GARDEN_Z1), M.SMOOTH)
    add_fill(fills, "jingjiao coping s", (GARDEN_X1, 7, GARDEN_Z2), (GARDEN_X2, 7, GARDEN_Z2), M.SMOOTH)
    add_fill(fills, "jingjiao coping w", (GARDEN_X1, 7, GARDEN_Z1), (GARDEN_X1, 7, GARDEN_Z2), M.SMOOTH)
    add_fill(fills, "jingjiao coping e", (GARDEN_X2, 7, GARDEN_Z1), (GARDEN_X2, 7, GARDEN_Z2), M.SMOOTH)
    # South gate: opening, twin quartz-pillar columns, timber lintel.
    add_fill(fills, "jingjiao gate opening", (GATE_X1, 4, GARDEN_Z2), (GATE_X2, 7, GARDEN_Z2), M.AIR)
    add_fill(fills, "jingjiao gate col w", (834, 4, GARDEN_Z2), (835, 10, GARDEN_Z2 + 1), QUARTZ_PILLAR)
    add_fill(fills, "jingjiao gate col e", (865, 4, GARDEN_Z2), (866, 10, GARDEN_Z2 + 1), QUARTZ_PILLAR)
    add_fill(fills, "jingjiao gate cap w", (834, 11, GARDEN_Z2), (835, 11, GARDEN_Z2 + 1), M.GOLD)
    add_fill(fills, "jingjiao gate cap e", (865, 11, GARDEN_Z2), (866, 11, GARDEN_Z2 + 1), M.GOLD)
    add_fill(fills, "jingjiao gate lamp w", (834, 12, GARDEN_Z2), (835, 12, GARDEN_Z2 + 1), M.SEA_LANTERN)
    add_fill(fills, "jingjiao gate lamp e", (865, 12, GARDEN_Z2), (866, 12, GARDEN_Z2 + 1), M.SEA_LANTERN)
    add_fill(fills, "jingjiao gate lintel", (GATE_X1 - 2, 8, GARDEN_Z2), (GATE_X2 + 2, 8, GARDEN_Z2), M.LOG)
    add_fill(fills, "jingjiao gate threshold", (GATE_X1, 4, GARDEN_Z2 - 2), (GATE_X2, 4, GARDEN_Z2 - 2), M.GOLD)

    # ------------------------------------------------------------------
    # 2. Paved causeway and landing paths along the axis.
    # ------------------------------------------------------------------
    add_fill(fills, "jingjiao causeway", (PATH_X1, 4, 3330), (PATH_X2, 4, GARDEN_Z2), M.SMOOTH)
    add_fill(fills, "jingjiao gate apron", (GATE_X1, 4, GARDEN_Z2 + 1), (GATE_X2, 4, GARDEN_Z2 + 25), M.SMOOTH)
    add_fill(fills, "jingjiao rest path", (760, 4, GARDEN_Z2 + 1), (832, 4, 3442), M.SMOOTH)
    add_fill(fills, "jingjiao forecourt", (830, 4, 3221), (870, 4, 3233), M.SMOOTH)
    add_fill(fills, "jingjiao chapel terrace", (CHAPEL_X1, 4, CHAPEL_Z1), (CHAPEL_X2, 4, CHAPEL_Z2), M.SMOOTH)
    # Steps up to and down from the pavilion terrace (gentle, one fill per tread).
    add_fill(fills, "jingjiao pavilion step s a", (PATH_X1, 5, 3323), (PATH_X2, 5, 3326), M.SMOOTH)
    add_fill(fills, "jingjiao pavilion step s b", (PATH_X1, 4, 3327), (PATH_X2, 4, 3330), M.SMOOTH)
    add_fill(fills, "jingjiao pavilion step n a", (PATH_X1, 5, 3254), (PATH_X2, 5, 3257), M.SMOOTH)
    add_fill(fills, "jingjiao pavilion step n b", (PATH_X1, 4, 3248), (PATH_X2, 4, 3253), M.SMOOTH)

    # ------------------------------------------------------------------
    # 3. Stele pavilion (碑亭): stepped terrace, four red columns, gilded
    #    pyramid roof, and the giant Nestorian stele at its heart.
    # ------------------------------------------------------------------
    add_platform_with_steps(fills, "jingjiao pavilion terrace", PAV_X1, PAV_Z1, PAV_X2, PAV_Z2, 4,
                            [(2, 0, M.STONE), (1, 6, M.SMOOTH)])
    for i, (px, pz) in enumerate([(838, 3280), (861, 3280), (838, 3299), (861, 3299)]):
        add_fill(fills, f"jingjiao pavilion column {i}", (px, 7, pz), (px + 1, 16, pz + 1), M.RED_WALL)
    # The Nestorian stele: dark turtle pedestal (龟趺), 3x3x11 quartz-pillar
    # shaft with inscription bands, crown with a 5x5 gold cross and
    # white-terracotta cloud corners (built after the roof stays intact).
    add_fill(fills, "jingjiao stele turtle base", (846, 7, 3286), (853, 7, 3293), M.DARK)
    add_fill(fills, "jingjiao stele turtle shell", (847, 8, 3287), (852, 8, 3292), M.DARK)
    add_fill(fills, "jingjiao stele turtle head", (849, 7, 3294), (851, 8, 3295), M.DARK)
    add_fill(fills, "jingjiao stele shaft", (849, 9, 3289), (851, 19, 3291), QUARTZ_PILLAR)
    add_fill(fills, "jingjiao stele band a", (849, 12, 3291), (851, 12, 3291), M.DARK)
    add_fill(fills, "jingjiao stele band b", (849, 16, 3291), (851, 16, 3291), M.DARK)
    add_fill(fills, "jingjiao stele crown", (848, 20, 3289), (852, 25, 3291), M.QUARTZ)
    # Gilded pyramid roof (攒尖金顶) over the four columns.
    add_pyramid_roof(fills, "jingjiao pavilion roof", PAV_CX, PAV_CZ, radius=11, y=17,
                     roof_block=M.ROOF_GREEN, apex_block=M.GOLD)
    # Crown front (south) mosaic: 5x5 gold cross, cloud corners in white.
    add_fill(fills, "jingjiao stele cross v", (850, 21, 3291), (850, 25, 3291), M.GOLD)
    add_fill(fills, "jingjiao stele cross h", (848, 23, 3291), (852, 23, 3291), M.GOLD)
    for cxx, cyy in ((848, 21), (852, 21), (848, 25), (852, 25)):
        add_fill(fills, f"jingjiao stele cloud {cxx},{cyy}", (cxx, cyy, 3291), (cxx, cyy, 3291), M.WHITE_TERRACOTTA)
    add_fill(fills, "jingjiao stele finial", (850, 26, 3290), (850, 27, 3290), M.GOLD)

    # ------------------------------------------------------------------
    # 4. Cross-and-pearl screen wall (十字连珠纹照壁) north of the pavilion:
    #    white stone body, great gold cross, yellow pearl ring, mirrored
    #    azalea-leaf scroll vines.
    # ------------------------------------------------------------------
    face_z = SCREEN_Z2  # south face looking back at the stele pavilion
    add_fill(fills, "jingjiao screen body", (SCREEN_X1, 4, SCREEN_Z1), (SCREEN_X2, 15, SCREEN_Z2), M.QUARTZ)
    add_fill(fills, "jingjiao screen coping", (SCREEN_X1 - 1, 16, SCREEN_Z1 - 1),
             (SCREEN_X2 + 1, 16, SCREEN_Z2 + 1), M.DARK)
    add_fill(fills, "jingjiao screen cross v", (849, 5, face_z), (851, 14, face_z), M.GOLD)
    add_fill(fills, "jingjiao screen cross h", (840, 8, face_z), (860, 10, face_z), M.GOLD)
    for bx in range(840, 861, 4):
        add_fill(fills, f"jingjiao screen bead b{bx}", (bx, 4, face_z), (bx, 4, face_z), M.YELLOW_WOOL)
        add_fill(fills, f"jingjiao screen bead t{bx}", (bx, 15, face_z), (bx, 15, face_z), M.YELLOW_WOOL)
    for by in (7, 11):
        add_fill(fills, f"jingjiao screen bead w{by}", (837, by, face_z), (837, by, face_z), M.YELLOW_WOOL)
        add_fill(fills, f"jingjiao screen bead e{by}", (863, by, face_z), (863, by, face_z), M.YELLOW_WOOL)
    for cxx, cyy in ((837, 4), (863, 4), (837, 15), (863, 15)):
        add_fill(fills, f"jingjiao screen bead c{cxx},{cyy}", (cxx, cyy, face_z), (cxx, cyy, face_z), M.YELLOW_WOOL)
    # Scroll vines (卷草纹): one curl mirrored to all four corners (x' = 1700-x, y' = 19-y).
    for vx, vy in ((836, 5), (835, 6), (834, 6), (833, 5)):
        add_fill(fills, f"jingjiao vine bl {vx},{vy}", (vx, vy, face_z), (vx, vy, face_z), AZALEA_LEAVES)
        add_fill(fills, f"jingjiao vine br {1700 - vx},{vy}", (1700 - vx, vy, face_z),
                 (1700 - vx, vy, face_z), AZALEA_LEAVES)
        add_fill(fills, f"jingjiao vine tl {vx},{19 - vy}", (vx, 19 - vy, face_z), (vx, 19 - vy, face_z), AZALEA_LEAVES)
        add_fill(fills, f"jingjiao vine tr {1700 - vx},{19 - vy}", (1700 - vx, 19 - vy, face_z),
                 (1700 - vx, 19 - vy, face_z), AZALEA_LEAVES)

    # ------------------------------------------------------------------
    # 5. Chapel (礼拜小堂) at the north end: white-stone walls, timber
    #    trusses, overhanging gable roof (悬山顶), round east window and a
    #    small gold cross on the door lintel.
    # ------------------------------------------------------------------
    add_hollow_box(fills, "jingjiao chapel", CHAPEL_X1, 5, CHAPEL_Z1, CHAPEL_X2, 13, CHAPEL_Z2, M.QUARTZ, thickness=1)
    add_fill(fills, "jingjiao chapel door", (844, 6, CHAPEL_Z2), (856, 9, CHAPEL_Z2), M.AIR)
    add_fill(fills, "jingjiao chapel lintel cross v", (850, 10, CHAPEL_Z2), (850, 12, CHAPEL_Z2), M.GOLD)
    add_fill(fills, "jingjiao chapel lintel cross h", (849, 11, CHAPEL_Z2), (851, 11, CHAPEL_Z2), M.GOLD)
    # Round east window (东向圆窗): glass disc radius 2 on the gable wall.
    for wdy in range(-2, 3):
        for wdz in range(-2, 3):
            if wdy * wdy + wdz * wdz <= 4:
                add_fill(fills, f"jingjiao chapel window {wdy},{wdz}",
                         (CHAPEL_X2, 9 + wdy, 3196 + wdz), (CHAPEL_X2, 9 + wdy, 3196 + wdz), M.GLASS)
    # Timber trusses (木桁架) inside both gable ends.
    for truss_x in (824, 876):
        add_fill(fills, f"jingjiao chapel truss king {truss_x}", (truss_x, 9, 3196), (truss_x, 12, 3196), M.LOG)
        add_fill(fills, f"jingjiao chapel truss post n {truss_x}", (truss_x, 10, 3188), (truss_x, 12, 3188), M.LOG)
        add_fill(fills, f"jingjiao chapel truss post s {truss_x}", (truss_x, 10, 3204), (truss_x, 12, 3204), M.LOG)
        add_fill(fills, f"jingjiao chapel truss collar {truss_x}", (truss_x, 12, 3189), (truss_x, 12, 3203), M.LOG)
    # Overhanging gable roof (悬山顶), ridge east-west so the gables carry
    # the round window and the finials.
    add_ridge_roof(fills, "jingjiao chapel roof", 818, 3169, 882, 3223, 14, layers=3,
                   ridge_axis="x", roof_block=M.ROOF_GREEN)
    # Interior: stone altar with a gold cross, plank benches, glow lamps.
    add_fill(fills, "jingjiao chapel altar", (870, 6, 3192), (876, 7, 3200), M.SMOOTH)
    add_fill(fills, "jingjiao chapel altar cross v", (874, 8, 3196), (874, 9, 3196), M.GOLD)
    add_fill(fills, "jingjiao chapel altar cross h", (873, 9, 3196), (875, 9, 3196), M.GOLD)
    add_fill(fills, "jingjiao chapel bench n", (838, 6, 3184), (848, 6, 3185), M.WOOD)
    add_fill(fills, "jingjiao chapel bench s", (838, 6, 3207), (848, 6, 3208), M.WOOD)
    add_fill(fills, "jingjiao chapel lamp n", (828, 12, 3180), (828, 12, 3180), M.SEA_LANTERN)
    add_fill(fills, "jingjiao chapel lamp s", (872, 12, 3212), (872, 12, 3212), M.SEA_LANTERN)
    # Door lantern posts on the forecourt.
    for dlx in (836, 864):
        add_fill(fills, f"jingjiao chapel door post {dlx}", (dlx, 5, 3222), (dlx, 9, 3222), M.LOG)
        add_fill(fills, f"jingjiao chapel door lamp {dlx}", (dlx, 10, 3222), (dlx, 10, 3222), M.SEA_LANTERN)

    # ------------------------------------------------------------------
    # 6. Scripture hall (经卷堂) east of the axis: bookshelf scripture
    #    walls, sutra-case chests, lectern translation desk, long table.
    # ------------------------------------------------------------------
    add_fill(fills, "jingjiao hall floor", (890, 4, 3270), (950, 4, 3320), M.SMOOTH)
    add_hollow_box(fills, "jingjiao hall", HALL_X1, 5, HALL_Z1, HALL_X2, 12, HALL_Z2, M.RED_WALL, thickness=1)
    add_fill(fills, "jingjiao hall door", (HALL_X1, 6, 3288), (HALL_X1, 9, 3300), M.AIR)
    add_fill(fills, "jingjiao hall window n", (900, 7, HALL_Z1), (940, 9, HALL_Z1), M.GLASS)
    add_fill(fills, "jingjiao hall window s", (900, 7, HALL_Z2), (940, 9, HALL_Z2), M.GLASS)
    # Bookshelf scripture walls (经架墙) along the north and east interior.
    add_fill(fills, "jingjiao hall shelf n", (894, 6, 3273), (946, 10, 3274), BOOKSHELF)
    add_fill(fills, "jingjiao hall shelf e", (946, 6, 3275), (947, 10, 3316), BOOKSHELF)
    # Sutra-case cabinet (经匣柜): a row of chests along the south wall.
    for chx in (900, 904, 908, 912, 916, 920):
        add_fill(fills, f"jingjiao hall chest {chx}", (chx, 6, 3316), (chx, 6, 3316), CHEST)
    # Long table (长桌) and lectern translation desk (译经案).
    add_fill(fills, "jingjiao hall table", (898, 6, 3296), (914, 6, 3298), M.WOOD)
    add_fill(fills, "jingjiao hall lectern", (906, 7, 3297), (906, 7, 3297), LECTERN)
    add_fill(fills, "jingjiao hall lamp", (920, 11, 3295), (920, 11, 3295), M.SEA_LANTERN)
    # Open west porch towards the axis.
    for ppx, ppz in ((888, 3290), (888, 3298)):
        add_fill(fills, f"jingjiao hall porch col {ppz}", (ppx, 4, ppz), (ppx, 9, ppz), M.LOG)
        add_fill(fills, f"jingjiao hall porch lamp {ppz}", (ppx, 10, ppz), (ppx, 10, ppz), M.SEA_LANTERN)
    add_ridge_roof(fills, "jingjiao hall roof", 889, 3269, 951, 3321, 13, layers=2,
                   ridge_axis="z", roof_block=M.ROOF_BLUE)

    # ------------------------------------------------------------------
    # 7. Missionary graveyard (传教士墓园) west of the axis: fenced plot
    #    with nine small steles in two diagonal ranks, two with crosses.
    # ------------------------------------------------------------------
    add_outline(fills, "jingjiao grave fence", GRAVE_X1, GRAVE_Z1, GRAVE_X2, GRAVE_Z2, 4, 5, M.FENCE, thickness=1)
    add_fill(fills, "jingjiao grave gate", (GRAVE_X2, 4, 3232), (GRAVE_X2, 5, 3238), M.AIR)
    rank_a = [(764, 3252), (773, 3245), (782, 3238), (791, 3231), (800, 3224)]
    rank_b = [(768, 3238), (777, 3231), (786, 3224), (795, 3217)]
    for gi, (gx, gz) in enumerate(rank_a + rank_b):
        _missionary_stele(fills, f"jingjiao grave stele {gi}", gx, gz, with_cross=(gi in (0, 5)))

    # ------------------------------------------------------------------
    # 8. Silk Road caravaneer rest stop outside the south gate: water
    #    trough, hitching posts, half-open thatched lean-to.
    # ------------------------------------------------------------------
    add_fill(fills, "jingjiao trough", (754, 4, 3430), (768, 5, 3436), M.SMOOTH)
    add_fill(fills, "jingjiao trough water", (756, 5, 3432), (766, 5, 3434), M.WATER)
    add_fill(fills, "jingjiao hitch post a", (750, 4, 3430), (750, 8, 3430), M.FENCE)
    add_fill(fills, "jingjiao hitch post b", (750, 4, 3436), (750, 8, 3436), M.FENCE)
    add_fill(fills, "jingjiao shed floor", (703, 4, 3425), (721, 4, 3443), M.SMOOTH)
    for shx, shz in ((704, 3426), (704, 3442), (720, 3426), (720, 3442)):
        add_fill(fills, f"jingjiao shed post {shx},{shz}", (shx, 5, shz), (shx, 8, shz), M.LOG)
    add_fill(fills, "jingjiao shed thatch low", (702, 9, 3424), (722, 9, 3444), M.YELLOW_WOOL)
    add_fill(fills, "jingjiao shed thatch high", (702, 10, 3424), (712, 10, 3444), M.YELLOW_WOOL)

    # ------------------------------------------------------------------
    # 9. Ink pool (墨池) with a stone rim, cypress rows, lantern causeway.
    # ------------------------------------------------------------------
    add_pool(fills, "jingjiao ink pool", POOL_X1, POOL_Z1, POOL_X2, POOL_Z2, 4, depth=1)
    add_fill(fills, "jingjiao ink pool glow", (914, 3, 3365), (914, 3, 3365), M.SEA_LANTERN)
    add_outline(fills, "jingjiao ink pool rim", POOL_X1 - 2, POOL_Z1 - 2, POOL_X2 + 2, POOL_Z2 + 2,
                4, 4, M.STONE, thickness=1)
    # Cypress rows flanking the causeway plus corner and court pines.
    for tx, tz in [(828, 3402), (872, 3402), (828, 3374), (872, 3374), (828, 3346), (872, 3346),
                   (756, 3196), (944, 3196), (752, 3268), (944, 3400), (816, 3242), (884, 3242),
                   (762, 3218), (798, 3250)]:
        add_tree(fills, f"jingjiao cypress {tx},{tz}", tx, tz, 4, height=8, spread=2)
    # Lantern-lined causeway (灯柱甬道).
    add_lantern_line(fills, "jingjiao path lanterns w", 834, 3344, 834, 3404, 4, every=30)
    add_lantern_line(fills, "jingjiao path lanterns e", 866, 3344, 866, 3404, 4, every=30)


def main() -> None:
    run_builder(build_jingjiao_bei_3d, "jingjiao_bei_3d")


if __name__ == "__main__":
    main()
