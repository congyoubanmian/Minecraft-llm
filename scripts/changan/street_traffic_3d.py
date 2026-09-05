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
    add_fill,
    add_outline,
    run_builder,
)


"""
Street Traffic 3D (朱雀大街市井车马·长安行旅) - the "market bustle" overlay
for imperial Zhuque Avenue: freight oxcarts, an official sedan chair, a
pack-donkey train, wheelbarrows, loaded porters and a roadside rest
pavilion, after the verse "长安大道连狭斜，青牛白马七香车"
(Lu Zhaolin, 《长安古意》).

Location in Chang'an city local coordinates:
    Two service lanes flanking Zhuque Avenue: west lane x 2780..2890 and
    east lane x 3110..3220, z 1000..3400. The centre band x 2900..3100 is
    STRICTLY FORBIDDEN: it holds the watchtower network
    (wanglou_network_3d.py towers near x 2860/3140, yards reaching
    x 2850..2870 / 3130..3150 - every set piece here keeps well clear of
    those yards too) and the flush pavement lamps of night_lighting_3d.py
    at x 2985/3015. A hard bounds guard in the builder rejects any fill
    that touches the forbidden band. Nothing is dug: the lane surface is
    turf y2..3 and every cart wheel, hoof and foot starts at y4
    (underground_drain_3d.py at negative y is untouched). Ward housing
    underneath may be overlapped by design.

Sections (分区清单):
    1. 货运牛车 Freight oxcarts x2 (signature piece) - two-wheeled timber
       carts: 5x5 vertical FENCE-ring wheels with WOOD spokes and LOG
       hubs, plank bed with fence side-rails and a RED_WOOL canvas arc
       tilt, long LOG shafts, and a QUARTZ draft ox (3x2x5 body, neck,
       head, ears, tail) in a FENCE yoke between the shafts; one cart
       hauls grain sacks, the other silk crates.
    2. 青帷官轿 Blue-canopy official sedan x1 - BLUE_WOOL curtained cabin
       on four WOOD pillars with an arc roof, a half-rolled RED_WOOL door
       curtain, front/rear carrying poles and four QUARTZ bearers in
       straw hats.
    3. 驮驴驴队 Pack donkeys x3 - LIGHT_GRAY_WOOL donkeys with long ears,
       short bodies, hay-block panniers and white sacks, roped
       nose-to-tail towards the West Market along the west lane edge.
    4. 独轮车 Wheelbarrows x2 - single FENCE-ring wheel, plank frame and
       rails, LOG handles, barrel and sack cargo.
    5. 挑夫行人 Shoulder-porters x4 - QUARTZ figures (1x2 body + head)
       under wide WHITE_TERRACOTTA bamboo hats, LOG shoulder poles with
       WOOD baskets at both ends.
    6. 歇脚亭 Roadside rest pavilion x1 - four-post hay-thatch shelter
       with plank benches, a water jar and two hitching posts.
    7. 路牌 Directional signposts x2 - FENCE posts with WOOD pointer
       boards and a red arrow tip: west market <- and east market ->.

Distinctive features (English):
    - Working two-wheeled oxcarts with ring-spoke wheels, red canvas
      tilts and a harnessed quartz ox slung between the shafts
    - A blue-canopy sedan chair on shoulder poles borne by four
      hatted bearers, door curtain rolled to half mast
    - A nose-to-tail rope line of long-eared pack donkeys with
      hay panniers heading for the West Market
    - Single-wheel barrows, bamboo-hatted porters with loaded
      shoulder poles, and a thatched wayside rest with hitching posts
    - Every one of the 15 set pieces stays strictly inside the two
      side-lane rectangles and clear of the watchtower/light x-band
"""


# ---------------------------------------------------------------------------
# Site bounds (硬约束常量).
# ---------------------------------------------------------------------------
WEST_X1, WEST_X2 = 2780, 2890          # west service lane of Zhuque Avenue
EAST_X1, EAST_X2 = 3110, 3220          # east service lane of Zhuque Avenue
LANE_Z1, LANE_Z2 = 1000, 3400          # along-avenue extent
FORBIDDEN_X1, FORBIDDEN_X2 = 2900, 3100  # wanglou + pavement-light band
GROUND_Y = 4                           # turf tops out at y3; builds start y4

