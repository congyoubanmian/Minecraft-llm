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
    add_hollow_box,
    add_staircase,
    run_builder,
)


"""
Zhuque Men (朱雀门) + Mingde Men (明德门) 3D enhancement pass.

An overlay pass that deepens the two great south gates built by
gate_zhuque_men.py (center 3000, 0) and gate_mingde_men.py (center 3000, -90)
with true 3D interiors:

- Gate passage interiors: stepped barrel-vault ring lining (拱券) inside the
  central gate tunnel, narrowing toward the crown, plus door-pivot stones
  (门枕石) and thresholds at both tunnel mouths.
- Portcullis (千斤闸): a half-lowered iron-bar grid hanging in the central
  passage, with a fence chain column rising through a floor shaft to a
  plank winch chamber (绞关室) hidden inside the gatehouse upper floor.
- Gate tower interior (城楼): the hollow gatehouse is floored with planks and
  split into two guard rooms with weapon racks, a guard table, and a
  mezzanine reached by an internal staircase.
- Wall access: an andesite staircase from the inner gate court up to the
  wall-top horse way (城墙马道) at the gatehouse base level (y=39 for
  Zhuque, y=35 for Mingde, matching each base tower's bottom).
- Barbican (瓮城) training ground: flag pole with red banner, two archery
  targets (white/red wool concentric squares on a log frame), weapon rack.
- Drawbridge (吊桥): a spruce plank deck over the moat band (z=-89..-43,
  on top of the existing stone bridge from moat_bridge_railings.py) with
  fence "chains" rising diagonally from the outer edge up to a lifting
  beam under the gate vault.
- Lantern posts at both mouths of each central passage.

Geometry aligned to the base modules:
    Zhuque Men: tower x 2950..3050 z -42..42 y 39..68 (wall 2 thick),
        central passage x 2996..3004 y 1..38 z -45..45, arch y 39..45,
        barbican x 2890..3110 z 80..200.
    Mingde Men: tower x 2930..3070 z -145..-35 y 35..72 (wall 3 thick),
        central passage x 2995..3005 y 1..34 z -150..-30, arch y 35..43,
        barbican x 2860..3140 z -270..-170.
"""

LOG_X = "minecraft:dark_oak_log[axis=x]"
LOG_Y = "minecraft:dark_oak_log[axis=y]"

# Moat band on the gate axis (from wall_battlement_moat / moat_bridge_railings).
MOAT_Z1, MOAT_Z2 = -89, -43

GATES = [
    {
        "name": "zhuque",
        "cx": 3000,
        "cz": 0,
        "hw": 4,                     # central passage half width
        "ptop": 38,                  # passage ceiling (arch starts above)
        "pz1": -45, "pz2": 45,       # passage tunnel z range
        "ix1": 2952, "ix2": 3048,    # gatehouse interior (tower shell inset)
        "iz1": -40, "iz2": 40,
        "floor_y": 41,               # plank floor on the tower shell base
        "rings": [-41, -30, -19, -8, 3, 14, 25, 36],
        "portcullis_z": 8,
        "wall_stair": (3056, 72, 3060, 35, 39),   # x1, z1, x2, z2, top y
        "flag": (2920, 120),
        "banner_dir": 1,
        "targets": [(2940, 160), (2970, 175)],
        "barbican_rack": (2898, 100),
        "tower_racks": [(3046, 20, 3046, 30), (2960, -38, 2980, -38)],
        "table": (3010, 24),
    },
    {
        "name": "mingde",
        "cx": 3000,
        "cz": -90,
        "hw": 5,
        "ptop": 34,
        "pz1": -150, "pz2": -30,
        "ix1": 2933, "ix2": 3067,
        "iz1": -142, "iz2": -38,
        "floor_y": 38,
        "rings": [-142, -131, -120, -109, -98, -87, -76, -65, -54, -43, -32],
        "portcullis_z": -100,
        "wall_stair": (3076, -2, 3080, -35, 35),
        "flag": (3080, -210),
        "banner_dir": -1,
        "targets": [(3060, -240), (3020, -255)],
        "barbican_rack": (3102, -190),
        "tower_racks": [(2935, -130, 2935, -120), (3010, -40, 3030, -40)],
        "table": (3040, -120),
    },
]


