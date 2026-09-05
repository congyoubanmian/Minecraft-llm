from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    BASE_X,
    BASE_Z,
    Fill,
    Materials as M,
    add_balustrade,
    add_fill,
    add_hollow_box,
    add_outline,
    run_builder,
)


"""
Taiye Pool Painted Barge Fleet & Water-Puppet Theatre (太液池画舫船队·水傀儡戏台).

Recreates the famous scene of Emperor Xuanzong and Lady Yang boating on
Taiye Pool of Daming Palace: feasting aboard a two-storey painted barge,
with a music barge alongside and a floating raft stage performing water
puppet plays (水傀儡) on the pool, reached by a flagged buoy channel from
the south-bank banquet tents.

Location in Chang'an city local coordinates:
    Taiye Pool water: x 2780..3220, z 5500..5740, surface y=2
    (imperial_daming_palace.py). Every fill stays inside the allowed
    shore band x 2750..3250, z 5470..5770.
    Penglai avoidance (penglai_island_3d.py): the main immortal isle
    (centre 3000,5620, mound radius 52 + triple pavilion, box
    x 2944..3056 / z 5564..5676), the north multi-arch stone bridge
    (x 2996..3004, z 5500..5582), the Fangzhang / Yingzhou attendant
    islets (centres 2900 / 3100 at z 5680, boxes x 2876..2924 and
    x 3076..3124, z 5656..5704) and the south boat dock (x 2990..3010,
    z 5670..5678) are all kept clear. Every structure below sits in the
    open south-east water or on the free south bank, and the builder
    asserts this against a keep-out list at run time. The west shore
    (Hanliang Hall, x <= 2768) is not touched.

Distinctive features:
    - Grand two-storey painted barge (~30x10): dark-oak hull with hollowed
      hold cabins, quartz-and-gold chi-dragon figurehead, vermilion
      balustraded deck, open upper pavilion with a gilded pyramidal roof,
      stern sculling tower with a great oar, and a banquet table with gold
      cups and wine barrels in the hold
    - Mid-size music barge (20x8): flat-roofed open shed with a red wool
      valance, four corner sea-lantern masts, and a bow music stage with
      red carpet and flanking player desks
    - Floating water-puppet theatre (16x14): double timber raft base
      (y3..4 on the water), four birch-post canopy with a yellow wool top,
      a backstage puppet cabinet housing three quartz puppets, a front
      stone-trough water-curtain gadget, and musician benches on both flanks
    - Buoy channel of eight alternating red/yellow flag floats leading from
      the south-bank pier to the theatre front
    - Two banquet tents (red / yellow wool roofs) with long tables, gold
      vessels and wine barrels on the south bank terrace
    - Eight lotus spots (lily pads with pink blossoms) scattered off the
      fairways
"""

# Taiye Pool water (imperial_daming_palace.py): surface at local y=2.
WATER_Y = 2

# Allowed shore band for every fill (local coords).
ALLOWED = (2750, 5470, 3250, 5770)

# Penglai Island module keep-out boxes (local x1, z1, x2, z2), inflated
# with a safety margin: main isle + pavilion, north bridge, two attendant
# islets, and the south boat dock.
KEEP_OUT = [
    (2944, 5564, 3056, 5676),  # main isle mound, shore ring, pavilion
    (2992, 5496, 3008, 5586),  # multi-arch bridge corridor
    (2876, 5656, 2924, 5704),  # Fangzhang islet (2900, 5680)
    (3076, 5656, 3124, 5704),  # Yingzhou islet (3100, 5680)
    (2986, 5666, 3014, 5682),  # south boat dock + mooring posts
]

# Grand painted barge (画舫): hull box, bow to the east.
BH_X1, BH_Z1 = 3142, 5694
BH_X2, BH_Z2 = 3171, 5703

# Music barge (歌舞舫): hull box, bow to the east.
MH_X1, MH_Z1 = 3160, 5665
MH_X2, MH_Z2 = 3179, 5672

# Floating water-puppet theatre (水傀儡戏台): raft box, stage faces south.
TH_X1, TH_Z1 = 3060, 5700
TH_X2, TH_Z2 = 3075, 5713

# South bank banquet terrace and tents.
BT_X1, BT_Z1 = 3028, 5742
BT_X2, BT_Z2 = 3084, 5764

