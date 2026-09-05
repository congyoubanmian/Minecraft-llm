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
    add_tree,
    run_builder,
)


"""
Food Street 3D (西市南门外饮食街·长安味道) - a Tang market food street of
street stalls and cookshops (煎饼 / 汤饼 / 蒸饼 / 饮子) south of the West
Market, the "smoke and hustle" (烟火气) quarter where the whole city came
to eat.

Location in Chang'an city local coordinates:
    Plot: x 1850..2200, z 3560..3800 (strict bounds - nothing may leave
    them; roof eaves, banners and trees included). The strip z < 3560
    stays clear so the east-west canal (canal_waterway.py, running
    z 3450..3550) is not touched. The ward gate at (2165..2175,
    3419..3421) (ward_gates_3d.py) and every West Market building
    (xishi_qiting_3d.py tower/tavern at x 1238..1344, tavern.py market
    rows ending at z <= 3060) lie north of the plot and are avoided; the
    Tangchang Guan abbey (tangchang_guan_3d.py, x 1150..1500,
    z 3120..3470) lies far to the west; the next ward gate sits at
    z >= 3820, south of the plot. Compact 240-deep plot: the two shop
    rows are compressed to three 31-block bays per side with no back
    courts, and the paifang gate closes the street at the south end
    (z ~3787). Ground is graded to stone y0..1 + grass y2..3 (lawn
    surface y4); the street paving sits at y4 and the main structures
    rise from y5.

Distinctive features:
    - North-south food street, 12 wide: polished-andesite flagstones with
      a central open drain (smooth-stone trough with flowing water) crossed
      by three timber cover-board segments
    - Soup-noodle cookshop (汤饼铺, east row): great dough case with three
      bundles of white noodle strands, a big soup cauldron (barrel + glowing
      boiling broth + twin steam plumes), a quartz shopkeeper figure and
      four diner stools
    - Steamer tower (蒸饼炉, east row): brick hearth with glowing fire-box
      mouth, a three-tier bamboo steamer stack (fence hoops + plank trays)
      venting steam, and a display rack of six white steamed cakes
    - Drink house (饮子铺, west row, centrepiece): timber counter with a
      lectern menu and three copper kettles (barrels), five named drink
      jars (stone ring + colour-coded wool "liquid surface": sour-plum,
      apricot, mint, peach and milk), a blue cloth awning slung out over
      the street on poles, and a grand gilded "饮子" signboard
    - Charcoal grill (烤肉架, west row): iron-bar rack over red-wool coals
      with four log-skewer kebabs (red / brown meat), plus a stone chimney
      with smoke
    - Pancake griddle stall (煎饼摊, west row): stone range with a smooth
      griddle, a stacked pile of yellow pancakes and an oil jar
    - Street well with windlass (辘轳井) in the open east yard
    - Three open-air shed seating areas down the street centre: four-post
      cloth roofs (red / blue / yellow), three table-bench sets each with
      gold cups and dishes, hanging lanterns
    - Street paifang gate at the south end: twin red columns on plinths,
      double crossbeams, a dark board with two gold glyphs ("食" plaque)
      and a small gable cap; paved south plaza with lantern posts
    - Every shop flies a coloured wool banner (幌子) on a fence pole and
      hangs a red-hooded sea-lantern under its eave; slim lamp posts line
      the street and tree groups dot the lawns on both flanks
"""

# ---------------------------------------------------------------------------
# Site (strict bounds), street and shop-row bays.
# ---------------------------------------------------------------------------
SITE_X1, SITE_Z1 = 1850, 3560
SITE_X2, SITE_Z2 = 2100, 3800

STREET_X1, STREET_X2 = 2019, 2030          # 12-wide flagstone street
STREET_Z1, STREET_Z2 = 3566, 3794
DRAIN_X1, DRAIN_X2 = 2024, 2025            # central open drain
DRAIN_COVERS = ((3578, 3598), (3658, 3678), (3716, 3736))

# Shop-row bays along the street (three per side, 31 long each).
ROW1_Z1, ROW1_Z2 = 3570, 3600
ROW2_Z1, ROW2_Z2 = 3610, 3640
ROW3_Z1, ROW3_Z2 = 3650, 3680

# East shop row: open front plane at x=2031 (faces west, to the street),
# back wall at x=2044 (14 deep).
E_X1, E_X2 = 2031, 2044

