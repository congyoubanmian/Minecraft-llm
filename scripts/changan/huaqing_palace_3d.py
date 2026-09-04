from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    BASE_X,
    BASE_Z,
    Fill,
    Materials as M,
    add_fill,
    add_hip_roof,
    add_hollow_box,
    add_outline,
    add_pool,
    add_pyramid_roof,
    add_ridge_roof,
    run_builder,
)


"""
Huaqing Palace 3D (华清宫·骊山温泉) - the winter palace and hot-spring
resort of Tang Xuanzong and Consort Yang at the foot of Mt. Li, home of
the legendary Crabapple Pool (春寒赐浴华清池，温泉水滑洗凝脂).

Location in Chang'an city local coordinates:
    parcel: x 1100..1750, z -1500..-1050 (southern-suburb foothills).
    Nine-Dragon Lake (九龙湖): x 1250..1600, z -1350..-1150, water y=1.
    Feishuang Hall (飞霜殿): x 1200..1420, z -1500..-1430 on a high terrace.
    Hot spring eye (温泉泉眼): around (1550, -1450) at the mountain foot.

Distinctive features:
    - Nine-Dragon Lake crossed by a nine-segment zigzag bridge (九段折桥)
      with gilded dragon bollards, leading to the Sunset Pavilion
      (晚霞亭), a pyramid-roofed pavilion on piles standing in the lake
    - Crabapple Pool (海棠汤·贵妃池): flower-shaped bath - a central round
      pool plus four petal pools with pink rims, quartz bottoms and
      flush sunken water, ringed by a quartz balustrade
    - Lotus Pool (莲花汤·御汤): two-tier eight-petal imperial stone
      platform with a gilded-rim central water basin
    - Stone-trough hot-spring aqueduct running from the spring eye
      (bubbling over sea lanterns) to both baths and the lake, ending in
      a spillway stair with white-glass steam
    - Double-eave Feishuang Hall on a two-tier terrace with twin stairs
      (月台双阶), two double-eave side halls, white palace walls with a
      south gate tower, a bathhouse changing room, plum trees and lamps
"""

STEAM = "minecraft:white_stained_glass"

# ---------------------------------------------------------------------------
# Site bounds (hard constraint: every fill must stay inside this parcel).
# ---------------------------------------------------------------------------
SITE_X1, SITE_X2 = 1100, 1750
SITE_Z1, SITE_Z2 = -1500, -1050

# Nine-Dragon Lake in front of the palace.
LAKE_X1, LAKE_Z1, LAKE_X2, LAKE_Z2 = 1250, -1350, 1600, -1150
LAKE_WATER_Y = 1

# Sunset Pavilion at the heart of the lake.
PAV_CX, PAV_CZ = 1425, -1250

# Hot-spring bath plaza south of the lake.
PLAZA_X1, PLAZA_Z1, PLAZA_X2, PLAZA_Z2 = 1255, -1145, 1505, -1085
LOTUS_CX, LOTUS_CZ = 1300, -1105  # Lotus Pool (御汤)
CRAB_CX, CRAB_CZ = 1400, -1105    # Crabapple Pool (贵妃池)

# Hot spring eye behind the palace at the mountain foot.
SPRING_CX, SPRING_CZ = 1550, -1450

# Feishuang Hall (main hall).
HALL_X1, HALL_Z1, HALL_X2, HALL_Z2 = 1200, -1500, 1420, -1430

# Palace enclosure wall.
WALL_X1, WALL_Z1, WALL_X2, WALL_Z2 = 1150, -1500, 1700, -1075


def _oval_rows(cx: int, cz: int, rx: int, rz: int) -> list[tuple[int, int, int]]:
    """Rows of an oval: (x1, x2, z) per z-slice, zero-width rows become 1 cell."""
    rows: list[tuple[int, int, int]] = []
    for dz in range(-rz, rz + 1):
        half = int(rx * math.sqrt(max(0.0, 1.0 - (dz / rz) ** 2))) if rz else rx
        rows.append((cx - half, cx + half, cz + dz))
    return rows


