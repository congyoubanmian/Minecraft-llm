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
    add_cantilevered_floor,
    add_column_grid,
    add_fill,
    add_lantern_line,
    add_outline,
    add_spiral_stair,
    add_tree,
    run_builder,
)


"""
Silk Road Caravan & Persian Trade House (丝路驼队·开远门外波斯邸) 3D module.

Chang'an was the eastern terminus of the Silk Road; camel caravans streamed
through Kaiyuan Gate (开远门), the north-western city gate. This module builds
the caravan road and a Persian trade house (波斯邸) on the ancient Silk Road
track outside the west wall.

Location in Chang'an city local coordinates:
    Site: west-suburb belt along the old Silk Road track,
    x -520..-100, z 2400..2700 (covers two or three scattered field parcels
    of the west farm belt by design; nothing else is built further west).
    After grading: stone y0..1 + grass y2..3, so the walking surface is y4.

Distinctive features:
    - Graded terrace crossed by an east-west yellow-sand caravan road with
      andesite curbs
    - Camel caravan: five blocky Bactrian camels (four standing, one sitting)
      with 2x2 legs, sandy bodies, twin brown-tipped humps, hay cargo on
      coloured wool blankets, stepped necks, ears, hitching posts and
      iron-bar reins linking each camel to the one ahead
    - Persian trade house (波斯邸): two-storey hall, red ground floor with
      three stepped arches, red/yellow glazed-terracotta diamond medallions,
      cantilevered balcony gallery, white upper storey, and a Persian dome
      of shrinking cut-sandstone rings on a square drum with a gold finial
    - Spice market: open hay-roofed sheds south of the road with spice
      sacks, jar rows (barrels + flower pots) and silk-bolt shelves
    - Goods yard behind the warehouse: hay ricks, crate stacks and
      FENCE+WOOD wheelbarrow props
    - Way station west: walled yard with a two-stall stable (hay roof,
      fence mangers, bedding), a stone water trough with water, a hay
      canopy and bales
    - Caravaneer lighthouse: quartz shaft with red bands, sea-lantern lamp
      room and a red pyramid roof with a gold spike
    - Desert poplars and lantern posts flanking the caravan road
"""

# ---------------------------------------------------------------------------
# Site: Silk Road track outside the west wall (strict bounds).
# ---------------------------------------------------------------------------
SITE_X1, SITE_X2 = -520, -100
SITE_Z1, SITE_Z2 = 2400, 2700

# East-west yellow-sand caravan road (walkable top y3, feet at y4).
ROAD_X1, ROAD_X2 = -500, -120
ROAD_Z1, ROAD_Z2 = 2571, 2598
CURB_N1, CURB_N2 = 2569, 2570
CURB_S1, CURB_S2 = 2599, 2600
REIN_Z = 2580  # global rein line: every camel body spans this z

# Persian trade house (波斯邸货栈).
WH_X1, WH_Z1 = -366, 2452
WH_X2, WH_Z2 = -254, 2514
WH_CX, WH_CZ = -310, 2483
DRUM_X1, DRUM_Z1 = WH_CX - 11, WH_CZ - 11
DRUM_X2, DRUM_Z2 = WH_CX + 11, WH_CZ + 11
DOME_BASE_Y = 25
DOME_R = 10

# Caravaneer lighthouse centre.
LIGHT_CX, LIGHT_CZ = -200, 2480

# Caravan-specific direct-string blocks.
SAND = "minecraft:sand"
HAY = "minecraft:hay_block"
CUT_SANDSTONE = "minecraft:cut_sandstone"
BARREL = "minecraft:barrel"
FLOWER_POT = "minecraft:flower_pot"
BROWN_WOOL = "minecraft:brown_wool"
CAMEL_BODY = SAND
CAMEL_LEG = M.WHITE_TERRACOTTA
LOG_X = "minecraft:dark_oak_log[axis=x]"
LOG_Z = "minecraft:dark_oak_log[axis=z]"


def _sandstone_stair(facing: str) -> str:
    return (
        "minecraft:sandstone_stairs"
        f"[facing={facing},half=bottom,shape=straight,waterlogged=false]"
    )


# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------
def _persian_dome(
    fills: list[Fill],
    label: str,
    cx: int,
    cz: int,
    radius: int,
    base_y: int,
    block: str = CUT_SANDSTONE,
    step: int = 5,
    shell: int = 5,
    min_r: int = 5,
) -> int:
    """Persian dome: horizontal scanline rings of cut sandstone shrinking to
    a cap. Returns the y level just above the last ring (finial seat)."""
    top_y = base_y
    for t in range(radius + 1):
        r = int(math.sqrt(radius * radius - t * t))
        if r < min_r:
            break
        inner = r - shell
        y = base_y + t
        for dz in range(-r, r + 1, step):
            outer_half = int(math.sqrt(max(0, r * r - dz * dz)))
            inner_half = (
                int(math.sqrt(max(0, inner * inner - dz * dz)))
                if abs(dz) <= inner
                else 0
            )
            z = cz + dz
            z2 = min(cz + dz + step - 1, cz + r)
            add_fill(fills, f"{label} w t{t} z{dz}", (cx - outer_half, y, z), (cx - inner_half, y, z2), block)
            add_fill(fills, f"{label} e t{t} z{dz}", (cx + inner_half, y, z), (cx + outer_half, y, z2), block)
        top_y = y + 1
    return top_y


def _glazed_diamond(
    fills: list[Fill],
    label: str,
    face: str,
    fixed: int,
    c: int,
    cy: int,
) -> None:
    """Red/yellow glazed-terracotta diamond medallion on a wall face.

    face 'n'/'s': fixed = z of the wall, medallion spans x around c.
    face 'e'/'w': fixed = x of the wall, medallion spans z around c.
    """
    rows = ((-2, 0, M.RED_GLAZED), (-1, 1, M.YELLOW_GLAZED), (0, 2, M.RED_GLAZED),
            (1, 1, M.YELLOW_GLAZED), (2, 0, M.RED_GLAZED))
    for dy, half, block in rows:
        if face in ("n", "s"):
            a, b = (c - half, cy + dy), (c + half, cy + dy)
            add_fill(fills, f"{label} y{cy + dy}", (a[0], a[1], fixed), (b[0], b[1], fixed), block)
        else:
            add_fill(fills, f"{label} y{cy + dy}", (fixed, cy + dy, c - half), (fixed, cy + dy, c + half), block)


