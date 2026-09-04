from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    Fill,
    Materials as M,
    add_cantilevered_floor,
    add_fill,
    add_hollow_box,
    add_lantern_line,
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
Bangyuan - Examination Hall and Result List Wall 3D (贡院·放榜墙) - the
imperial examination compound of the south-east Imperial City, where the
triennial candidates sat in the sealed session cells and where the "name on
the golden list" (金榜题名) scene unfolds, one line of inheritance from the
Qujiang Apricot Garden feast (曲江杏园探花宴) and the Wild Goose Pagoda
inscriptions (雁塔题名).

Location in Chang'an city local coordinates:
    South-east Imperial City plot: x 3350..3680, z 650..860 (hard bounds).
    The Medical Court (太医署, x 3550..3850) starts at z 900 further south,
    so nothing may cross z 860; ward housing to the east may be overwritten.
    Ground level y 0..4, main structures rise from y 5.

Distinctive features:
    - Session-cell ranks (号舍阵): two ranks of six 3-wide sealed cells with
      half-height plank bed-platforms along razor-thin 2-block lanes, each
      lane mouth marked by a small timber memorial arch
    - Mingyuan Watchtower (明远楼) at the centre: two red storeys, a
      cantilevered ring gallery with fence railings and a gilded pyramid
      roof (攒尖金顶) supervising the whole compound
    - The Result List Wall (放榜墙): a 139x14 yellow-list face framed in
      dark timber, seven rows of twelve black "name" strips, a gilded
      plaque on top, and a stepped stone dais with railing in front
    - Two list-viewing shelters with stone benches, plus the good-news
      shelter (报喜棚) with red-silk drapes and a gilded gong on a fence frame
    - Dragon Gate arch (龙门) inside the gate: twin sky-piercing columns, a
      gold "龙门" plaque and leaping blue-wool carp with gold scales
    - Transcription office (誊录所) in the east wing: a small walled
      courtyard with desk rows, lecterns, bookshelves and chest archives
    - Six apricot-yellow banners, a lantern-lined causeway and two cypress ranks
