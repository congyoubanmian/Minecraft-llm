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
    run_builder,
)


"""
Night Lighting 3D (唐长安城·全城夜景照明工程) - the city-wide night
illumination overlay. Lights the capital up after dark: a runway of flush
cold-light pavement lamps along the imperial Zhuque Avenue, glowing eave
corner and ridge-end beacons outlining the eight landmark buildings, low
plinth lamps ringing both great lakes, shop-front hanging lanterns along
the two market cross streets, and deck lights on the two great bridges.

All coordinates are local city coords read from the source modules:
    road_paving.py            Zhuque Avenue deck y=2 (x 2972..3028)
    street_facilities.py      existing median posts x 2960/3040 (z % 80 == 0)
    lantern_festival.py       canopy lamps x 2970/2990/3010/3030 (z % 120 == 80)
    palace_hanyuan_dian.py    Hanyuan roof x 2624..3376, z 5144..5516, y 61, layers 6
    palace_hanyuan_3d.py      rooftop ge pavilion x 2960..3040, z 5270..5330
    palace_linde_3d.py        front/middle/rear hall ridge roofs (axis x)
    palace_xuanzheng_dian.py  roof x 2716..3284, z 4856..5104, y 46, layers 5
    palace_zichen_dian.py     roof x 2342..2638, z 5182..5498, y 35, layers 4
    gate_zhuque_men.py        5 passages x 2968..3032 step 16, arch crown y 45
    gate_mingde_men.py        5 passages x 2952..3048 step 24, arch crown y 43
    imperial_daming_palace.py Danfeng passages x 2964..3036 step 18, crown y 22;
                              Taiye Pool x 2780..3220, z 5500..5740, water y 2
    bell_drum_3d.py           bell (2200, 4200), drum (3800, 4200), roof y 38
    qujiang_pool_3d.py        Qujiang Pool x 5060..5940, z 5320..5920, water y 1;
                              curved bridge rails x 5516/5524, z 5340..5860
    bridge_stone_arch.py      taiye_bridge rails z 5542/5558, x 2970..3030
    market_block.py           street width 12; block streets x 1300/4780, z 2600

Sections (分区清单):
    1. 朱雀大街轮廓灯 Zhuque Avenue axis lights - pairs of flush pavement
       SEA_LANTERNs at x 2985 / 3015, z 700..5900 every 80 (the brief's
       every-40 is doubled to hold the 300-500 fill budget; the grid is
       staggered against the existing 80-grid posts). Level taken from
       road_paving.py: the avenue deck surface is y=2, so lamps embed
       flush at y=2 (not the guessed y=4).
    2. 地标轮廓灯 Landmark outline lights - every great hall gets 4 glowing
       eave-corner beacons + 2 ridge-end beacons (SEA_LANTERN on a RED_WOOL
       pedestal): Hanyuan / Linde (front+middle+rear) / Xuanzheng / Zichen
       Dian and the Bell / Drum Towers; plus a 5-light row embedded in each
       gate-passage crown at Zhuque Men, Mingde Men and Danfeng Men.
    3. 太液池/曲江池岸灯 Lakeshore lamps - ANDESITE plinth + SEA_LANTERN
       "矮脚灯" 5 blocks inside each pool rim: Taiye every 30 on the N/S
       shores and 60 on the W/E shores; Qujiang every 80 on the N/S shores
       and 60 on the W/E shores (gap-aligned with the shore boardwalks).
    4. 东西市主街灯棚 Market hanging lamps - FENCE bracket + LANTERN along
       the true market cross streets (block street centrelines x 1300 /
       4780 and z 2600, width 12 per market_block.py), every 100, sides
       zigzagging so each lamp mounts on a shop facade.
    5. 坊门预埋 Ward gate pre-wiring - out of scope, skipped by design.
    6. 桥索灯 Bridge deck lights - SEA_LANTERN on the railing crowns of
       taiye_bridge (every 5 per the brief) and the Qujiang curved bridge
       (every 50; every-5 over the 520-block span alone would need 200+
       lamps and exceed the whole module budget).

Existing lantern lines respected (new lights kept >= 6 blocks away):
    street_facilities.py avenue posts (3x3, y 3..9) at x 2960/3040 and the
    avenue grids; lantern_festival.py canopy lamps at x 2970/2990/3010/3030;
    gates_south_3d.py passage-mouth lanterns (2993/3007, y6, z +-47) and
    (2992/3008, y6, z -152/-28); market_block.py per-block street posts
    every 30; night_market.py y=13 lamp strips; market_details.py y=8
    lantern strings; qujiang_night_3d.py festival boats, tents, piers and
    guide posts (the Qujiang north-shore lamp at x 5865 is skipped to keep
    clear of the tent landing piers); palace_hanyuan_dian.py approach lamp
    posts x 2960/3040, z 5060..5180.

Distinctive features (English):
    - Imperial-axis "runway": 132 flush cold-light pavement lamps doubling
      the rhythm of the existing median posts along all 5.2 km of Zhuque
      Avenue
    - Gilded-night skyline: four eave-corner beacons plus twin ridge-end
      beacons on red wool pedestals outline every great hall roof against
      the dark
    - Five-light gate crowns seated inside the arch vaults of all three
      great gates (Zhuque / Mingde / Danfeng)
    - Lakeshore plinth lamps standing in the shallow water margin of Taiye
      and Qujiang, mirrored north-south and east-west
    - Shop-front hanging lanterns on dark-oak bracket arms zigzagging down
      both market cross streets
    - Railing-crown bridge lights on the Taiye and Qujiang crossings
"""


