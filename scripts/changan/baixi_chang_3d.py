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
    run_builder,
)


"""
Baixi Chang 3D (百戏场·庙会杂技地) - the temple-fair variety-show ground
of Tang Chang'an, where acrobats performed zaishan pole-balancing (顶竿),
somersaults (筋斗), wrestling (角抵) and magic tricks (幻术) before
crowds of ten thousand, just outside the south gate of the East Market.

Location in Chang'an city local coordinates:
    Plot: x 4300..4600, z 3150..3450 (strict bounds - nothing may leave
    them), immediately south of the East Market (market zone ends at
    z 3100; the banner gate at z 3162 faces the market's south mouth).
    Avoidance checked against neighbours: the polo field of
    entertainment_venues.py (x 1800..2600, z 2200..3000) and the whole
    polo stadium of polo_stadium_3d.py (field x 5000..5800, stands and
    pavilion x 4930..5824, z 4762..5638) both lie far clear of this
    plot; Leyou Park (x 5000..5800, z 4800..5600) likewise. Only
    ordinary ward housing overlaps the site and is safe to overwrite -
    the build clears y5..14 before grading. Ground is graded to stone
    y0..1 + grass y2..4 (walking surface on top of y4); every main
    structure rises from y5.

Distinctive features (Tang temple-fair acrobatics):
    - Two great performance tents (24x18, 百戏大棚) with red/yellow
      striped patchwork cloth roofs, four corner lamp masts (sea-lantern
      clusters under red wool shades with gilded tips), interior
      red-carpet performance rings fenced in dark oak, hanging lamps,
      drums and prop chests
    - Pole-balancing frame (戴竿): a 15-high twin-log mast on crossed
      base beams, diagonal braces and stone anchors, carrying a top
      crossbar on which two quartz acrobat figures balance with open
      arms - one belly-against-mast pose - under a red streamer
    - Wrestling ring (角抵台): a 10x10 rammed-earth platform (y4..6)
      with granite trim, four corner flag poles, two wrestlers locked
      in a clinch (quartz bodies, red vs blue wool grips, horse stance)
      and stone spectator benches on all four sides
    - Magician's black dome tent (幻术帐) with a purple apex, paired
      sea-lantern door lights and a purple "huan" shop banner
    - Six timber spectator sheds (三面看棚) with green thatch roofs,
      log frames and two rows of spruce benches
    - Four peddler shoulder-pole loads (fence yokes, wood boxes, wool
      goods piles, purple pennants) plus a candied-hawthorn rack of
      iron bars strung with three red berry strings
    - Festival banner gate with twin columns, a heavy lintel and five
      coloured banners (red/yellow/blue/green/white), a gong-and-drum
      stand (gold gong, red wool drum), wool bunting strung between
      boundary lamp posts, and one old locust tree
"""

# ---------------------------------------------------------------------------
# Site: open show ground south of the East Market (strict bounds).
# ---------------------------------------------------------------------------
SITE_X1, SITE_X2 = 4300, 4600
SITE_Z1, SITE_Z2 = 3150, 3450

# Direct-string blocks and the one wool colour lib.py lacks.
PURPLE_WOOL = "minecraft:purple_wool"
LOG_X = "minecraft:dark_oak_log[axis=x]"
LOG_Z = "minecraft:dark_oak_log[axis=z]"

# Banner gate (百戏幡门) facing the East Market south mouth.
GATE_CX, GATE_Z = 4450, 3162

# Great performance tents (24x18 each), flanking the central axis.
TENT_A_X, TENT_B_X, TENT_Z = 4403, 4473, 3291

# Pole-balancing frame (戴竿): 2x2 mast foot at its north-west corner.
MAST_X1, MAST_Z1 = 4407, 3229

# Wrestling ring (角抵台) 10x10 in the west meadow.
RING_X1, RING_Z1 = 4326, 3290

# Magician's dome tent (幻术帐) in the east meadow.
MAGIC_CX, MAGIC_CZ = 4550, 3300

# Six spectator sheds: (tag, x1, z1, long axis, open side).
SHEDS = (
    ("w1", 4312, 3200, "z", "e"),
    ("w2", 4312, 3380, "z", "e"),
    ("e1", 4583, 3200, "z", "w"),
    ("e2", 4583, 3380, "z", "w"),
    ("s1", 4384, 3432, "x", "n"),
    ("s2", 4503, 3432, "x", "n"),
)

