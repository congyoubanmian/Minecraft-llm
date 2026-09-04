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
    add_platform_with_steps,
    add_pyramid_roof,
    add_ridge_roof,
    add_tree,
    add_underground_room,
    run_builder,
)


"""
Bing Jiao - Ling Yin 3D (官冰窖·凌阴) - the official state ice cellar of
Tang Chang'an, where blocks cut from frozen ponds each winter were stored
under straw for the summer "ban bing" (颁冰) ice-bestowing ceremonies.

Location in Chang'an city local coordinates:
    Site: the north-east corner of the city, x 4450..4750, z 4250..4550.
    The Jiaocheng rampart walkway (夹城复道) runs east-west around z ~ 4700
    to the north, so nothing in this module crosses z 4600; ward houses on
    the plot may be overwritten. Ground after grading: stone y 0..1,
    grass y 2..3, structures start y 4; negative y is used for the buried
    cellar chambers. Walled compound: x 4480..4720, z 4280..4538 with a
    small gate tower on the south wall and a postern on the west wall.

Distinctive features:
    - Three semi-subterranean ice cellars (地下冰窖) in a staggered pair +
      one layout, each an add_underground_room shell at y -6..-1 stacked
      with alternating packed-ice / ice bands in the lower half and a
      hay_block straw blanket over the upper half
    - Each cellar mouth sealed by a stone sill and a double timber door,
      reached by a hand-rolled south hauling ramp (anti-slip strips,
      smooth-stone curbs and a recessed snow-filled ice trough alongside)
    - Earth mounds (覆土窖顶) of grass/dirt 3 tiers deep over every
      cellar - three "earthen steamed buns" from afar - each pierced by
      one mossy stone vent mouth capped with iron bars, plus weeds
    - Ice canal outside the west wall with a sluice head, wooden unloading
      trestle and mooring posts for the winter ice harvest
    - Accountant office (账房) with chest row, lectern and charcoal
      brazier; ice-bestowing pavilion (赐冰亭) with four columns, pyramid
      roof and a stone table displaying gift ice
    - "Ice thieves will be punished" stele (QUARTZ_PILLAR + GOLD cap),
      two old locust trees and a lantern-flanked path from the south gate
"""

# Site plot and grading levels (plot bounds x 4450..4750, z 4250..4550).
SITE_X1, SITE_X2 = 4452, 4748
SITE_Z1, SITE_Z2 = 4252, 4548

# Walled compound (walls 2 thick, y 4..11 with dark coping).
WALL_X1, WALL_X2 = 4480, 4720
WALL_Z1, WALL_Z2 = 4280, 4538

# South gate block and postern through the west wall.
GATE_X1, GATE_X2 = 4590, 4610
POSTERN_Z1, POSTERN_Z2 = 4402, 4408

# Three buried ice cellars (x1, z1, x2, z2): two north, one south.
CELLARS = [
    (4500, 4320, 4580, 4400),
    (4600, 4320, 4680, 4400),
    (4520, 4430, 4600, 4510),
]
CELLAR_FLOOR = -6
CELLAR_CEILING = -1

HAY = "minecraft:hay_block"
PACKED_ICE = "minecraft:packed_ice"
ICE = "minecraft:ice"
SNOW = "minecraft:snow_block"
WEED = "minecraft:short_grass"


def _earth_mound(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    cx: int, cz: int,
) -> None:
    """Covered earth mound over one cellar: three grass/dirt tiers + weeds."""
    add_fill(fills, f"{label} skirt", (x1 + 4, 4, z1 + 4), (x2 - 4, 4, z2 - 4), M.DIRT)
    add_fill(fills, f"{label} mid", (x1 + 9, 5, z1 + 9), (x2 - 9, 5, z2 - 9), M.DIRT)
    add_fill(fills, f"{label} cap", (x1 + 14, 6, z1 + 14), (x2 - 14, 6, z2 - 14), M.GRASS)
    weeds = [
        (x1 + 6, 5, z1 + 6),
        (x2 - 6, 5, z2 - 6),
        (x1 + 12, 6, z2 - 12),
        (cx - 6, 7, cz - 6),
    ]
    for i, (wx, wy, wz) in enumerate(weeds):
        add_fill(fills, f"{label} weed {i}", (wx, wy, wz), (wx, wy, wz), WEED)