def _camel(
    fills: list[Fill],
    label: str,
    x: int,
    z: int,
    facing: str = "east",
    sitting: bool = False,
    blanket: str = M.RED_WOOL,
    rein_to: int | None = None,
    mooring: bool = False,
) -> None:
    """One blocky Bactrian camel standing on the caravan road (road top y3).

    facing 'east': head toward +x; 'west': head toward -x.
    Body offsets 0..9 along the facing axis, 4 wide in z (z..z+3); all
    bodies straddle REIN_Z so the iron-bar reins stay connected.
    rein_to: x of the mooring post on the camel ahead (draws the rope).
    mooring: add a rear tether post for the camel behind.
    """
    d = 1 if facing == "east" else -1

    def px(o: int) -> int:
        return x + d * o

    if sitting:
        body_y1, body_y2 = 4, 6
        neck = ((9, 6, 7), (10, 7, 9))
        head_y1, head_y2 = 8, 10
        hump_y1, hump_y2 = 7, 8
        blanket_y = 7
        hay_y1, hay_y2 = 8, 9
        post_top = 9
    else:
        body_y1, body_y2 = 8, 10
        neck = ((9, 10, 11), (10, 11, 13))
        head_y1, head_y2 = 12, 14
        hump_y1, hump_y2 = 11, 12
        blanket_y = 11
        hay_y1, hay_y2 = 12, 13
        post_top = 13

    # Legs: four 2x2 columns (standing) or folded pads at the sides (sitting).
    if not sitting:
        for o1, tag in ((2, "front"), (6, "rear")):
            add_fill(fills, f"{label} leg {tag} n", (px(o1), 4, z), (px(o1 + 1), 7, z + 1), CAMEL_LEG)
            add_fill(fills, f"{label} leg {tag} s", (px(o1), 4, z + 2), (px(o1 + 1), 7, z + 3), CAMEL_LEG)
    else:
        add_fill(fills, f"{label} leg fold n", (px(2), 4, z - 1), (px(7), 4, z - 1), CAMEL_LEG)
        add_fill(fills, f"{label} leg fold s", (px(2), 4, z + 4), (px(7), 4, z + 4), CAMEL_LEG)

    # Body, blanket, hay cargo, twin humps with brown tips.
    add_fill(fills, f"{label} body", (px(0), body_y1, z), (px(9), body_y2, z + 3), CAMEL_BODY)
    add_fill(fills, f"{label} blanket", (px(3), blanket_y, z), (px(6), blanket_y, z + 3), blanket)
    add_fill(fills, f"{label} hay cargo", (px(4), hay_y1, z + 1), (px(5), hay_y2, z + 2), HAY)
    for o1, tag in ((1, "front"), (7, "rear")):
        add_fill(fills, f"{label} hump {tag}", (px(o1), hump_y1, z + 1), (px(o1 + 1), hump_y1, z + 2), CAMEL_BODY)
        add_fill(fills, f"{label} hump {tag} tip", (px(o1), hump_y2, z + 1), (px(o1 + 1), hump_y2, z + 2), BROWN_WOOL)

    # Stepped neck, brown mane, head, ears.
    n1o, n1y1, n1y2 = neck[0]
    n2o, n2y1, n2y2 = neck[1]
    add_fill(fills, f"{label} neck 1", (px(n1o), n1y1, z + 1), (px(n1o), n1y2, z + 2), CAMEL_BODY)
    add_fill(fills, f"{label} neck 2", (px(n2o), n2y1, z + 1), (px(n2o), n2y2, z + 2), CAMEL_BODY)
    add_fill(fills, f"{label} mane", (px(n1o), n1y2 + 1, z + 1), (px(n1o), n1y2 + 1, z + 2), BROWN_WOOL)
    add_fill(fills, f"{label} head", (px(11), head_y1, z + 1), (px(13), head_y2, z + 2), CAMEL_BODY)
    add_fill(fills, f"{label} ear n", (px(11), head_y2 + 1, z + 1), (px(11), head_y2 + 1, z + 1), BROWN_WOOL)
    add_fill(fills, f"{label} ear s", (px(11), head_y2 + 1, z + 2), (px(11), head_y2 + 1, z + 2), BROWN_WOOL)

    # Hitching post ahead of the head; iron-bar reins to the camel in front.
    add_fill(fills, f"{label} rein post", (px(14), 4, REIN_Z), (px(14), post_top, REIN_Z), M.FENCE)
    if rein_to is not None:
        if sitting:
            # Sagging rope climbing from the low head to the mooring post.
            add_fill(fills, f"{label} rein rope 1", (px(15), 9, REIN_Z), (px(16), 9, REIN_Z), M.IRON_BARS)
            add_fill(fills, f"{label} rein rope 2", (px(17), 11, REIN_Z), (px(18), 11, REIN_Z), M.IRON_BARS)
            add_fill(fills, f"{label} rein rope 3", (px(19), 13, REIN_Z), (rein_to, 13, REIN_Z), M.IRON_BARS)
        else:
            add_fill(fills, f"{label} rein rope", (px(15), 13, REIN_Z), (rein_to, 13, REIN_Z), M.IRON_BARS)
    if mooring:
        add_fill(fills, f"{label} mooring post", (px(0), body_y2 + 1, REIN_Z), (px(0), 13, REIN_Z), M.FENCE)


