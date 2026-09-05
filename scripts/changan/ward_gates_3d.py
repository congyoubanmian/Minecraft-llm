from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    Fill,
    Materials as M,
    WARD_BLOCK_SIZE,
    WARD_X_LINES,
    WARD_Z_LINES,
    add_fill,
    add_pixel_mural,
    is_ward_excluded,
    run_builder,
)


"""
Ward Gates of Tang Chang'an (长安坊门·坊里身份工程) - one small named
gate tower on the south edge midpoint of every buildable ward, so each
of the city's fang carries its own name board (坊名匾).

Gate count: 51 ward gates (19 west of Zhuque Avenue + 32 east), one per
surviving 260x260 ward cell.  108 cells exist in the WARD grid;
12 fall inside the is_ward_excluded imperial-city / market zones and 45
host existing landmark modules (see LANDMARK_PLOTS below) and are
skipped, leaving 51 gates.

Ward-name sources (all attested Tang ward names, no inventions needed):
    - Chang'an County side (west of Zhuque Avenue) row by row from north
      to south: 修真 金城 长兴 醴泉 兴化 延寿 延康 安德 丰安 昌明 延祚
      通义 崇业 大安 修德 宣义 丰乐 安乐 丰邑 (唐两京城坊考 长安县 listed wards).
    - Wannian County side (east of Zhuque Avenue): 永兴 永昌 翊善 光宅
      长乐 大宁 安兴 胜业 兰陵 安仁 亲仁 道政 平康 崇仁 长寿 宣阳 升道
      广德 靖安 敦义 大业 保康 安平 升平 昭国 新昌 修政 保宁 安善 安义
      归义 曲池 (万年在坊, incl. the southern 归义/曲池).
    Names are assigned by orientation: palace-facing rows get the
    historical north-row wards, temple rows keep their temple wards
    (the temple cells themselves are excluded below).

Landmark exclusion list (each rect read from the module's constants):
    temple_dayan.py        大雁塔·慈恩寺    x 900..1400,  z 3500..4000
    temple_jianfu.py       荐福寺           x 1100..1550, z 3500..3950
    xiaoyanta_3d.py        小雁塔           x 1150..1500, z 3560..3920
    temple_qinglong.py     青龙寺           x 4800..5300, z 800..1300
    beilin_3d.py           碑林(务本坊)     x 1650..2150, z 4750..5150
                           (south of the ward band - kept for reference,
                           no ward cell intersects it)
    tangchang_guan_3d.py   唐昌观           x 1150..1500, z 3120..3470
    jinzouyuan_3d.py       进奏院           x 2450..2750, z 1750..2050
    baixi_chang_3d.py      百戏场           x 4300..4600, z 3150..3450
    temple_daxingshan.py   大兴善寺         x 1200..1700, z 2200..2700
    temple_xuandu.py       玄都观           x 4600..3500..4000 rect below
    temple_daci.py + pagoda_giant_3d.py 大慈恩寺·大塔 x 4300..4900, z 3600..4200
    palace_xingqing.py     兴庆宫·龙池      x 900..1700,  z 800..1600
    entertainment_venues.py 戏场乐棚        x 1800..2600, z 2200..3000
    zhijinfang_3d.py       织锦坊           x 4850..5150, z 1100..1450
    douting_post_3d.py     都亭驿           x 3450..3750, z 1500..1800
    taiyiyuan_3d.py        太医署           x 3550..3850, z 900..1250
    wenyuan_3d.py          文院             x 2050..2400, z 1200..1550
    qinwu_tower_3d.py      勤政务本楼       x 1330..1700, z 1500..1800
    jingjiao_bei_3d.py     景教碑(义宁坊)   x 700..1000,  z 3150..3450
    bangyuan_3d.py         榜元第           x 3350..3680, z 650..860
    foreign_temples.py     波斯胡寺/祆祠    x 500..900 / 1000..1300, z 2000..2400

Distinctive features (each gate, deliberately smaller and plainer than
the jieshi_pailou_3d crossroad arches):
    - Two-post one-bay timber form (两柱一门): dark-oak posts flanking a
      2-wide pedestrian doorway, rising from white ward-wall stubs with
      dark cap courses
    - Hanging white name board (门楣白匾) mounted proud on the outboard
      face and a plain white back board, painted with the ward name in
      BLACK_WOOL 5x5 pixel glyphs via add_pixel_mural (readable
      left-to-right from the southern approach); the board is 11x5 -
      wider than the spec's 7x3 - because two 5x5 characters cannot fit
      on 7 columns
    - Gabled xuanshan roof (悬山小顶): ROOF_GREEN stair slopes both
      sides + DARK ridge, one block overhang all round, total height 8
    - Pair of smooth-stone drum bases (抱鼓石) guarding the doorway
    - One fence-pole lantern (挑杆挂灯) beside the right wall stub
    - Air carve through the ward-wall line behind the doorway so the
      gate is actually passable

Coordinate conventions: gate line sits on the ward's z1 edge (south
edge in this project's compass, the palace lies at high z), facing
outward (-z).  Ground structure footprint 9x3 (cx-4..cx+4 x gz-1..gz+1),
all fills y1..y8 inclusive.
"""


