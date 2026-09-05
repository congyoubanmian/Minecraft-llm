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
    add_pixel_mural,
    run_builder,
)


"""
Palace Hall Interior V2 3D (大明宫四大殿室内精装·第二批:
藻井 / 蟠龙金柱 / 御屏风 / 帷幔 / 朝服架 / 铜鹤灯 / 麟德殿宴乐补).

Detail-enrichment overlay pass, batch two: imperial interior fittings for
the four already-built Daming Palace halls. Everything is add-only; objects
sit on the interior floors / hang under the ceilings / wrap the existing
columns derived from the source modules.

深化清单 (deepening list, coordinates read back from the source modules):

    - 含元殿 Hanyuan Dian  (palace_hanyuan_dian.py + palace_hanyuan_3d.py
      + palace_interior.py "hanyuan")
      floor y=9 (interior smooth floor at x 2668..3332, z 5188..5472),
      walls y 9..57 thickness 2 -> interior air top y=55; column grid
      spacing 30 -> the two throne-row columns flank the throne platform
      (2994..3006, 5206..5214, throne cx=3000) at (2990, 5210)/(3020, 5210),
      columns run y 9..55; the existing red-wall throne screen sits at
      z 5202..5205, so the new triptych screen is displaced to z 5217.
    - 宣政殿 Xuanzheng Dian (palace_xuanzheng_dian.py + palace_interior.py
      "xuanzheng")
      floor y=8, walls y 8..44 -> interior air 10..42; column grid spacing
      26, first interior row z=4906, pair flanking the throne axis x=3000
      at (2974, 4906)/(3026, 4906); throne (3000, 4910); new screen at
      z 4917 (existing screen z 4902..4905).
    - 紫宸殿 Zichen Dian    (palace_zichen_dian.py + palace_interior.py
      "zichen")
      floor y=6, walls y 6..34 -> interior air 8..32; column grid spacing
      22, front row z=5222, pair (2470, 5222)/(2514, 5222) around throne
      axis x=2490; throne (2490, 5230); new screen at z 5237 (existing
      screen z 5222..5225); no minister desks in this hall.
    - 麟德殿 Linde Hall     (palace_linde_3d.py)
      middle hall x 2130..2470, z 5470..5550, walls y 10..30 -> interior
      air 12..28, floor fill at y=10: receives the throne suite (dragon
      columns (2270, 5530)/(2330, 5530), caisson (2300, 5540), screen
      z 5544); front banquet hall x 2150..2450, z 5350..5450, walls y
      10..24 -> interior air 12..22: receives the feast dressing (wine
      vessel arrays, song stage, music desks).

Distinctive features (English):
    - Dragon-coiled gold columns (蟠龙金柱): a 1x1 gold "dragon body" block
      helixes up the 12-block ring around each 2x2 throne-flanking column,
      advancing one position per two-block rise, crowned by a gilded 4x4
      dragon-head slab with two backward-swept horns.
    - Gilded caisson ceilings (藻井) above each throne: three shrinking
      scanline discs (radius 4 gold disc with four white-terracotta lotus
      petal caps -> radius 2 second gold ring -> sea-lantern pearl flanked
      by petal tips), hung just below the interior ceiling.
    - Imperial triptych screens (三联屏) behind each throne: dark-oak frames
      around deepslate lacquer cores, the centre panel carrying an 8x6
      crane-and-mountain pixel mural (add_pixel_mural: gold moon, white
      crane, quartz peaks).
    - Red silk valances (帷幔) between the front-hall column bays: 2-high
      red wool cloth over a 1-high red stained-glass sheer.
    - Court-robe racks (朝服架) in the east chambers: dark-oak fence frames
      with hanging red robes and a gold sash.
    - Bronze crane lamps (铜鹤灯) flanking each throne: quartz crane with
      outstretched neck and gold beak, sea-lantern lamp on its back, on a
      dark plinth.
    - Linde Hall feast dressing: wine-vessel arrays (wood board, barrel,
      gold cups) patching the shortened banquet-table runs, plus a song
      stage (歌台) with red carpet and two music desks (乐案).
    - Add-only pass: no AIR fills, nothing from earlier modules is cleared;
      all new objects are displaced away from the palace_interior.py
      furniture (throne screens, desks, mats, lamps).
"""

