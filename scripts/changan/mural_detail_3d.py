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
    add_pixel_mural,
    run_builder,
)


"""
Mural Detail 3D (唐长安·巨幅像素壁画叠加：敦煌飞天 / 青绿山水 / 说法图 / 长安贡赋图)
Chang'an Mural Detail 3D: four large hand-painted pixel murals overlaid on
existing landmark walls via lib.add_pixel_mural.

Additive only: every mural hangs in a vertical plane exactly ONE block
outside its host wall's outer surface (mural z or x = wall face +/- 1), so
no wall block is ever replaced.  Sky/ground colour bands are laid down
first as thin plane fills, then the character art overpaints them ('.'
pixels leave the band showing), so a 24x14 painting costs ~100 fills
instead of 336 and the whole module stays within the ~250-450 fill budget.

Wall sources and coordinate derivation (local Chang'an coordinates):

Mural 1 - Dunhuang Feitian (敦煌飞天壁画, 24x14, axis='z')
    palace_hanyuan_dian.py: the hall body is
    add_hollow_box(2660, 9, 5180 .. 3340, 57, 5480, thickness=2), so the
    EAST outer face is x=3340.  That face is blank (windows and the main
    door are cut into the south facade only).  Mural plane x = 3340+1 =
    3341; 24 pixels along z centred on the wall mid z=(5180+5480)/2=5330
    -> z 5318..5341; top row y=44, so the panel spans y 31..44 - above
    the Qifeng link corridor (y 13..16, z 5324..5336) and far below the
    dougong bracket layer / lower eave (y>=58).  flip=True so the design
    reads left-to-right for a viewer on the east terrace looking west.

Mural 2 - Blue-green Landscape (青绿山水壁画, 24x12, axis='x')
    temple_qinglong.py: Buddha hall is
    add_hollow_box(5005, 1, 1015 .. 5095, 28, 1085, thickness=2); its
    courtyard-facing gable face is z=1015 and carries no openings.
    Mural plane z = 1015-1 = 1014; 24 pixels along x centred on
    (5005+5095)/2=5050 -> x 5038..5061; top row y=24 -> rows y 13..24,
    below the ridge-roof volume (y>=29) and clear of the pond (z<=1010).

Mural 3 - Sutra Preaching Scene (说法图壁画, 20x12, axis='x')
    temple_daxingshan.py: Mahavira hall is
    add_hollow_box(1405, 1, 2445 .. 1495, 30, 2515, thickness=2).  Its
    REAR (Z2-side) face z=2515 is completely blank.  Mural plane
    z = 2515+1 = 2516; 20 pixels centred on x=1450 -> x 1440..1459;
    top row y=28 -> rows y 17..28, just under the wall top (y30) and the
    roof pass (y>=31).

Mural 4 - Chang'an Tribute Scroll (长安贡赋图壁画, 24x10, axis='x')
    beilin_3d.py: the precinct south wall ("beilin wall s", z 5148..5150)
    stands only y 4..9 - too short for a 10-row panel - so this pass
    first ADDS a dedicated screen wall (照壁) just outside it: stone
    plinth y 4..5, white-terracotta body y 6..14 at x 1839..1864 /
    z 5153..5154, dark cap y 15 (nothing exists at z>=5151 in the
    source; the gate x 1876..1924 and its tower stay clear).  The mural
    hangs on the screen wall's south face: plane z = 5153-1 = 5152,
    x 1840..1863, top row y=13 -> rows y 4..13.

Each mural is annotated by a small mural stele (壁画碑记: dark seat +
quartz-pillar shaft + gilded cap) standing beside its panel:
    feitian stele (3344, z 5345) on the tier-2 terrace apron (top y 8),
        clear of the Qifeng corridor (z 5324..5336) and hall columns
    shanshui stele (5064, z 1012) beside the panel's east end, clear of
        the pond (z<=1010) and the hall's east wall (x 5094)
    shuofa stele (1435, z 2517) west of the rear-face panel, clear of the
        sutra pavilion (x<=1385) and pagoda (x>=1524)
    gongfu stele (1835, z 5154) west of the new screen wall

Distinctive features:
    - Four full-size character-design grids, one per mural, each with its
      own 8-10 colour wool/terracotta/gold palette (see constants below)
    - Dunhuang apsara: white-skinned flying figure arcing across a
      three-band teal sky, S-curved red + orange ribbons, gold cloud
      puffs, pink petal dots and diamond rosettes pinning all corners
    - Blue-green landscape: pale far peaks, a deep-teal mid ridge band,
      green near hills, blue water with light-blue sparkles, a
      red-columned black-roofed pavilion, three bird flocks, white cloud
      wisps and a gold sun
    - Preaching scene painted straight onto the earth-red hall wall: gold
      Buddha with a yellow flame halo under a yellow canopy with orange
      valances, 2+2 red/cyan attendants, pink/white lotus throne
    - Tribute scroll: black-roofed red gate tower, a gold crenellated
      city-wall line, four coloured banners, three brown camels and a
      horse-drawn cart procession
    - ~420 fills total (one 1x1x1 fill per painted pixel), zero air
      carving anywhere
"""

