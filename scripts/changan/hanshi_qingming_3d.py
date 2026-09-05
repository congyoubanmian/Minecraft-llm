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
    add_hollow_box,
    add_pixel_mural,
    run_builder,
    w,
)


"""
Hanshi & Qingming Folk Cemetery (寒食·清明坟园) - "清明时节雨纷纷": the Tang
cold-food / tomb-sweeping festival scene in the folk graveyard on the
north-east outskirts, beside the imperial tomb complex.

Location in Chang'an city local coordinates:
    Folk graveyard plot: x 6950..7350, z 6450..6850 (ground level y 0-4,
    all main bodies rise from y 5). Hard site rule: every fill stays inside
    the plot.
    Avoidance: the imperial tomb complex (tomb_spirit_way.py) sits around
    (6700, 6700). Its actual footprint - stepped mound x 6640..6760 /
    z 6640..6760, spirit road x 6692..6708 running to z 6950, guardian and
    hall corridor x 6676..6724, stele pavilion x 6694..6706 - is entirely
    west of x 6760. This site starts at x 6950, keeping a >=190 block
    buffer; the north farm belt (suburb_farms.py, x <= 6800) is not touched
    either. A bounds check runs at the end of the builder.

Distinctive features:
    - Seven folk burial mounds (four 7x7 domes y4..7, three 5x5 domes
      y4..6, dirt/grass shrinking each layer), each with a quartz-pillar
      stele on a dark plinth with a gold cap (big stelae carry pixel
      epitaph murals), an offering table with white dumplings and a red
      fruit plate, and a willow twig planted on the mound top
    - Paper-money shop by the park gate: five 3-strand yellow paper strings
      on a shelf, a blocky white paper horse, and a cash chest
    - Cold-food stove (禁火灶) by the gate: the fire is banned for hanshi,
      so the stove mouth is sealed with a barrel, white ash spilled in
      front, and a cold-food table with round wheat cakes and an
      apricot-jelly bowl
    - Willow custom (插柳): leaf strands on the gate lintel and on every
      mound top, plus six weeping willows (double leaf layers + hanging
      strands) around the park
    - Tall hanshi swing: two y+12 posts, a crossbeam, twin iron-bar ropes
      and a plank seat, with a small child swing beside it
    - Stone offering altar: two smooth-stone tiers, a barrel censer with a
      glowing incense light, and four corner candle lanterns
    - Two thatched mourning / rest sheds with plank benches
    - Low grassed earthen half-ring park wall open to the south, scattered
      yellow paper money, and puddles left by the drizzling spring rain
"""


# ---------------------------------------------------------------------------
# Site constants. Hard plot bounds - never build outside them.
# ---------------------------------------------------------------------------
X1, Z1 = 6950, 6450
X2, Z2 = 7350, 6850
GROUND_TOP = 4          # grass surface level; structures start at y 5

# tomb_spirit_way.py footprint (all west of this plot): mound x 6640..6760,
# road / hall corridor x 6676..6724 reaching z 6954. The site keeps a
# >=190 block buffer from the complex and clear of the x<=6800 farm belt.
SPIRIT_WAY_MAX_X = 6760

# Single-block ids not present in the shared palette.
QUARTZ_PILLAR = "minecraft:quartz_pillar"
BARREL = "minecraft:barrel"
CHEST = "minecraft:chest"

# Low earthen half-ring wall: arc around the park centre, open to the south.
RING_CX, RING_CZ = 7150, 6640
RING_R = 180
RING_POINTS = [
    (
        round(RING_CX + RING_R * math.cos(math.radians(deg))),
        round(RING_CZ + RING_R * math.sin(math.radians(deg))),
    )
    for deg in range(150, 391, 30)  # 9 points, gap at due south (deg 90)
]

# Burial mounds: (x, z, big?) - four large 7x7 + three small 5x5.
TOMBS = [
    (7030, 6530, True),
    (7100, 6510, True),
    (7020, 6620, True),
    (7100, 6610, True),
    (7200, 6520, False),
    (7260, 6520, False),
    (7220, 6620, False),
]
NORTH_SPUR_END = 6544   # tomb spurs join the north cross path (z 6545..6549)
SOUTH_SPUR_END = 6639   # ... or the south cross path (z 6640..6644)

