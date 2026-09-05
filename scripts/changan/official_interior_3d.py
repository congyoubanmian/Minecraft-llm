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
from scripts.changan.government_offices import OFFICES as GOVERNMENT_OFFICES


"""
Official Interior 3D (皇城官署内部深化叠加层) - furnishing pass that fits out
the full Tang court hall inside each of the four imperial-city offices.

中文名：皇城四官署内部深化叠加层（正堂公案 + 职能陈设 + 东西司文书房 +
登闻鼓架 + 门内影壁 + 庭院柏树灯柱）
英文名：Chang'an government-office interior overlay (court desks with seated
officials, function-specific furnishings, clerk stations, drum stands,
gate screen walls and courtyard planting).

坐标来源 / Coordinate derivation (replayed from government_offices.build_office,
OFFICES = shangshu_sheng(2000,4200) / yushi_tai(2200,4400) / dali_si(2400,4200)
/ honglu_si(2600,4400); z1 = cz-55):

    | 结构 structure | 外壳 shell | 室内净空 interior clear space |
    |----------------|-----------|-------------------------------|
    | 正堂 main hall | (cx-45,1,z1+30)-(cx+45,20,z1+90) 厚2 | x cx-43..cx+43, y 3..18, z cz-23..cz+33; 地面顶 y=2 -> 家具贴地 y=3 |
    | 大门 main gate | (cx-14,1,z1-4)-(cx+14,12,z1+4) 实体 | 影壁/鼓架置于 z1+10 = cz-45, 完全避开墙体与南侧檐(y12, z1+4..z1+8) |
    | 庭院 courtyard | 地面顶 y=1 | 柏树/灯柱贴地 y=2 (与既有树 y=2 一致) |
    | 东西司 side offices | z1+100 == z2-10 = cz+45, 退化为 1 格厚实心墙 | 无室内空间 -> 文书房案位移入正堂东西侧廊 |

    Per-office hall interiors (x1..x2 / z1..z2 of the air volume):
        shangshu_sheng  1957..2043 / 4177..4233
        yushi_tai       2157..2243 / 4377..4433
        dali_si         2357..2443 / 4177..4233
        honglu_si       2557..2643 / 4377..4433

避让 / Avoidance: roof_color_zoning_3d.py caps these roofs with yellow ridge
bands at y>=19 (gate band y19, hall band y29, finial marks y23/y33) - every
object added here tops out at y12 (the Guanzhong map mural), so nothing
touches the ridge markers. This pass is additive only: no AIR fill is issued
(只添加不清空).

深化清单 / Deepening list (per office unless noted):
    1. 正堂公案: central LOG-legged desk with plank top, quartz documents and
       gold seal, a seated official statue behind it (quartz legs/head, red
       robe, gold hat) and a red kneeling cushion before it
    2. 职能陈设 (differentiated by office):
       - shangshu_sheng: iron-bar weapons rack with three timber arms, plus an
         8x5 Guanzhong map mural (dark field, quartz ridges/rivers, gold
         Chang'an mark) painted on the east hall wall
       - yushi_tai: quartz Xiezhi (獬豸) justice beast with gold horn and tail,
         plus a chest for impeachment memos (弹章匣)
       - dali_si: three-tier archive shelf (bookshelf/timber), a gold gavel
         (惊堂木) on the desk and an iron-bar prisoner rail in the NE corner
       - honglu_si: four tribute boxes in red/blue/yellow/green wool with gold
         contents, two quartz envoy hats on stands, and a 3x5 red carpet
    3. 东西司文书房: two clerk stations on each flank (desk + lectern +
       bookshelf archive wall + fence candle stand with lantern)
    4. 廊下鼓架: fence-framed red drum (登闻鼓) with two drumsticks, one side
       of the main gate
    5. 门内影壁: white-terracotta screen wall 5x4 with dark frame and a gold
       seal panel, set behind the gate mass
    6. 庭院: two columnar cypresses and two lantern posts flanking the axis

Distinctive features:
    - Function-driven interiors: each office reads as its historical bureau
      (military racks + cartography, censorship beast + memo chest, judicial
      shelves + dock, diplomatic tribute display), not four copy-pasted rooms
    - A seated official behind every court desk (seat / robe / head / gold
      cap stack) turning each hall into a working audience scene
    - Pixel-painted Guanzhong map mural reusing lib.add_pixel_mural on a hall
      wall plane, echoing the chang'an map-wall motif of the roof-zoning pass
    - Strict interior clear-space discipline: every fill derived from the
      hollow-box air volume, all placement additive, ridge markers untouched
"""