# ---------------------------------------------------------------------------
# Section 1 - Zhuque Avenue axis lights (朱雀大街轮廓灯).
# ---------------------------------------------------------------------------
# Avenue deck surface is y=2 (road_paving.py "avenue x=3000 road"); the
# imperial strip / curbs (x 2992..3008) are untouched. z grid sits at
# z % 80 == 60 while existing street_facilities posts sit at z % 80 == 0.
ZHUQUE_AXIS_XS = (2985, 3015)
ZHUQUE_AXIS_ZS = range(700, 5901, 80)  # 700..5900 inclusive -> 66 pairs


# ---------------------------------------------------------------------------
# Section 2 - Landmark outline lights (地标轮廓灯).
# ---------------------------------------------------------------------------
# Each entry: (name, eave-corner (x,z) list, corner light y,
#              ridge-end (x,z) list, ridge light y).
# Corner lights sit one block above the eave slab corner (RED_WOOL pedestal
# replaces the slab corner block); ridge-end lights cap the gold ridge
# finials (pedestal replaces the finial top block).
LANDMARK_OUTLINES = [
    ("hanyuan",
     [(2622, 5141), (2622, 5519), (3378, 5141), (3378, 5519)], 61,
     [(3000, 5148), (3000, 5512)], 79),
    ("linde front",
     [], 0,
     [(2148, 5400), (2452, 5400)], 37),
    ("linde middle",
     [(2121, 5462), (2479, 5462), (2121, 5558), (2479, 5558)], 31,
     [(2128, 5510), (2472, 5510)], 45),
    ("linde rear",
     [], 0,
     [(2168, 5610), (2432, 5610)], 35),
    ("xuanzheng",
     [(2714, 4853), (2714, 5107), (3286, 4853), (3286, 5107)], 46,
     [(3000, 4860), (3000, 5100)], 62),
    ("zichen",
     [(2340, 5179), (2340, 5501), (2640, 5179), (2640, 5501)], 35,
     [(2490, 5186), (2490, 5494)], 49),
    ("bell tower",
     [(2187, 4188), (2213, 4188), (2187, 4212), (2213, 4212)], 38,
     [(2194, 4200), (2206, 4200)], 52),
    ("drum tower",
     [(3787, 4188), (3813, 4188), (3787, 4212), (3813, 4212)], 38,
     [(3794, 4200), (3806, 4200)], 52),
]

# Gate-passage crown lights: (gx, crown y, inner wall plane z). Each light
# seats in the carved arch crown with solid tower wall directly above.
GATE_CROWNS = [
    ("zhuque men", [(gx, 45, 41) for gx in (2968, 2984, 3000, 3016, 3032)]),
    ("mingde men", [(gx, 43, -37) for gx in (2952, 2976, 3000, 3024, 3048)]),
    ("danfeng men", [(gx, 22, 4149) for gx in (2964, 2982, 3000, 3018, 3036)]),
]


# ---------------------------------------------------------------------------
# Section 3 - Lakeshore lamps (太液池/曲江池岸灯), pool rims inset by 5.
# ---------------------------------------------------------------------------
# Taiye Pool water surface y=2 -> plinth y=2, lamp y=3.
# Qujiang Pool water surface y=1 -> plinth y=1, lamp y=2.
TAIYE_X1, TAIYE_X2 = 2785, 3215
TAIYE_Z_N, TAIYE_Z_S = 5505, 5735
TAIYE_W_E_ZS = range(5535, 5656, 60)          # 3 per short shore
QUJIANG_X1, QUJIANG_X2 = 5065, 5935
QUJIANG_Z_N, QUJIANG_Z_S = 5325, 5915
QUJIANG_W_E_ZS = range(5380, 5801, 60)        # 8 per shore, boardwalk gaps
# Skip: qujiang_night_3d tent piers occupy x 5806..5862 at z 5318..5322.
QUJIANG_N_SKIP_XS = {5865}


