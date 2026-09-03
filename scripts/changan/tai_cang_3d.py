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
    add_pyramid_roof,
    add_ridge_roof,
    add_spiral_stair,
    add_tree,
    add_underground_room,
    run_builder,
)


"""
Tai Cang Underground Granary 3D (太仓·地下仓窖群) - the state granary of
Tang Chang'an in the eastern suburbs, modelled on the underground pit
storage (地下仓窖) system excavated at Hanjia Cang (含嘉仓) in Luoyang:
most of the storage volume sits below grade, the defining trait of
this module.

Location in Chang'an city local coordinates:
    Site: x 7000..7500, z 3650..4150 (eastern suburb). The Guangyun Tan
    canal port (z 3000..3600) lies to the north and is not touched.
    Walled compound: x 7020..7480, z 3680..4120, rammed-earth walls
    y 4..11 with a gate tower over the south gate.
    Ground after grading: stone y 0..1, grass y 2..3; buildings start y 4.
    The canal wharf west of the wall (x 6860..7020) is graded too.

Distinctive features:
    - Six underground grain pits (地下仓窖) in a 3x2 matrix, each built
      with add_underground_room at y -5..-1, filled with stepped
      hay_block mounds and sealed with wooden covers at y -1
    - A link tunnel (联络隧道) along the pit-row midline connecting all
      three columns, plus an access trench stair from the yard
    - One quartz ventilation shaft per pit: a bored flue through the
      cover and ceiling up to a 4-block stack capped with iron bars
    - Three raised surface granary halls (仓廪) with iron-bar vent
      bands, interior hay mounds and barrel rows, dark-tile ridge roofs
    - Rammed-earth perimeter wall with a south gate, gilded plaque and
      a ridge-roofed gate tower
    - Weighing platform (计量台) inside the gate: log balance beam on
      posts with hanging wool grain sacks
    - North-east corner watch tower (卫楼) with a pyramid roof (攒尖顶)
    - Canal wharf outside the west wall: water channel dug through the
      grading layer, a culvert through the wall into an inner basin, a
      wooden unloading trestle and mooring posts
"""

# Site footprint and grading levels.
SITE_X1, SITE_X2 = 7000, 7500
SITE_Z1, SITE_Z2 = 3650, 4150

# Walled compound (walls are 3 thick, y 4..11).
WALL_X1, WALL_X2 = 7020, 7480
WALL_Z1, WALL_Z2 = 3680, 4120
GATE_X1, GATE_X2 = 7228, 7272

# Surface granary halls: (x1, z1, x2, z2).
GRANARIES = [
    (7060, 3720, 7220, 3820),
    (7260, 3720, 7420, 3820),
    (7060, 3900, 7220, 4000),
]

# Underground pit matrix: 3 columns x 2 rows, each pit 27 x 27.
PIT_COLS = [(7260, 7286), (7320, 7346), (7380, 7406)]
PIT_ROWS = [(3900, 3926), (3970, 3996)]
PIT_FLOOR = -5
PIT_CEILING = -1

# Link tunnel between the pit rows (row midline z ~ 3948).
TUN_X1, TUN_X2 = 7245, 7415
TUN_Z1, TUN_Z2 = 3943, 3953

# Canal wharf west of the wall.
CANAL_X1, CANAL_X2 = 6860, 7020
CANAL_Z1, CANAL_Z2 = 3860, 3890
BASIN_X1, BASIN_X2 = 7023, 7058
BASIN_Z1, BASIN_Z2 = 3862, 3888