# Pixel art for the imperial screens (仙鹤山纹 8x6): gold moon, white
# crane with spread wings, quartz mountain range.
CRANE_ART = [
    "..G.....",
    "..W.....",
    ".WWWW...",
    "..W...M.",
    "M..M..M.",
    "MMMMMMMM",
]
CRANE_PALETTE = {
    "G": M.GOLD,
    "W": M.WHITE_WOOL,
    "M": M.QUARTZ,
}

BARREL = "minecraft:barrel"


# ---------------------------------------------------------------------------
# Reusable fitting primitives.
# ---------------------------------------------------------------------------
def _dragon_column(
    fills: list[Fill],
    label: str,
    x: int,
    z: int,
    y1: int,
    y2: int,
) -> None:
    """Coiled gold dragon climbing one 2x2 column (蟠龙金柱).

    A 1x1 gold block walks the 12-block ring around the column core
    (x..x+1, z..z+1), advancing one ring position per two-block rise
    (每 2 格升 1 错位), forming the helical dragon body. The column is
    then crowned with a gilded 4x4 dragon-head slab and two horns.
    """
    ring = [
        (x - 1, z - 1), (x, z - 1), (x + 1, z - 1), (x + 2, z - 1),
        (x + 2, z), (x + 2, z + 1), (x + 2, z + 2), (x + 1, z + 2),
        (x, z + 2), (x - 1, z + 2), (x - 1, z + 1), (x - 1, z),
    ]
    for i, y in enumerate(range(y1, y2 + 1, 2)):
        px, pz = ring[i % len(ring)]
        add_fill(fills, f"{label} scale {y}", (px, y, pz), (px, y, pz), M.GOLD)
    # Gilded dragon head crowning the shaft, horns at diagonal corners.
    add_fill(fills, f"{label} head", (x - 1, y2 + 1, z - 1), (x + 2, y2 + 2, z + 2), M.GOLD)
    add_fill(fills, f"{label} horn nw", (x - 1, y2 + 3, z - 1), (x - 1, y2 + 4, z - 1), M.GOLD)
    add_fill(fills, f"{label} horn se", (x + 2, y2 + 3, z + 2), (x + 2, y2 + 4, z + 2), M.GOLD)


def _caisson(fills: list[Fill], label: str, cx: int, cz: int, y: int) -> None:
    """Gilded coffered ceiling above the throne (藻井), radius 4 -> 2 -> 1.

    Tier 1 is a scanline gold disc with four white lotus-petal caps, tier 2
    the second gold ring of the double ring, tier 3 the sea-lantern pearl
    flanked by two petal tips (mingtang scanline-disc approach).
    """
    # Tier 1: radius-4 gold disc, one scanline row per dz.
    for dz in range(-4, 5):
        half = int(math.sqrt(16 - dz * dz))
        add_fill(fills, f"{label} disc {dz}", (cx - half, y, cz + dz), (cx + half, y, cz + dz), M.GOLD)
    # Four cardinal lotus petals capping the disc rim.
    add_fill(fills, f"{label} petal n", (cx - 1, y, cz - 4), (cx + 1, y, cz - 4), M.WHITE_TERRACOTTA)
    add_fill(fills, f"{label} petal s", (cx - 1, y, cz + 4), (cx + 1, y, cz + 4), M.WHITE_TERRACOTTA)
    add_fill(fills, f"{label} petal w", (cx - 4, y, cz - 1), (cx - 4, y, cz + 1), M.WHITE_TERRACOTTA)
    add_fill(fills, f"{label} petal e", (cx + 4, y, cz - 1), (cx + 4, y, cz + 1), M.WHITE_TERRACOTTA)
    # Tier 2: radius-2 gold disc (second ring of the double ring).
    for dz in range(-2, 3):
        half = int(math.sqrt(4 - dz * dz))
        add_fill(fills, f"{label} inner {dz}", (cx - half, y + 1, cz + dz), (cx + half, y + 1, cz + dz), M.GOLD)
    # Tier 3: sea-lantern pearl with petal tips.
    add_fill(fills, f"{label} pearl", (cx - 1, y + 2, cz), (cx + 1, y + 2, cz), M.SEA_LANTERN)
    add_fill(fills, f"{label} pearl petal n", (cx, y + 2, cz - 1), (cx, y + 2, cz - 1), M.WHITE_TERRACOTTA)
    add_fill(fills, f"{label} pearl petal s", (cx, y + 2, cz + 1), (cx, y + 2, cz + 1), M.WHITE_TERRACOTTA)


