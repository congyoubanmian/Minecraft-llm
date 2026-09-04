from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    Fill,
    Materials as M,
    add_balustrade,
    add_dougong_brackets,
    add_dougong_cluster,
    add_door_studs,
    add_fill,
    run_builder,
)


"""
Palace Facade Detail 3D (大明宫四大殿 立面细节深化叠加) - detail-enrichment
overlay pass that dresses the four already-built Daming Palace halls.

深度化对象 (deepened targets, coordinates read back from their source modules):
    - 含元殿 Hanyuan Dian      (palace_hanyuan_dian.py + palace_hanyuan_3d.py)
      footprint x 2660..3340, z 5180..5480, terrace_top=9, eave dougong_y=58,
      main door air x 2984..3016 / y 10..23 / z 5177..5182 behind the gold
      frame whose south face is z 5175; terrace tier-3 top y=8 from z 5136.
    - 麟德殿 Linde Hall        (palace_linde_3d.py)
      front hall x 2150..2450, z 5350..5450, walls y 10..24, south door air
      x 2294..2306 / y 11..18 / z 5350..5351; tier-3 platform top y=9;
      tier edges 2090..2510 / 5330..5670.
    - 宣政殿 Xuanzheng Dian    (palace_xuanzheng_dian.py)
      footprint x 2740..3260, z 4880..5080, terrace_top=8, eave dougong_y=45,
      main door air x 2988..3012 / y 9..20 behind gold frame face z 4875.
    - 紫宸殿 Zichen Dian       (palace_zichen_dian.py)
      footprint x 2360..2620, z 5200..5480, terrace_top=6, hall y 6..33.
      The source module has NO door, so the main door is derived on the south
      wall face (z 5200) centred on mid_x=2490.

Distinctive features (English):
    - Dense spacing-8 dougong bracket bands (add_dougong_brackets) across the
      central bays of every hall's south principal facade, plus 3-tier
      add_dougong_cluster stacks at all four eave corners of each hall.
    - 5x7 gilded door-stud arrays (add_door_studs) on dark timber door leaves,
      flanked by paired pushou knockers (2x2 gold ring with inlaid iron bars
      and a gold beast-head block) and smooth-stone drum stones (抱鼓石).
    - A carved "dragon imperial ramp" (龙纹御路) of deepslate treads with three
      gold wave lines and quartz cloud dots along the head of the Hanyuan
      longwei dao approach.
    - Gold 5x2 plaques with dark-oak couplets (3 quartz glyph dots each) above
      every main door.
    - Balustrade posts (add_balustrade, post_every=8, white-terracotta lotus
      heads) on the Linde tier-3 grand-stair head and around the Zichen
      front moon platform (月台).

Budget note: full-perimeter spacing-8 dougong rings on all four halls would
need ~900 fills by themselves (Hanyuan's ring alone is ~256), which breaks the
250-450 fill target; the dense bands are therefore focused on the principal
south facades (the ceremonial faces) with corner clusters covering all four
facade corners, on top of the sparser rows the base modules already built.
Nothing is cleared: this pass only adds solid blocks, never AIR.
"""

# Dense dougong band spacing (denser than the base modules' 26-30).
BAND_SPACING = 8
# Balustrade post spacing.
POST_EVERY = 8


def _front_dougong_band(
    fills: list[Fill],
    name: str,
    cx: int,
    line_z: int,
    y: int,
) -> None:
    """Dense spacing-8 bracket band across the central bays of the south eave.

    line_z is the bracket line just outside the facade (wall face minus the
    frame projection); the band hangs directly under the main roof overhang.
    """
    add_dougong_brackets(
        fills, f"palaceface {name} eave dougong",
        cx - 22, line_z, cx + 22, line_z, y, spacing=BAND_SPACING,
    )


def _corner_clusters(
    fills: list[Fill],
    name: str,
    x1: int, z1: int,
    x2: int, z2: int,
    y: int,
) -> None:
    """3-tier dougong clusters at the four eave corners of one hall."""
    for cx, cz, side in ((x1, z1, "nw"), (x2, z1, "ne"), (x1, z2, "sw"), (x2, z2, "se")):
        add_dougong_cluster(fills, f"palaceface {name} corner dougong {side}", cx, cz, y, tiers=3)