# Buoy channel: pier tip at the south bank to the theatre front.
BUOYS = [
    (3076, 5734), (3074, 5732), (3076, 5730), (3073, 5728),
    (3075, 5726), (3072, 5724), (3073, 5721), (3070, 5718),
]

SLAB = "minecraft:dark_prismarine_slab[type=bottom,waterlogged=false]"
LILY_PAD = "minecraft:lily_pad"
BARREL = "minecraft:barrel"


def _lotus_patch(
    fills: list[Fill], label: str, x1: int, x2: int, z: int, buds: list[int]
) -> None:
    """One lotus spot: a lily-pad run at the water surface plus pink blooms."""
    add_fill(fills, f"{label} pads", (x1, WATER_Y, z), (x2, WATER_Y, z), LILY_PAD)
    for i, bx in enumerate(buds):
        add_fill(fills, f"{label} blossom {i}", (bx, WATER_Y + 1, z), (bx, WATER_Y + 1, z), M.PINK_WOOL)


def _flagpole(
    fills: list[Fill], label: str, x: int, z: int, y1: int, y2: int, wool: str
) -> None:
    """Fence mast with a two-block wool banner hung at its top."""
    add_fill(fills, f"{label} pole", (x, y1, z), (x, y2, z), M.FENCE)
    add_fill(fills, f"{label} banner", (x, y2 - 1, z), (x, y2, z), wool)


