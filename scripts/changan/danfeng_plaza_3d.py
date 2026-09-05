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
    add_outline,
    add_pixel_mural,
    add_ridge_roof,
    run_builder,
)


"""
Danfeng Gate Plaza - Imperial Ceremony Forecourt (丹凤门广场·皇家仪典).

The grand forecourt south of Danfengmen, the main gate of the Daming
Palace, where the whole court assembled for the New Year Grand Audience
(元日大朝会).

Location in Chang'an city local coordinates:
    Plaza deck: x 2700..3300, z 3940..4040, paving at y4; all structures
    rise from y5 (ground level y0-4).
    Danfengmen gate tower (imperial_daming_palace.py): body x 2945..3055 /
    z 4050..4150 (y 23..58), five AIR passages (x 2959..2969, 2977..2987,
    2995..3005, 3013..3023, 3031..3041) carved y1..22 through z 4045..4155,
    ridge roof from y59 with eaves slabs at y58 reaching z 4039.
    AVOIDANCE: no fill of this module enters the protected tower rectangle
    x 2945..3055 / z 4045..4155. The axis road paving stops at z 4044
    (abutting the passage mouths without covering them), the flanking
    link-galleries stop at x 2944 / start at x 3056, and the stone lions
    stand at z <= 4044 beside the central gateway, so the tower body,
    passages and roof are never touched; the only contact with the gate is
    at the passage positions, as required.
    The twin que platforms stay inside x 2860..3150 so they never reach
    the older daming que mounds at x 2828..2872 / x 3128..3172.

Distinctive features:
    - Grand stone parquet plaza: polished-andesite outer ring, smooth-stone
      middle field with parquet stripes and a square medallion, and a
      gold-edged imperial axis road (御道) running from the central gate
      passage straight to the plaza's south rim
    - Twin masonry que platforms (阙台, the real excavated form of
      Danfengmen) flanking the gate: three stepped, inward-tapering
      sections with flat tops and alternating smooth-stone / iron-bar
      crenellations, joined to the gate tower by single-storey walled
      galleries to form the historic "凹" plan opening south
    - Dismount steles (下马碑) at the east and west plaza entrances:
      deepslate pedestal, quartz-pillar shaft, gold cap, and a pixel mural
      of the eight characters "文武官员至此下马" (all civil and military
      officials dismount here)
    - Ceremonial banner array (仪仗旗阵): five dark-oak poles on each side
      of the axis, each with a three-band red/gold flag and a sea-lantern
      finial
    - Officials' waiting galleries (百官待朝廊) on both plaza edges: open
      colonnades with overhanging gable roofs, stone benches and long
      stone tables
    - Paired guardian lions (石狮) with gold brocade balls beside the
      central gate opening, and tall palace lamp posts at the four plaza
      corners
"""

# Plaza deck bounds (south forecourt of Danfengmen).
PX1, PZ1 = 2700, 3940
PX2, PZ2 = 3300, 4040
DECK_Y = 4  # paving level; structures start at y5

# Central gate passage of Danfengmen (gx = 3000) and its axis road.
GATE_CX = 3000
ROAD_X1, ROAD_X2 = 2992, 3008  # gold edging lines; interior 2993..3007
ROAD_Z1, ROAD_Z2 = 3940, 4044  # stops short of the AIR passage at z 4045

# Twin que platforms (west / east), inside x 2860..3150.
QUE_W_CX, QUE_E_CX, QUE_CZ = 2900, 3100, 4070

# Link galleries joining the que platforms to the gate tower walls.
# Body / roof / bridge x-ranges are chosen so every fill stays outside
# x 2945..3055 (the protected tower + passage rectangle).
LINK_W = dict(fx1=2911, fx2=2944, rx1=2911, rx2=2941, bx1=2942, bx2=2944)
LINK_E = dict(fx1=3056, fx2=3089, rx1=3059, rx2=3089, bx1=3056, bx2=3058)
LINK_Z1, LINK_Z2 = 4062, 4072

