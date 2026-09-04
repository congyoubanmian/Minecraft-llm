from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan import (
    academy_guozijian,
    ancestral_temple_altar,
    bell_drum_3d,
    bell_drum_towers,
    bridge_stone_arch,
    canal_waterway,
    city_guards,
    drainage_ditches,
    entertainment_venues,
    entertainment_spectators,
    farm_irrigation,
    flowers_gardens,
    foreign_temples,
    fudao_jiacheng_3d,
    garden_rockery,
    gate_mingde_men,
    gate_zhuque_men,
    gates_all,
    gates_south_3d,
    government_offices,
    grotto_buddha_3d,
    hanliang_ziyu_3d,
    imperial_daming_palace,
    imperial_taiji_palace,
    lantern_festival,
    leyouyuan_stele,
    lingyan_ge_3d,
    market_block,
    market_details,
    mingtang_altar_3d,
    moat_bridge_railings,
    mountain_zhongnan,
    night_market,
    observatory_3d,
    official_residence,
    palace_hanyuan_3d,
    palace_hanyuan_dian,
    palace_interior,
    palace_linde_3d,
    palace_plaques_murals,
    palace_xingqing,
    palace_xuanzheng_dian,
    palace_zichen_dian,
    pagoda_giant,
    pagoda_giant_3d,
    pagoda_small,
    penglai_island_3d,
    polo_stadium_3d,
    qujiang_pool_3d,
    road_paving,
    rampart_horse_way,
    roof_ornaments,
    street_facilities,
    street_props,
    street_wells_millstones,
    suburb_farms,
    tavern,
    temple_daci,
    temple_daxingshan,
    temple_dayan,
    temple_jianfu,
    temple_qinglong,
    temple_incense_banners,
    temple_xuandu,
    terrain_longshou,
    tomb_spirit_way,
    underground_drain_3d,
    wall_battlement_moat,
    wall_corner_tower,
    wall_dilou_3d,
    wanglou_network_3d,
    ward_block,
    water_gates,
    waterwheel_mill_3d,
    window_lattice,
    xingqing_palace_3d,
    xishi_qiting_3d,
    zhaigong_3d,
    baliu_3d,
    fuyong_yuan_3d,
    guangyun_dock_3d,
    liyuan_3d,
    tai_cang_3d,
    beilin_3d,
    huaqing_palace_3d,
    kunming_pool_3d,
    silk_caravan_3d,
    weishui_ferry_3d,
    douting_post_3d,
    hanlin_academy_3d,
    qinwu_tower_3d,
    sanqing_temple_3d,
    tangchang_guan_3d,
    beacon_tower_3d,
    jingjiao_bei_3d,
    taiyiyuan_3d,
    xiaoyanta_3d,
    bangyuan_3d,
    bingjiao_3d,
    palace_roof_detail_3d,
    palace_facade_detail_3d,
    pagoda_body_detail_3d,
    gate_wall_detail_3d,
    mural_detail_3d,
    courtyard_life_detail_3d,
    jinzouyuan_3d,
    wenyuan_3d,
    zhijinfang_3d,
    xingyuan_3d,
    seasonal_vegetation,
)
from scripts.changan.lib import (
    DOCKER_CONTAINER,
    Fill,
    RCON_TIMEOUT,
    execute_fill,
    group_fills_by_load_region,
    rcon,
    validate_fills,
)


"""
Phased orchestrator for building Tang Chang'an.

Runs the fine-grained modules in logical layers so the city is filled
progressively: tiling -> landmarks -> details -> events.

Usage:
    # Dry-run a phase
    .venv/bin/python scripts/changan/run_all_phases.py --phase tiling

    # Execute a phase in batches of 500
    .venv/bin/python scripts/changan/run_all_phases.py --phase tiling --execute --limit 500

    # Continue from offset 500
    .venv/bin/python scripts/changan/run_all_phases.py --phase tiling --execute --start 500 --limit 500

    # Dry-run everything
    .venv/bin/python scripts/changan/run_all_phases.py --phase all
"""


