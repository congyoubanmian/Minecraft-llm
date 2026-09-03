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
    add_hip_roof,
    add_outline,
    add_staircase,
    add_underground_room,
    run_builder,
)


"""
West Market flag pavilion + Sogdian tavern (西市旗亭 + 胡商酒肆) 3D module.

Built in the West Market center; this pass deliberately overwrites the
existing market stalls at its footprint.

Location in Chang'an city local coordinates:
    旗亭 Market Office Tower: center (1250, 2550), footprint 24x24
    胡商酒肆 Sogdian tavern:  center (1330, 2480), radius ~14

3D features:
    - 旗亭: square 3-storey tower (each storey 9 high, slightly inset),
      red walls + dark-oak edge columns, open arched market-office front
      with counter and document chests, interior straight staircases,
      庑殿顶 hip roof, roof-top flag poles with wool banners, and the
      market opening/closing drum on the second-floor balcony.
    - 胡商酒肆: circular white-terracotta drum wall (scanline ring), a
      true dome roof (stacked scanline sphere shell) with a gold oculus,
      arched doorways on four sides, circular spruce bar counter, wine
      jars, hanging lanterns, an underground wine cellar with a descending
      staircase, and a front courtyard with a Persian carpet plus two
      camel-caravan cargo piles.
"""

# 旗亭 Market Office Tower
TOWER_X1, TOWER_Z1 = 1238, 2538
TOWER_X2, TOWER_Z2 = 1261, 2561
TOWER_BASE_Y = 3          # ground-floor wall base; stone platform top is y=2
STOREY_PITCH = 9          # 8-high wall band + 1 floor layer per storey

# 胡商酒肆 Sogdian tavern
TAV_CX, TAV_CZ = 1330, 2480
TAV_R = 14
TAV_WALL_Y1, TAV_WALL_Y2 = 2, 9
TAV_DOME_Y = 10

BROWN_TERRACOTTA = "minecraft:brown_terracotta"
CHEST = "minecraft:chest"
LOG_X = "minecraft:dark_oak_log[axis=x]"
LOG_Z = "minecraft:dark_oak_log[axis=z]"


def _disk(fills: list[Fill], label: str, cx: int, cz: int, r: int, y1: int, y2: int, block: str, step: int = 2) -> None:
    """Approximate a filled circle with horizontal scanline rows."""
    for dz in range(-r, r + 1, step):
        half = int((r * r - dz * dz) ** 0.5)
        add_fill(fills, f"{label} row {dz}", (cx - half, y1, cz + dz), (cx + half, y2, cz + dz + step - 1), block)


def _ring(
    fills: list[Fill],
    label: str,
    cx: int,
    cz: int,
    r: int,
    y1: int,
    y2: int,
    block: str,
    width: int = 2,
    step: int = 2,
) -> None:
    """Approximate a circular ring wall with scanline outline rows."""
    inner = r - width
    for dz in range(-r, r + 1, step):
        outer_half = int((r * r - dz * dz) ** 0.5)
        inner_half = int(max(0, inner * inner - dz * dz) ** 0.5) if abs(dz) <= inner else 0
        z = cz + dz
        # west and east arcs of the ring
        add_fill(fills, f"{label} w {dz}", (cx - outer_half, y1, z), (cx - inner_half, y2, z + step - 1), block)
        add_fill(fills, f"{label} e {dz}", (cx + inner_half, y1, z), (cx + outer_half, y2, z + step - 1), block)


def _dome(fills: list[Fill], label: str, cx: int, cz: int, radius: int, base_y: int, block: str, shell: int = 2, step: int = 3) -> int:
    """True dome: stack horizontal scanline rings of shrinking radius (top half of a sphere shell).

    Returns the y level just above the last shell layer.
    """
    top_y = base_y
    for t in range(radius):
        r = int((radius * radius - t * t) ** 0.5)
        if r < 3:
            break
        _ring(fills, f"{label} layer {t}", cx, cz, r, base_y + t, base_y + t, block, width=shell, step=step)
        top_y = base_y + t + 1
    return top_y