QUARTZ_PILLAR = "minecraft:quartz_pillar[axis=y]"


# ---------------------------------------------------------------------------
# Mural 1 - Dunhuang Feitian (敦煌飞天), 24 x 14, top row first.
#
# Design sketch: the apsara flies toward the upper-right across a
# three-band teal sky (T deep / L mid / E pale, laid down as base fills).
# Her gold-framed head (K hair, S face, cols 17-18, rows 1-3) arcs down
# through chest and waist to the hips (S, cols 13-14, row 7); one leg
# kicks back up-left (rows 5-8), the other trails down to row 11.  A red
# ribbon sweeps over her head and down the left edge (R), a shorter red
# echo follows it (rows 2-5), and an orange ribbon (O) curls below her
# into a flicked tail at row 12.  Gold cloud puffs (G/Y) and pink petal
# dots (P) drift around her; 3x3 diamond rosettes (Y arms, G heart) pin
# all four corners as 宝相花角饰.
# Legend: K hair  S skin  R red ribbon  O orange ribbon  Y gold light
#         G gold cloud  P petal   T/L/E = sky bands (base fills)
# ---------------------------------------------------------------------------
FEITIAN_ART = [
    ".Y..GY.....RR.......P.Y.",
    "YGY..G...RR..R...KKPSYGY",
    ".Y.....RR...R.R..SSS..Y.",
    ".....RR....R...RSSS.....",
    "....R.....RSSS..SS..GY..",
    "....R..S.R.....SS...G...",
    "..RR....SS.....SS...P.G.",
    "..R.......SS.SSO....P...",
    "............SSSOO.......",
    "............SS...OO.....",
    "..GYG.....SS......OO....",
    ".........S.........OO.Y.",
    "YGY............GY.OO.YGY",
    ".Y.............G......Y.",
]

FEITIAN_PALETTE = {
    "K": "minecraft:black_wool",             # 螺髻发丝 hair
    "S": "minecraft:white_wool",             # 肤白身躯 skin
    "R": "minecraft:red_wool",               # 石红长飘带 red ribbon
    "O": "minecraft:orange_wool",            # 橘黄飘带 orange ribbon
    "Y": "minecraft:yellow_wool",            # 祥云暖光 gold light
    "G": "minecraft:gold_block",             # 金色祥云/花心 gold cloud
    "P": "minecraft:pink_wool",              # 天花落瓣 petals
    "T": "minecraft:cyan_terracotta",        # 青绿天空·深处 deep sky
    "L": "minecraft:light_blue_terracotta",  # 青绿天空·中层 mid sky
    "E": "minecraft:light_gray_terracotta",  # 青绿天空·近地 pale sky
}