PHASES: dict[str, list[tuple[str, Callable[[list[Fill]], None]]]] = {
    "terrain": [
        ("terrain_longshou", terrain_longshou.build_longshou_elevation),
    ],
    "tiling": [
        ("ward_block", ward_block.build_all_ward_blocks),
        ("market_block", market_block.build_all_market_blocks),
        ("suburb_farms", suburb_farms.build_suburb_farms),
        ("farm_irrigation", farm_irrigation.build_farm_irrigation),
        ("road_paving", road_paving.build_road_paving),
        ("street_facilities", street_facilities.build_street_facilities),
    ],
    "commercial": [
        ("tavern", tavern.build_taverns_in_markets),
        ("market_details", market_details.build_market_details),
    ],
    "landmarks": [
        ("palace_hanyuan_dian", palace_hanyuan_dian.build_hanyuan_dian),
        ("palace_hanyuan_3d", palace_hanyuan_3d.build_hanyuan_3d),
        ("palace_linde_3d", palace_linde_3d.build_linde_3d),
        ("palace_xuanzheng_dian", palace_xuanzheng_dian.build_xuanzheng_dian),
        ("palace_zichen_dian", palace_zichen_dian.build_zichen_dian),
        ("palace_xingqing", palace_xingqing.build_xingqing_palace),
        ("imperial_taiji_palace", imperial_taiji_palace.build_taiji_palace),
        ("imperial_daming_palace", imperial_daming_palace.build_daming_palace),
        ("palace_interior", palace_interior.build_palace_interior),
        ("gate_zhuque_men", gate_zhuque_men.build_zhuque_men),
        ("gate_mingde_men", gate_mingde_men.build_mingde_men),
        ("gates_all", gates_all.build_all_gates),
        ("wall_corner_tower", wall_corner_tower.build_corner_towers),
        ("wall_battlement_moat", wall_battlement_moat.build_wall_battlement_moat),
        ("rampart_horse_way", rampart_horse_way.build_horse_ways),
        ("pagoda_giant", pagoda_giant.build_giant_pagoda),
        ("pagoda_giant_3d", pagoda_giant_3d.build_giant_pagoda_3d),
        ("pagoda_small", pagoda_small.build_small_pagoda),
        ("temple_qinglong", temple_qinglong.build_qinglong_temple),
        ("temple_daxingshan", temple_daxingshan.build_daxingshan_temple),
        ("temple_dayan", temple_dayan.build_dayan_temple),
        ("temple_xuandu", temple_xuandu.build_xuandu_temple),
        ("temple_daci", temple_daci.build_daci_temple),
        ("temple_jianfu", temple_jianfu.build_jianfu_temple),
        ("foreign_temples", foreign_temples.build_foreign_temples),
        ("government_offices", government_offices.build_government_offices),
        ("entertainment_venues", entertainment_venues.build_entertainment_venues),
        ("polo_stadium_3d", polo_stadium_3d.build_polo_stadium_3d),
        ("entertainment_spectators", entertainment_spectators.build_entertainment_spectators),
        ("bell_drum_towers", bell_drum_towers.build_bell_drum_towers),
        ("bell_drum_3d", bell_drum_3d.build_bell_drum_3d),
        ("bridge_stone_arch", bridge_stone_arch.build_all_bridges),
        ("moat_bridge_railings", moat_bridge_railings.build_moat_bridge_railings),
        ("canal_waterway", canal_waterway.build_canals),
        ("water_gates", water_gates.build_water_gates),
        ("ancestral_temple_altar", ancestral_temple_altar.build_ancestral_temple_altar),
        ("academy_guozijian", academy_guozijian.build_guozijian),
        ("official_residence", official_residence.build_all_residences),
        ("garden_rockery", garden_rockery.build_all_rockeries),
        ("mountain_zhongnan", mountain_zhongnan.build_zhongnan_mountain),
        ("tomb_spirit_way", tomb_spirit_way.build_tomb_spirit_way),
        ("leyouyuan_stele", leyouyuan_stele.build_leyouyuan_details),
        ("qujiang_pool_3d", qujiang_pool_3d.build_qujiang_pool_3d),
        ("mingtang_altar_3d", mingtang_altar_3d.build_mingtang_altar_3d),
        ("observatory_3d", observatory_3d.build_observatory_3d),
        ("fudao_jiacheng_3d", fudao_jiacheng_3d.build_fudao_jiacheng_3d),
        ("grotto_buddha_3d", grotto_buddha_3d.build_grotto_buddha_3d),
        ("waterwheel_mill_3d", waterwheel_mill_3d.build_waterwheel_mill_3d),
        ("wall_dilou_3d", wall_dilou_3d.build_wall_dilou_3d),
        ("penglai_island_3d", penglai_island_3d.build_penglai_island_3d),
        ("underground_drain_3d", underground_drain_3d.build_underground_drain_3d),
        ("zhaigong_3d", zhaigong_3d.build_zhaigong_3d),
        ("lingyan_ge_3d", lingyan_ge_3d.build_lingyan_ge_3d),
        ("hanliang_ziyu_3d", hanliang_ziyu_3d.build_hanliang_ziyu_3d),
        ("xishi_qiting_3d", xishi_qiting_3d.build_xishi_qiting_3d),
        ("wanglou_network_3d", wanglou_network_3d.build_wanglou_network_3d),
        ("gates_south_3d", gates_south_3d.build_gates_south_3d),
        ("xingqing_palace_3d", xingqing_palace_3d.build_xingqing_palace_3d),
        ("fuyong_yuan_3d", fuyong_yuan_3d.build_fuyong_yuan_3d),
        ("xingyuan_3d", xingyuan_3d.build_xingyuan_3d),
        ("baliu_3d", baliu_3d.build_baliu_3d),
        ("guangyun_dock_3d", guangyun_dock_3d.build_guangyun_dock_3d),
        ("liyuan_3d", liyuan_3d.build_liyuan_3d),
        ("tai_cang_3d", tai_cang_3d.build_tai_cang_3d),
        ("weishui_ferry_3d", weishui_ferry_3d.build_weishui_ferry_3d),
        ("kunming_pool_3d", kunming_pool_3d.build_kunming_pool_3d),
        ("huaqing_palace_3d", huaqing_palace_3d.build_huaqing_palace_3d),
        ("beilin_3d", beilin_3d.build_beilin_3d),
        ("silk_caravan_3d", silk_caravan_3d.build_silk_caravan_3d),
        ("hanlin_academy_3d", hanlin_academy_3d.build_hanlin_academy_3d),
        ("sanqing_temple_3d", sanqing_temple_3d.build_sanqing_temple_3d),
        ("qinwu_tower_3d", qinwu_tower_3d.build_qinwu_tower_3d),
        ("douting_post_3d", douting_post_3d.build_douting_post_3d),
        ("tangchang_guan_3d", tangchang_guan_3d.build_tangchang_guan_3d),
        ("xiaoyanta_3d", xiaoyanta_3d.build_xiaoyanta_3d),
        ("taiyiyuan_3d", taiyiyuan_3d.build_taiyiyuan_3d),
        ("jingjiao_bei_3d", jingjiao_bei_3d.build_jingjiao_bei_3d),
        ("beacon_tower_3d", beacon_tower_3d.build_beacon_tower_3d),
        ("bangyuan_3d", bangyuan_3d.build_bangyuan_3d),
        ("wenyuan_3d", wenyuan_3d.build_wenyuan_3d),
        ("zhijinfang_3d", zhijinfang_3d.build_zhijinfang_3d),
        ("bingjiao_3d", bingjiao_3d.build_bingjiao_3d),
        ("jinzouyuan_3d", jinzouyuan_3d.build_jinzouyuan_3d),
        ("palace_roof_detail_3d", palace_roof_detail_3d.build_palace_roof_detail_3d),
        ("palace_facade_detail_3d", palace_facade_detail_3d.build_palace_facade_detail_3d),
        ("pagoda_body_detail_3d", pagoda_body_detail_3d.build_pagoda_body_detail_3d),
        ("gate_wall_detail_3d", gate_wall_detail_3d.build_gate_wall_detail_3d),
        ("mural_detail_3d", mural_detail_3d.build_mural_detail_3d),
        ("courtyard_life_detail_3d", courtyard_life_detail_3d.build_courtyard_life_detail_3d),
    ],
    "details": [
        ("window_lattice", window_lattice.build_window_lattices),
        ("roof_ornaments", roof_ornaments.build_roof_ornaments),
        ("street_props", street_props.build_street_props),
        ("drainage_ditches", drainage_ditches.build_drainage_ditches),
        ("city_guards", city_guards.build_city_guards),
        ("flowers_gardens", flowers_gardens.build_flowers_gardens),
        ("temple_incense_banners", temple_incense_banners.build_temple_rituals),
        ("palace_plaques_murals", palace_plaques_murals.build_palace_decor),
        ("street_wells_millstones", street_wells_millstones.build_street_wells_millstones),
    ],
    "events": [
        ("lantern_festival", lantern_festival.build_lantern_festival),
        ("night_market", night_market.build_night_market),
        ("seasonal_vegetation", seasonal_vegetation.build_seasonal_vegetation),
    ],
}