# Blocks not present in the shared palette.
LIGHT_GRAY_WOOL = "minecraft:light_gray_wool"
HAY = "minecraft:hay_block"
BARREL = "minecraft:barrel"
LOG_X = "minecraft:dark_oak_log[axis=x]"
LOG_Z = "minecraft:dark_oak_log[axis=z]"


# ---------------------------------------------------------------------------
# Reusable set-piece builders.
# ---------------------------------------------------------------------------
def _oxcart(
    fills: list[Fill],
    label: str,
    cx: int,
    cz: int,
    d: int,
    cargo: str,
) -> None:
    """One two-wheeled freight cart with a yoked draft ox (货运牛车).

    Anchor (cx, cz) is the wheel-axle centre line; d = -1 faces north
    (forward = -z), d = +1 faces south. The plank bed and canvas tilt sit
    behind the axle, the ox ahead of it between the twin shafts.
    cargo: "grain" (white sacks) or "silk" (plank crates, red strap).
    """

    def pz(o: int) -> int:
        return cz + d * o

    # 1. Wheels: two vertical 5x5 disks in the x-y plane at the axle line.
    for wx in (cx - 3, cx + 3):
        add_fill(fills, f"{label} wheel rim top", (wx - 2, 8, pz(0)), (wx + 2, 8, pz(0)), M.FENCE)
        add_fill(fills, f"{label} wheel rim bottom", (wx - 2, 4, pz(0)), (wx + 2, 4, pz(0)), M.FENCE)
        add_fill(fills, f"{label} wheel rim west", (wx - 2, 5, pz(0)), (wx - 2, 7, pz(0)), M.FENCE)
        add_fill(fills, f"{label} wheel rim east", (wx + 2, 5, pz(0)), (wx + 2, 7, pz(0)), M.FENCE)
        add_fill(fills, f"{label} wheel spoke west", (wx - 1, 6, pz(0)), (wx - 1, 6, pz(0)), M.WOOD)
        add_fill(fills, f"{label} wheel spoke east", (wx + 1, 6, pz(0)), (wx + 1, 6, pz(0)), M.WOOD)
        add_fill(fills, f"{label} wheel spoke up", (wx, 7, pz(0)), (wx, 7, pz(0)), M.WOOD)
        add_fill(fills, f"{label} wheel spoke down", (wx, 5, pz(0)), (wx, 5, pz(0)), M.WOOD)
        add_fill(fills, f"{label} wheel hub", (wx, 6, pz(0)), (wx, 6, pz(0)), M.LOG)

    # 2. Bed: under-frame, plank floor, fence rails, end boards.
    blo, bhi = min(pz(-1), pz(-6)), max(pz(-1), pz(-6))
    add_fill(fills, f"{label} bed frame", (cx - 2, 6, blo), (cx + 2, 6, bhi), M.WOOD)
    add_fill(fills, f"{label} bed floor", (cx - 2, 7, blo), (cx + 2, 7, bhi), M.WOOD)
    add_fill(fills, f"{label} bed rail west", (cx - 2, 8, blo), (cx - 2, 8, bhi), M.FENCE)
    add_fill(fills, f"{label} bed rail east", (cx + 2, 8, blo), (cx + 2, 8, bhi), M.FENCE)
    add_fill(fills, f"{label} bed board front", (cx - 1, 8, pz(-1)), (cx + 1, 8, pz(-1)), M.WOOD)
    add_fill(fills, f"{label} bed board rear", (cx - 1, 8, pz(-6)), (cx + 1, 8, pz(-6)), M.WOOD)

    # 3. Canvas tilt (盖布弧顶): sloped sides, raised crown, gable ends.
    add_fill(fills, f"{label} canvas west", (cx - 2, 9, blo), (cx - 2, 9, bhi), M.RED_WOOL)
    add_fill(fills, f"{label} canvas east", (cx + 2, 9, blo), (cx + 2, 9, bhi), M.RED_WOOL)
    add_fill(fills, f"{label} canvas crown", (cx - 1, 10, blo), (cx + 1, 10, bhi), M.RED_WOOL)
    add_fill(fills, f"{label} canvas gable front", (cx - 1, 9, pz(-1)), (cx + 1, 9, pz(-1)), M.RED_WOOL)
    add_fill(fills, f"{label} canvas gable rear", (cx - 1, 9, pz(-6)), (cx + 1, 9, pz(-6)), M.RED_WOOL)

    # 4. Cargo inside the tilt.
    if cargo == "grain":
        slo, shi = min(pz(-2), pz(-3)), max(pz(-2), pz(-3))
        add_fill(fills, f"{label} grain sacks", (cx - 1, 8, slo), (cx + 1, 8, shi), M.WHITE_TERRACOTTA)
        add_fill(fills, f"{label} grain sacks top", (cx - 1, 9, slo), (cx, 9, shi), M.WHITE_TERRACOTTA)
        add_fill(fills, f"{label} cargo barrel", (cx + 1, 8, pz(-5)), (cx + 1, 8, pz(-5)), BARREL)
    else:
        clo, chi = min(pz(-2), pz(-4)), max(pz(-2), pz(-4))
        add_fill(fills, f"{label} silk crates", (cx - 1, 8, clo), (cx + 1, 8, chi), M.WOOD)
        add_fill(fills, f"{label} silk strap", (cx - 1, 9, pz(-3)), (cx + 1, 9, pz(-3)), M.RED_WOOL)
        add_fill(fills, f"{label} cargo barrel", (cx + 1, 8, pz(-5)), (cx + 1, 8, pz(-5)), BARREL)

    # 5. Twin shafts (双辕杆) from the bed front forward past the wheels.
    solo, sohi = min(pz(-1), pz(5)), max(pz(-1), pz(5))
    add_fill(fills, f"{label} shaft west", (cx - 2, 7, solo), (cx - 2, 7, sohi), LOG_Z)
    add_fill(fills, f"{label} shaft east", (cx + 2, 7, solo), (cx + 2, 7, sohi), LOG_Z)

    # 6. Draft ox (驾辕牛): 3x2x5 body on four legs, neck, head, ears, tail.
    add_fill(fills, f"{label} ox leg front w", (cx - 1, 4, pz(5)), (cx - 1, 6, pz(5)), M.QUARTZ)
    add_fill(fills, f"{label} ox leg front e", (cx + 1, 4, pz(5)), (cx + 1, 6, pz(5)), M.QUARTZ)
    add_fill(fills, f"{label} ox leg rear w", (cx - 1, 4, pz(1)), (cx - 1, 6, pz(1)), M.QUARTZ)
    add_fill(fills, f"{label} ox leg rear e", (cx + 1, 4, pz(1)), (cx + 1, 6, pz(1)), M.QUARTZ)
    add_fill(fills, f"{label} ox body", (cx - 1, 7, min(pz(1), pz(5))), (cx + 1, 8, max(pz(1), pz(5))), M.QUARTZ)
    add_fill(fills, f"{label} ox neck", (cx - 1, 9, pz(5)), (cx + 1, 10, pz(5)), M.QUARTZ)
    add_fill(fills, f"{label} ox head", (cx - 1, 9, pz(6)), (cx + 1, 10, pz(6)), M.QUARTZ)
    add_fill(fills, f"{label} ox ear west", (cx - 1, 11, pz(6)), (cx - 1, 11, pz(6)), M.QUARTZ)
    add_fill(fills, f"{label} ox ear east", (cx + 1, 11, pz(6)), (cx + 1, 11, pz(6)), M.QUARTZ)
    add_fill(fills, f"{label} ox tail", (cx, 6, pz(0)), (cx, 7, pz(0)), M.QUARTZ)
    add_fill(fills, f"{label} ox nose bag", (cx, 8, pz(6)), (cx, 8, pz(6)), M.WOOD)

    # 7. Yoke (套轭) across the shoulders tying both shaft ends, plus a
    #    back strap and yoke pins.
    add_fill(fills, f"{label} yoke", (cx - 2, 8, pz(5)), (cx + 2, 8, pz(5)), M.FENCE)
    add_fill(fills, f"{label} yoke pin west", (cx - 2, 9, pz(5)), (cx - 2, 9, pz(5)), M.FENCE)
    add_fill(fills, f"{label} yoke pin east", (cx + 2, 9, pz(5)), (cx + 2, 9, pz(5)), M.FENCE)
    add_fill(fills, f"{label} harness strap", (cx - 1, 9, pz(3)), (cx + 1, 9, pz(3)), M.IRON_BARS)
    add_fill(fills, f"{label} mounting step", (cx, 4, pz(-7)), (cx, 4, pz(-7)), M.SMOOTH)