def _screen(
    fills: list[Fill],
    label: str,
    cx: int,
    z: int,
    y1: int,
    triptych: bool = True,
) -> None:
    """Imperial screen behind the throne (御屏风·三联屏).

    A 10-wide centre panel: dark-oak frame around a deepslate lacquer core
    carrying the 8x6 crane-and-mountain mural; flanking side panels repeat
    the frame in plain dark lacquer when triptych=True.
    """
    px1, px2 = cx - 5, cx + 4  # centre panel, mural bore exactly 8 wide
    add_fill(fills, f"{label} core", (px1 + 1, y1 + 1, z), (px2 - 1, y1 + 6, z), M.DARK)
    add_fill(fills, f"{label} cap", (px1, y1 + 7, z), (px2, y1 + 7, z), M.WOOD)
    add_fill(fills, f"{label} sill", (px1, y1, z), (px2, y1, z), M.WOOD)
    add_fill(fills, f"{label} post w", (px1, y1 + 1, z), (px1, y1 + 6, z), M.WOOD)
    add_fill(fills, f"{label} post e", (px2, y1 + 1, z), (px2, y1 + 6, z), M.WOOD)
    add_pixel_mural(fills, f"{label} mural", CRANE_ART, CRANE_PALETTE, px1 + 1, y1 + 6, z, axis="x")
    if triptych:
        # Plain lacquer side panels: dark core with timber cap and sill.
        for side, (sx1, sx2) in enumerate(((cx - 10, cx - 7), (cx + 6, cx + 9))):
            add_fill(fills, f"{label} side {side} core", (sx1 + 1, y1 + 1, z), (sx2 - 1, y1 + 6, z), M.DARK)
            add_fill(fills, f"{label} side {side} cap", (sx1, y1 + 7, z), (sx2, y1 + 7, z), M.WOOD)
            add_fill(fills, f"{label} side {side} sill", (sx1, y1, z), (sx2, y1, z), M.WOOD)


def _drape(fills: list[Fill], label: str, x: int, z: int, y_top: int) -> None:
    """One silk valance between front columns (帷幔): 2 red wool + 1 glass."""
    add_fill(fills, f"{label} cloth", (x, y_top - 1, z), (x + 1, y_top, z), M.RED_WOOL)
    add_fill(fills, f"{label} sheer", (x, y_top - 2, z), (x + 1, y_top - 2, z), M.RED_STAINED_GLASS)


def _robe_rack(fills: list[Fill], label: str, x1: int, x2: int, z: int, y: int) -> None:
    """Court-robe rack in the east chamber (朝服架): fence frame + robes."""
    add_fill(fills, f"{label} post w", (x1, y, z), (x1, y + 2, z), M.FENCE)
    add_fill(fills, f"{label} post e", (x2, y, z), (x2, y + 2, z), M.FENCE)
    add_fill(fills, f"{label} bar", (x1, y + 3, z), (x2, y + 3, z), M.FENCE)
    mid = (x1 + x2) // 2
    add_fill(fills, f"{label} robe w", (x1 + 1, y + 1, z), (x1 + 1, y + 2, z), M.RED_WOOL)
    add_fill(fills, f"{label} robe sash", (mid, y + 1, z), (mid, y + 2, z), M.GOLD)
    add_fill(fills, f"{label} robe e", (x2 - 1, y + 1, z), (x2 - 1, y + 2, z), M.RED_WOOL)


