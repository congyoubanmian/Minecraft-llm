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
    add_outline,
    add_tree,
    run_builder,
)


"""
Lishan Beacon Tower 3D (骊山烽火台) - the mountain-top signal beacon of the
"烽火戏诸侯" (beacon fire fooling the lords) legend, raised on the summit of
the Zhongnan main peak so the whole city of Chang'an can read its smoke.

Location:
    Summit of the Zhongnan main peak (cx, cz) = (3200, -680), the
    (half_width=70, height=180) entry of mountain_zhongnan.py.  That module
    lays layer y as half = max(1, 70 - y // 2): the half-width first reaches
    the clamp (1) at y = 138, then the 3x3 tip column continues up to
    y = height - 1 = 179, which is the true summit block.  The platform deck
    here is filled at y = 179, exactly level with the peak tip.  All fills
    stay inside x 3100..3300, z -780..-580.

Distinctive features:
    - 15x15 stone summit platform level with the peak tip (y=179), its rim
      weathered with mossy / cracked stone bands
    - Two-tier tapered beacon shaft (11x11 -> 9x9, 12 blocks up) crowned by
      a smooth-stone merlon parapet alternating iron-bar arrow slits
    - Central beacon basin: dark-oak tripod legs, gold bowl with a
      sea-lantern + red-wool flame and a three-segment swaying white-wool
      wolf-smoke column (9 blocks high)
    - Half-buried stone guard hut (wood roof, kang bed, stove) tucked into
      the shaft base, firewood lean-to with log stacks and hay bales
    - Signal mast flying three stepped red-wool banners
    - Stone stair hewn down the south ridge (~20 steps) and an access stair
      up the shaft's west face through a parapet gate
    - Sea-lantern watch windows on all four shaft faces, cliff pines
"""


# ---------------------------------------------------------------------------
# Summit geometry (derived from mountain_zhongnan.py, see docstring).
# ---------------------------------------------------------------------------
PEAK_X = 3200
PEAK_Z = -680
PEAK_HALF_WIDTH = 70
PEAK_HEIGHT = 180

# half = max(1, 70 - y // 2) clamps to 1 at y = 138; the 3x3 tip column runs
# on up to the last layer y = PEAK_HEIGHT - 1 = 179 = true summit block.
PEAK_TOP_Y = PEAK_HEIGHT - 1  # 179
DECK_Y = PEAK_TOP_Y           # platform surface level with the peak tip

# 15x15 platform footprint
DECK_HALF = 7
DECK_X1, DECK_X2 = PEAK_X - DECK_HALF, PEAK_X + DECK_HALF  # 3193..3207
DECK_Z1, DECK_Z2 = PEAK_Z - DECK_HALF, PEAK_Z + DECK_HALF  # -687..-673

# Summit plinth (two drums merging into the cone below the deck)
PLINTH1_Y1, PLINTH1_Y2 = 146, 167  # 15x15 lower drum
PLINTH2_Y1, PLINTH2_Y2 = 168, 178  # 13x13 upper drum

# Two-tier beacon shaft
SHAFT1_X1, SHAFT1_X2 = PEAK_X - 5, PEAK_X + 5  # 11x11 lower tier
SHAFT1_Z1, SHAFT1_Z2 = PEAK_Z - 5, PEAK_Z + 5
SHAFT1_Y1, SHAFT1_Y2 = DECK_Y + 1, DECK_Y + 6  # 180..185

SHAFT2_X1, SHAFT2_X2 = PEAK_X - 4, PEAK_X + 4  # 9x9 upper tier
SHAFT2_Z1, SHAFT2_Z2 = PEAK_Z - 4, PEAK_Z + 4
SHAFT2_Y1, SHAFT2_Y2 = DECK_Y + 7, DECK_Y + 12  # 186..191
WALK_Y = SHAFT2_Y2                              # 191 top walkway surface
PARAPET_Y1, PARAPET_Y2 = WALK_Y + 1, WALK_Y + 2  # 192..193 merlons

