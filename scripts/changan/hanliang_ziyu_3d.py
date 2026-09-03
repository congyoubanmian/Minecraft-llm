from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    Fill,
    Materials as M,
    add_column_grid,
    add_fill,
    add_hip_roof,
    add_lantern_line,
    add_outline,
    add_platform_with_steps,
    add_pyramid_roof,
    add_ridge_roof,
    add_staircase,
    add_underground_room,
    run_builder,
)


"""
Hanliang Hall + Self-Raining Pavilion (含凉殿·自雨亭) 3D module.

The Tang water-cooled summer palace on the west shore of Taiye Pool
(太液池) in Daming Palace. Hanliang Hall (含凉殿) stands on a raised stone
platform facing the pool, crowned by a hip roof (庑殿顶) that carries a
stone water tank - the imperial cooling reservoir. Water spills from the
tank down the east roof slope and falls from the eave line as a rain
curtain (雨帘) into a stone channel at the hall's base, which drains east
back into the pool. South of the hall, the Self-Raining Pavilion (自雨亭)
lifts pool water with a great vertical waterwheel and rains it back from
its pyramidal roof (攒尖顶) through curtains between its four columns into
a surrounding channel ring. An underground ice cellar (冰窖) stocked with
packed and blue ice sits beneath the hall, and a covered corridor links
hall and pavilion along the shore.

Location in Chang'an city local coordinates:
    x: 2620 .. 2760   (Taiye Pool water spans x 2780..3220)
    z: 5540 .. 5700   (Taiye Pool water spans z 5500..5740)

3D features:
    - Raised stone platform (~4 high) with southern entry steps
    - Red-walled hall with dark-oak colonnade and hip roof (庑殿顶)
    - Roof-top stone water tank with overflow cascade to the east eave
    - Rain curtain columns falling into a drained ground channel
    - Underground ice cellar (冰窖) with packed/blue ice and trapdoor stair
    - Square self-raining pavilion with pyramid roof (攒尖顶) and roof basin
    - Vertical scanline-ring lifting waterwheel half-dipping into an intake pool
    - Covered corridor along the shore, lantern posts, and shore rocks
"""

# Hall platform and body
PLAT_X1, PLAT_Z1 = 2660, 5560
PLAT_X2, PLAT_Z2 = 2700, 5630
PLAT_TOP = 4
HALL_X1, HALL_Z1 = 2668, 5570
HALL_X2, HALL_Z2 = 2698, 5620
HALL_Y1, HALL_Y2 = 5, 14
ROOF_Y = 15

# Self-Raining Pavilion (自雨亭)
PAV_CX, PAV_CZ = 2680, 5672
PAV_R = 8

# Waterwheel over the intake pool
WHEEL_CX, WHEEL_CY, WHEEL_Z, WHEEL_R = 2720, 6, 5672, 8

# Taiye Pool west edge (water starts at x=2780, surface local y=2)
POOL_EDGE_X = 2780