# ---------------------------------------------------------------------------
# 5x5 pixel glyphs (像素字模).  '#' = painted pixel, '.' = board behind.
# Difficult characters use consistent simplified impression forms; every
# glyph below is used city-wide with exactly this shape.
# ---------------------------------------------------------------------------
GLYPHS_5X5: dict[str, list[str]] = {
    "安": ["..#..", ".###.", "#####", ".#.#.", "#...#"],
    "保": ["#.###", "#.#.#", "#.###", "#.#.#", "#.###"],
    "昌": [".###.", ".#.#.", "#####", ".#.#.", ".###."],
    "崇": ["#.#.#", "#.#.#", "#####", ".###.", "#...#"],
    "大": ["..#..", ".###.", ".###.", ".#.#.", "#...#"],
    "池": ["##...", "..#..", "##.##", "..#..", "#..##"],
    "长": ["..##.", "..#..", "#####", ".#.#.", "#...#"],
    "城": ["###.#", "#.#.#", "#####", "#.#.#", "###.#"],
    "道": ["#####", "..#..", "#####", "..#..", "#.###"],
    "德": ["#.##.", "#####", "#.#.#", "#####", "#.##."],
    "敦": ["####.", "#.#.#", "####.", ".#.#.", "#...#"],
    "丰": ["..#..", "#####", "..#..", "#####", "..#.."],
    "归": ["#.###", "#.#.#", "#.###", "#.#..", "#.###"],
    "光": ["..#..", "#####", ".###.", ".#.#.", "#...#"],
    "广": ["#####", "..#..", ".###.", ".#.#.", "#...#"],
    "国": ["#####", "..#..", ".###.", "..#.#", "#####"],
    "化": ["#..#.", "#..#.", "#.##.", "..#.#", "..#.#"],
    "翊": ["####.", "#.###", "#.#.#", "#.###", "####."],
    "金": ["..#..", ".###.", "#####", ".###.", "#.#.#"],
    "靖": [".###.", "#.#.#", "#####", "#.#.#", "#####"],
    "康": ["#####", "#...#", "#####", "##.#.", "#..##"],
    "兰": ["#.#.#", ".###.", "#####", ".###.", "#####"],
    "乐": ["#####", ".###.", "#.#.#", ".#.#.", "..#.."],
    "醴": ["####.", "#..##", "####.", "#..##", "####."],
    "陵": ["##.##", "#.#.#", "#####", "#.#.#", "##.##"],
    "宁": ["..#..", "#####", "..#..", "..#..", "####."],
    "平": ["..#..", "#####", "#.#.#", "#####", "..#.."],
    "仁": ["#.###", "#....", "#.###", "#....", "#.###"],
    "曲": ["#####", "#.#.#", "#.#.#", "#...#", "#####"],
    "泉": ["#####", ".###.", "#.#.#", ".#.#.", "#...#"],
    "善": ["#.#.#", "..#..", "#####", "#.#.#", "#####"],
    "升": ["#.#..", "..#..", "#####", "..#..", "..#.."],
    "胜": ["#.##.", "#####", "#.###", "#.#.#", "#.###"],
    "宅": ["..#..", "#####", "#...#", "###.#", "#...#"],
    "修": ["#.###", "#.#.#", "#####", "#.##.", "#.#.#"],
    "宣": ["..#..", "#####", "#.#.#", "#####", ".###."],
    "义": ["..#..", "#...#", ".#.#.", ".#.#.", "..#.."],
    "永": ["..#..", ".###.", "..#..", ".#.#.", "#...#"],
    "兴": ["#.#.#", "#####", "..#..", ".###.", "#...#"],
    "新": [".####", "..#..", ".####", "..#.#", ".####"],
    "阳": ["#.###", "#.#.#", "#.###", "#.#.#", "#.###"],
    "业": ["#.#.#", "#.#.#", "#####", "..#..", ".###."],
    "祚": [".#.#.", "#####", "..#..", "#..##", "#..##"],
    "昭": ["#####", "#.#..", "#####", "#.#.#", "#####"],
    "真": ["..#..", "#####", "#.#.#", "#####", ".###."],
    "政": ["#####", "#.#..", "#####", "..#.#", "#####"],
    "延": ["#####", "....#", "####.", "..#..", "##..."],
    "寿": ["..#..", "#####", "..#..", "#####", ".###."],
    "通": [".###.", "##.##", ".###.", "#....", "##..."],
    "明": ["#####", "#.#.#", "#####", "#.#.#", "#####"],
    "邑": ["#####", ".#.#.", "#####", "..#.#", ".###."],
    "亲": [".###.", "..#..", "#####", "..#..", "#.#.#"],
}