def _sedan(fills: list[Fill], label: str, cx: int, cz: int, d: int) -> None:
    """Blue-canopy official sedan chair with four bearers (青帷官轿).

    Anchor (cx, cz) is the cabin centre; d = +1 means the door face and
    front bearer pair sit at larger z.
    """

    def pz(o: int) -> int:
        return cz + d * o

    # 1. Cabin floor and four corner pillars.
    flo, fhi = min(pz(-2), pz(2)), max(pz(-2), pz(2))
    add_fill(fills, f"{label} floor", (cx - 2, 7, flo), (cx + 2, 7, fhi), M.WOOD)
    for px in (cx - 2, cx + 2):
        for pzl in (pz(-2), pz(2)):
            add_fill(fills, f"{label} pillar {px},{pzl}", (px, 8, pzl), (px, 9, pzl), M.WOOD)

    # 2. Blue wool drapery walls; door face (front) stays open below the
    #    half-rolled red curtain.
    add_fill(fills, f"{label} curtain wall back", (cx - 1, 8, pz(-2)), (cx + 1, 9, pz(-2)), M.BLUE_WOOL)
    add_fill(fills, f"{label} curtain wall west", (cx - 2, 8, min(pz(-1), pz(1))), (cx - 2, 9, max(pz(-1), pz(1))), M.BLUE_WOOL)
    add_fill(fills, f"{label} curtain wall east", (cx + 2, 8, min(pz(-1), pz(1))), (cx + 2, 9, max(pz(-1), pz(1))), M.BLUE_WOOL)
    add_fill(fills, f"{label} door curtain", (cx - 1, 9, pz(2)), (cx + 1, 9, pz(2)), M.RED_WOOL)

    # 3. Blue arc roof: overhanging ring, crown, ridge knob row.
    add_outline(fills, f"{label} roof ring", cx - 2, pz(-3), cx + 2, pz(3), 10, 10, M.BLUE_WOOL)
    add_fill(fills, f"{label} roof crown", (cx - 1, 11, min(pz(-3), pz(3))), (cx + 1, 11, max(pz(-3), pz(3))), M.BLUE_WOOL)
    add_fill(fills, f"{label} roof ridge", (cx - 1, 12, min(pz(-2), pz(2))), (cx + 1, 12, max(pz(-2), pz(2))), M.BLUE_WOOL)
    for px in (cx - 2, cx + 2):
        for pzl in (pz(-3), pz(3)):
            add_fill(fills, f"{label} roof tassel {px},{pzl}", (px, 9, pzl), (px, 9, pzl), M.BLUE_WOOL)

    # 4. Twin carrying poles (抬杠) at shoulder height with upturned tips.
    polo, pohi = min(pz(-6), pz(6)), max(pz(-6), pz(6))
    add_fill(fills, f"{label} pole west", (cx - 2, 6, polo), (cx - 2, 6, pohi), LOG_Z)
    add_fill(fills, f"{label} pole east", (cx + 2, 6, polo), (cx + 2, 6, pohi), LOG_Z)
    for px in (cx - 2, cx + 2):
        for pzl in (pz(-6), pz(6)):
            add_fill(fills, f"{label} pole tip {px},{pzl}", (px, 7, pzl), (px, 7, pzl), M.FENCE)

    # 5. Four bearers (轿夫): 1x2 quartz body, head, straw hat; the poles
    #    rest on their shoulders one block beside each head.
    for pzl, tag in ((pz(5), "front"), (pz(-5), "rear")):
        for px in (cx - 3, cx + 3):
            add_fill(fills, f"{label} bearer {tag} {px} body", (px, 4, pzl), (px, 5, pzl), M.QUARTZ)
            add_fill(fills, f"{label} bearer {tag} {px} head", (px, 6, pzl), (px, 6, pzl), M.QUARTZ)
            add_fill(fills, f"{label} bearer {tag} {px} hat", (px, 7, pzl), (px, 7, pzl), M.WHITE_TERRACOTTA)

    # 6. Seat bench glimpsed through the open doorway.
    add_fill(fills, f"{label} bench", (cx - 1, 8, min(pz(-1), pz(0))), (cx + 1, 8, max(pz(-1), pz(0))), M.WOOD)


