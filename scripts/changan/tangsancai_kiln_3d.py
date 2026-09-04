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
    add_outline,
    add_ridge_roof,
    run_builder,
)


"""
Tang Sancai Kiln Complex (唐三彩窑场) 3D module - an official/private pottery
kiln yard in the south-west corner of Chang'an, firing the famous three-colour
glazed wares (三彩) that were exported along the Silk Road.

Location in Chang'an city local coordinates:
    Site: city south-west corner block, x 100..420, z 3900..4200.
    Surroundings are ordinary ward housing (covered by design); the official
    ice cellars sit far east at x 4450+ and the Silk Road caravan camp lies
    far north-west at x -520..-100, z 2400..2700, so nothing conflicts.
    After grading: stone y0..1 + grass y2..3, walking surface y4; negative y
    is left untouched.

Distinctive features:
    - Graded terrace ringed by a low unfired-clay wall (坯墙) with four gaps
      as workyard openings, plus a timber gate frame on the north side
    - Three hemispherical mantou kilns (馒头窑, diameter ~11): scanline-disc
      red-terracotta + smooth-stone dome shells shrinking layer by layer,
      arched fire mouths with red-wool ember / sea-lantern fire chambers and
      fire-screen walls, flank stoking holes, and tall 3x3 chimneys topped
      with three drifting white-wool smoke puffs
    - Drying yard: three long post-and-rail racks carrying ~15 unfired
      white-terracotta / smooth-stone blanks (素坯)
    - Glaze house: six glaze vats (green / light-blue / amber / white /
      plain water / pale-yellow wool under water as glaze slip) and a stone
      glaze-grinding roller
    - Sancai display shed: gabled exhibition hall with a blocky tri-colour
      Bactrian camel (~6 tall, white body with green/amber glaze patches),
      a red-brown sancai horse with green spots, and four small glazed
      bowls/vases on stands
    - Firewood yard: three log-and-hay stacks behind the kilns plus a mould
      workshop with a chest and wood concave moulds on racks
    - Kiln-god shrine (窑神龛) beside the gate: dark base, quartz-pillar
      stele, gold cap and a small incense-burner stand in front
    - Two FENCE+WOOD hand carts and four lantern posts along the path
"""

# ---------------------------------------------------------------------------
# Site bounds (strict): city south-west corner.
# ---------------------------------------------------------------------------
SITE_X1, SITE_X2 = 100, 420
SITE_Z1, SITE_Z2 = 3900, 4200

# Perimeter clay wall + gate.
WALL_Y1, WALL_Y2 = 4, 5
GATE_X1, GATE_X2 = 205, 235  # gap in the north wall

# Three mantou kilns in a row, mouths facing south to the drying yard.
KILN_BASE_Y = 4
KILN_APEX_Y = 10
CHIMNEY_TOP_Y = 18  # kiln ground y4 + 14
KILN_CENTERS = ((165, 3955), (260, 3955), (355, 3955))

# Drying racks (three rows), posts + one rail each.
RACK_ROWS = (4035, 4065, 4095)
RACK_X1, RACK_X2 = 150, 350
RACK_POSTS = (150, 250, 350)
RACK_BLANKS = (160, 200, 240, 280, 320)

# Glaze house.
GH_X1, GH_Z1 = 108, 4040
GH_X2, GH_Z2 = 146, 4082

# Mould workshop (north-east, behind the kilns).
MW_X1, MW_Z1 = 378, 3926
MW_X2, MW_Z2 = 414, 3962

# Sancai display shed.
SHED_X1, SHED_Z1 = 200, 4130
SHED_X2, SHED_Z2 = 330, 4168
SHED_ROOF_Y = 12

# Kiln-god shrine centre (east of the north gate).
SHRINE_CX, SHRINE_CZ = 246, 3906

