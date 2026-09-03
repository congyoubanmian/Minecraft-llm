from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    Fill,
    Materials as M,
    add_cantilevered_floor,
    add_fill,
    add_hip_roof,
    add_hollow_box,
    add_lantern_line,
    add_outline,
    add_pagoda_eave,
    add_pool,
    add_spiral_stair,
    add_tree,
    run_builder,
)


"""
Guangyun Pool Dock 3D (广运潭·漕运码头) - the Tang canal-transport harbour
in the eastern suburb, where Governor Wei Jian (韦坚) staged his famous
fleet review for Emperor Xuanzong in 743 AD: hundreds of grain boats
crowding the pool while the emperor watched from Wangchun Tower.

Location in Chang'an city local coordinates:
    East suburb beyond the farm belt: x 7000..7600, z 3000..3600.
    Guangyun Pool (广运潭): x 7100..7550, z 3100..3550, water surface y=1.
    Feeding canal (漕渠) from the west: x 6650..7100, z 3310..3340
    (west of x=7000 lies empty land, the only fills outside the plot).
    Ship lock (船闸) between canal and pool: x 7020..7100, z 3290..3360.
    Wangchun Tower (望春楼) on a north-east stone promontory:
    x 7380..7500, z 3160..3240, two storeys y 5..14 / 15..24.
    South berth trestle pier (南岸码头): x 7150..7300, z 3520..3560.

Distinctive features:
    - Levelled lake basin: stone base + grass topping over the whole plot,
      then the pool carved out of it (stone bed, water at y=1)
    - A stone-lined feeding canal with a two-gate ship lock: flooded stone
      lock chamber, iron-bar gates (IRON_BARS), gate towers with
      windlass beams and access steps
    - Wangchun Tower: two-storey red-wall pavilion on a stone promontory
      jutting into the pool, cantilevered balcony with fence rails
      (悬挑平座), a lower pagoda eave ring (重檐) around the square upper
      core and a hip roof (庑殿顶) above, twin spiral stairs inside,
      main front turned west towards the water
    - The tribute grain fleet: three dark-oak boats moored mid-lake with
      hollowed hulls, planked decks, hay-bale grain mounds and wool sails
      hung from tall log masts
    - South berth: plank trestle pier on log pilings, fence mooring
      bollards with lanterns, and a simple log crane with hanging crate
    - Stone quay rim around the pool and lantern lines on all four shores
"""

# Whole plot (levelled); only the canal may reach west of x=7000.
SITE_X1, SITE_Z1 = 7000, 3000
SITE_X2, SITE_Z2 = 7600, 3600

WATER_Y = 1

# Guangyun Pool and its stone quay rim.
POOL_X1, POOL_Z1 = 7100, 3100
POOL_X2, POOL_Z2 = 7550, 3550

# Feeding canal (west of the pool) and ship lock at the junction.
CANAL_X1, CANAL_X2 = 6650, 7100
CANAL_Z1, CANAL_Z2 = 3310, 3340
LOCK_X1, LOCK_Z1 = 7020, 3290
LOCK_X2, LOCK_Z2 = 7100, 3360

# Wangchun Tower: storey 1 rectangle, square storey 2 core, promontory.
TOWER_X1, TOWER_Z1 = 7380, 3160
TOWER_X2, TOWER_Z2 = 7500, 3240
TOWER_CX, TOWER_CZ = 7440, 3200
S2_X1, S2_Z1 = 7400, 3160
S2_X2, S2_Z2 = 7480, 3240
TERRACE_X1, TERRACE_Z1 = 7368, 3090
TERRACE_X2, TERRACE_Z2 = 7512, 3270

# South berth trestle pier.
PIER_X1, PIER_Z1 = 7150, 3520
PIER_X2, PIER_Z2 = 7300, 3560


def _edge_columns(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y1: int, y2: int,
) -> None:
    """Dark-oak columns on the four corners and edge midpoints of a storey."""
    mx, mz = (x1 + x2) // 2, (z1 + z2) // 2
    posts = [
        (x1, z1), (x2 - 1, z1), (x1, z2 - 1), (x2 - 1, z2 - 1),
        (mx - 1, z1), (mx - 1, z2 - 1),
        (x1, mz - 1), (x2 - 1, mz - 1),
    ]
    for i, (px, pz) in enumerate(posts):
        add_fill(fills, f"{label} col {i}", (px, y1, pz), (px + 1, y2, pz + 1), M.LOG)


