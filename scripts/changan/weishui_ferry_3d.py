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
    run_builder,
)


"""
Weishui Ferry 3D (渭水·咸阳古渡) - the great north-gate river crossing of
Chang'an on the Wei River; "咸阳古渡" (the Old Xianyang Ferry) is one of
the Eight Views of Guanzhong. There is deliberately NO bridge here:
travellers cross the Wei only by ferry boat.

Location in Chang'an city local coordinates:
    Far north suburb, beyond the farmland belt: x 1000..5000, z 7000..7400.
    The Wei River runs east-west across the whole plot, channel
    z 7150..7190 (40 wide), sandy bed at y0, water surface y1..2.

Distinctive features:
    - Full ground levelling (stone base y0..1 + grass y2..3) followed by
      a carved river channel with masonry banks on both sides
    - A ferry landing instead of a bridge: wide stone stepways descending
      level by level INTO the water, a timber trestle pier reaching over
      the channel, mooring posts linked by iron-bar hawsers
    - Two double-mast ferries with dark-oak hulls, hollow cabins, decks,
      one red and one white wool sail each and stern sweeps (船尾橹):
      one moored alongside the pier, one under way mid-river
    - A stone memorial archway (石牌坊) with gold plaque and the
      "咸阳古渡" stele (quartz body, gold cap) behind the landing
    - A river-god shrine (河神祠) on a terrace east of the landing:
      red hall, pyramid roof (攒尖顶) and an incense burner
    - A waiting shed with hay roof, benches, and a tea stall with stove
    - A boatmen's towpath along the north bank with tether stones and
      reed clumps (芦苇) on both shoals
"""

# Plot and ground levels (match baliu_3d convention: stone base, grass top).
PLAIN_X1, PLAIN_X2 = 1000, 5000
PLAIN_Z1, PLAIN_Z2 = 7000, 7400

# Wei River channel and masonry banks (banks lie north/south of the channel).
RIVER_Z1, RIVER_Z2 = 7150, 7190
BANK_N_Z1, BANK_N_Z2 = 7142, 7149
BANK_S_Z1, BANK_S_Z2 = 7191, 7198

# Ferry landing zone (渡口区) on the south bank, x 2800..3100.
PLAZA_X1, PLAZA_X2 = 2860, 3040
PLAZA_Z1, PLAZA_Z2 = 7206, 7266
PIER_X1, PIER_X2 = 2935, 2965
PIER_Z1, PIER_Z2 = 7158, 7205

# River-god shrine centre.
SHRINE_CX, SHRINE_CZ = 3150, 7250

HAY = "minecraft:hay_block"
SAND = "minecraft:sand"
BARREL = "minecraft:barrel"


def _willow(fills: list[Fill], label: str, x: int, z: int, y: int) -> None:
    """Riverside willow: leaf canopy with four drooping curtain columns."""
    add_fill(fills, f"{label} trunk", (x, y, z), (x, y + 6, z), M.LOG)
    add_fill(fills, f"{label} canopy", (x - 3, y + 5, z - 3), (x + 3, y + 7, z + 3), M.LEAVES)
    add_fill(fills, f"{label} crown", (x - 2, y + 8, z - 2), (x + 2, y + 8, z + 2), M.LEAVES)
    for dx, dz in ((-4, 0), (4, 0), (0, -4), (0, 4)):
        add_fill(fills, f"{label} curtain {dx},{dz}", (x + dx, y + 2, z + dz), (x + dx, y + 4, z + dz), M.LEAVES)


def _reeds(fills: list[Fill], label: str, x: int, z: int, y: int) -> None:
    """Reed clump (芦苇): small leaf cube with a taller centre spike."""
    add_fill(fills, f"{label} clump", (x - 1, y, z - 1), (x + 1, y + 1, z + 1), M.LEAVES)
    add_fill(fills, f"{label} spike", (x, y + 2, z), (x, y + 3, z), M.LEAVES)