def _donkey(fills: list[Fill], label: str, x: int, z: int, d: int) -> None:
    """One pack donkey with long ears, hay pannier and sacks (驮货驴).

    Anchor (x, z) is the rump; d = -1 faces north. Body is 2 wide
    (x..x+1), 4 long, with the head raised one block at the front.
    """

    def pz(o: int) -> int:
        return z + d * o

    # Legs (o=0 rear pair, o=3 front pair; forward = +o).
    for o, tag in ((0, "rear"), (3, "front")):
        add_fill(fills, f"{label} leg {tag} w", (x, 4, pz(o)), (x, 6, pz(o)), LIGHT_GRAY_WOOL)
        add_fill(fills, f"{label} leg {tag} e", (x + 1, 4, pz(o)), (x + 1, 6, pz(o)), LIGHT_GRAY_WOOL)
    # Short body, raised neck, head, and the trademark long ears.
    add_fill(fills, f"{label} body", (x, 7, min(pz(0), pz(3))), (x + 1, 7, max(pz(0), pz(3))), LIGHT_GRAY_WOOL)
    add_fill(fills, f"{label} neck", (x, 8, pz(4)), (x + 1, 9, pz(4)), LIGHT_GRAY_WOOL)
    add_fill(fills, f"{label} head", (x, 9, pz(5)), (x + 1, 9, pz(5)), LIGHT_GRAY_WOOL)
    add_fill(fills, f"{label} ear long w", (x, 10, pz(5)), (x, 11, pz(5)), LIGHT_GRAY_WOOL)
    add_fill(fills, f"{label} ear long e", (x + 1, 10, pz(5)), (x + 1, 11, pz(5)), LIGHT_GRAY_WOOL)
    add_fill(fills, f"{label} mane", (x, 10, pz(4)), (x + 1, 10, pz(4)), M.BLACK_WOOL)
    add_fill(fills, f"{label} tail", (x, 7, pz(-1)), (x, 8, pz(-1)), M.BLACK_WOOL)
    # Cargo: hay-block pannier with a white sack each side, nose bag.
    add_fill(fills, f"{label} pannier hay", (x, 8, min(pz(1), pz(2))), (x + 1, 8, max(pz(1), pz(2))), HAY)
    add_fill(fills, f"{label} sack w", (x, 9, pz(1)), (x, 9, pz(1)), M.WHITE_TERRACOTTA)
    add_fill(fills, f"{label} sack e", (x + 1, 9, pz(2)), (x + 1, 9, pz(2)), M.WHITE_TERRACOTTA)
    add_fill(fills, f"{label} nose bag", (x, 8, pz(5)), (x, 8, pz(5)), M.WOOD)


