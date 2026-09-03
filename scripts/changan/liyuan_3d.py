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
    add_hip_roof,
    add_lantern_line,
    add_outline,
    add_pyramid_roof,
    add_ridge_roof,
    run_builder,
)


"""
Liyuan, Pear Garden Music-and-Dance Academy (梨园·法曲乐舞) - the imperial
music school founded by Tang Xuanzong, the birthplace of the faqu melody
style, whose name "Pear Garden" became the Chinese word for opera itself.
Sited in the imperial forbidden-garden belt between the Daming Palace
north wall and the northern farm belt.

Location in Chang'an city local coordinates:
    Plot: x 2400..3000, z 5850..6060, north of the Daming Palace north
    wall (z=5820) and south of the north-suburb farmland (z=6080).
    Neighbours - Linde Hall (x 1970..2630, z 5210..5790) to the
    south-west and Penglai Isle of Taiye Pool (centre 3000,5620) to the
    north-east - do not overlap this plot. Every fill is clipped to
    x 2400..3000 and z 5850..6055. Ground level y 0..3, the buildings
    rise from y 5.

Distinctive features:
    - Music-and-Dance Great Hall (乐舞大堂): red-walled hall with dark-oak
      framing and a gilded hip roof, housing suspended drum racks
      (悬鼓架) with red drumheads hung mid-air, a bianzhong chime rack
      (编钟架) whose gilded bells diminish from large to small along a
      fence beam, and a raised performance stage (演出台) with a
      red-and-gold painted backdrop
    - Pear Garden Stage (梨园戏台): a stilted log-pile platform with four
      red columns under a gold-apex pyramid roof, encircled by
      concentric stone-seat and timber-bench spectator stands with
      radial aisles
    - Instrument Store (乐器库): a small ridge-roofed hall packed with
      note blocks, barrels, chests and wall ladders
    - Pear orchard east of the stage: a grid of white-blossom pear trees
    - Peony beds (牡丹圃) along the southern edge of the plot
    - Disciples' Court (弟子院): five sheds around a courtyard with a
      stone well and windlass
    - Lantern lines inside the courts and along the paths
"""

# Plot bounds - hard clip; never fill outside these.
SITE_X1, SITE_X2 = 2400, 3000
SITE_Z1, SITE_Z2 = 5850, 6055

# Music-and-Dance Great Hall wall envelope (roof extends past it).
HALL_X1, HALL_Z1, HALL_X2, HALL_Z2 = 2500, 5890, 2740, 6010

# Pear Garden Stage: centre of the stilted platform.
STAGE_CX, STAGE_CZ = 2825, 5935


def _drum_rack(fills: list[Fill], label: str, x: int, z1: int, z2: int) -> None:
    """Suspended drum rack (悬鼓架): fence posts and beam with a red
    drumhead hanging in mid-air below the beam."""
    cz = (z1 + z2) // 2
    add_fill(fills, f"{label} post n", (x, 5, z1), (x, 9, z1), M.FENCE)
    add_fill(fills, f"{label} post s", (x, 5, z2), (x, 9, z2), M.FENCE)
    add_fill(fills, f"{label} beam", (x, 9, z1), (x, 9, z2), M.FENCE)
    add_fill(fills, f"{label} drum", (x - 1, 7, cz - 1), (x + 1, 8, cz + 1), M.RED_WOOL)


def _chime_rack(fills: list[Fill], label: str, x1: int, x2: int, z: int) -> None:
    """Bianzhong chime rack (编钟架): log posts carrying a fence beam from
    which a row of gilded bells hangs, shrinking from large to small."""
    add_fill(fills, f"{label} post w", (x1, 5, z), (x1, 10, z), M.LOG)
    add_fill(fills, f"{label} post e", (x2, 5, z), (x2, 10, z), M.LOG)
    add_fill(fills, f"{label} beam", (x1, 10, z), (x2, 10, z), M.FENCE)
    bell_lengths = [4, 4, 4, 3, 3, 3, 2, 2, 1]
    span = x2 - x1
    for i, length in enumerate(bell_lengths):
        bx = x1 + (i + 1) * span // (len(bell_lengths) + 1)
        add_fill(fills, f"{label} bell {i}", (bx, 10 - length, z), (bx, 9, z), M.GOLD)


def _pear_tree(fills: list[Fill], label: str, x: int, z: int) -> None:
    """White-blossom pear tree: oak trunk, leaf canopy, white bloom on top."""
    add_fill(fills, f"{label} trunk", (x, 4, z), (x, 10, z), M.TREE_LOG)
    add_fill(fills, f"{label} canopy", (x - 2, 8, z - 2), (x + 2, 12, z + 2), M.LEAVES)
    add_fill(fills, f"{label} blossom", (x, 13, z), (x, 13, z), M.WHITE_WOOL)


