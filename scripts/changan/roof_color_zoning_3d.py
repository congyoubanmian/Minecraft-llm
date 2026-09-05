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
Roof Color Zoning 3D (唐长安城屋顶色彩规划叠加层) - city-wide detail
enrichment overlay that colour-codes every building class by ridge-line
band, so the city reads at a glance from the city walls.

中文名：唐长安城屋顶色彩规划叠加层（脊线色带 + 垂脊标饰 + 坊里色彩图例壁）
英文名：Chang'an roof-colour zoning overlay (ridge colour bands, hip-ridge
crowns, and a ward colour legend wall at the south mouth of Zhuque Avenue).

This module ONLY ADDS ridge-line colour bands and small ridge ornaments on
top of the EXISTING roofs. It never issues an AIR fill and never rebuilds a
roof volume (只添加不清空).

Every original add_ridge_roof follows the lib geometry:

    steps   = max(3, layers * 2)
    ridge_y = y_call + steps          # ridge occupies ridge_y .. ridge_y+1
    ridge-end finials occupy ridge_y+2 .. ridge_y+5

so a colour band laid at ridge_y+2 (inset 2 blocks from each ridge end to
clear the gold finials) caps the existing ridge, and a 1x1x2 marker at
ridge_y+6..ridge_y+7 stands exactly on each finial top. All coordinates
below were derived by replaying the roof calls of the source modules
(palace_roof_detail_3d.py, academy_guozijian.py, government_offices.py,
market_block.py, ward_block.py, temple_daci.py, temple_qinglong.py,
temple_daxingshan.py); the four Daming Palace ridges reuse the derivation
table of palace_roof_detail_3d.py verbatim.

色彩规范表 (Tang five-element / five-colour zoning scheme):

    | 分区 zone              | 色彩 colour | 方块 block                 | 脊线 ridge bands            |
    |------------------------|-------------|----------------------------|-----------------------------|
    | 宫城/大明宫 palace     | 金 gold     | gold_block                 | (already gold) + 垂脊标饰   |
    | 皇城官署 offices       | 黄 yellow   | yellow_glazed_terracotta   | guozijian + 4 offices       |
    | 东西市商铺 markets     | 深灰 dark   | deepslate_tiles            | 12 representative shops     |
    | 坊区宅邸 wards         | 灰 grey     | polished_andesite          | 12 representative mansions  |
    | 佛寺 temples           | 青 blue     | prismarine_bricks          | side halls of 3 temples     |

Distinctive features:
    - Hip-ridge crowns (垂脊标饰): a 1x1x2 gold marker capping the top of
      each pair of hip ridges on all four Daming Palace main halls (2 per
      hall, standing on the centre of the existing gold ridge finials,
      Hanyuan's nested between its chiwen horns) - echoes the palaceroof
      main-ridge walking beasts.
    - Zoning ridge bands: a 1x1 colour band laid block by block along the
      top of every targeted main ridge (22 yellow office ridges, 12 dark
      market ridges, 12 grey ward ridges, 8 blue temple ridges), each end
      flagged by a 1x1x2 colour marker above the existing gold finial.
    - Ward colour legend wall (屋顶色彩图例壁): a 12x8 pixel mural on a
      dark-framed stele beside Zhuque Avenue's south mouth (x 3080, just
      inside Mingde Men), showing the five colour swatches with glyph
      impressions and a red-dotted title band, on a stone plinth with
      timber posts and a dark cap.
