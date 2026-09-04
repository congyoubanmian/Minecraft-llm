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
    run_builder,
)


"""
Crossroad Pailou Group (十字街口牌楼群) - three four-column three-bay
timber memorial arches (四柱三间跨街牌楼) standing across the market
cross-streets of Tang Chang'an, each naming its ward or avenue on a
gilded hanging plaque.

Location in Chang'an city local coordinates (verified collision-free
against every existing module fill):
    西市牌楼 West Market pailou:  centre (1300, 2608), spanning the
        inner cross street of market block (1240, 2540); placed 8 blocks
        south of the block-centre well (1294..1306, 2594..2606) and
        clear of the shop eave slabs at z 2613 and the flag pavilion
        旗亭 (xishi_qiting_3d, x 1234..1266 / z 2530..2570) and the
        Sogdian tavern (x >= 1312, z 2444..2498).
    东市牌楼 East Market pailou:  centre (4780, 2608), same block-
        relative position in market block (4720, 2540).
    朱雀街牌楼 Zhuque Avenue pailou: centre (3000, 3150) at the
        Zhuque Avenue / south ward-lane junction, spanning the imperial
        roadway on a raised andesite plinth deck (y 5) that bridges the
        imperial median (road_paving median/curbs x 2992..3008 at
        y 3..4); ground piers at x 2988..2990 / 3010..3012 keep clear of
        the curbs, the street_facilities median lamps (nearest at
        z 3179) and the wanglou e4 yard (x >= 3130). Nothing is dug
        below ground, so the underground_drain_3d sewer (y <= -2) and
        the drainage_ditches channels (x 2962..2965 / 3035..3038) are
        untouched.

Distinctive features (identical form, different plaques and paints):
    - Four dark-oak skyline columns (冲天柱, up to y 12 / y 15 on the
      avenue plinth) on smooth-stone plinths with drum bases (抱鼓石),
      double lintels (额枋, wood + deepslate) with sparrow braces (雀替)
      and gilded beam-end tips
    - Painted floating panels (花板): four short red/gold wool strips
      woven block by block between the lintels
    - Gilded hanging plaque in the central bay (明间悬匾, 9-wide clear
      passage), framed in the site colour, readable from both faces
    - Cantilevered column-top brackets, an out-eave plank deck, a glazed
      tile roof (陶瓦顶, dark prismarine) with a deepslate ridge and
      gilded chi-wen end hooks
    - One sea-lantern with a red wool shade on every column top
      (柱头彩灯) plus red/gold roof finials
    - Six-block white ward-wall stubs with dark caps and end posts on
      both flanks (坊墙残段, marking the market-gate line)
    - Two trade banners (市招: tea / wine / medicine colours) hung from
      fence arms outside the side bays, a quartz-and-gold stone
      shigandang (石敢当) at the foot, and four smooth-stone drain
      cover strips along the street face (水沟盖板, echoing
      drainage_ditches without digging)
"""


def _span_fill(
    fills: list[Fill],
    label: str,
    cx: int,
    cz: int,
    facing: str,
    u1: int,
    v1: int,
    u2: int,
    v2: int,
    y1: int,
    y2: int,
    block: str,
) -> None:
    """Add one fill in pailou-local (u, v) space.

    u runs along the span (the column line), v across it (depth).
    facing 'x': the arch spans east-west and is crossed walking north-
    south; facing 'z' mirrors it. u1..u2 / v1..v2 may be given in any
    order; add_fill sorts the axes.
    """
    if facing == "x":
        add_fill(fills, label, (cx + u1, y1, cz + v1), (cx + u2, y2, cz + v2), block)
    else:
        add_fill(fills, label, (cx + v1, y1, cz + u1), (cx + v2, y2, cz + u2), block)