# West shop row: back wall at x=2005, open front plane at x=2018
# (faces east, to the street; 14 deep).
W_X1, W_X2 = 2005, 2018

# Street-centre shed seating: (x1, z1) north-west corners, 10x10 each.
SHEDS = ((2020, 3690, M.RED_WOOL), (2020, 3705, M.BLUE_WOOL), (2020, 3720, M.YELLOW_WOOL))

# South paifang gate (spans the street) and south plaza.
GATE_Z1, GATE_Z2 = 3784, 3786              # column depth
PLAZA_X1, PLAZA_Z1, PLAZA_Z2 = 2010, 3750, 3800

# Shared block ids used by this module.
BARREL = "minecraft:barrel"
LECTERN_E = "minecraft:lectern[facing=east]"
LOG_X = "minecraft:dark_oak_log[axis=x]"
LOG_Z = "minecraft:dark_oak_log[axis=z]"
BROWN_TERRACOTTA = "minecraft:brown_terracotta"
DARK_STAIR_S = "minecraft:deepslate_tile_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]"
DARK_STAIR_N = "minecraft:deepslate_tile_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]"
DARK_STAIR_E = "minecraft:deepslate_tile_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]"
DARK_STAIR_W = "minecraft:deepslate_tile_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]"
DARK_SLAB = "minecraft:dark_prismarine_slab[type=bottom,waterlogged=false]"


# ---------------------------------------------------------------------------
# Reusable stall / prop helpers.
# ---------------------------------------------------------------------------
def _stall(
    fills: list[Fill],
    label: str,
    x1: int,
    z1: int,
    x2: int,
    z2: int,
    open_side: str,
    plaque: bool = True,
) -> None:
    """One open-fronted market stall shell (铺面).

    Plank floor at y4, three timber walls y5..10, the street side left
    open with corner posts, an entry gap and a low counter, a log lintel,
    a one-step gable roof (ridge along z), a fascia plaque and a hanging
    eave lantern by the entry. open_side 'w' = front on x1 (east row),
    'e' = front on x2 (west row).
    """
    front_x = x1 if open_side == "w" else x2
    back_x = x2 if open_side == "w" else x1
    zc = (z1 + z2) // 2
    add_fill(fills, f"{label} floor", (x1, 4, z1), (x2, 4, z2), M.WOOD)
    add_fill(fills, f"{label} wall back", (back_x, 5, z1), (back_x, 10, z2), M.WOOD)
    add_fill(fills, f"{label} wall side n", (x1, 5, z1), (x2, 10, z1), M.WOOD)
    add_fill(fills, f"{label} wall side s", (x1, 5, z2), (x2, 10, z2), M.WOOD)
    add_fill(fills, f"{label} air", (x1 + 1, 5, z1 + 1), (x2 - 1, 9, z2 - 1), M.AIR)
    add_fill(fills, f"{label} post n", (front_x, 5, z1), (front_x, 10, z1), M.LOG)
    add_fill(fills, f"{label} post s", (front_x, 5, z2), (front_x, 10, z2), M.LOG)
    add_fill(fills, f"{label} lintel", (front_x, 10, z1), (front_x, 10, z2), LOG_Z)
    add_fill(fills, f"{label} counter n", (front_x, 5, z1 + 2), (front_x, 6, z1 + 8), M.WOOD)
    add_fill(fills, f"{label} counter s", (front_x, 5, z2 - 8), (front_x, 6, z2 - 2), M.WOOD)
    # Gable roof: ridge along z at y12, single stair step each side (y11).
    mx = (x1 + x2) // 2
    add_fill(fills, f"{label} ridge", (mx, 12, z1 - 1), (mx + 1, 12, z2 + 1), M.ROOF_DARK)
    if open_side == "w":
        add_fill(fills, f"{label} roof street", (x1 - 1, 11, z1 - 1), (mx - 1, 11, z2 + 1), DARK_STAIR_E)
        add_fill(fills, f"{label} roof back", (mx + 1, 11, z1 - 1), (x2 + 1, 11, z2 + 1), DARK_STAIR_W)
    else:
        add_fill(fills, f"{label} roof street", (mx + 1, 11, z1 - 1), (x2 + 1, 11, z2 + 1), DARK_STAIR_W)
        add_fill(fills, f"{label} roof back", (x1 - 1, 11, z1 - 1), (mx - 1, 11, z2 + 1), DARK_STAIR_E)
    if plaque:
        px = front_x - 1 if open_side == "w" else front_x + 1
        add_fill(fills, f"{label} plaque board", (px, 8, zc - 3), (px, 10, zc + 3), M.DARK)
        add_fill(fills, f"{label} plaque gold", (px, 9, zc - 2), (px, 9, zc + 2), M.GOLD)
    _eave_lantern(fills, f"{label} lantern", front_x - 1 if open_side == "w" else front_x + 1, z1 + 3)


