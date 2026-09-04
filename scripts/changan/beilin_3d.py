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
    add_hollow_box,
    add_lantern_line,
    add_outline,
    add_pagoda_eave,
    add_platform_with_steps,
    add_pool,
    add_pyramid_roof,
    add_ridge_roof,
    add_tree,
    run_builder,
)


"""
Beilin - Forest of Steles 3D (碑林·开成石经) - the official stone-scripture
repository of Wuben Ward, beside the Imperial Academy, where the Kaicheng
Stone Classics were kept and where the name "Forest of Steles" (碑林) was born.

Location in Chang'an city local coordinates:
    Wuben Ward (务本坊): x 1650..2150, z 4750..5150, tucked between the
    Imperial Academy (国子监, x 1600-2200 / z 4200-4700) to the north and
    Linde Hall (麟德殿, from z 5210) to the south. Ground level y 0..4,
    main structures rise from y 4/5.

Distinctive features:
    - Shitai Xiaojing Pavilion (石台孝经碑亭) on the central axis: stepped
      stone platform, two-storey red-walled square hall with a double eave
      (重檐) and a gilded pyramid roof (攒尖金顶), housing a giant 3x3x12
      quartz-pillar stele on a dark stone pedestal
    - Kaicheng Stone Classics corridors (开成石经长廊): two 400-block
      open timber colonnades flanking the axis, each sheltering two rows
      of quartz steles with dark bases and gilded caps
    - Epitaph forest (墓志铭林): ~20 small 3x1x6 quartz/ smooth-stone
      tablets in two staggered diagonal ranks in the north half
    - Rubbing workshop (拓印书肆) in the south-east corner: walled courtyard,
      small hall with bookshelf walls, lectern tables, ink barrels and a
      paper-drying rack of fence posts and plank bars
    - Lecture hall (讲经堂) west of the axis: stepped platform, open front
      porch, hall body and overhanging gable roof (悬山顶)
    - Ink pool (墨池) east of the pavilion with a stone rim and a
      brush-washing trough
    - Paved axial causeway with lantern posts and two rows of cypresses

Note: the rubbing-shop courtyard north wall is set at z 5068, just south of
the scripture corridor eaves (corridor spans z 5032..5068), so both the
"x 2050..2140, z 5050..5140" shop plot and the "z 5050" corridor fit
without overlapping.
"""

# ---------------------------------------------------------------------------
# Site constants (local Chang'an coordinates; world = +9000/+64/+9000 via lib).
# ---------------------------------------------------------------------------
SITE_X1, SITE_Z1 = 1650, 4750
SITE_X2, SITE_Z2 = 2150, 5150

# Central north-south axis through the south gate.
AXIS_X = 1900
PATH_X1, PATH_X2 = 1892, 1908

# Shitai Xiaojing Pavilion (石台孝经碑亭) on the axis near z 4950.
PAV_CX, PAV_CZ = 1900, 4950

# Kaicheng Stone Classics corridors (开成石经长廊).
CORR_N_Z1, CORR_N_Z2 = 4836, 4864  # centred on z 4850
CORR_S_Z1, CORR_S_Z2 = 5036, 5064  # centred on z 5050
CORR_X1, CORR_X2 = 1698, 2102

# Epitaph forest (墓志铭林) in the north half.
EPITAPH_ROW_A_Z = 4770
EPITAPH_ROW_B_Z = 4806

# Lecture hall (讲经堂) west of the axis.
HALL_X1, HALL_Z1 = 1690, 4900
HALL_X2, HALL_Z2 = 1810, 5000

# Ink pool (墨池) east of the pavilion.
POOL_X1, POOL_Z1 = 1975, 4920
POOL_X2, POOL_Z2 = 2035, 4970

# Rubbing workshop courtyard (拓印书肆), south-east corner.
SHOP_X1, SHOP_Z1 = 2050, 5068
SHOP_X2, SHOP_Z2 = 2140, 5140