# Extra block ids used by this pass (not in lib.Materials).
BOOKSHELF = "minecraft:bookshelf"
CHEST = "minecraft:chest"
LECTERN = "minecraft:lectern"

# 关中舆图 8x5: dark field, quartz mountain/river lines, gold Chang'an mark.
GUANZHONG_MAP = [
    "QQDDQQDQ",
    "DQQDDQDD",
    "DQQGGQQD",
    "DQQQQQQD",
    "DDQQQQDD",
]
GUANZHONG_PALETTE = {
    "D": M.DARK,  # 底: deepslate field
    "Q": M.QUARTZ,  # 山水线: quartz ridges and the Wei river
    "G": M.GOLD,  # 长安城 mark
}

# Honglu Si tribute wool colours (four quarters of the known world).
TRIBUTE_WOOLS = [M.RED_WOOL, M.BLUE_WOOL, M.YELLOW_WOOL, M.GREEN_WOOL]


# ---------------------------------------------------------------------------
# Shared furnishing helpers.
# ---------------------------------------------------------------------------
def _court_desk(fills: list[Fill], label: str, cx: int, cz: int) -> None:
    """正堂公案: central desk, seated official behind it, cushion before it.

    Hall floor top is y=2, so furniture stands at y=3+. The official faces
    north (-z) toward the gate; the desk is north of him.
    """
    # Kneeling cushion on the floor before the desk.
    add_fill(fills, f"{label} cushion", (cx, 3, cz - 10), (cx, 3, cz - 10), M.RED_WOOL)
    # Desk: dark-oak legs + 5x2 plank top.
    add_fill(fills, f"{label} desk top", (cx - 2, 4, cz - 6), (cx + 2, 4, cz - 5), M.WOOD)
    for lx in (cx - 2, cx + 2):
        for lz in (cz - 6, cz - 5):
            add_fill(fills, f"{label} desk leg {lx},{lz}", (lx, 3, lz), (lx, 3, lz), M.LOG)
    # Documents (quartz) and official seal (gold) laid on the desk.
    add_fill(fills, f"{label} documents", (cx - 1, 5, cz - 6), (cx, 5, cz - 6), M.QUARTZ)
    add_fill(fills, f"{label} seal", (cx + 1, 5, cz - 6), (cx + 1, 5, cz - 6), M.GOLD)
    # Seated official: quartz lap + head, red robe torso, gold hat.
    add_fill(fills, f"{label} official seat", (cx, 3, cz - 3), (cx, 3, cz - 3), M.QUARTZ)
    add_fill(fills, f"{label} official robe", (cx, 4, cz - 3), (cx, 4, cz - 3), M.RED_WOOL)
    add_fill(fills, f"{label} official head", (cx, 5, cz - 3), (cx, 5, cz - 3), M.QUARTZ)
    add_fill(fills, f"{label} official hat", (cx, 6, cz - 3), (cx, 6, cz - 3), M.GOLD)