def _eave_lantern(fills: list[Fill], label: str, x: int, z: int) -> None:
    """Eave lantern: red-wool hood over a glowing sea lantern."""
    add_fill(fills, f"{label} hood", (x, 10, z), (x, 10, z), M.RED_WOOL)
    add_fill(fills, f"{label} light", (x, 9, z), (x, 9, z), M.SEA_LANTERN)


def _banner(fills: list[Fill], label: str, px: int, pz: int, wool: str, arm_dir: str) -> None:
    """Shop banner (幌子): fence pole, horizontal挑 arm and a wool cloth."""
    dx = -1 if arm_dir == "w" else 1
    add_fill(fills, f"{label} pole", (px, 5, pz), (px, 9, pz), M.FENCE)
    add_fill(fills, f"{label} arm", (px + dx, 9, pz), (px + dx * 2, 9, pz), LOG_X)
    add_fill(fills, f"{label} cloth", (px + dx, 6, pz), (px + dx * 2, 8, pz), wool)


def _stool(fills: list[Fill], label: str, x: int, z: int) -> None:
    add_fill(fills, f"{label} leg", (x, 5, z), (x, 5, z), M.FENCE)
    add_fill(fills, f"{label} seat", (x, 6, z), (x, 6, z), M.WOOD)


def _table_set(
    fills: list[Fill],
    label: str,
    x1: int,
    z1: int,
    x2: int,
    z2: int,
    bench_axis: str,
) -> None:
    """Table with two benches and gold cups/dishes (桌凳+金杯盘)."""
    add_fill(fills, f"{label} table", (x1, 5, z1), (x2, 5, z2), M.WOOD)
    if bench_axis == "z":
        add_fill(fills, f"{label} bench n", (x1, 5, z1 - 1), (x2, 5, z1 - 1), M.FENCE)
        add_fill(fills, f"{label} bench s", (x1, 5, z2 + 1), (x2, 5, z2 + 1), M.FENCE)
    else:
        add_fill(fills, f"{label} bench w", (x1 - 1, 5, z1), (x1 - 1, 5, z2), M.FENCE)
        add_fill(fills, f"{label} bench e", (x2 + 1, 5, z1), (x2 + 1, 5, z2), M.FENCE)
    add_fill(fills, f"{label} cup a", (x1, 6, z1), (x1, 6, z1), M.GOLD)
    add_fill(fills, f"{label} cup b", (x2, 6, z2), (x2, 6, z2), M.GOLD)


def _shed(fills: list[Fill], label: str, x1: int, z1: int, cloth: str) -> None:
    """Open-air eatery shed: four posts, cloth roof, lantern, 3 table sets."""
    x2, z2 = x1 + 9, z1 + 9
    for i, (px, pz) in enumerate(((x1, z1), (x2, z1), (x1, z2), (x2, z2))):
        add_fill(fills, f"{label} post {i}", (px, 5, pz), (px, 8, pz), M.LOG)
    add_fill(fills, f"{label} cloth roof", (x1, 9, z1), (x2, 9, z2), cloth)
    add_fill(fills, f"{label} lamp", (x1 + 4, 8, z1 + 4), (x1 + 4, 8, z1 + 4), M.SEA_LANTERN)
    _table_set(fills, f"{label} table a", x1 + 2, z1 + 2, x1 + 3, z1 + 3, "z")
    _table_set(fills, f"{label} table b", x1 + 6, z1 + 2, x1 + 7, z1 + 3, "z")
    _table_set(fills, f"{label} table c", x1 + 4, z1 + 6, x1 + 5, z1 + 7, "x")