# ---------------------------------------------------------------------------
# Landmark plot rects (x1, z1, x2, z2, module, note) - see docstring table.
# ---------------------------------------------------------------------------
LANDMARK_PLOTS: list[tuple[int, int, int, int, str, str]] = [
    (900, 3500, 1400, 4000, "temple_dayan", "大雁塔·慈恩寺"),
    (1100, 3500, 1550, 3950, "temple_jianfu", "荐福寺"),
    (1150, 3560, 1500, 3920, "xiaoyanta_3d", "小雁塔"),
    (4800, 800, 5300, 1300, "temple_qinglong", "青龙寺"),
    (1650, 4750, 2150, 5150, "beilin_3d", "碑林·务本坊(坊带以南, 备案)"),
    (1150, 3120, 1500, 3470, "tangchang_guan_3d", "唐昌观"),
    (2450, 1750, 2750, 2050, "jinzouyuan_3d", "进奏院"),
    (4300, 3150, 4600, 3450, "baixi_chang_3d", "百戏场"),
    (1200, 2200, 1700, 2700, "temple_daxingshan", "大兴善寺·靖善坊"),
    (4600, 3500, 5100, 4000, "temple_xuandu", "玄都观"),
    (4300, 3600, 4900, 4200, "temple_daci+pagoda_giant_3d", "大慈恩寺·雁塔巨塔"),
    (900, 800, 1700, 1600, "palace_xingqing", "兴庆宫·龙池"),
    (1800, 2200, 2600, 3000, "entertainment_venues", "戏场乐棚"),
    (4850, 1100, 5150, 1450, "zhijinfang_3d", "织锦坊"),
    (3450, 1500, 3750, 1800, "douting_post_3d", "都亭驿"),
    (3550, 900, 3850, 1250, "taiyiyuan_3d", "太医署"),
    (2050, 1200, 2400, 1550, "wenyuan_3d", "文院"),
    (1330, 1500, 1700, 1800, "qinwu_tower_3d", "勤政务本楼"),
    (700, 3150, 1000, 3450, "jingjiao_bei_3d", "景教碑·义宁坊"),
    (3350, 650, 3680, 860, "bangyuan_3d", "榜元第"),
    (500, 2000, 900, 2400, "foreign_temples", "波斯胡寺"),
    (1000, 2000, 1300, 2300, "foreign_temples", "祆祠"),
]

# Ward names west / east of Zhuque Avenue (x=3000), listed in (z, x) cell
# order.  len(WEST_WARD_NAMES) == west cells, len(EAST_WARD_NAMES) == east.
WEST_WARD_NAMES: list[str] = [
    # row z=620 (palace-front row)
    "修真", "金城", "长兴",
    # row z=1020
    "醴泉", "兴化",
    # row z=1420
    "延寿", "延康",
    # row z=1820
    "安德", "丰安",
    # row z=2620
    "昌明",
    # row z=3020
    "延祚", "通义",
    # row z=3420
    "崇业", "大安", "修德",
    # row z=3820 (south rim row)
    "宣义", "丰乐", "安乐", "丰邑",
]