def selected_modules(
    phase: str,
    include: set[str] | None = None,
    exclude: set[str] | None = None,
) -> list[tuple[str, Callable[[list[Fill]], None]]]:
    modules = [module for entries in PHASES.values() for module in entries] if phase == "all" else list(PHASES[phase])
    available = {name for name, _ in modules}
    unknown = (include or set()) - available
    if unknown:
        raise ValueError(f"Modules not available in phase {phase}: {sorted(unknown)}")
    return [
        (name, builder)
        for name, builder in modules
        if (not include or name in include) and name not in (exclude or set())
    ]


def build_phase(
    fills: list[Fill],
    phase: str,
    include: set[str] | None = None,
    exclude: set[str] | None = None,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for name, builder in selected_modules(phase, include, exclude):
        before = len(fills)
        builder(fills)
        counts[name] = len(fills) - before
    return counts


def execute_fills(
    fills: list[Fill],
    start: int,
    start_region: int,
    limit: int | None,
    delay_ms: int,
    report_every: int,
    timeout: int,
    no_forceload: bool,
) -> None:
    selected = fills[start:]
    if limit is not None:
        selected = selected[:limit]

    print(
        json.dumps(
            {
                "phase": "selected",
                "total_fills": len(fills),
                "selected_fills": len(selected),
                "start": start,
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )

    rcon("gamerule randomTickSpeed 0", timeout)
    rcon("weather clear", timeout)

    if no_forceload:
        groups = {(0, 0): selected}
    else:
        groups = group_fills_by_load_region(selected)
    all_groups = list(groups.items())
    selected_groups = all_groups[start_region:]
    total_pieces = sum(len(group) for _, group in selected_groups)
    print(
        json.dumps(
            {
                "load_regions": len(all_groups),
                "start_region": start_region,
                "selected_regions": len(selected_groups),
                "execution_pieces": total_pieces,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    done = 0
    for region_index, ((rx, rz), region_fills) in enumerate(selected_groups, start=start_region + 1):
        load_x1 = min(min(fill.x1, fill.x2) for fill in region_fills)
        load_z1 = min(min(fill.z1, fill.z2) for fill in region_fills)
        load_x2 = max(max(fill.x1, fill.x2) for fill in region_fills)
        load_z2 = max(max(fill.z1, fill.z2) for fill in region_fills)
        try:
            if not no_forceload:
                rcon(f"forceload add {load_x1} {load_z1} {load_x2} {load_z2}", timeout)
            for fill in region_fills:
                output = rcon(
                    f"fill {fill.x1} {fill.y1} {fill.z1} {fill.x2} {fill.y2} {fill.z2} {fill.block}",
                    timeout,
                )
                done += 1
                if delay_ms:
                    time.sleep(delay_ms / 1000)
                if done % report_every == 0 or done == total_pieces:
                    print(
                        json.dumps(
                            {
                                "done": done,
                                "total": total_pieces,
                                "region": region_index,
                                "regions": len(all_groups),
                                "label": fill.label,
                                "sample": f"{fill.x1} {fill.y1} {fill.z1} {fill.x2} {fill.y2} {fill.z2} {fill.block}",
                                "result": output[:160],
                            },
                            ensure_ascii=False,
                        ),
                        flush=True,
                    )
        finally:
            if not no_forceload:
                rcon(f"forceload remove {load_x1} {load_z1} {load_x2} {load_z2}", timeout)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phased builder for Tang Chang'an fine-grained modules.",
    )
    parser.add_argument(
        "--phase",
        type=str,
        required=True,
        choices=list(PHASES.keys()) + ["all"],
        help="Which phase to build (terrain, tiling, commercial, landmarks, details, events, all).",
    )
    parser.add_argument("--include", default=None, help="Comma-separated module names to include from the selected phase.")
    parser.add_argument("--exclude", default=None, help="Comma-separated module names to exclude from the selected phase.")
    parser.add_argument("--execute", action="store_true", help="Actually send commands to the server.")
    parser.add_argument("--start", type=int, default=0, help="0-based fill offset.")
    parser.add_argument("--start-region", type=int, default=0, help="0-based load-region offset for an interrupted run.")
    parser.add_argument("--limit", type=int, default=None, help="Only process N fills.")
    parser.add_argument("--delay-ms", type=int, default=60, help="Delay between /fill commands.")
    parser.add_argument("--report-every", type=int, default=100)
    parser.add_argument("--timeout", type=int, default=RCON_TIMEOUT)
    parser.add_argument("--no-forceload", action="store_true", help="Skip forceload (only if chunks already loaded).")
    args = parser.parse_args()

    if args.start < 0:
        parser.error("--start must be >= 0")
    if args.start_region < 0:
        parser.error("--start-region must be >= 0")
    if args.limit is not None and args.limit < 0:
        parser.error("--limit must be >= 0")
    if args.delay_ms < 0:
        parser.error("--delay-ms must be >= 0")
    if args.report_every <= 0:
        parser.error("--report-every must be > 0")

    include = {name.strip() for name in args.include.split(",") if name.strip()} if args.include else None
    exclude = {name.strip() for name in args.exclude.split(",") if name.strip()} if args.exclude else None

    fills: list[Fill] = []
    try:
        module_counts = build_phase(fills, args.phase, include, exclude)
    except ValueError as exc:
        parser.error(str(exc))
    validation = validate_fills(fills)

    print(
        json.dumps(
            {
                "phase": args.phase,
                "total_fills": len(fills),
                "module_counts": module_counts,
                "execute": args.execute,
                "validation": validation,
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )

    if not args.execute:
        return
    if any(validation.values()):
        raise SystemExit("fill validation failed")

    execute_fills(
        fills,
        args.start,
        args.start_region,
        args.limit,
        args.delay_ms,
        args.report_every,
        args.timeout,
        args.no_forceload,
    )


if __name__ == "__main__":
    main()