def _pavilion_columns(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y1: int, y2: int,
) -> None:
    """Dark-oak posts on the four corners and edge midpoints of a pavilion storey."""
    mx, mz = (x1 + x2) // 2, (z1 + z2) // 2
    posts = [
        (x1, z1), (x2 - 1, z1), (x1, z2 - 1), (x2 - 1, z2 - 1),
        (mx - 1, z1), (mx - 1, z2 - 1),
        (x1, mz - 1), (x2 - 1, mz - 1),
    ]
    for i, (px, pz) in enumerate(posts):
        add_fill(fills, f"{label} col {i}", (px, y1, pz), (px + 1, y2, pz + 1), M.LOG)


def _scripture_stele(fills: list[Fill], label: str, x: int, z: int) -> None:
    """One Kaicheng classic stele: dark base, quartz-pillar shaft, gilded cap."""
    add_fill(fills, f"{label} base", (x - 1, 5, z - 1), (x + 1, 5, z + 1), M.DARK)
    add_fill(fills, f"{label} shaft", (x, 6, z), (x, 12, z), "minecraft:quartz_pillar[axis=y]")
    add_fill(fills, f"{label} cap", (x - 1, 13, z - 1), (x + 1, 13, z + 1), M.GOLD)


def _epitaph(fills: list[Fill], label: str, x: int, z: int) -> None:
    """One small epitaph tablet: smooth-stone foot, 3x1x6 quartz slab."""
    add_fill(fills, f"{label} foot", (x, 4, z), (x + 2, 4, z), M.SMOOTH)
    add_fill(fills, f"{label} slab", (x, 5, z), (x + 2, 9, z), M.QUARTZ)


def _paper_rack(fills: list[Fill], label: str, x1: int, x2: int, z: int) -> None:
    """Paper-drying rack: fence posts, a plank crossbar, hanging paper sheets."""
    for px in range(x1, x2 + 1, 15):
        add_fill(fills, f"{label} post {px}", (px, 4, z), (px, 7, z), M.FENCE)
    add_fill(fills, f"{label} bar", (x1 - 2, 8, z), (x2 + 2, 8, z), M.WOOD)
    for sx in range(x1 + 5, x2, 15):
        add_fill(fills, f"{label} sheet {sx}", (sx, 6, z), (sx, 7, z), M.WHITE_WOOL)