def _wheelbarrow(fills: list[Fill], label: str, x: int, z: int, d: int) -> None:
    """Single-wheel barrow with barrel cargo (独轮车).

    Anchor (x, z) is the wheel; d = +1 puts the frame and handles behind
    (larger z). Wheel is a 3x3 FENCE ring rolling in the x-y plane.
    """

    def pz(o: int) -> int:
        return z + d * o

    # Wheel: FENCE ring + wood hub.
    add_fill(fills, f"{label} wheel top", (x - 1, 6, pz(0)), (x + 1, 6, pz(0)), M.FENCE)
    add_fill(fills, f"{label} wheel bottom", (x - 1, 4, pz(0)), (x + 1, 4, pz(0)), M.FENCE)
    add_fill(fills, f"{label} wheel west", (x - 1, 5, pz(0)), (x - 1, 5, pz(0)), M.FENCE)
    add_fill(fills, f"{label} wheel east", (x + 1, 5, pz(0)), (x + 1, 5, pz(0)), M.FENCE)
    add_fill(fills, f"{label} wheel hub", (x, 5, pz(0)), (x, 5, pz(0)), M.WOOD)
    # Frame: plank bed, side rails, front board, stand leg.
    blo, bhi = min(pz(1), pz(4)), max(pz(1), pz(4))
    add_fill(fills, f"{label} bed", (x - 1, 5, blo), (x + 1, 5, bhi), M.WOOD)
    add_fill(fills, f"{label} rail west", (x - 1, 6, blo), (x - 1, 6, bhi), M.FENCE)
    add_fill(fills, f"{label} rail east", (x + 1, 6, blo), (x + 1, 6, bhi), M.FENCE)
    add_fill(fills, f"{label} front board", (x, 6, pz(1)), (x, 6, pz(1)), M.WOOD)
    add_fill(fills, f"{label} stand leg", (x, 4, pz(4)), (x, 4, pz(4)), M.FENCE)
    # Handles and cargo.
    hlo, hhi = min(pz(5), pz(7)), max(pz(5), pz(7))
    add_fill(fills, f"{label} handle west", (x - 1, 5, hlo), (x - 1, 5, hhi), LOG_Z)
    add_fill(fills, f"{label} handle east", (x + 1, 5, hlo), (x + 1, 5, hhi), LOG_Z)
    add_fill(fills, f"{label} handle grip west", (x - 1, 5, pz(5)), (x - 1, 5, pz(5)), M.FENCE)
    add_fill(fills, f"{label} handle grip east", (x + 1, 5, pz(5)), (x + 1, 5, pz(5)), M.FENCE)
    add_fill(fills, f"{label} barrel", (x, 6, pz(2)), (x, 6, pz(2)), BARREL)
    add_fill(fills, f"{label} sack", (x, 6, pz(3)), (x, 6, pz(3)), M.WHITE_TERRACOTTA)
    add_fill(fills, f"{label} ground sack", (x + 2, 4, pz(3)), (x + 2, 4, pz(3)), M.WHITE_TERRACOTTA)


