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
    add_column_grid,
    add_fill,
    add_hip_roof,
    add_hollow_box,
    add_lantern_line,
    add_outline,
    add_spiral_stair,
    add_tree,
    run_builder,
)


"""
Qinwu Zhengben Tower & Guanle Plaza (勤政务本楼·观乐广场) - the great
gate-tower astride the west end of Xingqing Palace's south wall, where
Emperor Xuanzong watched baixi performances from the balcony while the
commoners looked up from the plaza below (玄宗楼上观乐、与民同乐).

Location in Chang'an city local coordinates:
    Site graded by this pass: x 1330..1700, z 1500..1800 (hard bounds;
    nothing may be written outside). The Xingqing Palace south wall runs
    through the site at z 1596..1604 (body y 4..10, dark cap y 11).
    Qinwu Zhengben Tower: x 1360..1520 straddling the wall line, arched
    gate platform y 4..8, two storeys y 9..17 / 18..26, hip roof to y 43.
    Guanle Plaza: z 1640..1790 south of the tower.
    Keep-outs (far to the north, untouched): Hua'e Xianghui Lou
    (1120, 1280, z 1262..1298), Chenxiang Ting (1300, 1030, z
    1020..1040), north-bank colonnade z 1046..1049.

Distinctive features:
    - Gate-tower on a 5-block stone platform pierced by three arched
      passages so crowds can stream through the wall line
    - Two red-wall storeys with dark-oak edge columns and arched lattice
      windows, joined by a cantilevered gallery (平座) with fence
      railings and a lower eave ring forming a double roof (重檐)
    - Gilded hip roof (庑殿顶) with a gold ridge and finial 鸱吻
    - South cantilevered viewing terrace (观乐露台) 6 blocks deep with
      diagonal braces, a central gold throne dais and a grand stair
    - Music-viewing plaza: stone paving, a gold-trimmed imperial way
      (御道), eight commoners' thatched viewing sheds (看棚) with plank
      benches, and a threshing-floor lantern array along the edges
    - Baixi stage (百戏台) with red carpet and four flag poles flying
      red / yellow wool banners
    - Gold plaque above the south gate and a gold plaque on the
      palace-side north face
    - West horse ramp (马道) hugging the wall: a gentle stepped ramp
      with parapets built from per-level fills
    - Smooth-stone + quartz guardian lions flanking the terrace stair
      and lantern posts along the inner palace wall
"""

# ---------------------------------------------------------------------------
# Constants.
# ---------------------------------------------------------------------------
# Grading bounds for this module (hard site limits).
SITE_X1, SITE_Z1 = 1330, 1500
SITE_X2, SITE_Z2 = 1700, 1800

# Xingqing Palace south wall band crossing the site (body y 4..10).
WALL_Z1, WALL_Z2 = 1596, 1604
WALL_CAP_Y = 11

# Qinwu Zhengben Tower footprint (straddles the wall, centred z 1600).
T_X1, T_X2 = 1360, 1520
T_Z1, T_Z2 = 1580, 1620

# Vertical layout of the tower.
BASE_Y1, BASE_Y2 = 4, 8      # arched gate platform (券洞门)
S1_Y1, S1_Y2 = 9, 17         # lower storey red walls
PINGZUO_Y = 17               # cantilevered gallery slab between storeys
EAVE_Y = 19                  # lower eave ring of the double roof
S2_Y1, S2_Y2 = 18, 26        # upper storey red walls
ROOF_Y = 27                  # hip roof (庑殿顶) base level

# South viewing terrace (deck 6 blocks south of the tower face).
TER_Y = 8
TER_Z1, TER_Z2 = 1621, 1626

# Music-viewing plaza south of the tower.
PLZ_X1, PLZ_Z1 = 1340, 1640
PLZ_X2, PLZ_Z2 = 1680, 1790
WAY_X1, WAY_X2 = 1432, 1448  # central imperial way on the tower axis