# Stele epitaph motif (3-wide pixel mural) painted on the big stele bodies.
EPITAPH_ART = ("###", ".#.", "###", ".#.")
EPITAPH_PALETTE = {"#": M.BLACK_WOOL}

# Scattered paper money (8 single blocks) and drizzle puddles.
PAPER_MONEY = [
    (7060, 6540), (7120, 6480), (7220, 6560), (7300, 6600),
    (7080, 6660), (7240, 6650), (7160, 6760), (7090, 6710),
]
PUDDLES = [
    (7075, 6605, 7076, 6606),
    (7205, 6685, 7206, 6686),
    (7135, 6785, 7136, 6786),
]


# ---------------------------------------------------------------------------
# Reusable helpers.
# ---------------------------------------------------------------------------
def _tomb(fills: list[Fill], tag: str, mx: int, mz: int, big: bool) -> None:
    """One grave: stepped earth dome, quartz stele, offerings, mound willow."""
    spur_end = NORTH_SPUR_END if mz <= 6600 else SOUTH_SPUR_END
    if big:
        # 7x7 covered dome y4..7, shrinking each layer (dirt below, turf top).
        add_fill(fills, f"hanshi tomb {tag} mound y4", (mx - 3, 4, mz - 3), (mx + 3, 4, mz + 3), M.DIRT)
        add_fill(fills, f"hanshi tomb {tag} mound y5", (mx - 2, 5, mz - 2), (mx + 2, 5, mz + 2), M.DIRT)
        add_fill(fills, f"hanshi tomb {tag} mound y6", (mx - 1, 6, mz - 1), (mx + 1, 6, mz + 1), M.GRASS)
        add_fill(fills, f"hanshi tomb {tag} mound top", (mx, 7, mz), (mx, 7, mz), M.GRASS)
        stele_z, table_z = mz + 6, mz + 8
        # Stele: dark plinth, 3-wide quartz body with epitaph, gold cap.
        add_fill(fills, f"hanshi tomb {tag} stele base", (mx - 1, 5, stele_z), (mx + 1, 5, stele_z), M.DARK)
        add_fill(fills, f"hanshi tomb {tag} stele body", (mx - 1, 6, stele_z), (mx + 1, 9, stele_z), QUARTZ_PILLAR)
        add_pixel_mural(fills, f"hanshi tomb {tag} epitaph", list(EPITAPH_ART), EPITAPH_PALETTE, mx - 1, 9, stele_z)
        add_fill(fills, f"hanshi tomb {tag} stele cap", (mx - 1, 10, stele_z), (mx + 1, 10, stele_z), M.GOLD)
        add_fill(fills, f"hanshi tomb {tag} mound willow", (mx, 8, mz), (mx, 9, mz), M.LEAVES)
        tx1, tx2 = mx - 1, mx + 1
    else:
        # 5x5 dome y4..6 with a single-block stele.
        add_fill(fills, f"hanshi tomb {tag} mound y4", (mx - 2, 4, mz - 2), (mx + 2, 4, mz + 2), M.DIRT)
        add_fill(fills, f"hanshi tomb {tag} mound y5", (mx - 1, 5, mz - 1), (mx + 1, 5, mz + 1), M.DIRT)
        add_fill(fills, f"hanshi tomb {tag} mound top", (mx, 6, mz), (mx, 6, mz), M.GRASS)
        stele_z, table_z = mz + 5, mz + 7
        add_fill(fills, f"hanshi tomb {tag} stele base", (mx, 5, stele_z), (mx, 5, stele_z), M.DARK)
        add_fill(fills, f"hanshi tomb {tag} stele body", (mx, 6, stele_z), (mx, 8, stele_z), QUARTZ_PILLAR)
        add_fill(fills, f"hanshi tomb {tag} stele cap", (mx, 9, stele_z), (mx, 9, stele_z), M.GOLD)
        add_fill(fills, f"hanshi tomb {tag} mound willow", (mx, 7, mz), (mx, 8, mz), M.LEAVES)
        tx1, tx2 = mx - 1, mx
    # Offering table: plank top on legs, dumplings (white) + fruit plate (red).
    add_fill(fills, f"hanshi tomb {tag} table top", (tx1, 6, table_z), (tx2, 6, table_z), M.WOOD)
    add_fill(fills, f"hanshi tomb {tag} table leg w", (tx1, 5, table_z), (tx1, 5, table_z), M.WOOD)
    add_fill(fills, f"hanshi tomb {tag} table leg e", (tx2, 5, table_z), (tx2, 5, table_z), M.WOOD)
    add_fill(fills, f"hanshi tomb {tag} dumplings", (tx1, 7, table_z), (tx2 - 1, 7, table_z), M.WHITE_WOOL)
    add_fill(fills, f"hanshi tomb {tag} fruit plate", (tx2, 7, table_z), (tx2, 7, table_z), M.RED_WOOL)
    # Gravel spur from the table to the nearest cross path.
    add_fill(fills, f"hanshi tomb {tag} spur", (tx1, 4, table_z + 1), (tx1 + 2, 4, spur_end), M.ANDESITE)