def _pailou(
    fills: list[Fill],
    label: str,
    cx: int,
    cz: int,
    facing: str,
    plaque_color: str,
    *,
    base_y: int = 3,
    ground_y: int | None = None,
    wall_gap: int = 0,
    banner_colors: tuple[str, str] = (M.GREEN_WOOL, M.RED_WOOL),
    plinth: bool = False,
) -> None:
    """One four-column three-bay street pailou (四柱三间跨街牌楼).

    base_y  : first column layer (street surface is one block lower).
    ground_y: yard level for the flanking walls / covers / stele
              (defaults to base_y; the avenue pailou stands on a plinth
              but its flanks stay on the road surface).
    wall_gap: extra offset of the ward-wall stubs (1 on the avenue so
              they clear the plinth ground piers).
    plinth  : raised andesite deck for the imperial-way crossing.
    """
    gy = base_y if ground_y is None else ground_y
    top = base_y + 9        # skyline column top (冲天柱头)
    beam_y = base_y + 6     # lower lintel 额枋
    beam2_y = beam_y + 1    # upper lintel
    panel_y = beam2_y + 1   # painted panels 花板
    deck_y = top + 1        # out-eave plank deck
    tile_y = deck_y + 1     # glazed tile roof 陶瓦顶
    ridge_y = tile_y + 1    # ridge 正脊

    # ------------------------------------------------------------------
    # 0. Optional raised plinth (Zhuque Avenue imperial median crossing).
    # ------------------------------------------------------------------
    if plinth:
        _span_fill(fills, f"pailou {label} plinth deck", cx, cz, facing, -12, -3, 12, 4, base_y - 1, base_y - 1, M.ANDESITE)
        _span_fill(fills, f"pailou {label} plinth bedding", cx, cz, facing, -4, -3, 4, 4, base_y - 2, base_y - 2, M.ANDESITE)
        _span_fill(fills, f"pailou {label} plinth pier w", cx, cz, facing, -12, -3, -10, 4, gy, base_y - 2, M.ANDESITE)
        _span_fill(fills, f"pailou {label} plinth pier e", cx, cz, facing, 10, -3, 12, 4, gy, base_y - 2, M.ANDESITE)

    # ------------------------------------------------------------------
    # 1. Cantilever pads first, then the four skyline LOG columns,
    #    plinth blocks and drum bases (抱鼓石).
    # ------------------------------------------------------------------
    bays = [(-11, -8), (-6, -3), (3, 6), (8, 11)]     # pier/bracket footprints
    cols = [(-10, -9), (-5, -4), (4, 5), (9, 10)]     # 2x2 column footprints
    for i, (u1, u2) in enumerate(bays):
        _span_fill(fills, f"pailou {label} bracket {i}", cx, cz, facing, u1, -1, u2, 2, top, top, M.WOOD)
    for i, (u1, u2) in enumerate(cols):
        _span_fill(fills, f"pailou {label} col {i} lower", cx, cz, facing, u1, 0, u2, 1, base_y, base_y + 4, M.LOG)
        _span_fill(fills, f"pailou {label} col {i} upper", cx, cz, facing, u1, 0, u2, 1, base_y + 5, top, M.LOG)
    for i, (u1, u2) in enumerate(bays):
        _span_fill(fills, f"pailou {label} stone plinth {i}", cx, cz, facing, u1, -1, u2, 2, base_y, base_y, M.SMOOTH)
    for i, (u1, u2) in enumerate(cols):
        _span_fill(fills, f"pailou {label} drum {i}", cx, cz, facing, u1, 0, u2, 1, base_y + 1, base_y + 2, M.SMOOTH)

    # ------------------------------------------------------------------
    # 2. Double lintels (WOOD + DARK), gilded beam ends, sparrow braces
    #    (雀替) and sill blocks (地栿) closing the side bays.
    # ------------------------------------------------------------------
    _span_fill(fills, f"pailou {label} lintel lower", cx, cz, facing, -10, 0, 10, 1, beam_y, beam_y, M.WOOD)
    _span_fill(fills, f"pailou {label} lintel upper", cx, cz, facing, -10, 0, 10, 1, beam2_y, beam2_y, M.DARK)
    for sgn, name in ((-1, "w"), (1, "e")):
        u1, u2 = (11, 13) if sgn > 0 else (-13, -11)
        _span_fill(fills, f"pailou {label} lintel end {name}", cx, cz, facing, u1, 0, u2, 1, beam_y, beam2_y, M.WOOD)
        tip = 14 * sgn
        _span_fill(fills, f"pailou {label} lintel tip {name}", cx, cz, facing, tip, 0, tip, 1, beam_y, beam2_y, M.GOLD)
    for i, (u1, u2) in enumerate(((-8, -6), (-3, -1), (1, 3), (6, 8))):
        _span_fill(fills, f"pailou {label} que ti {i}", cx, cz, facing, u1, 0, u2, 1, beam_y - 1, beam_y - 1, M.WOOD)
    for sgn, name in ((-1, "w"), (1, "e")):
        _span_fill(fills, f"pailou {label} di fu {name}", cx, cz, facing, 7 * sgn, 0, 7 * sgn, 1, base_y, base_y, M.WOOD)

    # ------------------------------------------------------------------
    # 3. Painted floating panels (花板): four short RED/GOLD strips.
    # ------------------------------------------------------------------
    for i, (u1, u2) in enumerate(((-8, -6), (-3, -1), (1, 3), (6, 8))):
        for j, u in enumerate(range(u1, u2 + 1)):
            wool = M.RED_WOOL if (i + j) % 2 == 0 else M.GOLD
            _span_fill(fills, f"pailou {label} hua ban {i}.{j}", cx, cz, facing, u, 0, u, 1, panel_y, panel_y, wool)

    # ------------------------------------------------------------------
    # 4. Gilded plaque in the central bay, framed in the site colour,
    #    mounted proud on both faces of the lintel plane.
    # ------------------------------------------------------------------
    for sgn, name in ((1, "front"), (-1, "back")):
        v = 2 * sgn
        _span_fill(fills, f"pailou {label} plaque {name}", cx, cz, facing, -2, v, 2, v, beam_y, beam2_y, M.GOLD)
        _span_fill(fills, f"pailou {label} plaque {name} frame top", cx, cz, facing, -3, v, 3, v, panel_y, panel_y, plaque_color)
        _span_fill(fills, f"pailou {label} plaque {name} frame bottom", cx, cz, facing, -3, v, 3, v, beam_y - 1, beam_y - 1, plaque_color)
        _span_fill(fills, f"pailou {label} plaque {name} frame w", cx, cz, facing, -3, v, -3, v, beam_y, beam2_y, plaque_color)
        _span_fill(fills, f"pailou {label} plaque {name} frame e", cx, cz, facing, 3, v, 3, v, beam_y, beam2_y, plaque_color)

    # ------------------------------------------------------------------
    # 5. Out-eave deck, glazed tile roof (陶瓦顶), ridge and chi-wen.
    # ------------------------------------------------------------------
    _span_fill(fills, f"pailou {label} eave deck", cx, cz, facing, -12, -2, 12, 3, deck_y, deck_y, M.WOOD)
    _span_fill(fills, f"pailou {label} tile roof", cx, cz, facing, -13, -3, 13, 4, tile_y, tile_y, M.ROOF_GREEN)
    _span_fill(fills, f"pailou {label} ridge", cx, cz, facing, -10, 0, 10, 1, ridge_y, ridge_y, M.DARK)
    for sgn, name in ((-1, "w"), (1, "e")):
        u1, u2 = (11, 12) if sgn > 0 else (-12, -11)
        _span_fill(fills, f"pailou {label} chi wen {name}", cx, cz, facing, u1, 0, u2, 1, ridge_y, ridge_y + 1, M.GOLD_ACCENT)

    # ------------------------------------------------------------------
    # 6. Column-top lanterns (柱头彩灯): sea lantern + red wool shade.
    # ------------------------------------------------------------------
    for i, (u1, _u2) in enumerate(cols):
        _span_fill(fills, f"pailou {label} lamp {i}", cx, cz, facing, u1, 3, u1, 3, ridge_y, ridge_y, M.SEA_LANTERN)
        _span_fill(fills, f"pailou {label} lamp shade {i}", cx, cz, facing, u1, 3, u1, 3, ridge_y + 1, ridge_y + 1, M.RED_WOOL)

    # ------------------------------------------------------------------
    # 7. Ward-wall stubs (坊墙残段): 6-block white wall + dark cap +
    #    end post on each flank, marking the market-gate line.
    # ------------------------------------------------------------------
    wu1 = 12 + wall_gap
    wu2 = wu1 + 5
    for sgn, name in ((-1, "w"), (1, "e")):
        a, b = (wu1, wu2) if sgn > 0 else (-wu2, -wu1)
        _span_fill(fills, f"pailou {label} ward wall {name}", cx, cz, facing, a, 0, b, 1, gy, gy + 5, M.WHITE)
        _span_fill(fills, f"pailou {label} ward wall {name} cap", cx, cz, facing, a, 0, b, 1, gy + 6, gy + 6, M.DARK)
        post = wu2 * sgn
        _span_fill(fills, f"pailou {label} ward wall {name} post", cx, cz, facing, post, 0, post, 1, gy, gy + 7, M.LOG)

    # ------------------------------------------------------------------
    # 8. Trade banners (市招) on fence arms outside the side bays.
    # ------------------------------------------------------------------
    for i, (uu, wool) in enumerate(((-9, banner_colors[0]), (7, banner_colors[1]))):
        _span_fill(fills, f"pailou {label} banner {i} arm", cx, cz, facing, uu, -1, uu + 1, -1, beam_y - 1, beam_y - 1, M.FENCE)
        _span_fill(fills, f"pailou {label} banner {i} cloth", cx, cz, facing, uu + 1, -1, uu + 1, -1, base_y + 3, beam_y - 2, wool)

    # ------------------------------------------------------------------
    # 9. Stone shigandang (石敢当): quartz stele with a gold cap.
    # ------------------------------------------------------------------
    su = -(15 + wall_gap)
    _span_fill(fills, f"pailou {label} shigandang base", cx, cz, facing, su, 4, su, 4, gy, gy, M.SMOOTH)
    _span_fill(fills, f"pailou {label} shigandang stele", cx, cz, facing, su, 4, su, 4, gy + 1, gy + 2, M.QUARTZ)
    _span_fill(fills, f"pailou {label} shigandang cap", cx, cz, facing, su, 4, su, 4, gy + 3, gy + 3, M.GOLD)

    # ------------------------------------------------------------------
    # 10. Drain cover strips (水沟盖板) along both street faces,
    #     laid on the surface only - no ditch is dug.
    # ------------------------------------------------------------------
    for sgn, name in ((-1, "w"), (1, "e")):
        for j, (v1, v2) in enumerate(((-8, -1), (2, 9))):
            _span_fill(
                fills, f"pailou {label} drain cover {name}{j}",
                cx, cz, facing, 13 * sgn, v1, 13 * sgn, v2, gy, gy, M.SMOOTH,
            )