def _grain_ship(
    fills: list[Fill],
    label: str,
    cx: int, cz: int,
    sail_block: str,
) -> None:
    """One moored grain boat: log hull, plank deck, hay cargo, mast + sail."""
    hx1, hx2 = cx - 11, cx + 11
    hz1, hz2 = cz - 5, cz + 5
    # Hull shell rising from the pool bed, hold dug out, plank deck on top.
    add_fill(fills, f"{label} hull", (hx1, 0, hz1), (hx2, 3, hz2), M.LOG)
    add_fill(fills, f"{label} hold", (cx - 9, 1, cz - 4), (cx + 9, 2, cz + 4), M.AIR)
    add_fill(fills, f"{label} deck", (hx1, 3, hz1), (hx2, 3, hz2), M.WOOD)
    add_outline(fills, f"{label} rail", hx1, hz1, hx2, hz2, 4, 4, M.FENCE, thickness=1)
    # Stepped hay-bale grain mound on the deck.
    for tier, wy in enumerate((4, 5, 6)):
        add_fill(
            fills, f"{label} hay {wy}",
            (cx - 6 + tier, wy, cz - 3 + tier), (cx + 2 - tier, wy, cz + 3 - tier),
            "minecraft:hay_block",
        )
    # Mast, yard and hanging wool sail (sail plane across the beam).
    mx = cx - 8
    add_fill(fills, f"{label} mast", (mx, 4, cz), (mx, 15, cz), M.LOG)
    add_fill(fills, f"{label} yard", (mx, 15, cz - 5), (mx, 15, cz + 5), "minecraft:dark_oak_log[axis=z]")
    add_fill(fills, f"{label} sail", (mx, 7, cz - 4), (mx, 14, cz + 4), sail_block)
    add_fill(fills, f"{label} pennant", (mx, 16, cz), (mx, 16, cz), M.GOLD)
    # Stern steering bench.
    add_fill(fills, f"{label} stern bench", (cx + 8, 4, cz - 2), (cx + 11, 4, cz + 2), M.WOOD)