# Descending ridge stair (south of the deck)
PATH_STEPS = 20
PATH_X1, PATH_X2 = PEAK_X - 1, PEAK_X + 1  # 3199..3201
PATH_Z_START = DECK_Z2 + 1                 # -672, first step
PATH_TOP_Y = DECK_Y - 1                    # 178, first step top

HAY = "minecraft:hay_block"


def build_beacon_tower_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Summit platform: two stone drums capping the peak, deck at y=179
    # ------------------------------------------------------------------
    add_fill(
        fills, "beacon plinth lower",
        (DECK_X1, PLINTH1_Y1, DECK_Z1), (DECK_X2, PLINTH1_Y2, DECK_Z2), M.STONE,
    )
    add_fill(
        fills, "beacon plinth upper",
        (DECK_X1 + 1, PLINTH2_Y1, DECK_Z1 + 1), (DECK_X2 - 1, PLINTH2_Y2, DECK_Z2 - 1), M.STONE,
    )
    # Weathered deck: mossy rim, stone core, cracked patches on the lip
    add_outline(fills, "beacon deck rim", DECK_X1, DECK_Z1, DECK_X2, DECK_Z2, DECK_Y, DECK_Y, M.MOSS_STONE)
    add_fill(
        fills, "beacon deck core",
        (DECK_X1 + 1, DECK_Y, DECK_Z1 + 1), (DECK_X2 - 1, DECK_Y, DECK_Z2 - 1), M.STONE,
    )
    add_fill(fills, "beacon deck crack n", (PEAK_X - 1, DECK_Y, DECK_Z1), (PEAK_X + 1, DECK_Y, DECK_Z1), M.CRACKED_STONE)
    add_fill(fills, "beacon deck crack e", (DECK_X2, DECK_Y, PEAK_Z - 1), (DECK_X2, DECK_Y, PEAK_Z + 1), M.CRACKED_STONE)
    add_fill(fills, "beacon deck crack w", (DECK_X1, DECK_Y, PEAK_Z + 1), (DECK_X1, DECK_Y, PEAK_Z + 3), M.CRACKED_STONE)
    # Weathering bands and moss patches on the plinth faces
    add_outline(fills, "beacon plinth moss band", DECK_X1 + 1, DECK_Z1 + 1, DECK_X2 - 1, DECK_Z2 - 1, 174, 174, M.MOSS_STONE)
    add_outline(fills, "beacon plinth crack band", DECK_X1 + 1, DECK_Z1 + 1, DECK_X2 - 1, DECK_Z2 - 1, 170, 170, M.CRACKED_STONE)
    add_fill(fills, "beacon plinth moss w", (DECK_X1, 150, PEAK_Z - 4), (DECK_X1, 152, PEAK_Z), M.MOSS_STONE)
    add_fill(fills, "beacon plinth moss e", (DECK_X2, 158, PEAK_Z - 2), (DECK_X2, 160, PEAK_Z), M.MOSS_STONE)

    # ------------------------------------------------------------------
    # 2. Beacon shaft: 11x11 tier tapering to 9x9, solid beacon mound
    # ------------------------------------------------------------------
    add_fill(
        fills, "beacon shaft lower",
        (SHAFT1_X1, SHAFT1_Y1, SHAFT1_Z1), (SHAFT1_X2, SHAFT1_Y2, SHAFT1_Z2), M.STONE,
    )
    add_fill(
        fills, "beacon shaft upper",
        (SHAFT2_X1, SHAFT2_Y1, SHAFT2_Z1), (SHAFT2_X2, SHAFT2_Y2, SHAFT2_Z2), M.STONE,
    )
    # Shaft weathering patches
    add_fill(fills, "beacon shaft moss s", (PEAK_X - 2, SHAFT1_Y1 + 1, SHAFT1_Z2), (PEAK_X + 2, SHAFT1_Y1 + 2, SHAFT1_Z2), M.MOSS_STONE)
    add_fill(fills, "beacon shaft crack w", (SHAFT1_X1, SHAFT1_Y2 - 1, PEAK_Z - 2), (SHAFT1_X1, SHAFT1_Y2, PEAK_Z + 2), M.CRACKED_STONE)
    add_fill(fills, "beacon shaft moss e", (SHAFT2_X2, SHAFT2_Y1 + 1, PEAK_Z - 2), (SHAFT2_X2, SHAFT2_Y1 + 2, PEAK_Z + 2), M.MOSS_STONE)
    add_fill(fills, "beacon shaft crack n", (PEAK_X - 2, SHAFT2_Y2 - 2, SHAFT2_Z1), (PEAK_X + 2, SHAFT2_Y2 - 1, SHAFT2_Z1), M.CRACKED_STONE)

    # ------------------------------------------------------------------
    # 3. Watch windows: sea-lantern lamps mid-shaft on all four faces
    # ------------------------------------------------------------------
    add_fill(fills, "beacon window lower n", (PEAK_X, SHAFT1_Y1 + 3, SHAFT1_Z1), (PEAK_X, SHAFT1_Y1 + 3, SHAFT1_Z1), M.SEA_LANTERN)
    add_fill(fills, "beacon window lower s", (PEAK_X, SHAFT1_Y1 + 3, SHAFT1_Z2), (PEAK_X, SHAFT1_Y1 + 3, SHAFT1_Z2), M.SEA_LANTERN)
    add_fill(fills, "beacon window lower w", (SHAFT1_X1, SHAFT1_Y1 + 3, PEAK_Z), (SHAFT1_X1, SHAFT1_Y1 + 3, PEAK_Z), M.SEA_LANTERN)
    add_fill(fills, "beacon window lower e", (SHAFT1_X2, SHAFT1_Y1 + 3, PEAK_Z), (SHAFT1_X2, SHAFT1_Y1 + 3, PEAK_Z), M.SEA_LANTERN)
    add_fill(fills, "beacon window upper n", (PEAK_X, SHAFT2_Y1 + 2, SHAFT2_Z1), (PEAK_X, SHAFT2_Y1 + 2, SHAFT2_Z1), M.SEA_LANTERN)
    add_fill(fills, "beacon window upper s", (PEAK_X, SHAFT2_Y1 + 2, SHAFT2_Z2), (PEAK_X, SHAFT2_Y1 + 2, SHAFT2_Z2), M.SEA_LANTERN)
    add_fill(fills, "beacon window upper w", (SHAFT2_X1, SHAFT2_Y1 + 2, PEAK_Z), (SHAFT2_X1, SHAFT2_Y1 + 2, PEAK_Z), M.SEA_LANTERN)
    add_fill(fills, "beacon window upper e", (SHAFT2_X2, SHAFT2_Y1 + 2, PEAK_Z), (SHAFT2_X2, SHAFT2_Y1 + 2, PEAK_Z), M.SEA_LANTERN)

    # Arrow slits (dark air slots) flanking the lower windows
    for off in (-3, 3):
        add_fill(fills, f"beacon slit n {off}", (PEAK_X + off, SHAFT1_Y2 - 1, SHAFT1_Z1), (PEAK_X + off, SHAFT1_Y2, SHAFT1_Z1), M.AIR)
        add_fill(fills, f"beacon slit s {off}", (PEAK_X + off, SHAFT1_Y2 - 1, SHAFT1_Z2), (PEAK_X + off, SHAFT1_Y2, SHAFT1_Z2), M.AIR)
        add_fill(fills, f"beacon slit w {off}", (SHAFT1_X1, SHAFT1_Y2 - 1, PEAK_Z + off), (SHAFT1_X1, SHAFT1_Y2, PEAK_Z + off), M.AIR)
        add_fill(fills, f"beacon slit e {off}", (SHAFT1_X2, SHAFT1_Y2 - 1, PEAK_Z + off), (SHAFT1_X2, SHAFT1_Y2, PEAK_Z + off), M.AIR)

    # ------------------------------------------------------------------
    # 4. Access stair up the west face to the top walkway
    # ------------------------------------------------------------------
    for i in range(12):
        add_fill(
            fills, f"beacon shaft stair {i}",
            (SHAFT1_X1 - 1, SHAFT1_Y1 + i, PEAK_Z - 1), (SHAFT1_X1, SHAFT1_Y1 + i, PEAK_Z + 1), M.SMOOTH,
        )

    # ------------------------------------------------------------------
    # 5. Top cornice and merlon parapet (SMOOTH merlons / IRON_BARS slits)
    # ------------------------------------------------------------------
    add_outline(fills, "beacon cornice", SHAFT2_X1, SHAFT2_Z1, SHAFT2_X2, SHAFT2_Z2, WALK_Y, WALK_Y, M.SMOOTH)

    perimeter: list[tuple[int, int]] = []
    for x in range(SHAFT2_X1, SHAFT2_X2 + 1):           # north edge, west -> east
        perimeter.append((x, SHAFT2_Z1))
    for z in range(SHAFT2_Z1 + 1, SHAFT2_Z2 + 1):       # east edge
        perimeter.append((SHAFT2_X2, z))
    for x in range(SHAFT2_X2 - 1, SHAFT2_X1 - 1, -1):   # south edge, east -> west
        perimeter.append((x, SHAFT2_Z2))
    for z in range(SHAFT2_Z2 - 1, SHAFT2_Z1, -1):       # west edge, south -> north
        perimeter.append((SHAFT2_X1, z))
    gate = {(SHAFT2_X1, PEAK_Z - 1), (SHAFT2_X1, PEAK_Z), (SHAFT2_X1, PEAK_Z + 1)}
    for i, (x, z) in enumerate(perimeter):
        if (x, z) in gate:
            continue  # entrance gap where the west stair arrives
        block = M.IRON_BARS if i % 3 == 2 else M.SMOOTH
        add_fill(fills, f"beacon merlon {i}", (x, PARAPET_Y1, z), (x, PARAPET_Y2, z), block)

    # ------------------------------------------------------------------
    # 6. Central beacon basin: tripod, gold bowl, flame and wolf smoke
    # ------------------------------------------------------------------
    base_y = PARAPET_Y1  # 192, legs stand on the walkway
    for lx, lz in ((PEAK_X - 1, PEAK_Z - 1), (PEAK_X + 1, PEAK_Z - 1), (PEAK_X, PEAK_Z + 1)):
        add_fill(fills, f"beacon tripod {lx},{lz}", (lx, base_y, lz), (lx, base_y + 1, lz), M.LOG)
    add_fill(fills, "beacon basin base", (PEAK_X - 1, base_y + 2, PEAK_Z - 1), (PEAK_X + 1, base_y + 2, PEAK_Z + 1), M.GOLD)
    add_outline(fills, "beacon basin rim", PEAK_X - 1, PEAK_Z - 1, PEAK_X + 1, PEAK_Z + 1, base_y + 3, base_y + 3, M.GOLD)
    add_fill(fills, "beacon flame core", (PEAK_X, base_y + 3, PEAK_Z), (PEAK_X, base_y + 3, PEAK_Z), M.SEA_LANTERN)
    add_fill(fills, "beacon flame tip", (PEAK_X, base_y + 4, PEAK_Z), (PEAK_X, base_y + 4, PEAK_Z), M.RED_WOOL)
    # Wolf smoke: three 3-high white-wool segments, each offset 1 block
    add_fill(fills, "beacon smoke 1", (PEAK_X, base_y + 5, PEAK_Z), (PEAK_X, base_y + 7, PEAK_Z), M.WHITE_WOOL)
    add_fill(fills, "beacon smoke 2", (PEAK_X + 1, base_y + 8, PEAK_Z), (PEAK_X + 1, base_y + 10, PEAK_Z), M.WHITE_WOOL)
    add_fill(fills, "beacon smoke 3", (PEAK_X, base_y + 11, PEAK_Z - 1), (PEAK_X, base_y + 13, PEAK_Z - 1), M.WHITE_WOOL)

    # ------------------------------------------------------------------
    # 7. Guard hut: half-buried stone cell tucked into the shaft NW corner
    # ------------------------------------------------------------------
    hut_x1, hut_x2 = DECK_X1, PEAK_X - 1       # 3193..3199
    hut_z1, hut_z2 = DECK_Z1, PEAK_Z - 4       # -687..-684
    add_hollow_box(fills, "beacon hut", hut_x1, DECK_Y + 1, hut_z1, hut_x2, DECK_Y + 4, hut_z2, M.STONE, thickness=1)
    add_fill(fills, "beacon hut door", (DECK_X1 + 1, DECK_Y + 1, hut_z2), (DECK_X1 + 1, DECK_Y + 2, hut_z2), M.AIR)
    add_fill(fills, "beacon hut window", (PEAK_X - 4, DECK_Y + 2, hut_z1), (PEAK_X - 4, DECK_Y + 2, hut_z1), M.GLASS)
    add_fill(fills, "beacon hut kang", (DECK_X1 + 1, DECK_Y + 1, hut_z1 + 1), (DECK_X1 + 2, DECK_Y + 1, hut_z1 + 2), M.WOOD)
    add_fill(fills, "beacon hut stove", (hut_x2 - 1, DECK_Y + 1, hut_z1 + 1), (hut_x2 - 1, DECK_Y + 2, hut_z1 + 1), M.ANDESITE)
    add_fill(fills, "beacon hut roof", (hut_x1, DECK_Y + 5, hut_z1), (hut_x2, DECK_Y + 5, hut_z2), M.WOOD)
    add_fill(fills, "beacon hut ridge", (hut_x1 + 1, DECK_Y + 6, hut_z1 + 1), (hut_x2 - 1, DECK_Y + 6, hut_z1 + 1), f"{M.LOG}[axis=x]")
    add_fill(fills, "beacon hut eave fence", (hut_x1, DECK_Y + 6, hut_z1), (hut_x2, DECK_Y + 6, hut_z1), M.FENCE)
    # Lantern post beside the door
    add_fill(fills, "beacon hut lamp post", (DECK_X1 + 2, DECK_Y + 1, hut_z2 + 1), (DECK_X1 + 2, DECK_Y + 2, hut_z2 + 1), M.FENCE)
    add_fill(fills, "beacon hut lamp", (DECK_X1 + 2, DECK_Y + 3, hut_z2 + 1), (DECK_X1 + 2, DECK_Y + 3, hut_z2 + 1), M.LANTERN)

    # ------------------------------------------------------------------
    # 8. Firewood lean-to against the shaft's east face
    # ------------------------------------------------------------------
    shed_z1, shed_z2 = PEAK_Z - 3, PEAK_Z + 3  # -683..-677
    shed_x1, shed_x2 = SHAFT2_X2 + 2, SHAFT1_X2 + 2  # 3206..3207
    add_fill(fills, "beacon shed post n", (shed_x2, DECK_Y + 1, shed_z1), (shed_x2, DECK_Y + 3, shed_z1), M.LOG)
    add_fill(fills, "beacon shed post s", (shed_x2, DECK_Y + 1, shed_z2), (shed_x2, DECK_Y + 3, shed_z2), M.LOG)
    add_fill(fills, "beacon shed roof", (shed_x1, DECK_Y + 4, shed_z1), (shed_x2, DECK_Y + 4, shed_z2), M.WOOD)
    add_fill(fills, "beacon shed beam", (shed_x1, DECK_Y + 3, PEAK_Z), (shed_x2, DECK_Y + 3, PEAK_Z), f"{M.LOG}[axis=z]")
    add_fill(fills, "beacon firewood 1", (shed_x1, DECK_Y + 1, PEAK_Z - 1), (shed_x2, DECK_Y + 2, PEAK_Z), M.LOG)
    add_fill(fills, "beacon firewood 2", (shed_x1, DECK_Y + 1, PEAK_Z + 1), (shed_x2, DECK_Y + 1, PEAK_Z + 1), M.LOG)
    add_fill(fills, "beacon hay 1", (shed_x1, DECK_Y + 1, shed_z1), (shed_x2, DECK_Y + 1, shed_z1 + 1), HAY)
    add_fill(fills, "beacon hay 2", (shed_x1, DECK_Y + 2, shed_z1), (shed_x2, DECK_Y + 2, shed_z1), HAY)

    # ------------------------------------------------------------------
    # 9. Signal mast: 14-block pole with three stepped red banners
    # ------------------------------------------------------------------
    mast_x, mast_z = DECK_X1 + 1, DECK_Z2 - 6  # 3194, -674
    add_fill(fills, "beacon mast base", (DECK_X1, DECK_Y + 1, DECK_Z2 - 7), (DECK_X1 + 2, DECK_Y + 1, DECK_Z2 - 5), M.WHITE_TERRACOTTA)
    add_fill(fills, "beacon mast pole", (mast_x, DECK_Y + 1, mast_z), (mast_x, DECK_Y + 14, mast_z), M.LOG)
    add_fill(fills, "beacon flag high", (mast_x - 2, DECK_Y + 12, mast_z), (mast_x - 1, DECK_Y + 12, mast_z), M.RED_WOOL)
    add_fill(fills, "beacon flag mid", (mast_x - 2, DECK_Y + 9, mast_z), (mast_x - 1, DECK_Y + 9, mast_z), M.RED_WOOL)
    add_fill(fills, "beacon flag low", (mast_x - 2, DECK_Y + 6, mast_z), (mast_x - 1, DECK_Y + 6, mast_z), M.RED_WOOL)

    # ------------------------------------------------------------------
    # 10. Descending ridge stair: ~20 hewn steps down the south face
    # ------------------------------------------------------------------
    for i in range(PATH_STEPS):
        top_y = PATH_TOP_Y - 2 * i
        z = PATH_Z_START + i
        add_fill(
            fills, f"beacon path step {i}",
            (PATH_X1, top_y - 1, z), (PATH_X2, top_y, z), M.STONE,
        )
    # Buttress spurs where the stair rides over open air
    for i in range(0, PATH_STEPS, 4):
        top_y = PATH_TOP_Y - 2 * i
        z = PATH_Z_START + i
        add_fill(
            fills, f"beacon path spur {i}",
            (PATH_X1 - 1, top_y - 3, z), (PATH_X2 + 1, top_y - 2, z), M.STONE,
        )

    # ------------------------------------------------------------------
    # 11. Cliff pines flanking the stair head and the north-east corner
    # ------------------------------------------------------------------
    add_tree(fills, "beacon pine south", PEAK_X - 3, DECK_Z2 - 1, DECK_Y + 1, height=5, spread=2)
    add_tree(fills, "beacon pine corner", DECK_X2 - 1, DECK_Z1 + 1, DECK_Y + 1, height=5, spread=2)

    # ------------------------------------------------------------------
    # 12. Commemorative stele by the stair head
    # ------------------------------------------------------------------
    add_fill(fills, "beacon stele base", (PEAK_X + 2, DECK_Y + 1, DECK_Z2), (PEAK_X + 4, DECK_Y + 1, DECK_Z2), M.WHITE_TERRACOTTA)
    add_fill(fills, "beacon stele body", (PEAK_X + 3, DECK_Y + 2, DECK_Z2), (PEAK_X + 3, DECK_Y + 4, DECK_Z2), M.QUARTZ)
    add_fill(fills, "beacon stele cap", (PEAK_X + 3, DECK_Y + 5, DECK_Z2), (PEAK_X + 3, DECK_Y + 5, DECK_Z2), M.GOLD)


def main() -> None:
    run_builder(build_beacon_tower_3d, "beacon_tower_3d")


if __name__ == "__main__":
    main()