def _market_shed(fills: list[Fill], label: str, sx: int, sz: int, wool_a: str, wool_b: str) -> None:
    """Open spice-market shed: four log posts, hay roof, goods below."""
    zc = sz + 4
    for j, (px0, pz0) in enumerate(((sx + 1, sz + 1), (sx + 17, sz + 1), (sx + 1, sz + 7), (sx + 17, sz + 7))):
        add_fill(fills, f"{label} post {j}", (px0, 4, pz0), (px0, 9, pz0), M.LOG)
    add_fill(fills, f"{label} hay roof", (sx, 10, sz), (sx + 18, 10, sz + 8), HAY)
    add_fill(fills, f"{label} hay ridge", (sx + 2, 11, zc), (sx + 16, 11, zc), HAY)
    # Spice sacks: 2x2x2 wool bales in two hues.
    add_fill(fills, f"{label} sacks a", (sx + 2, 4, sz + 2), (sx + 3, 5, sz + 3), wool_a)
    add_fill(fills, f"{label} sacks b", (sx + 2, 4, sz + 5), (sx + 3, 5, sz + 6), wool_b)
    # Jar row: barrels plus a flower pot.
    add_fill(fills, f"{label} jars", (sx + 6, 4, sz + 2), (sx + 9, 4, sz + 2), BARREL)
    add_fill(fills, f"{label} jar pot", (sx + 10, 4, sz + 2), (sx + 10, 4, sz + 2), FLOWER_POT)
    # Silk-bolt shelf: wood boards with stacked wool rolls.
    add_fill(fills, f"{label} shelf 1", (sx + 13, 5, sz + 6), (sx + 17, 5, sz + 7), M.WOOD)
    add_fill(fills, f"{label} shelf 2", (sx + 13, 7, sz + 6), (sx + 17, 7, sz + 7), M.WOOD)
    add_fill(fills, f"{label} bolts lower", (sx + 13, 6, sz + 6), (sx + 16, 6, sz + 6), wool_a)
    add_fill(fills, f"{label} bolts upper", (sx + 13, 8, sz + 6), (sx + 16, 8, sz + 6), wool_b)