def _willow(fills: list[Fill], tag: str, x: int, z: int) -> None:
    """Weeping willow: tall trunk, double leaf layers, four hanging strands."""
    add_fill(fills, f"hanshi willow {tag} trunk", (x, 5, z), (x, 11, z), M.TREE_LOG)
    add_fill(fills, f"hanshi willow {tag} leaves low", (x - 2, 10, z - 2), (x + 2, 10, z + 2), M.LEAVES)
    add_fill(fills, f"hanshi willow {tag} leaves top", (x - 1, 11, z - 1), (x + 1, 11, z + 1), M.LEAVES)
    for sx, sz in ((x - 2, z), (x + 2, z), (x, z - 2), (x, z + 2)):
        add_fill(fills, f"hanshi willow {tag} strand {sx},{sz}", (sx, 7, sz), (sx, 9, sz), M.LEAVES)


def _ridge(fills: list[Fill], tag: str, p1: tuple[int, int], p2: tuple[int, int]) -> None:
    """Low grassed earthen ridge (2 wide, y5..6) between two plan points."""
    x1, z1 = p1
    x2, z2 = p2
    add_fill(fills, f"hanshi ring {tag} x dirt", (min(x1, x2), 5, z1), (max(x1, x2), 5, z1 + 1), M.DIRT)
    add_fill(fills, f"hanshi ring {tag} x turf", (min(x1, x2), 6, z1), (max(x1, x2), 6, z1 + 1), M.GRASS)
    add_fill(fills, f"hanshi ring {tag} z dirt", (x2, 5, min(z1, z2)), (x2 + 1, 5, max(z1, z2)), M.DIRT)
    add_fill(fills, f"hanshi ring {tag} z turf", (x2, 6, min(z1, z2)), (x2 + 1, 6, max(z1, z2)), M.GRASS)


def _check_bounds(fills: list[Fill]) -> None:
    """Hard site rule: keep every fill inside the graveyard plot, clear of
    the imperial spirit way (all west of x 6760) and the farm belt.

    lib's add_fill already emitted world coordinates (BASE 9000/64/9000
    applied), so the local plot bounds are converted with w() first.
    """
    wx1, _, wz1 = w(X1, 0, Z1)
    wx2, _, wz2 = w(X2, 0, Z2)
    wy_min, wy_max = w(0, 0, 0)[1], w(0, 40, 0)[1]
    for f in fills:
        if not f.label.startswith("hanshi"):
            continue  # build_all accumulates a shared fill list across modules
        if (
            min(f.x1, f.x2) < wx1 or max(f.x1, f.x2) > wx2
            or min(f.z1, f.z2) < wz1 or max(f.z1, f.z2) > wz2
        ):
            raise ValueError(f"outside graveyard plot x{X1}..{X2} z{Z1}..{Z2}: {f}")
        if min(f.y1, f.y2) < wy_min or max(f.y1, f.y2) > wy_max:
            raise ValueError(f"bad height for the graveyard build: {f}")
        if max(f.x1, f.x2) <= w(SPIRIT_WAY_MAX_X, 0, 0)[0]:
            raise ValueError(f"encroaches on tomb_spirit_way corridor: {f}")