def _peony_bed(fills: list[Fill], label: str, cx: int, cz: int) -> None:
    """One geometric peony bed: grass base, leaves border, striped flowers."""
    add_fill(fills, f"{label} base", (cx - 3, 2, cz - 3), (cx + 3, 2, cz + 3), M.GRASS)
    add_outline(fills, f"{label} border", cx - 3, cz - 3, cx + 3, cz + 3, 3, 3, M.LEAVES, thickness=1)
    for dz in range(-2, 3):
        block = M.PINK_WOOL if dz % 2 == 0 else M.RED_WOOL
        add_fill(fills, f"{label} peony {dz}", (cx - 2, 3, cz + dz), (cx + 2, 3, cz + dz), block)


def _court_house(
    fills: list[Fill],
    label: str,
    x1: int, z1: int,
    x2: int, z2: int,
    door: tuple[str, int, int] | None = None,
) -> None:
    """Small disciple shed: smooth plinth, red walls, timber roof, one door.

    door is (face, a, b): face in n/s/w/e, a..b the door span along that face.
    """
    add_fill(fills, f"{label} plinth", (x1, 4, z1), (x2, 4, z2), M.SMOOTH)
    add_outline(fills, f"{label} wall", x1, z1, x2, z2, 5, 8, M.RED_WALL, thickness=1)
    add_fill(fills, f"{label} roof", (x1, 9, z1), (x2, 9, z2), M.WOOD)
    if door is not None:
        face, a, b = door
        if face == "n":
            add_fill(fills, f"{label} door", (a, 5, z1), (b, 7, z1), M.AIR)
        elif face == "s":
            add_fill(fills, f"{label} door", (a, 5, z2), (b, 7, z2), M.AIR)
        elif face == "w":
            add_fill(fills, f"{label} door", (x1, 5, a), (x1, 7, b), M.AIR)
        else:
            add_fill(fills, f"{label} door", (x2, 5, a), (x2, 7, b), M.AIR)


