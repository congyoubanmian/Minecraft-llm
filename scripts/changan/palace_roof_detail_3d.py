from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    Fill,
    Materials as M,
    add_eave_bells,
    add_fill,
    add_roof_beasts,
    run_builder,
)


"""
Palace Roof Detail 3D (大明宫三大殿屋顶细节深化叠加层) - detail-enrichment
overlay pass on the already-built main halls of the Daming Palace.

中文名：大明宫含元殿·麟德殿·宣政殿·紫宸殿 屋顶细节深化叠加层
英文名：Daming Palace main-hall roof detail overlay (beasts, bells, tiles).

This module ONLY ADDS surface detail onto the existing structures; it never
issues a single AIR fill. Every coordinate was derived by reading the source
modules and replaying the lib.add_ridge_roof geometry actually used by all
four halls (none of them uses add_hip_roof):

    steps   = max(3, layers * 2)
    ridge_y = y_call + steps          # ridge occupies ridge_y .. ridge_y+1
    => first free block above the ridge (where add_roof_beasts stands)
       = y_call + steps + 2

Deepening targets and per-building derivation (local city coordinates):

    1. Hanyuan Dian 含元殿 (palace_hanyuan_dian.py + palace_hanyuan_3d.py)
       Roof call: add_ridge_roof(2624, 5144 .. 3376, 5516, y=DOUGONG_Y+3=61,
       layers=6, axis z) -> steps 12, ridge y 73..74, x 2999..3001,
       z 5148..5512; beasts at y 75.  The existing gold ridge finials
       (鸱吻) sit at z 5147..5149 / 5511..5513, y 75..78.  The rooftop
       ge pavilion added by palace_hanyuan_3d.py (x 2960..3040,
       z 5300..5360, y 71..79) buries the middle of the ridge, so the
       7-beast queue is split around it: 3 north (z 5152..5296) + 4 south
       (z 5364..5508).
    2. Linde Hall 麟德殿 (palace_linde_3d.py) - three joined halls, each
       _hall(...) calls add_ridge_roof(x1-6, z1-6 .. x2+6, z2+6, y_top+1,
       layers, axis x); all three main ridges get a beast queue:
       front  (hall 2150..2450 / 5350..5450, y_top 24, layers 3)
              -> ridge y 31..32, x 2148..2452, z 5399..5401, beasts y 33
       middle (hall 2130..2470 / 5470..5550, y_top 30, layers 4)
              -> ridge y 39..40, x 2128..2472, z 5509..5511, beasts y 41
       rear   (hall 2170..2430 / 5570..5650, y_top 22, layers 3)
              -> ridge y 29..30, x 2168..2432, z 5609..5611, beasts y 31
    3. Xuanzheng Dian 宣政殿 (palace_xuanzheng_dian.py): terrace_top 8,
       dougong_y 45; roof call add_ridge_roof(2716, 4856 .. 3284, 5104,
       y=46, layers=5, axis z) -> steps 10, ridge y 56..57, x 2999..3001,
       z 4860..5100, beasts y 58; finials y 58..61 at z 4859..4861 /
       5099..5101.
    4. Zichen Dian 紫宸殿 (palace_zichen_dian.py): terrace_top 6; roof call
       add_ridge_roof(2342, 5182 .. 2638, 5498, y=35, layers=4, axis z,
       ROOF_BLUE) -> steps 8, ridge y 43..44, x 2489..2491, z 5186..5494,
       beasts y 45; finials y 45..48 at z 5185..5187 / 5493..5495.

Distinctive features:
    - Ridge walking-beast queues (正脊走兽) on every main ridge: 7 on
      Hanyuan (split around the rooftop pavilion), 6 on each of the three
      Linde hall ridges, 5 on Xuanzheng and 4 on Zichen; alternating
      gold / gilded-blackstone / white-terracotta bodies on dark plinths.
    - Hip-end beasts (垂兽) at both ends of every main ridge: a dark claw
      block on the ridge top plus a gilded head leaning one block further
      down the roof slope, tucked just inside the existing gold finials.
    - Chiwen horns (鸱吻加高, Hanyuan only): each of the two existing gold
      ridge finials gains a pair of 2-block gold horns curling up and
      outward from its top (y 79..80).
    - Eave tile-end dots (檐口瓦当): quartz / gold single blocks strictly
      alternating with one-block gaps along the front eave edges. Rows
      follow the eave surfaces that really exist: Hanyuan's double-eave
      ring front edge (z 5152, top y 60) and the Linde north eave slabs
      (outer edge z = z1_roof-2); for the axis-z ridge roofs of Xuanzheng
      and Zichen, whose add_ridge_roof only generates west/east eave
      slabs, the rows run along the front half of those real slab outer
      edges instead of floating in mid air.
    - Wing-corner taoshou caps (翼角套兽): a 1x1x2 gilded-blackstone post
      standing on each of the four eave-slab corners of every hall, with
      a gold wind bell (檐角风铃) and a two-block iron chain hanging
      directly beneath the same corner.
"""