def _ferry(fills: list[Fill], label: str, x1: int, x2: int, z1: int, z2: int) -> None:
    """Double-mast wool-sail ferry (双帆渡船): dark-oak hull with a hollow
    cabin, deck one block above the waterline, one red and one white sail
    hung from log yards, and a stern sweep (船尾橹) aft."""
    cz = (z1 + z2) // 2
    cx = (x1 + x2) // 2
    # Hull bottom on the sandy bed, with tapered bow and stern tips.
    add_fill(fills, f"{label} hull bottom", (x1 + 2, 0, z1 + 1), (x2 - 2, 0, z2 - 1), M.WOOD)
    add_fill(fills, f"{label} bow tip", (x1, 0, cz - 2), (x1 + 1, 0, cz + 2), M.WOOD)
    add_fill(fills, f"{label} stern tip", (x2 - 1, 0, cz - 2), (x2, 0, cz + 2), M.WOOD)
    # Hull sides up to the gunwale (y4); the waterline sits at y2.
    add_fill(fills, f"{label} side n", (x1, 1, z1), (x2, 4, z1), M.LOG)
    add_fill(fills, f"{label} side s", (x1, 1, z2), (x2, 4, z2), M.LOG)
    add_fill(fills, f"{label} bow stem", (x1, 1, z1), (x1, 4, z2), M.LOG)
    add_fill(fills, f"{label} stern transom", (x2, 1, z1), (x2, 4, z2), M.LOG)
    # Deck and a hollow cabin amidships with a door on the south side.
    add_fill(fills, f"{label} deck", (x1 + 1, 3, z1 + 1), (x2 - 1, 3, z2 - 1), M.WOOD)
    add_hollow_box(fills, f"{label} cabin", cx - 8, 4, z1 + 3, cx + 8, 6, z2 - 3, M.WOOD)
    add_fill(fills, f"{label} cabin door", (cx - 1, 4, z2 - 3), (cx + 1, 5, z2 - 3), M.AIR)
    # Two masts with wool sails (one red, one white) hung from log yards.
    add_fill(fills, f"{label} mast fore", (cx + 14, 4, cz), (cx + 14, 16, cz), M.LOG)
    add_fill(fills, f"{label} mast main", (cx - 14, 4, cz), (cx - 14, 18, cz), M.LOG)
    add_fill(fills, f"{label} yard fore", (cx + 14, 13, z1 + 3), (cx + 14, 13, z2 - 3), M.LOG)
    add_fill(fills, f"{label} yard main", (cx - 14, 15, z1 + 3), (cx - 14, 15, z2 - 3), M.LOG)
    add_fill(fills, f"{label} sail fore", (cx + 14, 8, z1 + 4), (cx + 14, 12, z2 - 4), M.RED_WOOL)
    add_fill(fills, f"{label} sail main", (cx - 14, 9, z1 + 4), (cx - 14, 14, z2 - 4), M.WHITE_WOOL)
    # Stern sweep (船尾橹) on a pivot post, reaching out over the water.
    add_fill(fills, f"{label} oar post", (x2 - 2, 5, cz), (x2 - 2, 6, cz), M.LOG)
    add_fill(fills, f"{label} oar loom", (x2 + 1, 5, cz), (x2 + 4, 5, cz), M.LOG)
    add_fill(fills, f"{label} oar blade", (x2 + 5, 4, cz), (x2 + 6, 4, cz), M.WOOD)
    # Bow lantern and a deck cargo of barrels.
    add_fill(fills, f"{label} bow lantern", (x1 + 2, 4, cz), (x1 + 2, 4, cz), M.LANTERN)
    add_fill(fills, f"{label} cargo", (cx + 4, 4, cz - 2), (cx + 6, 5, cz + 2), BARREL)