# Baixi stage at the plaza centre.
ST_X1, ST_X2 = 1416, 1464
ST_Z1, ST_Z2 = 1700, 1730

# Arched window columns on the north/south tower faces (5 blocks wide).
WINDOW_XS = (1368, 1396, 1414, 1466, 1484, 1512)

ROOF_STAIR = "minecraft:dark_prismarine_stairs[facing={f},half=bottom,shape=straight,waterlogged=false]"
ROOF_SLAB = "minecraft:dark_prismarine_slab[type=bottom,waterlogged=false]"
HAY = "minecraft:hay_block"


# ---------------------------------------------------------------------------
# Small helpers.
# ---------------------------------------------------------------------------
def _edge_columns(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y1: int, y2: int,
) -> None:
    """Dark-oak columns on the four corners and edge midpoints of a storey."""
    mx, mz = (x1 + x2) // 2, (z1 + z2) // 2
    posts = [
        (x1, z1), (x2 - 1, z1), (x1, z2 - 1), (x2 - 1, z2 - 1),
        (mx - 1, z1), (mx - 1, z2 - 1),
        (x1, mz - 1), (x2 - 1, mz - 1),
    ]
    for i, (px, pz) in enumerate(posts):
        add_fill(fills, f"{label} col {i}", (px, y1, pz), (px + 1, y2, pz + 1), M.LOG)


def _arch_window(fills: list[Fill], tag: str, x0: int, zf: int, yg1: int, yg2: int, ya: int) -> None:
    """Arched lattice window (5 wide) on a north/south tower face."""
    add_fill(fills, f"{tag} lights", (x0, yg1, zf), (x0 + 4, yg2, zf), M.GLASS)
    add_fill(fills, f"{tag} arch", (x0 + 1, ya, zf), (x0 + 3, ya, zf), M.GLASS)


def _base_gate(fills: list[Fill], tag: str, x1: int, x2: int, arch_y: int) -> None:
    """Arched passage (券洞) cut through the gate platform, dark pier trims."""
    add_fill(fills, f"{tag} bore", (x1, BASE_Y1, T_Z1), (x2, arch_y - 1, T_Z2), M.AIR)
    add_fill(fills, f"{tag} crown", (x1 + 3, arch_y, T_Z1), (x2 - 3, BASE_Y2, T_Z2), M.AIR)
    for zf in (T_Z1, T_Z2):
        add_fill(fills, f"{tag} pier w {zf}", (x1 - 2, BASE_Y1, zf), (x1 - 1, BASE_Y2, zf), M.DARK)
        add_fill(fills, f"{tag} pier e {zf}", (x2 + 1, BASE_Y1, zf), (x2 + 2, BASE_Y2, zf), M.DARK)


def _lower_eave(fills: list[Fill]) -> None:
    """Rectangular lower eave ring (重檐下檐) on stair blocks above the pingzuo."""
    add_fill(fills, "qinwu lower eave n", (1356, EAVE_Y, 1576), (1524, EAVE_Y, 1579), ROOF_STAIR.format(f="south"))
    add_fill(fills, "qinwu lower eave s", (1356, EAVE_Y, 1621), (1524, EAVE_Y, 1624), ROOF_STAIR.format(f="north"))
    add_fill(fills, "qinwu lower eave w", (1356, EAVE_Y, 1580), (1359, EAVE_Y, 1620), ROOF_STAIR.format(f="east"))
    add_fill(fills, "qinwu lower eave e", (1521, EAVE_Y, 1580), (1524, EAVE_Y, 1620), ROOF_STAIR.format(f="west"))
    add_outline(fills, "qinwu lower eave drip", 1355, 1575, 1525, 1625, EAVE_Y + 1, EAVE_Y + 1, ROOF_SLAB, thickness=1)