def _build_grand_barge(fills: list[Fill]) -> None:
    """双层画舫: hull, figurehead, upper pavilion, stern tower, banquet hold."""
    # 1. Hull: keel plate, dark-oak side shell, hollowed hold, deck.
    add_fill(fills, "taiyeboat barge keel", (BH_X1, 1, BH_Z1), (BH_X2, 1, BH_Z2), M.WOOD)
    add_outline(fills, "taiyeboat barge hull", BH_X1, BH_Z1, BH_X2, BH_Z2, 2, 4, M.WOOD)
    add_fill(fills, "taiyeboat barge hold air", (BH_X1 + 1, 2, BH_Z1 + 1), (BH_X2 - 1, 3, BH_Z2 - 1), M.AIR)
    # Transverse bulkheads split the hold into three cabins.
    for bx in (3152, 3163):
        add_fill(fills, f"taiyeboat barge bulkhead {bx}", (bx, 2, BH_Z1 + 1), (bx, 3, BH_Z2 - 1), M.WOOD)
    add_fill(fills, "taiyeboat barge deck", (BH_X1 + 1, 4, BH_Z1 + 1), (BH_X2 - 1, 4, BH_Z2 - 1), M.SPRUCE)
    add_fill(fills, "taiyeboat barge hatch", (3157, 4, 5698), (3159, 4, 5699), M.AIR)

    # 2. Banquet hold below the hatch: feast table, gold cups, wine barrels.
    add_fill(fills, "taiyeboat barge feast table", (3155, 2, 5697), (3161, 2, 5700), M.WOOD)
    for i, (cx, cz) in enumerate([(3156, 5698), (3159, 5697), (3160, 5700)]):
        add_fill(fills, f"taiyeboat barge gold cup {i}", (cx, 3, cz), (cx, 3, cz), M.GOLD)
    add_fill(fills, "taiyeboat barge wine barrels", (3146, 2, 5696), (3147, 3, 5697), BARREL)
    add_fill(fills, "taiyeboat barge hold lantern", (3154, 3, 5701), (3154, 3, 5701), M.SEA_LANTERN)

    # 3. Vermilion balustraded deck (朱红栏杆平座).
    add_balustrade(
        fills, "taiyeboat barge rail",
        BH_X1, BH_Z1, BH_X2, BH_Z2, 5,
        post_block=M.RED_WALL, head_block=M.GOLD, post_every=6,
    )

    # 4. Carved chi-dragon figurehead (螭首) in quartz and gold.
    add_fill(fills, "taiyeboat chi neck", (3172, 2, 5697), (3173, 5, 5700), M.QUARTZ)
    add_fill(fills, "taiyeboat chi head", (3174, 3, 5697), (3176, 5, 5700), M.QUARTZ)
    add_fill(fills, "taiyeboat chi horns", (3173, 6, 5698), (3174, 7, 5699), M.GOLD)
    add_fill(fills, "taiyeboat chi eye s", (3175, 5, 5697), (3175, 5, 5697), M.GOLD)
    add_fill(fills, "taiyeboat chi eye n", (3175, 5, 5700), (3175, 5, 5700), M.GOLD)

    # 5. Upper open pavilion (敞阁): four columns + gilded pyramidal roof.
    for i, (px, pz) in enumerate([(3154, 5695), (3154, 5702), (3164, 5695), (3164, 5702)]):
        add_fill(fills, f"taiyeboat barge pavilion col {i}", (px, 5, pz), (px, 9, pz), M.LOG)
    add_outline(fills, "taiyeboat barge roof l0", 3153, 5694, 3165, 5703, 10, 10, M.ROOF_GREEN)
    add_outline(fills, "taiyeboat barge roof l1", 3155, 5695, 3163, 5702, 11, 11, M.ROOF_GREEN)
    add_outline(fills, "taiyeboat barge roof l2", 3157, 5696, 3161, 5701, 12, 12, M.ROOF_GREEN)
    add_fill(fills, "taiyeboat barge roof gold cap", (3158, 13, 5697), (3160, 13, 5700), M.GOLD)
    add_fill(fills, "taiyeboat barge roof finial", (3159, 14, 5698), (3159, 15, 5699), M.GOLD)
    for i, (ux, uz) in enumerate([(3153, 5694), (3165, 5694), (3153, 5703), (3165, 5703)]):
        add_fill(fills, f"taiyeboat barge roof upturn {i}", (ux, 11, uz), (ux, 11, uz), M.GOLD_ACCENT)

    # 6. Stern sculling tower (橹楼) with its great oar.
    add_hollow_box(fills, "taiyeboat barge stern tower", 3143, 5, 5695, 3149, 10, 5702, M.WOOD)
    add_fill(fills, "taiyeboat barge tower door", (3149, 5, 5698), (3149, 7, 5699), M.AIR)
    add_fill(fills, "taiyeboat barge tower window", (3143, 7, 5697), (3143, 8, 5700), M.RED_STAINED_GLASS)
    add_fill(fills, "taiyeboat barge tower roof", (3142, 11, 5694), (3150, 11, 5703), SLAB)
    for i, (fx, fz) in enumerate([(3142, 5694), (3150, 5694), (3142, 5703), (3150, 5703)]):
        add_fill(fills, f"taiyeboat barge tower finial {i}", (fx, 12, fz), (fx, 12, fz), M.GOLD)
    add_fill(fills, "taiyeboat barge tower lantern", (3146, 12, 5698), (3146, 12, 5698), M.SEA_LANTERN)
    add_fill(fills, "taiyeboat barge oar loft", (3140, 7, 5698), (3144, 7, 5699), "minecraft:dark_oak_log[axis=x]")
    add_fill(fills, "taiyeboat barge oar shaft", (3137, 5, 5698), (3139, 6, 5699), "minecraft:dark_oak_log[axis=x]")
    add_fill(fills, "taiyeboat barge oar blade", (3134, 2, 5697), (3136, 4, 5700), M.SPRUCE)

    # 7. Bow banners.
    _flagpole(fills, "taiyeboat barge flag red", 3169, 5695, 5, 9, M.RED_WOOL)
    _flagpole(fills, "taiyeboat barge flag yellow", 3169, 5702, 5, 9, M.YELLOW_WOOL)