def _drink_jar(fills: list[Fill], label: str, x1: int, z1: int, liquid: str) -> None:
    """One drink jar (饮子坛): 3x3 stone ring, brown body, wool liquid surface."""
    add_outline(fills, f"{label} stone ring", x1, z1, x1 + 2, z1 + 2, 5, 5, M.SMOOTH)
    add_fill(fills, f"{label} body", (x1, 6, z1), (x1 + 2, 6, z1 + 2), BROWN_TERRACOTTA)
    add_fill(fills, f"{label} surface", (x1, 7, z1), (x1 + 2, 7, z1 + 2), liquid)


def _steam(fills: list[Fill], label: str, x: int, z: int, y1: int, y2: int) -> None:
    """Twin white steam plumes (白汽两段) rising from a pot or tower."""
    add_fill(fills, f"{label} steam low", (x, y1, z), (x + 1, y1 + 1, z), M.WHITE_TERRACOTTA)
    add_fill(fills, f"{label} steam high", (x, y1 + 2, z), (x + 1, y2, z), M.WHITE_TERRACOTTA)


def _lamp_post(fills: list[Fill], label: str, x: int, z: int) -> None:
    """Slim street lamp: fence post with a sea lantern head."""
    add_fill(fills, f"{label} post", (x, 5, z), (x, 7, z), M.FENCE)
    add_fill(fills, f"{label} light", (x, 8, z), (x, 8, z), M.SEA_LANTERN)