def _disc(
    fills: list[Fill],
    label: str,
    cx: int, cz: int, r: int,
    y1: int, y2: int,
    block: str,
) -> None:
    """Fill a disc of radius r (one fill per row)."""
    for i, (x1, x2, z) in enumerate(_oval_rows(cx, cz, r, r)):
        add_fill(fills, f"{label} row {i}", (x1, y1, z), (x2, y2, z), block)


def _lamp(fills: list[Fill], x: int, z: int, y: int = 4) -> None:
    """Slim lantern post: log pole with a lantern on top."""
    add_fill(fills, f"huaqing lamp post {x},{z}", (x, y, z), (x, y + 4, z), M.LOG)
    add_fill(fills, f"huaqing lamp head {x},{z}", (x, y + 5, z), (x, y + 5, z), M.LANTERN)


def _plum_tree(fills: list[Fill], x: int, z: int, y: int = 4) -> None:
    """Winter plum tree: dark trunk with a pink wool blossom crown."""
    add_fill(fills, f"huaqing plum trunk {x},{z}", (x, y, z), (x, y + 3, z), M.LOG)
    add_fill(fills, f"huaqing plum bloom {x},{z}", (x - 2, y + 2, z - 2), (x + 2, y + 5, z + 2), M.PINK_WOOL)


def _trough_x(
    fills: list[Fill], tag: str,
    x1: int, x2: int, z1: int, z2: int,
) -> None:
    """East-west stone aqueduct trough: bed, side curbs and spring water."""
    add_fill(fills, f"huaqing aqueduct {tag} bed", (x1, 2, z1), (x2, 2, z2), M.STONE)
    add_fill(fills, f"huaqing aqueduct {tag} curb n", (x1, 3, z1 - 1), (x2, 3, z1 - 1), M.STONE)
    add_fill(fills, f"huaqing aqueduct {tag} curb s", (x1, 3, z2 + 1), (x2, 3, z2 + 1), M.STONE)
    add_fill(fills, f"huaqing aqueduct {tag} water", (x1, 3, z1), (x2, 3, z2), M.WATER)


def _trough_z(
    fills: list[Fill], tag: str,
    x1: int, x2: int, z1: int, z2: int,
) -> None:
    """North-south stone aqueduct trough: bed, side curbs and spring water."""
    add_fill(fills, f"huaqing aqueduct {tag} bed", (x1, 2, z1), (x2, 2, z2), M.STONE)
    add_fill(fills, f"huaqing aqueduct {tag} curb w", (x1 - 1, 3, z1), (x1 - 1, 3, z2), M.STONE)
    add_fill(fills, f"huaqing aqueduct {tag} curb e", (x2 + 1, 3, z1), (x2 + 1, 3, z2), M.STONE)
    add_fill(fills, f"huaqing aqueduct {tag} water", (x1, 3, z1), (x2, 3, z2), M.WATER)