def _chui_shou(
    fills: list[Fill],
    label: str,
    x: int,
    y: int,
    z: int,
    dx: int,
    dz: int,
) -> None:
    """垂兽 ridge-end beast: dark claw on the ridge-top level plus a
    gilded head leaning one block further outward/down-slope
    ((dx, dz) points away from the ridge centre)."""
    add_fill(fills, f"{label} claw", (x, y, z), (x, y, z), M.DARK)
    add_fill(fills, f"{label} head", (x + dx, y + 1, z + dz), (x + dx, y + 1, z + dz), M.GOLD_ACCENT)


def _taoshou(fills: list[Fill], label: str, x: int, y: int, z: int) -> None:
    """套兽 wing-corner cap: 1x1x2 gilded post standing on an eave corner."""
    add_fill(fills, f"{label} post", (x, y, z), (x, y + 1, z), M.GOLD_ACCENT)


def _tile_dots(
    fills: list[Fill],
    label: str,
    fixed: int,
    u1: int,
    u2: int,
    y: int,
    axis: str = "x",
) -> None:
    """瓦当 eave tile-ends: strictly alternating quartz/gold single-block
    fills with a one-block gap, running along an eave edge line."""
    for i, u in enumerate(range(u1, u2 + 1, 2)):
        block = M.QUARTZ if i % 2 == 0 else M.GOLD
        if axis == "x":
            add_fill(fills, f"{label} dot {u}", (u, y, fixed), (u, y, fixed), block)
        else:
            add_fill(fills, f"{label} dot {u}", (fixed, y, u), (fixed, y, u), block)