def _surface_granary(fills: list[Fill], label: str, x1: int, z1: int, x2: int, z2: int) -> None:
    """One raised granary hall: stone platform, vented walls, ridge roof, grain."""
    mx = (x1 + x2) // 2
    # Raised stone platform (y 4..6) and south entrance steps.
    add_fill(fills, f"{label} platform", (x1, 4, z1), (x2, 6, z2), M.STONE)
    add_fill(fills, f"{label} step hi", (mx - 10, 5, z2 + 1), (mx + 10, 5, z2 + 2), M.SMOOTH)
    add_fill(fills, f"{label} step lo", (mx - 10, 4, z2 + 3), (mx + 10, 4, z2 + 4), M.SMOOTH)
    # Dark-oak corner pillars.
    for i, (px, pz) in enumerate([(x1, z1), (x2 - 1, z1), (x1, z2 - 1), (x2 - 1, z2 - 1)]):
        add_fill(fills, f"{label} pillar {i}", (px, 7, pz), (px + 1, 15, pz + 1), M.LOG)
    # Hall body: red walls with a hollow interior.
    add_fill(fills, f"{label} wall", (x1, 7, z1), (x2, 15, z2), M.RED_WALL)
    add_fill(fills, f"{label} hall", (x1 + 1, 7, z1 + 1), (x2 - 1, 15, z2 - 1), M.AIR)
    # South doorway with a timber lintel.
    add_fill(fills, f"{label} door", (mx - 8, 7, z2), (mx + 8, 11, z2), M.AIR)
    add_fill(fills, f"{label} lintel", (mx - 9, 12, z2), (mx + 9, 12, z2), "minecraft:dark_oak_log[axis=x]")
    # Continuous iron-bar ventilation grilles through east/west walls.
    add_fill(fills, f"{label} vent w", (x1, 11, z1 + 12), (x1, 13, z2 - 12), M.IRON_BARS)
    add_fill(fills, f"{label} vent e", (x2, 11, z1 + 12), (x2, 13, z2 - 12), M.IRON_BARS)
    # Dark tiled gable roof, ridge on the long (x) axis.
    add_ridge_roof(fills, f"{label} roof", x1, z1, x2, z2, 16, layers=3, ridge_axis="x", roof_block=M.ROOF_DARK)
    # Stepped hay mounds inside.
    for i, (cx, cz) in enumerate([(x1 + 35, z1 + 30), (x1 + 85, z1 + 55)]):
        add_fill(fills, f"{label} mound {i} base", (cx - 14, 7, cz - 10), (cx + 14, 8, cz + 10), "minecraft:hay_block")
        add_fill(fills, f"{label} mound {i} mid", (cx - 8, 9, cz - 6), (cx + 8, 9, cz + 6), "minecraft:hay_block")
        add_fill(fills, f"{label} mound {i} top", (cx - 4, 10, cz - 3), (cx + 4, 10, cz + 3), "minecraft:hay_block")
    # Barrel row along the west wall plus a floor lamp.
    add_fill(fills, f"{label} barrels", (x1 + 4, 7, z1 + 15), (x1 + 4, 8, z2 - 15), "minecraft:barrel")
    add_fill(fills, f"{label} floor lamp", (x1 + 20, 6, z1 + 20), (x1 + 20, 6, z1 + 20), M.SEA_LANTERN)


def _grain_pit(fills: list[Fill], label: str, x1: int, z1: int, x2: int, z2: int) -> None:
    """One underground storage pit: room, hay mound, wooden cover."""
    add_underground_room(fills, f"{label} room", x1, z1, x2, z2, PIT_FLOOR, PIT_CEILING, M.STONE)
    # Stepped grain mound: y -5..-4 wide, y -3 narrower, y -2 kept clear.
    add_fill(fills, f"{label} grain base", (x1 + 3, -5, z1 + 3), (x2 - 3, -4, z2 - 3), "minecraft:hay_block")
    add_fill(fills, f"{label} grain top", (x1 + 6, -3, z1 + 6), (x2 - 6, -3, z2 - 6), "minecraft:hay_block")
    # Wooden cover sealing the pit mouth at y -1.
    add_fill(fills, f"{label} cover", (x1 + 1, -1, z1 + 1), (x2 - 1, -1, z2 - 1), M.WOOD)