# Officials' waiting galleries on the plaza's east / west edges.
GAL_W = (2704, 2722, 3950, 4025)
GAL_E = (3278, 3296, 3950, 4025)

# Dismount steles at the plaza's east / west entrances.
STEle_W_CX, STELE_E_CX, STELE_CZ = 2713, 3287, 4034

# Banner array: five poles each side of the axis.
BANNER_XS = (2965, 3035)
BANNER_ZS = (4020, 4000, 3980, 3960, 3944)

# Stele shaft block (quartz pillar is not in the shared palette).
STELE_SHAFT = "minecraft:quartz_pillar"

# Inscription glyphs for the dismount steles: 文武官员至此下马, each
# rendered as a stylised 4x4 stroke cell ("字意象", not literal calligraphy).
_GLYPHS = [
    [".##.", "#..#", ".##.", "#..#"],  # 文
    ["#..#", "####", "..#.", "..#."],  # 武
    ["####", ".##.", "#.#.", ".##."],  # 官
    [".##.", "#..#", ".##.", ".#.."],  # 员
    ["####", "..#.", ".##.", ".##."],  # 至
    ["#.#.", "####", "..#.", "..#."],  # 此
    ["####", "..#.", "..#.", ".#.."],  # 下
    [".##.", "#.##", ".##.", ".#.."],  # 马
]


def _stele_inscription() -> list[str]:
    """Lay the eight glyphs out as a 9x19 mural: 2 columns x 4 rows of
    4x4 cells with 1px gutters, right column (文武官员) read first."""
    rows: list[str] = []
    for gr in range(4):
        for gr_row in range(4):
            rows.append(_GLYPHS[4 + gr][gr_row] + "." + _GLYPHS[gr][gr_row])
        if gr < 3:
            rows.append(".........")
    return rows