# ---------------------------------------------------------------------------
# Section 4 - Market hanging lamps (东西市主街灯棚).
# ---------------------------------------------------------------------------
# True block-street centrelines (market_block.py BLOCK_SIZE=120 grid);
# street width 12, so facade arms sit at centre +-7 with the lantern at
# +-6 over the street edge. Lamp rows zigzag side to side.
MARKETS = [
    ("west market", 1300, 2600, 785, 1735),
    ("east market", 4780, 2600, 4265, 5215),
]
MARKET_VERTICAL_ZS = range(2085, 3036, 100)   # 10 per vertical street
MARKET_ARM_Y = 7                              # bracket y, lantern at 6


# ---------------------------------------------------------------------------
# Section 6 - Bridge deck lights (桥索灯).
# ---------------------------------------------------------------------------
# taiye_bridge (bridge_stone_arch.py): rails z 5542/5558, top y 7, centre
# pavilion body x 2995..3005 is skipped. Qujiang curved bridge
# (qujiang_pool_3d.py): rails x 5516/5524, top y 7, mid-lake pavilion
# z 5594..5606 stays clear at the every-50 grid.
TAIYE_BRIDGE_RAIL_ZS = (5542, 5558)
TAIYE_BRIDGE_XS = (2970, 2975, 2980, 2985, 2990,
                   3010, 3015, 3020, 3025, 3030)
TAIYE_BRIDGE_Y = 8
QUJIANG_BRIDGE_RAIL_XS = (5516, 5524)
QUJIANG_BRIDGE_ZS = range(5340, 5861, 50)     # 11 per rail
QUJIANG_BRIDGE_Y = 8


# ---------------------------------------------------------------------------
# Reusable light primitives.
# ---------------------------------------------------------------------------
def _flush_light(fills: list[Fill], label: str, x: int, z: int, y: int) -> None:
    """Embedded pavement light (嵌入式地灯): one SEA_LANTERN set flush into
    the road/ground surface level."""
    add_fill(fills, f"{label} lamp", (x, y, z), (x, y, z), M.SEA_LANTERN)


def _ground_light(fills: list[Fill], label: str, x: int, z: int, y: int) -> None:
    """Low shore lamp (矮脚灯): 3x3 ANDESITE plinth ring with one SEA_LANTERN
    centred on top - the plinth kerbs the lamp on all four sides."""
    add_fill(fills, f"{label} plinth", (x - 1, y - 1, z - 1), (x + 1, y - 1, z + 1), M.ANDESITE)
    add_fill(fills, f"{label} lamp", (x, y, z), (x, y, z), M.SEA_LANTERN)


def _outline_corner(fills: list[Fill], label: str, x: int, y: int, z: int) -> None:
    """Roof outline beacon (轮廓角灯): RED_WOOL pedestal at y-1 with a
    SEA_LANTERN blazing one block above it."""
    add_fill(fills, f"{label} pedestal", (x, y - 1, z), (x, y - 1, z), M.RED_WOOL)
    add_fill(fills, f"{label} lamp", (x, y, z), (x, y, z), M.SEA_LANTERN)


def _point_light(fills: list[Fill], label: str, x: int, y: int, z: int) -> None:
    """Single SEA_LANTERN point light (gate crowns, bridge deck lights)."""
    add_fill(fills, f"{label} lamp", (x, y, z), (x, y, z), M.SEA_LANTERN)


def _hanging_lamp(fills: list[Fill], label: str, x: int, y: int, z: int) -> None:
    """Shop-front hanging lamp (悬灯): dark-oak fence bracket arm with a
    warm LANTERN hanging one block below it."""
    add_fill(fills, f"{label} arm", (x, y, z), (x, y, z), M.FENCE)
    add_fill(fills, f"{label} lamp", (x, y - 1, z), (x, y - 1, z), M.LANTERN)


# ---------------------------------------------------------------------------
# Section builders.
# ---------------------------------------------------------------------------
def build_zhuque_axis_lights(fills: list[Fill]) -> None:
    """Section 1 - flush pavement light pairs down the Zhuque Avenue axis."""
    for z in ZHUQUE_AXIS_ZS:
        _flush_light(fills, f"nightlight zhuque axis w {z}", 2985, z, 2)
        _flush_light(fills, f"nightlight zhuque axis e {z}", 3015, z, 2)


def build_landmark_outline_lights(fills: list[Fill]) -> None:
    """Section 2 - eave-corner and ridge-end beacons on the great halls,
    towers, and the five-light crowns of the three great gates."""
    for name, corners, corner_y, ridges, ridge_y in LANDMARK_OUTLINES:
        for x, z in corners:
            _outline_corner(fills, f"nightlight {name} eave", x, corner_y, z)
        for x, z in ridges:
            _outline_corner(fills, f"nightlight {name} ridge", x, ridge_y, z)
    for name, lights in GATE_CROWNS:
        for gx, gy, gz in lights:
            _point_light(fills, f"nightlight {name} crown", gx, gy, gz)