# ---------------------------------------------------------------------------
# Main builder.
# ---------------------------------------------------------------------------
def build_hanshi_qingming_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Ground: dirt base y0..3 under a grass surface at y4.
    # ------------------------------------------------------------------
    add_fill(fills, "hanshi ground dirt", (X1, 0, Z1), (X2, 3, Z2), M.DIRT)
    add_fill(fills, "hanshi ground grass", (X1, GROUND_TOP, Z1), (X2, GROUND_TOP, Z2), M.GRASS)

    # ------------------------------------------------------------------
    # 2. Gravel paths: entrance walk, two cross walks, altar walk.
    #    (Tomb spur paths are laid by _tomb.)
    # ------------------------------------------------------------------
    add_fill(fills, "hanshi path main", (7148, GROUND_TOP, 6545), (7152, GROUND_TOP, 6845), M.SMOOTH)
    add_fill(fills, "hanshi path cross n", (7020, GROUND_TOP, 6545), (7270, GROUND_TOP, 6549), M.ANDESITE)
    add_fill(fills, "hanshi path cross s", (7010, GROUND_TOP, 6640), (7240, GROUND_TOP, 6644), M.ANDESITE)
    add_fill(fills, "hanshi path altar", (7123, GROUND_TOP, 6698), (7147, GROUND_TOP, 6702), M.ANDESITE)

    # ------------------------------------------------------------------
    # 3. Low earthen half-ring park wall (土埂), open to the south.
    # ------------------------------------------------------------------
    for i in range(len(RING_POINTS) - 1):
        _ridge(fills, f"seg {i}", RING_POINTS[i], RING_POINTS[i + 1])

    # ------------------------------------------------------------------
    # 4. Park gate: timber posts and lintel, willow strands on the lintel.
    # ------------------------------------------------------------------
    add_fill(fills, "hanshi gate post w", (7145, 5, 6800), (7145, 10, 6800), M.LOG)
    add_fill(fills, "hanshi gate post e", (7155, 5, 6800), (7155, 10, 6800), M.LOG)
    add_fill(fills, "hanshi gate lintel", (7143, 11, 6800), (7157, 11, 6800), M.LOG)
    add_fill(fills, "hanshi gate plaque", (7148, 10, 6800), (7152, 10, 6800), M.DARK)
    add_fill(fills, "hanshi gate willow w", (7147, 8, 6800), (7147, 9, 6800), M.LEAVES)
    add_fill(fills, "hanshi gate willow mid", (7150, 7, 6800), (7150, 9, 6800), M.LEAVES)
    add_fill(fills, "hanshi gate willow e", (7153, 8, 6800), (7153, 9, 6800), M.LEAVES)

    # ------------------------------------------------------------------
    # 5. Paper-money shop (纸钱铺): shelf with 5 yellow paper strings of 3
    #    strands, a white paper horse, and the cash chest.
    # ------------------------------------------------------------------
    add_fill(fills, "hanshi shop floor", (7169, 5, 6825), (7183, 5, 6835), M.WOOD)
    for i, (px, pz) in enumerate([(7170, 6826), (7182, 6826), (7170, 6834), (7182, 6834)]):
        add_fill(fills, f"hanshi shop post {i}", (px, 6, pz), (px, 10, pz), M.LOG)
    add_fill(fills, "hanshi shop back wall", (7170, 6, 6826), (7182, 8, 6826), M.WOOD)
    add_fill(fills, "hanshi shop roof", (7168, 11, 6824), (7184, 11, 6836), M.WOOD)
    add_fill(fills, "hanshi shop shelf", (7171, 9, 6827), (7181, 9, 6827), M.LOG)
    for i, sx in enumerate(range(7172, 7182, 2)):  # 5 strings, 3 strands each
        add_fill(fills, f"hanshi shop paper string {i}", (sx, 6, 6827), (sx, 8, 6827), M.YELLOW_WOOL)
    add_fill(fills, "hanshi shop counter", (7171, 6, 6832), (7176, 7, 6832), M.WOOD)
    add_fill(fills, "hanshi shop cash chest", (7177, 6, 6832), (7177, 6, 6832), CHEST)
    # Blocky white paper horse (纸马) tethered beside the shop.
    add_fill(fills, "hanshi horse body", (7187, 6, 6830), (7190, 6, 6830), M.WHITE_WOOL)
    add_fill(fills, "hanshi horse leg w", (7187, 5, 6830), (7187, 5, 6830), M.WHITE_WOOL)
    add_fill(fills, "hanshi horse leg e", (7190, 5, 6830), (7190, 5, 6830), M.WHITE_WOOL)
    add_fill(fills, "hanshi horse tail", (7186, 7, 6830), (7186, 7, 6830), M.WHITE_WOOL)
    add_fill(fills, "hanshi horse neck", (7189, 7, 6830), (7189, 7, 6830), M.WHITE_WOOL)
    add_fill(fills, "hanshi horse head", (7190, 8, 6830), (7190, 8, 6830), M.WHITE_WOOL)

    # ------------------------------------------------------------------
    # 6. Cold-food stove (禁火灶): the fire is banned for hanshi, so the
    #    stove mouth is sealed with a barrel, ash spilled in front, and a
    #    cold-food table offers round wheat cakes and apricot jelly.
    # ------------------------------------------------------------------
    add_fill(fills, "hanshi stove base", (7114, 5, 6830), (7116, 5, 6832), M.SMOOTH)
    add_hollow_box(fills, "hanshi stove body", 7114, 6, 6830, 7116, 7, 6832, M.STONE)
    add_fill(fills, "hanshi stove sealed mouth", (7115, 6, 6831), (7115, 6, 6831), BARREL)
    add_fill(fills, "hanshi stove cap", (7114, 8, 6830), (7116, 8, 6832), M.SMOOTH)
    add_fill(fills, "hanshi stove ash front", (7114, 5, 6833), (7116, 5, 6834), M.WHITE_TERRACOTTA)
    add_fill(fills, "hanshi stove ash spill", (7115, 5, 6835), (7115, 5, 6835), M.WHITE_TERRACOTTA)
    add_fill(fills, "hanshi stove firewood", (7111, 5, 6829), (7113, 5, 6829), M.LOG)
    add_fill(fills, "hanshi cold table top", (7105, 6, 6832), (7110, 6, 6833), M.WOOD)
    add_fill(fills, "hanshi cold table leg nw", (7105, 5, 6832), (7105, 5, 6832), M.WOOD)
    add_fill(fills, "hanshi cold table leg ne", (7110, 5, 6832), (7110, 5, 6832), M.WOOD)
    add_fill(fills, "hanshi cold table leg sw", (7105, 5, 6833), (7105, 5, 6833), M.WOOD)
    add_fill(fills, "hanshi cold table leg se", (7110, 5, 6833), (7110, 5, 6833), M.WOOD)
    add_fill(fills, "hanshi wheat cakes row", (7106, 7, 6833), (7108, 7, 6833), M.WHITE_WOOL)
    add_fill(fills, "hanshi wheat cake side n", (7107, 7, 6832), (7107, 7, 6832), M.WHITE_WOOL)
    add_fill(fills, "hanshi wheat cake side s", (7107, 7, 6834), (7107, 7, 6834), M.WHITE_WOOL)
    add_fill(fills, "hanshi jelly bowl", (7110, 7, 6833), (7110, 7, 6833), M.DARK)
    add_fill(fills, "hanshi jelly dollop", (7110, 8, 6833), (7110, 8, 6833), M.WHITE_TERRACOTTA)

    # ------------------------------------------------------------------
    # 7. The seven burial mounds (坟丘群): domes, stelae, offerings.
    # ------------------------------------------------------------------
    for i, (mx, mz, big) in enumerate(TOMBS):
        _tomb(fills, str(i + 1), mx, mz, big)

    # ------------------------------------------------------------------
    # 8. Stone offering altar (祭台): two tiers, barrel censer with a
    #    glowing incense light, four corner candle lanterns.
    # ------------------------------------------------------------------
    add_fill(fills, "hanshi altar tier 1", (7117, 5, 6697), (7123, 5, 6703), M.SMOOTH)
    add_fill(fills, "hanshi altar tier 2", (7118, 6, 6698), (7122, 6, 6702), M.SMOOTH)
    add_fill(fills, "hanshi altar censer", (7120, 7, 6700), (7120, 7, 6700), BARREL)
    add_fill(fills, "hanshi altar incense glow", (7120, 8, 6700), (7120, 8, 6700), M.SEA_LANTERN)
    for i, (cx, cz) in enumerate([(7118, 6698), (7122, 6698), (7118, 6702), (7122, 6702)]):
        add_fill(fills, f"hanshi altar candle {i}", (cx, 7, cz), (cx, 7, cz), M.SEA_LANTERN)

    # ------------------------------------------------------------------
    # 9. Hanshi swings (寒食秋千): tall frame with twin ropes and a child
    #    swing beside it - the classic Tang cold-food pastime.
    # ------------------------------------------------------------------
    add_fill(fills, "hanshi swing post w", (7256, 5, 6730), (7256, 17, 6730), M.LOG)
    add_fill(fills, "hanshi swing post e", (7266, 5, 6730), (7266, 17, 6730), M.LOG)
    add_fill(fills, "hanshi swing beam", (7254, 18, 6730), (7268, 18, 6730), M.LOG)
    add_fill(fills, "hanshi swing rope w", (7259, 16, 6730), (7259, 17, 6730), M.IRON_BARS)
    add_fill(fills, "hanshi swing rope e", (7263, 16, 6730), (7263, 17, 6730), M.IRON_BARS)
    add_fill(fills, "hanshi swing seat", (7259, 15, 6730), (7263, 15, 6730), M.WOOD)
    add_fill(fills, "hanshi mini post w", (7056, 5, 6740), (7056, 11, 6740), M.LOG)
    add_fill(fills, "hanshi mini post e", (7063, 5, 6740), (7063, 11, 6740), M.LOG)
    add_fill(fills, "hanshi mini beam", (7054, 12, 6740), (7065, 12, 6740), M.LOG)
    add_fill(fills, "hanshi mini rope w", (7058, 10, 6740), (7058, 11, 6740), M.IRON_BARS)
    add_fill(fills, "hanshi mini rope e", (7061, 10, 6740), (7061, 11, 6740), M.IRON_BARS)
    add_fill(fills, "hanshi mini seat", (7058, 9, 6740), (7061, 9, 6740), M.WOOD)

    # ------------------------------------------------------------------
    # 10. Thatched mourning / rest sheds (哭丧棚) with plank benches.
    # ------------------------------------------------------------------
    for i, (sx1, sz1, sx2, sz2) in enumerate([(7036, 6737, 7042, 6741), (7286, 6696, 7292, 6700)]):
        for j, (px, pz) in enumerate([(sx1, sz1), (sx2, sz1), (sx1, sz2), (sx2, sz2)]):
            add_fill(fills, f"hanshi shed {i} post {j}", (px, 5, pz), (px, 9, pz), M.LOG)
        add_fill(fills, f"hanshi shed {i} thatch", (sx1 - 1, 10, sz1 - 1), (sx2 + 1, 10, sz2 + 1), M.LEAVES)
        add_fill(fills, f"hanshi shed {i} thatch cap", (sx1 + 1, 11, sz1 + 1), (sx2 - 1, 11, sz2 - 1), M.LEAVES)
        add_fill(fills, f"hanshi shed {i} bench n", (sx1 + 1, 5, sz1 + 1), (sx2 - 1, 5, sz1 + 1), M.WOOD)
        add_fill(fills, f"hanshi shed {i} bench s", (sx1 + 1, 5, sz2 - 1), (sx2 - 1, 5, sz2 - 1), M.WOOD)

    # ------------------------------------------------------------------
    # 11. Weeping willows around the park (插柳 custom).
    # ------------------------------------------------------------------
    for i, (wx, wz) in enumerate(
        [(6995, 6690), (7050, 6500), (7250, 6500), (7310, 6690), (7290, 6780), (7010, 6790)]
    ):
        _willow(fills, str(i + 1), wx, wz)

    # ------------------------------------------------------------------
    # 12. Scattered paper money and puddles from the drizzling rain.
    # ------------------------------------------------------------------
    for i, (px, pz) in enumerate(PAPER_MONEY):
        add_fill(fills, f"hanshi paper money {i}", (px, 5, pz), (px, 5, pz), M.YELLOW_WOOL)
    for i, (ax, az, bx, bz) in enumerate(PUDDLES):
        add_fill(fills, f"hanshi rain puddle {i}", (ax, GROUND_TOP, az), (bx, GROUND_TOP, bz), M.WATER)

    # Hard site-rule check: plot bounds + spirit way / farm belt clearance.
    _check_bounds(fills)


def main() -> None:
    run_builder(build_hanshi_qingming_3d, "hanshi_qingming_3d")


if __name__ == "__main__":
    main()
