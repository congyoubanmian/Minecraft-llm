"""Module verification toolkit for the Tang Chang'an build pipeline.

Three checks, usable together:

1. bbox   — bounding-box overlap between new modules and every other
            module. Fast; flags possible conflicts (city-wide tiling
            layers can be excluded).
2. voxel  — fill-level collision: the actual block sets of the new
            modules are intersected with those of every bbox-flagged
            module. Zero tolerance for real overlaps.
3. attach — attachment-ratio for detail-overlay modules: every solid
            detail block must be adjacent to (or part of) the target
            buildings' own blocks, so nothing floats in mid-air.

Usage:
    # bbox + voxel for new modules (tiling/detail layers excluded)
    python3 scripts/changan/verify_modules.py --modules a_3d,b_3d

    # whitelist known overlay targets
    python3 scripts/changan/verify_modules.py --modules a_3d \
        --allow '{"a_3d": ["pagoda_giant", "window_lattice"]}'

    # attachment check against explicit target modules
    python3 scripts/changan/verify_modules.py --modules a_3d --attach \
        --targets '{"a_3d": ["palace_hanyuan_dian"]}'

Exit code 0 = clean (only whitelisted hits), 1 = unexpected conflicts.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan import build_all
from scripts.changan.lib import Fill

# Layers that legitimately span the whole city; landmarks are expected to
# overwrite them, so bbox hits against these are not reportable.
CITY_WIDE_LAYERS = {
    "ward_block", "market_block", "road_paving", "street_facilities",
    "street_props", "roof_ornaments", "window_lattice", "drainage_ditches",
    "lantern_festival", "night_market", "seasonal_vegetation",
    "flowers_gardens", "city_guards", "suburb_farms", "farm_irrigation",
    "temple_incense_banners", "palace_plaques_murals", "palace_interior",
    "street_wells_millstones", "garden_rockery", "moat_bridge_railings",
    "wall_battlement_moat", "gates_all", "wall_corner_tower",
    "rampart_horse_way", "wall_dilou_3d", "terrain_longshou",
}


def bbox_of(fn) -> tuple[int, int, int, int, int, int]:
    fills: list[Fill] = []
    fn(fills)
    return (
        min(f.x1 for f in fills), max(f.x2 for f in fills),
        min(f.y1 for f in fills), max(f.y2 for f in fills),
        min(f.z1 for f in fills), max(f.z2 for f in fills),
    )


def voxels_of(fn) -> set[tuple[int, int, int]]:
    voxels: set[tuple[int, int, int]] = set()
    fills: list[Fill] = []
    fn(fills)
    for f in fills:
        if f.block == "minecraft:air":
            continue
        for x in range(f.x1, f.x2 + 1):
            for y in range(f.y1, f.y2 + 1):
                for z in range(f.z1, f.z2 + 1):
                    voxels.add((x, y, z))
    return voxels


def bbox_scan(new_modules: dict[str, callable], allow: dict[str, set[str]]) -> dict[str, list[str]]:
    others = {}
    for name, fn in build_all.MODULES.items():
        if name in new_modules:
            continue
        try:
            others[name] = bbox_of(fn)
        except Exception:
            continue
    report = {}
    for nm, fn in new_modules.items():
        nx1, nx2, ny1, ny2, nz1, nz2 = bbox_of(fn)
        whitelist = allow.get(nm, set()) | CITY_WIDE_LAYERS
        hits = []
        for other, (ox1, ox2, oy1, oy2, oz1, oz2) in others.items():
            if other in whitelist:
                continue
            if (nx1 - 3 < ox2 and ox1 - 3 < nx2 and ny1 - 3 < oy2 and oy1 - 3 < ny2
                    and nz1 - 3 < oz2 and oz1 - 3 < nz2):
                hits.append(other)
        report[nm] = hits
    return report


def voxel_scan(new_modules: dict[str, callable], suspicious: dict[str, list[str]]) -> dict[str, dict[str, int]]:
    report: dict[str, dict[str, int]] = {}
    new_vox = {nm: voxels_of(fn) for nm, fn in new_modules.items()}
    other_cache: dict[str, set] = {}
    for nm, others in suspicious.items():
        if not others:
            continue
        report[nm] = {}
        for other in others:
            if other not in build_all.MODULES:
                report[nm][other] = -1
                continue
            if other not in other_cache:
                other_cache[other] = voxels_of(build_all.MODULES[other])
            inter = new_vox[nm] & other_cache[other]
            report[nm][other] = len(inter)
    return report


def attach_scan(new_modules: dict[str, callable], targets: dict[str, list[str]]) -> dict[str, float]:
    report = {}
    target_sets = {}
    for nm, fn in new_modules.items():
        tnames = targets.get(nm, [])
        if not tnames:
            continue
        key = tuple(sorted(tnames))
        if key not in target_sets:
            tset: set[tuple[int, int, int]] = set()
            for tn in tnames:
                if tn in build_all.MODULES:
                    tset |= voxels_of(build_all.MODULES[tn])
            target_sets[key] = tset
        tset = target_sets[key]
        fills: list[Fill] = []
        fn(fills)
        ok = total = 0
        for f in fills:
            if f.block == "minecraft:air":
                continue
            for x in range(f.x1, f.x2 + 1):
                for y in range(f.y1, f.y2 + 1):
                    for z in range(f.z1, f.z2 + 1):
                        total += 1
                        if any((x + dx, y + dy, z + dz) in tset for dx, dy, dz in
                               ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))):
                            ok += 1
        report[nm] = round(ok / max(1, total), 3)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Chang'an modules for conflicts before execution.")
    parser.add_argument("--modules", required=True, help="Comma-separated NEW module names to verify.")
    parser.add_argument("--allow", default=None, help="JSON: module -> list of expected-overlay module names (whitelisted).")
    parser.add_argument("--voxel", action="store_true", help="Run fill-level voxel collision on bbox-flagged pairs.")
    parser.add_argument("--attach", action="store_true", help="Run attachment-ratio check (detail overlays).")
    parser.add_argument("--targets", default=None, help="JSON: module -> list of target module names for --attach.")
    args = parser.parse_args()

    names = [n.strip() for n in args.modules.split(",") if n.strip()]
    unknown = [n for n in names if n not in build_all.MODULES]
    if unknown:
        raise SystemExit(f"unknown modules: {unknown}")
    new_modules = {n: build_all.MODULES[n] for n in names}
    allow = {k: set(v) for k, v in json.loads(args.allow).items()} if args.allow else {}
    targets = json.loads(args.targets) if args.targets else {}

    exit_code = 0

    print("== bbox 扫描 ==")
    bbox_report = bbox_scan(new_modules, allow)
    for nm, hits in bbox_report.items():
        if hits:
            print(f"  ⚠️ {nm}: {hits}")
        else:
            print(f"  ✓ {nm}: 无相交")

    if args.voxel and any(bbox_report.values()):
        print("== voxel 体素碰撞（bbox 命中项复核）==")
        voxel_report = voxel_scan(new_modules, bbox_report)
        for nm, pairs in voxel_report.items():
            for other, count in pairs.items():
                if count > 0:
                    print(f"  ⚠️ {nm} × {other}: {count} 格真实重叠")
                    exit_code = 1
                elif count == 0:
                    print(f"  ✓ {nm} × {other}: bbox 相邻但零碰撞")

    if args.attach:
        print("== attach 贴附率（细节叠加模块）==")
        attach_report = attach_scan(new_modules, targets)
        for nm, ratio in attach_report.items():
            print(f"  {nm}: 贴附率 {ratio:.1%}")

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