def _crane_lamp(fills: list[Fill], label: str, x: int, z: int, y: int, face: int) -> None:
    """Bronze crane lamp flanking the throne (铜鹤灯).

    Quartz crane with raised neck and gold beak (`face` = +1 neck reaches
    east, -1 west), sea-lantern lamp on its back, standing on a dark plinth.
    """
    add_fill(fills, f"{label} plinth", (x - 1, y, z - 1), (x + 1, y, z + 1), M.DARK)
    add_fill(fills, f"{label} legs", (x, y + 1, z), (x, y + 1, z), M.QUARTZ)
    add_fill(fills, f"{label} body", (x, y + 2, z), (x, y + 3, z), M.QUARTZ)
    add_fill(fills, f"{label} lamp", (x, y + 4, z), (x, y + 4, z), M.SEA_LANTERN)
    add_fill(fills, f"{label} neck", (x + face, y + 4, z), (x + face, y + 5, z), M.QUARTZ)
    add_fill(fills, f"{label} head", (x + 2 * face, y + 6, z), (x + 2 * face, y + 6, z), M.QUARTZ)
    add_fill(fills, f"{label} beak", (x + 3 * face, y + 6, z), (x + 3 * face, y + 6, z), M.GOLD)


def _wine_group(fills: list[Fill], label: str, x: int, z: int, y: int) -> None:
    """Wine-vessel group patching a banquet-table gap (酒器阵列)."""
    add_fill(fills, f"{label} board", (x - 2, y, z), (x + 2, y, z), M.WOOD)
    add_fill(fills, f"{label} jar", (x, y + 1, z), (x, y + 1, z), BARREL)
    add_fill(fills, f"{label} cup w", (x - 1, y + 1, z), (x - 1, y + 1, z), M.GOLD)
    add_fill(fills, f"{label} cup e", (x + 1, y + 1, z), (x + 1, y + 1, z), M.GOLD)