"""

# ---------------------------------------------------------------------------
# Site constants (local Chang'an coordinates; world = +9000/+64/+9000 via lib).
# ---------------------------------------------------------------------------
SITE_X1, SITE_Z1 = 3350, 650
SITE_X2, SITE_Z2 = 3680, 860  # hard southern limit: Taiyiyuan starts at z 900

# Central north-south causeway through the south gate.
AXIS_X = 3515
PATH_X1, PATH_X2 = 3506, 3524

# Mingyuan Watchtower (明远楼) at the centre of the compound.
TWR_CX, TWR_CZ = 3515, 755

# Result List Wall (放榜墙) against the north wall.
LWALL_X1, LWALL_X2 = 3440, 3590

# Session-cell ranks (号舍阵): back walls of the west and east ranks.
CELL_W_BACK, CELL_E_BACK = 3410, 3603
CELL_ROW_Z1 = 694

# Viewing shelters (观榜棚) and good-news shelter (报喜棚).
SHED_A_X1, SHED_A_Z1 = 3468, 678
SHED_A_X2, SHED_A_Z2 = 3498, 698
SHED_B_X1, SHED_B_Z1 = 3532, 678
SHED_B_X2, SHED_B_Z2 = 3562, 698
GOOD_X1, GOOD_Z1 = 3604, 672
GOOD_X2, GOOD_Z2 = 3644, 692

# Transcription office courtyard (誊录所), east wing.
TRANS_X1, TRANS_Z1 = 3625, 700
TRANS_X2, TRANS_Z2 = 3674, 780


def _exam_cell(fills: list[Fill], label: str, x_back: int, z1: int, open_side: str) -> None:
    """One sealed session cell: three stone walls, one open side, a
    half-height plank bed-platform and a flat plank roof."""
    d = 1 if open_side == "e" else -1
    lo, hi = x_back, x_back + 4 * d
    add_fill(fills, f"{label} wall back", (x_back, 5, z1), (x_back, 10, z1 + 2), M.STONE)
    add_fill(fills, f"{label} wall n", (x_back + d, 5, z1), (x_back + 4 * d, 10, z1), M.STONE)
    add_fill(fills, f"{label} wall s", (x_back + d, 5, z1 + 2), (x_back + 4 * d, 10, z1 + 2), M.STONE)
    add_fill(fills, f"{label} roof", (lo, 11, z1), (hi, 11, z1 + 2), M.WOOD)
    add_fill(fills, f"{label} bed", (x_back + d, 5, z1 + 1), (x_back + 3 * d, 5, z1 + 1), M.WOOD)


def _viewing_shed(fills: list[Fill], label: str, x1: int, z1: int, x2: int, z2: int) -> None:
    """One open list-viewing shelter: four posts, stone benches, dark roof."""
    add_fill(fills, f"{label} paving", (x1, 4, z1), (x2, 4, z2), M.SMOOTH)
    for i, (px, pz) in enumerate(((x1, z1), (x2, z1), (x1, z2), (x2, z2))):
        add_fill(fills, f"{label} post {i}", (px, 5, pz), (px, 10, pz), M.LOG)
    add_fill(fills, f"{label} bench n", (x1 + 4, 5, z1 + 2), (x2 - 4, 5, z1 + 3), M.SMOOTH)
    add_fill(fills, f"{label} bench s", (x1 + 4, 5, z2 - 3), (x2 - 4, 5, z2 - 2), M.SMOOTH)
    add_ridge_roof(fills, f"{label} roof", x1 - 2, z1 - 2, x2 + 2, z2 + 2, 11, layers=1,
                   ridge_axis="x", roof_block=M.ROOF_DARK)


def _banner(fills: list[Fill], label: str, x: int, z: int) -> None:
    """One apricot-yellow banner: log pole and a 3x3 yellow wool cloth."""
    add_fill(fills, f"{label} pole", (x, 5, z), (x, 13, z), M.LOG)
    add_fill(fills, f"{label} cloth", (x + 1, 11, z), (x + 3, 13, z), M.YELLOW_WOOL)


def build_bangyuan_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site grading: stone base y0..1, lawn y2..3, grey-white perimeter
    #    wall with andesite coping and a south "贡院" gate tower.
    # ------------------------------------------------------------------
    add_fill(fills, "bangyuan foundation", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "bangyuan lawn", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)
    add_fill(fills, "bangyuan wall n", (SITE_X1, 4, SITE_Z1), (SITE_X2, 9, SITE_Z1 + 1), M.WHITE_TERRACOTTA)
    add_fill(fills, "bangyuan wall s", (SITE_X1, 4, SITE_Z2 - 1), (SITE_X2, 9, SITE_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "bangyuan wall w", (SITE_X1, 4, SITE_Z1), (SITE_X1 + 1, 9, SITE_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "bangyuan wall e", (SITE_X2 - 1, 4, SITE_Z1), (SITE_X2, 9, SITE_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "bangyuan coping n", (SITE_X1, 10, SITE_Z1), (SITE_X2, 10, SITE_Z1 + 1), M.ANDESITE)
    add_fill(fills, "bangyuan coping s", (SITE_X1, 10, SITE_Z2 - 1), (SITE_X2, 10, SITE_Z2), M.ANDESITE)
    add_fill(fills, "bangyuan coping w", (SITE_X1, 10, SITE_Z1), (SITE_X1 + 1, 10, SITE_Z2), M.ANDESITE)
    add_fill(fills, "bangyuan coping e", (SITE_X2 - 1, 10, SITE_Z1), (SITE_X2, 10, SITE_Z2), M.ANDESITE)
    # South gate: opening, gold threshold, inner landing.
    add_fill(fills, "bangyuan gate opening", (3495, 4, SITE_Z2 - 2), (3535, 9, SITE_Z2), M.AIR)
    add_fill(fills, "bangyuan gate landing", (3493, 4, 850), (3537, 4, 857), M.SMOOTH)
    add_fill(fills, "bangyuan gate threshold", (3500, 4, 857), (3530, 4, 857), M.GOLD)
    # Gate tower (大门楼) astride the opening, gold "贡院" plaque on the face.
    add_fill(fills, "bangyuan gate deck", (3490, 10, 852), (3540, 10, 859), M.WOOD)
    add_fill(fills, "bangyuan gate body", (3490, 11, 852), (3540, 13, 859), M.RED_WALL)
    add_fill(fills, "bangyuan gate plaque", (3505, 11, SITE_Z2), (3525, 13, SITE_Z2), M.GOLD)
    add_ridge_roof(fills, "bangyuan gate roof", 3488, 850, 3542, 857, 14, layers=1,
                   ridge_axis="x", roof_block=M.ROOF_GREEN)

    # ------------------------------------------------------------------
    # 2. Axial stone causeway from the gate north to the tower and wall.
    # ------------------------------------------------------------------
    add_fill(fills, "bangyuan causeway", (PATH_X1, 4, 658), (PATH_X2, 4, 850), M.SMOOTH)

    # ------------------------------------------------------------------
    # 3. Result List Wall (放榜墙): dark timber backing, yellow list face,
    #    frame, gilded plaque, and 7 rows x 12 black "name" strips, with a
    #    stepped stone dais and side railings in front.
    # ------------------------------------------------------------------
    add_fill(fills, "bangyuan list wall body", (LWALL_X1, 4, 654), (LWALL_X2, 18, 657), M.DARK)
    add_fill(fills, "bangyuan list face", (3446, 5, 658), (3584, 18, 658), M.YELLOW_WOOL)
    add_fill(fills, "bangyuan list frame top", (3443, 19, 656), (3587, 19, 658), M.LOG)
    add_fill(fills, "bangyuan list frame w", (3443, 4, 657), (3444, 19, 658), M.LOG)
    add_fill(fills, "bangyuan list frame e", (3586, 4, 657), (3587, 19, 658), M.LOG)
    add_fill(fills, "bangyuan list plaque", (3490, 20, 655), (3540, 22, 657), M.GOLD)
    for r, ry in enumerate((6, 7, 9, 10, 12, 13, 15)):
        for c in range(12):
            sx = 3450 + c * 11
            add_fill(fills, f"bangyuan list strip r{r} c{c}", (sx, ry, 658), (sx + 6, ry, 658), M.BLACK_WOOL)
    add_fill(fills, "bangyuan list dais", (3455, 5, 659), (3575, 5, 665), M.SMOOTH)
    add_fill(fills, "bangyuan list dais step", (3455, 4, 666), (3575, 4, 667), M.SMOOTH)
    add_fill(fills, "bangyuan list dais rail w", (3455, 6, 659), (3455, 7, 665), M.FENCE)
    add_fill(fills, "bangyuan list dais rail e", (3575, 6, 659), (3575, 7, 665), M.FENCE)

    # ------------------------------------------------------------------
    # 4. Two list-viewing shelters (观榜棚) with stone benches.
    # ------------------------------------------------------------------
    _viewing_shed(fills, "bangyuan viewing shed a", SHED_A_X1, SHED_A_Z1, SHED_A_X2, SHED_A_Z2)
    _viewing_shed(fills, "bangyuan viewing shed b", SHED_B_X1, SHED_B_Z1, SHED_B_X2, SHED_B_Z2)

    # ------------------------------------------------------------------
    # 5. Good-news shelter (报喜棚) east of the wall: red-silk drapes and a
    #    gilded gong hung on a fence frame.
    # ------------------------------------------------------------------
    add_fill(fills, "bangyuan good news roof", (GOOD_X1 - 2, 12, GOOD_Z1 - 2), (GOOD_X2 + 2, 12, GOOD_Z2 + 2), M.WOOD)
    for i, (px, pz) in enumerate((
        (GOOD_X1, GOOD_Z1), (GOOD_X2, GOOD_Z1), (GOOD_X1, GOOD_Z2), (GOOD_X2, GOOD_Z2),
    )):
        add_fill(fills, f"bangyuan good news post {i}", (px, 5, pz), (px, 11, pz), M.LOG)
        add_fill(fills, f"bangyuan good news silk {i}", (px, 8, pz), (px, 11, pz), M.RED_WOOL)
    add_fill(fills, "bangyuan good news ridge silk", (3610, 13, 682), (3638, 13, 683), M.RED_WOOL)
    add_fill(fills, "bangyuan good news banner", (3610, 9, GOOD_Z2 + 3), (3638, 11, GOOD_Z2 + 3), M.RED_WOOL)
    add_fill(fills, "bangyuan good news bench", (3612, 5, 686), (3636, 5, 687), M.SMOOTH)
    # gong (锣): fence posts, crossbar and a gilded gong face.
    add_fill(fills, "bangyuan gong post w", (3626, 5, 674), (3626, 10, 674), M.FENCE)
    add_fill(fills, "bangyuan gong post e", (3628, 5, 674), (3628, 10, 674), M.FENCE)
    add_fill(fills, "bangyuan gong bar", (3626, 10, 674), (3628, 10, 674), M.WOOD)
    add_fill(fills, "bangyuan gong face", (3627, 7, 674), (3627, 9, 674), M.GOLD)

    # ------------------------------------------------------------------
    # 6. Mingyuan Watchtower (明远楼): stepped platform, two red storeys,
    #    lower eave ring, ring gallery with railings, gilded pyramid roof.
    # ------------------------------------------------------------------
    add_platform_with_steps(fills, "bangyuan tower platform", 3490, 730, 3540, 780, 4,
                            [(2, 0, M.STONE), (1, 4, M.SMOOTH)])
    add_fill(fills, "bangyuan tower step s", (3500, 5, 781), (3530, 5, 782), M.SMOOTH)
    add_fill(fills, "bangyuan tower step n", (3500, 5, 728), (3530, 5, 729), M.SMOOTH)
    # Storey 1 (y 7..15).
    add_hollow_box(fills, "bangyuan tower body1", 3496, 7, 736, 3534, 15, 774, M.RED_WALL, thickness=1)
    for i, (px, pz) in enumerate(((3496, 736), (3533, 736), (3496, 773), (3533, 773),
                                  (3514, 736), (3514, 773), (3496, 754), (3533, 754))):
        add_fill(fills, f"bangyuan tower body1 col {i}", (px, 7, pz), (px + 1, 15, pz + 1), M.LOG)
    add_fill(fills, "bangyuan tower door s", (3508, 7, 774), (3522, 11, 774), M.AIR)
    add_fill(fills, "bangyuan tower window n", (3505, 9, 736), (3525, 11, 736), M.GLASS)
    add_fill(fills, "bangyuan tower window w", (3496, 9, 745), (3496, 11, 765), M.GLASS)
    add_fill(fills, "bangyuan tower window e", (3534, 9, 745), (3534, 11, 765), M.GLASS)
    add_fill(fills, "bangyuan tower lamp sw", (3508, 8, 748), (3508, 8, 748), M.SEA_LANTERN)
    add_fill(fills, "bangyuan tower lamp ne", (3522, 8, 762), (3522, 8, 762), M.SEA_LANTERN)
    add_spiral_stair(fills, "bangyuan tower stair1", TWR_CX, TWR_CZ, radius=5, y1=7, y2=14, block=M.SMOOTH)
    # Lower eave ring (重檐下檐).
    add_pagoda_eave(fills, "bangyuan tower lower eave", TWR_CX, TWR_CZ, radius=19, y=15,
                    overhang=3, roof_block=M.ROOF_GREEN)
    # Storey 2 (y 16..22) with its cantilevered ring gallery and railing.
    add_hollow_box(fills, "bangyuan tower body2", 3502, 16, 742, 3528, 22, 768, M.RED_WALL, thickness=1)
    for i, (px, pz) in enumerate(((3502, 742), (3527, 742), (3502, 767), (3527, 767),
                                  (3514, 742), (3514, 767), (3502, 754), (3527, 754))):
        add_fill(fills, f"bangyuan tower body2 col {i}", (px, 16, pz), (px + 1, 22, pz + 1), M.LOG)
    add_fill(fills, "bangyuan tower window2 n", (3508, 18, 742), (3522, 20, 742), M.GLASS)
    add_fill(fills, "bangyuan tower window2 s", (3508, 18, 768), (3522, 20, 768), M.GLASS)
    add_spiral_stair(fills, "bangyuan tower stair2", TWR_CX, TWR_CZ, radius=4, y1=16, y2=23, block=M.SMOOTH)
    add_cantilevered_floor(fills, "bangyuan tower gallery", 3502, 742, 3528, 768, y=23, overhang=3, block=M.WOOD)
    add_outline(fills, "bangyuan tower gallery rail", 3502, 742, 3528, 768, 24, 24, M.FENCE, thickness=1)
    # Gilded pyramid roof (攒尖金顶).
    add_pyramid_roof(fills, "bangyuan tower roof", TWR_CX, TWR_CZ, radius=14, y=24,
                     roof_block=M.ROOF_GREEN, apex_block=M.GOLD)

    # ------------------------------------------------------------------
    # 7. Session-cell ranks (号舍阵): six 3-wide cells per rank along
    #    razor-thin lanes, each lane mouth marked by a small arch.
    # ------------------------------------------------------------------
    add_fill(fills, "bangyuan cell rank w floor", (CELL_W_BACK, 4, CELL_ROW_Z1),
             (CELL_W_BACK + 4, 4, CELL_ROW_Z1 + 27), M.STONE)
    add_fill(fills, "bangyuan cell rank e floor", (CELL_E_BACK - 4, 4, CELL_ROW_Z1),
             (CELL_E_BACK, 4, CELL_ROW_Z1 + 27), M.STONE)
    for k in range(6):
        cz = CELL_ROW_Z1 + k * 5
        _exam_cell(fills, f"bangyuan cell w{k}", CELL_W_BACK, cz, open_side="e")
        _exam_cell(fills, f"bangyuan cell e{k}", CELL_E_BACK, cz, open_side="w")
    add_fill(fills, "bangyuan lane w paving", (3415, 4, 692), (3416, 4, 742), M.SMOOTH)
    add_fill(fills, "bangyuan lane e paving", (3597, 4, 692), (3598, 4, 742), M.SMOOTH)
    # Small memorial arches at the two lane mouths (south ends).
    for tag, px1, px2 in (("w", 3414, 3417), ("e", 3596, 3599)):
        add_fill(fills, f"bangyuan lane arch {tag} post w", (px1, 5, 741), (px1, 10, 741), M.LOG)
        add_fill(fills, f"bangyuan lane arch {tag} post e", (px2, 5, 741), (px2, 10, 741), M.LOG)
        add_fill(fills, f"bangyuan lane arch {tag} beam", (px1, 11, 741), (px2, 11, 741), M.WOOD)
        add_fill(fills, f"bangyuan lane arch {tag} eave", (px1 - 1, 12, 740), (px2 + 1, 12, 742), M.ROOF_DARK)
        add_fill(fills, f"bangyuan lane arch {tag} plaque", (px1 + 1, 13, 741), (px2 - 1, 13, 741), M.GOLD)

    # ------------------------------------------------------------------
    # 8. Dragon Gate arch (龙门) inside the entrance: sky-piercing twin
    #    columns, gold "龙门" plaque, leaping blue carp with gold scales.
    # ------------------------------------------------------------------
    add_fill(fills, "bangyuan dragon gate col w", (3508, 5, 814), (3509, 17, 815), M.RED_WALL)
    add_fill(fills, "bangyuan dragon gate col e", (3521, 5, 814), (3522, 17, 815), M.RED_WALL)
    add_fill(fills, "bangyuan dragon gate beam", (3506, 14, 814), (3524, 15, 815), M.WOOD)
    add_fill(fills, "bangyuan dragon gate plaque", (3511, 16, 816), (3519, 17, 816), M.GOLD)
    for tag, cx1 in (("w", 3508), ("e", 3521)):
        add_fill(fills, f"bangyuan dragon gate fish body {tag}", (cx1, 18, 814), (cx1 + 1, 18, 815), M.BLUE_WOOL)
        add_fill(fills, f"bangyuan dragon gate fish leap {tag}", (cx1, 19, 815), (cx1 + 1, 20, 815), M.BLUE_WOOL)
        add_fill(fills, f"bangyuan dragon gate fish scale {tag}", (cx1, 19, 814), (cx1 + 1, 19, 814), M.GOLD)

    # ------------------------------------------------------------------
    # 9. Transcription office (誊录所) in the east wing: walled courtyard,
    #    hall with bookshelves, desk rows, lecterns and chest archives.
    # ------------------------------------------------------------------
    add_fill(fills, "bangyuan trans wall n", (TRANS_X1, 5, TRANS_Z1), (TRANS_X2, 9, TRANS_Z1), M.WHITE_TERRACOTTA)
    add_fill(fills, "bangyuan trans wall s", (TRANS_X1, 5, TRANS_Z2), (TRANS_X2, 9, TRANS_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "bangyuan trans wall w", (TRANS_X1, 5, TRANS_Z1), (TRANS_X1, 9, TRANS_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "bangyuan trans wall e", (TRANS_X2, 5, TRANS_Z1), (TRANS_X2, 9, TRANS_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "bangyuan trans coping n", (TRANS_X1, 10, TRANS_Z1), (TRANS_X2, 10, TRANS_Z1), M.ANDESITE)
    add_fill(fills, "bangyuan trans coping s", (TRANS_X1, 10, TRANS_Z2), (TRANS_X2, 10, TRANS_Z2), M.ANDESITE)
    add_fill(fills, "bangyuan trans coping w", (TRANS_X1, 10, TRANS_Z1), (TRANS_X1, 10, TRANS_Z2), M.ANDESITE)
    add_fill(fills, "bangyuan trans coping e", (TRANS_X2, 10, TRANS_Z1), (TRANS_X2, 10, TRANS_Z2), M.ANDESITE)
    add_fill(fills, "bangyuan trans gate", (TRANS_X1, 5, 735), (TRANS_X1, 9, 755), M.AIR)
    add_fill(fills, "bangyuan trans gate lintel", (TRANS_X1, 10, 734), (TRANS_X1, 10, 756), M.GOLD)
    add_fill(fills, "bangyuan trans paving", (TRANS_X1 + 1, 4, TRANS_Z1 + 1), (TRANS_X2 - 1, 4, TRANS_Z2 - 1), M.SMOOTH)
    # Office hall.
    add_hollow_box(fills, "bangyuan trans hall", 3642, 5, 712, 3668, 11, 742, M.RED_WALL, thickness=1)
    add_fill(fills, "bangyuan trans hall door", (3642, 5, 722), (3642, 9, 732), M.AIR)
    add_fill(fills, "bangyuan trans hall window", (3650, 7, 742), (3662, 9, 742), M.GLASS)
    add_fill(fills, "bangyuan trans shelf", (3644, 5, 714), (3666, 9, 715), "minecraft:bookshelf")
    add_fill(fills, "bangyuan trans desk a", (3646, 5, 724), (3664, 5, 724), M.WOOD)
    add_fill(fills, "bangyuan trans desk b", (3646, 5, 731), (3664, 5, 731), M.WOOD)
    add_fill(fills, "bangyuan trans lectern a", (3649, 6, 724), (3649, 6, 724), "minecraft:lectern")
    add_fill(fills, "bangyuan trans lectern b", (3657, 6, 731), (3657, 6, 731), "minecraft:lectern")
    add_fill(fills, "bangyuan trans chests", (3646, 5, 738), (3664, 5, 738), "minecraft:chest")
    add_fill(fills, "bangyuan trans barrel a", (3666, 5, 717), (3666, 5, 717), "minecraft:barrel")
    add_fill(fills, "bangyuan trans barrel b", (3666, 5, 719), (3666, 5, 719), "minecraft:barrel")
    add_fill(fills, "bangyuan trans lamp", (3655, 10, 727), (3655, 10, 727), M.SEA_LANTERN)
    add_ridge_roof(fills, "bangyuan trans roof", 3640, 710, 3670, 746, 12, layers=2,
                   ridge_axis="z", roof_block=M.ROOF_GREEN)

    # ------------------------------------------------------------------
    # 10. Six apricot-yellow banners, lantern-lined causeway, cypresses.
    # ------------------------------------------------------------------
    for i, fz in enumerate((802, 824, 846)):
        _banner(fills, f"bangyuan banner w{i}", 3496, fz)
        _banner(fills, f"bangyuan banner e{i}", 3534, fz)
    add_lantern_line(fills, "bangyuan path lanterns w", 3502, 800, 3502, 852, 4, every=16)
    add_lantern_line(fills, "bangyuan path lanterns e", 3528, 800, 3528, 852, 4, every=16)
    for tz in (706, 736, 766, 796):
        add_tree(fills, f"bangyuan cypress w {tz}", 3470, tz, 4, height=7, spread=2)
        add_tree(fills, f"bangyuan cypress e {tz}", 3560, tz, 4, height=7, spread=2)


def main() -> None:
    run_builder(build_bangyuan_3d, "bangyuan_3d")


if __name__ == "__main__":
    main()