EAST_WARD_NAMES: list[str] = [
    # row z=620
    "永兴", "永昌", "翊善",
    # row z=1020
    "光宅", "长乐",
    # row z=1420
    "大宁", "安兴", "胜业", "兰陵",
    # row z=1820
    "安仁", "亲仁", "道政", "平康", "崇仁", "长寿",
    # row z=2220
    "宣阳", "升道", "广德", "靖安",
    # row z=2620
    "敦义", "大业", "保康", "安平",
    # row z=3020
    "升平", "昭国", "新昌",
    # row z=3420
    "修政", "保宁", "安善",
    # row z=3820
    "安义", "归义", "曲池",
]


def _glyph(ch: str) -> list[str]:
    """Return the 5x5 dot rows for one character, validating the shape."""
    rows = GLYPHS_5X5.get(ch)
    if rows is None or len(rows) != 5 or any(len(row) != 5 for row in rows):
        raise RuntimeError(f"ward gate glyph missing/invalid for char {ch!r}")
    return rows


def _name_art(name: str) -> list[str]:
    """Compose the 11x5 board art for a 2-character ward name (5+1+5)."""
    if len(name) != 2:
        raise RuntimeError(f"ward name {name!r} must be exactly 2 characters")
    left, right = _glyph(name[0]), _glyph(name[1])
    return [left[r] + "." + right[r] for r in range(5)]


def _landmark_hit(x: int, z: int) -> str | None:
    """Return the landmark name overlapping ward cell (x, z), if any."""
    cx1, cz1, cx2, cz2 = x, z, x + WARD_BLOCK_SIZE, z + WARD_BLOCK_SIZE
    for lx1, lz1, lx2, lz2, module, note in LANDMARK_PLOTS:
        if cx1 < lx2 and lx1 < cx2 and cz1 < lz2 and lz1 < cz2:
            return f"{module}({note})"
    return None