def build_beilin_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site grading: stone base y0..1, lawn y2..3, perimeter white wall
    #    with a south mountain gate (山门) and gate tower.
    # ------------------------------------------------------------------
    add_fill(fills, "beilin foundation", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "beilin lawn", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)
    add_fill(fills, "beilin wall n", (SITE_X1, 4, SITE_Z1), (SITE_X2, 9, SITE_Z1 + 2), M.WHITE_TERRACOTTA)
    add_fill(fills, "beilin wall s", (SITE_X1, 4, SITE_Z2 - 2), (SITE_X2, 9, SITE_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "beilin wall w", (SITE_X1, 4, SITE_Z1), (SITE_X1 + 2, 9, SITE_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "beilin wall e", (SITE_X2 - 2, 4, SITE_Z1), (SITE_X2, 9, SITE_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "beilin coping n", (SITE_X1, 10, SITE_Z1), (SITE_X2, 10, SITE_Z1 + 2), M.DARK)
    add_fill(fills, "beilin coping s", (SITE_X1, 10, SITE_Z2 - 2), (SITE_X2, 10, SITE_Z2), M.DARK)
    add_fill(fills, "beilin coping w", (SITE_X1, 10, SITE_Z1), (SITE_X1 + 2, 10, SITE_Z2), M.DARK)
    add_fill(fills, "beilin coping e", (SITE_X2 - 2, 10, SITE_Z1), (SITE_X2, 10, SITE_Z2), M.DARK)
    # South gate: opening, gilded threshold rim, inner landing.
    add_fill(fills, "beilin gate opening", (1876, 4, SITE_Z2 - 2), (1924, 9, SITE_Z2), M.AIR)
    add_fill(fills, "beilin gate rim", (1874, 4, SITE_Z2 - 3), (1926, 4, SITE_Z2 - 3), M.GOLD)
    add_fill(fills, "beilin gate landing", (1876, 3, SITE_Z2 - 6), (1924, 4, SITE_Z2 - 3), M.SMOOTH)
    # Gate tower (gatehouse) astride the opening.
    add_fill(fills, "beilin gate deck", (1872, 10, 5140), (1928, 10, 5146), M.WOOD)
    add_fill(fills, "beilin gate rail n", (1872, 11, 5140), (1928, 11, 5140), M.FENCE)
    add_fill(fills, "beilin gate rail s", (1872, 11, 5146), (1928, 11, 5146), M.FENCE)
    add_fill(fills, "beilin gate body", (1872, 11, 5140), (1928, 13, 5146), M.RED_WALL)
    add_ridge_roof(fills, "beilin gate roof", 1870, 5138, 1930, 5148, 14, layers=1,
                   ridge_axis="x", roof_block=M.ROOF_GREEN)

    # ------------------------------------------------------------------
    # 2. Axial stone causeway from the gate north to the pavilion.
    # ------------------------------------------------------------------
    add_fill(fills, "beilin causeway", (PATH_X1, 4, 4985), (PATH_X2, 4, SITE_Z2 - 3), M.SMOOTH)

    # ------------------------------------------------------------------
    # 3. Epitaph forest (墓志铭林): two staggered ranks of small tablets.
    # ------------------------------------------------------------------
    for i, ex in enumerate(range(1700, 1970, 30)):
        _epitaph(fills, f"beilin epitaph a{i}", ex, EPITAPH_ROW_A_Z)
    for i, ex in enumerate(range(1715, 1985, 30)):
        _epitaph(fills, f"beilin epitaph b{i}", ex, EPITAPH_ROW_B_Z)

    # ------------------------------------------------------------------
    # 4. Kaicheng Stone Classics corridors (开成石经长廊), north and south
    #    wings: timber colonnades with ridge roofs and two rows of steles.
    # ------------------------------------------------------------------
    for tag, cz1, cz2 in (("n", CORR_N_Z1, CORR_N_Z2), ("s", CORR_S_Z1, CORR_S_Z2)):
        ccz = (cz1 + cz2) // 2
        add_fill(fills, f"beilin corridor {tag} floor", (CORR_X1, 4, cz1), (CORR_X2, 4, cz2), M.SMOOTH)
        # Colonnade: slender log posts on both long sides, skipping the
        # south corridor bay where the axial causeway passes through.
        for cx in range(1702, CORR_X2 - 2, 32):
            if tag == "s" and PATH_X1 <= cx <= PATH_X2:
                continue
            add_fill(fills, f"beilin corridor {tag} col n {cx}", (cx, 5, cz1 + 1), (cx, 10, cz1 + 1), M.LOG)
            add_fill(fills, f"beilin corridor {tag} col s {cx}", (cx, 5, cz2 - 1), (cx, 10, cz2 - 1), M.LOG)
        add_fill(fills, f"beilin corridor {tag} beam n", (CORR_X1, 11, cz1 + 1), (CORR_X2, 11, cz1 + 1), M.LOG)
        add_fill(fills, f"beilin corridor {tag} beam s", (CORR_X1, 11, cz2 - 1), (CORR_X2, 11, cz2 - 1), M.LOG)
        add_ridge_roof(fills, f"beilin corridor {tag} roof", CORR_X1, cz1 - 2, CORR_X2, cz2 + 2,
                       12, layers=2, ridge_axis="x", roof_block=M.ROOF_GREEN)
        # Two rows of scripture steles, spaced 8, centred on the axis.
        for sz in (ccz - 6, ccz + 6):
            for sx in range(1864, 1941, 8):
                if tag == "s" and PATH_X1 <= sx <= PATH_X2:
                    continue
                _scripture_stele(fills, f"beilin classic {tag} {sx},{sz}", sx, sz)

    # ------------------------------------------------------------------
    # 5. Shitai Xiaojing Pavilion (石台孝经碑亭): stepped stone platform,
    #    two red-walled storeys with a double eave, gilded pyramid roof,
    #    and the giant 3x3x12 classic stele at its heart.
    # ------------------------------------------------------------------
    add_platform_with_steps(fills, "beilin pavilion platform", 1870, 4920, 1930, 4980, 4,
                            [(2, 0, M.STONE), (1, 4, M.SMOOTH)])
    add_fill(fills, "beilin pavilion step a", (1890, 6, 4977), (1910, 6, 4980), M.SMOOTH)
    add_fill(fills, "beilin pavilion step b", (1890, 5, 4981), (1910, 5, 4984), M.SMOOTH)
    # Storey 1 (y 7..17).
    add_hollow_box(fills, "beilin pavilion body1", 1882, 7, 4932, 1918, 17, 4968, M.RED_WALL, thickness=1)
    _pavilion_columns(fills, "beilin pavilion body1", 1882, 4932, 1918, 4968, 7, 17)
    add_fill(fills, "beilin pavilion door", (1894, 8, 4968), (1906, 12, 4968), M.AIR)
    add_fill(fills, "beilin pavilion window n", (1894, 9, 4932), (1906, 11, 4932), M.GLASS)
    add_fill(fills, "beilin pavilion window w", (1882, 9, 4944), (1882, 11, 4956), M.GLASS)
    add_fill(fills, "beilin pavilion window e", (1918, 9, 4944), (1918, 11, 4956), M.GLASS)
    add_fill(fills, "beilin pavilion lamp sw", (1886, 7, 4936), (1886, 7, 4936), M.SEA_LANTERN)
    add_fill(fills, "beilin pavilion lamp ne", (1914, 7, 4964), (1914, 7, 4964), M.SEA_LANTERN)
    # Lower eave ring (重檐下檐).
    add_pagoda_eave(fills, "beilin pavilion lower eave", PAV_CX, PAV_CZ, radius=18, y=17,
                    overhang=3, roof_block=M.ROOF_GREEN)
    # Storey 2 (y 18..25), setback.
    add_hollow_box(fills, "beilin pavilion body2", 1886, 18, 4936, 1914, 25, 4964, M.RED_WALL, thickness=1)
    _pavilion_columns(fills, "beilin pavilion body2", 1886, 4936, 1914, 4964, 18, 25)
    add_fill(fills, "beilin pavilion window2 n", (1894, 20, 4936), (1906, 22, 4936), M.GLASS)
    add_fill(fills, "beilin pavilion window2 s", (1894, 20, 4964), (1906, 22, 4964), M.GLASS)
    # Gilded pyramid roof (攒尖金顶).
    add_pyramid_roof(fills, "beilin pavilion roof", PAV_CX, PAV_CZ, radius=15, y=26,
                     roof_block=M.ROOF_GREEN, apex_block=M.GOLD)
    # The giant Shitai Xiaojing stele: stone platform base, dark pedestal,
    # 3x3x12 quartz-pillar shaft, gilded cap (built last so it stays intact).
    add_fill(fills, "beilin xiaojing tai", (1896, 8, 4946), (1904, 8, 4954), M.DARK)
    add_fill(fills, "beilin xiaojing pedestal", (1898, 9, 4948), (1902, 9, 4952), M.DARK)
    add_fill(fills, "beilin xiaojing shaft", (1899, 10, 4949), (1901, 21, 4951),
             "minecraft:quartz_pillar[axis=y]")
    add_fill(fills, "beilin xiaojing cap", (1898, 22, 4948), (1902, 22, 4952), M.GOLD)
    add_fill(fills, "beilin xiaojing cap top", (1899, 23, 4949), (1901, 23, 4951), M.GOLD)

    # ------------------------------------------------------------------
    # 6. Lecture hall (讲经堂) west of the axis: steps, open porch, hall
    #    body, overhanging gable roof (悬山顶).
    # ------------------------------------------------------------------
    add_platform_with_steps(fills, "beilin hall platform", HALL_X1, HALL_Z1, HALL_X2, HALL_Z2, 4,
                            [(1, 0, M.STONE), (1, 3, M.SMOOTH)])
    add_fill(fills, "beilin hall step a", (1808, 4, 4940), (1812, 4, 4960), M.SMOOTH)
    add_fill(fills, "beilin hall step b", (1813, 3, 4942), (1817, 3, 4958), M.SMOOTH)
    for pz in range(4908, 4992, 16):
        add_fill(fills, f"beilin hall porch col {pz}", (1802, 6, pz), (1803, 10, pz + 1), M.LOG)
    add_hollow_box(fills, "beilin hall body", 1700, 6, 4906, 1795, 14, 4994, M.RED_WALL, thickness=1)
    add_fill(fills, "beilin hall door", (1795, 7, 4938), (1795, 11, 4962), M.AIR)
    add_fill(fills, "beilin hall window n", (1720, 8, 4906), (1740, 10, 4906), M.GLASS)
    add_fill(fills, "beilin hall window s", (1720, 8, 4994), (1740, 10, 4994), M.GLASS)
    add_fill(fills, "beilin hall window w", (1700, 8, 4940), (1700, 10, 4960), M.GLASS)
    # Interior: rostrum, lectern, bench rows.
    add_fill(fills, "beilin hall rostrum", (1704, 7, 4930), (1712, 8, 4970), M.SMOOTH)
    add_fill(fills, "beilin hall lectern", (1708, 9, 4948), (1708, 9, 4948), "minecraft:lectern")
    add_fill(fills, "beilin hall bench a", (1730, 7, 4920), (1731, 7, 4980), M.WOOD)
    add_fill(fills, "beilin hall bench b", (1748, 7, 4920), (1749, 7, 4980), M.WOOD)
    add_ridge_roof(fills, "beilin hall roof", 1697, 4903, 1798, 4997, 15, layers=3,
                   ridge_axis="z", roof_block=M.ROOF_GREEN)

    # ------------------------------------------------------------------
    # 7. Ink pool (墨池) east of the pavilion, with stone rim and a
    #    brush-washing trough.
    # ------------------------------------------------------------------
    add_pool(fills, "beilin ink pool", POOL_X1, POOL_Z1, POOL_X2, POOL_Z2, 4, depth=1)
    add_outline(fills, "beilin ink pool rim", POOL_X1 - 2, POOL_Z1 - 2, POOL_X2 + 2, POOL_Z2 + 2,
                4, 4, M.STONE, thickness=1)
    add_fill(fills, "beilin wash trough", (2045, 4, 4938), (2053, 5, 4946), M.SMOOTH)
    add_fill(fills, "beilin wash trough water", (2047, 5, 4940), (2051, 5, 4944), M.WATER)

    # ------------------------------------------------------------------
    # 8. Rubbing workshop (拓印书肆), south-east corner: walled courtyard,
    #    small hall with bookshelves, lectern tables, ink barrels and a
    #    paper-drying rack.
    # ------------------------------------------------------------------
    add_fill(fills, "beilin shop wall n", (SHOP_X1, 4, SHOP_Z1), (SHOP_X2 - 1, 9, SHOP_Z1 + 1), M.WHITE_TERRACOTTA)
    add_fill(fills, "beilin shop wall s", (SHOP_X1, 4, SHOP_Z2 - 1), (SHOP_X2 - 1, 9, SHOP_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "beilin shop wall w", (SHOP_X1, 4, SHOP_Z1), (SHOP_X1 + 1, 9, SHOP_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "beilin shop wall e", (SHOP_X2 - 2, 4, SHOP_Z1), (SHOP_X2 - 1, 9, SHOP_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "beilin shop coping n", (SHOP_X1, 10, SHOP_Z1), (SHOP_X2 - 1, 10, SHOP_Z1 + 1), M.DARK)
    add_fill(fills, "beilin shop coping s", (SHOP_X1, 10, SHOP_Z2 - 1), (SHOP_X2 - 1, 10, SHOP_Z2), M.DARK)
    add_fill(fills, "beilin shop coping w", (SHOP_X1, 10, SHOP_Z1), (SHOP_X1 + 1, 10, SHOP_Z2), M.DARK)
    add_fill(fills, "beilin shop coping e", (SHOP_X2 - 2, 10, SHOP_Z1), (SHOP_X2 - 1, 10, SHOP_Z2), M.DARK)
    add_fill(fills, "beilin shop gate", (2085, 4, SHOP_Z1), (2105, 9, SHOP_Z1 + 1), M.AIR)
    add_fill(fills, "beilin shop gate lintel", (2083, 10, SHOP_Z1), (2107, 10, SHOP_Z1 + 1), M.GOLD)
    # Shop hall with plank floor and ridge roof.
    add_fill(fills, "beilin shop floor", (2070, 4, 5086), (2120, 4, 5126), M.WOOD)
    add_hollow_box(fills, "beilin shop hall", 2070, 5, 5086, 2120, 12, 5126, M.RED_WALL, thickness=1)
    add_fill(fills, "beilin shop door", (2120, 5, 5100), (2120, 9, 5112), M.AIR)
    add_fill(fills, "beilin shop window n", (2080, 7, 5086), (2100, 9, 5086), M.GLASS)
    add_fill(fills, "beilin shop window s", (2080, 7, 5126), (2100, 9, 5126), M.GLASS)
    # Bookshelf walls (书架墙) along the north and west interior.
    add_fill(fills, "beilin shop shelf n", (2072, 5, 5088), (2118, 10, 5089), "minecraft:bookshelf")
    add_fill(fills, "beilin shop shelf w", (2072, 5, 5090), (2073, 10, 5124), "minecraft:bookshelf")
    # Rubbing table (拓案) with lecterns, and ink barrels (墨缸).
    add_fill(fills, "beilin shop table", (2088, 5, 5102), (2098, 5, 5110), M.WOOD)
    add_fill(fills, "beilin shop lectern a", (2091, 6, 5105), (2091, 6, 5105), "minecraft:lectern")
    add_fill(fills, "beilin shop lectern b", (2095, 6, 5105), (2095, 6, 5105), "minecraft:lectern")
    add_fill(fills, "beilin shop ink barrel a", (2110, 5, 5092), (2110, 5, 5092), "minecraft:barrel")
    add_fill(fills, "beilin shop ink barrel b", (2113, 5, 5092), (2113, 5, 5092), "minecraft:barrel")
    add_fill(fills, "beilin shop lamp", (2094, 12, 5105), (2094, 12, 5105), M.SEA_LANTERN)
    # Paper-drying rack in the south courtyard strip.
    _paper_rack(fills, "beilin shop rack", 2058, 2088, 5132)
    # Courtyard lamp post by the gate.
    add_fill(fills, "beilin shop lamp post", (2110, 4, 5073), (2110, 9, 5073), M.LOG)
    add_fill(fills, "beilin shop lamp head", (2110, 10, 5073), (2110, 10, 5073), M.SEA_LANTERN)
    add_ridge_roof(fills, "beilin shop roof", 2068, 5084, 2122, 5128, 13, layers=2,
                   ridge_axis="x", roof_block=M.ROOF_GREEN)

    # ------------------------------------------------------------------
    # 9. Causeway lantern posts and two rows of cypresses.
    # ------------------------------------------------------------------
    add_lantern_line(fills, "beilin axis lanterns wn", 1884, 4984, 1884, 5020, 4, every=36)
    add_lantern_line(fills, "beilin axis lanterns ws", 1884, 5072, 1884, 5144, 4, every=48)
    add_lantern_line(fills, "beilin axis lanterns en", 1916, 4984, 1916, 5020, 4, every=36)
    add_lantern_line(fills, "beilin axis lanterns es", 1916, 5072, 1916, 5144, 4, every=48)
    for tz in (4996, 5026, 5078, 5108):
        add_tree(fills, f"beilin cypress w {tz}", 1866, tz, 4, height=7, spread=2)
        add_tree(fills, f"beilin cypress e {tz}", 1934, tz, 4, height=7, spread=2)


def main() -> None:
    run_builder(build_beilin_3d, "beilin_3d")


if __name__ == "__main__":
    main()