def _pedestrian(fills: list[Fill], label: str, x: int, z: int, pole_side: int) -> None:
    """Loaded shoulder-porter under a bamboo hat (挑夫).

    Quartz figure: 1x2 body + head + wide WHITE_TERRACOTTA hat; a LOG
    shoulder pole one row off the body carries WOOD baskets at both ends.
    pole_side: +1 or -1, which side of the figure the pole runs along.
    """
    add_fill(fills, f"{label} body", (x, 4, z), (x, 5, z), M.QUARTZ)
    add_fill(fills, f"{label} head", (x, 6, z), (x, 6, z), M.QUARTZ)
    add_fill(fills, f"{label} hat crown", (x, 7, z), (x, 7, z), M.WHITE_TERRACOTTA)
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        add_fill(fills, f"{label} hat brim {dx},{dz}", (x + dx, 7, z + dz), (x + dx, 7, z + dz), M.WHITE_TERRACOTTA)
    pz2 = z + pole_side
    add_fill(fills, f"{label} shoulder pole", (x - 3, 6, pz2), (x + 3, 6, pz2), LOG_X)
    add_fill(fills, f"{label} basket west", (x - 3, 5, pz2), (x - 3, 5, pz2), M.WOOD)
    add_fill(fills, f"{label} basket east", (x + 3, 5, pz2), (x + 3, 5, pz2), M.WOOD)
    add_fill(fills, f"{label} arm", (x, 6, pz2), (x, 6, pz2), M.QUARTZ)