# Extra palette for the kiln yard.
HAY = "minecraft:hay_block"
CHEST = "minecraft:chest"
QUARTZ_PILLAR = "minecraft:quartz_pillar"
GRAY_CONCRETE = "minecraft:gray_concrete"
LIGHT_BLUE_WOOL = "minecraft:light_blue_wool"
ORANGE_WOOL = "minecraft:orange_wool"
LOG_X = "minecraft:dark_oak_log[axis=x]"


# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------
def _disc_rows(
    fills: list[Fill],
    label: str,
    cx: int,
    cz: int,
    y1: int,
    y2: int,
    r: int,
    block: str,
) -> None:
    """Solid scanline disc (or disc prism y1..y2) of radius r: one fill per
    z-row, width from the circle equation. Used to stack kiln dome layers."""
    for dz in range(-r, r + 1):
        half = int(math.sqrt(r * r - dz * dz))
        add_fill(
            fills,
            f"{label} row {dz}",
            (cx - half, y1, cz + dz),
            (cx + half, y2, cz + dz),
            block,
        )


def _kiln(fills: list[Fill], label: str, cx: int, cz: int) -> None:
    """One hemispherical mantou kiln (馒头窑), fire mouth facing south.

    Dome shell of scanline discs shrinking layer by layer (diameter ~11,
    RED_WALL + SMOOTH bands), arched fire mouth with ember/glow fire chamber
    and a fire-screen wall, two flank stoking holes, and a tall 3x3 chimney
    to ground+14 with three white-wool smoke puffs.
    """
    # Seating plinth and working apron in front of the mouth.
    add_fill(fills, f"{label} plinth", (cx - 6, 4, cz - 6), (cx + 6, 4, cz + 6), M.SMOOTH)
    add_fill(fills, f"{label} apron", (cx - 6, 4, cz + 7), (cx + 6, 4, cz + 12), M.SMOOTH)

    # Dome shell: smooth-stone base ring, red body, smooth band, red shoulder.
    _disc_rows(fills, f"{label} base ring", cx, cz, 4, 4, 5, M.SMOOTH)
    _disc_rows(fills, f"{label} body", cx, cz, 5, 7, 4, M.RED_WALL)
    _disc_rows(fills, f"{label} stone band", cx, cz, 8, 8, 3, M.SMOOTH)
    _disc_rows(fills, f"{label} shoulder", cx, cz, 9, 9, 2, M.RED_WALL)
    _disc_rows(fills, f"{label} cap", cx, cz, 10, 10, 1, M.RED_WALL)

    # Arched fire mouth punched through the south face.
    add_fill(fills, f"{label} mouth", (cx - 1, 5, cz + 3), (cx + 1, 6, cz + 5), M.AIR)
    add_fill(fills, f"{label} mouth arch", (cx, 7, cz + 3), (cx, 7, cz + 5), M.AIR)
    # Fire chamber: red-wool embers under a sea-lantern glow.
    add_fill(fills, f"{label} embers", (cx - 1, 5, cz + 1), (cx + 1, 5, cz + 2), M.RED_WOOL)
    add_fill(fills, f"{label} fire glow", (cx - 1, 6, cz + 1), (cx + 1, 6, cz + 2), M.SEA_LANTERN)
    # Fire-screen wall in front of the mouth with a central draught slot.
    add_fill(fills, f"{label} fire screen", (cx - 2, 5, cz + 8), (cx + 2, 6, cz + 8), M.RED_WALL)
    add_fill(fills, f"{label} screen slot", (cx, 5, cz + 8), (cx, 6, cz + 8), M.AIR)

    # Two stoking holes on the flanks (glowing plug below, opening above).
    for side, sx in (("w", -4), ("e", 4)):
        add_fill(fills, f"{label} stoke {side} plug", (cx + sx, 6, cz), (cx + sx, 6, cz), M.RED_WOOL)
        add_fill(fills, f"{label} stoke {side} hole", (cx + sx, 7, cz), (cx + sx, 7, cz), M.AIR)

    # Tall 3x3 chimney up to ground+14, then three white-wool smoke puffs.
    add_fill(fills, f"{label} chimney", (cx - 1, 8, cz - 1), (cx + 1, CHIMNEY_TOP_Y, cz + 1), M.RED_WALL)
    add_fill(fills, f"{label} smoke 1", (cx - 1, 19, cz - 1), (cx + 1, 19, cz + 1), M.WHITE_WOOL)
    add_fill(fills, f"{label} smoke 2", (cx, 21, cz), (cx + 1, 21, cz + 1), M.WHITE_WOOL)
    add_fill(fills, f"{label} smoke 3", (cx, 23, cz), (cx, 23, cz), M.WHITE_WOOL)