def _build_tower(fills: list[Fill]) -> None:
    """旗亭 Market Office Tower at (1250, 2550)."""
    # Clear leftover market stalls inside the tower footprint.
    add_fill(fills, "qiting clear", (1234, 3, 2530), (1266, 46, 2570), M.AIR)
    # Stone platform + front apron flush with the market street level.
    add_fill(fills, "qiting platform", (1236, 1, 2536), (1264, 2, 2564), M.STONE)
    add_fill(fills, "qiting apron", (1240, 2, 2530), (1260, 2, 2535), M.SMOOTH)

    # ------------------------------------------------------------------
    # Three inset storeys: red walls + dark-oak edge columns.
    # ------------------------------------------------------------------
    for s in range(3):
        ix1, iz1 = TOWER_X1 + s, TOWER_Z1 + s
        ix2, iz2 = TOWER_X2 - s, TOWER_Z2 - s
        y0 = TOWER_BASE_Y + s * STOREY_PITCH
        y1 = y0 + STOREY_PITCH - 2
        add_outline(fills, f"qiting storey {s} walls", ix1, iz1, ix2, iz2, y0, y1, M.RED_WALL, thickness=1)
        mx, mz = (ix1 + ix2) // 2, (iz1 + iz2) // 2
        for cx, cz in ((ix1, iz1), (ix1, iz2), (ix2, iz1), (ix2, iz2), (mx, iz1), (mx, iz2), (ix1, mz), (ix2, mz)):
            add_fill(fills, f"qiting storey {s} column {cx},{cz}", (cx, y0, cz), (cx, y1, cz), M.LOG)

    # Wood floors between storeys.
    add_fill(fills, "qiting floor 1", (1239, 11, 2539), (1260, 11, 2560), M.WOOD)
    add_fill(fills, "qiting floor 2", (1240, 20, 2540), (1259, 20, 2559), M.WOOD)

    # ------------------------------------------------------------------
    # Ground floor: open arched market-office front.
    # ------------------------------------------------------------------
    arches = [
        # (opening a, opening b, lintel a, lintel b, lintel block)
        ((1243, 3, 2538), (1246, 7, 2538), (1242, 8, 2538), (1247, 8, 2538), LOG_X),   # north front west arch
        ((1253, 3, 2538), (1256, 7, 2538), (1252, 8, 2538), (1257, 8, 2538), LOG_X),   # north front east arch
        ((1248, 3, 2561), (1251, 7, 2561), (1247, 8, 2561), (1252, 8, 2561), LOG_X),   # south door
        ((1261, 3, 2548), (1261, 7, 2551), (1261, 8, 2547), (1261, 8, 2552), LOG_Z),   # east door
        ((1238, 3, 2548), (1238, 7, 2551), (1238, 8, 2547), (1238, 8, 2552), LOG_Z),   # west door
    ]
    for index, (oa, ob, la, lb, lintel_block) in enumerate(arches):
        add_fill(fills, f"qiting arch {index} opening", oa, ob, M.AIR)
        add_fill(fills, f"qiting arch {index} lintel", la, lb, lintel_block)

    # Small windows on the upper two storeys.
    for s in (1, 2):
        ix1, iz1 = TOWER_X1 + s, TOWER_Z1 + s
        ix2, iz2 = TOWER_X2 - s, TOWER_Z2 - s
        wy1 = TOWER_BASE_Y + s * STOREY_PITCH + 2
        wy2 = wy1 + 2
        for wx in (ix1 + 4, ix2 - 5):
            add_fill(fills, f"qiting s{s} window n {wx}", (wx, wy1, iz1), (wx + 1, wy2, iz1), M.AIR)
            add_fill(fills, f"qiting s{s} window s {wx}", (wx, wy1, iz2), (wx + 1, wy2, iz2), M.AIR)
        for wz in (iz1 + 4, iz2 - 5):
            add_fill(fills, f"qiting s{s} window w {wz}", (ix1, wy1, wz), (ix1, wy2, wz + 1), M.AIR)
            add_fill(fills, f"qiting s{s} window e {wz}", (ix2, wy1, wz), (ix2, wy2, wz + 1), M.AIR)

    # ------------------------------------------------------------------
    # Second-floor balcony with the market opening/closing drum.
    # ------------------------------------------------------------------
    add_fill(fills, "qiting balcony slab", (1243, 11, 2534), (1257, 11, 2538), M.WOOD)
    add_fill(fills, "qiting balcony post w", (1243, 3, 2534), (1243, 10, 2534), M.LOG)
    add_fill(fills, "qiting balcony post e", (1257, 3, 2534), (1257, 10, 2534), M.LOG)
    add_outline(fills, "qiting balcony rail", 1243, 2534, 1257, 2538, 12, 12, M.FENCE, thickness=1)
    # Door from storey 1 onto the balcony (cuts railing + wall).
    add_fill(fills, "qiting balcony door", (1248, 12, 2538), (1250, 15, 2539), M.AIR)
    add_fill(fills, "qiting balcony door lintel", (1247, 16, 2539), (1251, 16, 2539), LOG_X)
    # Drum frame: red wool drum hanging in a dark-oak frame.
    add_fill(fills, "qiting drum post w", (1245, 12, 2535), (1245, 14, 2535), M.FENCE)
    add_fill(fills, "qiting drum post e", (1248, 12, 2535), (1248, 14, 2535), M.FENCE)
    add_fill(fills, "qiting drum beam", (1245, 15, 2535), (1248, 15, 2535), LOG_X)
    add_fill(fills, "qiting drum", (1246, 13, 2535), (1247, 14, 2535), M.RED_WOOL)

    # ------------------------------------------------------------------
    # Ground-floor office interior: counter, document chests, lanterns.
    # ------------------------------------------------------------------
    add_fill(fills, "qiting counter", (1244, 3, 2556), (1256, 3, 2556), M.SPRUCE)
    add_fill(fills, "qiting document chests", (1245, 3, 2558), (1255, 3, 2558), CHEST)
    add_fill(fills, "qiting counter lantern w", (1244, 4, 2556), (1244, 4, 2556), M.LANTERN)
    add_fill(fills, "qiting counter lantern e", (1256, 4, 2556), (1256, 4, 2556), M.LANTERN)

    # ------------------------------------------------------------------
    # Interior straight staircases climbing storey to storey.
    # ------------------------------------------------------------------
    add_staircase(fills, "qiting stair 0", 1240, 2540, 1248, 2541, 3, 11, "east", block=M.WOOD)
    add_fill(fills, "qiting stair 0 hole", (1240, 11, 2540), (1247, 11, 2541), M.AIR)
    add_staircase(fills, "qiting stair 1", 1250, 2557, 1258, 2558, 12, 20, "west", block=M.WOOD)
    add_fill(fills, "qiting stair 1 hole", (1251, 20, 2557), (1258, 20, 2558), M.AIR)

    # ------------------------------------------------------------------
    # 庑殿顶 hip roof, then roof-top flag poles with wool banners.
    # ------------------------------------------------------------------
    add_hip_roof(fills, "qiting roof", 1236, 2536, 1263, 2563, 29, 8, ridge_axis="z", roof_block=M.ROOF_GREEN, ridge_block=M.GOLD)
    banners = [
        (1237, 2537, 1, 1, M.RED_WOOL),
        (1262, 2537, -1, 1, M.YELLOW_WOOL),
        (1237, 2562, 1, -1, M.BLUE_WOOL),
        (1262, 2562, -1, -1, M.RED_WOOL),
    ]
    for index, (px, pz, dx, dz, wool) in enumerate(banners):
        add_fill(fills, f"qiting flag pole {index}", (px, 29, pz), (px, 36, pz), M.LOG)
        add_fill(fills, f"qiting banner {index}", (px + dx, 33, pz + dz), (px + dx, 35, pz + dz), wool)