def build_palace_roof_detail_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Hanyuan Dian (含元殿): main ridge y 73..74, x 2999..3001,
    #    z 5148..5512.  Beasts stand at y 75.
    # ------------------------------------------------------------------
    # The 3d overlay's rooftop ge pavilion (x 2960..3040, z 5300..5360,
    # y 71..79) buries the central ridge, so the 7-beast queue splits into
    # a north row of 3 and a south row of 4 around it.
    add_roof_beasts(fills, "palaceroof hanyuan beasts n", 2999, 5152, 3001, 5296, 75, ridge_axis="z", count=3)
    add_roof_beasts(fills, "palaceroof hanyuan beasts s", 2999, 5364, 3001, 5508, 75, ridge_axis="z", count=4)
    # 垂兽 at both ridge ends, just inside the existing gold finials
    # (z 5147..5149 / 5511..5513, y 75..78), heads leaning down-slope.
    _chui_shou(fills, "palaceroof hanyuan chuishou n", 3000, 75, 5151, 0, -1)
    _chui_shou(fills, "palaceroof hanyuan chuishou s", 3000, 75, 5509, 0, 1)
    # 鸱吻加高: a pair of 2-block gold horns on top of each existing ridge
    # finial (finial box x 2998..3002, top y 78, z rz-1..rz+1).
    for rz in (5148, 5512):
        add_fill(fills, f"palaceroof hanyuan chiwen horn wl1 {rz}", (2999, 79, rz), (2999, 79, rz), M.GOLD)
        add_fill(fills, f"palaceroof hanyuan chiwen horn wl2 {rz}", (2998, 80, rz), (2998, 80, rz), M.GOLD)
        add_fill(fills, f"palaceroof hanyuan chiwen horn er1 {rz}", (3001, 79, rz), (3001, 79, rz), M.GOLD)
        add_fill(fills, f"palaceroof hanyuan chiwen horn er2 {rz}", (3002, 80, rz), (3002, 80, rz), M.GOLD)
    # Wind bells hanging under the four eave-slab corners (slab at y 60),
    # each corner capped by a gilded taoshou post above the slab.
    add_eave_bells(fills, "palaceroof hanyuan bells", [
        (2622, 57, 5141), (3378, 57, 5141),
        (2622, 57, 5519), (3378, 57, 5519),
    ])
    for tx, tz in [(2622, 5141), (3378, 5141), (2622, 5519), (3378, 5519)]:
        _taoshou(fills, f"palaceroof hanyuan taoshou {tx},{tz}", tx, 61, tz)
    # 瓦当 row on the front (south) edge of the double-eave ring top
    # (ring top y 60 at z 5152; the main-roof stairs at y 61 only cover
    # x <= 2655 / x >= 3345, so the row spans the clear centre).
    _tile_dots(fills, "palaceroof hanyuan tiles", 5152, 2940, 3060, 61, axis="x")

    # ------------------------------------------------------------------
    # 2. Linde Hall (麟德殿): three joined halls, ridge axis x, one beast
    #    queue per ridge plus hip-end beasts, bells, taoshou and tiles.
    # ------------------------------------------------------------------
    linde_halls = [
        # name,    rx1,  rx2,   cz,   beast_y, slab_y, sx1,  sx2,  zn,   zs,   tile_x1, tile_x2
        ("front",  2148, 2452, 5400, 33,      24,     2141, 2459, 5342, 5458, 2260,    2340),
        ("middle", 2128, 2472, 5510, 41,      30,     2121, 2479, 5462, 5558, 2260,    2340),
        ("rear",   2168, 2432, 5610, 31,      22,     2161, 2439, 5562, 5658, 2270,    2330),
    ]
    for name, rx1, rx2, cz, beast_y, slab_y, sx1, sx2, zn, zsl, tu1, tu2 in linde_halls:
        add_roof_beasts(fills, f"palaceroof linde {name} beasts", rx1, cz - 1, rx2, cz + 1, beast_y, ridge_axis="x", count=6)
        # 垂兽 claw right on top of each ridge end block, head leaning out.
        _chui_shou(fills, f"palaceroof linde {name} chuishou w", rx1, beast_y, cz, -1, 0)
        _chui_shou(fills, f"palaceroof linde {name} chuishou e", rx2, beast_y, cz, 1, 0)
        # Bells under the four eave-slab corners; taoshou posts above them.
        add_eave_bells(fills, f"palaceroof linde {name} bells", [
            (sx1, slab_y - 3, zn), (sx2, slab_y - 3, zn),
            (sx1, slab_y - 3, zsl), (sx2, slab_y - 3, zsl),
        ])
        for tx, tz in [(sx1, zn), (sx2, zn), (sx1, zsl), (sx2, zsl)]:
            _taoshou(fills, f"palaceroof linde {name} taoshou {tx},{tz}", tx, slab_y + 1, tz)
        # 瓦当 row along the front (north) eave slab outer edge.
        _tile_dots(fills, f"palaceroof linde {name} tiles", zn, tu1, tu2, slab_y + 1, axis="x")

    # ------------------------------------------------------------------
    # 3. Xuanzheng Dian (宣政殿): main ridge y 56..57, x 2999..3001,
    #    z 4860..5100.  Beasts stand at y 58.
    # ------------------------------------------------------------------
    add_roof_beasts(fills, "palaceroof xuanzheng beasts", 2999, 4860, 3001, 5100, 58, ridge_axis="z", count=5)
    # 垂兽 inside the finials (z 4859..4861 / 5099..5101, y 58..61).
    _chui_shou(fills, "palaceroof xuanzheng chuishou n", 3000, 58, 4863, 0, -1)
    _chui_shou(fills, "palaceroof xuanzheng chuishou s", 3000, 58, 5097, 0, 1)
    # Axis-z ridge roof: only west/east eave slabs exist (y 45, x
    # 2692..2696 / 3304..3308, z 4853..5107).  Hang bells under their end
    # corners and cap the corners with taoshou posts.
    add_eave_bells(fills, "palaceroof xuanzheng bells", [
        (2692, 42, 4853), (3308, 42, 4853),
        (2692, 42, 5107), (3308, 42, 5107),
    ])
    for tx, tz in [(2692, 4853), (3308, 4853), (2692, 5107), (3308, 5107)]:
        _taoshou(fills, f"palaceroof xuanzheng taoshou {tx},{tz}", tx, 46, tz)
    # 瓦当 rows along the front half of those real slab outer edges.
    _tile_dots(fills, "palaceroof xuanzheng tiles w", 2692, 4854, 4882, 46, axis="z")
    _tile_dots(fills, "palaceroof xuanzheng tiles e", 3308, 4854, 4882, 46, axis="z")

    # ------------------------------------------------------------------
    # 4. Zichen Dian (紫宸殿): main ridge y 43..44, x 2489..2491,
    #    z 5186..5494.  Beasts stand at y 45.
    # ------------------------------------------------------------------
    add_roof_beasts(fills, "palaceroof zichen beasts", 2489, 5186, 2491, 5494, 45, ridge_axis="z", count=4)
    # 垂兽 inside the finials (z 5185..5187 / 5493..5495, y 45..48).
    _chui_shou(fills, "palaceroof zichen chuishou n", 2490, 45, 5189, 0, -1)
    _chui_shou(fills, "palaceroof zichen chuishou s", 2490, 45, 5491, 0, 1)
    # Eave slabs at y 34 (x 2340..2344 / 2636..2640, z 5179..5501).
    add_eave_bells(fills, "palaceroof zichen bells", [
        (2340, 31, 5179), (2640, 31, 5179),
        (2340, 31, 5501), (2640, 31, 5501),
    ])
    for tx, tz in [(2340, 5179), (2640, 5179), (2340, 5501), (2640, 5501)]:
        _taoshou(fills, f"palaceroof zichen taoshou {tx},{tz}", tx, 35, tz)
    _tile_dots(fills, "palaceroof zichen tiles w", 2340, 5180, 5208, 35, axis="z")
    _tile_dots(fills, "palaceroof zichen tiles e", 2640, 5180, 5208, 35, axis="z")


def main() -> None:
    run_builder(build_palace_roof_detail_3d, "palace_roof_detail_3d")


if __name__ == "__main__":
    main()