def _main_door_suite(
    fills: list[Fill],
    name: str,
    u1: int, u2: int,
    y1: int, y2: int,
    leaf_z: int,
    ground_y: int,
    stud_u1: int, stud_u2: int,
    stud_y1: int, stud_y2: int,
    stud_step: int,
    push_u1: int, push_u2: int,
    push_y1: int, push_y2: int,
    plaque_y1: int, plaque_y2: int,
    plaque_z: int,
    couple_w: int, couple_e: int,
    couple_y1: int, couple_y2: int,
) -> None:
    """Full door dressing on one south-facing main entrance.

    leaf_z is the door-leaf plane one block proud of the gold frame face
    (derived from each source module's door/frame add_fill coordinates);
    zp = leaf_z - 1 is the stud/pushou plane proud of the leaf.
    """
    zp = leaf_z - 1
    # Dark timber door leaf covering the entrance face.
    add_fill(fills, f"palaceface {name} door leaf", (u1, y1, leaf_z), (u2, y2, leaf_z), M.DARK)
    # 5-column x 7-row gold stud array on the leaf face (门钉金阵列).
    add_door_studs(
        fills, f"palaceface {name} door studs", "z", zp,
        stud_u1, stud_u2, stud_y1, stud_y2, M.GOLD, stud_step,
    )
    # Paired pushou knockers (铺首): gold ring plate, inlaid iron bars, beast head.
    for i, pu in enumerate((push_u1, push_u2)):
        add_fill(fills, f"palaceface {name} pushou {i} ring", (pu, push_y1, zp), (pu + 1, push_y2, zp), M.GOLD)
        add_fill(fills, f"palaceface {name} pushou {i} bars", (pu, push_y1, zp - 1), (pu + 1, push_y2, zp - 1), M.IRON_BARS)
        add_fill(fills, f"palaceface {name} pushou {i} head", (pu, push_y1 - 1, zp), (pu + 1, push_y1 - 1, zp), M.GOLD)
    # Paired drum stones (抱鼓石) standing on the terrace beside the portal.
    for i, bx in enumerate((u1 - 4, u2 + 4)):
        add_fill(fills, f"palaceface {name} baogu {i} base", (bx - 1, ground_y, leaf_z), (bx + 1, ground_y, leaf_z), M.DARK)
        add_fill(fills, f"palaceface {name} baogu {i} drum", (bx, ground_y, leaf_z), (bx, ground_y + 1, leaf_z), M.SMOOTH)
        add_fill(fills, f"palaceface {name} baogu {i} face", (bx, ground_y, leaf_z - 1), (bx, ground_y + 1, leaf_z - 1), M.QUARTZ)
    # Gold plaque (5x2) centred above the door.
    mid = (u1 + u2) // 2
    add_fill(fills, f"palaceface {name} plaque", (mid - 2, plaque_y1, plaque_z), (mid + 2, plaque_y2, plaque_z), M.GOLD)
    # Dark-oak couplets with three quartz glyph dots each.
    for i, cx in enumerate((couple_w, couple_e)):
        add_fill(fills, f"palaceface {name} couplet {i}", (cx, couple_y1, leaf_z), (cx, couple_y2, leaf_z), M.WOOD)
        for dy in (1, 3, 5):
            add_fill(
                fills, f"palaceface {name} couplet {i} glyph {dy}",
                (cx, couple_y1 + dy, leaf_z - 1), (cx, couple_y1 + dy, leaf_z - 1), M.QUARTZ,
            )


def _dragon_road(fills: list[Fill]) -> None:
    """Carved dragon imperial ramp (龙纹御路) on the longwei dao head.

    Descends the Hanyuan terrace tier faces on the door axis (mid_x=3000):
    tier-3 top y=8 at z>=5136, tier-2 top y=6 from z 5128, tier-1 top y=3
    from z 5120. Each tread is a 3x1x2 deepslate slab carrying three gold
    wave lines (outer lines straight, centre line offset one step = wave)
    plus quartz cloud dots every third tread.
    """
    name = "palaceface hanyuan dragon road"
    # Landing apron on the terrace top at the head of the slope.
    add_fill(fills, f"{name} apron", (2999, 8, 5138), (3001, 8, 5141), M.DARK)
    add_fill(fills, f"{name} apron cloud", (3000, 8, 5139), (3000, 8, 5140), M.QUARTZ)
    for k in range(6):
        y = 8 - k          # 8..3, one drop per tread
        z = 5136 - 2 * k   # treads march south down the tier faces
        add_fill(fills, f"{name} tread {k}", (2999, y, z), (3001, y, z + 1), M.DARK)
        add_fill(fills, f"{name} wave w {k}", (2999, y, z), (2999, y, z), M.GOLD)
        add_fill(fills, f"{name} wave c {k}", (3000, y, z + 1), (3000, y, z + 1), M.GOLD)
        add_fill(fills, f"{name} wave e {k}", (3001, y, z), (3001, y, z), M.GOLD)
        if k % 3 == 0:
            add_fill(fills, f"{name} cloud {k}", (3000, y, z), (3000, y, z), M.QUARTZ)