# ---------------------------------------------------------------------------
# Main builder.
# ---------------------------------------------------------------------------
def build_silk_caravan_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Site grading: clear leftover crops, lay stone + grass terrace,
    #    then cut the east-west yellow-sand caravan road with curbs.
    # ------------------------------------------------------------------
    add_fill(fills, "silk clear site", (SITE_X1, 4, SITE_Z1), (SITE_X2, 7, SITE_Z2), M.AIR)
    add_fill(fills, "silk terrace stone", (SITE_X1, 0, SITE_Z1), (SITE_X2, 1, SITE_Z2), M.STONE)
    add_fill(fills, "silk terrace grass", (SITE_X1, 2, SITE_Z1), (SITE_X2, 3, SITE_Z2), M.GRASS)
    add_fill(fills, "silk road sand", (ROAD_X1, 2, ROAD_Z1), (ROAD_X2, 3, ROAD_Z2), SAND)
    add_fill(fills, "silk road curb n", (ROAD_X1, 3, CURB_N1), (ROAD_X2, 3, CURB_N2), M.ANDESITE)
    add_fill(fills, "silk road curb s", (ROAD_X1, 3, CURB_S1), (ROAD_X2, 3, CURB_S2), M.ANDESITE)

    # ------------------------------------------------------------------
    # 2. The camel caravan: five Bactrian camels heading east toward
    #    Kaiyuan Gate - four standing, one kneeling to rest.
    # ------------------------------------------------------------------
    _camel(fills, "silk camel lead", -296, 2577, "east", blanket=M.RED_WOOL, mooring=True)
    _camel(fills, "silk camel 2", -324, 2579, "east", blanket=M.YELLOW_WOOL, rein_to=-296, mooring=True)
    _camel(fills, "silk camel 3", -352, 2578, "east", blanket=M.BLUE_WOOL, rein_to=-324, mooring=True)
    _camel(fills, "silk camel rest", -382, 2580, "east", sitting=True, blanket=M.GREEN_WOOL, rein_to=-352, mooring=True)
    _camel(fills, "silk camel 5", -410, 2577, "east", blanket=M.WHITE_WOOL, rein_to=-382)

    # ------------------------------------------------------------------
    # 3. Persian trade house (波斯邸货栈): plinth, two storeys, glazed
    #    diamonds, balcony gallery, drum + cut-sandstone dome.
    # ------------------------------------------------------------------
    add_fill(fills, "silk wh plinth", (WH_X1 - 2, 4, WH_Z1 - 2), (WH_X2 + 2, 4, WH_Z2 + 2), M.STONE)
    add_fill(fills, "silk wh floor", (WH_X1 + 1, 4, WH_Z1 + 1), (WH_X2 - 1, 4, WH_Z2 - 1), M.WOOD)
    # Storey 1: red walls, timber columns.
    add_outline(fills, "silk wh walls 1", WH_X1, WH_Z1, WH_X2, WH_Z2, 5, 12, M.RED_WALL)
    add_column_grid(fills, "silk wh columns", WH_X1, WH_Z1, WH_X2, WH_Z2, 5, 12, 20, M.LOG)
    # Three stepped arches on the road-facing south front.
    for i, dx in enumerate((-346, -316, -286)):
        add_fill(fills, f"silk wh arch {i} opening", (dx, 5, WH_Z2), (dx + 4, 10, WH_Z2), M.AIR)
        add_fill(fills, f"silk wh arch {i} step w", (dx, 9, WH_Z2), (dx, 10, WH_Z2), M.RED_WALL)
        add_fill(fills, f"silk wh arch {i} step e", (dx + 4, 9, WH_Z2), (dx + 4, 10, WH_Z2), M.RED_WALL)
        add_fill(fills, f"silk wh arch {i} lintel", (dx - 1, 11, WH_Z2), (dx + 5, 11, WH_Z2), LOG_X)
    # Side doors on the west and east walls.
    for face, fx, lz in (("w", WH_X1, 2478), ("e", WH_X2, 2478)):
        add_fill(fills, f"silk wh door {face} opening", (fx, 5, lz), (fx, 10, lz + 4), M.AIR)
        add_fill(fills, f"silk wh door {face} step n", (fx, 9, lz), (fx, 10, lz), M.RED_WALL)
        add_fill(fills, f"silk wh door {face} step s", (fx, 9, lz + 4), (fx, 10, lz + 4), M.RED_WALL)
        add_fill(fills, f"silk wh door {face} lintel", (fx, 11, lz - 1), (fx, 11, lz + 5), LOG_Z)
    # Yellow glazed band along the storey-1 top rows.
    add_fill(fills, "silk wh band s", (WH_X1, 12, WH_Z2), (WH_X2, 12, WH_Z2), M.YELLOW_GLAZED)
    add_fill(fills, "silk wh band n", (WH_X1, 12, WH_Z1), (WH_X2, 12, WH_Z1), M.YELLOW_GLAZED)
    # Red/yellow glazed diamond medallions on all four walls.
    for i, mx in enumerate((-329, -301, -271)):
        _glazed_diamond(fills, f"silk wh diamond s{i}", "s", WH_Z2, mx, 8)
    _glazed_diamond(fills, "silk wh diamond n", "n", WH_Z1, -310, 8)
    _glazed_diamond(fills, "silk wh diamond w", "w", WH_X1, 2492, 8)
    _glazed_diamond(fills, "silk wh diamond e", "e", WH_X2, 2492, 8)
    # Balcony gallery (平座) between the storeys.
    add_cantilevered_floor(fills, "silk wh gallery", WH_X1, WH_Z1, WH_X2, WH_Z2, y=13, overhang=2, block=M.WOOD)
    add_outline(fills, "silk wh gallery rail", WH_X1 - 2, WH_Z1 - 2, WH_X2 + 2, WH_Z2 + 2, 14, 14, M.FENCE)
    # Storey 2: white walls with arched windows and yellow diamonds.
    add_outline(fills, "silk wh walls 2", WH_X1, WH_Z1, WH_X2, WH_Z2, 14, 20, M.WHITE_TERRACOTTA)
    for face, fz, wins in (("s", WH_Z2, (-345, -315, -285)), ("n", WH_Z1, (-315,))):
        for i, wx in enumerate(wins):
            add_fill(fills, f"silk wh win {face}{i}", (wx, 15, fz), (wx + 2, 18, fz), M.AIR)
            add_fill(fills, f"silk wh win {face}{i} step w", (wx, 18, fz), (wx, 18, fz), M.WHITE_TERRACOTTA)
            add_fill(fills, f"silk wh win {face}{i} step e", (wx + 2, 18, fz), (wx + 2, 18, fz), M.WHITE_TERRACOTTA)
    _glazed_diamond(fills, "silk wh diamond 2 s", "s", WH_Z2, -331, 17)
    # Flat roof with parapet; the dome drum rises from its centre.
    add_fill(fills, "silk wh roof", (WH_X1, 21, WH_Z1), (WH_X2, 21, WH_Z2), M.WOOD)
    add_outline(fills, "silk wh parapet", WH_X1, WH_Z1, WH_X2, WH_Z2, 22, 22, M.RED_WALL)
    add_outline(fills, "silk wh drum", DRUM_X1, DRUM_Z1, DRUM_X2, DRUM_Z2, 21, 24, CUT_SANDSTONE)
    add_fill(fills, "silk wh drum win n", (WH_CX, 22, DRUM_Z1), (WH_CX + 1, 23, DRUM_Z1), M.AIR)
    add_fill(fills, "silk wh drum win s", (WH_CX, 22, DRUM_Z2), (WH_CX + 1, 23, DRUM_Z2), M.AIR)
    add_fill(fills, "silk wh drum win w", (DRUM_X1, 22, WH_CZ), (DRUM_X1, 23, WH_CZ + 1), M.AIR)
    add_fill(fills, "silk wh drum win e", (DRUM_X2, 22, WH_CZ), (DRUM_X2, 23, WH_CZ + 1), M.AIR)
    # Flared skirt of sandstone stairs, then the shrinking ring dome.
    add_fill(fills, "silk dome skirt n", (DRUM_X1 + 1, 24, DRUM_Z1 - 1), (DRUM_X2 - 1, 24, DRUM_Z1 - 1), _sandstone_stair("south"))
    add_fill(fills, "silk dome skirt s", (DRUM_X1 + 1, 24, DRUM_Z2 + 1), (DRUM_X2 - 1, 24, DRUM_Z2 + 1), _sandstone_stair("north"))
    add_fill(fills, "silk dome skirt w", (DRUM_X1 - 1, 24, DRUM_Z1 + 1), (DRUM_X1 - 1, 24, DRUM_Z2 - 1), _sandstone_stair("east"))
    add_fill(fills, "silk dome skirt e", (DRUM_X2 + 1, 24, DRUM_Z1 + 1), (DRUM_X2 + 1, 24, DRUM_Z2 - 1), _sandstone_stair("west"))
    dome_top = _persian_dome(fills, "silk wh dome", WH_CX, WH_CZ, DOME_R, DOME_BASE_Y)
    add_fill(fills, "silk wh dome finial", (WH_CX - 1, dome_top, WH_CZ - 1), (WH_CX + 1, dome_top + 2, WH_CZ + 1), M.GOLD)
    # Interior: spiral stairs, traded goods.
    add_spiral_stair(fills, "silk wh stair 1", WH_CX, WH_CZ, 4, 5, 12, M.SMOOTH)
    add_fill(fills, "silk wh stair hole", (WH_CX - 4, 13, WH_CZ - 4), (WH_CX + 1, 13, WH_CZ - 3), M.AIR)
    add_spiral_stair(fills, "silk wh stair 2", WH_CX, WH_CZ, 4, 13, 20, M.SMOOTH)
    add_fill(fills, "silk wh jars", (-360, 5, 2500), (-350, 6, 2500), BARREL)
    add_fill(fills, "silk wh hay pile", (-270, 5, 2460), (-266, 6, 2462), HAY)
    add_fill(fills, "silk wh crates", (-330, 5, 2505), (-326, 6, 2507), M.WOOD)
    add_fill(fills, "silk wh bales red", (-300, 5, 2470), (-297, 6, 2471), M.RED_WOOL)
    add_fill(fills, "silk wh bales yellow", (-296, 5, 2470), (-293, 6, 2471), M.YELLOW_WOOL)

    # ------------------------------------------------------------------
    # 4. Forecourt between the trade house and the road: paving, a
    #    Persian carpet in wool, lantern posts.
    # ------------------------------------------------------------------
    add_fill(fills, "silk forecourt pave", (-380, 3, 2518), (-220, 3, 2560), M.ANDESITE)
    add_outline(fills, "silk carpet border", -350, 2530, -280, 2544, 4, 4, M.RED_WOOL)
    for cz in range(2531, 2544, 2):
        wool = M.YELLOW_WOOL if cz % 2 == 0 else M.BLUE_WOOL
        add_fill(fills, f"silk carpet stripe {cz}", (-349, 4, cz), (-281, 4, cz), wool)
    add_fill(fills, "silk carpet medallion", (-319, 4, 2535), (-311, 4, 2539), M.YELLOW_WOOL)
    add_fill(fills, "silk carpet core", (-317, 4, 2536), (-313, 4, 2538), M.RED_WOOL)
    for i, (px0, pz0) in enumerate(((-370, 2555), (-230, 2555))):
        add_fill(fills, f"silk forecourt lamp {i}", (px0, 4, pz0), (px0, 6, pz0), M.FENCE)
        add_fill(fills, f"silk forecourt lamp {i} light", (px0, 7, pz0), (px0, 7, pz0), M.LANTERN)

    # ------------------------------------------------------------------
    # 5. Caravaneer lighthouse (胡商望乡灯塔) east of the trade house:
    #    quartz shaft with red bands, sea-lantern lamp room, pyramid top.
    # ------------------------------------------------------------------
    add_fill(fills, "silk light base", (-204, 4, 2476), (-196, 5, 2484), M.STONE)
    add_outline(fills, "silk light shaft", -202, 2478, -198, 2482, 6, 15, M.QUARTZ)
    add_fill(fills, "silk light door", (-202, 6, 2479), (-202, 9, 2481), M.AIR)
    add_outline(fills, "silk light band 1", -202, 2478, -198, 2482, 10, 10, M.RED_WALL)
    add_outline(fills, "silk light band 2", -202, 2478, -198, 2482, 13, 13, M.RED_WALL)
    add_fill(fills, "silk light balcony", (-204, 16, 2476), (-196, 16, 2484), M.WOOD)
    add_outline(fills, "silk light rail", -204, 2476, -196, 2484, 17, 17, M.FENCE)
    add_outline(fills, "silk light lamp room", -203, 2477, -197, 2483, 18, 20, M.QUARTZ)
    add_fill(fills, "silk light lamp core", (-201, 18, 2479), (-199, 20, 2481), M.SEA_LANTERN)
    add_fill(fills, "silk light roof 1", (-203, 21, 2477), (-197, 21, 2483), M.RED_WALL)
    add_fill(fills, "silk light roof 2", (-202, 22, 2478), (-198, 22, 2482), M.RED_WALL)
    add_fill(fills, "silk light roof 3", (-201, 23, 2479), (-199, 23, 2481), M.RED_WALL)
    add_fill(fills, "silk light spike", (-200, 24, 2480), (-200, 26, 2480), M.GOLD)

    # ------------------------------------------------------------------
    # 6. Spice market: two staggered rows of open sheds south of the road.
    # ------------------------------------------------------------------
    sheds = [
        (-470, 2616, M.YELLOW_WOOL, M.RED_WOOL),
        (-400, 2616, M.GREEN_WOOL, M.YELLOW_WOOL),
        (-330, 2616, M.RED_WOOL, M.BLUE_WOOL),
        (-460, 2650, M.BLUE_WOOL, M.YELLOW_WOOL),
        (-370, 2650, M.YELLOW_WOOL, M.RED_WOOL),
    ]
    for i, (sx, sz, wa, wb) in enumerate(sheds):
        _market_shed(fills, f"silk shed {i}", sx, sz, wa, wb)

    # ------------------------------------------------------------------
    # 7. Goods yard behind (north of) the trade house: hay ricks, crate
    #    stacks, wheelbarrow props.
    # ------------------------------------------------------------------
    for i, (hx, hz) in enumerate(((-350, 2410), (-330, 2412), (-310, 2408))):
        add_fill(fills, f"silk rick {i}", (hx, 4, hz), (hx + 2, 5, hz + 2), HAY)
        add_fill(fills, f"silk rick {i} cap", (hx + 1, 6, hz + 1), (hx + 1, 6, hz + 1), HAY)
    crates = [(-360, 2430), (-352, 2430), (-344, 2430), (-360, 2438), (-352, 2438), (-344, 2438)]
    for i, (bx, bz) in enumerate(crates):
        add_fill(fills, f"silk crate {i}", (bx, 4, bz), (bx + 1, 5, bz + 1), M.WOOD)
    for i, (bx, bz) in enumerate(((-320, 2425), (-300, 2440))):
        add_fill(fills, f"silk barrow {i} bed", (bx, 5, bz), (bx + 2, 5, bz + 1), M.WOOD)
        add_fill(fills, f"silk barrow {i} legs", (bx, 4, bz), (bx, 4, bz + 1), M.FENCE)
        add_fill(fills, f"silk barrow {i} wheel", (bx + 3, 4, bz), (bx + 3, 5, bz), M.FENCE)
        add_fill(fills, f"silk barrow {i} handles", (bx + 3, 6, bz), (bx + 4, 6, bz + 1), M.FENCE)

    # ------------------------------------------------------------------
    # 8. Way station west of the trade house: walled yard, two-stall
    #    stable, water trough, hay canopy.
    # ------------------------------------------------------------------
    add_fill(fills, "silk station pave", (-508, 3, 2432), (-432, 3, 2528), M.ANDESITE)
    add_outline(fills, "silk station wall", -508, 2432, -432, 2528, 4, 5, M.STONE)
    add_fill(fills, "silk station gate", (-474, 4, 2528), (-466, 5, 2528), M.AIR)
    # Stable: two stalls with a log divider, hay roof, mangers, bedding.
    add_outline(fills, "silk stable walls", -504, 2436, -470, 2458, 4, 8, M.WOOD)
    add_fill(fills, "silk stable roof", (-505, 9, 2435), (-469, 9, 2459), HAY)
    add_fill(fills, "silk stable divider", (-487, 4, 2437), (-487, 8, 2457), M.LOG)
    add_fill(fills, "silk stable door a", (-498, 4, 2458), (-494, 7, 2458), M.AIR)
    add_fill(fills, "silk stable door b", (-480, 4, 2458), (-476, 7, 2458), M.AIR)
    add_fill(fills, "silk stable manger a", (-502, 4, 2438), (-490, 5, 2438), M.FENCE)
    add_fill(fills, "silk stable manger b", (-484, 4, 2438), (-472, 5, 2438), M.FENCE)
    add_fill(fills, "silk stable bedding a", (-502, 4, 2450), (-490, 4, 2455), HAY)
    add_fill(fills, "silk stable bedding b", (-484, 4, 2450), (-472, 4, 2455), HAY)
    # Stone water trough with water.
    add_fill(fills, "silk trough n", (-462, 4, 2470), (-450, 5, 2470), M.STONE)
    add_fill(fills, "silk trough s", (-462, 4, 2472), (-450, 5, 2472), M.STONE)
    add_fill(fills, "silk trough w", (-462, 4, 2470), (-462, 5, 2472), M.STONE)
    add_fill(fills, "silk trough e", (-450, 4, 2470), (-450, 5, 2472), M.STONE)
    add_fill(fills, "silk trough water", (-461, 4, 2471), (-451, 4, 2471), M.WATER)
    # Hay canopy over the resting yard.
    for j, (px0, pz0) in enumerate(((-495, 2480), (-475, 2480), (-495, 2496), (-475, 2496))):
        add_fill(fills, f"silk canopy post {j}", (px0, 4, pz0), (px0, 8, pz0), M.LOG)
    add_fill(fills, "silk canopy roof", (-497, 9, 2478), (-473, 9, 2498), HAY)
    add_fill(fills, "silk canopy ridge", (-494, 10, 2481), (-476, 10, 2495), HAY)
    add_fill(fills, "silk station bale 1", (-460, 4, 2500), (-458, 5, 2502), HAY)
    add_fill(fills, "silk station bale 2", (-456, 4, 2502), (-454, 5, 2504), HAY)
    add_fill(fills, "silk station lamp post", (-470, 4, 2490), (-470, 5, 2490), M.FENCE)
    add_fill(fills, "silk station lamp", (-470, 6, 2490), (-470, 6, 2490), M.LANTERN)

    # ------------------------------------------------------------------
    # 9. Desert poplars and lantern posts flanking the caravan road.
    # ------------------------------------------------------------------
    poplars = [(-440, 2563), (-360, 2563), (-280, 2563), (-440, 2607), (-360, 2607), (-280, 2607), (-200, 2607)]
    for i, (tx, tz) in enumerate(poplars):
        add_tree(fills, f"silk poplar {i}", tx, tz, 4, height=7, spread=2)
    add_lantern_line(fills, "silk road lamps n", -480, 2566, -160, 2566, 4, 80)
    add_lantern_line(fills, "silk road lamps s", -480, 2603, -160, 2603, 4, 80)


def main() -> None:
    run_builder(build_silk_caravan_3d, "silk_caravan_3d")


if __name__ == "__main__":
    main()