def _passage_vault(fills: list[Fill], cfg: dict) -> None:
    """Stepped barrel-vault rings inside the central tunnel, plus pivot stones."""
    name, cx = cfg["name"], cfg["cx"]
    hw, ptop = cfg["hw"], cfg["ptop"]
    pier_y1, step1_y1, step2_y1 = ptop - 12, ptop - 6, ptop - 2
    for rz in cfg["rings"]:
        # Side piers and two corbelled steps narrowing toward the crown.
        add_fill(fills, f"{name} vault {rz} pier w", (cx - hw, pier_y1, rz), (cx - hw + 1, ptop, rz + 1), M.STONE)
        add_fill(fills, f"{name} vault {rz} pier e", (cx + hw - 1, pier_y1, rz), (cx + hw, ptop, rz + 1), M.STONE)
        add_fill(fills, f"{name} vault {rz} step1 w", (cx - hw + 2, step1_y1, rz), (cx - hw + 2, ptop, rz + 1), M.DARK_BRICKS)
        add_fill(fills, f"{name} vault {rz} step1 e", (cx + hw - 2, step1_y1, rz), (cx + hw - 2, ptop, rz + 1), M.DARK_BRICKS)
        add_fill(fills, f"{name} vault {rz} step2 w", (cx - hw + 3, step2_y1, rz), (cx - hw + 3, ptop, rz + 1), M.DARK_BRICKS)
        add_fill(fills, f"{name} vault {rz} step2 e", (cx + hw - 3, step2_y1, rz), (cx + hw - 3, ptop, rz + 1), M.DARK_BRICKS)
        add_fill(fills, f"{name} vault {rz} crown", (cx - hw + 3, ptop + 1, rz), (cx + hw - 3, ptop + 1, rz + 1), M.DARK_BRICKS)
    # Pivot stones (门枕石) and thresholds at both tunnel mouths.
    for zm in (cfg["pz1"], cfg["pz2"]):
        zlo = zm + 1 if zm == cfg["pz1"] else zm - 2
        add_fill(fills, f"{name} pivot {zm} w", (cx - hw, 1, zlo), (cx - hw, 4, zlo + 1), M.DARK)
        add_fill(fills, f"{name} pivot {zm} e", (cx + hw, 1, zlo), (cx + hw, 4, zlo + 1), M.DARK)
        add_fill(fills, f"{name} threshold {zm}", (cx - hw, 2, zlo), (cx + hw, 2, zlo + 1), M.DARK)


def _portcullis_and_winch(fills: list[Fill], cfg: dict) -> None:
    """Half-lowered portcullis with chain up to a winch chamber in the tower."""
    name, cx = cfg["name"], cfg["cx"]
    hw, ptop, fy = cfg["hw"], cfg["ptop"], cfg["floor_y"]
    pz = cfg["portcullis_z"]
    bottom = ptop - 25
    # Iron-bar grid, wooden bottom rail and a cross brace.
    add_fill(fills, f"{name} portcullis bars", (cx - hw, bottom, pz), (cx + hw, ptop, pz), M.IRON_BARS)
    add_fill(fills, f"{name} portcullis rail", (cx - hw, bottom - 1, pz), (cx + hw, bottom - 1, pz), LOG_X)
    add_fill(fills, f"{name} portcullis brace", (cx - hw, bottom + 11, pz), (cx + hw, bottom + 11, pz), LOG_X)
    # Winch chamber on the gatehouse floor, shaft through the floor, chain, drum.
    add_hollow_box(fills, f"{name} winch chamber", cx - hw, fy + 1, pz - 5, cx + hw, fy + 9, pz + 5, M.WOOD, thickness=1)
    add_fill(fills, f"{name} winch shaft", (cx - 1, ptop + 1, pz - 1), (cx + 1, fy + 1, pz + 1), M.AIR)
    add_fill(fills, f"{name} winch chain", (cx, ptop + 1, pz), (cx, fy + 6, pz), M.FENCE)
    add_fill(fills, f"{name} winch drum", (cx - 2, fy + 7, pz - 2), (cx + 2, fy + 7, pz + 2), LOG_X)


