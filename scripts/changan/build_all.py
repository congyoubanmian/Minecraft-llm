from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

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
    xingyuan_3d,
    seasonal_vegetation,
)
from scripts.changan.lib import Fill, run_builder


"""
Orchestrator that builds all fine-grained Chang'an modules.

Usage:
    # Dry run everything
    .venv/bin/python scripts/changan/build_all.py

    # Execute only palace + landmarks in batches
    .venv/bin/python scripts/changan/build_all.py --include palace_hanyuan_dian,pagoda_giant --execute --limit 300
"""

MODULES = {
    "palace_hanyuan_dian": palace_hanyuan_dian.build_hanyuan_dian,
    "palace_xuanzheng_dian": palace_xuanzheng_dian.build_xuanzheng_dian,
    "palace_zichen_dian": palace_zichen_dian.build_zichen_dian,
    "palace_xingqing": palace_xingqing.build_xingqing_palace,
    "imperial_taiji_palace": imperial_taiji_palace.build_taiji_palace,
    "imperial_daming_palace": imperial_daming_palace.build_daming_palace,
    "palace_interior": palace_interior.build_palace_interior,
    "palace_plaques_murals": palace_plaques_murals.build_palace_decor,
    "gate_zhuque_men": gate_zhuque_men.build_zhuque_men,
    "gate_mingde_men": gate_mingde_men.build_mingde_men,
    "gates_all": gates_all.build_all_gates,
    "wall_corner_tower": wall_corner_tower.build_corner_towers,
    "wall_battlement_moat": wall_battlement_moat.build_wall_battlement_moat,
    "rampart_horse_way": rampart_horse_way.build_horse_ways,
    "pagoda_giant": pagoda_giant.build_giant_pagoda,
    "pagoda_giant_3d": pagoda_giant_3d.build_giant_pagoda_3d,
    "pagoda_small": pagoda_small.build_small_pagoda,
    "palace_hanyuan_3d": palace_hanyuan_3d.build_hanyuan_3d,
    "palace_linde_3d": palace_linde_3d.build_linde_3d,
    "mingtang_altar_3d": mingtang_altar_3d.build_mingtang_altar_3d,
    "observatory_3d": observatory_3d.build_observatory_3d,
    "polo_stadium_3d": polo_stadium_3d.build_polo_stadium_3d,
    "qujiang_pool_3d": qujiang_pool_3d.build_qujiang_pool_3d,
    "fudao_jiacheng_3d": fudao_jiacheng_3d.build_fudao_jiacheng_3d,
    "grotto_buddha_3d": grotto_buddha_3d.build_grotto_buddha_3d,
    "waterwheel_mill_3d": waterwheel_mill_3d.build_waterwheel_mill_3d,
    "wall_dilou_3d": wall_dilou_3d.build_wall_dilou_3d,
    "penglai_island_3d": penglai_island_3d.build_penglai_island_3d,
    "underground_drain_3d": underground_drain_3d.build_underground_drain_3d,
    "zhaigong_3d": zhaigong_3d.build_zhaigong_3d,
    "bell_drum_3d": bell_drum_3d.build_bell_drum_3d,
    "lingyan_ge_3d": lingyan_ge_3d.build_lingyan_ge_3d,
    "hanliang_ziyu_3d": hanliang_ziyu_3d.build_hanliang_ziyu_3d,
    "xishi_qiting_3d": xishi_qiting_3d.build_xishi_qiting_3d,
    "wanglou_network_3d": wanglou_network_3d.build_wanglou_network_3d,
    "gates_south_3d": gates_south_3d.build_gates_south_3d,
    "xingqing_palace_3d": xingqing_palace_3d.build_xingqing_palace_3d,
    "fuyong_yuan_3d": fuyong_yuan_3d.build_fuyong_yuan_3d,
    "xingyuan_3d": xingyuan_3d.build_xingyuan_3d,
    "baliu_3d": baliu_3d.build_baliu_3d,
    "guangyun_dock_3d": guangyun_dock_3d.build_guangyun_dock_3d,
    "liyuan_3d": liyuan_3d.build_liyuan_3d,
    "tai_cang_3d": tai_cang_3d.build_tai_cang_3d,
    "temple_qinglong": temple_qinglong.build_qinglong_temple,
    "temple_daxingshan": temple_daxingshan.build_daxingshan_temple,
    "temple_dayan": temple_dayan.build_dayan_temple,
    "temple_xuandu": temple_xuandu.build_xuandu_temple,
    "temple_daci": temple_daci.build_daci_temple,
    "temple_jianfu": temple_jianfu.build_jianfu_temple,
    "foreign_temples": foreign_temples.build_foreign_temples,
    "market_block": market_block.build_all_market_blocks,
    "ward_block": ward_block.build_all_ward_blocks,
    "tavern": tavern.build_taverns_in_markets,
    "night_market": night_market.build_night_market,
    "market_details": market_details.build_market_details,
    "moat_bridge_railings": moat_bridge_railings.build_moat_bridge_railings,
    "street_facilities": street_facilities.build_street_facilities,
    "street_props": street_props.build_street_props,
    "street_wells_millstones": street_wells_millstones.build_street_wells_millstones,
    "city_guards": city_guards.build_city_guards,
    "bridge_stone_arch": bridge_stone_arch.build_all_bridges,
    "canal_waterway": canal_waterway.build_canals,
    "water_gates": water_gates.build_water_gates,
    "drainage_ditches": drainage_ditches.build_drainage_ditches,
    "road_paving": road_paving.build_road_paving,
    "garden_rockery": garden_rockery.build_all_rockeries,
    "official_residence": official_residence.build_all_residences,
    "entertainment_venues": entertainment_venues.build_entertainment_venues,
    "entertainment_spectators": entertainment_spectators.build_entertainment_spectators,
    "roof_ornaments": roof_ornaments.build_roof_ornaments,
    "window_lattice": window_lattice.build_window_lattices,
    "bell_drum_towers": bell_drum_towers.build_bell_drum_towers,
    "government_offices": government_offices.build_government_offices,
    "lantern_festival": lantern_festival.build_lantern_festival,
    "ancestral_temple_altar": ancestral_temple_altar.build_ancestral_temple_altar,
    "academy_guozijian": academy_guozijian.build_guozijian,
    "suburb_farms": suburb_farms.build_suburb_farms,
    "farm_irrigation": farm_irrigation.build_farm_irrigation,
    "mountain_zhongnan": mountain_zhongnan.build_zhongnan_mountain,
    "terrain_longshou": terrain_longshou.build_longshou_elevation,
    "flowers_gardens": flowers_gardens.build_flowers_gardens,
    "temple_incense_banners": temple_incense_banners.build_temple_rituals,
    "tomb_spirit_way": tomb_spirit_way.build_tomb_spirit_way,
    "leyouyuan_stele": leyouyuan_stele.build_leyouyuan_details,
    "seasonal_vegetation": seasonal_vegetation.build_seasonal_vegetation,
}


def build_selected(fills: list[Fill], include: list[str] | None = None) -> None:
    selected = include if include else list(MODULES.keys())
    for name in selected:
        if name not in MODULES:
            raise ValueError(f"Unknown module: {name}. Available: {list(MODULES.keys())}")
        MODULES[name](fills)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build all fine-grained Chang'an modules.")
    parser.add_argument(
        "--include",
        type=str,
        default=None,
        help="Comma-separated module names to include. Default: all.",
    )
    # Re-use the common execution harness but with a custom builder.
    args, remaining = parser.parse_known_args()
    sys.argv = [sys.argv[0], *remaining]

    include = [m.strip() for m in args.include.split(",")] if args.include else None

    # The section name encodes which modules are included for the summary.
    section_name = "changan_build_all"
    if include:
        section_name += "(" + ",".join(include) + ")"

    run_builder(lambda f: build_selected(f, include), section_name)


if __name__ == "__main__":
    main()