def build_hanliang_ziyu_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Underground ice cellar (冰窖) beneath the hall
    # ------------------------------------------------------------------
    add_underground_room(
        fills, "ice cellar",
        2668, 5580, 2694, 5612,
        y_floor=-6,
        y_ceiling=-1,
        block=M.STONE,
    )
    # Ice stocks: packed ice and blue ice blocks piled along the west wall
    add_fill(fills, "ice stock packed 1", (2670, -6, 5582), (2674, -4, 5586), "minecraft:packed_ice")
    add_fill(fills, "ice stock packed 2", (2676, -6, 5592), (2680, -4, 5596), "minecraft:packed_ice")
    add_fill(fills, "ice stock packed 3", (2682, -6, 5582), (2684, -4, 5586), "minecraft:packed_ice")
    add_fill(fills, "ice stock blue 1", (2676, -6, 5582), (2680, -5, 5586), "minecraft:blue_ice")
    add_fill(fills, "ice stock blue 2", (2670, -6, 5592), (2674, -5, 5596), "minecraft:blue_ice")

    # ------------------------------------------------------------------
    # 2. Raised stone platform (~4 high) with southern entry steps
    # ------------------------------------------------------------------
    add_platform_with_steps(
        fills, "hanliang platform",
        PLAT_X1, PLAT_Z1, PLAT_X2, PLAT_Z2,
        base_y=1,
        tiers=[(3, 0, M.STONE), (1, 0, M.SMOOTH)],
    )
    add_staircase(
        fills, "hanliang south steps",
        2680, 5630, 2686, 5634,
        1, PLAT_TOP,
        "south",
        block=M.SMOOTH,
    )

    # ------------------------------------------------------------------
    # 3. Cellar stair descending from the platform + trapdoor entrance
    # ------------------------------------------------------------------
    add_staircase(
        fills, "ice cellar stair",
        2687, 5600, 2689, 5610,
        -6, PLAT_TOP,
        "south",
        block=M.SMOOTH,
    )
    # Open shaft through the platform above the stair
    add_fill(fills, "ice cellar shaft", (2687, 4, 5600), (2689, 9, 5611), M.AIR)
    # Wooden trapdoor frame flush with the platform floor
    add_outline(fills, "ice cellar trapdoor", 2686, 5599, 2690, 5601, 4, 4, M.WOOD, thickness=1)

    # ------------------------------------------------------------------
    # 4. Hanliang Hall (含凉殿): red walls, windows, door, colonnade
    # ------------------------------------------------------------------
    add_outline(fills, "hanliang walls", HALL_X1, HALL_Z1, HALL_X2, HALL_Z2, HALL_Y1, HALL_Y2, M.RED_WALL, thickness=1)
    # West window strip and east strips flanking the pool-side door
    add_fill(fills, "hanliang windows west", (HALL_X1, 8, 5575), (HALL_X1, 10, 5615), M.RED_STAINED_GLASS)
    add_fill(fills, "hanliang windows east n", (HALL_X2, 8, 5575), (HALL_X2, 10, 5590), M.RED_STAINED_GLASS)
    add_fill(fills, "hanliang windows east s", (HALL_X2, 8, 5600), (HALL_X2, 10, 5615), M.RED_STAINED_GLASS)
    # East door facing Taiye Pool, with a dark-oak lintel
    add_fill(fills, "hanliang door", (HALL_X2, 5, 5593), (HALL_X2, 9, 5597), M.AIR)
    add_fill(fills, "hanliang door lintel", (HALL_X2, 10, 5592), (HALL_X2, 10, 5598), "minecraft:dark_oak_log[axis=z]")
    # Corner pillars and interior dark-oak column grid
    for cx, cz in ((HALL_X1, HALL_Z1), (HALL_X2 - 1, HALL_Z1), (HALL_X1, HALL_Z2 - 1), (HALL_X2 - 1, HALL_Z2 - 1)):
        add_fill(fills, f"hanliang corner col {cx},{cz}", (cx, HALL_Y1, cz), (cx + 1, HALL_Y2, cz + 1), M.LOG)
    add_column_grid(
        fills, "hanliang",
        HALL_X1, HALL_Z1, HALL_X2, HALL_Z2,
        HALL_Y1, HALL_Y2,
        spacing=8,
        column_block=M.LOG,
        column_size=2,
    )

    # ------------------------------------------------------------------
    # 5. Hip roof (庑殿顶) over the hall
    # ------------------------------------------------------------------
    add_hip_roof(
        fills, "hanliang roof",
        HALL_X1, HALL_Z1, HALL_X2, HALL_Z2,
        ROOF_Y,
        layers=15,
        ridge_axis="z",
        roof_block=M.ROOF_GREEN,
    )

    # ------------------------------------------------------------------
    # 6. Roof-top imperial water tank with overflow cascade
    # ------------------------------------------------------------------
    add_fill(fills, "tank floor", (2674, 31, 5588), (2686, 31, 5602), M.STONE)
    add_outline(fills, "tank walls", 2674, 5588, 2686, 5602, 32, 35, M.STONE, thickness=1)
    add_fill(fills, "tank water", (2675, 32, 5589), (2685, 33, 5601), M.WATER)
    # Overflow notch in the east wall and a spout pouring onto the slope
    add_fill(fills, "tank overflow notch", (2686, 34, 5595), (2686, 35, 5595), M.AIR)
    add_fill(fills, "tank spout", (2687, 28, 5595), (2687, 33, 5595), M.WATER)
    for i in range(4):
        cx = 2689 + i * 3
        cy = 27 - i * 4
        add_fill(fills, f"tank cascade {i}", (cx, cy, 5594), (cx + 2, cy, 5596), M.WATER)

    # ------------------------------------------------------------------
    # 7. Rain curtain (雨帘), ground channel, and drain to Taiye Pool
    # ------------------------------------------------------------------
    for z in range(5572, 5619, 4):
        add_fill(fills, f"rain curtain {z}", (2702, 3, z), (2702, 13, z), M.WATER)
    # Shallow smooth-stone trough along the hall's east base
    add_fill(fills, "channel floor", (2701, 1, 5565), (2703, 1, 5625), M.SMOOTH)
    add_fill(fills, "channel water", (2701, 2, 5565), (2703, 2, 5625), M.WATER)
    add_fill(fills, "channel curb", (2704, 2, 5565), (2704, 2, 5625), M.SMOOTH)
    add_fill(fills, "channel cap n", (2701, 2, 5564), (2704, 2, 5564), M.SMOOTH)
    add_fill(fills, "channel cap s", (2701, 2, 5626), (2704, 2, 5626), M.SMOOTH)
    # Gap in the curb and a short water run draining east into the pool
    add_fill(fills, "channel drain gap", (2704, 2, 5593), (2704, 2, 5596), M.WATER)
    add_fill(fills, "drain floor", (2705, 1, 5593), (POOL_EDGE_X - 1, 1, 5596), M.SMOOTH)
    add_fill(fills, "drain water", (2705, 2, 5593), (POOL_EDGE_X - 1, 2, 5596), M.WATER)
    add_fill(fills, "drain curb n", (2705, 2, 5592), (POOL_EDGE_X - 1, 2, 5592), M.SMOOTH)
    add_fill(fills, "drain curb s", (2705, 2, 5597), (POOL_EDGE_X - 1, 2, 5597), M.SMOOTH)

    # ------------------------------------------------------------------
    # 8. Self-Raining Pavilion (自雨亭) south of the hall
    # ------------------------------------------------------------------
    # Apron, platform, and surrounding square water channel ring
    add_fill(fills, "ziyu apron", (2668, 1, 5660), (2692, 1, 5684), M.SMOOTH)
    add_platform_with_steps(
        fills, "ziyu platform",
        PAV_CX - PAV_R, PAV_CZ - PAV_R, PAV_CX + PAV_R, PAV_CZ + PAV_R,
        base_y=1,
        tiers=[(2, 0, M.STONE), (1, 0, M.SMOOTH)],
    )
    add_outline(fills, "ziyu channel water", 2666, 5658, 2694, 5686, 2, 2, M.WATER, thickness=2)
    add_outline(fills, "ziyu channel curb", 2665, 5657, 2695, 5687, 2, 2, M.SMOOTH, thickness=1)
    # Plank bridge from the corridor over the channel to the platform
    add_fill(fills, "ziyu bridge", (2689, 3, 5664), (2695, 3, 5666), M.WOOD)
    # Four corner columns
    for cx, cz in ((2673, 5665), (2686, 5665), (2673, 5678), (2686, 5678)):
        add_fill(fills, f"ziyu col {cx},{cz}", (cx, 4, cz), (cx + 1, 12, cz + 1), M.LOG)
    # Pyramidal roof (攒尖顶) with a roof-top water basin
    add_pyramid_roof(fills, "ziyu roof", PAV_CX, PAV_CZ, PAV_R, 13, roof_block=M.ROOF_GREEN)
    add_fill(fills, "ziyu basin floor", (2675, 19, 5667), (2685, 19, 5677), M.STONE)
    add_outline(fills, "ziyu basin walls", 2675, 5667, 2685, 5677, 20, 20, M.STONE, thickness=1)
    add_fill(fills, "ziyu basin water", (2676, 20, 5668), (2684, 20, 5676), M.WATER)
    # Water curtains falling between the four columns along the edge rows
    add_fill(fills, "ziyu curtain north", (2675, 4, 5664), (2685, 12, 5664), M.WATER)
    add_fill(fills, "ziyu curtain south", (2675, 4, 5680), (2685, 12, 5680), M.WATER)
    add_fill(fills, "ziyu curtain west", (2672, 4, 5667), (2672, 12, 5677), M.WATER)
    add_fill(fills, "ziyu curtain east", (2688, 4, 5667), (2688, 12, 5677), M.WATER)

    # ------------------------------------------------------------------
    # 9. Lifting waterwheel half-dipping into an intake pool
    # ------------------------------------------------------------------
    # Intake pool connected to Taiye Pool by a short channel
    add_fill(fills, "intake floor", (2712, -2, 5666), (2728, -1, 5678), M.SMOOTH)
    add_outline(fills, "intake walls", 2711, 5665, 2729, 5679, 0, 3, M.STONE, thickness=1)
    add_fill(fills, "intake water", (2712, 0, 5666), (2728, 2, 5678), M.WATER)
    add_fill(fills, "intake east gap", (2729, 2, 5670), (2729, 3, 5674), M.AIR)
    add_fill(fills, "intake channel floor", (2730, 1, 5670), (POOL_EDGE_X - 1, 1, 5674), M.SMOOTH)
    add_fill(fills, "intake channel water", (2730, 2, 5670), (POOL_EDGE_X - 1, 2, 5674), M.WATER)
    add_fill(fills, "intake channel curb n", (2730, 2, 5669), (POOL_EDGE_X - 1, 3, 5669), M.STONE)
    add_fill(fills, "intake channel curb s", (2730, 2, 5675), (POOL_EDGE_X - 1, 3, 5675), M.STONE)
    # Vertical scanline ring (x/y plane) with spokes and eight paddles
    r = WHEEL_R
    for dy in range(-r, r + 1):
        half = int((r * r - dy * dy) ** 0.5)
        add_fill(fills, f"wheel rim w {dy}", (WHEEL_CX - half, WHEEL_CY + dy, WHEEL_Z), (WHEEL_CX - half, WHEEL_CY + dy, WHEEL_Z), M.WOOD)
        add_fill(fills, f"wheel rim e {dy}", (WHEEL_CX + half, WHEEL_CY + dy, WHEEL_Z), (WHEEL_CX + half, WHEEL_CY + dy, WHEEL_Z), M.WOOD)
    add_fill(fills, "wheel spoke v", (WHEEL_CX, WHEEL_CY - r, WHEEL_Z), (WHEEL_CX, WHEEL_CY + r, WHEEL_Z), M.LOG)
    add_fill(fills, "wheel spoke h", (WHEEL_CX - r, WHEEL_CY, WHEEL_Z), (WHEEL_CX + r, WHEEL_CY, WHEEL_Z), M.LOG)
    for i, (dx, dy) in enumerate([(0, r), (0, -r), (r, 0), (-r, 0), (6, 6), (6, -6), (-6, 6), (-6, -6)]):
        add_fill(fills, f"wheel paddle {i}", (WHEEL_CX + dx - 2, WHEEL_CY + dy, WHEEL_Z - 1), (WHEEL_CX + dx + 2, WHEEL_CY + dy, WHEEL_Z + 1), M.SPRUCE)
    # Axle piers on both banks and the axle through the wheel hub
    add_fill(fills, "wheel pier north", (2718, 1, 5663), (2722, 5, 5665), M.STONE)
    add_fill(fills, "wheel pier south", (2718, 1, 5679), (2722, 5, 5681), M.STONE)
    add_fill(fills, "wheel axle", (WHEEL_CX, WHEEL_CY, 5663), (WHEEL_CX, WHEEL_CY, 5681), M.LOG)

    # ------------------------------------------------------------------
    # 10. Covered corridor linking hall and pavilion along the shore
    # ------------------------------------------------------------------
    add_fill(fills, "corridor floor", (2692, 3, 5631), (2698, 3, 5666), M.WOOD)
    for z in (5635, 5643, 5651, 5659):
        add_fill(fills, f"corridor col w {z}", (2692, 2, z), (2692, 9, z), M.LOG)
        add_fill(fills, f"corridor col e {z}", (2698, 2, z), (2698, 9, z), M.LOG)
    add_ridge_roof(
        fills, "corridor roof",
        2691, 5630, 2699, 5667,
        10,
        layers=2,
        ridge_axis="z",
        roof_block=M.ROOF_GREEN,
    )

    # ------------------------------------------------------------------
    # 11. Lantern posts along the shore and scattered rocks
    # ------------------------------------------------------------------
    add_lantern_line(fills, "shore lantern n", 2716, 5560, 2716, 5590, 2, 15)
    add_lantern_line(fills, "shore lantern s", 2716, 5600, 2716, 5660, 2, 15)
    for i, (rx, rz, s) in enumerate([(2745, 5570, 3), (2760, 5610, 3), (2750, 5645, 2), (2740, 5660, 2), (2755, 5680, 2), (2765, 5690, 3)]):
        add_fill(fills, f"shore rock {i}", (rx, 2, rz), (rx + s, 3 + s % 2, rz + s), M.COBBLE)


def main() -> None:
    run_builder(build_hanliang_ziyu_3d, "hanliang_ziyu_3d")


if __name__ == "__main__":
    main()