def _gatehouse_rooms(fills: list[Fill], cfg: dict) -> None:
    """Plank floor, two guard rooms, racks, a guard table, mezzanine + stairs."""
    name, cx, cz = cfg["name"], cfg["cx"], cfg["cz"]
    ix1, ix2, iz1 = cfg["ix1"], cfg["ix2"], cfg["iz1"]
    fy = cfg["floor_y"]
    # Plank floor over the tower shell and a partition making two rooms.
    add_fill(fills, f"{name} tower plank floor", (ix1, fy, iz1), (ix2, fy, cfg["iz2"]), M.WOOD)
    add_fill(fills, f"{name} tower partition", (ix1, fy + 1, cz - 1), (ix2, fy + 8, cz + 1), M.WOOD)
    add_fill(fills, f"{name} tower partition door", (cx - 20, fy + 1, cz - 1), (cx - 16, fy + 4, cz + 1), M.AIR)
    # Weapon racks: fence posts with iron bars above.
    for index, (rx1, rz1, rx2, rz2) in enumerate(cfg["tower_racks"]):
        add_fill(fills, f"{name} rack {index} posts", (rx1, fy + 1, rz1), (rx2, fy + 2, rz2), M.FENCE)
        add_fill(fills, f"{name} rack {index} arms", (rx1, fy + 3, rz1), (rx2, fy + 5, rz2), M.IRON_BARS)
    # Guard table.
    tx, tz = cfg["table"]
    add_fill(fills, f"{name} guard table top", (tx, fy + 3, tz), (tx + 3, fy + 3, tz + 2), M.WOOD)
    add_fill(fills, f"{name} guard table leg w", (tx, fy + 1, tz), (tx, fy + 2, tz + 2), M.FENCE)
    add_fill(fills, f"{name} guard table leg e", (tx + 3, fy + 1, tz), (tx + 3, fy + 2, tz + 2), M.FENCE)
    # Mezzanine over the far room with four posts and an internal staircase.
    mz = fy + 13
    add_fill(fills, f"{name} mezzanine slab", (ix1 + 4, mz, iz1 + 2), (ix2 - 4, mz, cz - 13), M.WOOD)
    for px in (ix1 + 8, ix2 - 8):
        for pz in (iz1 + 6, cz - 17):
            add_fill(fills, f"{name} mezzanine post {px},{pz}", (px, fy + 1, pz), (px, mz - 1, pz), M.LOG)
    add_staircase(
        fills, f"{name} mezzanine stair",
        ix1 + 2, cz - 2,
        ix1 + 4, cz - 14,
        fy + 1, mz,
        "south",
        block=M.SMOOTH,
    )


def _wall_access_stair(fills: list[Fill], cfg: dict) -> None:
    """Staircase from the inner gate court up to the wall-top horse way."""
    name = cfg["name"]
    sx1, sz1, sx2, sz2, top_y = cfg["wall_stair"]
    add_staircase(fills, f"{name} wall horse way stair", sx1, sz1, sx2, sz2, 2, top_y, "south", block=M.ANDESITE)
    add_fill(fills, f"{name} wall stair landing", (sx1, top_y, sz2 - 2), (sx2, top_y, sz2), M.ANDESITE)