def build_palace_facade_detail_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. 含元殿 Hanyuan Dian (palace_hanyuan_dian.py + palace_hanyuan_3d.py)
    #    Door air (2984..3016, 10..23, 5177..5182); gold frame face z 5175;
    #    eave line DOUGONG_Y = 58; terrace tier-3 top y 8 from z 5136.
    # ------------------------------------------------------------------
    _front_dougong_band(fills, "hanyuan", 3000, 5174, 58)
    _corner_clusters(fills, "hanyuan", 2654, 5174, 3346, 5486, 58)
    _main_door_suite(
        fills, "hanyuan",
        u1=2984, u2=3016, y1=10, y2=23, leaf_z=5174, ground_y=9,
        stud_u1=2996, stud_u2=3004, stud_y1=11, stud_y2=23, stud_step=2,
        push_u1=2986, push_u2=3013, push_y1=15, push_y2=16,
        plaque_y1=24, plaque_y2=25, plaque_z=5174,
        couple_w=2983, couple_e=3017, couple_y1=12, couple_y2=17,
    )
    _dragon_road(fills)

    # ------------------------------------------------------------------
    # 2. 麟德殿 Linde Hall (palace_linde_3d.py, front hall of the triple hall)
    #    Front hall door air (2294..2306, 11..18, 5350..5351); roof y 25 over
    #    (2144,5344)-(2456,5456); tier-3 platform top y 9; tier-3 stair head
    #    at z 5330 gets the balustrade posts (tier edges already carry the
    #    base module's quartz rails).
    # ------------------------------------------------------------------
    _front_dougong_band(fills, "linde", 2300, 5344, 23)
    _corner_clusters(fills, "linde", 2144, 5344, 2456, 5456, 21)
    _main_door_suite(
        fills, "linde",
        u1=2294, u2=2306, y1=11, y2=18, leaf_z=5349, ground_y=10,
        stud_u1=2298, stud_u2=2302, stud_y1=11, stud_y2=17, stud_step=1,
        push_u1=2294, push_u2=2305, push_y1=14, push_y2=15,
        plaque_y1=19, plaque_y2=20, plaque_z=5349,
        couple_w=2292, couple_e=2308, couple_y1=11, couple_y2=16,
    )
    add_balustrade(
        fills, "palaceface linde terrace balustrade",
        2274, 5330, 2326, 5338, 10,
        post_block=M.QUARTZ, head_block=M.WHITE_TERRACOTTA, post_every=POST_EVERY,
    )

    # ------------------------------------------------------------------
    # 3. 宣政殿 Xuanzheng Dian (palace_xuanzheng_dian.py)
    #    Door air (2988..3012, 9..20, 4877..4882); gold frame face z 4875
    #    (top y 22), so the plaque mounts on the wall face z 4879 above it;
    #    eave line DOUGONG_Y = 45.
    # ------------------------------------------------------------------
    _front_dougong_band(fills, "xuanzheng", 3000, 4874, 45)
    _corner_clusters(fills, "xuanzheng", 2734, 4874, 3266, 5086, 42)
    _main_door_suite(
        fills, "xuanzheng",
        u1=2988, u2=3012, y1=9, y2=22, leaf_z=4874, ground_y=8,
        stud_u1=2996, stud_u2=3004, stud_y1=9, stud_y2=21, stud_step=2,
        push_u1=2990, push_u2=3009, push_y1=14, push_y2=15,
        plaque_y1=23, plaque_y2=24, plaque_z=4879,
        couple_w=2987, couple_e=3013, couple_y1=11, couple_y2=16,
    )

    # ------------------------------------------------------------------
    # 4. 紫宸殿 Zichen Dian (palace_zichen_dian.py)
    #    The source builds no door, so the main door is derived on the south
    #    wall face z 5200 centred on mid_x 2490: leaf x 2478..2502, y 7..19.
    #    The tier-2 front apron (top y 5, z 5186..5199) acts as the moon
    #    platform (月台) and is ringed with balustrade posts.
    # ------------------------------------------------------------------
    _front_dougong_band(fills, "zichen", 2490, 5194, 32)
    _corner_clusters(fills, "zichen", 2354, 5194, 2626, 5486, 30)
    _main_door_suite(
        fills, "zichen",
        u1=2478, u2=2502, y1=7, y2=19, leaf_z=5199, ground_y=6,
        stud_u1=2486, stud_u2=2494, stud_y1=7, stud_y2=19, stud_step=2,
        push_u1=2480, push_u2=2499, push_y1=12, push_y2=13,
        plaque_y1=20, plaque_y2=21, plaque_z=5199,
        couple_w=2477, couple_e=2503, couple_y1=8, couple_y2=13,
    )
    add_balustrade(
        fills, "palaceface zichen yuetai balustrade",
        2462, 5186, 2518, 5194, 6,
        post_block=M.QUARTZ, head_block=M.WHITE_TERRACOTTA, post_every=POST_EVERY,
    )


def main() -> None:
    run_builder(build_palace_facade_detail_3d, "palace_facade_detail_3d")


if __name__ == "__main__":
    main()