def _rest_pavilion(fills: list[Fill], label: str) -> None:
    """Wayside rest pavilion: four posts, hay thatch, benches, hitching
    posts (歇脚亭：四柱草顶+条凳+拴马桩)."""
    px1, pz1 = 2796, 2144
    px2, pz2 = 2812, 2160
    add_fill(fills, f"{label} floor", (px1, 4, pz1), (px2, 4, pz2), M.WOOD)
    for cx in (px1 + 2, px2 - 2):
        for cz in (pz1 + 2, pz2 - 2):
            add_fill(fills, f"{label} post {cx},{cz}", (cx, 5, cz), (cx, 9, cz), M.LOG)
    add_fill(fills, f"{label} thatch wide", (px1 - 1, 10, pz1 - 1), (px2 + 1, 10, pz2 + 1), HAY)
    add_fill(fills, f"{label} thatch mid", (px1 + 2, 11, pz1 + 2), (px2 - 2, 11, pz2 - 2), HAY)
    add_fill(fills, f"{label} thatch top", (px1 + 5, 12, pz1 + 5), (px2 - 5, 12, pz2 - 5), HAY)
    add_fill(fills, f"{label} bench west", (px1 + 4, 5, 2150), (px1 + 4, 5, 2154), M.WOOD)
    add_fill(fills, f"{label} bench east", (px2 - 4, 5, 2150), (px2 - 4, 5, 2154), M.WOOD)
    add_fill(fills, f"{label} low table", (2804, 5, 2152), (2805, 5, 2153), M.WOOD)
    add_fill(fills, f"{label} water jar", (px2 - 2, 5, pz1 + 4), (px2 - 2, 5, pz1 + 4), BARREL)
    add_fill(fills, f"{label} hitch post 1", (px1 - 2, 4, 2148), (px1 - 2, 6, 2148), M.FENCE)
    add_fill(fills, f"{label} hitch post 2", (px1 - 2, 4, 2156), (px1 - 2, 6, 2156), M.FENCE)
    add_fill(fills, f"{label} step south", (2802, 4, pz2 + 1), (2806, 4, pz2 + 1), M.SMOOTH)
    add_fill(fills, f"{label} step north", (2802, 4, pz1 - 1), (2806, 4, pz1 - 1), M.SMOOTH)


def _signpost(fills: list[Fill], label: str, x: int, z: int, direction: int) -> None:
    """Directional pointer board (路牌): FENCE post + WOOD board + red
    arrow tip. direction -1 points west (西市), +1 points east (东市)."""
    add_fill(fills, f"{label} post", (x, 4, z), (x, 8, z), M.FENCE)
    add_fill(fills, f"{label} cap", (x, 9, z), (x, 9, z), M.SMOOTH)
    blo, bhi = (x - 3, x - 1) if direction < 0 else (x + 1, x + 3)
    add_fill(fills, f"{label} board", (blo, 6, z), (bhi, 7, z), M.WOOD)
    add_fill(fills, f"{label} board lettering", (blo + direction, 5, z), (bhi + direction, 5, z), M.BLACK_WOOL)
    tip = x + direction * 4
    add_fill(fills, f"{label} arrow tip", (tip, 6, z), (tip, 6, z), M.RED_WOOL)


# ---------------------------------------------------------------------------
# Bounds guard (自查：严禁进入 x 2900..3100 望楼/地灯带).
# ---------------------------------------------------------------------------
def _check_bounds(fills: list[Fill]) -> None:
    """Raise if any fill leaves the two service lanes, the z range, or
    dips below the turf (no digging); implicitly bans x 2900..3100."""
    for f in fills:
        if not f.label.startswith("traffic"):
            continue  # build_all accumulates a shared fill list across modules
        lo_x, hi_x = sorted((f.x1 - BASE_X, f.x2 - BASE_X))
        lo_z, hi_z = sorted((f.z1 - BASE_Z, f.z2 - BASE_Z))
        in_west = WEST_X1 <= lo_x and hi_x <= WEST_X2
        in_east = EAST_X1 <= lo_x and hi_x <= EAST_X2
        if not (in_west or in_east):
            raise ValueError(f"{f.label}: local x {lo_x}..{hi_x} outside service lanes")
        if lo_x <= FORBIDDEN_X2 and hi_x >= FORBIDDEN_X1:
            raise ValueError(f"{f.label}: enters forbidden watchtower band x 2900..3100")
        if lo_z < LANE_Z1 or hi_z > LANE_Z2:
            raise ValueError(f"{f.label}: z {lo_z}..{hi_z} outside lane range")
        if min(f.y1, f.y2) < GROUND_Y:
            raise ValueError(f"{f.label}: digs below turf (y < {GROUND_Y})")