# ---------------------------------------------------------------------------
# Mural 2 - Blue-green Landscape (青绿山水), 24 x 12, top row first.
#
# Design sketch: pale silk sky (W band), gold sun (G) upper right, three
# black bird flocks (K) and white cloud wisps (C).  Far peaks (F pale
# blue) rise in rows 2-4 over a full-width far-ridge base row (row 5)
# with two deep-teal mid peaks (M) poking through; a deep-teal mid ridge
# band (M, rows 6-8) carries the green near hills (N, rows 7-8) with a
# black-roofed red-columned pavilion (K/R) on the right shoulder; a green
# shore band (row 9) meets blue water (B band, rows 10-11) flecked with
# light-blue sparkles (V).
# Legend: K roof/birds  R columns  G sun  C cloud  F far peak
#         M mid ridge(band)  N near hill  V sparkle  W/B = sky/water bands
# ---------------------------------------------------------------------------
SHANSHUI_ART = [
    "...KK.....KK.....K......",
    "..........K.....K...GG..",
    "...F..CC.FF.....FF..GG..",
    "..FFF....FFF....FFF.....",
    ".FFFFF..FFFFF..FFFFF....",
    "FFFFFFMMMFFFFMMMFFFFFFFF",
    "................KK......",
    ".NNN..........KKKKKK....",
    "NNNNN..........RKKR.NNNN",
    "........................",
    "...VV.......V.....VV....",
    "........V......V........",
]

SHANSHUI_PALETTE = {
    "K": "minecraft:black_wool",             # 亭顶/飞鸟 roof & birds
    "R": "minecraft:red_wool",               # 亭柱 red columns
    "G": "minecraft:gold_block",             # 旭日 gold sun
    "C": "minecraft:white_wool",             # 留白云气 cloud wisps
    "F": "minecraft:light_blue_terracotta",  # 远山·淡青 far peaks
    "M": "minecraft:cyan_terracotta",        # 中山·深青 mid ridge
    "N": "minecraft:green_wool",             # 近坡·石绿 near hills
    "V": "minecraft:light_blue_wool",        # 水面波光 water sparkle
    "W": "minecraft:white_terracotta",       # 绢底天空 sky band
    "B": "minecraft:blue_wool",              # 近水 water band
}


# ---------------------------------------------------------------------------
# Mural 3 - Sutra Preaching Scene (说法图), 20 x 12, top row first.
# Painted directly on the earth-red hall wall: the red plaster IS the
# mural ground, just like Dunhuang's red-ground preaching scenes.
#
# Design sketch: a yellow canopy (Y, rows 0-1) with orange valance
# tassels (O, rows 1-2) crowns the scene.  The gold Buddha (G) sits
# centred: head row 3, shoulders row 4, torso rows 5-6, lap row 7, legs
# row 8, wrapped in a yellow flame halo (Y diamond, rows 2-4).  Four
# attendants flank him, 2 + 2: inner red-robed (R) and outer cyan-robed
# (C), white faces (S), robes flaring rows 5-8.  A pink/white lotus
# throne (P/W petals, row 9) rests on a grey terracotta base (D, row 10);
# pink lotus buds (P) dot the foreground and flanks.
# Legend: Y canopy/halo  O valance  G Buddha body  S faces  R red robe
#         C cyan robe  P lotus pink  W lotus white  D throne base
# ---------------------------------------------------------------------------
SHUOFA_ART = [
    ".......YYYYYY.......",
    "..GY...YO..OY...YG..",
    "..G...O.YY.O....G...",
    "........YGGY........",
    "....S..YGGGGY..S....",
    "..S.R...GGGG...C.S..",
    "..C.R...GGGG...C.R..",
    ".CCRR..GGGGGG..CCRR.",
    ".CCRR.GGGGGGGG.CCRR.",
    "......PWPWPWPW......",
    "..P....DDDDDD....P..",
    ".....P........P.....",
]

SHUOFA_PALETTE = {
    "Y": "minecraft:yellow_wool",      # 华盖/背光金环 canopy & halo
    "O": "minecraft:orange_wool",      # 垂幔 valance tassels
    "G": "minecraft:gold_block",       # 佛金身 gold body
    "S": "minecraft:white_wool",       # 胁侍肤白 attendant faces
    "R": "minecraft:red_wool",         # 红衣胁侍 red robes
    "C": "minecraft:cyan_wool",        # 青衣胁侍 cyan robes
    "P": "minecraft:pink_wool",        # 莲瓣 pink lotus
    "W": "minecraft:quartz_block",     # 白莲 white lotus
    "D": "minecraft:gray_terracotta",  # 莲台基座 throne base
}