# ---------------------------------------------------------------------------
# Main builder.
# ---------------------------------------------------------------------------
def build_food_street_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site clearing and grading: stone base, grass lawn.
    # ------------------------------------------------------------------
    add_fill(fills, "foodst clear site", (SITE_X1, 4, SITE_Z1), (SITE_X2, 8, SITE_Z2), M.AIR)
    add_fill(fills, "foodst clear street", (STREET_X1 - 4, 4, STREET_Z1), (STREET_X2 + 4, 16, STREET_Z2), M.AIR)
    add_fill(fills, "foodst clear shop e1", (E_X1 - 1, 4, ROW1_Z1 - 1), (E_X2 + 1, 16, ROW1_Z2 + 1), M.AIR)
    add_fill(fills, "foodst clear shop e2", (E_X1 - 1, 4, ROW2_Z1 - 1), (E_X2 + 1, 16, ROW2_Z2 + 1), M.AIR)
    add_fill(fills, "foodst clear yard e", (E_X1 - 1, 4, ROW3_Z1 - 1), (E_X2 + 1, 12, ROW3_Z2 + 1), M.AIR)
    add_fill(fills, "foodst clear shop w1", (W_X1 - 1, 4, ROW1_Z1 - 1), (W_X2 + 1, 16, ROW1_Z2 + 1), M.AIR)
    add_fill(fills, "foodst clear shop w2", (W_X1 - 1, 4, ROW2_Z1 - 1), (W_X2 + 1, 18, ROW2_Z2 + 1), M.AIR)
    add_fill(fills, "foodst clear shop w3", (W_X1 + 3, 4, ROW3_Z1 - 1), (W_X2 + 1, 16, ROW3_Z2 + 1), M.AIR)
    add_fill(fills, "foodst clear gate", (2012, 4, 3774), (2037, 20, 3798), M.AIR)
    add_fill(fills, "foodst ground stone", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "foodst ground grass", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)

    # ------------------------------------------------------------------
    # 2. The street: andesite flagstones, central drain trough with
    #    water and three timber cover-board segments, aprons.
    # ------------------------------------------------------------------
    add_fill(fills, "foodst street pave", (STREET_X1, 4, STREET_Z1), (STREET_X2, 4, STREET_Z2), M.ANDESITE)
    add_fill(fills, "foodst drain bed", (DRAIN_X1, 3, 3568), (DRAIN_X2, 3, 3792), M.SMOOTH)
    add_fill(fills, "foodst drain water", (DRAIN_X1, 4, 3568), (DRAIN_X2, 4, 3792), M.WATER)
    for ci, (cz1, cz2) in enumerate(DRAIN_COVERS):
        add_fill(fills, f"foodst drain cover {ci}", (DRAIN_X1, 4, cz1), (DRAIN_X2, 4, cz2), M.WOOD)
    add_fill(fills, "foodst north apron", (2015, 4, SITE_Z1), (2034, 4, 3565), M.ANDESITE)
    add_fill(fills, "foodst apron e1", (2027, 4, ROW1_Z1), (2030, 4, ROW1_Z2), M.SMOOTH)
    add_fill(fills, "foodst apron e2", (2027, 4, ROW2_Z1), (2030, 4, ROW2_Z2), M.SMOOTH)
    add_fill(fills, "foodst apron e3", (E_X1, 4, ROW3_Z1), (2042, 4, ROW3_Z2), M.SMOOTH)
    add_fill(fills, "foodst apron w1", (2019, 4, ROW1_Z1), (2022, 4, ROW1_Z2), M.SMOOTH)
    add_fill(fills, "foodst apron w2", (2019, 4, ROW2_Z1), (2022, 4, ROW2_Z2), M.SMOOTH)
    add_fill(fills, "foodst apron w3", (2019, 4, ROW3_Z1), (2022, 4, ROW3_Z2), M.SMOOTH)
    add_fill(fills, "foodst south plaza", (PLAZA_X1, 4, PLAZA_Z1), (2040, 4, PLAZA_Z2), M.ANDESITE)

    # ------------------------------------------------------------------
    # 3. 汤饼铺 soup-noodle shop (east row, first stall).
    # ------------------------------------------------------------------
    _stall(fills, "foodst noodle", E_X1, ROW1_Z1, E_X2, ROW1_Z2, "w")
    # Great dough case with three bundles of white noodle strands.
    add_fill(fills, "foodst noodle case base", (2033, 5, 3578), (2036, 5, 3586), M.WOOD)
    add_fill(fills, "foodst noodle case top", (2033, 6, 3578), (2036, 6, 3586), M.SPRUCE)
    add_fill(fills, "foodst noodle strands 1", (2034, 7, 3580), (2034, 7, 3582), M.WHITE_WOOL)
    add_fill(fills, "foodst noodle strands 2", (2035, 7, 3581), (2035, 7, 3583), M.WHITE_WOOL)
    add_fill(fills, "foodst noodle strands 3", (2034, 7, 3584), (2034, 7, 3586), M.WHITE_WOOL)
    # Big soup cauldron: stove, barrel pot, glowing broth, twin steam.
    add_fill(fills, "foodst noodle stove", (2039, 5, 3578), (2041, 5, 3580), M.STONE)
    add_fill(fills, "foodst noodle pot", (2039, 6, 3578), (2040, 6, 3579), BARREL)
    add_fill(fills, "foodst noodle broth", (2039, 7, 3578), (2040, 7, 3579), M.SEA_LANTERN)
    _steam(fills, "foodst noodle", 2039, 3578, 8, 11)
    # Shopkeeper figure in quartz behind the case.
    add_fill(fills, "foodst noodle keeper legs", (2035, 5, 3589), (2035, 5, 3589), M.QUARTZ)
    add_fill(fills, "foodst noodle keeper body", (2035, 6, 3589), (2035, 7, 3589), M.QUARTZ)
    add_fill(fills, "foodst noodle keeper head", (2035, 8, 3589), (2035, 8, 3589), M.QUARTZ)
    # Four diner stools by the front counter.
    _stool(fills, "foodst noodle stool 1", 2032, 3592)
    _stool(fills, "foodst noodle stool 2", 2032, 3596)
    _stool(fills, "foodst noodle stool 3", 2034, 3594)
    _stool(fills, "foodst noodle stool 4", 2036, 3597)

    # ------------------------------------------------------------------
    # 4. 蒸饼炉 steamer shop (east row, second stall).
    # ------------------------------------------------------------------
    _stall(fills, "foodst steamer", E_X1, ROW2_Z1, E_X2, ROW2_Z2, "w")
    # Brick steamer tower: stone hearth base, three fence-hoop + plank
    # tray tiers, lid, and venting steam.
    add_fill(fills, "foodst steamer base", (2037, 5, 3622), (2039, 5, 3624), M.STONE)
    add_fill(fills, "foodst steamer fire", (2038, 5, 3623), (2038, 5, 3623), M.SEA_LANTERN)
    add_fill(fills, "foodst steamer mouth", (2037, 5, 3625), (2039, 5, 3625), M.RED_WOOL)
    add_outline(fills, "foodst steamer hoop 1", 2037, 3622, 2039, 3624, 6, 6, M.FENCE)
    add_fill(fills, "foodst steamer tray 1", (2037, 7, 3622), (2039, 7, 3624), M.WOOD)
    add_outline(fills, "foodst steamer hoop 2", 2037, 3622, 2039, 3624, 8, 8, M.FENCE)
    add_fill(fills, "foodst steamer tray 2", (2037, 9, 3622), (2039, 9, 3624), M.WOOD)
    add_outline(fills, "foodst steamer hoop 3", 2037, 3622, 2039, 3624, 10, 10, M.FENCE)
    add_fill(fills, "foodst steamer lid", (2037, 11, 3622), (2039, 11, 3624), M.WOOD)
    _steam(fills, "foodst steamer", 2038, 3623, 12, 15)
    # Steamed-cake display rack: shelf with six white round cakes.
    add_fill(fills, "foodst steamer shelf", (2041, 6, 3629), (2043, 6, 3639), M.WOOD)
    for i, cz in enumerate((3629, 3631, 3633, 3635, 3637, 3639)):
        add_fill(fills, f"foodst steamer cake {i}", (2042, 7, cz), (2042, 7, cz), M.WHITE_WOOL)

    # ------------------------------------------------------------------
    # 5. 饮子铺 drink house (west row, first stall - centrepiece).
    # ------------------------------------------------------------------
    _stall(fills, "foodst drink", W_X1, ROW1_Z1, W_X2, ROW1_Z2, "e", plaque=False)
    # Timber counter in two segments leaving the middle entry open.
    add_fill(fills, "foodst drink counter n", (2015, 5, 3572), (2017, 5, 3580), M.WOOD)
    add_fill(fills, "foodst drink counter n top", (2015, 6, 3572), (2017, 6, 3580), M.SPRUCE)
    add_fill(fills, "foodst drink counter s", (2015, 5, 3590), (2017, 5, 3598), M.WOOD)
    add_fill(fills, "foodst drink counter s top", (2015, 6, 3590), (2017, 6, 3598), M.SPRUCE)
    # Lectern menu and three copper kettles on the counter.
    add_fill(fills, "foodst drink menu", (2016, 7, 3577), (2016, 7, 3577), LECTERN_E)
    add_fill(fills, "foodst drink kettle 1", (2016, 7, 3574), (2016, 7, 3574), BARREL)
    add_fill(fills, "foodst drink kettle 2", (2016, 7, 3579), (2016, 7, 3579), BARREL)
    add_fill(fills, "foodst drink kettle 3", (2016, 7, 3593), (2016, 7, 3593), BARREL)
    # Five named drink jars along the back wall, colour-coded liquids.
    _drink_jar(fills, "foodst drink jar plum", 2006, 3571, M.RED_WOOL)        # 酸梅汤
    _drink_jar(fills, "foodst drink jar apricot", 2006, 3577, M.YELLOW_WOOL)  # 杏酪
    _drink_jar(fills, "foodst drink jar mint", 2006, 3583, M.GREEN_WOOL)      # 薄荷饮
    _drink_jar(fills, "foodst drink jar peach", 2006, 3589, M.PINK_WOOL)      # 桃浆
    _drink_jar(fills, "foodst drink jar milk", 2006, 3595, M.WHITE_WOOL)      # 乳饮
    # Blue cloth awning slung out over the street on two poles.
    add_fill(fills, "foodst drink awning 1", (2019, 9, 3574), (2019, 9, 3596), M.BLUE_WOOL)
    add_fill(fills, "foodst drink awning 2", (2020, 8, 3574), (2020, 8, 3596), M.BLUE_WOOL)
    add_fill(fills, "foodst drink awning 3", (2021, 7, 3574), (2021, 7, 3596), M.BLUE_WOOL)
    add_fill(fills, "foodst drink awning 4", (2022, 6, 3574), (2022, 6, 3596), M.BLUE_WOOL)
    add_fill(fills, "foodst drink pole n", (2022, 5, 3574), (2022, 5, 3574), M.FENCE)
    add_fill(fills, "foodst drink pole s", (2022, 5, 3596), (2022, 5, 3596), M.FENCE)
    # Grand gilded "饮子" signboard with gold trim and two gold glyphs.
    add_fill(fills, "foodst drink sign board", (2019, 7, 3581), (2019, 11, 3589), M.DARK)
    add_fill(fills, "foodst drink sign trim top", (2019, 11, 3581), (2019, 11, 3589), M.GOLD)
    add_fill(fills, "foodst drink sign trim bottom", (2019, 7, 3581), (2019, 7, 3589), M.GOLD)
    add_fill(fills, "foodst drink glyph 1", (2019, 9, 3582), (2019, 9, 3583), M.GOLD)
    add_fill(fills, "foodst drink glyph 2", (2019, 9, 3587), (2019, 9, 3588), M.GOLD)

    # ------------------------------------------------------------------
    # 6. 烤肉架 charcoal grill shop (west row, second stall).
    # ------------------------------------------------------------------
    _stall(fills, "foodst grill", W_X1, ROW2_Z1, W_X2, ROW2_Z2, "e")
    # Charcoal pit: stone bed, red-wool coals, iron-bar grill rack.
    add_fill(fills, "foodst grill bed", (2009, 5, 3618), (2013, 5, 3626), M.STONE)
    add_fill(fills, "foodst grill coals", (2010, 5, 3619), (2012, 5, 3625), M.RED_WOOL)
    add_fill(fills, "foodst grill rack", (2009, 6, 3618), (2013, 6, 3626), M.IRON_BARS)
    # Four kebabs: log skewers with red / brown meat chunks.
    for i, cz in enumerate((3619, 3621, 3623, 3625)):
        add_fill(fills, f"foodst grill skewer {i}", (2009, 7, cz), (2013, 7, cz), LOG_X)
        add_fill(fills, f"foodst grill meat r {i}", (2010, 8, cz), (2010, 8, cz), M.RED_WOOL)
        add_fill(fills, f"foodst grill meat b {i}", (2012, 8, cz), (2012, 8, cz), BROWN_TERRACOTTA)
    # Stone chimney punching through the roof, with smoke.
    add_fill(fills, "foodst grill chimney", (2006, 5, 3638), (2007, 14, 3639), M.STONE)
    add_fill(fills, "foodst grill chimney cap", (2005, 15, 3637), (2008, 15, 3640), M.STONE)
    add_fill(fills, "foodst grill smoke", (2006, 16, 3638), (2007, 17, 3639), M.WHITE_TERRACOTTA)

    # ------------------------------------------------------------------
    # 7. 煎饼摊 pancake stall (west row, third stall).
    # ------------------------------------------------------------------
    _stall(fills, "foodst pancake", W_X1 + 4, ROW3_Z1, W_X2, ROW3_Z2, "e")
    add_fill(fills, "foodst pancake range", (2012, 5, 3658), (2015, 5, 3661), M.STONE)
    add_fill(fills, "foodst pancake griddle", (2012, 6, 3658), (2015, 6, 3661), M.SMOOTH)
    add_fill(fills, "foodst pancake stack", (2013, 7, 3659), (2014, 8, 3660), M.YELLOW_WOOL)
    add_fill(fills, "foodst pancake oil jar", (2016, 6, 3662), (2016, 7, 3662), BROWN_TERRACOTTA)
    _stool(fills, "foodst pancake stool 1", 2017, 3654)
    _stool(fills, "foodst pancake stool 2", 2017, 3668)

    # ------------------------------------------------------------------
    # 8. East third bay: street well with windlass (辘轳井).
    # ------------------------------------------------------------------
    add_outline(fills, "foodst well curb", 2037, 3663, 2041, 3667, 5, 5, M.STONE)
    add_fill(fills, "foodst well water", (2038, 5, 3664), (2040, 5, 3666), M.WATER)
    add_fill(fills, "foodst well post w", (2037, 6, 3665), (2037, 9, 3665), M.LOG)
    add_fill(fills, "foodst well post e", (2041, 6, 3665), (2041, 9, 3665), M.LOG)
    add_fill(fills, "foodst well bar", (2037, 9, 3665), (2041, 9, 3665), LOG_X)
    add_fill(fills, "foodst well crank", (2041, 10, 3665), (2041, 10, 3665), M.FENCE)
    add_fill(fills, "foodst well bucket", (2039, 7, 3665), (2039, 8, 3665), M.WOOD)
    add_fill(fills, "foodst well cap", (2036, 10, 3662), (2042, 10, 3668), DARK_SLAB)

    # ------------------------------------------------------------------
    # 9. Street-centre shed seating (食客棚座 x3).
    # ------------------------------------------------------------------
    for si, (sx, sz, cloth) in enumerate(SHEDS):
        _shed(fills, f"foodst shed {si}", sx, sz, cloth)

    # ------------------------------------------------------------------
    # 10. South paifang gate (街口牌坊): plinths, twin red columns,
    #     double crossbeams, gold "食" plaque, gable cap.
    # ------------------------------------------------------------------
    add_fill(fills, "foodst gate plinth w", (2018, 5, GATE_Z1 - 1), (2021, 5, GATE_Z2 + 1), M.SMOOTH)
    add_fill(fills, "foodst gate plinth e", (2028, 5, GATE_Z1 - 1), (2031, 5, GATE_Z2 + 1), M.SMOOTH)
    add_fill(fills, "foodst gate column w", (2019, 6, GATE_Z1), (2020, 12, GATE_Z2), M.RED_WALL)
    add_fill(fills, "foodst gate column e", (2029, 6, GATE_Z1), (2030, 12, GATE_Z2), M.RED_WALL)
    add_fill(fills, "foodst gate beam 1", (2017, 13, GATE_Z1), (2032, 13, GATE_Z2), LOG_X)
    add_fill(fills, "foodst gate beam 2", (2018, 14, GATE_Z1), (2031, 14, GATE_Z2), M.RED_WALL)
    add_fill(fills, "foodst gate plaque board", (2022, 10, GATE_Z1 + 1), (2027, 12, GATE_Z1 + 1), M.DARK)
    add_fill(fills, "foodst gate glyph 1", (2023, 11, GATE_Z1 + 1), (2024, 12, GATE_Z1 + 1), M.GOLD)
    add_fill(fills, "foodst gate glyph 2", (2025, 11, GATE_Z1 + 1), (2026, 12, GATE_Z1 + 1), M.GOLD)
    add_fill(fills, "foodst gate cap n", (2014, 15, 3782), (2035, 15, 3783), DARK_STAIR_S)
    add_fill(fills, "foodst gate cap s", (2014, 15, 3787), (2035, 15, 3788), DARK_STAIR_N)
    add_fill(fills, "foodst gate ridge", (2017, 16, GATE_Z1), (2032, 16, GATE_Z2), M.ROOF_DARK)
    # Gate flags on both flanks.
    add_fill(fills, "foodst gate pole w", (2016, 5, 3785), (2016, 9, 3785), M.FENCE)
    add_fill(fills, "foodst gate flag w", (2014, 6, 3785), (2015, 8, 3785), M.RED_WOOL)
    add_fill(fills, "foodst gate pole e", (2033, 5, 3785), (2033, 9, 3785), M.FENCE)
    add_fill(fills, "foodst gate flag e", (2034, 6, 3785), (2035, 8, 3785), M.YELLOW_WOOL)
    # Plaza lanterns.
    _lamp_post(fills, "foodst plaza lamp w", 2012, 3760)
    _lamp_post(fills, "foodst plaza lamp e", 2038, 3760)

    # ------------------------------------------------------------------
    # 11. Shop banners (幌子 x5), street lamps and lawn trees.
    # ------------------------------------------------------------------
    _banner(fills, "foodst banner noodle", 2027, ROW1_Z1 + 4, M.RED_WOOL, "e")
    _banner(fills, "foodst banner steamer", 2027, ROW2_Z1 + 4, M.GREEN_WOOL, "e")
    _banner(fills, "foodst banner drink", 2022, 3566, M.BLUE_WOOL, "w")
    _banner(fills, "foodst banner grill", 2022, ROW2_Z1 + 4, M.YELLOW_WOOL, "w")
    _banner(fills, "foodst banner pancake", 2022, ROW3_Z1 + 4, M.PINK_WOOL, "w")
    _lamp_post(fills, "foodst street lamp 1", STREET_X1, 3648)
    _lamp_post(fills, "foodst street lamp 2", STREET_X2, 3672)
    _lamp_post(fills, "foodst street lamp 3", STREET_X1, 3745)
    _lamp_post(fills, "foodst street lamp 4", STREET_X2, 3755)
    add_tree(fills, "foodst tree w1", 1990, 3600, 4, height=7, spread=2)
    add_tree(fills, "foodst tree w2", 1990, 3720, 4, height=7, spread=2)
    add_tree(fills, "foodst tree e1", 2060, 3600, 4, height=7, spread=2)
    add_tree(fills, "foodst tree e2", 2060, 3720, 4, height=7, spread=2)
    add_tree(fills, "foodst tree gate w", 2006, 3760, 4, height=7, spread=2)
    add_tree(fills, "foodst tree gate e", 2044, 3760, 4, height=7, spread=2)


def main() -> None:
    run_builder(build_food_street_3d, "food_street_3d")


if __name__ == "__main__":
    main()
