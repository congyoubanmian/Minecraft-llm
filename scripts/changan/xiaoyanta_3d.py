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
    add_platform_with_steps,
    add_pyramid_roof,
    add_spiral_stair,
    add_tree,
    add_underground_room,
    run_builder,
)


"""
Small Wild Goose Pagoda 3D deepening (小雁塔 · 雁塔晨钟 3D 深化).

This module deepens the existing pagoda_small.py build: the thirteen
dense-eave tiers themselves are left untouched, and only new 3D detail is
overlaid on top of the known tier geometry.

"Yan Ta Chen Zhong" (雁塔晨钟, the Morning Bell of the Wild Goose Pagoda) is
one of the Eight Scenic Views of Guanzhong (关中八景); the great bell of the
Jianfu Temple bell tower is a genuine surviving relic, which is why the bell
pavilion is the centerpiece of this pass.

Location: Jianfu Temple courtyard, centered on the pagoda at local
(1320, 3700). Every fill stays strictly inside x 1150..1500, z 3560..3920
(the Tangchang Abbey ground north of z 3500 is never touched).

Distinctive features:
    - Underground reliquary palace (地宫) beneath the tower base at
      y -6..-2: stone sarcophagus bed, lamp niches in all four walls, a
      quartz-and-gold relic casket, and a south descending stone stair
      (磴道) from the courtyard
    - Wind bells (风铃) at every eave corner of all thirteen tiers: one
      gold bell plus a 2-block iron-bar chain, offset one block diagonally
      from the existing GOLD_ACCENT corner posts so they never collide
    - Rebuilt segmented finial (塔刹): smooth-stone inverted bowl (覆钵),
      three stacked gold ring discs (相轮), a crescent moon (仰月) and a
      glowing jewel (宝珠), ~10 blocks tall, replacing the plain gold rod
    - A carved central stairwell with a per-storey spiral stair (塔内螺旋梯)
      climbing the full tower, plus a small south arched doorway (南向券门)
      on every storey
    - The Morning Bell Tower (钟楼) southeast of the pagoda: two-tier
      terrace, four-column pavilion with a gilded pyramid roof (攒尖金顶),
      a segmented tapering gold bell hung on an iron chain, and a log
      striking beam (撞木)
    - "Morning Bell" stele (雁塔晨钟碑) beside the tower
    - Brick paving ring around the pagoda with four avenues and lamp posts
    - Two old scholar trees (古槐) with wide crowns

Base tier geometry (must match pagoda_small.py exactly):
    tier t (0..12): r = max(8, 34 - 2t), y_base = 1 + 6t,
    body y_base..y_base+5, eave at y_eave = y_base + 5, old spire y 79..93.
"""

CX = 1320
CZ = 3700

BASE_RADIUS = 34
TIERS = 13
TIER_HEIGHT = 5
TIER_PITCH = 6  # vertical pitch between storeys used by pagoda_small.py

# Morning Bell Tower site: southeast of the pagoda, in the free slot between
# the old pagoda courtyard wall (x 1399..1400) and the monastery quarters
# (walls x >= 1430, roof from x 1424), both built by other modules.
BELL_X = 1412
BELL_Z = 3746

QUARTZ_PILLAR = "minecraft:quartz_pillar"


def _tier(t: int) -> tuple[int, int]:
    """Radius and base y of tier t, exactly as pagoda_small.py builds it."""
    return max(8, BASE_RADIUS - 2 * t), 1 + TIER_PITCH * t


def _lamp_post(fills: list[Fill], label: str, x: int, z: int) -> None:
    """Slim courtyard lamp: log post with a lantern on top."""
    add_fill(fills, f"{label} post", (x, 5, z), (x, 9, z), M.LOG)
    add_fill(fills, f"{label} light", (x, 10, z), (x, 10, z), M.LANTERN)