def _vent_shaft(fills: list[Fill], label: str, cx: int, cz: int) -> None:
    """Quartz ventilation shaft above one pit: bore, stack, flue, bar grate."""
    # Bore the flue through cover, ceiling and grading down to the pit.
    add_fill(fills, f"{label} bore", (cx, -1, cz), (cx + 1, 3, cz + 1), M.AIR)
    # Quartz stack on the surface (y 4..9) with a 2x2 hollow core.
    add_fill(fills, f"{label} stack", (cx - 1, 4, cz - 1), (cx + 2, 9, cz + 2), M.QUARTZ)
    add_fill(fills, f"{label} flue", (cx, 4, cz), (cx + 1, 9, cz + 1), M.AIR)
    # Iron-bar grate capping the draft.
    add_fill(fills, f"{label} grate", (cx, 10, cz), (cx + 1, 10, cz + 1), M.IRON_BARS)


def build_tai_cang_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site grading: stone y 0..1 + grass y 2..3 over the whole
    #    footprint, plus a graded margin for the west canal wharf.
    # ------------------------------------------------------------------
    add_fill(fills, "taicang grade stone", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "taicang grade grass", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)

    # ------------------------------------------------------------------
    # 2. Courtyard roads (smooth stone at y 3).
    # ------------------------------------------------------------------
    add_fill(fills, "taicang road main", (7236, 3, 3700), (7264, 3, 4117), M.SMOOTH)
    add_fill(fills, "taicang road cross", (7060, 3, 3844), (7450, 3, 3864), M.SMOOTH)

    # ------------------------------------------------------------------
    # 3. Perimeter wall (y 4..11) with parapet, south gate and gate tower.
    # ------------------------------------------------------------------
    add_outline(fills, "taicang wall plinth", WALL_X1, WALL_Z1, WALL_X2, WALL_Z2, 4, 5, M.STONE, thickness=3)
    add_outline(fills, "taicang wall body", WALL_X1, WALL_Z1, WALL_X2, WALL_Z2, 6, 11, M.WHITE_TERRACOTTA, thickness=3)
    add_outline(fills, "taicang wall parapet", WALL_X1, WALL_Z1, WALL_X2, WALL_Z2, 12, 13, M.WHITE_TERRACOTTA, thickness=1)
    # South gate opening and timber lintel.
    add_fill(fills, "taicang gate opening", (GATE_X1, 4, 4118), (GATE_X2, 11, 4120), M.AIR)
    add_fill(fills, "taicang gate lintel", (GATE_X1 - 2, 11, 4117), (GATE_X2 + 2, 11, 4121), "minecraft:dark_oak_log[axis=x]")
    # Solid gate block flanking the opening, carrying the gate tower.
    add_fill(fills, "taicang gate block n", (7222, 4, 4112), (7278, 11, 4117), M.STONE)
    add_fill(fills, "taicang gate block s", (7222, 4, 4121), (7278, 11, 4126), M.STONE)
    # Gate tower (y 12..18) with corner pillars.
    add_hollow_box(fills, "taicang gate tower", 7222, 12, 4112, 7278, 18, 4126, M.RED_WALL, thickness=1)
    for i, (px, pz) in enumerate([(7222, 4112), (7276, 4112), (7222, 4124), (7276, 4124)]):
        add_fill(fills, f"taicang gate tower pillar {i}", (px, 12, pz), (px + 1, 18, pz + 1), M.LOG)
    add_fill(fills, "taicang gate tower door", (7238, 12, 4126), (7262, 15, 4126), M.AIR)
    add_fill(fills, "taicang gate tower window w", (7228, 14, 4126), (7233, 16, 4126), M.GLASS)
    add_fill(fills, "taicang gate tower window e", (7266, 14, 4126), (7271, 16, 4126), M.GLASS)
    # Gilded plaque above the gate.
    add_fill(fills, "taicang gate plaque", (7242, 16, 4127), (7258, 17, 4127), M.GOLD)
    add_fill(fills, "taicang gate lamp w", (7224, 12, 4127), (7224, 12, 4127), M.SEA_LANTERN)
    add_fill(fills, "taicang gate lamp e", (7276, 12, 4127), (7276, 12, 4127), M.SEA_LANTERN)
    add_ridge_roof(fills, "taicang gate tower roof", 7220, 4110, 7280, 4128, 19, layers=3, ridge_axis="x", roof_block=M.ROOF_GREEN)

    # ------------------------------------------------------------------
    # 4. Three surface granary halls (仓廪).
    # ------------------------------------------------------------------
    for i, (x1, z1, x2, z2) in enumerate(GRANARIES):
        _surface_granary(fills, f"taicang granary {i + 1}", x1, z1, x2, z2)

    # ------------------------------------------------------------------
    # 5. Underground pit matrix: 6 pits, link tunnel, adits, access stair.
    # ------------------------------------------------------------------
    for r, (z1, z2) in enumerate(PIT_ROWS):
        for c, (x1, x2) in enumerate(PIT_COLS):
            _grain_pit(fills, f"taicang pit {c + 1}{r + 1}", x1, z1, x2, z2)
    # Link tunnel along the row midline: ceiling, cavity, floor, walls.
    add_fill(fills, "taicang tunnel ceiling", (TUN_X1, -1, TUN_Z1), (TUN_X2, -1, TUN_Z2), M.STONE)
    add_fill(fills, "taicang tunnel cavity", (TUN_X1 + 1, -5, TUN_Z1 + 1), (TUN_X2 - 1, -2, TUN_Z2 - 1), M.AIR)
    add_fill(fills, "taicang tunnel floor", (TUN_X1, -6, TUN_Z1), (TUN_X2, -6, TUN_Z2), M.SMOOTH)
    add_fill(fills, "taicang tunnel wall w", (TUN_X1, -5, TUN_Z1), (TUN_X1, -1, TUN_Z2), M.STONE)
    add_fill(fills, "taicang tunnel wall e", (TUN_X2, -5, TUN_Z1), (TUN_X2, -1, TUN_Z2), M.STONE)
    # Adits from the tunnel into each pit column, with a smooth floor.
    for c, (px1, px2) in enumerate(PIT_COLS):
        ax1, ax2 = px1 + 8, px2 - 8
        add_fill(fills, f"taicang adit {c} north", (ax1, -5, 3926), (ax2, -2, 3944), M.AIR)
        add_fill(fills, f"taicang adit {c} south", (ax1, -5, 3952), (ax2, -2, 3970), M.AIR)
        add_fill(fills, f"taicang adit {c} floor", (ax1, -6, 3926), (ax2, -6, 3970), M.SMOOTH)
    # Access trench stair from the yard down into the tunnel (gentle,
    # hand-rolled: one block drop per two-block tread, with headroom).
    for i in range(9):
        y = 3 - i
        z1 = 3962 - i * 2
        add_fill(fills, f"taicang pit stair step {i}", (7246, y, z1), (7252, y, z1 + 1), M.SMOOTH)
        add_fill(fills, f"taicang pit stair head {i}", (7246, y + 1, z1), (7252, y + 4, z1 + 1), M.AIR)
    add_fill(fills, "taicang pit stair lining w", (7245, -5, 3944), (7245, 4, 3964), M.STONE)
    add_fill(fills, "taicang pit stair lining e", (7253, -5, 3944), (7253, 4, 3964), M.STONE)
    # Sea-lantern strips let into the tunnel ceiling.
    for x in range(7264, TUN_X2, 60):
        add_fill(fills, f"taicang tunnel lamp {x}", (x, -1, 3947), (x, -1, 3949), M.SEA_LANTERN)

    # ------------------------------------------------------------------
    # 6. Ventilation shafts, one directly above each pit.
    # ------------------------------------------------------------------
    for r, (z1, z2) in enumerate(PIT_ROWS):
        for c, (x1, x2) in enumerate(PIT_COLS):
            _vent_shaft(fills, f"taicang shaft {c + 1}{r + 1}", x1 + 13, z1 + 13)

    # ------------------------------------------------------------------
    # 7. Weighing platform (计量台) inside the south gate: balance beam
    #    on log posts with hanging wool grain sacks.
    # ------------------------------------------------------------------
    add_fill(fills, "taicang measure platform", (7210, 4, 4050), (7290, 5, 4090), M.STONE)
    add_fill(fills, "taicang measure step", (7240, 4, 4091), (7260, 4, 4092), M.SMOOTH)
    add_fill(fills, "taicang measure post w", (7232, 6, 4068), (7233, 15, 4069), M.LOG)
    add_fill(fills, "taicang measure post e", (7267, 6, 4068), (7268, 15, 4069), M.LOG)
    add_fill(fills, "taicang measure fulcrum", (7249, 6, 4068), (7250, 19, 4069), M.LOG)
    add_fill(fills, "taicang measure beam", (7230, 16, 4068), (7270, 17, 4069), "minecraft:dark_oak_log[axis=x]")
    for i, (sx, wool) in enumerate([
        (7237, M.YELLOW_WOOL),
        (7261, M.RED_WOOL),
    ]):
        add_fill(fills, f"taicang measure rope {i}", (sx, 14, 4068), (sx, 15, 4068), M.LOG)
        add_fill(fills, f"taicang measure sack {i}", (sx, 11, 4068), (sx + 1, 13, 4069), wool)

    # ------------------------------------------------------------------
    # 8. Watch tower (卫楼) in the north-east corner: stepped stone base,
    #    red body, deck, spiral stair and a pyramid roof.
    #    Base kept at x <= 7476 / z <= 4116 so it never cuts the wall.
    # ------------------------------------------------------------------
    add_fill(fills, "taicang watch base", (7440, 4, 4080), (7476, 6, 4116), M.STONE)
    add_hollow_box(fills, "taicang watch body", 7444, 7, 4084, 7472, 16, 4112, M.RED_WALL, thickness=1)
    for i, (px, pz) in enumerate([(7444, 4084), (7471, 4084), (7444, 4111), (7471, 4111)]):
        add_fill(fills, f"taicang watch pillar {i}", (px, 7, pz), (px + 1, 16, pz + 1), M.LOG)
    add_fill(fills, "taicang watch window n", (7452, 11, 4084), (7464, 13, 4084), M.IRON_BARS)
    add_fill(fills, "taicang watch window s", (7452, 11, 4112), (7464, 13, 4112), M.IRON_BARS)
    add_fill(fills, "taicang watch door", (7454, 7, 4112), (7462, 10, 4112), M.AIR)
    add_fill(fills, "taicang watch step hi", (7452, 5, 4115), (7464, 5, 4116), M.SMOOTH)
    add_fill(fills, "taicang watch step lo", (7452, 4, 4117), (7464, 4, 4117), M.SMOOTH)
    add_fill(fills, "taicang watch deck", (7442, 17, 4082), (7474, 17, 4114), M.WOOD)
    add_outline(fills, "taicang watch rail", 7442, 4082, 7474, 4114, 18, 18, M.FENCE, thickness=1)
    add_spiral_stair(fills, "taicang watch stair", 7458, 4098, radius=7, y1=7, y2=16, block=M.SMOOTH)
    add_pyramid_roof(fills, "taicang watch roof", 7458, 4098, radius=12, y=18, roof_block=M.ROOF_GREEN, apex_block=M.GOLD)

    # ------------------------------------------------------------------
    # 9. Canal wharf (漕渠码头) west of the wall: channel dug through the
    #    grading layer, culvert into an inner basin, trestle, mooring posts.
    # ------------------------------------------------------------------
    # Main channel: carve, water, stone banks, stone heading at the west end.
    add_fill(fills, "taicang canal carve", (CANAL_X1, 1, CANAL_Z1), (CANAL_X2, 4, CANAL_Z2), M.AIR)
    add_fill(fills, "taicang canal water", (CANAL_X1, 1, CANAL_Z1), (CANAL_X2, 1, CANAL_Z2), M.WATER)
    add_fill(fills, "taicang canal bank n", (CANAL_X1, 1, 3857), (CANAL_X2, 3, 3859), M.STONE)
    add_fill(fills, "taicang canal bank s", (CANAL_X1, 1, 3891), (CANAL_X2, 3, 3893), M.STONE)
    add_fill(fills, "taicang canal head", (6856, 1, 3856), (6859, 4, 3894), M.STONE)
    # North spur pointing toward the Guangyun Tan port (symbolic link).
    add_fill(fills, "taicang spur carve", (6862, 1, 3660), (6882, 4, 3859), M.AIR)
    add_fill(fills, "taicang spur water", (6862, 1, 3660), (6882, 1, 3859), M.WATER)
    add_fill(fills, "taicang spur bank w", (6860, 1, 3660), (6861, 3, 3859), M.STONE)
    add_fill(fills, "taicang spur bank e", (6883, 1, 3660), (6884, 3, 3859), M.STONE)
    add_fill(fills, "taicang spur sluice", (6858, 1, 3654), (6886, 5, 3659), M.STONE)
    add_fill(fills, "taicang spur grate", (6866, 1, 3657), (6880, 4, 3657), M.IRON_BARS)
    # Culvert through the west wall with a stone arch.
    add_fill(fills, "taicang culvert carve", (7020, 1, 3866), (7022, 4, 3884), M.AIR)
    add_fill(fills, "taicang culvert arch", (7020, 5, 3864), (7022, 6, 3886), M.STONE)
    # Inner basin inside the wall with stone quays.
    add_fill(fills, "taicang basin carve", (BASIN_X1, 1, BASIN_Z1), (BASIN_X2, 4, BASIN_Z2), M.AIR)
    add_fill(fills, "taicang basin water", (BASIN_X1, 1, BASIN_Z1), (BASIN_X2, 1, BASIN_Z2), M.WATER)
    add_fill(fills, "taicang basin quay n", (BASIN_X1, 1, 3859), (BASIN_X2, 3, 3861), M.STONE)
    add_fill(fills, "taicang basin quay s", (BASIN_X1, 1, 3889), (BASIN_X2, 3, 3891), M.STONE)
    add_fill(fills, "taicang basin quay e", (7059, 1, BASIN_Z1), (7060, 3, BASIN_Z2), M.STONE)
    # Unloading trestle: ramp, plank deck on log piles, fence rails.
    add_fill(fills, "taicang trestle ramp", (6954, 3, 3870), (6959, 3, 3880), M.SMOOTH)
    add_fill(fills, "taicang trestle ramp pile", (6956, 0, 3875), (6957, 2, 3875), M.LOG)
    add_fill(fills, "taicang trestle deck", (6960, 2, 3868), (7019, 2, 3882), M.WOOD)
    for px in (6966, 6994):
        for pz in (3869, 3881):
            add_fill(fills, f"taicang trestle pile {px},{pz}", (px, 0, pz), (px, 1, pz), M.LOG)
    add_fill(fills, "taicang trestle rail n", (6960, 3, 3868), (7019, 3, 3868), M.FENCE)
    add_fill(fills, "taicang trestle rail s", (6960, 3, 3882), (7019, 3, 3882), M.FENCE)
    # Mooring posts along both banks.
    for px in (6890, 6960):
        add_fill(fills, f"taicang mooring n {px}", (px, 4, 3858), (px, 6, 3858), M.LOG)
        add_fill(fills, f"taicang mooring s {px}", (px, 4, 3892), (px, 6, 3892), M.LOG)

    # ------------------------------------------------------------------
    # 10. Yard lanterns and trees.
    # ------------------------------------------------------------------
    add_lantern_line(fills, "taicang road lanterns", 7250, 4044, 7250, 3990, 4, every=54)
    add_tree(fills, "taicang tree sw", 7090, 4060, 4)
    add_tree(fills, "taicang tree ne", 7445, 3750, 4)


def main() -> None:
    run_builder(build_tai_cang_3d, "tai_cang_3d")


if __name__ == "__main__":
    main()