# ---------------------------------------------------------------------------
# Mural 4 - Chang'an Tribute Scroll (长安贡赋图), 24 x 10, top row first.
# Painted on the white face of the new screen wall (照壁) outside the
# Beilin south gate - the white plaster is the scroll's silk ground.
#
# Design sketch: at the left a red gate tower with black triple roof
# (K rows 0-2, R walls rows 3-5, K doorway) anchors a gold crenellated
# city-wall line (G, row 5) running to the right edge; four coloured
# banners (R/O/Y/B, row 2) fly from poles on the wall walk (K, rows 2-3,
# rising from gold crenels G row 4).  Below the wall a tribute caravan
# marches right: three two-hump brown camels (N, cols 8-21) and, in
# front of the gate, a horse-drawn cart (N cargo + K wheels, N horse).
# Legend: K roof/poles/door/wheels  R tower wall/red flag  O orange flag
#         Y yellow flag  B blue flag  N camels/cart/horse  G gold wall
#         D gate platform
# ---------------------------------------------------------------------------
GONGFU_ART = [
    "..KKK...................",
    ".KKKKK..................",
    "KKKKKKK..KRR.KOO.KYY.KBB",
    "..RRR....K...K...K...K..",
    "..RKR....G...G...G...G..",
    ".DRRRGGGGGGGGGGGGGGGGGGG",
    "..NN..N.NN.N.NN.N.NN.N..",
    "..NNNNN.NNNN.NNNN.NNNN..",
    "..K.KNN.N..N.N..N.N..N..",
    "........................",
]

GONGFU_PALETTE = {
    "K": "minecraft:black_wool",       # 城楼顶/门洞/旗杆/车轮
    "R": "minecraft:red_wool",         # 城楼红墙/红旗
    "O": "minecraft:orange_wool",      # 橙旗
    "Y": "minecraft:yellow_wool",      # 黄旗
    "B": "minecraft:blue_wool",        # 蓝旗
    "N": "minecraft:brown_terracotta", # 驼队/车马 brown caravan
    "G": "minecraft:gold_block",       # 金色城墙线 gold wall line
    "D": "minecraft:gray_terracotta",  # 城台基座 platform
}


# ---------------------------------------------------------------------------
# Local helpers.
# ---------------------------------------------------------------------------
def _check_art(name: str, art: list[str], palette: dict[str, str]) -> None:
    """Guard: every art row must share one width and use known chars."""
    width = len(art[0])
    bad = [i for i, row in enumerate(art) if len(row) != width]
    if bad:
        raise ValueError(f"{name}: rows {bad} length != {width}")
    unknown = sorted({ch for row in art for ch in row} - set(palette) - {"."})
    if unknown:
        raise ValueError(f"{name}: unknown art chars {unknown}")


def _mural_stele(
    fills: list[Fill],
    label: str,
    x: int,
    z: int,
    ground_y: int,
) -> None:
    """One mural stele (壁画碑记): dark seat, quartz shaft, gilded cap."""
    add_fill(fills, f"{label} seat", (x - 1, ground_y, z - 1), (x + 1, ground_y, z + 1), M.DARK)
    add_fill(fills, f"{label} shaft", (x, ground_y + 1, z), (x, ground_y + 6, z), QUARTZ_PILLAR)
    add_fill(fills, f"{label} cap", (x - 1, ground_y + 7, z - 1), (x + 1, ground_y + 7, z + 1), M.GOLD)