def _shed(fills: list[Fill], tag: str, x1: int, z1: int) -> None:
    """One commoners' viewing shed: log frame, hay thatch, plank benches."""
    x2, z2 = x1 + 17, z1 + 13
    mx = (x1 + x2) // 2
    for i, (px, pz) in enumerate([(x1, z1), (x2, z1), (x1, z2), (x2, z2)]):
        add_fill(fills, f"{tag} post {i}", (px, 5, pz), (px, 10, pz), M.LOG)
    add_fill(fills, f"{tag} king post n", (mx, 5, z1), (mx, 12, z1), M.LOG)
    add_fill(fills, f"{tag} king post s", (mx, 5, z2), (mx, 12, z2), M.LOG)
    add_fill(fills, f"{tag} bench w", (x1 + 2, 5, z1 + 2), (x1 + 2, 5, z2 - 2), M.WOOD)
    add_fill(fills, f"{tag} bench e", (x2 - 2, 5, z1 + 2), (x2 - 2, 5, z2 - 2), M.WOOD)
    add_fill(fills, f"{tag} thatch", (x1 - 1, 11, z1 - 1), (x2 + 1, 11, z2 + 1), HAY)
    add_fill(fills, f"{tag} thatch ridge", (mx - 6, 12, z1 + 3), (mx + 6, 12, z2 - 3), HAY)


def _lion(fills: list[Fill], tag: str, x: int, z: int) -> None:
    """Stylised seated guardian lion: smooth-stone + quartz, facing south."""
    add_fill(fills, f"{tag} pedestal", (x - 1, 4, z - 1), (x + 1, 5, z + 1), M.SMOOTH)
    add_fill(fills, f"{tag} haunch", (x - 1, 6, z - 1), (x + 1, 8, z), M.QUARTZ)
    add_fill(fills, f"{tag} paws", (x - 1, 6, z + 1), (x + 1, 6, z + 1), M.QUARTZ)
    add_fill(fills, f"{tag} ball", (x, 7, z + 1), (x, 7, z + 1), M.GOLD)
    add_fill(fills, f"{tag} head", (x - 1, 9, z - 1), (x + 1, 10, z), M.SMOOTH)


def _flag(fills: list[Fill], tag: str, x: int, z: int, wool: str, dx: int) -> None:
    """Corner flag pole with a coloured wool banner hanging inward."""
    add_fill(fills, f"{tag} pole", (x, 7, z), (x, 14, z), M.FENCE)
    add_fill(fills, f"{tag} banner", (x + dx, 11, z), (x + 3 * dx, 13, z), wool)