# ---------------------------------------------------------------------------
# Main builder.
# ---------------------------------------------------------------------------
def build_street_traffic_3d(fills: list[Fill]) -> None:
    """Zhuque Avenue street traffic overlay - add-only, label 'traffic '."""

    # ------------------------------------------------------------------
    # 1. Freight oxcarts x2 (货运牛车) - signature pieces, one per lane.
    #    West cart rolls north with grain; east cart rolls south with silk.
    # ------------------------------------------------------------------
    _oxcart(fills, "traffic oxcart west", 2832, 1180, d=-1, cargo="grain")
    _oxcart(fills, "traffic oxcart east", 3170, 2050, d=+1, cargo="silk")

    # ------------------------------------------------------------------
    # 2. Blue-canopy official sedan x1 (青帷官轿) on the east lane.
    # ------------------------------------------------------------------
    _sedan(fills, "traffic sedan", 3124, 1790, d=+1)

    # ------------------------------------------------------------------
    # 3. Pack-donkey train x3 (驮驴驴队) roped nose-to-tail towards the
    #    West Market along the west lane's avenue edge.
    # ------------------------------------------------------------------
    _donkey(fills, "traffic donkey 1", 2876, 1268, d=-1)
    _donkey(fills, "traffic donkey 2", 2876, 1292, d=-1)
    _donkey(fills, "traffic donkey 3", 2876, 1316, d=-1)
    add_fill(fills, "traffic donkey lead rope 1", (2876, 9, 1264), (2876, 9, 1291), M.IRON_BARS)
    add_fill(fills, "traffic donkey lead rope 2", (2876, 9, 1288), (2876, 9, 1315), M.IRON_BARS)

    # ------------------------------------------------------------------
    # 4. Wheelbarrows x2 (独轮车), parked at the ward edge of each lane.
    # ------------------------------------------------------------------
    _wheelbarrow(fills, "traffic barrow west", 2790, 1700, d=+1)
    _wheelbarrow(fills, "traffic barrow east", 3198, 2450, d=+1)

    # ------------------------------------------------------------------
    # 5. Shoulder-porters x4 (挑夫行人), two per lane.
    # ------------------------------------------------------------------
    _pedestrian(fills, "traffic porter 1", 2842, 1420, pole_side=+1)
    _pedestrian(fills, "traffic porter 2", 2808, 1560, pole_side=-1)
    _pedestrian(fills, "traffic porter 3", 3132, 2250, pole_side=+1)
    _pedestrian(fills, "traffic porter 4", 3180, 2620, pole_side=-1)

    # ------------------------------------------------------------------
    # 6. Roadside rest pavilion x1 (歇脚亭) on the west lane.
    # ------------------------------------------------------------------
    _rest_pavilion(fills, "traffic pavilion")

    # ------------------------------------------------------------------
    # 7. Directional signposts x2 (路牌): 西市 <- on the west lane,
    #    东市 -> on the east lane.
    # ------------------------------------------------------------------
    _signpost(fills, "traffic sign west", 2886, 1900, direction=-1)
    _signpost(fills, "traffic sign east", 3116, 2900, direction=+1)

    # Hard self-check: nothing may leave the lanes or touch x 2900..3100.
    _check_bounds(fills)


def main() -> None:
    run_builder(build_street_traffic_3d, "street_traffic_3d")


if __name__ == "__main__":
    main()