# ---------------------------------------------------------------------------
# Main builder.
# ---------------------------------------------------------------------------
def build_mural_detail_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Dunhuang Feitian (敦煌飞天) - Hanyuan Dian east gable.
    #    Wall face x=3340 -> mural plane x=3341, z 5318..5341, y 44..31.
    # ------------------------------------------------------------------
    _check_art("feitian", FEITIAN_ART, FEITIAN_PALETTE)
    add_fill(fills, "mural feitian sky deep", (3341, 41, 5318), (3341, 44, 5341),
             FEITIAN_PALETTE["T"])
    add_fill(fills, "mural feitian sky mid", (3341, 36, 5318), (3341, 40, 5341),
             FEITIAN_PALETTE["L"])
    add_fill(fills, "mural feitian sky low", (3341, 31, 5318), (3341, 35, 5341),
             FEITIAN_PALETTE["E"])
    add_pixel_mural(fills, "mural feitian", FEITIAN_ART, FEITIAN_PALETTE,
                    x=3341, y=44, z=5318, axis="z", flip=True)
    _mural_stele(fills, "mural feitian stele", 3344, 5345, ground_y=9)

    # ------------------------------------------------------------------
    # 2. Blue-green Landscape (青绿山水) - Qinglong Temple hall gable.
    #    Wall face z=1015 -> mural plane z=1014, x 5038..5061, y 24..13.
    # ------------------------------------------------------------------
    _check_art("shanshui", SHANSHUI_ART, SHANSHUI_PALETTE)
    add_fill(fills, "mural shanshui sky", (5038, 19, 1014), (5061, 24, 1014),
             SHANSHUI_PALETTE["W"])
    add_fill(fills, "mural shanshui ridge band", (5038, 16, 1014), (5061, 18, 1014),
             SHANSHUI_PALETTE["M"])
    add_fill(fills, "mural shanshui shore", (5038, 15, 1014), (5061, 15, 1014),
             SHANSHUI_PALETTE["N"])
    add_fill(fills, "mural shanshui water", (5038, 13, 1014), (5061, 14, 1014),
             SHANSHUI_PALETTE["B"])
    add_pixel_mural(fills, "mural shanshui", SHANSHUI_ART, SHANSHUI_PALETTE,
                    x=5038, y=24, z=1014, axis="x", flip=True)
    _mural_stele(fills, "mural shanshui stele", 5064, 1012, ground_y=1)

    # ------------------------------------------------------------------
    # 3. Sutra Preaching Scene (说法图) - Daxingshan hall rear wall.
    #    Wall face z=2515 -> mural plane z=2516, x 1440..1459, y 28..17.
    #    No background bands: the red wall itself is the mural ground.
    # ------------------------------------------------------------------
    _check_art("shuofa", SHUOFA_ART, SHUOFA_PALETTE)
    add_pixel_mural(fills, "mural shuofa", SHUOFA_ART, SHUOFA_PALETTE,
                    x=1440, y=28, z=2516, axis="x", flip=False)
    _mural_stele(fills, "mural shuofa stele", 1435, 2517, ground_y=1)

    # ------------------------------------------------------------------
    # 4. Chang'an Tribute Scroll (长安贡赋图) - Beilin screen wall.
    #    The source south wall (y 4..9) is too low for a 10-row panel,
    #    so first raise a dedicated white 照壁 just outside it, then
    #    paint on its south face: plane z=5152, x 1840..1863, y 13..4.
    # ------------------------------------------------------------------
    _check_art("gongfu", GONGFU_ART, GONGFU_PALETTE)
    add_fill(fills, "mural gongfu zhaobi plinth", (1839, 4, 5153), (1864, 5, 5154), M.STONE)
    add_fill(fills, "mural gongfu zhaobi body", (1839, 6, 5153), (1864, 14, 5154),
             M.WHITE_TERRACOTTA)
    add_fill(fills, "mural gongfu zhaobi cap", (1838, 15, 5152), (1865, 15, 5155), M.DARK)
    add_pixel_mural(fills, "mural gongfu", GONGFU_ART, GONGFU_PALETTE,
                    x=1840, y=13, z=5152, axis="x", flip=False)
    _mural_stele(fills, "mural gongfu stele", 1835, 5154, ground_y=4)


def main() -> None:
    run_builder(build_mural_detail_3d, "mural_detail_3d")


if __name__ == "__main__":
    main()