def build_jieshi_pailou_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. West Market inner cross street (西市内十字街口), block (1240,2540).
    #    Kept south of the central well and clear of the flag pavilion.
    # ------------------------------------------------------------------
    _pailou(fills, "xishi", 1300, 2608, "x", M.RED_WOOL, banner_colors=(M.GREEN_WOOL, M.RED_WOOL))

    # ------------------------------------------------------------------
    # 2. East Market inner cross street (东市内十字街口), block (4720,2540).
    # ------------------------------------------------------------------
    _pailou(fills, "dongshi", 4780, 2608, "x", M.BLUE_WOOL, banner_colors=(M.BLUE_WOOL, M.YELLOW_WOOL))

    # ------------------------------------------------------------------
    # 3. Zhuque Avenue / south ward-lane junction (朱雀大街与南坊巷交口).
    #    Raised andesite plinth bridges the imperial median; flanks stay
    #    at road level and nothing is excavated (sewer lies at y <= -2).
    # ------------------------------------------------------------------
    _pailou(
        fills, "zhuque", 3000, 3150, "x", M.YELLOW_WOOL,
        base_y=6, ground_y=3, wall_gap=1, plinth=True,
        banner_colors=(M.RED_WOOL, M.WHITE_WOOL),
    )


def main() -> None:
    run_builder(build_jieshi_pailou_3d, "jieshi_pailou_3d")


if __name__ == "__main__":
    main()