def _ward_gate(fills: list[Fill], label: str, cx: int, gate_z: int, name: str) -> None:
    """One two-post ward gate with its name board (两柱一门坊门).

    cx/gate_z: centre of the ward's south edge.  Ground footprint is
    cx-4..cx+4 x gate_z-1..gate_z+1 (9x3), every fill lies in y1..y8
    (8 tall).  The gate faces -z (outward / project-south).
    """
    # ------------------------------------------------------------------
    # 1. Flanking wall stubs (门洞两侧矮墙各3格) with dark cap courses.
    # ------------------------------------------------------------------
    add_fill(fills, f"{label} wall w", (cx - 4, 1, gate_z), (cx - 2, 2, gate_z), M.WHITE_TERRACOTTA)
    add_fill(fills, f"{label} wall e", (cx + 2, 1, gate_z), (cx + 4, 2, gate_z), M.WHITE_TERRACOTTA)
    add_fill(fills, f"{label} cap w", (cx - 4, 3, gate_z), (cx - 2, 3, gate_z), M.DARK)
    add_fill(fills, f"{label} cap e", (cx + 2, 3, gate_z), (cx + 4, 3, gate_z), M.DARK)

    # ------------------------------------------------------------------
    # 2. Two LOG posts (两柱) flanking the 2-wide doorway + lintel (门楣).
    # ------------------------------------------------------------------
    add_fill(fills, f"{label} post w", (cx - 2, 1, gate_z), (cx - 2, 7, gate_z), M.LOG)
    add_fill(fills, f"{label} post e", (cx + 1, 1, gate_z), (cx + 1, 7, gate_z), M.LOG)
    add_fill(fills, f"{label} lintel", (cx - 2, 3, gate_z), (cx + 1, 3, gate_z), M.LOG)

    # ------------------------------------------------------------------
    # 3. Name boards: white 匾底 proud on the outward face (with the
    #    BLACK_WOOL 5x5 pixel name via add_pixel_mural) and a plain back
    #    board so the gate reads solid from the ward side.
    # ------------------------------------------------------------------
    add_fill(fills, f"{label} board front", (cx - 5, 3, gate_z - 1), (cx + 5, 7, gate_z - 1), M.WHITE_TERRACOTTA)
    add_fill(fills, f"{label} board back", (cx - 5, 3, gate_z + 1), (cx + 5, 7, gate_z + 1), M.WHITE_TERRACOTTA)
    add_pixel_mural(
        fills,
        f"{label} plaque",
        _name_art(name),
        {"#": M.BLACK_WOOL},
        cx - 5,
        7,
        gate_z - 1,
        axis="x",
        flip=True,  # left-to-right reading for a viewer approaching from -z
    )

    # ------------------------------------------------------------------
    # 4. Xuanshan roof (悬山小顶): ROOF_GREEN stair slopes + DARK ridge.
    # ------------------------------------------------------------------
    add_fill(
        fills, f"{label} roof out",
        (cx - 5, 8, gate_z - 1), (cx + 5, 8, gate_z - 1),
        "minecraft:dark_prismarine_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]",
    )
    add_fill(
        fills, f"{label} roof in",
        (cx - 5, 8, gate_z + 1), (cx + 5, 8, gate_z + 1),
        "minecraft:dark_prismarine_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]",
    )
    add_fill(fills, f"{label} ridge", (cx - 5, 8, gate_z), (cx + 5, 8, gate_z), M.DARK)

    # ------------------------------------------------------------------
    # 5. Drum bases (抱鼓石2枚) and the pole lantern (挑杆挂灯).
    # ------------------------------------------------------------------
    add_fill(fills, f"{label} drum w", (cx - 2, 1, gate_z - 1), (cx - 2, 1, gate_z - 1), M.SMOOTH)
    add_fill(fills, f"{label} drum e", (cx + 1, 1, gate_z - 1), (cx + 1, 1, gate_z - 1), M.SMOOTH)
    add_fill(fills, f"{label} lamp pole", (cx + 4, 4, gate_z), (cx + 4, 5, gate_z), M.FENCE)
    add_fill(fills, f"{label} lamp", (cx + 4, 6, gate_z), (cx + 4, 6, gate_z), M.LANTERN)

    # ------------------------------------------------------------------
    # 6. Carve the doorway through the ward-wall line behind the gate so
    #    it is actually passable (no ward wall is built here).
    # ------------------------------------------------------------------
    add_fill(fills, f"{label} doorway carve", (cx - 1, 1, gate_z + 1), (cx, 3, gate_z + 2), M.AIR)


def build_ward_gates_3d(fills: list[Fill]) -> None:
    """Place one named gate on the south edge of every buildable ward."""
    # ------------------------------------------------------------------
    # 1. Collect buildable ward origins: skip imperial/market zones and
    #    every cell hosting a landmark module.
    # ------------------------------------------------------------------
    origins: list[tuple[int, int]] = []
    for x in WARD_X_LINES:
        for z in WARD_Z_LINES:
            if is_ward_excluded(x, z):
                continue
            if _landmark_hit(x, z) is not None:
                continue
            origins.append((x, z))

    west = sorted([o for o in origins if o[0] < 3000], key=lambda o: (o[1], o[0]))
    east = sorted([o for o in origins if o[0] >= 3000], key=lambda o: (o[1], o[0]))
    if len(west) != len(WEST_WARD_NAMES):
        raise RuntimeError(
            f"west ward cell/name mismatch: {len(west)} cells vs {len(WEST_WARD_NAMES)} names"
        )
    if len(east) != len(EAST_WARD_NAMES):
        raise RuntimeError(
            f"east ward cell/name mismatch: {len(east)} cells vs {len(EAST_WARD_NAMES)} names"
        )

    # ------------------------------------------------------------------
    # 2. Build every gate: two-post form + pixel-name board.
    # ------------------------------------------------------------------
    for (x, z), name in list(zip(west, WEST_WARD_NAMES)) + list(zip(east, EAST_WARD_NAMES)):
        cx = x + WARD_BLOCK_SIZE // 2
        _ward_gate(fills, f"wardgate {name}", cx, z, name)


def main() -> None:
    run_builder(build_ward_gates_3d, "ward_gates_3d")


if __name__ == "__main__":
    main()