def build_huaqing_palace_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site preparation: stone base y0..1 plus grass cover y2..3.
    # ------------------------------------------------------------------
    add_fill(fills, "huaqing site stone base", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "huaqing site grass cover", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)

    # ------------------------------------------------------------------
    # 2. Nine-Dragon Lake (九龙湖): water surface y1, smooth stone bed.
    # ------------------------------------------------------------------
    add_fill(fills, "huaqing lake clear", (LAKE_X1, 2, LAKE_Z1), (LAKE_X2, 3, LAKE_Z2), M.AIR)
    add_pool(fills, "huaqing lake", LAKE_X1, LAKE_Z1, LAKE_X2, LAKE_Z2, LAKE_WATER_Y, depth=2, floor_block=M.SMOOTH)
    add_outline(fills, "huaqing lake embankment", LAKE_X1, LAKE_Z1, LAKE_X2, LAKE_Z2, 2, 3, M.STONE, thickness=2)

    # ------------------------------------------------------------------
    # 3. Nine-dragon zigzag bridge (九段折桥) from the south shore to the
    #    pavilion, with gilded dragon bollards at every bend.
    # ------------------------------------------------------------------
    legs = [
        (1424, -1165, 1426, -1146),
        (1412, -1166, 1425, -1164),
        (1412, -1184, 1414, -1165),
        (1412, -1185, 1426, -1183),
        (1424, -1203, 1426, -1184),
        (1412, -1204, 1426, -1202),
        (1412, -1222, 1414, -1203),
        (1412, -1223, 1426, -1221),
        (1424, -1243, 1426, -1222),
    ]
    for i, (x1, z1, x2, z2) in enumerate(legs):
        add_fill(fills, f"huaqing dragon bridge seg {i} deck", (x1, 3, z1), (x2, 3, z2), M.WOOD)
        if x2 - x1 < z2 - z1:  # north-south segment
            add_fill(fills, f"huaqing dragon bridge seg {i} rail w", (x1 - 1, 4, z1), (x1 - 1, 4, z2), M.FENCE)
            add_fill(fills, f"huaqing dragon bridge seg {i} rail e", (x2 + 1, 4, z1), (x2 + 1, 4, z2), M.FENCE)
            add_fill(fills, f"huaqing dragon bridge seg {i} pile", (x1, 0, (z1 + z2) // 2), (x2, 2, (z1 + z2) // 2), M.LOG)
        else:  # east-west segment
            add_fill(fills, f"huaqing dragon bridge seg {i} rail n", (x1, 4, z1 - 1), (x2, 4, z1 - 1), M.FENCE)
            add_fill(fills, f"huaqing dragon bridge seg {i} rail s", (x1, 4, z2 + 1), (x2, 4, z2 + 1), M.FENCE)
            add_fill(fills, f"huaqing dragon bridge seg {i} pile", ((x1 + x2) // 2, 0, z1), ((x1 + x2) // 2, 2, z2), M.LOG)
    for j, (bx, bz) in enumerate([
        (1425, -1165), (1413, -1165), (1413, -1184), (1425, -1184),
        (1425, -1203), (1413, -1203), (1413, -1222), (1425, -1222),
        (1425, -1243),
    ]):
        add_fill(fills, f"huaqing dragon bollard {j}", (bx, 4, bz), (bx, 5, bz), M.GOLD)
    add_fill(fills, "huaqing bridge landing", (1408, 3, -1149), (1442, 3, -1146), M.STONE)

    # ------------------------------------------------------------------
    # 4. Sunset Pavilion (晚霞亭) on piles at the heart of the lake.
    # ------------------------------------------------------------------
    add_fill(fills, "huaqing pavilion platform", (PAV_CX - 6, 2, PAV_CZ - 6), (PAV_CX + 6, 3, PAV_CZ + 6), M.STONE)
    for px in (PAV_CX - 6, PAV_CX + 4):
        for pz in (PAV_CZ - 6, PAV_CZ + 4):
            add_fill(fills, f"huaqing pavilion pile {px},{pz}", (px, 0, pz), (px + 1, 1, pz + 1), M.STONE)
    add_fill(fills, "huaqing pavilion rail n", (PAV_CX - 6, 4, PAV_CZ - 6), (PAV_CX + 6, 4, PAV_CZ - 6), M.FENCE)
    add_fill(fills, "huaqing pavilion rail w", (PAV_CX - 6, 4, PAV_CZ - 5), (PAV_CX - 6, 4, PAV_CZ + 5), M.FENCE)
    add_fill(fills, "huaqing pavilion rail e", (PAV_CX + 6, 4, PAV_CZ - 5), (PAV_CX + 6, 4, PAV_CZ + 5), M.FENCE)
    for px in (PAV_CX - 5, PAV_CX + 3):
        for pz in (PAV_CZ - 5, PAV_CZ + 3):
            add_fill(fills, f"huaqing pavilion column {px},{pz}", (px, 4, pz), (px + 1, 10, pz + 1), M.RED_WALL)
    add_fill(fills, "huaqing pavilion floor motif", (PAV_CX - 1, 3, PAV_CZ - 1), (PAV_CX + 1, 3, PAV_CZ + 1), M.GOLD)
    add_pyramid_roof(fills, "huaqing pavilion roof", PAV_CX, PAV_CZ, radius=8, y=11, roof_block=M.ROOF_BLUE, apex_block=M.GOLD)

    # ------------------------------------------------------------------
    # 5. Hot-spring bath plaza (汤殿区) south of the lake, flush stone deck.
    # ------------------------------------------------------------------
    add_fill(fills, "huaqing bath plaza", (PLAZA_X1, 3, PLAZA_Z1), (PLAZA_X2, 3, PLAZA_Z2), M.STONE)

    # ------------------------------------------------------------------
    # 6. Lotus Pool (莲花汤·御汤): two-tier eight-petal imperial platform.
    # ------------------------------------------------------------------
    lx, lz = LOTUS_CX, LOTUS_CZ
    add_fill(fills, "huaqing lotus tier1", (lx - 14, 4, lz - 14), (lx + 14, 5, lz + 14), M.STONE)
    for tag, (x1, z1, x2, z2) in {
        "n": (lx - 3, lz - 19, lx + 3, lz - 15),
        "s": (lx - 3, lz + 15, lx + 3, lz + 19),
        "w": (lx - 19, lz - 3, lx - 15, lz + 3),
        "e": (lx + 15, lz - 3, lx + 19, lz + 3),
    }.items():
        add_fill(fills, f"huaqing lotus tier1 petal {tag}", (x1, 4, z1), (x2, 5, z2), M.QUARTZ)
    for tag, (x1, z1, x2, z2) in {
        "nw": (lx - 19, lz - 18, lx - 15, lz - 14),
        "ne": (lx + 15, lz - 18, lx + 19, lz - 14),
        "sw": (lx - 19, lz + 14, lx - 15, lz + 18),
        "se": (lx + 15, lz + 14, lx + 19, lz + 18),
    }.items():
        add_fill(fills, f"huaqing lotus tier1 corner {tag}", (x1, 4, z1), (x2, 5, z2), M.QUARTZ)
    for tag, (x1, z1, x2, z2) in {
        "n": (lx - 2, lz - 20, lx + 2, lz - 20),
        "s": (lx - 2, lz + 20, lx + 2, lz + 20),
        "w": (lx - 20, lz - 1, lx - 20, lz + 1),
        "e": (lx + 20, lz - 1, lx + 20, lz + 1),
    }.items():
        add_fill(fills, f"huaqing lotus petal tip {tag}", (x1, 4, z1), (x2, 5, z2), M.PINK_WOOL)
    add_fill(fills, "huaqing lotus tier2", (lx - 8, 6, lz - 8), (lx + 8, 7, lz + 8), M.QUARTZ)
    for tag, (x1, z1, x2, z2) in {
        "n": (lx - 3, lz - 13, lx + 3, lz - 9),
        "s": (lx - 3, lz + 9, lx + 3, lz + 13),
        "w": (lx - 13, lz - 3, lx - 9, lz + 3),
        "e": (lx + 9, lz - 3, lx + 13, lz + 3),
    }.items():
        add_fill(fills, f"huaqing lotus tier2 petal {tag}", (x1, 6, z1), (x2, 7, z2), M.QUARTZ)
    add_fill(fills, "huaqing lotus basin floor", (lx - 4, 7, lz - 4), (lx + 4, 7, lz + 4), M.QUARTZ)
    add_fill(fills, "huaqing lotus basin water", (lx - 4, 8, lz - 4), (lx + 4, 8, lz + 4), M.WATER)
    add_outline(fills, "huaqing lotus basin rim", lx - 5, lz - 5, lx + 5, lz + 5, 8, 9, M.GOLD, thickness=1)

    # ------------------------------------------------------------------
    # 7. Crabapple Pool (海棠汤·贵妃池): central round pool plus four
    #    petal pools, pink rims, quartz bottoms, sunken spring water.
    # ------------------------------------------------------------------
    gx, gz = CRAB_CX, CRAB_CZ
    add_fill(fills, "huaqing crab quartz bed", (gx - 13, 1, gz - 13), (gx + 13, 2, gz + 13), M.QUARTZ)
    add_fill(fills, "huaqing crab deep bottom", (gx - 5, 1, gz - 5), (gx + 5, 1, gz + 5), M.QUARTZ)
    _disc(fills, "huaqing crab centre water", gx, gz, 5, 2, 3, M.WATER)
    _disc(fills, "huaqing crab centre rim", gx, gz, 5, 4, 4, M.PINK_WOOL)
    _disc(fills, "huaqing crab centre rim hollow", gx, gz, 4, 4, 4, M.AIR)
    petals = {
        "e": (
            [(gx + 9, gz - 1, gx + 9, gz - 1), (gx + 5, gz, gx + 13, gz), (gx + 9, gz + 1, gx + 9, gz + 1)],
            [(gx + 14, gz, gx + 14, gz), (gx + 10, gz - 1, gx + 13, gz - 1), (gx + 10, gz + 1, gx + 13, gz + 1)],
        ),
        "w": (
            [(gx - 9, gz - 1, gx - 9, gz - 1), (gx - 13, gz, gx - 5, gz), (gx - 9, gz + 1, gx - 9, gz + 1)],
            [(gx - 14, gz, gx - 14, gz), (gx - 13, gz - 1, gx - 10, gz - 1), (gx - 13, gz + 1, gx - 10, gz + 1)],
        ),
        "n": (
            [(gx - 1, gz - 13, gx + 1, gz - 13), (gx - 1, gz - 12, gx + 1, gz - 6), (gx - 4, gz - 5, gx + 4, gz - 5)],
            [(gx - 2, gz - 14, gx + 2, gz - 14), (gx - 2, gz - 12, gx - 2, gz - 7), (gx + 2, gz - 12, gx + 2, gz - 7)],
        ),
        "s": (
            [(gx - 1, gz + 13, gx + 1, gz + 13), (gx - 1, gz + 6, gx + 1, gz + 12), (gx - 4, gz + 5, gx + 4, gz + 5)],
            [(gx - 2, gz + 14, gx + 2, gz + 14), (gx - 2, gz + 7, gx - 2, gz + 12), (gx + 2, gz + 7, gx + 2, gz + 12)],
        ),
    }
    for name, (waters, rims) in petals.items():
        for k, (x1, z1, x2, z2) in enumerate(waters):
            add_fill(fills, f"huaqing crab petal {name} water {k}", (x1, 3, z1), (x2, 3, z2), M.WATER)
        for k, (x1, z1, x2, z2) in enumerate(rims):
            add_fill(fills, f"huaqing crab petal {name} rim {k}", (x1, 4, z1), (x2, 4, z2), M.PINK_WOOL)
    # Stone balustrade around the consort's bath, with a channel inlet north.
    add_fill(fills, "huaqing crab rail n", (gx - 20, 4, gz - 15), (gx + 20, 5, gz - 15), M.QUARTZ)
    add_fill(fills, "huaqing crab rail w", (gx - 20, 4, gz - 14), (gx - 20, 5, gz + 14), M.QUARTZ)
    add_fill(fills, "huaqing crab rail e", (gx + 20, 4, gz - 14), (gx + 20, 5, gz + 14), M.QUARTZ)
    add_fill(fills, "huaqing crab rail sw", (gx - 20, 4, gz + 15), (gx - 8, 5, gz + 15), M.QUARTZ)
    add_fill(fills, "huaqing crab rail se", (gx + 8, 4, gz + 15), (gx + 20, 5, gz + 15), M.QUARTZ)
    add_fill(fills, "huaqing crab rail inlet", (gx - 1, 4, gz - 15), (gx + 1, 5, gz - 15), M.AIR)

    # ------------------------------------------------------------------
    # 8. Changing room (更衣室) beside the Crabapple Pool.
    # ------------------------------------------------------------------
    add_hollow_box(fills, "huaqing dressing walls", 1440, 4, -1120, 1476, 9, -1092, M.WHITE_TERRACOTTA, thickness=1)
    add_fill(fills, "huaqing dressing floor", (1441, 4, -1119), (1475, 4, -1093), M.SMOOTH)
    add_fill(fills, "huaqing dressing door", (1440, 5, -1109), (1441, 8, -1103), M.AIR)
    add_fill(fills, "huaqing dressing window n", (1450, 6, -1120), (1457, 8, -1120), M.GLASS)
    add_ridge_roof(fills, "huaqing dressing roof", 1436, -1124, 1480, -1088, 10, layers=2, ridge_axis="x")

    # ------------------------------------------------------------------
    # 9. Hot spring eye (温泉泉眼) at the mountain foot, bubbling over
    #    sea lanterns with white-glass mist, sheltered by a timber canopy.
    # ------------------------------------------------------------------
    sx, sz = SPRING_CX, SPRING_CZ
    add_fill(fills, "huaqing spring apron", (sx - 12, 3, sz - 12), (sx + 12, 3, sz + 12), M.STONE)
    add_fill(fills, "huaqing spring water", (sx - 6, 2, sz - 6), (sx + 6, 3, sz + 6), M.WATER)
    add_fill(fills, "huaqing spring glow", (sx - 2, 1, sz - 2), (sx + 2, 1, sz + 2), M.SEA_LANTERN)
    add_outline(fills, "huaqing spring rim", sx - 7, sz - 7, sx + 7, sz + 7, 4, 5, M.STONE, thickness=1)
    add_fill(fills, "huaqing spring spout", (sx - 1, 4, sz - 2), (sx + 1, 5, sz), M.WATER)
    add_fill(fills, "huaqing spring steam", (sx - 6, 5, sz - 5), (sx - 2, 7, sz), STEAM)
    for px in (sx - 7, sx + 7):
        for pz in (sz - 7, sz + 7):
            add_fill(fills, f"huaqing spring post {px},{pz}", (px, 6, pz), (px, 8, pz), M.LOG)
    add_fill(fills, "huaqing spring canopy", (sx - 9, 9, sz - 9), (sx + 9, 9, sz + 9), M.WOOD)

    # ------------------------------------------------------------------
    # 10. Hot-spring aqueduct (温泉暗渠): stone troughs feeding both baths
    #     and the lake, ending in a spillway with white-glass steam.
    # ------------------------------------------------------------------
    _trough_z(fills, "spring run", sx - 2, sx, sz + 7, -1360)
    _trough_x(fills, "east run", 1451, sx + 2, -1362, -1360)
    _trough_z(fills, "south run", 1610, 1612, -1360, -1137)
    _trough_x(fills, "plaza run", 1266, 1611, -1137, -1135)
    # Spill into the north-east corner of the Nine-Dragon Lake.
    add_fill(fills, "huaqing aqueduct lake gap", (1444, 2, -1350), (1448, 3, -1349), M.AIR)
    _trough_z(fills, "lake spill", 1445, 1447, -1360, -1351)
    add_fill(fills, "huaqing aqueduct lake cascade", (1445, 1, -1352), (1447, 2, -1349), M.WATER)
    # Feed stub into the Lotus Pool (runs beneath the overhanging petal).
    add_fill(fills, "huaqing aqueduct lotus curb w", (1298, 3, -1134), (1298, 3, -1121), M.STONE)
    add_fill(fills, "huaqing aqueduct lotus curb e", (1302, 3, -1134), (1302, 3, -1121), M.STONE)
    add_fill(fills, "huaqing aqueduct lotus water", (1299, 3, -1134), (1301, 3, -1120), M.WATER)
    # Feed stub into the Crabapple Pool, through the balustrade inlet.
    add_fill(fills, "huaqing aqueduct crab curb w", (1398, 3, -1134), (1398, 3, -1118), M.STONE)
    add_fill(fills, "huaqing aqueduct crab curb e", (1402, 3, -1134), (1402, 3, -1118), M.STONE)
    add_fill(fills, "huaqing aqueduct crab water", (1399, 3, -1134), (1401, 3, -1118), M.WATER)
    # Channel tail: spillway basin, stone steps and white-glass steam.
    add_fill(fills, "huaqing spillway basin bed", (1256, 1, -1141), (1264, 2, -1132), M.QUARTZ)
    add_fill(fills, "huaqing spillway basin water", (1257, 2, -1140), (1263, 3, -1132), M.WATER)
    add_outline(fills, "huaqing spillway basin rim", 1255, -1142, 1265, -1130, 4, 4, M.STONE, thickness=1)
    add_fill(fills, "huaqing spillway link water", (1264, 3, -1137), (1266, 3, -1135), M.WATER)
    add_fill(fills, "huaqing spillway steam", (1259, 4, -1139), (1262, 6, -1134), STEAM)

    # ------------------------------------------------------------------
    # 11. Feishuang Hall (飞霜殿): high two-tier terrace, double-eave
    #     hip-roofed hall, moon terrace with twin stairs (月台双阶).
    # ------------------------------------------------------------------
    add_fill(fills, "huaqing hall terrace t1", (1180, 4, -1500), (1440, 6, -1378), M.STONE)
    add_fill(fills, "huaqing hall terrace t2", (1195, 7, -1495), (1425, 9, -1405), M.STONE)
    add_outline(fills, "huaqing hall terrace rail t1", 1180, -1500, 1440, -1378, 7, 7, M.QUARTZ, thickness=1)
    add_outline(fills, "huaqing hall terrace rail t2", 1195, -1495, 1425, -1405, 10, 10, M.QUARTZ, thickness=1)
    for fx1, fx2 in ((1272, 1288), (1332, 1348)):  # twin staircases
        for k in range(3):
            add_fill(fills, f"huaqing hall stair t2 {fx1} {k}", (fx1, 7, -1404 + 4 * k), (fx2, 9 - k, -1401 + 4 * k), M.SMOOTH)
        for k in range(3):
            add_fill(fills, f"huaqing hall stair t1 {fx1} {k}", (fx1, 4, -1392 + 4 * k), (fx2, 6 - k, -1389 + 4 * k), M.SMOOTH)
        add_fill(fills, f"huaqing hall stair base {fx1}", (fx1, 4, -1380), (fx2, 5, -1377), M.SMOOTH)
    add_hollow_box(fills, "huaqing hall lower walls", HALL_X1, 10, HALL_Z1, HALL_X2, 22, HALL_Z2, M.RED_WALL, thickness=2)
    add_fill(fills, "huaqing hall floor", (HALL_X1 + 1, 10, HALL_Z1 + 1), (HALL_X2 - 1, 10, HALL_Z2 - 1), M.SMOOTH)
    add_fill(fills, "huaqing hall door s", (1300, 10, -1430), (1320, 16, -1429), M.AIR)
    add_fill(fills, "huaqing hall door n", (1300, 10, -1500), (1320, 16, -1499), M.AIR)
    for tag, (x1, z1, x2, z2) in {
        "s1": (1225, -1430, 1231, -1429),
        "s2": (1255, -1430, 1261, -1429),
        "s3": (1359, -1430, 1365, -1429),
        "s4": (1389, -1430, 1395, -1429),
        "e": (1419, -1480, 1420, -1466),
        "w": (1200, -1480, 1201, -1466),
    }.items():
        add_fill(fills, f"huaqing hall window {tag}", (x1, 14, z1), (x2, 18, z2), M.GLASS)
    for cx in (1220, 1270, 1350, 1400):
        for cz in (-1490, -1460):
            add_fill(fills, f"huaqing hall column {cx},{cz}", (cx, 11, cz), (cx + 1, 21, cz + 1), M.LOG)
    add_fill(fills, "huaqing hall dais", (1290, 11, -1470), (1330, 12, -1452), M.QUARTZ)
    add_fill(fills, "huaqing hall throne", (1305, 13, -1466), (1315, 14, -1456), M.GOLD)
    # Lower eave ring of the double eave (重檐下檐).
    add_outline(fills, "huaqing hall lower eave", 1196, -1500, 1424, -1426, 23, 24, M.ROOF_GREEN, thickness=3)
    # Upper storey and hip roof (庑殿顶).
    add_hollow_box(fills, "huaqing hall upper walls", 1210, 25, -1494, 1410, 32, -1436, M.RED_WALL, thickness=1)
    add_fill(fills, "huaqing hall upper floor", (1211, 25, -1493), (1409, 25, -1437), M.WOOD)
    add_fill(fills, "huaqing hall upper window w", (1240, 27, -1436), (1252, 30, -1436), M.GLASS)
    add_fill(fills, "huaqing hall upper window e", (1368, 27, -1436), (1380, 30, -1436), M.GLASS)
    add_hip_roof(fills, "huaqing hall hip roof", 1206, -1494, 1414, -1436, 33, layers=6, ridge_axis="x", roof_block=M.ROOF_GREEN)

    # ------------------------------------------------------------------
    # 12. East / West side halls (东西配殿), each double-eaved, flanking
    #     the lake.
    # ------------------------------------------------------------------
    for side, px1, px2 in (("west", 1156, 1244), ("east", 1616, 1698)):
        pz1, pz2 = -1314, -1246
        mx1, mx2 = px1 + 10, px2 - 10
        add_fill(fills, f"huaqing {side} hall platform", (px1, 4, pz1), (px2, 5, pz2), M.STONE)
        add_hollow_box(fills, f"huaqing {side} hall walls", mx1, 6, pz1 + 4, mx2, 14, pz2 - 4, M.RED_WALL, thickness=2)
        add_fill(fills, f"huaqing {side} hall floor", (mx1 + 1, 6, pz1 + 5), (mx2 - 1, 6, pz2 - 5), M.SMOOTH)
        if side == "west":  # door pierces the lake-facing wall leaf
            dx1, dx2 = mx2 - 1, mx2
        else:
            dx1, dx2 = mx1, mx1 + 1
        add_fill(fills, f"huaqing {side} hall door", (dx1, 7, -1286), (dx2, 12, -1274), M.AIR)
        add_fill(fills, f"huaqing {side} hall window", (mx1, 9, -1302), (mx1 + 1, 12, -1290), M.GLASS)
        add_outline(fills, f"huaqing {side} hall lower eave", px1 + 4, pz1, px2 - 4, pz2, 15, 16, M.ROOF_GREEN, thickness=3)
        add_hollow_box(fills, f"huaqing {side} hall upper walls", mx1 + 10, 17, pz1 + 14, mx2 - 10, 22, pz2 - 14, M.RED_WALL, thickness=2)
        add_hip_roof(fills, f"huaqing {side} hall roof", mx1 + 4, pz1 + 8, mx2 - 4, pz2 - 8, 23, layers=3, ridge_axis="x", roof_block=M.ROOF_GREEN)

    # ------------------------------------------------------------------
    # 13. Palace walls (宫墙) with crenellation and the south gate tower.
    # ------------------------------------------------------------------
    add_outline(fills, "huaqing palace wall", WALL_X1, WALL_Z1, WALL_X2, WALL_Z2, 4, 10, M.WHITE_TERRACOTTA, thickness=2)
    add_hollow_box(fills, "huaqing gate tower", 1396, 4, -1082, 1454, 14, -1052, M.WHITE_TERRACOTTA, thickness=2)
    add_fill(fills, "huaqing gate tower floor", (1398, 4, -1080), (1452, 5, -1054), M.STONE)
    add_fill(fills, "huaqing gate passage", (1415, 5, -1082), (1435, 11, -1052), M.AIR)
    add_outline(fills, "huaqing gate lower eave", 1392, -1086, 1458, -1052, 15, 16, M.ROOF_GREEN, thickness=3)
    add_hollow_box(fills, "huaqing gate upper chamber", 1406, 17, -1078, 1444, 23, -1056, M.RED_WALL, thickness=1)
    add_ridge_roof(fills, "huaqing gate roof", 1402, -1082, 1448, -1056, 24, layers=2, ridge_axis="x")
    add_fill(fills, "huaqing gate path", (1414, 3, -1086), (1436, 3, -1052), M.SMOOTH)

    # ------------------------------------------------------------------
    # 14. Court dressing: axial path, plum trees and perimeter lamps.
    # ------------------------------------------------------------------
    add_fill(fills, "huaqing hall lake path", (1280, 3, -1400), (1350, 3, -1352), M.SMOOTH)
    for tx, tz in ((1162, -1420), (1162, -1200), (1660, -1420), (1660, -1200), (1230, -1082), (1560, -1485)):
        _plum_tree(fills, tx, tz)
    for lxp, lzp in ((1247, -1300), (1247, -1220), (1605, -1300), (1605, -1220), (1350, -1148), (1480, -1148)):
        _lamp(fills, lxp, lzp)


def main() -> None:
    fills: list[Fill] = []
    build_huaqing_palace_3d(fills)
    for f in fills:
        xs = sorted((f.x1, f.x2))
        zs = sorted((f.z1, f.z2))
        if xs[0] < BASE_X + SITE_X1 or xs[1] > BASE_X + SITE_X2:
            raise SystemExit(f"fill out of x bounds: {f}")
        if zs[0] < BASE_Z + SITE_Z1 or zs[1] > BASE_Z + SITE_Z2:
            raise SystemExit(f"fill out of z bounds: {f}")
    run_builder(build_huaqing_palace_3d, "huaqing_palace_3d")


if __name__ == "__main__":
    main()