def _glaze_vat(fills: list[Fill], label: str, cx: int, cz: int, slip: str | None) -> None:
    """One glaze vat: 3x3 cobble ring, wool slip block under water (釉浆).
    slip=None gives a plain water vat."""
    add_outline(fills, f"{label} ring", cx - 1, cz - 1, cx + 1, cz + 1, 5, 6, M.COBBLE, thickness=1)
    if slip is None:
        add_fill(fills, f"{label} water low", (cx, 5, cz), (cx, 5, cz), M.WATER)
    else:
        add_fill(fills, f"{label} slip", (cx, 5, cz), (cx, 5, cz), slip)
    add_fill(fills, f"{label} water top", (cx, 6, cz), (cx, 6, cz), M.WATER)


def _hand_cart(fills: list[Fill], label: str, bx: int, bz: int, cargo: str | None) -> None:
    """FENCE+WOOD hand cart: plank bed, rear legs, front wheel, handles."""
    add_fill(fills, f"{label} bed", (bx, 5, bz), (bx + 2, 5, bz + 1), M.WOOD)
    add_fill(fills, f"{label} legs", (bx, 4, bz), (bx, 4, bz + 1), M.FENCE)
    add_fill(fills, f"{label} wheel", (bx + 3, 4, bz), (bx + 3, 5, bz), M.FENCE)
    add_fill(fills, f"{label} handles", (bx + 3, 6, bz), (bx + 4, 6, bz + 1), M.FENCE)
    if cargo is not None:
        add_fill(fills, f"{label} cargo", (bx + 1, 6, bz), (bx + 1, 6, bz + 1), cargo)