def _crenellations(
    fills: list[Fill],
    label: str,
    x1: int, z1: int, x2: int, z2: int,
    y: int,
    unit: int = 3,
) -> None:
    """Battlement ring (垛口) alternating smooth stone and iron bars."""
    sides = [
        [(x, z1) for x in range(x1, x2 + 1)],
        [(x, z2) for x in range(x1, x2 + 1)],
        [(x1, z) for z in range(z1 + 1, z2)],
        [(x2, z) for z in range(z1 + 1, z2)],
    ]
    for si, cells in enumerate(sides):
        t = 0
        while t < len(cells):
            end = min(t + unit, len(cells))
            block = M.SMOOTH if (t // unit) % 2 == 0 else M.IRON_BARS
            sx, sz = cells[t]
            ex, ez = cells[end - 1]
            add_fill(fills, f"{label} s{si} {t}", (sx, y, sz), (ex, y, ez), block)
            t = end


def _que_tower(fills: list[Fill], label: str, cx: int, cz: int) -> None:
    """Square que platform (阙台): three tapering sections, flat top, battlements."""
    add_fill(fills, f"{label} tier1", (cx - 10, 4, cz - 10), (cx + 10, 10, cz + 10), M.STONE)
    add_outline(fills, f"{label} tier1 cap", cx - 10, cz - 10, cx + 10, cz + 10, 10, 10, M.SMOOTH)
    add_fill(fills, f"{label} tier2", (cx - 7, 11, cz - 7), (cx + 7, 16, cz + 7), M.STONE)
    add_outline(fills, f"{label} tier2 cap", cx - 7, cz - 7, cx + 7, cz + 7, 16, 16, M.SMOOTH)
    add_fill(fills, f"{label} tier3", (cx - 4, 17, cz - 4), (cx + 4, 22, cz + 4), M.SMOOTH)
    _crenellations(fills, f"{label} crenel", cx - 4, cz - 4, cx + 4, cz + 4, 23)


def _link_gallery(
    fills: list[Fill],
    label: str,
    fx1: int, fx2: int, rx1: int, rx2: int, bx1: int, bx2: int,
    z1: int, z2: int,
) -> None:
    """Single-storey walled gallery (廊庑) linking a que platform to the
    gate tower wall. rx/br ranges must stay outside x 2945..3055."""
    add_fill(fills, f"{label} floor", (fx1, DECK_Y, z1), (fx2, DECK_Y, z2), M.SMOOTH)
    # Low red parapet walls on both long sides, open above.
    add_fill(fills, f"{label} wall n", (fx1, 5, z1), (fx2, 7, z1), M.RED_WALL)
    add_fill(fills, f"{label} wall s", (fx1, 5, z2), (fx2, 7, z2), M.RED_WALL)
    # Dark-oak columns rising from the parapet to the eave.
    for col_x in (fx1 + 1, (fx1 + fx2) // 2, fx2 - 2):
        add_fill(fills, f"{label} col n {col_x}", (col_x, 8, z1), (col_x, 12, z1), M.LOG)
        add_fill(fills, f"{label} col s {col_x}", (col_x, 8, z2), (col_x, 12, z2), M.LOG)
    add_ridge_roof(fills, f"{label} roof", rx1, z1, rx2, z2, 13, layers=2, ridge_axis="x")
    # Tie beam bridging the last bays up to the gate tower wall.
    add_fill(fills, f"{label} tie beam", (bx1, 13, z1), (bx2, 13, z2), M.WOOD)


def _dismount_stele(fills: list[Fill], label: str, cx: int, cz: int) -> None:
    """下马碑: deepslate pedestal, quartz-pillar shaft, gold cap, mural."""
    add_fill(fills, f"{label} pedestal", (cx - 3, 5, cz - 3), (cx + 3, 6, cz + 3), M.DARK)
    add_fill(fills, f"{label} pedestal step", (cx - 2, 7, cz - 2), (cx + 2, 7, cz + 2), M.DARK)
    add_fill(fills, f"{label} shaft", (cx - 1, 8, cz - 5), (cx + 1, 27, cz + 5), STELE_SHAFT)
    add_pixel_mural(
        fills, f"{label} inscription", _stele_inscription(), {"#": M.DARK},
        cx, 26, cz - 4, axis="z",
    )
    add_fill(fills, f"{label} cap", (cx - 2, 28, cz - 4), (cx + 2, 29, cz + 4), M.GOLD)
    add_fill(fills, f"{label} finial", (cx - 1, 30, cz - 1), (cx + 1, 30, cz + 1), M.GOLD)
    add_fill(fills, f"{label} orb", (cx, 31, cz), (cx, 31, cz), M.GOLD)


def _banner_pole(fills: list[Fill], label: str, px: int, pz: int) -> None:
    """仪仗旗杆: log pole, three-band red/gold flag, sea-lantern finial."""
    add_fill(fills, f"{label} pole", (px, 5, pz), (px, 17, pz), M.LOG)
    add_fill(fills, f"{label} lamp", (px, 18, pz), (px, 18, pz), M.SEA_LANTERN)
    # Flag hangs west of the pole in three 2x2 bands: red / gold / red.
    add_fill(fills, f"{label} flag red1", (px - 2, 12, pz), (px - 1, 13, pz), M.RED_WOOL)
    add_fill(fills, f"{label} flag gold", (px - 2, 14, pz), (px - 1, 15, pz), M.GOLD)
    add_fill(fills, f"{label} flag red2", (px - 2, 16, pz), (px - 1, 17, pz), M.RED_WOOL)


def _waiting_gallery(fills: list[Fill], label: str, x1: int, x2: int, z1: int, z2: int) -> None:
    """百官待朝廊: open colonnade, gable roof, stone benches and long tables."""
    for cz in (z1, (z1 + z2) // 2, z2):
        for cx in (x1, x2):
            add_fill(fills, f"{label} col {cx},{cz}", (cx, 5, cz), (cx, 13, cz), M.LOG)
    add_ridge_roof(fills, f"{label} roof", x1, z1, x2, z2, 14, layers=2, ridge_axis="z")
    # Ridge spine beam closing the gable slit.
    add_fill(fills, f"{label} spine", ((x1 + x2) // 2, 14, z1 + 2), ((x1 + x2) // 2, 17, z2 - 2), M.LOG)
    # Stone benches along both sides.
    add_fill(fills, f"{label} bench w", (x1 + 4, 5, z1 + 4), (x1 + 4, 5, z2 - 4), M.SMOOTH)
    add_fill(fills, f"{label} bench e", (x2 - 4, 5, z1 + 4), (x2 - 4, 5, z2 - 4), M.SMOOTH)
    # Two long stone tables (条案) on log legs.
    for tz in (z1 + 10, z2 - 26):
        add_fill(fills, f"{label} table {tz}", (x1 + 8, 10, tz), (x1 + 10, 10, tz + 16), M.SMOOTH)
        add_fill(fills, f"{label} table leg a {tz}", (x1 + 8, 5, tz + 2), (x1 + 8, 9, tz + 2), M.LOG)
        add_fill(fills, f"{label} table leg b {tz}", (x1 + 10, 5, tz + 14), (x1 + 10, 9, tz + 14), M.LOG)


def _stone_lion(fills: list[Fill], label: str, cx: int, cz: int) -> None:
    """Guardian lion (石狮): smooth-stone plinth, quartz body, gold ball.

    Faces south toward the plaza; footprint 9x7, entirely at z <= 4044 so
    it never enters the protected gate rectangle.
    """
    add_fill(fills, f"{label} plinth", (cx - 4, 5, cz - 3), (cx + 4, 5, cz + 3), M.SMOOTH)
    add_fill(fills, f"{label} haunch", (cx - 2, 6, cz - 1), (cx + 2, 10, cz + 2), M.QUARTZ)
    add_fill(fills, f"{label} chest", (cx - 2, 6, cz - 3), (cx + 2, 12, cz - 2), M.QUARTZ)
    add_fill(fills, f"{label} head", (cx - 1, 13, cz - 3), (cx + 1, 15, cz - 1), M.QUARTZ)
    add_fill(fills, f"{label} ear w", (cx - 1, 16, cz - 3), (cx - 1, 16, cz - 3), M.GOLD)
    add_fill(fills, f"{label} ear e", (cx + 1, 16, cz - 3), (cx + 1, 16, cz - 3), M.GOLD)
    add_fill(fills, f"{label} brocade ball", (cx - 4, 6, cz - 2), (cx - 3, 7, cz - 1), M.GOLD)


def _palace_lamp(fills: list[Fill], label: str, cx: int, cz: int) -> None:
    """Corner palace lamp post (宫灯柱): tall pole with a lamp cluster."""
    add_fill(fills, f"{label} base", (cx - 1, 5, cz - 1), (cx + 1, 5, cz + 1), M.DARK)
    add_fill(fills, f"{label} pole", (cx, 6, cz), (cx, 17, cz), M.LOG)
    add_fill(fills, f"{label} lamp cluster", (cx - 1, 18, cz - 1), (cx + 1, 18, cz + 1), M.SEA_LANTERN)
    add_fill(fills, f"{label} finial", (cx, 19, cz), (cx, 19, cz), M.GOLD)


def build_danfeng_plaza_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Plaza deck (御广场): three-layer stone parquet.
    #    Outer ring polished andesite, middle field smooth stone.
    # ------------------------------------------------------------------
    add_fill(fills, "danfeng plaza deck outer", (PX1, DECK_Y, PZ1), (PX2, DECK_Y, PZ2), M.ANDESITE)
    add_fill(fills, "danfeng plaza deck middle", (PX1 + 12, DECK_Y, PZ1 + 12), (PX2 - 12, DECK_Y, PZ2 - 12), M.SMOOTH)
    # Parquet stripes across the middle field, stopping at the axis road.
    for sz in (3975, 4005):
        add_fill(fills, f"danfeng plaza stripe w {sz}", (PX1 + 12, DECK_Y, sz), (ROAD_X1 - 1, DECK_Y, sz), M.ANDESITE)
        add_fill(fills, f"danfeng plaza stripe e {sz}", (ROAD_X2 + 1, DECK_Y, sz), (PX2 - 12, DECK_Y, sz), M.ANDESITE)
    # Square medallion ring around the axis centre.
    add_outline(fills, "danfeng plaza medallion", 2960, 3960, 3040, 4020, DECK_Y, DECK_Y, M.ANDESITE, thickness=2)

    # ------------------------------------------------------------------
    # 2. Imperial axis road (御道): smooth stone with gold edging, from
    #    the central gate passage straight to the plaza's south rim.
    #    Paving stops at z 4044, abutting (never covering) the AIR passage.
    # ------------------------------------------------------------------
    add_fill(fills, "danfeng road bed", (ROAD_X1 + 1, DECK_Y, ROAD_Z1), (ROAD_X2 - 1, DECK_Y, ROAD_Z2), M.SMOOTH)
    add_fill(fills, "danfeng road edge w", (ROAD_X1, DECK_Y, ROAD_Z1), (ROAD_X1, DECK_Y, ROAD_Z2), M.GOLD)
    add_fill(fills, "danfeng road edge e", (ROAD_X2, DECK_Y, ROAD_Z1), (ROAD_X2, DECK_Y, ROAD_Z2), M.GOLD)
    for dz in range(3945, 4044, 10):
        add_fill(fills, f"danfeng road dash {dz}", (GATE_CX, DECK_Y, dz), (GATE_CX, DECK_Y, dz), M.GOLD)

    # ------------------------------------------------------------------
    # 3. Twin que platforms (阙台) + link galleries forming the "凹" plan.
    #    Everything stays within x 2860..3150 and outside the protected
    #    tower rectangle; galleries only touch the tower at its wall line.
    # ------------------------------------------------------------------
    _que_tower(fills, "danfeng que w", QUE_W_CX, QUE_CZ)
    _que_tower(fills, "danfeng que e", QUE_E_CX, QUE_CZ)
    _link_gallery(fills, "danfeng gallery w", z1=LINK_Z1, z2=LINK_Z2, **LINK_W)
    _link_gallery(fills, "danfeng gallery e", z1=LINK_Z1, z2=LINK_Z2, **LINK_E)

    # ------------------------------------------------------------------
    # 4. Dismount steles (下马碑) at the plaza's east / west entrances.
    # ------------------------------------------------------------------
    _dismount_stele(fills, "danfeng stele w", STEle_W_CX, STELE_CZ)
    _dismount_stele(fills, "danfeng stele e", STELE_E_CX, STELE_CZ)

    # ------------------------------------------------------------------
    # 5. Ceremonial banner array (仪仗旗阵), five poles each side.
    # ------------------------------------------------------------------
    for bx in BANNER_XS:
        for bi, bz in enumerate(BANNER_ZS):
            _banner_pole(fills, f"danfeng banner {bx} {bi}", bx, bz)

    # ------------------------------------------------------------------
    # 6. Officials' waiting galleries (百官待朝廊) on both plaza edges.
    # ------------------------------------------------------------------
    _waiting_gallery(fills, "danfeng wait w", *GAL_W)
    _waiting_gallery(fills, "danfeng wait e", *GAL_E)

    # ------------------------------------------------------------------
    # 7. Guardian lions (石狮) beside the central gate opening.
    # ------------------------------------------------------------------
    _stone_lion(fills, "danfeng lion w", 2986, 4040)
    _stone_lion(fills, "danfeng lion e", 3014, 4040)

    # ------------------------------------------------------------------
    # 8. Palace lamp posts at the four plaza corners.
    # ------------------------------------------------------------------
    for li, (lx, lz) in enumerate(
        [(PX1 + 3, PZ1 + 3), (PX2 - 3, PZ1 + 3), (PX1 + 3, PZ2 - 3), (PX2 - 3, PZ2 - 3)]
    ):
        _palace_lamp(fills, f"danfeng corner lamp {li}", lx, lz)


def main() -> None:
    run_builder(build_danfeng_plaza_3d, "danfeng_plaza_3d")


if __name__ == "__main__":
    main()
