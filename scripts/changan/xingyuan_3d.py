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
    add_lantern_line,
    add_outline,
    add_pyramid_roof,
    add_ridge_roof,
    run_builder,
)


"""
Xingyuan Apricot Garden 3D (杏园·曲水流觞) - the famous apricot garden
beside Qujiang Pool where new jinshi graduates held the Flower-Seeking
Banquet (探花宴). "春风得意马蹄疾，一日看尽长安花" was written about
this garden.

Location in Chang'an city local coordinates:
    West of Qujiang Pool, east of the observatory: x 4620..4990,
    z 5350..5850.

Distinctive features:
    - An apricot orchard grid of pink cherry-leaf canopies in bloom
    - A winding "floating goblet" stream (曲水流觞): a serpentine water
      channel stepping down through the garden with pink wine cups
      drifting on it
    - The Goblet-Pavilion (流杯亭) at the stream head spring
    - A three-tier Flower-Seeking Banquet terrace (探花宴高台) with a
      banquet hall and eagle-eye view over the blossoms
    - A name-inscription stele corridor (进士题名碑廊) along the north
      wall, echoing the Yanta inscription custom
"""

X1, Z1 = 4620, 5350
X2, Z2 = 4990, 5850


def _apricot_tree(fills: list[Fill], label: str, x: int, z: int, y: int) -> None:
    """Blossoming apricot: cherry leaves over a dark trunk, pink rim."""
    add_fill(fills, f"{label} trunk", (x, y, z), (x, y + 5, z), M.LOG)
    add_fill(fills, f"{label} bloom", (x - 3, y + 4, z - 3), (x + 3, y + 7, z + 3), "minecraft:cherry_leaves")
    add_fill(fills, f"{label} crown", (x - 2, y + 8, z - 2), (x + 2, y + 9, z + 2), M.PINK_WOOL)


def _stele(fills: list[Fill], label: str, x: int, z: int, y: int) -> None:
    add_fill(fills, f"{label} base", (x - 2, y, z - 2), (x + 2, y, z + 2), M.DARK)
    add_fill(fills, f"{label} shaft", (x - 1, y + 1, z - 1), (x + 1, y + 6, z + 1), M.QUARTZ)
    add_fill(fills, f"{label} cap", (x - 2, y + 7, z - 2), (x + 2, y + 7, z + 2), M.GOLD)