def _build_tavern(fills: list[Fill]) -> None:
    """胡商酒肆 Sogdian tavern at (1330, 2480)."""
    cx, cz, r = TAV_CX, TAV_CZ, TAV_R

    # Clear leftover market stalls inside the tavern footprint.
    add_fill(fills, "tavern clear", (1312, 3, 2444), (1348, 30, 2498), M.AIR)

    # Quartz floor + circular white-terracotta drum wall.
    _disk(fills, "tavern floor", cx, cz, r - 1, 2, 2, M.QUARTZ)
    _ring(fills, "tavern wall", cx, cz, r, TAV_WALL_Y1, TAV_WALL_Y2, M.WHITE_TERRACOTTA, width=2)

    # ------------------------------------------------------------------
    # Arched doorways on four sides (carve AIR + dark-oak lintels/posts).
    # ------------------------------------------------------------------
    add_fill(fills, "tavern door n opening", (1328, 3, 2464), (1332, 7, 2469), M.AIR)
    add_fill(fills, "tavern door n lintel", (1327, 8, 2466), (1333, 8, 2466), LOG_X)
    add_fill(fills, "tavern door n post w", (1328, 3, 2466), (1328, 8, 2466), M.LOG)
    add_fill(fills, "tavern door n post e", (1332, 3, 2466), (1332, 8, 2466), M.LOG)
    add_fill(fills, "tavern door s opening", (1328, 3, 2491), (1332, 7, 2496), M.AIR)
    add_fill(fills, "tavern door s lintel", (1327, 8, 2494), (1333, 8, 2494), LOG_X)
    add_fill(fills, "tavern door s post w", (1328, 3, 2494), (1328, 8, 2494), M.LOG)
    add_fill(fills, "tavern door s post e", (1332, 3, 2494), (1332, 8, 2494), M.LOG)
    add_fill(fills, "tavern door e opening", (1342, 3, 2478), (1347, 7, 2482), M.AIR)
    add_fill(fills, "tavern door e lintel", (1344, 8, 2477), (1344, 8, 2483), LOG_Z)
    add_fill(fills, "tavern door e post n", (1344, 3, 2478), (1344, 8, 2478), M.LOG)
    add_fill(fills, "tavern door e post s", (1344, 3, 2482), (1344, 8, 2482), M.LOG)
    add_fill(fills, "tavern door w opening", (1313, 3, 2478), (1318, 7, 2482), M.AIR)
    add_fill(fills, "tavern door w lintel", (1316, 8, 2477), (1316, 8, 2483), LOG_Z)
    add_fill(fills, "tavern door w post n", (1316, 3, 2478), (1316, 8, 2478), M.LOG)
    add_fill(fills, "tavern door w post s", (1316, 3, 2482), (1316, 8, 2482), M.LOG)

    # ------------------------------------------------------------------
    # True dome roof (sphere shell) with a gold oculus ring at the top.
    # ------------------------------------------------------------------
    dome_top = _dome(fills, "tavern dome", cx, cz, r, TAV_DOME_Y, M.WHITE_TERRACOTTA, shell=2, step=3)
    _ring(fills, "tavern oculus", cx, cz, 3, dome_top, dome_top, M.GOLD, width=1, step=1)

    # ------------------------------------------------------------------
    # Interior: circular bar counter, wine jars, hanging lanterns.
    # ------------------------------------------------------------------
    _ring(fills, "tavern bar", cx, cz, 5, 3, 3, M.SPRUCE, width=1)
    for i in range(8):
        ang = i * math.pi / 4
        jx = cx + int(9 * math.cos(ang))
        jz = cz + int(9 * math.sin(ang))
        add_fill(fills, f"tavern jar {i}", (jx, 3, jz), (jx, 4, jz), BROWN_TERRACOTTA)
    # Dark-oak beams across the dome springing, lanterns hanging below.
    add_fill(fills, "tavern beam x", (1319, 9, 2480), (1341, 9, 2480), LOG_X)
    add_fill(fills, "tavern beam z", (1330, 9, 2472), (1330, 9, 2488), LOG_Z)
    for i, (lx, lz) in enumerate([(1324, 2480), (1330, 2480), (1336, 2480), (1330, 2474), (1330, 2486)]):
        add_fill(fills, f"tavern lantern {i}", (lx, 8, lz), (lx, 8, lz), M.LANTERN)

    # ------------------------------------------------------------------
    # Underground wine cellar with jar rows and a descending staircase.
    # ------------------------------------------------------------------
    add_underground_room(fills, "tavern cellar", 1322, 2472, 1338, 2488, y_floor=-6, y_ceiling=-2, block=M.STONE)
    add_fill(fills, "tavern cellar jars n", (1324, -6, 2474), (1336, -5, 2474), BROWN_TERRACOTTA)
    add_fill(fills, "tavern cellar jars s", (1324, -6, 2486), (1336, -5, 2486), BROWN_TERRACOTTA)
    add_fill(fills, "tavern cellar lantern", (1330, -2, 2480), (1330, -2, 2480), M.LANTERN)
    # Stairwell punched through cellar ceiling + ground + tavern floor.
    add_fill(fills, "tavern cellar shaft", (1333, -1, 2477), (1337, 2, 2485), M.AIR)
    add_staircase(fills, "tavern cellar stair", 1334, 2486, 1336, 2478, -6, 2, "north", block=M.SPRUCE)

    # ------------------------------------------------------------------
    # Front courtyard: Persian carpet + camel-caravan cargo piles.
    # ------------------------------------------------------------------
    add_outline(fills, "carpet border", 1320, 2450, 1340, 2462, 2, 2, M.RED_WOOL, thickness=1)
    for z in range(2451, 2462):
        wool = M.YELLOW_WOOL if (z - 2451) % 2 == 0 else M.BLUE_WOOL
        add_fill(fills, f"carpet stripe {z}", (1321, 2, z), (1339, 2, z), wool)
    add_fill(fills, "carpet medallion", (1328, 2, 2454), (1332, 2, 2458), M.YELLOW_WOOL)
    add_fill(fills, "carpet medallion core", (1329, 2, 2455), (1331, 2, 2457), M.RED_WOOL)

    # Cargo pile 1: chests + yellow/white wool bales.
    add_fill(fills, "cargo 1 chests", (1312, 3, 2454), (1313, 3, 2454), CHEST)
    add_fill(fills, "cargo 1 bales yellow", (1312, 3, 2455), (1313, 4, 2456), M.YELLOW_WOOL)
    add_fill(fills, "cargo 1 bales white", (1314, 3, 2455), (1315, 3, 2456), M.WHITE_WOOL)
    # Cargo pile 2: chests + blue/red wool bales.
    add_fill(fills, "cargo 2 chests", (1346, 3, 2456), (1347, 3, 2456), CHEST)
    add_fill(fills, "cargo 2 bales blue", (1346, 3, 2457), (1347, 4, 2458), M.BLUE_WOOL)
    add_fill(fills, "cargo 2 bales red", (1348, 3, 2457), (1349, 3, 2458), M.RED_WOOL)


def build_xishi_qiting_3d(fills: list[Fill]) -> None:
    _build_tower(fills)
    _build_tavern(fills)


def main() -> None:
    run_builder(build_xishi_qiting_3d, "xishi_qiting_3d")


if __name__ == "__main__":
    main()