def _clerk_desk(fills: list[Fill], label: str, mx: int, dz: int, side: str) -> None:
    """东西司 clerk station: desk + lectern + archive wall + candle stand.

    mx is the desk centre x; side 'w' puts the bookshelf wall on the west
    hall wall (x = mx-4), side 'e' mirrors it (x = mx+4).
    """
    x1, x2 = mx - 1, mx + 1
    wall_x = mx - 4 if side == "w" else mx + 4
    lec_x = mx + 2 if side == "w" else mx - 2
    lamp_x = mx + 4 if side == "w" else mx - 4
    add_fill(fills, f"{label} desk top", (x1, 4, dz), (x2, 4, dz), M.WOOD)
    add_fill(fills, f"{label} desk leg n", (x1, 3, dz), (x1, 3, dz), M.LOG)
    add_fill(fills, f"{label} desk leg s", (x2, 3, dz), (x2, 3, dz), M.LOG)
    add_fill(fills, f"{label} lectern", (lec_x, 3, dz), (lec_x, 3, dz), LECTERN)
    add_fill(fills, f"{label} archive wall", (wall_x, 3, dz - 1), (wall_x, 4, dz + 1), BOOKSHELF)
    add_fill(fills, f"{label} candle post", (lamp_x, 3, dz), (lamp_x, 4, dz), M.FENCE)
    add_fill(fills, f"{label} candle", (lamp_x, 5, dz), (lamp_x, 5, dz), M.LANTERN)


def _drum_stand(fills: list[Fill], label: str, cx: int, gz: int) -> None:
    """廊下鼓架: 登闻鼓 on a fence frame with a pair of drumsticks."""
    add_fill(fills, f"{label} post w", (cx + 6, 2, gz), (cx + 6, 3, gz), M.FENCE)
    add_fill(fills, f"{label} post e", (cx + 8, 2, gz), (cx + 8, 3, gz), M.FENCE)
    add_fill(fills, f"{label} drum", (cx + 6, 4, gz), (cx + 8, 5, gz), M.RED_WOOL)
    add_fill(fills, f"{label} stick w", (cx + 5, 4, gz), (cx + 5, 5, gz), M.WOOD)
    add_fill(fills, f"{label} stick e", (cx + 9, 4, gz), (cx + 9, 5, gz), M.WOOD)


def _screen_wall(fills: list[Fill], label: str, cx: int, wz: int) -> None:
    """门内影壁: white screen 5x4, dark frame, gold seal at the centre."""
    add_fill(fills, f"{label} core", (cx - 2, 2, wz), (cx + 2, 5, wz), M.WHITE_TERRACOTTA)
    add_fill(fills, f"{label} frame top", (cx - 3, 6, wz), (cx + 3, 6, wz), M.DARK)
    add_fill(fills, f"{label} frame w", (cx - 3, 2, wz), (cx - 3, 5, wz), M.DARK)
    add_fill(fills, f"{label} frame e", (cx + 3, 2, wz), (cx + 3, 5, wz), M.DARK)
    add_fill(fills, f"{label} seal", (cx, 3, wz), (cx, 4, wz), M.GOLD)


def _cypress(fills: list[Fill], label: str, x: int, z: int) -> None:
    """庭院柏树: narrow columnar cypress (trunk + tight foliage + crown)."""
    add_fill(fills, f"{label} trunk", (x, 2, z), (x, 8, z), M.TREE_LOG)
    add_fill(fills, f"{label} foliage", (x - 1, 6, z - 1), (x + 1, 8, z + 1), M.LEAVES)
    add_fill(fills, f"{label} crown", (x, 9, z), (x, 10, z), M.LEAVES)


def _yard_lamp(fills: list[Fill], label: str, x: int, z: int) -> None:
    """庭院灯柱: timber post with a sitting lantern on top."""
    add_fill(fills, f"{label} post", (x, 2, z), (x, 5, z), M.LOG)
    add_fill(fills, f"{label} lantern", (x, 6, z), (x, 6, z), M.LANTERN)