# ---------------------------------------------------------------------------
# Main builder.
# ---------------------------------------------------------------------------
def build_tangsancai_kiln_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site grading: clear leftovers, stone y0..1 + grass y2..3.
    # ------------------------------------------------------------------
    add_fill(fills, "kiln clear site", (SITE_X1, 4, SITE_Z1), (SITE_X2, 9, SITE_Z2), M.AIR)
    add_fill(fills, "kiln terrace stone", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "kiln terrace grass", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)

    # ------------------------------------------------------------------
    # 2. Low unfired-clay perimeter wall with four workyard gaps + gate.
    # ------------------------------------------------------------------
    add_outline(
        fills, "kiln boundary wall",
        SITE_X1, SITE_Z1, SITE_X2, SITE_Z2,
        WALL_Y1, WALL_Y2, M.WHITE_TERRACOTTA, thickness=1,
    )
    add_fill(fills, "kiln gate gap n", (GATE_X1, WALL_Y1, SITE_Z1), (GATE_X2, WALL_Y2, SITE_Z1), M.AIR)
    add_fill(fills, "kiln gap e", (SITE_X2, WALL_Y1, 4050), (SITE_X2, WALL_Y2, 4070), M.AIR)
    add_fill(fills, "kiln gap s", (240, WALL_Y1, SITE_Z2), (260, WALL_Y2, SITE_Z2), M.AIR)
    add_fill(fills, "kiln gap w", (SITE_X1, WALL_Y1, 3980), (SITE_X1, WALL_Y2, 3995), M.AIR)
    # Timber gate frame: two log posts and a plank lintel.
    add_fill(fills, "kiln gate post w", (GATE_X1, 5, SITE_Z1), (GATE_X1 + 1, 9, SITE_Z1), M.LOG)
    add_fill(fills, "kiln gate post e", (GATE_X2 - 1, 5, SITE_Z1), (GATE_X2, 9, SITE_Z1), M.LOG)
    add_fill(fills, "kiln gate lintel", (GATE_X1 - 1, 10, SITE_Z1), (GATE_X2 + 1, 10, SITE_Z1), M.WOOD)
    # Gravel path from the gate south through the yard to the shed.
    add_fill(fills, "kiln main path", (210, 4, SITE_Z1 + 1), (230, 4, SHED_Z1), M.ANDESITE)

    # ------------------------------------------------------------------
    # 3. Kiln-god shrine (窑神龛) beside the gate.
    # ------------------------------------------------------------------
    add_fill(fills, "kiln shrine base", (SHRINE_CX - 1, 5, SHRINE_CZ - 1), (SHRINE_CX + 1, 5, SHRINE_CZ + 1), M.DARK)
    add_fill(fills, "kiln shrine back", (SHRINE_CX - 1, 6, SHRINE_CZ - 2), (SHRINE_CX + 1, 9, SHRINE_CZ - 2), M.RED_WALL)
    add_fill(fills, "kiln shrine stele", (SHRINE_CX, 6, SHRINE_CZ), (SHRINE_CX, 8, SHRINE_CZ), QUARTZ_PILLAR)
    add_fill(fills, "kiln shrine cap", (SHRINE_CX, 9, SHRINE_CZ), (SHRINE_CX, 9, SHRINE_CZ), M.GOLD)
    add_fill(fills, "kiln burner seat", (SHRINE_CX, 5, SHRINE_CZ + 3), (SHRINE_CX, 5, SHRINE_CZ + 3), M.SMOOTH)
    add_fill(fills, "kiln burner pot", (SHRINE_CX, 6, SHRINE_CZ + 3), (SHRINE_CX, 6, SHRINE_CZ + 3), M.DARK)
    add_fill(fills, "kiln burner incense", (SHRINE_CX, 7, SHRINE_CZ + 3), (SHRINE_CX, 7, SHRINE_CZ + 3), M.LANTERN)

    # ------------------------------------------------------------------
    # 4. Three mantou kilns (馒头窑) in a row, mouths to the drying yard.
    # ------------------------------------------------------------------
    for i, (kx, kz) in enumerate(KILN_CENTERS):
        _kiln(fills, f"kiln furnace {i + 1}", kx, kz)

    # ------------------------------------------------------------------
    # 5. Firewood yard behind the kilns: three log stacks with hay kindling.
    # ------------------------------------------------------------------
    for i, (wx, wz) in enumerate(((165, 3916), (260, 3916), (355, 3916))):
        add_fill(fills, f"kiln woodpile {i} base", (wx, 4, wz), (wx + 3, 4, wz + 1), M.LOG)
        add_fill(fills, f"kiln woodpile {i} mid", (wx, 5, wz), (wx + 2, 5, wz), M.LOG)
        add_fill(fills, f"kiln woodpile {i} top", (wx, 6, wz), (wx + 1, 6, wz), M.LOG)
        add_fill(fills, f"kiln woodpile {i} hay", (wx + 3, 5, wz), (wx + 3, 6, wz), HAY)

    # ------------------------------------------------------------------
    # 6. Mould workshop (模具房): timber hut, chest, racks with wood
    #    concave moulds (凹模).
    # ------------------------------------------------------------------
    add_fill(fills, "kiln moulds plinth", (MW_X1, 4, MW_Z1), (MW_X2, 4, MW_Z2), M.SMOOTH)
    add_outline(fills, "kiln moulds walls", MW_X1, MW_Z1, MW_X2, MW_Z2, 5, 9, M.WOOD, thickness=1)
    add_fill(fills, "kiln moulds hollow", (MW_X1 + 1, 5, MW_Z1 + 1), (MW_X2 - 1, 9, MW_Z2 - 1), M.AIR)
    add_fill(fills, "kiln moulds roof", (MW_X1, 10, MW_Z1), (MW_X2, 10, MW_Z2), M.WOOD)
    add_fill(fills, "kiln moulds door", (394, 5, MW_Z2), (396, 7, MW_Z2), M.AIR)
    add_fill(fills, "kiln moulds window", (MW_X2, 6, 3938), (MW_X2, 7, 3942), M.AIR)
    add_fill(fills, "kiln moulds chest", (398, 5, 3930), (398, 5, 3930), CHEST)
    add_fill(fills, "kiln mould rack a", (390, 6, 3950), (393, 6, 3951), M.WOOD)
    add_fill(fills, "kiln mould rack b", (402, 6, 3950), (405, 6, 3951), M.WOOD)
    add_fill(fills, "kiln mould a1", (390, 7, 3950), (391, 7, 3950), M.WOOD)
    add_fill(fills, "kiln mould a2", (392, 7, 3950), (393, 7, 3950), M.WOOD)
    add_fill(fills, "kiln mould b1", (402, 7, 3950), (403, 7, 3950), M.WOOD)
    add_fill(fills, "kiln mould b2", (404, 7, 3950), (405, 7, 3950), M.WOOD)

    # ------------------------------------------------------------------
    # 7. Drying yard (晾坯场): three post-and-rail racks with blanks.
    # ------------------------------------------------------------------
    for i, rz in enumerate(RACK_ROWS):
        add_fill(fills, f"kiln rack {i} rail", (RACK_X1, 6, rz), (RACK_X2, 6, rz), LOG_X)
        for px in RACK_POSTS:
            add_fill(fills, f"kiln rack {i} post {px}", (px, 4, rz), (px, 5, rz), M.LOG)
        for j, bx in enumerate(RACK_BLANKS):
            blank = M.WHITE_TERRACOTTA if j % 2 == 0 else M.SMOOTH
            add_fill(fills, f"kiln rack {i} blank {j}", (bx, 7, rz), (bx + 1, 7, rz), blank)

    # ------------------------------------------------------------------
    # 8. Glaze house (釉料房): timber hut, six glaze vats, stone roller.
    # ------------------------------------------------------------------
    add_fill(fills, "kiln glaze plinth", (GH_X1, 4, GH_Z1), (GH_X2, 4, GH_Z2), M.SMOOTH)
    add_outline(fills, "kiln glaze walls", GH_X1, GH_Z1, GH_X2, GH_Z2, 5, 9, M.WOOD, thickness=1)
    add_fill(fills, "kiln glaze hollow", (GH_X1 + 1, 5, GH_Z1 + 1), (GH_X2 - 1, 9, GH_Z2 - 1), M.AIR)
    add_fill(fills, "kiln glaze roof", (GH_X1, 10, GH_Z1), (GH_X2, 10, GH_Z2), M.WOOD)
    add_fill(fills, "kiln glaze door", (GH_X2, 5, 4058), (GH_X2, 7, 4060), M.AIR)
    add_fill(fills, "kiln glaze window", (118, 6, GH_Z2), (124, 7, GH_Z2), M.AIR)
    # Vat array: green / light-blue / amber / white / plain water / pale yellow.
    _glaze_vat(fills, "kiln vat green", 116, 4052, M.GREEN_WOOL)
    _glaze_vat(fills, "kiln vat blue", 128, 4052, LIGHT_BLUE_WOOL)
    _glaze_vat(fills, "kiln vat amber", 140, 4052, ORANGE_WOOL)
    _glaze_vat(fills, "kiln vat white", 116, 4066, M.WHITE_WOOL)
    _glaze_vat(fills, "kiln vat plain", 128, 4066, None)
    _glaze_vat(fills, "kiln vat yellow", 140, 4066, M.YELLOW_WOOL)
    # Stone glaze-grinding roller (研釉石碾): bed, vertical wheel, axle.
    add_fill(fills, "kiln roller bed", (114, 5, 4074), (120, 5, 4076), M.ANDESITE)
    add_fill(fills, "kiln roller wheel", (117, 6, 4075), (117, 8, 4075), GRAY_CONCRETE)
    add_fill(fills, "kiln roller axle", (113, 6, 4075), (119, 6, 4075), LOG_X)

    # ------------------------------------------------------------------
    # 9. Sancai display shed (三彩成品棚): columns, gable roof, exhibits.
    # ------------------------------------------------------------------
    add_fill(fills, "kiln shed floor", (SHED_X1, 4, SHED_Z1), (SHED_X2, 4, SHED_Z2), M.SMOOTH)
    for i, (colx, colz) in enumerate(
        ((206, 4136), (265, 4136), (324, 4136), (206, 4162), (265, 4162), (324, 4162))
    ):
        add_fill(fills, f"kiln shed column {i}", (colx, 5, colz), (colx + 1, 11, colz + 1), M.LOG)
    add_ridge_roof(
        fills, "kiln shed roof",
        SHED_X1, SHED_Z1, SHED_X2, SHED_Z2,
        SHED_ROOF_Y, layers=3, ridge_axis="x",
    )
    # Display tables under the two animal sculptures.
    add_fill(fills, "kiln camel table", (214, 5, 4144), (247, 5, 4147), M.WOOD)
    add_fill(fills, "kiln horse table", (283, 5, 4144), (316, 5, 4147), M.WOOD)

    # Sancai Bactrian camel (三彩骆驼): white body, green/amber glaze patches.
    add_fill(fills, "kiln camel pedestal", (218, 6, 4144), (228, 6, 4146), M.DARK)
    for leg, (lx, lz) in enumerate(((226, 4144), (226, 4146), (219, 4144), (219, 4146))):
        add_fill(fills, f"kiln camel leg {leg}", (lx, 7, lz), (lx, 8, lz), M.WHITE_TERRACOTTA)
    add_fill(fills, "kiln camel body", (218, 9, 4144), (227, 10, 4146), M.WHITE_TERRACOTTA)
    add_fill(fills, "kiln camel glaze g1", (221, 10, 4144), (222, 10, 4145), M.GREEN_WOOL)
    add_fill(fills, "kiln camel glaze a1", (224, 9, 4145), (224, 9, 4146), ORANGE_WOOL)
    add_fill(fills, "kiln camel glaze g2", (219, 9, 4145), (219, 9, 4146), M.GREEN_WOOL)
    add_fill(fills, "kiln camel blanket", (222, 11, 4144), (223, 11, 4146), ORANGE_WOOL)
    add_fill(fills, "kiln camel hump f", (220, 11, 4145), (220, 11, 4145), M.WHITE_TERRACOTTA)
    add_fill(fills, "kiln camel hump r", (225, 11, 4145), (225, 11, 4145), M.WHITE_TERRACOTTA)
    add_fill(fills, "kiln camel hump f tip", (220, 12, 4145), (220, 12, 4145), ORANGE_WOOL)
    add_fill(fills, "kiln camel hump r tip", (225, 12, 4145), (225, 12, 4145), ORANGE_WOOL)
    add_fill(fills, "kiln camel neck 1", (228, 10, 4145), (228, 11, 4145), M.WHITE_TERRACOTTA)
    add_fill(fills, "kiln camel neck 2", (229, 11, 4145), (229, 12, 4145), M.WHITE_TERRACOTTA)
    add_fill(fills, "kiln camel head", (230, 12, 4144), (231, 13, 4146), M.WHITE_TERRACOTTA)
    add_fill(fills, "kiln camel ear n", (231, 14, 4144), (231, 14, 4144), ORANGE_WOOL)
    add_fill(fills, "kiln camel ear s", (231, 14, 4146), (231, 14, 4146), ORANGE_WOOL)
    add_fill(fills, "kiln camel tail", (217, 9, 4145), (217, 10, 4145), M.WHITE_TERRACOTTA)

    # Sancai horse (三彩马): red-brown body with green glaze spots.
    add_fill(fills, "kiln horse pedestal", (295, 6, 4144), (305, 6, 4146), M.DARK)
    for leg, (lx, lz) in enumerate(((297, 4144), (297, 4146), (304, 4144), (304, 4146))):
        add_fill(fills, f"kiln horse leg {leg}", (lx, 7, lz), (lx, 8, lz), M.RED_WALL)
    add_fill(fills, "kiln horse body", (296, 9, 4144), (305, 10, 4146), M.RED_WALL)
    add_fill(fills, "kiln horse spot 1", (300, 10, 4144), (301, 10, 4145), M.GREEN_WOOL)
    add_fill(fills, "kiln horse spot 2", (298, 9, 4145), (298, 9, 4146), M.GREEN_WOOL)
    add_fill(fills, "kiln horse blanket", (301, 11, 4144), (302, 11, 4146), M.GREEN_WOOL)
    add_fill(fills, "kiln horse neck", (295, 10, 4145), (295, 12, 4145), M.RED_WALL)
    add_fill(fills, "kiln horse head", (292, 11, 4144), (294, 12, 4146), M.RED_WALL)
    add_fill(fills, "kiln horse mane", (295, 13, 4144), (295, 13, 4146), M.WHITE_TERRACOTTA)
    add_fill(fills, "kiln horse ear n", (293, 13, 4144), (293, 13, 4144), M.WHITE_TERRACOTTA)
    add_fill(fills, "kiln horse ear s", (293, 13, 4146), (293, 13, 4146), M.WHITE_TERRACOTTA)
    add_fill(fills, "kiln horse tail", (306, 9, 4145), (306, 10, 4145), M.RED_WALL)

    # Four small glazed bowls/vases on stands (三彩碗/瓶).
    stands = (
        (255, 4137, M.GREEN_WOOL),
        (273, 4137, ORANGE_WOOL),
        (255, 4159, LIGHT_BLUE_WOOL),
        (273, 4159, M.YELLOW_WOOL),
    )
    for i, (sx, sz, glaze) in enumerate(stands):
        add_fill(fills, f"kiln vase stand {i}", (sx, 5, sz), (sx + 1, 5, sz + 1), M.WOOD)
        add_fill(fills, f"kiln vase body {i}", (sx, 6, sz), (sx, 6, sz), M.WHITE_TERRACOTTA)
        add_fill(fills, f"kiln vase glaze {i}", (sx, 7, sz), (sx, 7, sz), glaze)

    # ------------------------------------------------------------------
    # 10. Hand carts and lantern posts around the yard.
    # ------------------------------------------------------------------
    _hand_cart(fills, "kiln cart 1", 180, 4080, M.WHITE_TERRACOTTA)
    _hand_cart(fills, "kiln cart 2", 310, 4178, None)
    for i, (lx, lz) in enumerate(((204, 3920), (236, 4010), (140, 4100), (368, 4060))):
        add_fill(fills, f"kiln lamp post {i}", (lx, 4, lz), (lx, 6, lz), M.FENCE)
        add_fill(fills, f"kiln lamp light {i}", (lx, 7, lz), (lx, 7, lz), M.LANTERN)


def main() -> None:
    run_builder(build_tangsancai_kiln_3d, "tangsancai_kiln_3d")


if __name__ == "__main__":
    main()