# Peddler shoulder-pole loads and the candied-hawthorn rack.
PEDDLERS = ((4425, 3195), (4475, 3195), (4425, 3355), (4475, 3355))
SUGAR_X, SUGAR_Z = 4430, 3174

# Boundary lamp posts (pairs carry wool bunting).
LAMPS_N = ((4420, 3280), (4480, 3280))
LAMPS_S = ((4392, 3400), (4508, 3400))
LAMPS_EDGE = ((4392, 3200), (4508, 3200), (4360, 3260), (4540, 3340))

# Old locust tree in the south-west meadow.
TREE_X, TREE_Z = 4345, 3395


# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------
def _big_tent(fills: list[Fill], tag: str, x1: int, z1: int, door_dx: int) -> None:
    """One 24x18 performance tent: patchwork roof, corner lamp masts,
    a fenced red-carpet ring, hanging lamps, drum and prop chest."""
    x2, z2 = x1 + 23, z1 + 17
    # Plank floor over the plaza.
    add_fill(fills, f"baixi tent {tag} floor", (x1, 4, z1), (x2, 4, z2), M.WOOD)
    # Mid wall posts carrying the cloth roof.
    for px in (x1 + 8, x1 + 16):
        add_fill(fills, f"baixi tent {tag} post n {px}", (px, 5, z1), (px, 11, z1), M.LOG)
        add_fill(fills, f"baixi tent {tag} post s {px}", (px, 5, z2), (px, 11, z2), M.LOG)
    add_fill(fills, f"baixi tent {tag} post w", (x1, 5, z1 + 8), (x1, 11, z1 + 8), M.LOG)
    add_fill(fills, f"baixi tent {tag} post e", (x2, 5, z1 + 8), (x2, 11, z1 + 8), M.LOG)
    # Striped red/yellow patchwork cloth roof, one block of overhang.
    rx1, rx2, rz1, rz2 = x1 - 1, x2 + 1, z1 - 1, z2 + 1
    stripe, si = rx1, 0
    while stripe <= rx2:
        send = min(rx2, stripe + 2)
        wool = M.RED_WOOL if si % 2 == 0 else M.YELLOW_WOOL
        add_fill(fills, f"baixi tent {tag} roof stripe {si}", (stripe, 12, rz1), (send, 12, rz2), wool)
        si += 1
        stripe = send + 1
    # Four corner lamp masts piercing the roof: pole, lantern cluster,
    # red shade, dark cap and a gilded tip.
    for px in (x1, x2):
        for pz in (z1, z2):
            corner = "nw" if px == x1 and pz == z1 else "ne" if px == x2 and pz == z1 else "sw" if px == x1 else "se"
            add_fill(fills, f"baixi tent {tag} mast {corner}", (px, 5, pz), (px, 15, pz), M.LOG)
            add_fill(fills, f"baixi tent {tag} mast glow {corner}", (px - 1, 16, pz - 1), (px + 1, 17, pz + 1), M.SEA_LANTERN)
            add_fill(fills, f"baixi tent {tag} mast shade {corner}", (px - 2, 18, pz - 2), (px + 2, 18, pz + 2), M.RED_WOOL)
            add_fill(fills, f"baixi tent {tag} mast cap {corner}", (px - 1, 19, pz - 1), (px + 1, 19, pz + 1), M.DARK)
            add_fill(fills, f"baixi tent {tag} mast tip {corner}", (px, 20, pz), (px, 20, pz), M.GOLD)
    # Interior red-carpet performance ring with a fence and a north gap.
    cx1, cx2, cz1, cz2 = x1 + 5, x1 + 18, z1 + 5, z1 + 12
    add_fill(fills, f"baixi tent {tag} carpet", (cx1, 5, cz1), (cx2, 5, cz2), M.RED_WOOL)
    add_outline(fills, f"baixi tent {tag} ring fence", cx1, cz1, cx2, cz2, 6, 6, M.FENCE, thickness=1)
    add_fill(fills, f"baixi tent {tag} ring gap", (x1 + 11, 6, cz1), (x1 + 12, 6, cz1), M.AIR)
    # Hanging lamps under the roof.
    add_fill(fills, f"baixi tent {tag} hang lamp w", (x1 + 8, 11, z1 + 8), (x1 + 9, 11, z1 + 9), M.SEA_LANTERN)
    add_fill(fills, f"baixi tent {tag} hang lamp e", (x1 + 14, 11, z1 + 8), (x1 + 15, 11, z1 + 9), M.SEA_LANTERN)
    # North entrance (toward the axis) with a yellow door valance.
    add_fill(fills, f"baixi tent {tag} door", (x1 + door_dx, 5, z1), (x1 + door_dx + 3, 9, z1), M.AIR)
    add_fill(fills, f"baixi tent {tag} valance", (x1 + door_dx, 10, z1), (x1 + door_dx + 3, 11, z1), M.YELLOW_WOOL)
    # Props: a drum and a prop chest inside.
    add_fill(fills, f"baixi tent {tag} drum", (x1 + 2, 5, z1 + 3), (x1 + 3, 6, z1 + 4), M.RED_WOOL)
    add_fill(fills, f"baixi tent {tag} drum skin", (x1 + 2, 7, z1 + 3), (x1 + 3, 7, z1 + 4), M.WHITE_WOOL)
    add_fill(fills, f"baixi tent {tag} chest", (x1 + 20, 5, z1 + 3), (x1 + 22, 6, z1 + 5), M.WOOD)