def _vent_mouth(fills: list[Fill], label: str, cx: int, cz: int) -> None:
    """One mossy stone vent mouth: bore, stack, flue, iron-bar grate."""
    add_fill(fills, f"{label} bore", (cx, 0, cz), (cx + 1, 6, cz + 1), M.AIR)
    add_fill(fills, f"{label} stack", (cx - 1, 5, cz - 1), (cx + 2, 9, cz + 2), M.MOSS_STONE)
    add_fill(fills, f"{label} flue", (cx, 5, cz), (cx + 1, 9, cz + 1), M.AIR)
    add_fill(fills, f"{label} grate", (cx, 10, cz), (cx + 1, 10, cz + 1), M.IRON_BARS)


def _ice_ramp(fills: list[Fill], label: str, mx: int, zm: int) -> None:
    """South hauling ramp: gentle trench from the yard down to the cellar
    door, with retaining walls, anti-slip strips and a recessed ice trough
    (snow blocks) along its east side. One block drop per two-block tread."""
    zx1, zx2 = zm + 1, zm + 22
    # Carve the trench through grading and earth, then line it.
    add_fill(fills, f"{label} trench", (mx - 6, -5, zx1), (mx + 5, 7, zx2), M.AIR)
    add_fill(fills, f"{label} wall w", (mx - 8, -6, zx1), (mx - 7, 6, zx2), M.STONE)
    add_fill(fills, f"{label} wall e", (mx + 6, -6, zx1), (mx + 7, 6, zx2), M.STONE)
    add_fill(fills, f"{label} landing", (mx - 6, -6, zx1), (mx + 5, -6, zx1 + 3), M.SMOOTH)
    for i in range(9):
        y = 3 - i
        zt = zx2 - 1 - i * 2
        add_fill(fills, f"{label} tread {i}", (mx - 6, y, zt), (mx + 2, y, zt + 1), M.SMOOTH)
        if i % 3 == 0:
            add_fill(fills, f"{label} grip {i}", (mx - 6, y, zt), (mx + 2, y, zt), M.DARK)
        add_fill(fills, f"{label} curb {i}", (mx + 3, y, zt), (mx + 3, y, zt + 1), M.SMOOTH)
        add_fill(fills, f"{label} trough {i}", (mx + 4, y - 1, zt), (mx + 5, y - 1, zt + 1), SNOW)
    # Stone sill, doorway through the cellar wall, double timber doors.
    add_fill(fills, f"{label} sill", (mx - 6, -6, zx1), (mx + 5, -6, zx1), M.ANDESITE)
    add_fill(fills, f"{label} doorway", (mx - 6, -5, zm), (mx + 5, -2, zm), M.AIR)
    add_fill(fills, f"{label} door outer", (mx - 6, -5, zx1), (mx + 5, -2, zx1), M.WOOD)
    add_fill(fills, f"{label} door inner", (mx - 6, -5, zx1 + 1), (mx + 5, -2, zx1 + 1), M.WOOD)


def _ice_cellar(fills: list[Fill], label: str, x1: int, z1: int, x2: int, z2: int) -> None:
    """One semi-subterranean ice cellar: buried chamber, ice stack, straw
    blanket, earth mound, vent mouth and the south hauling ramp."""
    cx, cz = (x1 + x2) // 2, (z1 + z2) // 2
    # Buried chamber y -6..-1 with a full stone shell.
    add_underground_room(fills, f"{label} chamber", x1, z1, x2, z2, CELLAR_FLOOR, CELLAR_CEILING, M.STONE)
    # Ice stack in the lower half: alternating packed-ice / ice bands.
    add_fill(fills, f"{label} ice base w", (x1 + 2, -6, z1 + 2), (cx - 1, -6, z2 - 2), PACKED_ICE)
    add_fill(fills, f"{label} ice base e", (cx, -6, z1 + 2), (x2 - 2, -6, z2 - 2), ICE)
    add_fill(fills, f"{label} ice mid w", (x1 + 2, -5, z1 + 2), (cx - 1, -5, z2 - 2), ICE)
    add_fill(fills, f"{label} ice mid e", (cx, -5, z1 + 2), (x2 - 2, -5, z2 - 2), PACKED_ICE)
    add_fill(fills, f"{label} ice top w", (x1 + 2, -4, z1 + 2), (cx - 1, -4, z2 - 2), PACKED_ICE)
    add_fill(fills, f"{label} ice top e", (cx, -4, z1 + 2), (x2 - 2, -4, z2 - 2), ICE)
    # Straw blanket over the ice; y -1 stays open as the working gap.
    add_fill(fills, f"{label} straw lower", (x1 + 3, -3, z1 + 3), (x2 - 3, -3, z2 - 3), HAY)
    add_fill(fills, f"{label} straw upper", (x1 + 3, -2, z1 + 3), (x2 - 3, -2, z2 - 3), HAY)
    _earth_mound(fills, f"{label} mound", x1, z1, x2, z2, cx, cz)
    _vent_mouth(fills, f"{label} vent", cx, cz)
    _ice_ramp(fills, f"{label} ramp", cx, z2)