def build_xiaoyanta_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Pagoda courtyard brick paving: ring + four avenues + lamp posts.
    #    (Paved first so later door carves can cut through it.)
    # ------------------------------------------------------------------
    # Ring apron around the tier-0 body (body footprint 1286..1354 squared).
    add_fill(fills, "xiaoyanta pave ring n", (1275, 4, 3655), (1365, 4, 3665), M.STONE)
    add_fill(fills, "xiaoyanta pave ring s w", (1275, 4, 3735), (1328, 4, 3745), M.STONE)
    add_fill(fills, "xiaoyanta pave ring s e", (1338, 4, 3735), (1365, 4, 3745), M.STONE)
    add_fill(fills, "xiaoyanta pave ring w", (1275, 4, 3666), (1285, 4, 3734), M.STONE)
    add_fill(fills, "xiaoyanta pave ring e", (1355, 4, 3666), (1365, 4, 3734), M.STONE)
    # Four avenues toward the old courtyard walls (gap in the south ring is
    # the crypt stair trench).
    add_fill(fills, "xiaoyanta avenue n", (1312, 4, 3624), (1328, 4, 3654), M.SMOOTH)
    add_fill(fills, "xiaoyanta avenue s", (1312, 4, 3753), (1328, 4, 3776), M.SMOOTH)
    add_fill(fills, "xiaoyanta avenue e", (1366, 4, 3692), (1397, 4, 3708), M.SMOOTH)
    add_fill(fills, "xiaoyanta avenue w", (1243, 4, 3692), (1274, 4, 3708), M.SMOOTH)
    # Forecourt in front of the crypt stair portal.
    add_fill(fills, "xiaoyanta crypt forecourt", (1312, 4, 3749), (1339, 4, 3752), M.SMOOTH)
    for i, (lx, lz) in enumerate(
        [(1284, 3663), (1356, 3663), (1284, 3737), (1356, 3737),
         (1314, 3650), (1326, 3650), (1314, 3756), (1326, 3756)]
    ):
        _lamp_post(fills, f"xiaoyanta court lamp {i}", lx, lz)

    # ------------------------------------------------------------------
    # 2. Underground reliquary palace (地宫) below the tower base.
    # ------------------------------------------------------------------
    add_underground_room(
        fills, "xiaoyanta crypt",
        CX - 14, CZ - 14, CX + 14, CZ + 14,
        y_floor=-6, y_ceiling=-2, block=M.STONE,
    )
    # Stone sarcophagus bed along the north wall with a quartz coffin.
    add_fill(fills, "xiaoyanta crypt sarcophagus bed", (1312, -6, 3688), (1328, -5, 3694), M.SMOOTH)
    add_fill(fills, "xiaoyanta crypt coffin", (1315, -5, 3690), (1325, -4, 3692), M.QUARTZ)
    # Relic casket (舍利函): quartz pedestal, gold box, glowing core.
    add_fill(fills, "xiaoyanta crypt casket pedestal", (1318, -6, 3703), (1322, -5, 3707), M.QUARTZ)
    add_fill(fills, "xiaoyanta crypt casket", (1319, -4, 3704), (1321, -3, 3706), M.GOLD)
    add_fill(fills, "xiaoyanta crypt casket glow", (1320, -3, 3705), (1320, -3, 3705), M.SEA_LANTERN)
    # Lamp niches in all four walls (quartz bracket + lantern).
    for i, (nx, nz) in enumerate([(1320, 3687), (1333, 3700), (1307, 3700), (1312, 3713)]):
        add_fill(fills, f"xiaoyanta crypt niche {i}", (nx, -5, nz), (nx, -5, nz), M.QUARTZ)
        add_fill(fills, f"xiaoyanta crypt niche lamp {i}", (nx, -4, nz), (nx, -4, nz), M.LANTERN)
    # South descending stair (磴道): eleven steps dropping y 4 -> -6, east of
    # the ground-floor doorway so the trench never blocks it.
    for i in range(11):
        z = 3747 - i
        y = 4 - i
        add_fill(fills, f"xiaoyanta crypt stair step {i}", (1331, y, z), (1335, y, z), M.SMOOTH)
        add_fill(fills, f"xiaoyanta crypt stair head {i}", (1331, y + 1, z), (1335, y + 3, z), M.AIR)
    # Flanking parapets and an entry portal at the trench head.
    add_fill(fills, "xiaoyanta crypt stair parapet w", (1329, 0, 3737), (1330, 8, 3747), M.STONE)
    add_fill(fills, "xiaoyanta crypt stair parapet e", (1336, 0, 3737), (1337, 8, 3747), M.STONE)
    add_fill(fills, "xiaoyanta crypt portal post w", (1329, 5, 3748), (1329, 9, 3748), M.QUARTZ)
    add_fill(fills, "xiaoyanta crypt portal post e", (1337, 5, 3748), (1337, 9, 3748), M.QUARTZ)
    add_fill(fills, "xiaoyanta crypt portal lintel", (1329, 10, 3748), (1337, 10, 3748), M.QUARTZ)
    add_fill(fills, "xiaoyanta crypt portal lamp", (1333, 11, 3748), (1333, 11, 3748), M.LANTERN)
    add_fill(fills, "xiaoyanta crypt portal opening", (1331, 5, 3745), (1335, 9, 3748), M.AIR)
    # Tunnel from the stair foot north into the crypt through its south wall.
    add_fill(fills, "xiaoyanta crypt tunnel", (1331, -6, 3714), (1335, -2, 3736), M.AIR)
    add_fill(fills, "xiaoyanta crypt tunnel floor", (1331, -7, 3714), (1335, -7, 3736), M.SMOOTH)

    # ------------------------------------------------------------------
    # 3. Tower interior: central stairwell shaft, per-storey spiral stairs,
    #    and a south arched doorway (券门) on every storey.
    # ------------------------------------------------------------------
    # One continuous open shaft (half-width 7) through every storey floor.
    add_fill(fills, "xiaoyanta stairwell shaft", (CX - 7, 2, CZ - 7), (CX + 7, 78, CZ + 7), M.AIR)
    for t in range(TIERS):
        r, y_base = _tier(t)
        # Spiral stair climbing this storey inside the shaft (the lib draws
        # eight ring segments rising one block each, so it overshoots y2 by
        # design and neatly pokes into the next storey's carved shaft).
        add_spiral_stair(fills, f"xiaoyanta stair t{t}", CX, CZ, 6, y_base + 1, y_base + 7, M.SMOOTH)
        # Small south arched doorway through the wall (2-3 blocks wide, 3 high).
        add_fill(
            fills, f"xiaoyanta south door t{t}",
            (CX - 1, y_base + 1, CZ + r - 2), (CX + 1, y_base + 3, CZ + r + 1), M.AIR,
        )

    # ------------------------------------------------------------------
    # 4. Wind bells (风铃) at every eave corner of every tier.
    #    The base eave puts a GOLD_ACCENT post at the (r+4, r+4) diagonal;
    #    these bells sit one block further out at (r+5, r+5) so they never
    #    collide, one gold bell with a 2-block iron chain below.
    # ------------------------------------------------------------------
    for t in range(TIERS):
        r, y_base = _tier(t)
        y_eave = y_base + TIER_HEIGHT
        for sx in (-1, 1):
            for sz in (-1, 1):
                bx = CX + sx * (r + 5)
                bz = CZ + sz * (r + 5)
                add_fill(fills, f"xiaoyanta wind bell t{t} {sx},{sz}", (bx, y_eave, bz), (bx, y_eave, bz), M.GOLD)
                add_fill(fills, f"xiaoyanta wind bell chain t{t} {sx},{sz}", (bx, y_eave - 2, bz), (bx, y_eave - 1, bz), M.IRON_BARS)

    # ------------------------------------------------------------------
    # 5. Rebuilt segmented finial (塔刹), replacing the plain gold rod
    #    (old spire occupied y 79..93). Total height ~10: y 79..90.
    # ------------------------------------------------------------------
    add_fill(fills, "xiaoyanta finial clear old", (CX - 3, 79, CZ - 3), (CX + 3, 94, CZ + 3), M.AIR)
    # Inverted bowl (覆钵): shrinking smooth-stone discs.
    add_fill(fills, "xiaoyanta finial bowl base", (CX - 2, 79, CZ - 2), (CX + 2, 79, CZ + 2), M.SMOOTH)
    add_fill(fills, "xiaoyanta finial bowl top", (CX - 1, 80, CZ - 1), (CX + 1, 80, CZ + 1), M.SMOOTH)
    # Mast with three gold ring discs (相轮).
    add_fill(fills, "xiaoyanta finial mast", (CX, 81, CZ), (CX, 87, CZ), M.GOLD)
    for i, ry in enumerate((82, 84, 86)):
        add_fill(fills, f"xiaoyanta finial ring {i}", (CX - 1, ry, CZ - 1), (CX + 1, ry, CZ + 1), M.GOLD)
    # Crescent moon (仰月).
    add_fill(fills, "xiaoyanta finial moon", (CX - 2, 88, CZ), (CX + 2, 88, CZ), M.GOLD)
    # Jewel (宝珠) with a glowing heart.
    add_fill(fills, "xiaoyanta finial jewel", (CX, 89, CZ), (CX, 89, CZ), M.GOLD)
    add_fill(fills, "xiaoyanta finial jewel glow", (CX, 90, CZ), (CX, 90, CZ), M.SEA_LANTERN)

    # ------------------------------------------------------------------
    # 6. Morning Bell Tower (雁塔晨钟楼): two-tier terrace, four-column
    #    pavilion with gilded pyramid roof, hanging segmented gold bell,
    #    and a log striking beam.
    # ------------------------------------------------------------------
    add_fill(fills, "xiaoyanta bell tower clear site", (BELL_X - 11, 1, BELL_Z - 12), (BELL_X + 9, 32, BELL_Z + 12), M.AIR)
    # Two-tier terrace (两层台基).
    add_platform_with_steps(
        fills, "xiaoyanta bell terrace",
        BELL_X - 11, BELL_Z - 12, BELL_X + 11, BELL_Z + 12, 5,
        [(2, 0, M.STONE), (2, 2, M.SMOOTH)],
    )
    # South approach steps: ground -> lower terrace -> upper terrace.
    add_fill(fills, "xiaoyanta bell step 1", (BELL_X - 3, 5, BELL_Z + 15), (BELL_X + 3, 5, BELL_Z + 16), M.SMOOTH)
    add_fill(fills, "xiaoyanta bell step 2", (BELL_X - 3, 6, BELL_Z + 13), (BELL_X + 3, 6, BELL_Z + 14), M.SMOOTH)
    add_fill(fills, "xiaoyanta bell step 3", (BELL_X - 3, 7, BELL_Z + 11), (BELL_X + 3, 7, BELL_Z + 12), M.SMOOTH)
    add_fill(fills, "xiaoyanta bell step 4", (BELL_X - 3, 8, BELL_Z + 9), (BELL_X + 3, 8, BELL_Z + 10), M.SMOOTH)
    # Four pillars (四柱) on the upper terrace.
    for i, (px, pz) in enumerate([(BELL_X - 7, BELL_Z - 8), (BELL_X + 7, BELL_Z - 8),
                                  (BELL_X - 7, BELL_Z + 8), (BELL_X + 7, BELL_Z + 8)]):
        add_fill(fills, f"xiaoyanta bell pillar {i}", (px, 9, pz), (px + 1, 18, pz + 1), M.LOG)
    # Tie-beam ring on the pillars plus a center hook beam.
    add_outline(fills, "xiaoyanta bell tie beam", BELL_X - 7, BELL_Z - 8, BELL_X + 7, BELL_Z + 8, 19, 19, M.LOG, thickness=1)
    add_fill(fills, "xiaoyanta bell hook beam", (BELL_X - 7, 19, BELL_Z), (BELL_X + 7, 19, BELL_Z), M.LOG)
    # Hanging chain and the great bell: 3x3 tapering body, 4 tall.
    add_fill(fills, "xiaoyanta bell chain", (BELL_X, 17, BELL_Z), (BELL_X, 18, BELL_Z), M.IRON_BARS)
    add_fill(fills, "xiaoyanta bell body", (BELL_X - 1, 13, BELL_Z - 1), (BELL_X + 1, 15, BELL_Z + 1), M.GOLD)
    add_fill(fills, "xiaoyanta bell crown", (BELL_X, 16, BELL_Z), (BELL_X, 16, BELL_Z), M.GOLD)
    # Log striking beam (撞木) on a fence sling, resting against the bell face.
    add_fill(fills, "xiaoyanta bell striker sling", (BELL_X - 4, 15, BELL_Z), (BELL_X - 4, 18, BELL_Z), M.FENCE)
    add_fill(fills, "xiaoyanta bell striker", (BELL_X - 4, 14, BELL_Z), (BELL_X - 2, 14, BELL_Z), M.LOG)
    # Gilded pyramid roof (攒尖金顶).
    add_pyramid_roof(fills, "xiaoyanta bell pavilion roof", BELL_X, BELL_Z, 9, 20, M.ROOF_GREEN, M.GOLD)

    # ------------------------------------------------------------------
    # 7. "Morning Bell" stele (雁塔晨钟碑) beside the tower.
    # ------------------------------------------------------------------
    add_fill(fills, "xiaoyanta stele base", (1416, 5, 3765), (1420, 6, 3767), M.DARK)
    add_fill(fills, "xiaoyanta stele tablet", (1418, 7, 3766), (1418, 12, 3766), QUARTZ_PILLAR)
    add_fill(fills, "xiaoyanta stele cap", (1417, 13, 3765), (1419, 13, 3767), M.GOLD)

    # ------------------------------------------------------------------
    # 8. Two old scholar trees (古槐) with wide crowns.
    # ------------------------------------------------------------------
    add_tree(fills, "xiaoyanta locust tree w", 1268, 3656, 5, height=8, spread=3)
    add_tree(fills, "xiaoyanta locust tree s", 1370, 3770, 5, height=8, spread=3)


def main() -> None:
    run_builder(build_xiaoyanta_3d, "xiaoyanta_3d")


if __name__ == "__main__":
    main()