def build_xingyuan_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Foundation and boundary wall with a south gate.
    # ------------------------------------------------------------------
    add_fill(fills, "xingyuan foundation", (X1, 0, Z1), (X2, 2, Z2), M.STONE)
    add_fill(fills, "xingyuan lawn", (X1, 3, Z1), (X2, 3, Z2), M.GRASS)
    add_fill(fills, "xingyuan wall s", (X1, 4, Z2 - 4), (X2, 9, Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "xingyuan wall w", (X1, 4, Z1), (X1 + 4, 9, Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "xingyuan wall e", (X2 - 4, 4, Z1), (X2, 9, Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "xingyuan wall n", (X1, 4, Z1), (X2, 9, Z1 + 4), M.WHITE_TERRACOTTA)
    add_fill(fills, "xingyuan coping", (X1, 10, Z1), (X2, 10, Z1 + 4), M.DARK)
    add_fill(fills, "xingyuan coping s", (X1, 10, Z2 - 4), (X2, 10, Z2), M.DARK)
    add_fill(fills, "xingyuan coping w", (X1, 10, Z1), (X1 + 4, 10, Z2), M.DARK)
    add_fill(fills, "xingyuan coping e", (X2 - 4, 10, Z1), (X2, 10, Z2), M.DARK)
    add_fill(fills, "xingyuan gate", (4780, 4, Z2 - 4), (4830, 9, Z2), M.AIR)
    add_fill(fills, "xingyuan gate rim", (4776, 4, Z2 - 5), (4834, 4, Z2 - 5), M.GOLD)
    add_fill(fills, "xingyuan gate landing", (4780, 3, Z2 + 1), (4830, 4, Z2 + 7), M.SMOOTH)

    # ------------------------------------------------------------------
    # 2. Winding floating-goblet stream (曲水流觞): serpentine channel
    #    stepping down from the northwest spring to a south pond.
    # ------------------------------------------------------------------
    channel = [
        (4680, 5430, 4780, 5442), (4780, 5430, 4792, 5520), (4690, 5508, 4792, 5520),
        (4690, 5508, 4702, 5600), (4702, 5588, 4830, 5600), (4818, 5600, 4830, 5700),
        (4830, 5688, 4900, 5700), (4888, 5700, 4900, 5770),
    ]
    for i, (cx1, cz1, cx2, cz2) in enumerate(channel):
        add_fill(fills, f"goblet stream bed {i}", (cx1, 3, cz1), (cx2, 3, cz2), M.SMOOTH)
        add_fill(fills, f"goblet stream water {i}", (cx1, 4, cz1), (cx2, 4, cz2), M.WATER)
        if cz2 - cz1 >= cx2 - cx1:  # runs north-south: rim the long x sides
            add_fill(fills, f"goblet stream rim w {i}", (cx1 - 1, 4, cz1), (cx1 - 1, 4, cz2), M.STONE)
            add_fill(fills, f"goblet stream rim e {i}", (cx2 + 1, 4, cz1), (cx2 + 1, 4, cz2), M.STONE)
        else:  # runs east-west: rim the long z sides
            add_fill(fills, f"goblet stream rim n {i}", (cx1, 4, cz1 - 1), (cx2, 4, cz1 - 1), M.STONE)
            add_fill(fills, f"goblet stream rim s {i}", (cx1, 4, cz2 + 1), (cx2, 4, cz2 + 1), M.STONE)
    # Drifting wine cups: pink goblets floating on the stream.
    for i, (gx, gz) in enumerate([(4740, 5434), (4784, 5470), (4740, 5512), (4694, 5560), (4760, 5592), (4822, 5650), (4892, 5730)]):
        add_fill(fills, f"wine cup {i}", (gx, 4, gz), (gx + 1, 4, gz + 1), M.PINK_WOOL)
    # Head spring pavilion (流杯亭) over the stream head.
    add_fill(fills, "spring", (4668, 4, 5418), (4692, 4, 5442), M.WATER)
    for px in (4670, 4688):
        for pz in (5420, 5438):
            add_fill(fills, f"spring col {px},{pz}", (px, 5, pz), (px + 1, 10, pz + 1), M.RED_WALL)
    add_pyramid_roof(fills, "spring roof", 4680, 5430, radius=14, y=11, roof_block=M.ROOF_GREEN, apex_block=M.GOLD)

    # ------------------------------------------------------------------
    # 3. Apricot orchard (杏林) in bloom across the east half.
    # ------------------------------------------------------------------
    for row, oz in enumerate(range(5430, 5830, 44)):
        for col, ox in enumerate(range(4860, 4970, 44)):
            _apricot_tree(fills, f"apricot {row}-{col}", ox, oz, y=4)
    # A blossom carpet under the orchard.
    for i, oz in enumerate(range(5436, 5830, 88)):
        add_fill(fills, f"blossom carpet {i}", (4856, 3, oz), (4964, 3, oz + 8), M.PINK_WOOL)
        add_fill(fills, f"blossom carpet core {i}", (4864, 3, oz + 2), (4956, 3, oz + 6), M.WHITE_WOOL)

    # ------------------------------------------------------------------
    # 4. Flower-Seeking Banquet terrace (探花宴高台), three tiers with
    #    a banquet hall on top, facing the blossoms.
    # ------------------------------------------------------------------
    add_fill(fills, "banquet tier1", (4640, 4, 5640), (4800, 4, 5800), M.STONE)
    add_fill(fills, "banquet tier2", (4655, 5, 5655), (4785, 5, 5785), M.SMOOTH)
    add_fill(fills, "banquet tier3", (4670, 6, 5670), (4770, 6, 5770), M.SMOOTH)
    # Stepped terraces descending south and east onto the lawn.
    for i in range(3):
        add_fill(fills, f"banquet steps s {i}", (4700, 3, 5802 + i * 8), (4740, 5 - i, 5807 + i * 8), M.SMOOTH)
        add_fill(fills, f"banquet steps e {i}", (4802 + i * 8, 3, 5700), (4807 + i * 8, 5 - i, 5740), M.SMOOTH)
    add_outline(fills, "banquet rail", 4640, 5640, 4800, 5800, 5, 5, M.FENCE, thickness=1)
    # Banquet hall on the terrace.
    add_fill(fills, "banquet hall", (4690, 7, 5690), (4750, 15, 5750), M.RED_WALL)
    add_outline(fills, "banquet hall frame", 4690, 5690, 4750, 5750, 7, 15, M.LOG, thickness=1)
    add_fill(fills, "banquet hall door", (4716, 8, 5750), (4724, 12, 5750), M.AIR)
    add_ridge_roof(fills, "banquet hall roof", 4686, 5686, 4754, 5754, y=16, layers=4, ridge_axis="x", roof_block=M.ROOF_GREEN)
    # Long banquet table with wine vessels.
    add_fill(fills, "banquet table", (4700, 8, 5740), (4740, 9, 5744), M.WOOD)
    for i, wx in enumerate(range(4704, 4740, 8)):
        add_fill(fills, f"banquet jar {i}", (wx, 10, 5741), (wx + 1, 11, 5743), "minecraft:barrel")

    # ------------------------------------------------------------------
    # 5. Name-inscription stele corridor (进士题名碑廊) along the north
    #    wall: covered gallery with eight graduate steles.
    # ------------------------------------------------------------------
    add_fill(fills, "stele hall floor", (4640, 4, 5364), (4940, 4, 5404), M.SMOOTH)
    add_fill(fills, "stele hall roof", (4640, 12, 5364), (4940, 12, 5370), M.DARK)
    add_fill(fills, "stele hall roof s", (4640, 12, 5398), (4940, 12, 5404), M.DARK)
    add_fill(fills, "stele hall beam", (4640, 11, 5364), (4940, 11, 5404), M.WOOD)
    for px in range(4650, 4940, 50):
        for pz in (5366, 5402):
            add_fill(fills, f"stele col {px},{pz}", (px, 5, pz), (px, 10, pz), M.LOG)
    for i, sx in enumerate(range(4680, 4930, 36)):
        _stele(fills, f"graduate stele {i}", sx, 5384, y=5)

    # ------------------------------------------------------------------
    # 6. Garden lanterns.
    # ------------------------------------------------------------------
    add_lantern_line(fills, "orchard lanterns", 4848, 5420, 4848, 5820, y=4, every=56)
    add_lantern_line(fills, "banquet lanterns", 4630, 5640, 4630, 5800, y=4, every=56)


def main() -> None:
    run_builder(build_xingyuan_3d, "xingyuan_3d")


if __name__ == "__main__":
    main()