def build_liyuan_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 0. Level the whole plot first (stone base, grass on top).
    # ------------------------------------------------------------------
    add_fill(fills, "liyuan plain base", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "liyuan plain grass", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)

    # ------------------------------------------------------------------
    # 1. Music-and-Dance Great Hall (乐舞大堂): terrace, red walls,
    #    dark-oak framing, hip roof.
    # ------------------------------------------------------------------
    add_fill(fills, "liyuan hall terrace", (2492, 4, 5882), (2748, 4, 6018), M.STONE)
    add_fill(fills, "liyuan hall floor", (2501, 4, 5891), (2739, 4, 6009), M.WOOD)
    add_outline(fills, "liyuan hall wall", HALL_X1, HALL_Z1, HALL_X2, HALL_Z2, 5, 15, M.RED_WALL, thickness=1)
    add_outline(fills, "liyuan hall lintel", HALL_X1, HALL_Z1, HALL_X2, HALL_Z2, 15, 15, M.LOG, thickness=1)
    # Dark-oak edge columns: corners, wall quarters and east/west midpoints
    # (kept clear of the door and window spans).
    hall_posts = [
        (2500, 5890), (2739, 5890), (2500, 6009), (2739, 6009),
        (2570, 5890), (2670, 5890), (2570, 6009), (2670, 6009),
        (2500, 5949), (2739, 5949),
    ]
    for i, (px, pz) in enumerate(hall_posts):
        add_fill(fills, f"liyuan hall col {i}", (px, 5, pz), (px + 1, 14, pz + 1), M.LOG)
    # Doors on north, south (aligned with the south path) and east faces.
    add_fill(fills, "liyuan hall door n", (2605, 5, 5890), (2635, 9, 5890), M.AIR)
    add_fill(fills, "liyuan hall door s", (2612, 5, 6010), (2628, 9, 6010), M.AIR)
    add_fill(fills, "liyuan hall door e", (2740, 5, 5954), (2740, 9, 5980), M.AIR)
    # Latticework suggested by glass bands between the columns.
    add_fill(fills, "liyuan hall window n w", (2528, 10, 5890), (2566, 12, 5890), M.GLASS)
    add_fill(fills, "liyuan hall window n e", (2674, 10, 5890), (2712, 12, 5890), M.GLASS)
    add_fill(fills, "liyuan hall window s w", (2528, 10, 6010), (2566, 12, 6010), M.GLASS)
    add_fill(fills, "liyuan hall window s e", (2674, 10, 6010), (2712, 12, 6010), M.GLASS)
    # Timber eave ceiling closing the wall top against the roof base.
    add_fill(fills, "liyuan hall eave plate", (2496, 16, 5886), (2744, 16, 6014), M.LOG)
    add_hip_roof(fills, "liyuan hall roof", 2496, 5886, 2744, 6014, y=17, layers=7, ridge_axis="x", roof_block=M.ROOF_GREEN)

    # ------------------------------------------------------------------
    # 2. Hall interior: performance stage, suspended drums, chimes.
    # ------------------------------------------------------------------
    # Raised performance stage (演出台) at the north end with backdrop.
    add_fill(fills, "liyuan hall stage base", (2590, 5, 5892), (2650, 7, 5910), M.STONE)
    add_fill(fills, "liyuan hall stage deck", (2590, 7, 5892), (2650, 7, 5910), M.WOOD)
    add_fill(fills, "liyuan hall stage step lo", (2608, 5, 5912), (2632, 5, 5912), M.SMOOTH)
    add_fill(fills, "liyuan hall stage step hi", (2612, 6, 5911), (2628, 6, 5911), M.SMOOTH)
    add_fill(fills, "liyuan hall backdrop", (2596, 8, 5892), (2644, 12, 5892), M.RED_WOOL)
    add_fill(fills, "liyuan hall backdrop gold w", (2612, 9, 5892), (2612, 11, 5892), M.GOLD)
    add_fill(fills, "liyuan hall backdrop gold e", (2628, 9, 5892), (2628, 11, 5892), M.GOLD)
    # Suspended drum racks (悬鼓架) flanking the central floor.
    _drum_rack(fills, "liyuan drum rack w n", 2530, 5925, 5945)
    _drum_rack(fills, "liyuan drum rack w s", 2530, 5960, 5980)
    _drum_rack(fills, "liyuan drum rack e", 2710, 5945, 5965)
    # Bianzhong chime rack (编钟架), bells large -> small, west to east.
    _chime_rack(fills, "liyuan chime rack", 2560, 2600, 5945)
    # Corner pillars carrying the ceiling.
    for px, pz in [(2530, 5920), (2710, 5920), (2530, 6000), (2710, 6000)]:
        add_fill(fills, f"liyuan hall pillar {px},{pz}", (px, 5, pz), (px + 1, 14, pz + 1), M.LOG)

    # ------------------------------------------------------------------
    # 3. Pear Garden Stage (梨园戏台): log piles, deck, four columns,
    #    pyramid roof, ring spectator stands.
    # ------------------------------------------------------------------
    for px, pz in [(2814, 5924), (2814, 5946), (2825, 5924), (2825, 5946), (2836, 5924), (2836, 5946)]:
        add_fill(fills, f"liyuan stage pile {px},{pz}", (px, 2, pz), (px, 4, pz), M.LOG)
    add_fill(fills, "liyuan stage platform", (2812, 5, 5922), (2838, 6, 5948), M.LOG)
    add_fill(fills, "liyuan stage deck", (2812, 7, 5922), (2838, 7, 5948), M.WOOD)
    # Fence rail around the deck, open on the south stair bay.
    add_fill(fills, "liyuan stage rail n", (2812, 8, 5922), (2838, 8, 5922), M.FENCE)
    add_fill(fills, "liyuan stage rail w", (2812, 8, 5922), (2812, 8, 5948), M.FENCE)
    add_fill(fills, "liyuan stage rail e", (2838, 8, 5922), (2838, 8, 5948), M.FENCE)
    add_fill(fills, "liyuan stage rail s w", (2812, 8, 5948), (2819, 8, 5948), M.FENCE)
    add_fill(fills, "liyuan stage rail s e", (2831, 8, 5948), (2838, 8, 5948), M.FENCE)
    # Three steps up from the ground to the deck.
    add_fill(fills, "liyuan stage step hi", (2820, 6, 5949), (2830, 6, 5949), M.SMOOTH)
    add_fill(fills, "liyuan stage step mid", (2818, 5, 5950), (2832, 5, 5950), M.SMOOTH)
    add_fill(fills, "liyuan stage step lo", (2818, 4, 5951), (2832, 4, 5951), M.SMOOTH)
    # Four red columns under the pyramid roof (攒尖顶) with gold apex.
    for px, pz in [(2816, 5926), (2834, 5926), (2816, 5944), (2834, 5944)]:
        add_fill(fills, f"liyuan stage column {px},{pz}", (px, 8, pz), (px + 1, 15, pz + 1), M.RED_WALL)
    add_pyramid_roof(fills, "liyuan stage roof", STAGE_CX, STAGE_CZ, radius=12, y=16, roof_block=M.ROOF_GREEN, apex_block=M.GOLD)
    # Ring stands: smooth stone seats, timber benches, outer stone ring.
    add_outline(fills, "liyuan stands inner", 2792, 5912, 2858, 5958, 4, 4, M.SMOOTH, thickness=2)
    add_outline(fills, "liyuan stands bench", 2785, 5905, 2865, 5965, 4, 5, M.WOOD, thickness=1)
    add_outline(fills, "liyuan stands outer", 2780, 5900, 2870, 5970, 4, 4, M.SMOOTH, thickness=1)
    # Radial aisles north, west and east (south aisle is the store path).
    add_fill(fills, "liyuan stands aisle n", (2820, 4, 5900), (2830, 4, 5913), M.ANDESITE)
    add_fill(fills, "liyuan stands aisle w", (2780, 4, 5930), (2793, 4, 5940), M.ANDESITE)
    add_fill(fills, "liyuan stands aisle e", (2857, 4, 5930), (2870, 4, 5940), M.ANDESITE)

    # ------------------------------------------------------------------
    # 4. Instrument Store (乐器库): small hall with note blocks, barrels,
    #    chests and wall ladders.
    # ------------------------------------------------------------------
    add_fill(fills, "liyuan store floor", (2778, 4, 5988), (2872, 4, 6052), M.SMOOTH)
    add_outline(fills, "liyuan store wall", 2780, 5990, 2870, 6050, 5, 10, M.RED_WALL, thickness=1)
    add_outline(fills, "liyuan store lintel", 2780, 5990, 2870, 6050, 11, 11, M.LOG, thickness=1)
    store_posts = [
        (2780, 5990), (2869, 5990), (2780, 6049), (2869, 6049),
        (2824, 5990), (2824, 6049), (2780, 6019), (2869, 6019),
    ]
    for i, (px, pz) in enumerate(store_posts):
        add_fill(fills, f"liyuan store col {i}", (px, 5, pz), (px + 1, 10, pz + 1), M.LOG)
    add_ridge_roof(fills, "liyuan store roof", 2778, 5988, 2872, 6052, y=13, layers=3, ridge_axis="x", roof_block=M.ROOF_GREEN)
    # Doors and windows (kept clear of the edge columns).
    add_fill(fills, "liyuan store door n", (2800, 5, 5990), (2810, 8, 5990), M.AIR)
    add_fill(fills, "liyuan store door w", (2780, 5, 6030), (2780, 7, 6040), M.AIR)
    add_fill(fills, "liyuan store window n", (2830, 8, 5990), (2850, 9, 5990), M.GLASS)
    add_fill(fills, "liyuan store window s w", (2790, 8, 6050), (2810, 9, 6050), M.GLASS)
    add_fill(fills, "liyuan store window s e", (2830, 8, 6050), (2850, 9, 6050), M.GLASS)
    add_fill(fills, "liyuan store window e", (2870, 8, 6030), (2870, 9, 6045), M.GLASS)
    # Instruments and fittings.
    add_fill(fills, "liyuan store note blocks a", (2792, 5, 5996), (2824, 5, 5996), "minecraft:note_block")
    add_fill(fills, "liyuan store note blocks b", (2792, 5, 6000), (2824, 5, 6000), "minecraft:note_block")
    add_fill(fills, "liyuan store barrels", (2842, 5, 6015), (2849, 7, 6022), "minecraft:barrel")
    add_fill(fills, "liyuan store chests", (2830, 5, 6032), (2842, 5, 6038), "minecraft:chest")
    add_fill(fills, "liyuan store ladder a", (2781, 5, 6040), (2781, 10, 6040), "minecraft:ladder[facing=east]")
    add_fill(fills, "liyuan store ladder b", (2781, 5, 6043), (2781, 10, 6043), "minecraft:ladder[facing=east]")
    add_fill(fills, "liyuan store shelf a", (2795, 5, 6016), (2815, 5, 6020), M.WOOD)
    add_fill(fills, "liyuan store shelf b", (2795, 5, 6026), (2815, 5, 6030), M.WOOD)

    # ------------------------------------------------------------------
    # 5. Disciples' Court (弟子院): sheds around a courtyard, well inside.
    # ------------------------------------------------------------------
    add_fill(fills, "liyuan court paving", (2443, 4, 5966), (2467, 4, 5974), M.SMOOTH)
    add_fill(fills, "liyuan court walk", (2451, 4, 5915), (2459, 4, 6025), M.SMOOTH)
    _court_house(fills, "liyuan court house n", 2424, 5894, 2486, 5914, door=("s", 2450, 2456))
    _court_house(fills, "liyuan court house s", 2424, 6026, 2486, 6046, door=("n", 2450, 2456))
    _court_house(fills, "liyuan court wing w", 2422, 5920, 2442, 6020, door=("e", 5960, 5966))
    _court_house(fills, "liyuan court wing e n", 2468, 5920, 2488, 5944, door=("w", 5928, 5934))
    _court_house(fills, "liyuan court wing e s", 2468, 5972, 2488, 6020, door=("w", 5982, 5988))
    # Gate passage between the two east wings.
    add_fill(fills, "liyuan court gate post n", (2478, 5, 5945), (2478, 8, 5945), M.FENCE)
    add_fill(fills, "liyuan court gate post s", (2478, 5, 5971), (2478, 8, 5971), M.FENCE)
    add_fill(fills, "liyuan court gate lintel", (2478, 8, 5945), (2478, 8, 5971), M.FENCE)
    # Courtyard well: shaft, water, stone rim, windlass posts and bar.
    add_fill(fills, "liyuan well shaft", (2453, 4, 5968), (2457, 4, 5972), M.AIR)
    add_fill(fills, "liyuan well water", (2453, 2, 5968), (2457, 3, 5972), M.WATER)
    add_outline(fills, "liyuan well rim", 2452, 5967, 2458, 5973, 4, 4, M.SMOOTH, thickness=1)
    add_fill(fills, "liyuan well post w", (2452, 5, 5970), (2452, 7, 5970), M.FENCE)
    add_fill(fills, "liyuan well post e", (2458, 5, 5970), (2458, 7, 5970), M.FENCE)
    add_fill(fills, "liyuan well windlass", (2452, 7, 5970), (2458, 7, 5970), M.FENCE)
    # A pear tree shading the courtyard.
    _pear_tree(fills, "liyuan court pear", 2448, 5932)

    # ------------------------------------------------------------------
    # 6. Pear orchard (梨园): white-blossom pear tree grid to the east.
    # ------------------------------------------------------------------
    for ox in range(2896, 2990, 22):
        for oz in range(5896, 6012, 22):
            _pear_tree(fills, f"liyuan pear {ox},{oz}", ox, oz)

    # ------------------------------------------------------------------
    # 7. Peony beds (牡丹圃) along the southern edge.
    # ------------------------------------------------------------------
    for i, (bx, bz) in enumerate([(2545, 6036), (2680, 6036), (2745, 6036)]):
        _peony_bed(fills, f"liyuan peony {i}", bx, bz)

    # ------------------------------------------------------------------
    # 8. Paths tying the complex together (cut the aisles last).
    # ------------------------------------------------------------------
    add_fill(fills, "liyuan promenade", (2492, 4, 5868), (2990, 4, 5878), M.ANDESITE)
    add_fill(fills, "liyuan south path", (2612, 4, 6012), (2628, 4, 6054), M.ANDESITE)
    add_fill(fills, "liyuan stage spur", (2822, 4, 5879), (2828, 4, 5899), M.ANDESITE)
    add_fill(fills, "liyuan store path", (2790, 4, 5952), (2860, 4, 5988), M.ANDESITE)
    add_fill(fills, "liyuan court path", (2468, 4, 5948), (2499, 4, 5968), M.ANDESITE)

    # ------------------------------------------------------------------
    # 9. Lantern lines inside the courts and along the paths.
    # ------------------------------------------------------------------
    add_lantern_line(fills, "liyuan promenade lamps", 2500, 5873, 2800, 5873, y=5, every=100)
    add_lantern_line(fills, "liyuan terrace lamps", 2540, 6016, 2660, 6016, y=5, every=60)
    add_lantern_line(fills, "liyuan south lamps w", 2614, 6026, 2614, 6046, y=5, every=20)
    add_lantern_line(fills, "liyuan south lamps e", 2626, 6026, 2626, 6046, y=5, every=20)
    add_lantern_line(fills, "liyuan court lamps", 2455, 5930, 2455, 5990, y=5, every=60)
    add_lantern_line(fills, "liyuan stage lamps n", 2790, 5894, 2860, 5894, y=4, every=70)
    add_lantern_line(fills, "liyuan stage lamps s", 2790, 5976, 2860, 5976, y=5, every=70)
    add_lantern_line(fills, "liyuan orchard lamps", 2882, 5900, 2882, 5990, y=4, every=40)


def main() -> None:
    run_builder(build_liyuan_3d, "liyuan_3d")


if __name__ == "__main__":
    main()