def _build_music_barge(fills: list[Fill]) -> None:
    """歌舞舫: flat open shed, corner lantern masts, bow music stage."""
    add_fill(fills, "taiyeboat music keel", (MH_X1, 1, MH_Z1), (MH_X2, 1, MH_Z2), M.WOOD)
    add_outline(fills, "taiyeboat music hull", MH_X1, MH_Z1, MH_X2, MH_Z2, 2, 3, M.WOOD)
    add_fill(fills, "taiyeboat music hold air", (MH_X1 + 1, 2, MH_Z1 + 1), (MH_X2 - 1, 3, MH_Z2 - 1), M.AIR)
    add_fill(fills, "taiyeboat music deck", (MH_X1 + 1, 4, MH_Z1 + 1), (MH_X2 - 1, 4, MH_Z2 - 1), M.SPRUCE)
    add_outline(fills, "taiyeboat music rail", MH_X1, MH_Z1, MH_X2, MH_Z2, 5, 5, M.FENCE)

    # Stern cabin with wine barrel and slab roof.
    add_outline(fills, "taiyeboat music cabin", 3161, 5667, 3165, 5670, 5, 7, M.WOOD)
    add_fill(fills, "taiyeboat music cabin air", (3162, 5, 5668), (3164, 7, 5669), M.AIR)
    add_fill(fills, "taiyeboat music cabin barrel", (3162, 5, 5668), (3163, 6, 5669), BARREL)
    add_fill(fills, "taiyeboat music cabin door", (3165, 5, 5668), (3165, 6, 5669), M.AIR)
    add_fill(fills, "taiyeboat music cabin roof", (3161, 8, 5667), (3165, 8, 5670), SLAB)

    # Flat open shed (平顶敞棚): posts, slab roof, red wool valance.
    for i, (px, pz) in enumerate([(3167, 5666), (3167, 5671), (3173, 5666), (3173, 5671)]):
        add_fill(fills, f"taiyeboat music shed col {i}", (px, 5, pz), (px, 9, pz), M.LOG)
    add_fill(fills, "taiyeboat music shed roof", (3165, 10, MH_Z1), (3175, 10, MH_Z2), SLAB)
    add_outline(fills, "taiyeboat music shed valance", 3165, MH_Z1, 3175, MH_Z2, 9, 9, M.RED_WOOL)

    # Four corner lantern masts (四角灯杆).
    for i, (px, pz) in enumerate([(3165, MH_Z1), (3175, MH_Z1), (3165, MH_Z2), (3175, MH_Z2)]):
        add_fill(fills, f"taiyeboat music mast {i}", (px, 5, pz), (px, 8, pz), M.FENCE)
        add_fill(fills, f"taiyeboat music mast lamp {i}", (px, 9, pz), (px, 9, pz), M.SEA_LANTERN)

    # Bow music stage (船头乐台): red carpet and flanking player desks.
    add_fill(fills, "taiyeboat music stage", (3176, 5, 5667), (3179, 5, 5670), M.SPRUCE)
    add_fill(fills, "taiyeboat music stage carpet", (3177, 6, 5668), (3179, 6, 5669), M.RED_WOOL)
    add_fill(fills, "taiyeboat music desk n", (3176, 5, 5666), (3179, 5, 5666), M.WOOD)
    add_fill(fills, "taiyeboat music desk s", (3176, 5, 5671), (3179, 5, 5671), M.WOOD)
    add_fill(fills, "taiyeboat music player n", (3177, 6, 5666), (3177, 6, 5666), M.QUARTZ)
    add_fill(fills, "taiyeboat music player s", (3179, 6, 5671), (3179, 6, 5671), M.QUARTZ)
    add_fill(fills, "taiyeboat music shed lamp", (3170, 9, 5668), (3170, 9, 5668), M.SEA_LANTERN)
    _flagpole(fills, "taiyeboat music flag", 3162, 5668, 9, 11, M.RED_WOOL)