def _shore_row(
    fills: list[Fill],
    label: str,
    lamp_y: int,
    points: list[tuple[int, int]],
) -> None:
    for x, z in points:
        _ground_light(fills, f"nightlight {label} {x},{z}", x, z, lamp_y)


def build_lakeshore_lights(fills: list[Fill]) -> None:
    """Section 3 - low plinth lamps ringing Taiye Pool and Qujiang Pool,
    5 blocks inside each pool rim."""
    # Taiye Pool (water y=2): long N/S shores every 30, short W/E every 60.
    _shore_row(fills, "taiye shore n", 3,
               [(x, TAIYE_Z_N) for x in range(TAIYE_X1, TAIYE_X2 + 1, 30)])
    _shore_row(fills, "taiye shore s", 3,
               [(x, TAIYE_Z_S) for x in range(TAIYE_X1, TAIYE_X2 + 1, 30)])
    _shore_row(fills, "taiye shore w", 3,
               [(TAIYE_X1, z) for z in TAIYE_W_E_ZS])
    _shore_row(fills, "taiye shore e", 3,
               [(TAIYE_X2, z) for z in TAIYE_W_E_ZS])
    # Qujiang Pool (water y=1): N/S shores every 80, W/E every 60 aligned
    # with the boardwalk gaps; skip the north point blocked by tent piers.
    north = [x for x in range(QUJIANG_X1, QUJIANG_X2 + 1, 80)
             if x not in QUJIANG_N_SKIP_XS]
    _shore_row(fills, "qujiang shore n", 2,
               [(x, QUJIANG_Z_N) for x in north])
    _shore_row(fills, "qujiang shore s", 2,
               [(x, QUJIANG_Z_S) for x in range(QUJIANG_X1, QUJIANG_X2 + 1, 80)])
    _shore_row(fills, "qujiang shore w", 2,
               [(QUJIANG_X1, z) for z in QUJIANG_W_E_ZS])
    _shore_row(fills, "qujiang shore e", 2,
               [(QUJIANG_X2, z) for z in QUJIANG_W_E_ZS])


def build_market_hanging_lamps(fills: list[Fill]) -> None:
    """Section 4 - bracket-hung lanterns along both market cross streets."""
    for name, street_x, street_z, hx1, hx2 in MARKETS:
        # Vertical main street: arms alternate west/east facades.
        for k, z in enumerate(MARKET_VERTICAL_ZS):
            arm_x = street_x - 7 if k % 2 == 0 else street_x + 7
            _hanging_lamp(fills, f"nightlight {name} hang v {z}", arm_x, MARKET_ARM_Y, z)
        # Horizontal main street: arms alternate north/south facades.
        for k, x in enumerate(range(hx1, hx2 + 1, 100)):
            arm_z = street_z - 7 if k % 2 == 0 else street_z + 7
            _hanging_lamp(fills, f"nightlight {name} hang h {x}", x, MARKET_ARM_Y, arm_z)


def build_bridge_lights(fills: list[Fill]) -> None:
    """Section 6 - railing-crown deck lights on the two great bridges."""
    for x in TAIYE_BRIDGE_XS:
        for rz in TAIYE_BRIDGE_RAIL_ZS:
            _point_light(fills, f"nightlight taiye bridge {x}", x, TAIYE_BRIDGE_Y, rz)
    for z in QUJIANG_BRIDGE_ZS:
        for rx in QUJIANG_BRIDGE_RAIL_XS:
            _point_light(fills, f"nightlight qujiang bridge {z}", rx, QUJIANG_BRIDGE_Y, z)


def build_night_lighting_3d(fills: list[Fill]) -> None:
    """City-wide night lighting overlay - add-only, label 'nightlight '."""
    # 1. Zhuque Avenue axis pavement lights.
    build_zhuque_axis_lights(fills)
    # 2. Landmark outline lights (8 buildings incl. both tower gates).
    build_landmark_outline_lights(fills)
    # 3. Taiye / Qujiang lakeshore lamps.
    build_lakeshore_lights(fills)
    # 4. East & West market main-cross hanging lamps.
    build_market_hanging_lamps(fills)
    # 5. Ward gate pre-wiring: out of scope, skipped by design.
    # 6. Taiye / Qujiang bridge deck lights.
    build_bridge_lights(fills)


def main() -> None:
    run_builder(build_night_lighting_3d, "night_lighting_3d")


if __name__ == "__main__":
    main()