def _barbican_training(fills: list[Fill], cfg: dict) -> None:
    """Flag pole with banner, archery targets, and a weapon rack in the barbican."""
    name = cfg["name"]
    fx, fz = cfg["flag"]
    add_fill(fills, f"{name} flag pole", (fx, 2, fz), (fx, 22, fz), M.FENCE)
    d = cfg["banner_dir"]
    add_fill(fills, f"{name} flag banner", (min(fx + d, fx + 3 * d), 19, fz), (max(fx + d, fx + 3 * d), 20, fz), M.RED_WOOL)
    for index, (tx, tz) in enumerate(cfg["targets"]):
        add_fill(fills, f"{name} target {index} stand", (tx + 3, 1, tz), (tx + 3, 2, tz), M.FENCE)
        add_fill(fills, f"{name} target {index} frame t", (tx, 9, tz), (tx + 6, 9, tz), M.LOG)
        add_fill(fills, f"{name} target {index} frame b", (tx, 3, tz), (tx + 6, 3, tz), M.LOG)
        add_fill(fills, f"{name} target {index} frame w", (tx, 4, tz), (tx, 8, tz), M.LOG)
        add_fill(fills, f"{name} target {index} frame e", (tx + 6, 4, tz), (tx + 6, 8, tz), M.LOG)
        add_fill(fills, f"{name} target {index} white", (tx + 1, 4, tz), (tx + 5, 8, tz), M.WHITE_WOOL)
        add_fill(fills, f"{name} target {index} red", (tx + 2, 5, tz), (tx + 4, 7, tz), M.RED_WOOL)
        add_fill(fills, f"{name} target {index} heart", (tx + 3, 6, tz), (tx + 3, 6, tz), M.WHITE_WOOL)
    rx, rz = cfg["barbican_rack"]
    add_fill(fills, f"{name} barbican rack posts", (rx, 2, rz), (rx, 3, rz + 10), M.FENCE)
    add_fill(fills, f"{name} barbican rack arms", (rx, 4, rz), (rx, 5, rz + 10), M.IRON_BARS)


def _drawbridge(fills: list[Fill], cfg: dict) -> None:
    """Plank drawbridge over the moat with diagonal fence chains to the vault."""
    name, cx, ptop = cfg["name"], cfg["cx"], cfg["ptop"]
    add_fill(fills, f"{name} drawbridge deck", (cx - 6, 4, MOAT_Z1), (cx + 6, 4, MOAT_Z2), M.SPRUCE)
    for x in (cx - 5, cx + 5):
        for i in range(9):
            z, y = -86 + 4 * i, 5 + 3 * i
            add_fill(fills, f"{name} drawbridge chain {x} {i}", (x, y, z), (x, y, z + 3), M.FENCE)
    # Lifting beam across the chain tops and an anchor log up to the vault.
    add_fill(fills, f"{name} drawbridge beam", (cx - 5, 30, -54), (cx + 5, 30, -52), LOG_X)
    add_fill(fills, f"{name} drawbridge anchor", (cx - 1, 30, -54), (cx + 1, ptop, -52), LOG_Y)


def _mouth_lanterns(fills: list[Fill], cfg: dict) -> None:
    """Lantern posts flanking both mouths of the central passage."""
    name, cx, hw = cfg["name"], cfg["cx"], cfg["hw"]
    for zm in (cfg["pz1"], cfg["pz2"]):
        zo = zm - 2 if zm == cfg["pz1"] else zm + 2
        for x in (cx - hw - 3, cx + hw + 3):
            add_fill(fills, f"{name} lamp post {x},{zo}", (x, 1, zo), (x, 5, zo), M.FENCE)
            add_fill(fills, f"{name} lamp {x},{zo}", (x, 6, zo), (x, 6, zo), M.LANTERN)


def _deepen_gate(fills: list[Fill], cfg: dict) -> None:
    _passage_vault(fills, cfg)
    _portcullis_and_winch(fills, cfg)
    _gatehouse_rooms(fills, cfg)
    _wall_access_stair(fills, cfg)
    _barbican_training(fills, cfg)
    _drawbridge(fills, cfg)
    _mouth_lanterns(fills, cfg)


def build_gates_south_3d(fills: list[Fill]) -> None:
    for cfg in GATES:
        _deepen_gate(fills, cfg)


def main() -> None:
    run_builder(build_gates_south_3d, "gates_south_3d")


if __name__ == "__main__":
    main()