# ---------------------------------------------------------------------------
# Main builder.
# ---------------------------------------------------------------------------
def build_palace_hall_v2_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. 含元殿 Hanyuan Dian (emphasis hall).
    #    floor y=9, interior air 11..55; throne (3000, 5210); the two
    #    throne-row columns at (2990/3020, 5210) carry the dragon coils.
    # ------------------------------------------------------------------
    for i, col_x in enumerate((2990, 3020)):
        _dragon_column(fills, f"hallv2 hanyuan dragon col {i}", col_x, 5210, 12, 44)
    _caisson(fills, "hallv2 hanyuan caisson", 3000, 5208, 52)
    _screen(fills, "hallv2 hanyuan screen", 3000, 5217, 11)
    # Valances across the front bays; the two bays flanking the main door
    # (x 2984..3016) stay open.
    for dx in (2720, 2780, 2840, 2900, 3080, 3140, 3200, 3260):
        _drape(fills, f"hallv2 hanyuan drape {dx}", dx, 5184, 55)
    # East-chamber robe racks between the desk rows (z rows 5300/5330/5360).
    _robe_rack(fills, "hallv2 hanyuan robe rack a", 3326, 3330, 5315, 10)
    _robe_rack(fills, "hallv2 hanyuan robe rack b", 3326, 3330, 5345, 10)
    # Crane lamps flanking the throne, clear of the flanking desks.
    _crane_lamp(fills, "hallv2 hanyuan crane w", 2980, 5215, 10, 1)
    _crane_lamp(fills, "hallv2 hanyuan crane e", 3020, 5215, 10, -1)

    # ------------------------------------------------------------------
    # 2. 宣政殿 Xuanzheng Dian.
    #    floor y=8, interior air 10..42; throne (3000, 4910); throne-front
    #    column pair at (2974/3026, 4906).
    # ------------------------------------------------------------------
    for i, col_x in enumerate((2974, 3026)):
        _dragon_column(fills, f"hallv2 xuanzheng dragon col {i}", col_x, 4906, 11, 33)
    _caisson(fills, "hallv2 xuanzheng caisson", 3000, 4910, 39)
    _screen(fills, "hallv2 xuanzheng screen", 3000, 4917, 10)
    for dx in (2844, 2948, 3052, 3156):
        _drape(fills, f"hallv2 xuanzheng drape {dx}", dx, 4884, 42)
    _robe_rack(fills, "hallv2 xuanzheng robe rack", 3226, 3230, 4950, 9)
    _crane_lamp(fills, "hallv2 xuanzheng crane w", 2980, 4915, 9, 1)
    _crane_lamp(fills, "hallv2 xuanzheng crane e", 3020, 4915, 9, -1)

    # ------------------------------------------------------------------
    # 3. 紫宸殿 Zichen Dian (emphasis hall).
    #    floor y=6, interior air 8..32; throne (2490, 5230); throne-front
    #    column pair at (2470/2514, 5222).
    # ------------------------------------------------------------------
    for i, col_x in enumerate((2470, 2514)):
        _dragon_column(fills, f"hallv2 zichen dragon col {i}", col_x, 5222, 9, 23)
    _caisson(fills, "hallv2 zichen caisson", 2490, 5228, 29)
    _screen(fills, "hallv2 zichen screen", 2490, 5237, 8)
    for dx in (2404, 2448, 2492, 2536, 2580):
        _drape(fills, f"hallv2 zichen drape {dx}", dx, 5204, 31)
    _robe_rack(fills, "hallv2 zichen robe rack a", 2586, 2590, 5300, 7)
    _robe_rack(fills, "hallv2 zichen robe rack b", 2586, 2590, 5360, 7)
    _crane_lamp(fills, "hallv2 zichen crane w", 2472, 5240, 7, 1)
    _crane_lamp(fills, "hallv2 zichen crane e", 2508, 5240, 7, -1)

    # ------------------------------------------------------------------
    # 4. 麟德殿 Linde Hall, middle hall throne suite.
    #    Interior air 12..28 over the solid y=10..11 slab, so all
    #    floor-standing objects start at the first air level y=12.
    # ------------------------------------------------------------------
    for i, col_x in enumerate((2270, 2330)):
        # Linde has no base column grid, so the 2x2 red-lacquer shaft the
        # dragon coils around is added here (y 12..23, first air 12).
        add_fill(fills, f"hallv2 linde dragon col {i} shaft", (col_x, 12, 5530), (col_x + 1, 23, 5531), M.RED_WALL_ALT)
        _dragon_column(fills, f"hallv2 linde dragon col {i}", col_x, 5530, 13, 21)
    _caisson(fills, "hallv2 linde caisson", 2300, 5540, 24)
    _screen(fills, "hallv2 linde screen", 2300, 5544, 12)
    for dx in (2200, 2240, 2320, 2400):
        _drape(fills, f"hallv2 linde drape {dx}", dx, 5474, 28)
    _robe_rack(fills, "hallv2 linde robe rack", 2436, 2440, 5495, 12)
    _crane_lamp(fills, "hallv2 linde crane w", 2280, 5540, 12, 1)
    _crane_lamp(fills, "hallv2 linde crane e", 2320, 5540, 12, -1)

    # ------------------------------------------------------------------
    # 5. 麟德殿 Linde Hall, front banquet hall feast dressing.
    #    Interior air 12..22; boards/deck stand on the floor at y=12.
    # ------------------------------------------------------------------
    for i, wx in enumerate((2200, 2260, 2340, 2400)):
        _wine_group(fills, f"hallv2 linde wine {i}", wx, 5380, 12)
    # Song stage (歌台) in the south-west corner of the hall (west of both
    # the Zichen pavilion overlap at x>=2280 and the main-hall overlap at
    # x>=2360) with carpet and step.
    add_fill(fills, "hallv2 linde stage deck", (2160, 12, 5405), (2200, 12, 5445), M.WOOD)
    add_fill(fills, "hallv2 linde stage carpet", (2162, 13, 5407), (2198, 13, 5443), M.RED_WOOL)
    add_fill(fills, "hallv2 linde stage step", (2174, 12, 5402), (2180, 12, 5404), M.WOOD)
    # Music desks (乐案) on the stage with gold instruments.
    add_fill(fills, "hallv2 linde music desk a", (2168, 14, 5416), (2170, 15, 5417), M.WOOD)
    add_fill(fills, "hallv2 linde music piece a", (2169, 16, 5416), (2169, 16, 5416), M.GOLD)
    add_fill(fills, "hallv2 linde music desk b", (2188, 14, 5416), (2190, 15, 5417), M.WOOD)
    add_fill(fills, "hallv2 linde music piece b", (2189, 16, 5416), (2189, 16, 5416), M.GOLD)


def main() -> None:
    run_builder(build_palace_hall_v2_3d, "palace_hall_v2_3d")


if __name__ == "__main__":
    main()