"""


# ---------------------------------------------------------------------------
# Zoning palette (唐代五行五色示意).
# ---------------------------------------------------------------------------
PALACE_RIDGE = M.GOLD  # 宫城/大明宫 金脊 (existing; completed with hip crowns)
OFFICE_RIDGE = M.YELLOW_GLAZED  # 皇城官署 黄脊
MARKET_RIDGE = M.DARK  # 东西市商铺 深灰脊
WARD_RIDGE = M.ANDESITE  # 坊区宅邸 灰脊
TEMPLE_RIDGE = M.ROOF_BLUE  # 佛寺 青脊


# ---------------------------------------------------------------------------
# Overlay primitives.
# ---------------------------------------------------------------------------
def _zone_ridge(
    fills: list[Fill],
    label: str,
    cx: int,
    rz1: int,
    rz2: int,
    ridge_y: int,
    block: str,
) -> None:
    """Colour-code one existing north-south main ridge (axis z).

    The existing ridge cap occupies (cx-1..cx+1, ridge_y..ridge_y+1) with
    gold finials at rz1/rz2 rising to ridge_y+5.  We add: a 1x1 band laid
    block by block along the ridge top at ridge_y+2 (inset 2 from each end
    to clear the finials), plus a 1x1x2 colour marker standing on each
    finial top at ridge_y+6..ridge_y+7.
    """
    add_fill(fills, f"{label} band", (cx, ridge_y + 2, rz1 + 2), (cx, ridge_y + 2, rz2 - 2), block)
    add_fill(fills, f"{label} mark n", (cx, ridge_y + 6, rz1), (cx, ridge_y + 7, rz1), block)
    add_fill(fills, f"{label} mark s", (cx, ridge_y + 6, rz2), (cx, ridge_y + 7, rz2), block)


def _hip_crown(fills: list[Fill], label: str, x: int, y: int, z: int) -> None:
    """垂脊标饰: 1x1x2 gold crown capping the top of a pair of hip ridges
    (垂脊) - i.e. one main-ridge end - standing on the finial centre whose
    top block is at y-1."""
    add_fill(fills, label, (x, y, z), (x, y + 1, z), PALACE_RIDGE)


# ---------------------------------------------------------------------------
# Derived ridge tables (local city coordinates).
# ---------------------------------------------------------------------------
# Daming Palace main ridges - coordinates reused verbatim from the
# palace_roof_detail_3d.py derivation table. mark_y = ridge_y + 6.
PALACE_HIP_CROWNS = [
    # hall       centre_x  finial_z1  finial_z2  mark_y
    ("hanyuan", 3000, 5148, 5512, 79),   # ridge y 73..74 (layers 6, y 61)
    ("xuanzheng", 3000, 4860, 5100, 62),  # ridge y 56..57 (layers 5, y 46)
    ("zichen", 2490, 5186, 5494, 49),     # ridge y 43..44 (layers 4, y 35)
]
LINDE_HIP_CROWNS = [
    # hall      west_x  east_x  centre_z  mark_y
    ("front", 2148, 2452, 5400, 37),   # ridge y 31..32 (layers 3, y 25)
    ("middle", 2128, 2472, 5510, 45),  # ridge y 39..40 (layers 4, y 31)
    ("rear", 2168, 2432, 5610, 35),    # ridge y 29..30 (layers 3, y 23)
]

# Guozijian (academy_guozijian.py: X1,Z1 = 1600,4200; mid_x = 1900).
# lingxing roof (1878..1922 / 4194..4206, y 15, l2) -> ridge_y 19, z 4198..4202.
# confucius roof (1844..1956 / 4394..4486, y 23, l3) -> ridge_y 29, z 4398..4482.
# lecture roofs (hx-40..hx+40 / 4414..4526, y 15, l2) -> ridge_y 19, z 4418..4522.
# dorm roofs (1624..2176 / dz-4..dz+34, y 11, l2) -> ridge_y 15, z dz..dz+30.
GUOZIJIAN_RIDGES = [
    # name        cx    rz1   rz2   ridge_y
    ("lingxing", 1900, 4198, 4202, 19),
    ("confucius", 1900, 4398, 4482, 29),
    ("lecture w", 1800, 4418, 4522, 19),
    ("lecture e", 2000, 4418, 4522, 19),
    ("dorm s", 1900, 4560, 4590, 15),
    ("dorm n", 1900, 4600, 4630, 15),
]

# Imperial city offices (government_offices.py OFFICES; z1 = cz-55).
# gate roof (cx-18..cx+18 / z1-6..z1+6, y 13, l2)   -> ridge_y 17, z z1-2..z1+2.
# hall roof (cx-52..cx+52 / z1+24..z1+96, y 21, l3) -> ridge_y 27, z z1+28..z1+92.
# side office roofs (y 13, l2)                      -> ridge_y 17, z cz+43..cz+47.
OFFICES = [
    ("shangshu_sheng", 2000, 4200),
    ("yushi_tai", 2200, 4400),
    ("dali_si", 2400, 4200),
    ("honglu_si", 2600, 4400),
]

# Market shop quadrants inside one 120x120 market block (market_block.py,
# base_y 2): roof (sx-4..sx+50 / sz-4..sz+36, y 15, l2) -> ridge_y 19,
# ridge z sz..sz+32, centre x sx+23.
MARKET_SHOP_QUADRANTS = [(8, 8), (66, 8), (8, 80), (66, 80)]
MARKET_SAMPLE_SHOPS = [
    # (block origin_x, origin_z, quadrant) - 6 West Market + 6 East Market
    (760, 2060, 0), (1000, 2180, 1), (1240, 2300, 2),
    (1480, 2420, 3), (880, 2540, 0), (1360, 2660, 1),
    (4240, 2060, 2), (4480, 2180, 3), (4720, 2300, 0),
    (4960, 2420, 1), (4360, 2540, 2), (5080, 2660, 3),
]

# Ward mansion quadrants inside one 260x260 ward (ward_block.py, base_y 1):
# roof (mx+10..mx+60 / mz+10..mz+60, y 12, l2) -> ridge_y 16, ridge z
# mz+14..mz+56, centre x mx+35.
WARD_MANSION_QUADRANTS = [(25, 25), (165, 25), (25, 165), (165, 165)]
WARD_SAMPLE_MANSIONS = [
    # (ward origin_x, origin_z) - 12 wards spread across the residential grid
    (520, 620), (900, 1020), (1280, 1420),
    (2040, 620), (2420, 1020), (3420, 620),
    (3800, 1420), (4180, 1820), (4560, 620),
    (4940, 1020), (5320, 1420), (3420, 3020),
]

# Temple side halls (non-main-hall roofs; all axis-z, all layers 2 ->
# ridge_y = y_call + 4). Derived from temple_daci.py / temple_qinglong.py /
# temple_daxingshan.py.
TEMPLE_SIDE_RIDGES = [
    # name              cx    rz1   rz2   ridge_y
    ("daci gate", 4600, 3598, 3602, 20),     # roof y 16, z 3594..3606
    ("daci dharma", 4600, 3954, 4006, 23),   # roof y 19, z 3950..4010
    ("daci sutra w", 4520, 3905, 3935, 19),  # roof y 15, z 3901..3939
    ("daci sutra e", 4680, 3905, 3935, 19),
    ("qinglong gate", 5050, 798, 802, 21),   # roof y 17, z 794..806
    ("qinglong sutra", 5130, 1109, 1151, 23),  # roof y 19, z 1105..1155
    ("daxingshan gate", 1450, 2198, 2202, 19),  # roof y 15, z 2194..2206
    ("daxingshan sutra", 1360, 2459, 2501, 25),  # roof y 21, z 2455..2505
]

# ---------------------------------------------------------------------------
# Ward colour legend wall (屋顶色彩图例壁) at the south mouth of Zhuque
# Avenue, just inside Mingde Men: 12x8 mural in the plane x=3080, running
# z 24..35, top row at y 10. Five colour swatches (palace gold, office
# yellow, market dark, ward andesite, temple blue) with white glyph
# impressions, red-dotted title band, dark frame.
# ---------------------------------------------------------------------------
MURAL_X = 3080
MURAL_TOP_Y = 10
MURAL_Z = 24

MURAL_ART = [
    "DDDDDDDDDDDD",
    "DWWRWWRWWRWD",
    "DGGWWDDWWDDD",
    "DYYDWWWWDWWD",
    "DKKWWDWWWDWD",
    "DAADWWDDDWWW",
    "DBBDWWDWWWWW",
    "DDDDDDDDDDDD",
]
MURAL_PALETTE = {
    "D": M.DARK,  # frame + market grey swatch (deepslate tiles)
    "G": M.GOLD,  # palace gold swatch
    "Y": M.YELLOW_GLAZED,  # office yellow swatch
    "K": M.DARK,  # market grey swatch
    "A": M.ANDESITE,  # ward grey swatch
    "B": M.ROOF_BLUE,  # temple blue swatch
    "W": M.WHITE,  # glyph impressions
    "R": M.RED_WOOL,  # title dots
}


def build_roof_color_zoning_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Palace gold completion (宫城金脊补齐): one 1x1x2 gold 垂脊标饰
    #    on top of each main-ridge end of the four Daming Palace halls,
    #    echoing the palaceroof main-ridge walking beasts.
    # ------------------------------------------------------------------
    for hall, cx, rz1, rz2, mark_y in PALACE_HIP_CROWNS:
        _hip_crown(fills, f"roofzone palace {hall} hip crown n", cx, mark_y, rz1)
        _hip_crown(fills, f"roofzone palace {hall} hip crown s", cx, mark_y, rz2)
    for hall, wx, ex, cz, mark_y in LINDE_HIP_CROWNS:
        _hip_crown(fills, f"roofzone palace linde {hall} hip crown w", wx, mark_y, cz)
        _hip_crown(fills, f"roofzone palace linde {hall} hip crown e", ex, mark_y, cz)

    # ------------------------------------------------------------------
    # 2. Imperial city yellow ridges (皇城官署黄脊): guozijian plus the
    #    four government offices, one YELLOW_GLAZED ridge band per main
    #    ridge (gate / main hall / both side office ranges).
    # ------------------------------------------------------------------
    for name, cx, rz1, rz2, ridge_y in GUOZIJIAN_RIDGES:
        _zone_ridge(fills, f"roofzone office guozijian {name}", cx, rz1, rz2, ridge_y, OFFICE_RIDGE)
    for name, cx, cz in OFFICES:
        z1, z2 = cz - 55, cz + 55
        _zone_ridge(fills, f"roofzone office {name} gate", cx, z1 - 2, z1 + 2, 17, OFFICE_RIDGE)
        _zone_ridge(fills, f"roofzone office {name} hall", cx, z1 + 28, z1 + 92, 27, OFFICE_RIDGE)
        _zone_ridge(fills, f"roofzone office {name} office w", cx - 45, cz + 43, cz + 47, 17, OFFICE_RIDGE)
        _zone_ridge(fills, f"roofzone office {name} office e", cx + 45, cz + 43, cz + 47, 17, OFFICE_RIDGE)

    # ------------------------------------------------------------------
    # 3. Market dark ridges (东西市深灰脊): 12 representative shops across
    #    the West and East Market blocks.
    # ------------------------------------------------------------------
    for ox, oz, q in MARKET_SAMPLE_SHOPS:
        dx, dz = MARKET_SHOP_QUADRANTS[q]
        sx, sz = ox + dx, oz + dz
        _zone_ridge(fills, f"roofzone market shop {ox},{oz} q{q}", sx + 23, sz, sz + 32, 19, MARKET_RIDGE)

    # ------------------------------------------------------------------
    # 4. Ward grey ridges (坊区灰脊): 12 representative courtyard mansions.
    # ------------------------------------------------------------------
    for i, (ox, oz) in enumerate(WARD_SAMPLE_MANSIONS):
        dx, dz = WARD_MANSION_QUADRANTS[i % 4]
        mx, mz = ox + dx, oz + dz
        _zone_ridge(fills, f"roofzone ward mansion {ox},{oz}", mx + 35, mz + 14, mz + 56, 16, WARD_RIDGE)

    # ------------------------------------------------------------------
    # 5. Temple blue ridges (佛寺青脊补齐): side halls (gates, dharma and
    #    sutra halls) of Da Ci'en, Qinglong and Daxingshan.
    # ------------------------------------------------------------------
    for name, cx, rz1, rz2, ridge_y in TEMPLE_SIDE_RIDGES:
        _zone_ridge(fills, f"roofzone temple {name}", cx, rz1, rz2, ridge_y, TEMPLE_RIDGE)

    # ------------------------------------------------------------------
    # 6. Ward colour legend wall (坊里色彩图例壁): free-standing stele on
    #    the east side of Zhuque Avenue's south mouth, facing the avenue.
    # ------------------------------------------------------------------
    add_fill(fills, "roofzone mural plinth", (MURAL_X - 1, 2, MURAL_Z - 2), (MURAL_X + 1, 2, MURAL_Z + 13), M.DARK_BRICKS)
    add_fill(fills, "roofzone mural post n", (MURAL_X, 3, MURAL_Z - 2), (MURAL_X, 11, MURAL_Z - 2), M.LOG)
    add_fill(fills, "roofzone mural post s", (MURAL_X, 3, MURAL_Z + 13), (MURAL_X, 11, MURAL_Z + 13), M.LOG)
    add_fill(fills, "roofzone mural cap", (MURAL_X, 11, MURAL_Z - 1), (MURAL_X, 11, MURAL_Z + 12), M.DARK)
    add_pixel_mural(fills, "roofzone mural", MURAL_ART, MURAL_PALETTE, MURAL_X, MURAL_TOP_Y, MURAL_Z, axis="z")


def main() -> None:
    run_builder(build_roof_color_zoning_3d, "roof_color_zoning_3d")


if __name__ == "__main__":
    main()