# ---------------------------------------------------------------------------
# Main builder.
# ---------------------------------------------------------------------------
def build_qinwu_tower_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site grading: stone subgrade y 0..1, grass y 2..3.
    # ------------------------------------------------------------------
    add_fill(fills, "qinwu ground stone", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "qinwu ground grass", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)

    # ------------------------------------------------------------------
    # 2. Xingqing Palace south wall segment crossing the site.
    # ------------------------------------------------------------------
    add_fill(fills, "qinwu palace wall", (SITE_X1, 4, WALL_Z1), (SITE_X2, 10, WALL_Z2), M.STONE)
    add_fill(fills, "qinwu palace wall cap", (SITE_X1, WALL_CAP_Y, WALL_Z1 - 1), (SITE_X2, WALL_CAP_Y, WALL_Z2 + 1), M.DARK)

    # ------------------------------------------------------------------
    # 3. Gate platform (y 4..8) with three arched through-passages.
    # ------------------------------------------------------------------
    add_fill(fills, "qinwu platform", (T_X1, BASE_Y1, T_Z1), (T_X2, BASE_Y2, T_Z2), M.STONE)
    add_outline(fills, "qinwu platform trim", T_X1, T_Z1, T_X2, T_Z2, BASE_Y1, BASE_Y2, M.ANDESITE, thickness=1)
    _base_gate(fills, "qinwu gate main", 1428, 1452, 8)
    _base_gate(fills, "qinwu gate west", 1376, 1396, 7)
    _base_gate(fills, "qinwu gate east", 1484, 1504, 7)

    # ------------------------------------------------------------------
    # 4. Storey 1 (y 9..17): red walls, edge columns, arched windows, doors.
    # ------------------------------------------------------------------
    add_hollow_box(fills, "qinwu storey1", T_X1, S1_Y1, T_Z1, T_X2, S1_Y2, T_Z2, M.RED_WALL, thickness=1)
    _edge_columns(fills, "qinwu storey1", T_X1, T_Z1, T_X2, T_Z2, S1_Y1, S1_Y2)
    for side, zf in (("n", T_Z1), ("s", T_Z2)):
        for i, wx in enumerate(WINDOW_XS):
            _arch_window(fills, f"qinwu s1 win {side} {i}", wx, zf, 11, 14, 15)
    add_fill(fills, "qinwu s1 door s", (1434, 9, T_Z2), (1446, 12, T_Z2), M.AIR)
    add_fill(fills, "qinwu s1 door n", (1434, 9, T_Z1), (1446, 12, T_Z1), M.AIR)
    add_fill(fills, "qinwu s1 door w", (T_X1, 9, 1588), (T_X1, 12, 1596), M.AIR)
    add_fill(fills, "qinwu s1 door e", (T_X2, 9, 1588), (T_X2, 12, 1596), M.AIR)
    add_column_grid(fills, "qinwu hall columns", 1364, 1584, 1516, 1616, 9, 16, 32)

    # ------------------------------------------------------------------
    # 5. Cantilevered gallery (平座) y 17, railings, spiral stair, lower eave.
    # ------------------------------------------------------------------
    add_cantilevered_floor(fills, "qinwu pingzuo", T_X1, T_Z1, T_X2, T_Z2, y=PINGZUO_Y, overhang=3, block=M.WOOD)
    add_outline(fills, "qinwu pingzuo rail", T_X1 - 3, T_Z1 - 3, T_X2 + 3, T_Z2 + 3, PINGZUO_Y + 1, PINGZUO_Y + 1, M.FENCE, thickness=1)
    add_spiral_stair(fills, "qinwu tower stair", 1470, 1600, radius=4, y1=9, y2=16, block=M.SMOOTH)
    add_fill(fills, "qinwu stair opening", (1466, PINGZUO_Y, 1596), (1474, PINGZUO_Y, 1604), M.AIR)
    _lower_eave(fills)

    # ------------------------------------------------------------------
    # 6. Storey 2 (y 18..26): red walls, edge columns, arched windows.
    # ------------------------------------------------------------------
    add_hollow_box(fills, "qinwu storey2", T_X1, S2_Y1, T_Z1, T_X2, S2_Y2, T_Z2, M.RED_WALL, thickness=1)
    _edge_columns(fills, "qinwu storey2", T_X1, T_Z1, T_X2, T_Z2, S2_Y1, S2_Y2)
    for side, zf in (("n", T_Z1), ("s", T_Z2)):
        for i, wx in enumerate(WINDOW_XS):
            _arch_window(fills, f"qinwu s2 win {side} {i}", wx, zf, 20, 24, 25)

    # ------------------------------------------------------------------
    # 7. Hip roof (庑殿顶) with gold ridge and 鸱吻 finials.
    # ------------------------------------------------------------------
    add_hip_roof(fills, "qinwu hip roof", T_X1 - 4, T_Z1 - 4, T_X2 + 4, T_Z2 + 4,
                 y=ROOF_Y, layers=11, ridge_axis="x", roof_block=M.ROOF_GREEN, ridge_block=M.GOLD)

    # ------------------------------------------------------------------
    # 8. South cantilevered viewing terrace (观乐露台) with gold throne.
    # ------------------------------------------------------------------
    add_fill(fills, "qinwu terrace deck", (T_X1, TER_Y, TER_Z1), (T_X2, TER_Y, TER_Z2), M.WOOD)
    add_fill(fills, "qinwu terrace rail s w", (T_X1, TER_Y + 1, TER_Z2), (1428, TER_Y + 1, TER_Z2), M.FENCE)
    add_fill(fills, "qinwu terrace rail s e", (1452, TER_Y + 1, TER_Z2), (T_X2, TER_Y + 1, TER_Z2), M.FENCE)
    add_fill(fills, "qinwu terrace rail w", (T_X1, TER_Y + 1, TER_Z1), (T_X1, TER_Y + 1, TER_Z2 - 1), M.FENCE)
    add_fill(fills, "qinwu terrace rail e", (T_X2, TER_Y + 1, TER_Z1), (T_X2, TER_Y + 1, TER_Z2 - 1), M.FENCE)
    # Diagonal support braces under the outer deck edge.
    for bx in (1380, 1440, 1500):
        add_fill(fills, f"qinwu terrace brace base {bx}", (bx, 4, 1625), (bx + 1, 6, 1626), M.LOG)
        add_fill(fills, f"qinwu terrace brace top {bx}", (bx, 7, 1623), (bx + 1, 7, 1625), M.LOG)
    # Gold throne dais: the emperor faces south over the plaza.
    add_fill(fills, "qinwu throne dais", (1437, 9, 1622), (1443, 9, 1624), M.GOLD)
    add_fill(fills, "qinwu throne seat", (1438, 10, 1623), (1442, 10, 1624), M.GOLD)
    add_fill(fills, "qinwu throne back", (1438, 10, 1622), (1442, 12, 1622), M.GOLD)
    # Grand stair from the terrace down to the plaza.
    for i in range(5):
        add_fill(fills, f"qinwu terrace step {i}", (1430, TER_Y - i, 1627 + i), (1450, TER_Y - i, 1627 + i), M.SMOOTH)
    add_fill(fills, "qinwu terrace stair cheek w", (1428, 4, 1627), (1429, 8, 1631), M.ANDESITE)
    add_fill(fills, "qinwu terrace stair cheek e", (1451, 4, 1627), (1452, 8, 1631), M.ANDESITE)

    # ------------------------------------------------------------------
    # 9. Gold plaques: "勤政务本" above the south gate, gold plaque inside.
    # ------------------------------------------------------------------
    add_fill(fills, "qinwu plaque s frame", (1430, 12, 1621), (1450, 16, 1621), M.DARK)
    add_fill(fills, "qinwu plaque s gold", (1433, 13, 1622), (1447, 15, 1622), M.GOLD)
    add_fill(fills, "qinwu plaque n frame", (1432, 12, 1579), (1448, 16, 1579), M.DARK)
    add_fill(fills, "qinwu plaque n gold", (1435, 13, 1578), (1445, 15, 1578), M.GOLD)

    # ------------------------------------------------------------------
    # 10. West horse ramp (马道) hugging the wall: gentle stepped slope.
    # ------------------------------------------------------------------
    ramp_segments = [(1332, 1338, 4), (1339, 1345, 5), (1346, 1352, 6), (1353, 1359, 7)]
    for i, (rx1, rx2, ry) in enumerate(ramp_segments):
        add_fill(fills, f"qinwu ramp deck {i}", (rx1, 4, 1582), (rx2, ry, 1594), M.STONE)
        add_fill(fills, f"qinwu ramp parapet n {i}", (rx1, ry + 1, 1581), (rx2, ry + 2, 1581), M.STONE)
        add_fill(fills, f"qinwu ramp parapet s {i}", (rx1, ry + 1, 1595), (rx2, ry + 2, 1595), M.STONE)

    # ------------------------------------------------------------------
    # 11. Guanle plaza: stone paving + gold-trimmed imperial way (御道).
    # ------------------------------------------------------------------
    add_fill(fills, "qinwu plaza paving", (PLZ_X1, 4, PLZ_Z1), (PLZ_X2, 4, PLZ_Z2), M.ANDESITE)
    add_fill(fills, "qinwu imperial way", (WAY_X1, 4, 1631), (WAY_X2, 4, PLZ_Z2), M.SMOOTH)
    add_fill(fills, "qinwu way trim w", (WAY_X1 - 1, 4, 1631), (WAY_X1 - 1, 4, PLZ_Z2), M.GOLD)
    add_fill(fills, "qinwu way trim e", (WAY_X2 + 1, 4, 1631), (WAY_X2 + 1, 4, PLZ_Z2), M.GOLD)

    # ------------------------------------------------------------------
    # 12. Baixi stage (百戏台): y 4..6 platform, carpet, corner banners.
    # ------------------------------------------------------------------
    add_fill(fills, "qinwu stage base", (ST_X1, 4, ST_Z1), (ST_X2, 5, ST_Z2), M.STONE)
    add_fill(fills, "qinwu stage deck", (ST_X1 + 2, 6, ST_Z1 + 2), (ST_X2 - 2, 6, ST_Z2 - 2), M.SMOOTH)
    add_fill(fills, "qinwu stage carpet", (1430, 6, 1706), (1450, 6, 1724), M.RED_WOOL)
    _flag(fills, "qinwu stage flag nw", 1420, 1704, M.RED_WOOL, 1)
    _flag(fills, "qinwu stage flag ne", 1460, 1704, M.YELLOW_WOOL, -1)
    _flag(fills, "qinwu stage flag sw", 1420, 1726, M.YELLOW_WOOL, 1)
    _flag(fills, "qinwu stage flag se", 1460, 1726, M.RED_WOOL, -1)

    # ------------------------------------------------------------------
    # 13. Commoners' viewing sheds (看棚): two rows of four thatched sheds.
    # ------------------------------------------------------------------
    for row, sx in (("w", 1390), ("e", 1473)):
        for i, sz in enumerate((1648, 1672, 1696, 1720)):
            _shed(fills, f"qinwu shed {row} {i}", sx, sz)

    # ------------------------------------------------------------------
    # 14. Threshing-floor lantern arrays around the plaza edges.
    # ------------------------------------------------------------------
    add_lantern_line(fills, "qinwu plaza lantern s", 1350, 1786, 1670, 1786, y=5, every=24)
    add_lantern_line(fills, "qinwu plaza lantern w", 1344, 1652, 1344, 1780, y=5, every=26)
    add_lantern_line(fills, "qinwu plaza lantern e", 1676, 1652, 1676, 1780, y=5, every=26)

    # ------------------------------------------------------------------
    # 15. Guardian lions at the terrace stair + inner palace-wall lanterns.
    # ------------------------------------------------------------------
    _lion(fills, "qinwu lion w", 1424, 1629)
    _lion(fills, "qinwu lion e", 1456, 1629)
    for lx in range(1528, 1691, 32):
        add_fill(fills, f"qinwu wall lamp post {lx}", (lx, 4, 1592), (lx, 8, 1592), M.FENCE)
        add_fill(fills, f"qinwu wall lamp {lx}", (lx, 9, 1592), (lx, 9, 1592), M.LANTERN)
    for lx in (1336, 1352):
        add_fill(fills, f"qinwu wall lamp post {lx}", (lx, 4, 1570), (lx, 8, 1570), M.FENCE)
        add_fill(fills, f"qinwu wall lamp {lx}", (lx, 9, 1570), (lx, 9, 1570), M.LANTERN)

    # ------------------------------------------------------------------
    # 16. Plaza corner trees.
    # ------------------------------------------------------------------
    for i, (tx, tz) in enumerate([(1352, 1652), (1668, 1652), (1352, 1760), (1668, 1760)]):
        add_tree(fills, f"qinwu plaza tree {i}", tx, tz, 5)


def main() -> None:
    run_builder(build_qinwu_tower_3d, "qinwu_tower_3d")


if __name__ == "__main__":
    main()
