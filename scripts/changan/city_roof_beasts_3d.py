from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    Fill,
    Materials as M,
    add_fill,
    add_roof_beasts,
    run_builder,
)
from scripts.changan.roof_color_zoning_3d import (
    GUOZIJIAN_RIDGES,
    MARKET_SAMPLE_SHOPS,
    MARKET_SHOP_QUADRANTS,
    OFFICES,
    TEMPLE_SIDE_RIDGES,
    WARD_MANSION_QUADRANTS,
    WARD_SAMPLE_MANSIONS,
)


"""
City Roof Beasts 3D (唐长安城全城脊兽扩展叠加层) - city-wide detail
enrichment overlay that extends the Daming Palace ridge walking beasts
(palace_roof_detail_3d.py) to the temples, government offices, market
shops and ward mansions of the whole city, so every rooftop skyline
gets its Tang-style undulation.

中文名：唐长安城全城脊兽扩展叠加层（佛寺·官署·市铺·宅邸 正脊走兽 + 翼角套兽）
英文名：Chang'an city-wide roof-beast extension overlay (main-ridge
walking beasts plus wing-corner taoshou caps on temples, offices,
market shops and ward mansions).

This module ONLY ADDS statues standing on existing ridge caps and eave
slabs; it never issues an AIR fill and never rebuilds a roof volume
(只添加不清空).

Coordinate derivation (all local city coordinates).  Every target roof
was built with lib.add_ridge_roof (none of the targets uses
add_hip_roof), whose geometry is

    steps      = max(3, layers * 2)
    ridge_y    = y_call + steps       # ridge cap occupies ridge_y..ridge_y+1
    ridge span = z1+4 .. z2-4 at cx-1..cx+1 (axis z)
    finials    = ridge_y+2 .. ridge_y+5 at each ridge end (z rz-1..rz+1)

so the first free block above the ridge - where a walking beast stands -
is ridge_y + 2 = y_call + max(3, layers * 2) + 2.  The west/east eave
slabs of an axis-z ridge roof sit at y_call-1 spanning (x1-2..x1+2 and
x2-2..x2+2, z1-3..z2+3), so each wing-corner taoshou cap (1x1x2) stands
at y_call on a slab corner (x1-2 / x2+2, z1-3 / z2+3).

Footprints below were replayed from the source modules (temple_daci.py,
temple_qinglong.py, temple_daxingshan.py, academy_guozijian.py,
government_offices.py, market_block.py with base_y=2, ward_block.py with
base_y=1) and are cross-checked at build time against the ridge tables
imported from roof_color_zoning_3d.py (GUOZIJIAN_RIDGES,
TEMPLE_SIDE_RIDGES, OFFICES), reusing its coordinate system verbatim.

五类脊兽分布表 (five beast categories):

    | 类别 category | 正脊 ridges | 每脊走兽 | 走兽用色 beasts | 套兽 taoshou | 走兽 |
    |---------------|-------------|----------|-----------------|--------------|------|
    | 佛寺 temple   | 13 = 5 main halls + 8 side halls of 大慈恩寺/青龙寺/大兴善寺 | 3 | ROOF_BLUE plinth, gold / gilded-blackstone bodies | gold | 39 |
    | 官署 office   | 10 = 6 guozijian ridges + 4 office main halls | 3 | yellow-glazed / gilded-blackstone bodies | yellow glazed | 30 |
    | 市铺 market   | 12 representative West/East Market shops | 2 | deepslate / gilded-blackstone bodies | deepslate | 24 |
    | 宅邸 ward     | 12 representative ward mansions | 2 | andesite / dark-oak bodies | andesite | 24 |
    | 翼角套兽      | all 47 ridges x 4 eave corners | - | - | per category | 188 caps |

    Totals: 117 walking beasts (234 fills) + 188 taoshou caps
    = 422 fills, all labelled with the "citybeast " prefix.

Clearance: the closest palace beast/cap of palace_roof_detail_3d.py
(Xuanzheng taoshou at x 2692 / z 4853) sits more than 400 blocks away
from the nearest city beast (honglu_si hall at x 2600 / z 4373..4437) -
far beyond the required 4-block separation; no palace placement is
touched.

Ridges shorter than the 4-block-inset row (the five-block gate ridges)
get their three beasts abreast across the 3-wide ridge cap instead of
collapsed onto one spot.
"""