def _build_puppet_theatre(fills: list[Fill]) -> None:
    """水傀儡戏台: double raft, yellow canopy, puppet cabinet, water curtain."""
    # 1. Double timber raft base floating on the water (y3..4).
    add_fill(fills, "taiyeboat stage raft lower", (TH_X1, 3, TH_Z1), (TH_X2, 3, TH_Z2), M.WOOD)
    add_fill(fills, "taiyeboat stage raft upper", (TH_X1, 4, TH_Z1), (TH_X2, 4, TH_Z2), M.SPRUCE)

    # 2. Four bamboo-style birch posts and the yellow wool canopy.
    for i, (px, pz) in enumerate([(TH_X1 + 1, TH_Z1 + 1), (TH_X2 - 1, TH_Z1 + 1),
                                  (TH_X1 + 1, TH_Z2 - 1), (TH_X2 - 1, TH_Z2 - 1)]):
        add_fill(fills, f"taiyeboat stage col {i}", (px, 5, pz), (px, 9, pz), "minecraft:birch_log[axis=y]")
    add_fill(fills, "taiyeboat stage canopy", (TH_X1, 10, TH_Z1), (TH_X2, 10, TH_Z2), M.YELLOW_WOOL)
    add_fill(fills, "taiyeboat stage canopy l1", (TH_X1 + 2, 11, TH_Z1 + 2), (TH_X2 - 2, 11, TH_Z2 - 2), M.YELLOW_WOOL)
    add_fill(fills, "taiyeboat stage canopy l2", (TH_X1 + 4, 12, TH_Z1 + 4), (TH_X2 - 4, 12, TH_Z2 - 4), M.YELLOW_WOOL)
    add_fill(fills, "taiyeboat stage canopy apex", (3066, 13, 5706), (3069, 13, 5707), M.GOLD)

    # 3. Backstage puppet cabinet (后台傀儡柜): three bays, three quartz puppets.
    add_fill(fills, "taiyeboat cabinet back", (3062, 5, TH_Z1), (3073, 8, TH_Z1), M.WOOD)
    for dx in (3066, 3070):
        add_fill(fills, f"taiyeboat cabinet divider {dx}", (dx, 5, TH_Z1), (dx, 8, TH_Z1 + 3), M.WOOD)
    for dx in (3062, 3073):
        add_fill(fills, f"taiyeboat cabinet end {dx}", (dx, 5, TH_Z1), (dx, 8, TH_Z1 + 3), M.WOOD)
    add_fill(fills, "taiyeboat cabinet shelf", (3062, 8, TH_Z1), (3073, 8, TH_Z1 + 3), M.WOOD)
    for i, px in enumerate([(3064, 5701), (3068, 5701), (3072, 5701)]):
        add_fill(fills, f"taiyeboat puppet {i}", (px[0], 5, px[1]), (px[0], 7, px[1]), M.QUARTZ)
        add_fill(fills, f"taiyeboat puppet sash {i}", (px[0], 6, px[1]), (px[0], 6, px[1]), M.RED_WOOL)

    # 4. Centre puppet stage with red carpet and one dancing puppet.
    add_fill(fills, "taiyeboat stage platform", (3066, 5, 5706), (3071, 5, 5709), M.WOOD)
    add_fill(fills, "taiyeboat stage carpet", (3066, 6, 5706), (3071, 6, 5709), M.RED_WOOL)
    add_fill(fills, "taiyeboat stage dancer", (3068, 7, 5707), (3068, 8, 5707), M.QUARTZ)

    # 5. Front stone-trough water-curtain gadget (石槽水幕).
    for dx in (3062, 3073):
        add_fill(fills, f"taiyeboat trough side {dx}", (dx, 5, TH_Z2 - 1), (dx, 5, TH_Z2), M.STONE)
    add_fill(fills, "taiyeboat trough lip", (3063, 5, TH_Z2), (3072, 5, TH_Z2), M.STONE)
    add_fill(fills, "taiyeboat trough water", (3063, 5, TH_Z2 - 1), (3072, 5, TH_Z2), M.WATER)
    add_fill(fills, "taiyeboat curtain tank", (3065, 8, TH_Z2 - 1), (3070, 9, TH_Z2 - 1), M.STONE)
    add_fill(fills, "taiyeboat curtain fall", (3065, 6, TH_Z2 - 1), (3070, 7, TH_Z2 - 1), M.WATER)

    # 6. Musician benches and quartz players on both flanks (两侧乐师座).
    add_fill(fills, "taiyeboat bench w", (TH_X1 + 1, 5, 5705), (TH_X1 + 1, 5, 5710), M.SPRUCE)
    add_fill(fills, "taiyeboat bench e", (TH_X2 - 1, 5, 5705), (TH_X2 - 1, 5, 5710), M.SPRUCE)
    for i, z in enumerate((5706, 5708, 5710)):
        add_fill(fills, f"taiyeboat player w {i}", (TH_X1 + 1, 6, z), (TH_X1 + 1, 6, z), M.QUARTZ)
        add_fill(fills, f"taiyeboat player e {i}", (TH_X2 - 1, 6, z), (TH_X2 - 1, 6, z), M.QUARTZ)

    # 7. Hanging lanterns and the boarding plank toward the buoy line.
    for i, (lx, lz) in enumerate([(3063, 5702), (3072, 5702), (3063, 5711), (3072, 5711)]):
        add_fill(fills, f"taiyeboat stage lamp {i}", (lx, 9, lz), (lx, 9, lz), M.SEA_LANTERN)
    add_fill(fills, "taiyeboat stage plank", (3066, 4, 5714), (3069, 4, 5716), M.SPRUCE)