def build_bingjiao_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site grading: stone y 0..1 + grass y 2..3 over the whole plot.
    # ------------------------------------------------------------------
    add_fill(fills, "bingjiao grade stone", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "bingjiao grade grass", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)

    # ------------------------------------------------------------------
    # 2. Yard roads (smooth stone at y 3) and the gate apron.
    # ------------------------------------------------------------------
    add_fill(fills, "bingjiao road main", (4598, 3, 4432), (4608, 3, 4534), M.SMOOTH)
    add_fill(fills, "bingjiao road cross", (4584, 3, 4424), (4608, 3, 4430), M.SMOOTH)
    add_fill(fills, "bingjiao road spur", (4584, 3, 4316), (4596, 3, 4424), M.SMOOTH)
    add_fill(fills, "bingjiao road west a", (4484, 3, 4402), (4531, 3, 4408), M.SMOOTH)
    add_fill(fills, "bingjiao road west b", (4549, 3, 4402), (4583, 3, 4408), M.SMOOTH)
    add_fill(fills, "bingjiao gate apron", (4590, 3, 4541), (4610, 3, 4548), M.SMOOTH)

    # ------------------------------------------------------------------
    # 3. Rammed-earth compound wall (y 4..11) with dark coping and corner
    #    blocks, a south gate block with small gate tower, and a west
    #    postern down to the ice canal.
    # ------------------------------------------------------------------
    add_outline(fills, "bingjiao wall plinth", WALL_X1, WALL_Z1, WALL_X2, WALL_Z2, 4, 4, M.STONE, thickness=2)
    add_outline(fills, "bingjiao wall body", WALL_X1, WALL_Z1, WALL_X2, WALL_Z2, 5, 10, M.WHITE_TERRACOTTA, thickness=2)
    add_outline(fills, "bingjiao wall coping", WALL_X1, WALL_Z1, WALL_X2, WALL_Z2, 11, 11, M.DARK, thickness=2)
    for i, (kx, kz) in enumerate([(4478, 4278), (4717, 4278), (4478, 4535), (4717, 4535)]):
        add_fill(fills, f"bingjiao wall corner {i}", (kx, 4, kz), (kx + 5, 11, kz + 5), M.STONE)
    # South gate: solid block, carved passage, timber beam, corner pillars.
    add_fill(fills, "bingjiao gate block", (4584, 4, 4535), (4616, 15, 4540), M.STONE)
    add_fill(fills, "bingjiao gate passage", (GATE_X1, 4, 4535), (GATE_X2, 15, 4540), M.AIR)
    add_fill(fills, "bingjiao gate beam", (GATE_X1, 14, 4535), (GATE_X2, 14, 4540), "minecraft:dark_oak_log[axis=x]")
    for i, (px, pz) in enumerate([(4584, 4535), (4615, 4535), (4584, 4539), (4615, 4539)]):
        add_fill(fills, f"bingjiao gate pillar {i}", (px, 11, pz), (px + 1, 16, pz + 1), M.LOG)
    add_fill(fills, "bingjiao gate plaque", (4592, 12, 4541), (4608, 13, 4541), M.GOLD)
    add_fill(fills, "bingjiao gate lamp w", (4586, 12, 4541), (4586, 12, 4541), M.SEA_LANTERN)
    add_fill(fills, "bingjiao gate lamp e", (4614, 12, 4541), (4614, 12, 4541), M.SEA_LANTERN)
    add_ridge_roof(fills, "bingjiao gate roof", 4583, 4534, 4617, 4541, 17, layers=2, ridge_axis="x", roof_block=M.ROOF_GREEN)
    # West postern with lintel and steps down to the canal path.
    add_fill(fills, "bingjiao postern opening", (4480, 4, POSTERN_Z1), (4481, 9, POSTERN_Z2), M.AIR)
    add_fill(fills, "bingjiao postern floor", (4480, 4, POSTERN_Z1), (4481, 4, POSTERN_Z2), M.SMOOTH)
    add_fill(fills, "bingjiao postern lintel", (4480, 10, POSTERN_Z1 - 1), (4481, 10, POSTERN_Z2 + 1), "minecraft:dark_oak_log[axis=z]")
    add_fill(fills, "bingjiao postern step out", (4478, 3, POSTERN_Z1), (4479, 3, POSTERN_Z2), M.SMOOTH)
    add_fill(fills, "bingjiao postern step in", (4482, 3, POSTERN_Z1), (4483, 3, POSTERN_Z2), M.SMOOTH)

    # ------------------------------------------------------------------
    # 4. Three buried ice cellars with ice stacks, straw, mounds, vents
    #    and hauling ramps.
    # ------------------------------------------------------------------
    for i, (x1, z1, x2, z2) in enumerate(CELLARS):
        _ice_cellar(fills, f"bingjiao cellar {i + 1}", x1, z1, x2, z2)

    # ------------------------------------------------------------------
    # 5. Ice canal outside the west wall: dug channel, sluice head with
    #    grate, wooden unloading trestle and mooring posts.
    # ------------------------------------------------------------------
    add_fill(fills, "bingjiao canal carve", (4454, -1, 4392), (4478, 3, 4397), M.AIR)
    add_fill(fills, "bingjiao canal bed", (4454, -2, 4392), (4478, -2, 4397), M.SMOOTH)
    add_fill(fills, "bingjiao canal water", (4454, -1, 4392), (4478, 0, 4397), M.WATER)
    add_fill(fills, "bingjiao canal bank n", (4454, -1, 4389), (4478, 2, 4391), M.STONE)
    add_fill(fills, "bingjiao canal bank s", (4454, -1, 4398), (4478, 2, 4400), M.STONE)
    add_fill(fills, "bingjiao canal head", (4454, -1, 4390), (4456, 4, 4399), M.STONE)
    add_fill(fills, "bingjiao canal grate", (4457, 0, 4393), (4457, 2, 4396), M.IRON_BARS)
    # Unloading trestle on the north bank: deck, piles, fence rail.
    add_fill(fills, "bingjiao trestle deck", (4462, 3, 4386), (4478, 3, 4391), M.WOOD)
    add_fill(fills, "bingjiao trestle rail", (4462, 4, 4386), (4478, 4, 4386), M.FENCE)
    for px, pz in [(4463, 4387), (4463, 4390), (4476, 4387), (4476, 4390)]:
        add_fill(fills, f"bingjiao trestle pile {px},{pz}", (px, 0, pz), (px, 2, pz), M.LOG)
    # Mooring posts on both quays.
    for px in (4458, 4470):
        add_fill(fills, f"bingjiao mooring n {px}", (px, 3, 4390), (px, 5, 4390), M.LOG)
        add_fill(fills, f"bingjiao mooring s {px}", (px, 3, 4399), (px, 5, 4399), M.LOG)

    # ------------------------------------------------------------------
    # 6. Accountant office (账房) in the north yard: stone platform, red
    #    hall, chest row, lectern and charcoal brazier.
    # ------------------------------------------------------------------
    add_fill(fills, "bingjiao office platform", (4560, 4, 4284), (4660, 4, 4314), M.STONE)
    add_fill(fills, "bingjiao office apron", (4580, 4, 4315), (4600, 4, 4317), M.SMOOTH)
    add_hollow_box(fills, "bingjiao office hall", 4560, 6, 4284, 4660, 12, 4314, M.RED_WALL, thickness=1)
    add_fill(fills, "bingjiao office floor", (4561, 6, 4285), (4659, 6, 4313), M.WOOD)
    for i, (px, pz) in enumerate([(4560, 4284), (4659, 4284), (4560, 4313), (4659, 4313)]):
        add_fill(fills, f"bingjiao office pillar {i}", (px, 6, pz), (px + 1, 12, pz + 1), M.LOG)
    add_fill(fills, "bingjiao office door", (4582, 7, 4314), (4598, 10, 4314), M.AIR)
    add_fill(fills, "bingjiao office lintel", (4581, 11, 4314), (4599, 11, 4314), "minecraft:dark_oak_log[axis=x]")
    add_fill(fills, "bingjiao office window w", (4580, 9, 4284), (4600, 10, 4284), M.GLASS)
    add_fill(fills, "bingjiao office window e", (4620, 9, 4284), (4640, 10, 4284), M.GLASS)
    add_fill(fills, "bingjiao office vent w", (4560, 9, 4292), (4560, 10, 4306), M.IRON_BARS)
    add_fill(fills, "bingjiao office vent e", (4660, 9, 4292), (4660, 10, 4306), M.IRON_BARS)
    # Furnishings on the timber floor: chest row, lectern, brazier, lamp.
    add_fill(fills, "bingjiao office chests", (4570, 7, 4288), (4580, 7, 4288), "minecraft:chest")
    add_fill(fills, "bingjiao office lectern", (4590, 7, 4288), (4590, 7, 4288), "minecraft:lectern")
    add_fill(fills, "bingjiao office brazier", (4630, 7, 4299), (4630, 7, 4299), "minecraft:campfire")
    add_fill(fills, "bingjiao office lamp", (4650, 7, 4288), (4650, 7, 4288), M.SEA_LANTERN)
    add_ridge_roof(fills, "bingjiao office roof", 4560, 4284, 4660, 4314, 13, layers=3, ridge_axis="x", roof_block=M.ROOF_DARK)

    # ------------------------------------------------------------------
    # 7. Ice-bestowing pavilion (赐冰亭) south-east of the gate: stepped
    #    stone platform, four red columns, pyramid roof, and a stone
    #    table displaying the summer gift ice.
    # ------------------------------------------------------------------
    add_platform_with_steps(fills, "bingjiao pavilion base", 4634, 4462, 4658, 4486, 4, [(1, 0, M.SMOOTH), (1, 2, M.STONE)])
    add_fill(fills, "bingjiao pavilion apron", (4642, 4, 4487), (4650, 4, 4488), M.SMOOTH)
    for i, (px, pz) in enumerate([(4639, 4467), (4652, 4467), (4639, 4480), (4652, 4480)]):
        add_fill(fills, f"bingjiao pavilion column {i}", (px, 6, pz), (px + 1, 12, pz + 1), M.RED_WALL)
    add_fill(fills, "bingjiao pavilion table", (4645, 6, 4473), (4647, 6, 4475), M.SMOOTH)
    add_fill(fills, "bingjiao pavilion gift ice", (4645, 7, 4473), (4647, 7, 4475), PACKED_ICE)
    add_pyramid_roof(fills, "bingjiao pavilion roof", 4646, 4474, radius=10, y=13, roof_block=M.ROOF_GREEN, apex_block=M.GOLD)

    # ------------------------------------------------------------------
    # 8. Warning stele by the south gate: "ice thieves will be punished".
    # ------------------------------------------------------------------
    add_fill(fills, "bingjiao stele base", (4616, 4, 4506), (4617, 4, 4507), M.DARK)
    add_fill(fills, "bingjiao stele shaft", (4616, 5, 4506), (4617, 9, 4507), "minecraft:quartz_pillar[axis=y]")
    add_fill(fills, "bingjiao stele inscription", (4616, 6, 4508), (4617, 8, 4508), M.BLACK_WOOL)
    add_fill(fills, "bingjiao stele cap", (4615, 10, 4505), (4618, 10, 4508), M.GOLD)

    # ------------------------------------------------------------------
    # 9. Lantern-flanked path and two old locust trees.
    # ------------------------------------------------------------------
    add_lantern_line(fills, "bingjiao lantern east", 4612, 4532, 4612, 4444, 4, every=44)
    add_lantern_line(fills, "bingjiao lantern west", 4594, 4532, 4594, 4512, 4, every=20)
    add_tree(fills, "bingjiao locust west", 4510, 4296, 4, height=9, spread=4)
    add_tree(fills, "bingjiao locust east", 4700, 4296, 4, height=9, spread=4)


def main() -> None:
    run_builder(build_bingjiao_3d, "bingjiao_3d")


if __name__ == "__main__":
    main()