# ---------------------------------------------------------------------------
# Category palettes (材质随类别).
# ---------------------------------------------------------------------------
TEMPLE_BEAST_BASE = M.ROOF_BLUE  # 青脊底座: same colour family as the blue temple roofs
TEMPLE_BEAST_PALETTE = [M.GOLD, M.GOLD_ACCENT]  # 佛寺金兽 (blue roof topped with gold)
TEMPLE_TAOSHOU = M.GOLD
OFFICE_BEAST_PALETTE = [M.YELLOW_GLAZED, M.GOLD_ACCENT]  # 官署黄兽
OFFICE_TAOSHOU = M.YELLOW_GLAZED
MARKET_BEAST_PALETTE = [M.DARK, M.GOLD_ACCENT]  # 市井低调
MARKET_TAOSHOU = M.DARK
WARD_BEAST_PALETTE = [M.ANDESITE, M.WOOD]  # 民宅朴素
WARD_TAOSHOU = M.ANDESITE


# ---------------------------------------------------------------------------
# Derived footprint tables (name, x1, z1, x2, z2, y_call, layers) - replayed
# add_ridge_roof calls of the source modules, local city coordinates.
# ---------------------------------------------------------------------------
# Three great temples: main halls (temple_daci/temple_qinglong/
# temple_daxingshan.py) plus the 8 side ridges of roof_color_zoning_3d.
TEMPLE_BUILDINGS = [
    # name                        x1    z1    x2    z2   y_call layers
    ("daci gate",                 4580, 3594, 4620, 3606, 16, 2),
    ("daci heavenly hall",        4562, 3672, 4638, 3728, 21, 3),
    ("daci mahavira hall",        4545, 3805, 4655, 3895, 29, 4),
    ("daci dharma",               4560, 3950, 4640, 4010, 19, 2),
    ("daci sutra w",              4498, 3901, 4542, 3939, 15, 2),
    ("daci sutra e",              4658, 3901, 4702, 3939, 15, 2),
    ("qinglong gate",             5030,  794, 5070,  806, 17, 2),
    ("qinglong buddha hall",      4998, 1008, 5102, 1092, 29, 4),
    ("qinglong sutra",            5100, 1105, 5160, 1155, 19, 2),
    ("daxingshan gate",           1432, 2194, 1468, 2206, 15, 2),
    ("daxingshan heavenly hall",  1414, 2294, 1486, 2346, 23, 3),
    ("daxingshan mahavira hall",  1398, 2438, 1502, 2522, 31, 4),
    ("daxingshan sutra",          1330, 2455, 1390, 2505, 21, 2),
]

# Guozijian (academy_guozijian.py): the six ridges of roof_color_zoning_3d.
GUOZIJIAN_BUILDINGS = [
    # name        x1    z1    x2    z2   y_call layers
    ("lingxing",  1878, 4194, 1922, 4206, 15, 2),
    ("confucius", 1844, 4394, 1956, 4486, 23, 3),
    ("lecture w", 1760, 4414, 1840, 4526, 15, 2),
    ("lecture e", 1960, 4414, 2040, 4526, 15, 2),
    ("dorm s",    1624, 4556, 2176, 4594, 11, 2),
    ("dorm n",    1624, 4596, 2176, 4634, 11, 2),
]

# Imperial city office main halls (government_offices.py):
# hall roof (cx-52..cx+52 / z1+24..z1+96, y 21, l3) with z1 = cz-55.
OFFICE_HALL_BUILDINGS = [
    (name, cx - 52, cz - 31, cx + 52, cz + 41, 21, 3)
    for name, cx, cz in OFFICES
]


def _market_shop_buildings() -> list[tuple[str, int, int, int, int, int, int]]:
    """Replay the 12 market_block.py shop roofs (base_y 2, y_call 15, l2)."""
    buildings = []
    for ox, oz, q in MARKET_SAMPLE_SHOPS:
        qx, qz = MARKET_SHOP_QUADRANTS[q]
        sx, sz = ox + qx, oz + qz
        buildings.append((f"shop {sx},{sz}", sx - 4, sz - 4, sx + 50, sz + 36, 15, 2))
    return buildings


def _ward_mansion_buildings() -> list[tuple[str, int, int, int, int, int, int]]:
    """Replay the 12 ward_block.py mansion roofs (base_y 1, y_call 12, l2)."""
    buildings = []
    for i, (ox, oz) in enumerate(WARD_SAMPLE_MANSIONS):
        qx, qz = WARD_MANSION_QUADRANTS[i % 4]
        mx, mz = ox + qx, oz + qz
        buildings.append((f"mansion {ox},{oz}", mx + 10, mz + 10, mx + 60, mz + 60, 12, 2))
    return buildings


MARKET_SHOP_BUILDINGS = _market_shop_buildings()
WARD_MANSION_BUILDINGS = _ward_mansion_buildings()


# ---------------------------------------------------------------------------
# Overlay primitives.
# ---------------------------------------------------------------------------
def _ridge_base_y(y_call: int, layers: int) -> int:
    """lib.add_ridge_roof ridge-cap base: y_call + max(3, layers * 2)."""
    return y_call + max(3, layers * 2)