def _build_buoy_channel(fills: list[Fill]) -> None:
    """彩旗浮标水道: south-bank pier plus eight alternating flag floats."""
    # Timber pier from the bank out over the water.
    add_fill(fills, "taiyeboat pier deck", (3072, 3, 5736), (3079, 3, 5749), M.SPRUCE)
    add_fill(fills, "taiyeboat pier rail w", (3072, 4, 5736), (3072, 4, 5749), M.FENCE)
    add_fill(fills, "taiyeboat pier rail e", (3079, 4, 5736), (3079, 4, 5749), M.FENCE)
    for i, (px, pz) in enumerate([(3072, 5737), (3079, 5737), (3072, 5740), (3079, 5740)]):
        add_fill(fills, f"taiyeboat pier pile {i}", (px, 1, pz), (px, 2, pz), M.LOG)
    add_fill(fills, "taiyeboat pier lamp pole", (3075, 4, 5736), (3075, 9, 5736), M.LOG)
    add_fill(fills, "taiyeboat pier lamp", (3075, 10, 5736), (3075, 10, 5736), M.SEA_LANTERN)

    # Eight flag buoys marking the route to the theatre.
    for i, (bx, bz) in enumerate(BUOYS):
        wool = M.RED_WOOL if i % 2 == 0 else M.YELLOW_WOOL
        add_fill(fills, f"taiyeboat buoy {i} float", (bx, WATER_Y, bz), (bx, WATER_Y, bz), M.SEA_LANTERN)
        add_fill(fills, f"taiyeboat buoy {i} pole", (bx, WATER_Y + 1, bz), (bx, WATER_Y + 3, bz), M.FENCE)
        add_fill(fills, f"taiyeboat buoy {i} flag", (bx, WATER_Y + 3, bz), (bx, WATER_Y + 4, bz), wool)


def _banquet_tent(fills: list[Fill], tag: str, x1: int, z1: int, roof: str) -> None:
    """One banquet tent: corner posts, stepped wool roof, long table inside."""
    x2, z2 = x1 + 15, z1 + 15
    add_fill(fills, f"taiyeboat {tag} carpet", (x1 + 2, 3, z1 + 2), (x2 - 2, 3, z2 - 2), roof)
    for i, (px, pz) in enumerate([(x1 + 1, z1 + 1), (x2 - 1, z1 + 1), (x1 + 1, z2 - 1), (x2 - 1, z2 - 1)]):
        add_fill(fills, f"taiyeboat {tag} post {i}", (px, 4, pz), (px, 8, pz), M.LOG)
    add_fill(fills, f"taiyeboat {tag} roof l0", (x1, 8, z1), (x2, 8, z2), roof)
    add_fill(fills, f"taiyeboat {tag} roof l1", (x1 + 2, 9, z1 + 2), (x2 - 2, 9, z2 - 2), roof)
    add_fill(fills, f"taiyeboat {tag} roof l2", (x1 + 4, 10, z1 + 4), (x2 - 4, 10, z2 - 4), roof)
    add_fill(fills, f"taiyeboat {tag} roof apex", (x1 + 7, 11, z1 + 7), (x1 + 8, 11, z1 + 8), M.GOLD)
    # Door curtains on the pool-facing side.
    add_fill(fills, f"taiyeboat {tag} curtain a", (x1 + 5, 4, z1), (x1 + 5, 6, z1), roof)
    add_fill(fills, f"taiyeboat {tag} curtain b", (x1 + 8, 4, z1), (x1 + 8, 6, z1), roof)
    # Long table with gold vessels and a wine barrel.
    add_fill(fills, f"taiyeboat {tag} table", (x1 + 4, 4, z1 + 7), (x1 + 11, 4, z1 + 8), M.WOOD)
    for i, (vx, vz) in enumerate([(x1 + 5, z1 + 7), (x1 + 8, z1 + 8), (x1 + 10, z1 + 7)]):
        add_fill(fills, f"taiyeboat {tag} vessel {i}", (vx, 5, vz), (vx, 5, vz), M.GOLD)
    add_fill(fills, f"taiyeboat {tag} barrel", (x1 + 2, 4, z1 + 2), (x1 + 3, 5, z1 + 3), BARREL)
    add_fill(fills, f"taiyeboat {tag} lamp pole", (x2 - 2, 4, z2 - 2), (x2 - 2, 7, z2 - 2), M.FENCE)
    add_fill(fills, f"taiyeboat {tag} lamp", (x2 - 2, 8, z2 - 2), (x2 - 2, 8, z2 - 2), M.LANTERN)