def _spectator_shed(fills: list[Fill], tag: str, x1: int, z1: int, long_axis: str, open_dir: str) -> None:
    """One 14x6 timber viewing shed: log frame, thatch roof, two bench
    rows, open toward `open_dir`, railed at the back."""
    length, depth = 14, 6
    if long_axis == "z":
        x2, z2 = x1 + depth - 1, z1 + length - 1
        back_x = x1 if open_dir == "e" else x2
        front_x = x2 if open_dir == "e" else x1
        add_fill(fills, f"baixi shed {tag} floor", (x1, 4, z1), (x2, 4, z2), M.WOOD)
        for pz in (z1, z1 + 6, z2):
            add_fill(fills, f"baixi shed {tag} post back {pz}", (back_x, 5, pz), (back_x, 9, pz), M.LOG)
            add_fill(fills, f"baixi shed {tag} post front {pz}", (front_x, 5, pz), (front_x, 9, pz), M.LOG)
        add_fill(fills, f"baixi shed {tag} roof", (x1 - 2, 10, z1 - 2), (x2 + 2, 10, z2 + 2), M.GREEN_WOOL)
        add_fill(fills, f"baixi shed {tag} ridge", (x1 + depth // 2, 11, z1), (x1 + depth // 2, 11, z2), LOG_Z)
        for bx in (x1 + 2, x1 + 4):
            add_fill(fills, f"baixi shed {tag} bench {bx}", (bx, 5, z1), (bx, 5, z2), M.SPRUCE)
        add_fill(fills, f"baixi shed {tag} back rail", (back_x, 6, z1), (back_x, 7, z2), M.FENCE)
    else:
        x2, z2 = x1 + length - 1, z1 + depth - 1
        back_z = z1 if open_dir == "s" else z2
        front_z = z2 if open_dir == "s" else z1
        add_fill(fills, f"baixi shed {tag} floor", (x1, 4, z1), (x2, 4, z2), M.WOOD)
        for px in (x1, x1 + 6, x2):
            add_fill(fills, f"baixi shed {tag} post back {px}", (px, 5, back_z), (px, 9, back_z), M.LOG)
            add_fill(fills, f"baixi shed {tag} post front {px}", (px, 5, front_z), (px, 9, front_z), M.LOG)
        add_fill(fills, f"baixi shed {tag} roof", (x1 - 2, 10, z1 - 2), (x2 + 2, 10, z2 + 2), M.GREEN_WOOL)
        add_fill(fills, f"baixi shed {tag} ridge", (x1, 11, z1 + depth // 2), (x2, 11, z1 + depth // 2), LOG_X)
        for bz in (z1 + 2, z1 + 4):
            add_fill(fills, f"baixi shed {tag} bench {bz}", (x1, 5, bz), (x2, 5, bz), M.SPRUCE)
        add_fill(fills, f"baixi shed {tag} back rail", (x1, 6, back_z), (x2, 7, back_z), M.FENCE)


def _peddler_load(fills: list[Fill], tag: str, cx: int, cz: int) -> None:
    """One itinerant peddler's shoulder-pole stand: fence yoke on two
    posts, wood boxes at both ends, wool goods piles and a pennant."""
    add_fill(fills, f"baixi peddler {tag} post w", (cx - 3, 5, cz), (cx - 3, 6, cz), M.LOG)
    add_fill(fills, f"baixi peddler {tag} post e", (cx + 3, 5, cz), (cx + 3, 6, cz), M.LOG)
    add_fill(fills, f"baixi peddler {tag} yoke", (cx - 4, 7, cz), (cx + 4, 7, cz), M.FENCE)
    add_fill(fills, f"baixi peddler {tag} box w", (cx - 6, 5, cz - 1), (cx - 4, 6, cz + 1), M.WOOD)
    add_fill(fills, f"baixi peddler {tag} box e", (cx + 4, 5, cz - 1), (cx + 6, 6, cz + 1), M.WOOD)
    add_fill(fills, f"baixi peddler {tag} goods w", (cx - 6, 7, cz - 1), (cx - 5, 7, cz), M.YELLOW_WOOL)
    add_fill(fills, f"baixi peddler {tag} goods e", (cx + 5, 7, cz), (cx + 6, 7, cz + 1), M.RED_WOOL)
    add_fill(fills, f"baixi peddler {tag} pennant", (cx, 8, cz), (cx, 9, cz), PURPLE_WOOL)


def _lamp_post(fills: list[Fill], tag: str, x: int, z: int) -> None:
    """Field lamp post: log mast, sea-lantern head, red wool shade."""
    add_fill(fills, f"baixi lamp {tag} post", (x, 5, z), (x, 10, z), M.LOG)
    add_fill(fills, f"baixi lamp {tag} glow", (x - 1, 11, z - 1), (x + 1, 11, z + 1), M.SEA_LANTERN)
    add_fill(fills, f"baixi lamp {tag} shade", (x - 2, 12, z - 2), (x + 2, 12, z + 2), M.RED_WOOL)


def _bunting(fills: list[Fill], tag: str, y: int, z: int, x1: int, x2: int) -> None:
    """Four coloured wool bunting spans strung between two lamp posts."""
    span = x2 - x1
    colors = (M.RED_WOOL, M.YELLOW_WOOL, M.BLUE_WOOL, M.GREEN_WOOL)
    for bi in range(4):
        sx1 = x1 + 1 + (span - 2) * bi // 4
        sx2 = x1 + 1 + (span - 2) * (bi + 1) // 4
        add_fill(fills, f"baixi bunting {tag} {bi}", (sx1, y, z), (sx2, y, z), colors[bi])


# ---------------------------------------------------------------------------
# Main builder.
# ---------------------------------------------------------------------------
def build_baixi_chang_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site grading: clear the old ward housing, lay the meadow and
    #    the central andesite plaza with paths, carpet and aprons.
    # ------------------------------------------------------------------
    add_fill(fills, "baixi clear site", (SITE_X1, 5, SITE_Z1), (SITE_X2, 14, SITE_Z2), M.AIR)
    add_fill(fills, "baixi ground stone", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "baixi ground soil", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)
    add_fill(fills, "baixi ground turf", (SITE_X1, 4, SITE_Z1), (SITE_X2, 4, SITE_Z2), M.GRASS)
    add_fill(fills, "baixi plaza pave", (4390, 4, 3205), (4510, 4, 3395), M.ANDESITE)
    add_fill(fills, "baixi gate approach", (4436, 4, SITE_Z1), (4464, 4, 3204), M.SMOOTH)
    add_fill(fills, "baixi axis carpet", (4444, 4, GATE_Z), (4456, 4, 3310), M.RED_WOOL)
    add_fill(fills, "baixi pole apron", (4399, 4, 3221), (4417, 4, 3239), M.SMOOTH)
    add_fill(fills, "baixi ring apron", (4322, 4, 3286), (4338, 4, 3302), M.SMOOTH)
    add_fill(fills, "baixi magic apron", (4541, 4, 3291), (4559, 4, 3309), M.SMOOTH)

    # ------------------------------------------------------------------
    # 2. Festival banner gate (百戏幡门): twin columns, heavy lintel,
    #    five coloured banners, plus the gong-and-drum stand beside it.
    # ------------------------------------------------------------------
    gx1, gx2 = GATE_CX - 12, GATE_CX + 12  # columns at 4438/4461
    add_fill(fills, "baixi gate base w", (gx1 - 1, 4, GATE_Z - 1), (gx1 + 2, 4, GATE_Z + 2), M.STONE)
    add_fill(fills, "baixi gate base e", (gx2 - 2, 4, GATE_Z - 1), (gx2 + 1, 4, GATE_Z + 2), M.STONE)
    add_fill(fills, "baixi gate column w", (gx1, 5, GATE_Z), (gx1 + 1, 16, GATE_Z + 1), M.LOG)
    add_fill(fills, "baixi gate column e", (gx2 - 1, 5, GATE_Z), (gx2, 16, GATE_Z + 1), M.LOG)
    add_fill(fills, "baixi gate passage", (gx1 + 2, 5, GATE_Z), (gx2 - 2, 15, GATE_Z + 1), M.AIR)
    add_fill(fills, "baixi gate lintel", (gx1 - 3, 16, GATE_Z), (gx2 + 3, 17, GATE_Z + 1), M.LOG)
    add_fill(fills, "baixi gate lintel cap", (gx1 - 1, 18, GATE_Z - 1), (gx2 + 1, 18, GATE_Z + 2), M.DARK)
    banners = (
        (4441, 4443, M.RED_WOOL),
        (4445, 4447, M.YELLOW_WOOL),
        (4449, 4451, M.BLUE_WOOL),
        (4453, 4455, M.GREEN_WOOL),
        (4457, 4459, M.WHITE_WOOL),
    )
    for bi, (bx1, bx2, wool) in enumerate(banners):
        add_fill(fills, f"baixi gate banner {bi}", (bx1, 11, GATE_Z), (bx2, 15, GATE_Z + 1), wool)
    add_fill(fills, "baixi gate lamp w", (gx1, 19, GATE_Z), (gx1 + 1, 19, GATE_Z + 1), M.SEA_LANTERN)
    add_fill(fills, "baixi gate lamp e", (gx2 - 1, 19, GATE_Z), (gx2, 19, GATE_Z + 1), M.SEA_LANTERN)
    # Gong frame west of the gate: posts, crossbar, hanging gold gong.
    add_fill(fills, "baixi gong post w", (4408, 5, 3166), (4408, 11, 3166), M.LOG)
    add_fill(fills, "baixi gong post e", (4416, 5, 3166), (4416, 11, 3166), M.LOG)
    add_fill(fills, "baixi gong bar", (4407, 11, 3166), (4417, 12, 3166), LOG_X)
    add_fill(fills, "baixi gong hanger", (4412, 9, 3166), (4412, 10, 3166), M.IRON_BARS)
    add_fill(fills, "baixi gong disc", (4411, 7, 3166), (4413, 8, 3166), M.GOLD)
    # Festival drum east of the gate: wood pad, red wool barrel, skin.
    add_fill(fills, "baixi drum pad", (4424, 4, 3174), (4426, 4, 3176), M.LOG)
    add_fill(fills, "baixi drum body", (4424, 5, 3174), (4426, 6, 3176), M.RED_WOOL)
    add_fill(fills, "baixi drum skin", (4424, 7, 3174), (4426, 7, 3176), M.WHITE_WOOL)

    # ------------------------------------------------------------------
    # 3. Central performance tents (百戏大棚) flanking the axis.
    # ------------------------------------------------------------------
    _big_tent(fills, "west", TENT_A_X, TENT_Z, door_dx=19)  # door toward the central gap
    _big_tent(fills, "east", TENT_B_X, TENT_Z, door_dx=1)

    # ------------------------------------------------------------------
    # 4. Pole-balancing frame (戴竿): crossed base beams and braces on
    #    stone anchors, a 15-high twin-log mast, top crossbar with two
    #    balancing acrobat figures, red streamer on a gilded tip.
    # ------------------------------------------------------------------
    for ai, (ax, az) in enumerate(((4402, 3224), (4412, 3224), (4402, 3234), (4412, 3234))):
        add_fill(fills, f"baixi mast anchor {ai}", (ax, 5, az), (ax + 1, 5, az + 1), M.GRANITE)
    add_fill(fills, "baixi mast beam x", (4403, 5, MAST_Z1), (4412, 5, MAST_Z1), LOG_X)
    add_fill(fills, "baixi mast beam z", (MAST_X1, 5, 3225), (MAST_X1, 5, 3234), LOG_Z)
    for bi, (bx, bz) in enumerate(((4405, 3227), (4409, 3227), (4405, 3231), (4409, 3231))):
        add_fill(fills, f"baixi mast brace {bi}", (bx, 6, bz), (bx + 1, 7, bz + 1), M.LOG)
    add_fill(fills, "baixi mast pole", (MAST_X1, 5, MAST_Z1), (MAST_X1 + 1, 19, MAST_Z1 + 1), M.LOG)
    add_fill(fills, "baixi mast crossbar", (4398, 18, MAST_Z1), (4417, 19, MAST_Z1 + 1), LOG_X)
    # Acrobat A at the bar's west end: open arms, on tiptoe.
    add_fill(fills, "baixi walker a legs", (4401, 20, MAST_Z1), (4401, 20, MAST_Z1), M.QUARTZ)
    add_fill(fills, "baixi walker a torso", (4401, 21, MAST_Z1), (4401, 22, MAST_Z1), M.QUARTZ)
    add_fill(fills, "baixi walker a head", (4401, 23, MAST_Z1), (4401, 23, MAST_Z1), M.QUARTZ)
    add_fill(fills, "baixi walker a arm w", (4399, 22, MAST_Z1), (4400, 22, MAST_Z1), M.QUARTZ)
    add_fill(fills, "baixi walker a arm e", (4402, 22, MAST_Z1), (4403, 22, MAST_Z1), M.QUARTZ)
    # Acrobat B hugging the mast: belly against the pole, one arm out.
    add_fill(fills, "baixi walker b legs", (4410, 20, MAST_Z1), (4410, 20, MAST_Z1), M.QUARTZ)
    add_fill(fills, "baixi walker b torso", (4410, 21, MAST_Z1), (4410, 22, MAST_Z1), M.QUARTZ)
    add_fill(fills, "baixi walker b head", (4410, 23, MAST_Z1), (4410, 23, MAST_Z1), M.QUARTZ)
    add_fill(fills, "baixi walker b arm grip", (4409, 22, MAST_Z1), (4409, 22, MAST_Z1), M.QUARTZ)
    add_fill(fills, "baixi walker b arm out", (4411, 22, MAST_Z1), (4412, 22, MAST_Z1), M.QUARTZ)
    add_fill(fills, "baixi mast tip", (MAST_X1, 20, MAST_Z1), (MAST_X1 + 1, 21, MAST_Z1 + 1), M.GOLD)
    add_fill(fills, "baixi mast streamer", (4405, 20, MAST_Z1), (4406, 23, MAST_Z1), M.RED_WOOL)
    # Crowd fence around the mast circle, open on the south side.
    add_outline(fills, "baixi mast fence", 4399, 3221, 4417, 3239, 5, 5, M.FENCE, thickness=1)
    add_fill(fills, "baixi mast fence gap", (MAST_X1, 5, 3239), (MAST_X1 + 2, 5, 3239), M.AIR)

    # ------------------------------------------------------------------
    # 5. Wrestling ring (角抵台): rammed-earth platform, granite trim,
    #    corner flags, two grapplers, four stone bench rows.
    # ------------------------------------------------------------------
    rx1, rz1 = RING_X1, RING_Z1
    rx2, rz2 = RING_X1 + 9, RING_Z1 + 9
    add_fill(fills, "baixi ring platform", (rx1, 4, rz1), (rx2, 6, rz2), M.WHITE_TERRACOTTA)
    add_outline(fills, "baixi ring trim", rx1, rz1, rx2, rz2, 6, 6, M.GRANITE, thickness=1)
    add_fill(fills, "baixi ring step up", (4329, 5, rz2 + 1), (4332, 5, rz2 + 1), M.GRANITE)
    add_fill(fills, "baixi ring step low", (4329, 4, rz2 + 2), (4332, 4, rz2 + 2), M.GRANITE)
    for fi, (fx, fz, flag_wool, fz1, fz2) in enumerate((
        (rx1, rz1, M.RED_WOOL, 3288, 3289),
        (rx2, rz1, M.YELLOW_WOOL, 3288, 3289),
        (rx1, rz2, M.GREEN_WOOL, 3300, 3301),
        (rx2, rz2, M.BLUE_WOOL, 3300, 3301),
    )):  # corner flag poles with coloured flags
        add_fill(fills, f"baixi ring flag pole {fi}", (fx, 7, fz), (fx, 12, fz), M.FENCE)
        add_fill(fills, f"baixi ring flag cloth {fi}", (fx, 10, fz1), (fx, 12, fz2), flag_wool)
    # Red wrestler (west) and blue wrestler (east) locked in a clinch:
    # horse-stance legs, quartz torsos and heads, wool gripping arms.
    add_fill(fills, "baixi wrestler red leg n", (4329, 7, 3294), (4329, 7, 3294), M.RED_WOOL)
    add_fill(fills, "baixi wrestler red leg s", (4329, 7, 3296), (4329, 7, 3296), M.RED_WOOL)
    add_fill(fills, "baixi wrestler red torso", (4329, 8, 3295), (4329, 8, 3295), M.QUARTZ)
    add_fill(fills, "baixi wrestler red arm low", (4330, 8, 3295), (4330, 8, 3295), M.RED_WOOL)
    add_fill(fills, "baixi wrestler red arm high", (4330, 9, 3295), (4330, 9, 3295), M.RED_WOOL)
    add_fill(fills, "baixi wrestler red head", (4329, 9, 3295), (4329, 9, 3295), M.QUARTZ)
    add_fill(fills, "baixi wrestler blue leg n", (4332, 7, 3294), (4332, 7, 3294), M.BLUE_WOOL)
    add_fill(fills, "baixi wrestler blue leg s", (4332, 7, 3296), (4332, 7, 3296), M.BLUE_WOOL)
    add_fill(fills, "baixi wrestler blue torso", (4332, 8, 3295), (4332, 8, 3295), M.QUARTZ)
    add_fill(fills, "baixi wrestler blue arm low", (4331, 8, 3295), (4331, 8, 3295), M.BLUE_WOOL)
    add_fill(fills, "baixi wrestler blue arm high", (4331, 9, 3295), (4331, 9, 3295), M.BLUE_WOOL)
    add_fill(fills, "baixi wrestler blue head", (4332, 9, 3295), (4332, 9, 3295), M.QUARTZ)
    # Stone spectator benches on the four sides of the platform.
    add_fill(fills, "baixi ring bench n", (4327, 5, 3286), (4334, 5, 3287), M.STONE)
    add_fill(fills, "baixi ring bench s", (4327, 5, 3303), (4334, 5, 3304), M.STONE)
    add_fill(fills, "baixi ring bench w", (4322, 5, 3289), (4323, 5, 3301), M.STONE)
    add_fill(fills, "baixi ring bench e", (4338, 5, 3289), (4339, 5, 3301), M.STONE)

    # ------------------------------------------------------------------
    # 6. Magician's black dome tent (幻术帐) with purple apex, door
    #    lanterns and the purple "huan" banner.
    # ------------------------------------------------------------------
    mx, mz = MAGIC_CX, MAGIC_CZ
    add_outline(fills, "baixi magic dome wall", mx - 6, mz - 6, mx + 6, mz + 6, 5, 7, M.BLACK_WOOL, thickness=1)
    add_fill(fills, "baixi magic dome ring 1", (mx - 5, 8, mz - 5), (mx + 5, 8, mz + 5), M.BLACK_WOOL)
    add_fill(fills, "baixi magic dome ring 2", (mx - 4, 9, mz - 4), (mx + 4, 9, mz + 4), M.BLACK_WOOL)
    add_fill(fills, "baixi magic dome ring 3", (mx - 3, 10, mz - 3), (mx + 3, 10, mz + 3), M.BLACK_WOOL)
    add_fill(fills, "baixi magic dome ring 4", (mx - 2, 11, mz - 2), (mx + 2, 11, mz + 2), M.BLACK_WOOL)
    add_fill(fills, "baixi magic dome ring 5", (mx - 1, 12, mz - 1), (mx + 1, 12, mz + 1), M.BLACK_WOOL)
    add_fill(fills, "baixi magic dome apex", (mx, 13, mz), (mx, 13, mz), PURPLE_WOOL)
    add_fill(fills, "baixi magic door", (mx - 2, 5, mz + 6), (mx + 2, 7, mz + 6), M.AIR)
    add_fill(fills, "baixi magic door lamp w", (mx - 3, 5, mz + 7), (mx - 3, 5, mz + 7), M.SEA_LANTERN)
    add_fill(fills, "baixi magic door lamp e", (mx + 3, 5, mz + 7), (mx + 3, 5, mz + 7), M.SEA_LANTERN)
    add_fill(fills, "baixi magic banner pole", (mx + 4, 5, mz + 9), (mx + 4, 10, mz + 9), M.FENCE)
    add_fill(fills, "baixi magic banner cloth", (mx + 2, 7, mz + 9), (mx + 3, 10, mz + 9), PURPLE_WOOL)
    add_fill(fills, "baixi magic carpet", (mx - 2, 5, mz - 2), (mx + 2, 5, mz + 2), PURPLE_WOOL)
    add_fill(fills, "baixi magic pedestal", (mx, 5, mz), (mx, 5, mz), M.QUARTZ)
    add_fill(fills, "baixi magic crystal", (mx, 6, mz), (mx, 6, mz), M.SEA_LANTERN)

    # ------------------------------------------------------------------
    # 7. Six spectator sheds (三面看棚): two each on the west, east and
    #    south edges, thatch roofs and double bench rows.
    # ------------------------------------------------------------------
    for tag, sx, sz, axis, open_dir in SHEDS:
        _spectator_shed(fills, tag, sx, sz, axis, open_dir)

    # ------------------------------------------------------------------
    # 8. Market edge: four peddler shoulder-pole loads and the
    #    candied-hawthorn rack by the gate.
    # ------------------------------------------------------------------
    for pi, (px, pz) in enumerate(PEDDLERS):
        _peddler_load(fills, f"{pi}", px, pz)
    add_fill(fills, "baixi sugar base", (SUGAR_X - 2, 4, SUGAR_Z - 1), (SUGAR_X + 2, 4, SUGAR_Z + 1), M.WOOD)
    add_fill(fills, "baixi sugar pole", (SUGAR_X, 5, SUGAR_Z), (SUGAR_X, 9, SUGAR_Z), M.IRON_BARS)
    add_fill(fills, "baixi sugar bar", (SUGAR_X - 3, 9, SUGAR_Z), (SUGAR_X + 3, 9, SUGAR_Z), M.IRON_BARS)
    for si, sx in enumerate((SUGAR_X - 2, SUGAR_X, SUGAR_X + 2)):
        add_fill(fills, f"baixi sugar string {si}", (sx, 6, SUGAR_Z), (sx, 8, SUGAR_Z), M.RED_WOOL)

    # ------------------------------------------------------------------
    # 9. Boundary lamp posts with wool bunting, and the old locust tree.
    # ------------------------------------------------------------------
    for li, (lx, lz) in enumerate(LAMPS_N + LAMPS_S + LAMPS_EDGE):
        _lamp_post(fills, f"{li}", lx, lz)
    _bunting(fills, "north", 13, 3280, 4420, 4480)
    _bunting(fills, "south", 13, 3400, 4392, 4508)
    add_fill(fills, "baixi flank pole w", (4430, 5, 3155), (4430, 11, 3155), M.LOG)
    add_fill(fills, "baixi flank flag w", (4428, 8, 3155), (4429, 10, 3155), M.RED_WOOL)
    add_fill(fills, "baixi flank pole e", (4470, 5, 3155), (4470, 11, 3155), M.LOG)
    add_fill(fills, "baixi flank flag e", (4471, 8, 3155), (4472, 10, 3155), M.YELLOW_WOOL)
    # Old locust tree: broad layered canopy, massive 2x2 trunk, branches.
    add_fill(fills, "baixi locust canopy low", (4339, 12, 3390), (4351, 13, 3400), M.LEAVES)
    add_fill(fills, "baixi locust canopy mid", (4338, 14, 3389), (4352, 15, 3401), M.LEAVES)
    add_fill(fills, "baixi locust canopy top", (4341, 16, 3392), (4349, 16, 3398), M.LEAVES)
    add_fill(fills, "baixi locust trunk", (TREE_X - 1, 5, TREE_Z - 1), (TREE_X, 14, TREE_Z), M.TREE_LOG)
    add_fill(fills, "baixi locust branch w", (4341, 12, 3395), (4343, 12, 3395), M.TREE_LOG)
    add_fill(fills, "baixi locust branch s", (4344, 12, 3396), (4344, 12, 3398), M.TREE_LOG)


def main() -> None:
    run_builder(build_baixi_chang_3d, "baixi_chang_3d")


if __name__ == "__main__":
    main()