# ---------------------------------------------------------------------------
# Function-specific furnishings (one per office).
# ---------------------------------------------------------------------------
def _weapons_rack(fills: list[Fill], label: str, rx: int, rz: int) -> None:
    """尚书省 兵部架: iron-bar posts, timber crossbar, three timber arms."""
    add_fill(fills, f"{label} post n", (rx, 3, rz), (rx, 6, rz), M.IRON_BARS)
    add_fill(fills, f"{label} post s", (rx, 3, rz + 6), (rx, 6, rz + 6), M.IRON_BARS)
    add_fill(fills, f"{label} crossbar", (rx, 6, rz + 1), (rx, 6, rz + 5), M.WOOD)
    for i, wz in enumerate((rz + 2, rz + 3, rz + 4)):
        add_fill(fills, f"{label} arm {i}", (rx, 5, wz), (rx, 5, wz), M.WOOD)


def _xiezhi(fills: list[Fill], label: str, cx: int, cz: int) -> None:
    """御史台 獬豸像: quartz justice beast on a dark plinth, gold horn, tail.

    Faces west toward the hall centre (head at cx+36, tail at cx+39).
    """
    add_fill(fills, f"{label} plinth", (cx + 37, 3, cz - 1), (cx + 38, 3, cz + 1), M.DARK)
    add_fill(fills, f"{label} body", (cx + 37, 4, cz - 1), (cx + 38, 5, cz + 1), M.QUARTZ)
    add_fill(fills, f"{label} head", (cx + 36, 5, cz), (cx + 36, 6, cz), M.QUARTZ)
    add_fill(fills, f"{label} horn", (cx + 36, 7, cz), (cx + 36, 7, cz), M.GOLD)
    add_fill(fills, f"{label} tail", (cx + 39, 5, cz), (cx + 39, 6, cz), M.QUARTZ)


def _archive_shelf(fills: list[Fill], label: str, sx: int, sz: int) -> None:
    """大理寺 卷宗架: log posts with three bookshelf tiers on timber boards."""
    add_fill(fills, f"{label} post n", (sx, 3, sz), (sx, 8, sz), M.LOG)
    add_fill(fills, f"{label} post s", (sx, 3, sz + 6), (sx, 8, sz + 6), M.LOG)
    for y in (4, 6, 8):
        add_fill(fills, f"{label} books y{y}", (sx, y, sz + 1), (sx, y, sz + 5), BOOKSHELF)
    for y in (5, 7):
        add_fill(fills, f"{label} board y{y}", (sx, y, sz + 1), (sx, y, sz + 5), M.WOOD)


def _tribute_display(fills: list[Fill], label: str, cx: int, cz: int) -> None:
    """鸿胪寺 四方贡品: four wool tribute boxes with gold contents, plus two
    quartz envoy hats on stands near the entrance."""
    spots = [
        (cx - 41, cz + 2),
        (cx - 41, cz + 9),
        (cx + 40, cz + 2),
        (cx + 40, cz + 9),
    ]
    for i, (bx, bz) in enumerate(spots):
        add_fill(fills, f"{label} box {i}", (bx, 3, bz), (bx + 1, 3, bz + 1), TRIBUTE_WOOLS[i])
        add_fill(fills, f"{label} box {i} goods", (bx, 4, bz), (bx + 1, 4, bz + 1), M.GOLD)
    for hx in (cx - 30, cx + 30):
        add_fill(fills, f"{label} hat stand {hx}", (hx, 3, cz - 18), (hx, 4, cz - 18), M.FENCE)
        add_fill(fills, f"{label} envoy hat {hx}", (hx, 5, cz - 18), (hx, 5, cz - 18), M.QUARTZ)