def build_guangyun_dock_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 0. Level the whole lake plain first (stone base, grass on top),
    #    mirroring the "ba plain" pass of baliu_3d.
    # ------------------------------------------------------------------
    add_fill(fills, "guangyun plain base", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "guangyun plain grass", (SITE_X1, 2, SITE_Z1), (SITE_X2, 2 + 1, SITE_Z2), M.GRASS)

    # ------------------------------------------------------------------
    # 1. Guangyun Pool (广运潭): carve the basin out of the levelled
    #    ground, then lay the stone bed and flood it to y=1.
    # ------------------------------------------------------------------
    add_fill(fills, "guangyun pool carve", (POOL_X1, 2, POOL_Z1), (POOL_X2, 3, POOL_Z2), M.AIR)
    add_pool(fills, "guangyun pool", POOL_X1, POOL_Z1, POOL_X2, POOL_Z2, WATER_Y, depth=2)
    # Stone quay rim paving around the water edge (split west side to
    # keep the ship-lock junction intact).
    add_fill(fills, "guangyun quay n", (7097, 2, 3097), (7553, 3, 3099), M.SMOOTH)
    add_fill(fills, "guangyun quay s", (7097, 2, 3551), (7553, 3, 3553), M.SMOOTH)
    add_fill(fills, "guangyun quay w north", (7097, 2, 3100), (7099, 3, 3288), M.SMOOTH)
    add_fill(fills, "guangyun quay w south", (7097, 2, 3362), (7099, 3, 3550), M.SMOOTH)
    add_fill(fills, "guangyun quay e", (7551, 2, 3100), (7553, 3, 3550), M.SMOOTH)

    # ------------------------------------------------------------------
    # 2. Feeding canal (漕渠) from the west: stone banks, water at y=1,
    #    plus a small service bridge over it.
    # ------------------------------------------------------------------
    add_fill(fills, "guangyun canal carve", (CANAL_X1, 2, CANAL_Z1), (CANAL_X2, 3, CANAL_Z2), M.AIR)
    add_fill(fills, "guangyun canal bed", (CANAL_X1, 0, CANAL_Z1), (CANAL_X2, 0, CANAL_Z2), M.STONE)
    add_fill(fills, "guangyun canal water", (CANAL_X1, WATER_Y, CANAL_Z1), (CANAL_X2, WATER_Y, CANAL_Z2), M.WATER)
    add_fill(fills, "guangyun canal bank n", (CANAL_X1, 0, CANAL_Z1 - 3), (CANAL_X2, 2, CANAL_Z1 - 1), M.STONE)
    add_fill(fills, "guangyun canal bank s", (CANAL_X1, 0, CANAL_Z2 + 1), (CANAL_X2, 2, CANAL_Z2 + 3), M.STONE)
    add_fill(fills, "guangyun canal bank cap n", (CANAL_X1, 3, CANAL_Z1 - 3), (CANAL_X2, 3, CANAL_Z1 - 1), M.SMOOTH)
    add_fill(fills, "guangyun canal bank cap s", (CANAL_X1, 3, CANAL_Z2 + 1), (CANAL_X2, 3, CANAL_Z2 + 3), M.SMOOTH)
    add_fill(fills, "guangyun canal bridge deck", (6844, 4, 3304), (6856, 4, 3346), M.STONE)
    add_fill(fills, "guangyun canal bridge rail n", (6844, 5, 3304), (6856, 5, 3304), M.FENCE)
    add_fill(fills, "guangyun canal bridge rail s", (6844, 5, 3346), (6856, 5, 3346), M.FENCE)

    # ------------------------------------------------------------------
    # 3. Ship lock (船闸) between canal and pool: flooded stone chamber,
    #    two iron-bar gates, gate towers with windlass beams, steps up.
    # ------------------------------------------------------------------
    add_fill(fills, "guangyun lock chamber", (LOCK_X1, 0, LOCK_Z1), (LOCK_X2, 5, LOCK_Z2), M.STONE)
    add_fill(fills, "guangyun lock hollow", (LOCK_X1 + 2, 2, LOCK_Z1 + 2), (LOCK_X2 - 2, 5, LOCK_Z2 - 2), M.AIR)
    add_fill(fills, "guangyun lock water", (LOCK_X1 + 2, WATER_Y, LOCK_Z1 + 2), (LOCK_X2 - 2, WATER_Y, LOCK_Z2 - 2), M.WATER)
    # The two gates, sunk into the wall lines so they read from both sides.
    add_fill(fills, "guangyun lock gate w", (LOCK_X1 + 1, 1, LOCK_Z1 + 2), (LOCK_X1 + 1, 5, LOCK_Z2 - 2), M.IRON_BARS)
    add_fill(fills, "guangyun lock gate e", (LOCK_X2 - 1, 1, LOCK_Z1 + 2), (LOCK_X2 - 1, 5, LOCK_Z2 - 2), M.IRON_BARS)
    add_fill(fills, "guangyun lock lintel w", (LOCK_X1 + 1, 6, LOCK_Z1), (LOCK_X1 + 1, 6, LOCK_Z2), M.STONE)
    add_fill(fills, "guangyun lock lintel e", (LOCK_X2 - 1, 6, LOCK_Z1), (LOCK_X2 - 1, 6, LOCK_Z2), M.STONE)
    # Gate towers on the four corners with caps, lanterns and windlasses.
    for i, (tx, tz) in enumerate([(LOCK_X1 - 2, LOCK_Z1 - 2), (LOCK_X1 - 2, LOCK_Z2 - 2),
                                  (LOCK_X2 - 2, LOCK_Z1 - 2), (LOCK_X2 - 2, LOCK_Z2 - 2)]):
        add_fill(fills, f"guangyun lock tower {i}", (tx, 0, tz), (tx + 4, 7, tz + 4), M.STONE)
        add_fill(fills, f"guangyun lock tower cap {i}", (tx, 8, tz), (tx + 4, 8, tz + 4), M.SMOOTH)
        add_fill(fills, f"guangyun lock tower lamp {i}", (tx + 2, 9, tz + 2), (tx + 2, 9, tz + 2), M.LANTERN)
    add_fill(fills, "guangyun lock windlass w", (LOCK_X1, 9, LOCK_Z1 + 2), (LOCK_X1, 9, LOCK_Z2 - 2), "minecraft:dark_oak_log[axis=z]")
    add_fill(fills, "guangyun lock windlass e", (LOCK_X2, 9, LOCK_Z1 + 2), (LOCK_X2, 9, LOCK_Z2 - 2), "minecraft:dark_oak_log[axis=z]")
    # Access steps onto the lock walls from both banks.
    add_fill(fills, "guangyun lock step w1", (7016, 4, 3322), (7019, 4, 3328), M.SMOOTH)
    add_fill(fills, "guangyun lock step w2", (7018, 5, 3322), (7019, 5, 3328), M.SMOOTH)
    add_fill(fills, "guangyun lock step e1", (7101, 4, 3322), (7104, 4, 3328), M.SMOOTH)
    add_fill(fills, "guangyun lock step e2", (7101, 5, 3322), (7102, 5, 3328), M.SMOOTH)

    # ------------------------------------------------------------------
    # 4. Wangchun Tower (望春楼) promontory: a stone terrace driven into
    #    the pool from the north-east shore, railed against the water.
    # ------------------------------------------------------------------
    add_fill(fills, "guangyun terrace base", (TERRACE_X1, -1, TERRACE_Z1), (TERRACE_X2, 2, TERRACE_Z2), M.STONE)
    add_fill(fills, "guangyun terrace top", (TERRACE_X1, 3, TERRACE_Z1), (TERRACE_X2, 4, TERRACE_Z2), M.SMOOTH)
    add_fill(fills, "guangyun terrace step n", (7428, 4, 3086), (7448, 4, 3088), M.SMOOTH)
    add_fill(fills, "guangyun terrace rail n west", (TERRACE_X1, 5, TERRACE_Z1), (7427, 5, TERRACE_Z1), M.FENCE)
    add_fill(fills, "guangyun terrace rail n east", (7449, 5, TERRACE_Z1), (TERRACE_X2, 5, TERRACE_Z1), M.FENCE)
    add_fill(fills, "guangyun terrace rail s", (TERRACE_X1, 5, TERRACE_Z2), (TERRACE_X2, 5, TERRACE_Z2), M.FENCE)
    add_fill(fills, "guangyun terrace rail w", (TERRACE_X1, 5, TERRACE_Z1), (TERRACE_X1, 5, TERRACE_Z2), M.FENCE)
    add_fill(fills, "guangyun terrace rail e", (TERRACE_X2, 5, TERRACE_Z1), (TERRACE_X2, 5, TERRACE_Z2), M.FENCE)

    # ------------------------------------------------------------------
    # 5. Storey 1 (y 5..14): red walls, edge columns, west front door
    #    facing the pool, lattice windows, hall columns.
    # ------------------------------------------------------------------
    add_hollow_box(fills, "guangyun wangchun storey1", TOWER_X1, 5, TOWER_Z1, TOWER_X2, 14, TOWER_Z2, M.RED_WALL, thickness=1)
    _edge_columns(fills, "guangyun wangchun storey1", TOWER_X1, TOWER_Z1, TOWER_X2, TOWER_Z2, 5, 14)
    add_fill(fills, "guangyun wangchun door w", (TOWER_X1, 6, 3195), (TOWER_X1, 9, 3205), M.AIR)
    add_fill(fills, "guangyun wangchun door e", (TOWER_X2, 6, 3195), (TOWER_X2, 9, 3205), M.AIR)
    add_fill(fills, "guangyun wangchun door step w", (TOWER_X1 - 2, 5, 3195), (TOWER_X1 - 1, 5, 3205), M.SMOOTH)
    add_fill(fills, "guangyun wangchun door step e", (TOWER_X2 + 1, 5, 3195), (TOWER_X2 + 2, 5, 3205), M.SMOOTH)
    add_fill(fills, "guangyun wangchun window w1", (TOWER_X1, 8, 3170), (TOWER_X1, 11, 3176), M.GLASS)
    add_fill(fills, "guangyun wangchun window w2", (TOWER_X1, 8, 3224), (TOWER_X1, 11, 3230), M.GLASS)
    add_fill(fills, "guangyun wangchun window n1", (7400, 8, TOWER_Z1), (7430, 11, TOWER_Z1), M.GLASS)
    add_fill(fills, "guangyun wangchun window n2", (7450, 8, TOWER_Z1), (7480, 11, TOWER_Z1), M.GLASS)
    add_fill(fills, "guangyun wangchun window e1", (TOWER_X2, 8, 3190), (TOWER_X2, 11, 3210), M.GLASS)
    add_fill(fills, "guangyun wangchun window s1", (7400, 8, TOWER_Z2), (7430, 11, TOWER_Z2), M.GLASS)
    add_fill(fills, "guangyun wangchun window s2", (7450, 8, TOWER_Z2), (7480, 11, TOWER_Z2), M.GLASS)
    for i, (px, pz) in enumerate([(7420, 3180), (7460, 3180), (7420, 3220), (7460, 3220)]):
        add_fill(fills, f"guangyun wangchun hall col {i}", (px, 6, pz), (px + 1, 13, pz + 1), M.RED_WALL)

    # ------------------------------------------------------------------
    # 6. Cantilevered balcony (悬挑平座) at y15 with fence railing.
    # ------------------------------------------------------------------
    add_cantilevered_floor(fills, "guangyun wangchun balcony", TOWER_X1, TOWER_Z1, TOWER_X2, TOWER_Z2, y=15, overhang=4, block=M.WOOD)
    add_outline(fills, "guangyun wangchun balcony rail", TOWER_X1 - 4, TOWER_Z1 - 4, TOWER_X2 + 4, TOWER_Z2 + 4, 16, 16, M.FENCE, thickness=1)

    # ------------------------------------------------------------------
    # 7. Storey 2 (y 15..24): square red-wall core with the lower pagoda
    #    eave ring (重檐) hugging it, windows and the stair shaft.
    # ------------------------------------------------------------------
    add_hollow_box(fills, "guangyun wangchun storey2", S2_X1, 15, S2_Z1, S2_X2, 24, S2_Z2, M.RED_WALL, thickness=1)
    _edge_columns(fills, "guangyun wangchun storey2", S2_X1, S2_Z1, S2_X2, S2_Z2, 15, 24)
    add_pagoda_eave(fills, "guangyun wangchun lower eave", TOWER_CX, TOWER_CZ, radius=40, y=16, overhang=3, roof_block=M.ROOF_GREEN)
    add_fill(fills, "guangyun wangchun s2 door w", (S2_X1, 17, 3195), (S2_X1, 20, 3205), M.AIR)
    add_fill(fills, "guangyun wangchun s2 window w1", (S2_X1, 18, 3175), (S2_X1, 21, 3181), M.GLASS)
    add_fill(fills, "guangyun wangchun s2 window w2", (S2_X1, 18, 3219), (S2_X1, 21, 3225), M.GLASS)
    add_fill(fills, "guangyun wangchun s2 window n", (7425, 18, S2_Z1), (7455, 21, S2_Z1), M.GLASS)
    add_fill(fills, "guangyun wangchun s2 window s", (7425, 18, S2_Z2), (7455, 21, S2_Z2), M.GLASS)
    add_fill(fills, "guangyun wangchun s2 window e", (S2_X2, 18, 3190), (S2_X2, 21, 3210), M.GLASS)
    add_fill(fills, "guangyun wangchun stair shaft", (TOWER_CX - 3, 14, TOWER_CZ - 3), (TOWER_CX + 3, 15, TOWER_CZ + 3), M.AIR)
    add_spiral_stair(fills, "guangyun wangchun stair1", TOWER_CX, TOWER_CZ, radius=6, y1=6, y2=13, block=M.SMOOTH)
    add_spiral_stair(fills, "guangyun wangchun stair2", TOWER_CX, TOWER_CZ, radius=6, y1=16, y2=23, block=M.SMOOTH)
    add_hip_roof(fills, "guangyun wangchun hip roof", S2_X1, S2_Z1, S2_X2, S2_Z2, y=25, layers=8, ridge_axis="x", roof_block=M.ROOF_GREEN)

    # ------------------------------------------------------------------
    # 8. The tribute grain fleet (漕船队): three boats moored mid-lake.
    # ------------------------------------------------------------------
    _grain_ship(fills, "guangyun ship 1", 7250, 3350, M.RED_WOOL)
    _grain_ship(fills, "guangyun ship 2", 7350, 3420, M.WHITE_WOOL)
    _grain_ship(fills, "guangyun ship 3", 7200, 3250, M.WHITE_WOOL)

    # ------------------------------------------------------------------
    # 9. South berth (南岸码头): plank trestle on log pilings, mooring
    #    bollards with lanterns, and a simple log crane.
    # ------------------------------------------------------------------
    add_fill(fills, "guangyun pier deck", (PIER_X1, 3, PIER_Z1), (PIER_X2, 3, PIER_Z2), M.WOOD)
    for px in range(PIER_X1 + 5, PIER_X2 + 1, 15):
        for pz in (3524, 3548):
            add_fill(fills, f"guangyun pier piling {px},{pz}", (px, 0, pz), (px, 2, pz), M.LOG)
    for px in range(PIER_X1 + 5, PIER_X2 + 1, 15):
        add_fill(fills, f"guangyun pier bollard {px}", (px, 4, 3521), (px, 5, 3521), M.FENCE)
        if (px - PIER_X1) // 15 % 2 == 0:
            add_fill(fills, f"guangyun pier bollard lamp {px}", (px, 6, 3521), (px, 6, 3521), M.LANTERN)
    add_fill(fills, "guangyun pier rail s", (PIER_X1, 4, PIER_Z2), (PIER_X2, 4, PIER_Z2), M.FENCE)
    # Crane: log post, jib arm, stone counterweight, chain and hanging crate.
    add_fill(fills, "guangyun crane post", (7288, 4, 3556), (7288, 13, 3556), M.LOG)
    add_fill(fills, "guangyun crane arm", (7268, 13, 3556), (7290, 13, 3556), "minecraft:dark_oak_log[axis=x]")
    add_fill(fills, "guangyun crane weight", (7286, 14, 3554), (7289, 14, 3558), M.STONE)
    add_fill(fills, "guangyun crane chain", (7270, 10, 3556), (7270, 12, 3556), M.IRON_BARS)
    add_fill(fills, "guangyun crane crate", (7269, 9, 3555), (7271, 9, 3557), "minecraft:barrel")

    # ------------------------------------------------------------------
    # 10. Shore lantern lines, trees and the commemorative stele.
    # ------------------------------------------------------------------
    add_lantern_line(fills, "guangyun shore lantern n", 7110, 3070, 7530, 3070, y=4, every=60)
    add_lantern_line(fills, "guangyun shore lantern s", 7110, 3565, 7530, 3565, y=4, every=60)
    add_lantern_line(fills, "guangyun shore lantern e", 7560, 3110, 7560, 3530, y=4, every=60)
    # West line split around the ship lock (x 7020..7100, z 3290..3360).
    add_lantern_line(fills, "guangyun shore lantern w a", 7090, 3110, 7090, 3230, y=4, every=60)
    add_lantern_line(fills, "guangyun shore lantern w b", 7090, 3410, 7090, 3530, y=4, every=60)
    for tx in (7125, 7195, 7265, 7335, 7405, 7475, 7545):
        add_tree(fills, f"guangyun shore tree n {tx}", tx, 3078, y=4)
    for tx in (7085, 7330, 7400, 7470, 7540):
        add_tree(fills, f"guangyun shore tree s {tx}", tx, 3575, y=4)
    for tz in (3140, 3200, 3440, 3500):
        add_tree(fills, f"guangyun shore tree w {tz}", 7078, tz, y=4)
        add_tree(fills, f"guangyun shore tree e {tz}", 7570, tz, y=4)
    # Stele naming the pool, on the north-west shore.
    add_fill(fills, "guangyun stele base", (7078, 4, 3063), (7082, 4, 3067), M.STONE)
    add_fill(fills, "guangyun stele pillar", (7080, 5, 3065), (7080, 10, 3065), M.WHITE_TERRACOTTA)
    add_fill(fills, "guangyun stele cap", (7080, 11, 3065), (7080, 11, 3065), M.GOLD)


def main() -> None:
    run_builder(build_guangyun_dock_3d, "guangyun_dock_3d")


if __name__ == "__main__":
    main()