def _build_bank_banquet(fills: list[Fill]) -> None:
    """岸边宴帐: south-bank terrace, two tents, banners and lanterns."""
    add_fill(fills, "taiyeboat terrace base", (BT_X1, 2, BT_Z1), (BT_X2, 2, BT_Z2), M.STONE)
    add_fill(fills, "taiyeboat terrace top", (BT_X1, 3, BT_Z1), (BT_X2, 3, BT_Z2), M.SMOOTH)
    _banquet_tent(fills, "tent red", 3032, 5745, M.RED_WOOL)
    _banquet_tent(fills, "tent yellow", 3054, 5745, M.YELLOW_WOOL)
    # Pair of banners between the tents.
    _flagpole(fills, "taiyeboat terrace flag red", 3049, BT_Z1 + 1, 4, 9, M.RED_WOOL)
    _flagpole(fills, "taiyeboat terrace flag yellow", 3051, BT_Z1 + 1, 4, 9, M.YELLOW_WOOL)
    # Terrace corner lanterns facing the pool.
    for i, lx in enumerate((BT_X1 + 2, BT_X2 - 2)):
        add_fill(fills, f"taiyeboat terrace lamp pole {i}", (lx, 4, BT_Z1 + 1), (lx, 8, BT_Z1 + 1), M.LOG)
        add_fill(fills, f"taiyeboat terrace lamp {i}", (lx, 9, BT_Z1 + 1), (lx, 9, BT_Z1 + 1), M.SEA_LANTERN)
    # A few bank rocks south-east of the terrace.
    for i, (rx, rz, s) in enumerate([(3090, 5744, 2), (3100, 5750, 2), (3112, 5742, 1)]):
        add_fill(fills, f"taiyeboat bank rock {i}", (rx, 2, rz), (rx + s, 3 + i % 2, rz + s), M.COBBLE)


def _build_lotus_patches(fills: list[Fill]) -> None:
    """池面荷花点缀: eight spots kept clear of the buoy fairway."""
    _lotus_patch(fills, "taiyeboat lotus 1", 3095, 3101, 5721, [3096, 3100])
    _lotus_patch(fills, "taiyeboat lotus 2", 3128, 3132, 5712, [3129, 3131])
    _lotus_patch(fills, "taiyeboat lotus 3", 3196, 3202, 5699, [3197, 3201])
    _lotus_patch(fills, "taiyeboat lotus 4", 3198, 3204, 5628, [3199, 3203])
    _lotus_patch(fills, "taiyeboat lotus 5", 3138, 3144, 5640, [3139, 3143])
    _lotus_patch(fills, "taiyeboat lotus 6", 3085, 3090, 5732, [3086, 3089])
    _lotus_patch(fills, "taiyeboat lotus 7", 3206, 3210, 5682, [3208])
    _lotus_patch(fills, "taiyeboat lotus 8", 3050, 3055, 5724, [3051, 3054])


def _verify_placement(fills: list[Fill]) -> None:
    """Hard checks: every OWN fill inside the shore band and clear of Penglai.

    build_all.py accumulates one shared fill list across modules, so only
    fills labelled with this module's prefix are checked.
    """
    for fill in fills:
        if not fill.label.startswith("taiyeboat"):
            continue
        lx1, lx2 = sorted((fill.x1 - BASE_X, fill.x2 - BASE_X))
        lz1, lz2 = sorted((fill.z1 - BASE_Z, fill.z2 - BASE_Z))
        if lx1 < ALLOWED[0] or lx2 > ALLOWED[2] or lz1 < ALLOWED[1] or lz2 > ALLOWED[3]:
            raise ValueError(
                f"{fill.label} outside Taiye shore band: x {lx1}..{lx2}, z {lz1}..{lz2}"
            )
        for kx1, kz1, kx2, kz2 in KEEP_OUT:
            if lx1 <= kx2 and lx2 >= kx1 and lz1 <= kz2 and lz2 >= kz1:
                raise ValueError(
                    f"{fill.label} intrudes into Penglai keep-out "
                    f"({kx1},{kz1})..({kx2},{kz2}): x {lx1}..{lx2}, z {lz1}..{lz2}"
                )


def build_taiye_boat_3d(fills: list[Fill]) -> None:
    """太液池画舫船队·水傀儡戏台 - fleet, floating stage and bank banquet."""
    _build_grand_barge(fills)
    _build_music_barge(fills)
    _build_puppet_theatre(fills)
    _build_buoy_channel(fills)
    _build_bank_banquet(fills)
    _build_lotus_patches(fills)
    _verify_placement(fills)


def main() -> None:
    run_builder(build_taiye_boat_3d, "taiye_boat_3d")


if __name__ == "__main__":
    main()