def build_weishui_ferry_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 0. Level the whole river plain first (stone base, grass on top).
    # ------------------------------------------------------------------
    add_fill(fills, "weishui plain base", (PLAIN_X1, 0, PLAIN_Z1), (PLAIN_X2, 1, PLAIN_Z2), M.STONE)
    add_fill(fills, "weishui plain grass", (PLAIN_X1, 2, PLAIN_Z1), (PLAIN_X2, 3, PLAIN_Z2), M.GRASS)

    # ------------------------------------------------------------------
    # 1. The Wei River (渭水): carve the channel, sandy bed, water, then
    #    masonry banks on both sides (order follows baliu_3d). No bridge:
    #    the crossing is by ferry only.
    # ------------------------------------------------------------------
    add_fill(fills, "weishui river carve", (PLAIN_X1, -3, RIVER_Z1), (PLAIN_X2, 4, RIVER_Z2), M.AIR)
    add_fill(fills, "weishui river bed", (PLAIN_X1, 0, RIVER_Z1), (PLAIN_X2, 0, RIVER_Z2), SAND)
    add_fill(fills, "weishui river water", (PLAIN_X1, 1, RIVER_Z1), (PLAIN_X2, 2, RIVER_Z2), M.WATER)
    add_fill(fills, "weishui bank n", (PLAIN_X1, -3, BANK_N_Z1), (PLAIN_X2, 2, BANK_N_Z2), M.STONE)
    add_fill(fills, "weishui bank s", (PLAIN_X1, -3, BANK_S_Z1), (PLAIN_X2, 2, BANK_S_Z2), M.STONE)
    add_fill(fills, "weishui bank n top", (PLAIN_X1, 3, BANK_N_Z1), (PLAIN_X2, 3, BANK_N_Z2), M.SMOOTH)
    add_fill(fills, "weishui bank s top", (PLAIN_X1, 3, BANK_S_Z1), (PLAIN_X2, 3, BANK_S_Z2), M.SMOOTH)

    # ------------------------------------------------------------------
    # 2. Ferry landing (渡口): plaza, stone stepways descending INTO the
    #    water, timber trestle pier, mooring posts and hawsers.
    # ------------------------------------------------------------------
    add_fill(fills, "weishui plaza", (PLAZA_X1, 4, PLAZA_Z1), (PLAZA_X2, 5, PLAZA_Z2), M.STONE)
    add_fill(fills, "weishui plaza step sw", (2880, 4, 7267), (2902, 4, 7269), M.SMOOTH)
    add_fill(fills, "weishui plaza step se", (2998, 4, 7267), (3020, 4, 7269), M.SMOOTH)
    add_fill(fills, "weishui plaza step w", (2854, 4, 7226), (2859, 4, 7246), M.SMOOTH)
    add_fill(fills, "weishui plaza step e", (3041, 4, 7226), (3046, 4, 7246), M.SMOOTH)

    # Stone stepways: each step its own add_fill, sinking below the water
    # surface (y2) down to the sandy bed (y0) - a ferry slipway.
    for tag, sx1, sx2 in (("w", 2900, 2930), ("e", 2970, 3000)):
        add_fill(fills, f"weishui stair {tag} plaza", (sx1, 0, 7204), (sx2, 4, 7205), M.STONE)
        add_fill(fills, f"weishui stair {tag} bank", (sx1, 0, 7202), (sx2, 3, 7203), M.STONE)
        add_fill(fills, f"weishui stair {tag} edge cut", (sx1, 3, 7191), (sx2, 3, 7191), M.AIR)
        add_fill(fills, f"weishui stair {tag} step 1", (sx1, 0, 7189), (sx2, 2, 7190), M.STONE)
        add_fill(fills, f"weishui stair {tag} step 2", (sx1, 0, 7187), (sx2, 1, 7188), M.STONE)
        add_fill(fills, f"weishui stair {tag} step 3", (sx1, 0, 7185), (sx2, 0, 7186), M.STONE)

    # Timber trestle pier reaching out over the channel (deck at y5).
    add_fill(fills, "weishui pier deck", (PIER_X1, 5, PIER_Z1), (PIER_X2, 5, PIER_Z2), M.WOOD)
    add_fill(fills, "weishui pier rail w", (PIER_X1, 6, PIER_Z1), (PIER_X1, 6, PIER_Z2), M.FENCE)
    add_fill(fills, "weishui pier rail e", (PIER_X2, 6, PIER_Z1), (PIER_X2, 6, PIER_Z2), M.FENCE)
    for px in (PIER_X1 + 1, PIER_X2 - 1):
        for pz in (7160, 7176, 7192):
            add_fill(fills, f"weishui pier pile {px},{pz}", (px, 0, pz), (px, 4, pz), M.LOG)
    # Gangplank down to the moored ferry plus two iron-bar hawsers.
    add_fill(fills, "weishui gangplank", (2966, 4, 7164), (2967, 4, 7168), M.WOOD)
    add_fill(fills, "weishui hawser n", (2966, 5, 7162), (2967, 5, 7162), M.IRON_BARS)
    add_fill(fills, "weishui hawser s", (2966, 5, 7170), (2967, 5, 7170), M.IRON_BARS)

    # Mooring posts (系船桩) along the quay edge, rope lines between them.
    for mx in (2880, 2960, 3040):
        add_fill(fills, f"weishui mooring post {mx}", (mx, 6, 7208), (mx, 9, 7208), M.LOG)
        add_fill(fills, f"weishui mooring cap {mx}", (mx, 10, 7208), (mx, 10, 7208), M.GOLD)
    add_fill(fills, "weishui mooring line w", (2880, 8, 7208), (2960, 8, 7208), M.IRON_BARS)
    add_fill(fills, "weishui mooring line e", (2960, 8, 7208), (3040, 8, 7208), M.IRON_BARS)
    add_lantern_line(fills, "weishui plaza lanterns", 2880, 7214, 3000, 7214, y=6, every=40)

    # ------------------------------------------------------------------
    # 3. Two double-mast ferries (双帆渡船): one moored at the pier, one
    #    under way mid-river. Built after the water so hulls displace it.
    # ------------------------------------------------------------------
    _ferry(fills, "weishui ferry moored", 2968, 3028, 7160, 7172)
    _ferry(fills, "weishui ferry underway", 3270, 3330, 7164, 7176)

    # ------------------------------------------------------------------
    # 4. Stone memorial archway (石牌坊) and the "咸阳古渡" stele behind
    #    the landing.
    # ------------------------------------------------------------------
    add_fill(fills, "weishui paifang base", (2910, 4, 7268), (2986, 5, 7276), M.STONE)
    add_fill(fills, "weishui paifang pillar w", (2916, 6, 7270), (2917, 15, 7271), M.QUARTZ)
    add_fill(fills, "weishui paifang pillar e", (2979, 6, 7270), (2980, 15, 7271), M.QUARTZ)
    add_fill(fills, "weishui paifang beam low", (2916, 13, 7269), (2980, 14, 7272), M.QUARTZ)
    add_fill(fills, "weishui paifang beam top", (2912, 15, 7268), (2984, 16, 7273), M.QUARTZ)
    add_fill(fills, "weishui paifang plaque", (2938, 13, 7268), (2958, 14, 7268), M.GOLD)
    add_fill(fills, "weishui paifang cap 1", (2910, 17, 7266), (2986, 17, 7275), M.QUARTZ)
    add_fill(fills, "weishui paifang cap 2", (2922, 18, 7268), (2974, 18, 7273), M.QUARTZ)
    add_fill(fills, "weishui paifang finial", (2944, 19, 7269), (2952, 20, 7272), M.GOLD)
    add_fill(fills, "weishui paifang step w", (2902, 4, 7270), (2909, 4, 7275), M.SMOOTH)
    add_fill(fills, "weishui paifang step e", (2987, 4, 7270), (2994, 4, 7275), M.SMOOTH)

    add_fill(fills, "weishui stele plinth", (3026, 6, 7246), (3036, 6, 7258), M.STONE)
    add_fill(fills, "weishui stele back", (3027, 7, 7247), (3028, 15, 7256), M.QUARTZ)
    add_fill(fills, "weishui stele body", (3029, 7, 7249), (3032, 15, 7254), M.QUARTZ)
    add_fill(fills, "weishui stele cap", (3028, 16, 7248), (3033, 17, 7255), M.GOLD)
    add_fill(fills, "weishui stele lantern s", (3027, 6, 7244), (3027, 6, 7244), M.LANTERN)
    add_fill(fills, "weishui stele lantern n", (3027, 6, 7260), (3027, 6, 7260), M.LANTERN)

    # ------------------------------------------------------------------
    # 5. River-god shrine (河神祠) east of the landing: terrace, red hall,
    #    pyramid roof (攒尖顶), altar and incense burner.
    # ------------------------------------------------------------------
    add_fill(fills, "weishui shrine terrace", (3128, 4, 7228), (3172, 5, 7272), M.STONE)
    add_fill(fills, "weishui shrine terrace step", (3144, 4, 7273), (3156, 4, 7275), M.SMOOTH)
    add_outline(fills, "weishui shrine rail", 3128, 7228, 3172, 7272, 6, 6, M.FENCE, thickness=1)
    add_hollow_box(fills, "weishui shrine hall", 3140, 6, 7240, 3160, 12, 7260, M.RED_WALL, thickness=1)
    add_fill(fills, "weishui shrine door s", (3147, 6, 7260), (3153, 9, 7260), M.AIR)
    add_fill(fills, "weishui shrine door n", (3147, 6, 7240), (3153, 9, 7240), M.AIR)
    for cx0, cz0 in ((3140, 7240), (3159, 7240), (3140, 7259), (3159, 7259)):
        add_fill(fills, f"weishui shrine col {cx0},{cz0}", (cx0, 6, cz0), (cx0 + 1, 12, cz0 + 1), M.LOG)
    add_pyramid_roof(fills, "weishui shrine roof", SHRINE_CX, SHRINE_CZ, radius=12, y=13,
                     roof_block=M.ROOF_GREEN, apex_block=M.GOLD)
    add_fill(fills, "weishui shrine altar", (3145, 6, 7255), (3155, 7, 7258), M.WOOD)
    add_fill(fills, "weishui shrine burner", (3147, 6, 7264), (3153, 7, 7268), BARREL)
    add_fill(fills, "weishui burner cap", (3148, 8, 7265), (3152, 8, 7267), M.GOLD)
    add_fill(fills, "weishui shrine lantern sw", (3134, 6, 7234), (3134, 6, 7234), M.LANTERN)
    add_fill(fills, "weishui shrine lantern ne", (3166, 6, 7266), (3166, 6, 7266), M.LANTERN)

    # ------------------------------------------------------------------
    # 6. Waiting shed (候船草棚) with hay roof and benches, plus the tea
    #    stall (茶摊) with counter, stove and kettle.
    # ------------------------------------------------------------------
    add_fill(fills, "weishui shed floor", (2696, 4, 7206), (2768, 4, 7246), M.SMOOTH)
    for px, pz in ((2700, 7210), (2700, 7242), (2734, 7210), (2734, 7242), (2764, 7210), (2764, 7242)):
        add_fill(fills, f"weishui shed post {px},{pz}", (px, 5, pz), (px, 10, pz), M.LOG)
    add_fill(fills, "weishui shed hay roof", (2694, 11, 7204), (2770, 12, 7248), HAY)
    add_fill(fills, "weishui shed bench s", (2706, 5, 7236), (2758, 6, 7239), M.WOOD)
    add_fill(fills, "weishui shed bench n", (2706, 5, 7213), (2758, 6, 7216), M.WOOD)
    add_fill(fills, "weishui shed lantern", (2732, 10, 7226), (2732, 10, 7226), M.LANTERN)

    add_fill(fills, "weishui tea floor", (2774, 4, 7212), (2800, 4, 7242), M.SMOOTH)
    for px, pz in ((2776, 7214), (2776, 7240), (2798, 7214), (2798, 7240)):
        add_fill(fills, f"weishui tea post {px},{pz}", (px, 5, pz), (px, 8, pz), M.LOG)
    add_fill(fills, "weishui tea hay roof", (2772, 9, 7210), (2802, 10, 7244), HAY)
    add_fill(fills, "weishui tea counter", (2778, 5, 7216), (2796, 6, 7221), M.WOOD)
    add_fill(fills, "weishui tea shelf", (2776, 5, 7236), (2798, 7, 7238), BARREL)
    add_fill(fills, "weishui tea stove", (2784, 5, 7227), (2790, 7, 7233), M.COBBLE)
    add_fill(fills, "weishui tea kettle", (2786, 8, 7229), (2788, 8, 7231), BARREL)
    add_fill(fills, "weishui tea chimney", (2787, 8, 7233), (2787, 11, 7233), M.COBBLE)
    add_fill(fills, "weishui tea sign", (2785, 8, 7211), (2789, 8, 7211), M.GOLD)

    # ------------------------------------------------------------------
    # 7. Boatmen towpath (纤夫栈道) along the north bank: narrow stone
    #    flags, tether stones (拴纤石) and reed clumps on both shoals.
    # ------------------------------------------------------------------
    add_fill(fills, "weishui towpath", (1100, 3, 7141), (4900, 3, 7145), M.ANDESITE)
    for bx in (1200, 1700, 2200, 2700, 3400, 3900, 4400, 4900):
        add_fill(fills, f"weishui tether stone {bx}", (bx, 4, 7143), (bx, 5, 7143), M.STONE)
        add_fill(fills, f"weishui tether cap {bx}", (bx, 6, 7143), (bx, 6, 7143), M.SMOOTH)
    for rx, rz in ((1250, 7148), (1750, 7148), (2250, 7148), (3350, 7148), (3850, 7148),
                   (1500, 7193), (2450, 7193), (3250, 7193), (4300, 7193), (4650, 7193)):
        _reeds(fills, f"weishui reeds {rx}", rx, rz, y=4)

    # ------------------------------------------------------------------
    # 8. Riverside willows on both banks.
    # ------------------------------------------------------------------
    for wx, wz in ((1250, 7212), (3400, 7212), (2100, 7128), (4000, 7128)):
        _willow(fills, f"weishui willow {wx}", wx, wz, y=4)


def main() -> None:
    run_builder(build_weishui_ferry_3d, "weishui_ferry_3d")


if __name__ == "__main__":
    main()