# ---------------------------------------------------------------------------
# Main builder.
# ---------------------------------------------------------------------------
def build_official_interior_3d(fills: list[Fill]) -> None:
    for name, cx, cz, _label in GOVERNMENT_OFFICES:
        # --------------------------------------------------------------
        # 1. 正堂公案 (main-hall court desk set) - every office.
        # --------------------------------------------------------------
        _court_desk(fills, f"offint {name} court", cx, cz)

        # --------------------------------------------------------------
        # 2. 职能差异陈设 (function-specific furnishings).
        # --------------------------------------------------------------
        if name == "shangshu_sheng":
            _weapons_rack(fills, f"offint {name} arms rack", cx - 42, cz + 6)
            # 舆图墙: 8x5 Guanzhong map on the east hall wall (plane x=cx+43,
            # z cz-4..cz+3, top row y12 -> y8).
            add_pixel_mural(
                fills,
                f"offint {name} map wall",
                GUANZHONG_MAP,
                GUANZHONG_PALETTE,
                cx + 43,
                12,
                cz - 4,
                axis="z",
            )
        elif name == "yushi_tai":
            _xiezhi(fills, f"offint {name} xiezhi", cx, cz)
            add_fill(
                fills,
                f"offint {name} impeachment chest",
                (cx + 4, 3, cz - 5),
                (cx + 4, 3, cz - 5),
                CHEST,
            )
        elif name == "dali_si":
            _archive_shelf(fills, f"offint {name} archive shelf", cx - 42, cz + 6)
            # 惊堂木: gold gavel on the desk's near corner.
            add_fill(fills, f"offint {name} gavel", (cx - 2, 5, cz - 5), (cx - 2, 5, cz - 5), M.GOLD)
            # 囚栏: iron-bar dock rail along the NE corner of the hall.
            add_fill(
                fills,
                f"offint {name} prison rail n",
                (cx + 18, 3, cz - 22),
                (cx + 32, 6, cz - 22),
                M.IRON_BARS,
            )
            add_fill(
                fills,
                f"offint {name} prison rail e",
                (cx + 33, 3, cz - 22),
                (cx + 33, 6, cz - 10),
                M.IRON_BARS,
            )
        elif name == "honglu_si":
            _tribute_display(fills, f"offint {name} tribute", cx, cz)
            # 地毯: 3x5 red carpet up the centre aisle.
            add_fill(fills, f"offint {name} carpet", (cx - 1, 3, cz - 20), (cx + 1, 3, cz - 16), M.RED_WOOL)

        # --------------------------------------------------------------
        # 3. 东西司文书房 (clerk stations, two desks per flank) - the built
        #    side ranges are 1-block slabs, so the stations live in the
        #    hall's east/west aisles (z cz+16 / cz+22).
        # --------------------------------------------------------------
        for k, dz in enumerate((cz + 16, cz + 22)):
            _clerk_desk(fills, f"offint {name} clerk w{k}", cx - 39, dz, "w")
            _clerk_desk(fills, f"offint {name} clerk e{k}", cx + 39, dz, "e")

        # --------------------------------------------------------------
        # 4. 廊下鼓架 (drum stand just inside the main gate, east side).
        # --------------------------------------------------------------
        _drum_stand(fills, f"offint {name} drum", cx, cz - 45)

        # --------------------------------------------------------------
        # 5. 门内影壁 (screen wall behind the gate, clear of the gate mass
        #    at z1-4..z1+4 and of its south eave at z1+4..z1+8).
        # --------------------------------------------------------------
        _screen_wall(fills, f"offint {name} screen", cx, cz - 45)

        # --------------------------------------------------------------
        # 6. 庭院柏树与灯柱 (two cypresses + two lamp posts flanking the
        #    axis between screen wall and hall front).
        # --------------------------------------------------------------
        _cypress(fills, f"offint {name} cypress w", cx - 18, cz - 34)
        _cypress(fills, f"offint {name} cypress e", cx + 18, cz - 34)
        _yard_lamp(fills, f"offint {name} lamp w", cx - 8, cz - 30)
        _yard_lamp(fills, f"offint {name} lamp e", cx + 8, cz - 30)


def main() -> None:
    run_builder(build_official_interior_3d, "official_interior_3d")


if __name__ == "__main__":
    main()