def _verify_against_roof_zoning() -> None:
    """Cross-check our replayed ridge lines against the roof_color_zoning_3d
    tables (GUOZIJIAN_RIDGES, TEMPLE_SIDE_RIDGES, OFFICES hall derivation)."""
    replayed_guozijian = sorted(
        (name, (x1 + x2) // 2, z1 + 4, z2 - 4, _ridge_base_y(y, layers))
        for name, x1, z1, x2, z2, y, layers in GUOZIJIAN_BUILDINGS
    )
    if replayed_guozijian != sorted(GUOZIJIAN_RIDGES):
        raise ValueError("guozijian ridge replay drifted from roof_color_zoning_3d.GUOZIJIAN_RIDGES")

    side_names = {name for name, *_ in TEMPLE_SIDE_RIDGES}
    replayed_temples = sorted(
        (name, (x1 + x2) // 2, z1 + 4, z2 - 4, _ridge_base_y(y, layers))
        for name, x1, z1, x2, z2, y, layers in TEMPLE_BUILDINGS
        if name in side_names
    )
    if replayed_temples != sorted(TEMPLE_SIDE_RIDGES):
        raise ValueError("temple side ridge replay drifted from roof_color_zoning_3d.TEMPLE_SIDE_RIDGES")

    for name, cx, cz in OFFICES:
        z1 = cz - 55
        expected = (cx, z1 + 28, z1 + 92, 27)
        found = next(r for r in OFFICE_HALL_BUILDINGS if r[0] == name)
        _, x1, fz1, x2, fz2, y, layers = found
        got = ((x1 + x2) // 2, fz1 + 4, fz2 - 4, _ridge_base_y(y, layers))
        if got != expected:
            raise ValueError(f"office hall {name} ridge replay drifted: {got} != {expected}")


def _one_beast(
    fills: list[Fill],
    label: str,
    x: int,
    y: int,
    z: int,
    body: str,
    base_block: str = M.DARK,
) -> None:
    """One walking beast: dark plinth plus a 3-block body/head column
    (same silhouette as lib.add_roof_beasts, merged into two fills)."""
    add_fill(fills, f"{label} base", (x, y, z), (x, y, z), base_block)
    add_fill(fills, f"{label} body", (x, y + 1, z), (x, y + 3, z), body)


def _city_beasts(
    fills: list[Fill],
    label: str,
    cx: int,
    rz1: int,
    rz2: int,
    y: int,
    count: int,
    palette: list[str] | None = None,
    base_block: str = M.DARK,
) -> None:
    """Walking beasts along one axis-z main ridge (正脊走兽).

    Mirrors lib.add_roof_beasts (same 4-block end inset and even spacing,
    plinth + coloured body, beasts standing on the first free block above
    the ridge cap) with a category palette; the default palette delegates
    to lib.add_roof_beasts directly.  Ridges too short for the inset row
    (the five-block gate ridges) get their beasts abreast across the
    3-wide ridge cap instead of collapsed onto a single spot.
    """
    if count < 1:
        return
    if palette is None:
        add_roof_beasts(fills, label, cx, rz1, cx, rz2, y, ridge_axis="z", count=count)
        return
    length = rz2 - rz1
    if length >= count + 7:
        # Inline row between the ridge ends (4-block inset clears the finials).
        for i in range(count):
            z = rz1 + 4 + int(i * max(1, length - 8) / max(1, count - 1))
            _one_beast(
                fills, f"{label} beast {i}", cx, y, min(z, rz2 - 4),
                palette[i % len(palette)], base_block,
            )
    else:
        # Short ridge: beasts side by side on the cap, centred between the finials.
        z = (rz1 + rz2) // 2
        for i in range(count):
            x = min(max(cx - 1 + round(i * 2 / max(1, count - 1)), cx - 1), cx + 1)
            _one_beast(
                fills, f"{label} beast {i}", x, y, z,
                palette[i % len(palette)], base_block,
            )


def _taoshou(fills: list[Fill], label: str, x: int, y: int, z: int, block: str) -> None:
    """套兽 wing-corner cap: a 1x1x2 post standing on an eave-slab corner
    (the slab occupies y-1, so the post stands at y_call)."""
    add_fill(fills, label, (x, y, z), (x, y + 1, z), block)


def _detail_ridge(
    fills: list[Fill],
    label: str,
    x1: int,
    z1: int,
    x2: int,
    z2: int,
    y_call: int,
    layers: int,
    count: int,
    palette: list[str],
    taoshou_block: str,
    beast_base: str = M.DARK,
) -> int:
    """Beast row on one main ridge plus the four wing-corner taoshou caps."""
    cx = (x1 + x2) // 2
    _city_beasts(
        fills, label, cx, z1 + 4, z2 - 4,
        _ridge_base_y(y_call, layers) + 2, count, palette, beast_base,
    )
    for tx, tz in ((x1 - 2, z1 - 3), (x1 - 2, z2 + 3), (x2 + 2, z1 - 3), (x2 + 2, z2 + 3)):
        _taoshou(fills, f"{label} taoshou {tx},{tz}", tx, y_call, tz, taoshou_block)
    return count


# ---------------------------------------------------------------------------
# Main builder.
# ---------------------------------------------------------------------------
def build_city_roof_beasts_3d(fills: list[Fill]) -> None:
    _verify_against_roof_zoning()
    beasts = 0

    # ------------------------------------------------------------------
    # 1. Temple ridge beasts (佛寺青脊金兽): main + side halls of
    #    Da Ci'en, Qinglong and Daxingshan, count=3 per ridge, blue
    #    plinths with gold / gilded-blackstone bodies.
    # ------------------------------------------------------------------
    for name, x1, z1, x2, z2, y_call, layers in TEMPLE_BUILDINGS:
        beasts += _detail_ridge(
            fills, f"citybeast temple {name}", x1, z1, x2, z2, y_call, layers,
            count=3, palette=TEMPLE_BEAST_PALETTE,
            taoshou_block=TEMPLE_TAOSHOU, beast_base=TEMPLE_BEAST_BASE,
        )

    # ------------------------------------------------------------------
    # 2. Office ridge beasts (官署黄脊黄兽): six guozijian ridges plus
    #    the four office main halls, count=3, yellow-glazed / gilded.
    # ------------------------------------------------------------------
    for name, x1, z1, x2, z2, y_call, layers in GUOZIJIAN_BUILDINGS:
        beasts += _detail_ridge(
            fills, f"citybeast office guozijian {name}", x1, z1, x2, z2, y_call, layers,
            count=3, palette=OFFICE_BEAST_PALETTE, taoshou_block=OFFICE_TAOSHOU,
        )
    for name, x1, z1, x2, z2, y_call, layers in OFFICE_HALL_BUILDINGS:
        beasts += _detail_ridge(
            fills, f"citybeast office {name} hall", x1, z1, x2, z2, y_call, layers,
            count=3, palette=OFFICE_BEAST_PALETTE, taoshou_block=OFFICE_TAOSHOU,
        )

    # ------------------------------------------------------------------
    # 3. Market shop ridge beasts (市铺深灰兽): 12 representative shops,
    #    count=2, deepslate / gilded - understated market grade.
    # ------------------------------------------------------------------
    for name, x1, z1, x2, z2, y_call, layers in MARKET_SHOP_BUILDINGS:
        beasts += _detail_ridge(
            fills, f"citybeast market {name}", x1, z1, x2, z2, y_call, layers,
            count=2, palette=MARKET_BEAST_PALETTE, taoshou_block=MARKET_TAOSHOU,
        )

    # ------------------------------------------------------------------
    # 4. Ward mansion ridge beasts (宅邸灰兽): 12 representative ward
    #    mansions, count=2, andesite / dark oak - plain residential grade.
    # ------------------------------------------------------------------
    for name, x1, z1, x2, z2, y_call, layers in WARD_MANSION_BUILDINGS:
        beasts += _detail_ridge(
            fills, f"citybeast ward {name}", x1, z1, x2, z2, y_call, layers,
            count=2, palette=WARD_BEAST_PALETTE, taoshou_block=WARD_TAOSHOU,
        )

    # ------------------------------------------------------------------
    # 5. City-wide beast tally (全城走兽数量统计).
    # ------------------------------------------------------------------
    tallies: dict[str, dict[str, int]] = {}
    for cat, ridges in (
        ("temple", TEMPLE_BUILDINGS),
        ("office", GUOZIJIAN_BUILDINGS + OFFICE_HALL_BUILDINGS),
        ("market", MARKET_SHOP_BUILDINGS),
        ("ward", WARD_MANSION_BUILDINGS),
    ):
        cat_fills = [f for f in fills if f.label.startswith(f"citybeast {cat} ")]
        tallies[cat] = {
            "ridges": len(ridges),
            "beasts": sum(1 for f in cat_fills if f.label.endswith(" base")),
            "taoshou": sum(1 for f in cat_fills if " taoshou " in f.label),
            "fills": len(cat_fills),
        }
    print(
        json.dumps(
            {
                "section": "city_roof_beasts_3d",
                "categories": tallies,
                "total_ridges": sum(t["ridges"] for t in tallies.values()),
                "total_beasts": beasts,
                "total_taoshou": sum(t["taoshou"] for t in tallies.values()),
                "total_fills": len(fills),
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )


def main() -> None:
    run_builder(build_city_roof_beasts_3d, "city_roof_beasts_3d")


if __name__ == "__main__":
    main()
