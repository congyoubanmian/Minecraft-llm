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
    add_eave_bells,
    add_fill,
    add_pixel_mural,
    run_builder,
)


"""
Gate & Wall Detail 3D (城墙城门细节深化叠加) - a pure overlay-detail pass
that adorns the already-built city gates, walls and towers. Every fill
sits on or one block in front of an existing surface; nothing is cleared
and no gate interior is touched.

Deepened objects (all coordinates derived from the source modules):
    1. Gate stone plaques (城门石匾) - quartz-on-deepslate pixel murals
       hung directly above the central gate arches:
       Zhuque Men (gate_zhuque_men.py: tower x 2950..3050 z -42..42,
       central passage x 2996..3004, arch crown y=45, outer face z=-42),
       bed plaque at z=-43, y 46..51.
       Mingde Men (gate_mingde_men.py: tower x 2930..3070 z -145..-35,
       central passage x 2995..3005, arch crown y=43, outer face z=-145),
       bed plaque at z=-146, y 44..49 (below the old gold board y 58..64).
    2. "Chang'an" bastion inscription (长安堡铭) - 20x8 mural on the
       outer face (z=-10) of the south-wall watch tower at x=4200
       (wall_battlement_moat.py watch towers every 300; x=4200 aligns
       with the west edge of the East Market zone x 4200..5300).
    3. Stone-drop hole grids (礌石孔) on the outer faces of the four
       double-storey enemy towers (wall_dilou_3d.py TOWERS s/n 1350/4350:
       storey-1 y 40..49, outer faces z=-4 / z=6003) and four south-wall
       watch towers (pos 900/1800/3300/4800, outer face z=-10, y 1..50),
       each with an embedded sea lantern and a two-step stone drip eave.
    4. Battlement flag stations (垛口旗台) on the y=39 wall-top deck
       (wall_battlement_moat.py; deck z 0..33 south / 5966..5999 north),
       positioned clear of the gates (x 2950..3050, 1164..1236, ...),
       the enemy towers (x 1338..1362, 4338..4362) and the horse-way
       ramp heads (x 1494..1506, 4494..4506).
    5. Passage niche lamps (门洞壁龛灯) flush-mounted in the tunnel side
       walls of all five passages of both gates (zhuque walls at x=gx±5,
       mingde walls at x=gx±6, z=41 / z=-34 near the inner mouths),
       avoiding the gates_south_3d.py portcullis (z=8 / z=-100), vault
       rings (z -41..36 / -142..-32) and the winch chambers.
    6. Corner-tower wind bells + rooftop balustrade - four towers
       (wall_corner_tower.py TOWERS (80,80)..(5920,5920)): bells under
       the eave slab ring (y=58) at the four eave corners, and a
       post_every=6 balustrade ring around the beacon platform
       (y 67..72) with its rail at y=73.
    7. Horse-way stelae (登城马道碑) beside the ramp feet of the two
       south-wall horse ways (rampart_horse_way.py HORSE_WAYS at
       x=1500/4500, ramps z -24..-1, rails at x=1495/1505 and 4495/4505).

Distinctive features (English):
    - Hand-designed 16x6 quartz-on-deepslate pixel plaques spelling
      "朱雀门" / "明德门" with gold seal corners, hung square above the
      central gate arches - the calling-card inscriptions of the capital.
    - A monumental 20x8 "长安" bastion inscription in quartz with gold
      seal corners, the largest piece of wall calligraphy in the city.
    - Murder-hole style stone-drop grids (2x3 iron bars each) with an
      embedded glowing sea lantern and stepped smooth-stone drip eaves
      on every enemy-tower outer face.
    - Red banner flag stations marched along the battlement line, gold
      wind bells under every corner-tower eave, quartz stelae marking
      the mounted ramps, and sea-lantern niche lamps lining each gate
      passage.
"""

QUARTZ_PILLAR = "minecraft:quartz_pillar[axis=y]"

# Pixel palette shared by the plaques and the bastion inscription.
_PLAQUE_PALETTE = {"#": M.QUARTZ, "@": M.GOLD}

# 4x6 glyph strokes (top row first) for the two gate plaques.
_ZHU = [".##.", "####", ".##.", "####", ".##.", "#..#"]
_QUE = ["#..#", ".##.", "####", ".##.", "####", "#..#"]
_MEN = ["####", "#..#", "#..#", "#..#", "#..#", "#.##"]
_MING = ["####", "#..#", "####", "#..#", "#..#", "##.."]
_DE = ["#..#", "####", "#.##", "#.##", "####", "####"]

# 8x8 glyph strokes for the 20x8 "长安" bastion inscription.
_CHANG = [
    "...##...",
    "...##...",
    ".######.",
    "...##...",
    "...##...",
    "..##....",
    ".##...##",
    ".#.....#",
]
_AN = [
    "...##...",
    ".######.",
    "#......#",
    ".#....#.",
    ".#....#.",
    "..#..#..",
    ".######.",
    ".#....#.",
]


def _seal_frame(left: list[str], mid: list[str], right: list[str]) -> list[str]:
    """Compose three 4x6 glyphs into a 16x6 plaque with gold seal corners."""
    rows = []
    for i in range(6):
        cap = "@" if i in (0, 5) else "."
        rows.append(cap + left[i] + "." + mid[i] + "." + right[i] + cap)
    assert all(len(row) == 16 for row in rows)
    return rows


def _changan_rows() -> list[str]:
    """Compose the two 8x8 glyphs into a 20x8 inscription with seal corners."""
    rows = []
    for i in range(8):
        cap = "@" if i in (0, 7) else "."
        rows.append(cap + _CHANG[i] + ".." + _AN[i] + cap)
    assert all(len(row) == 20 for row in rows)
    return rows


# ---------------------------------------------------------------------------
# Section coordinates.
# ---------------------------------------------------------------------------
# Outer faces of the four double-storey enemy towers (wall_dilou_3d.py):
# (centre_x, face_z, lamp_z, drip eave z near, drip eave z far).
_DILOU_FACES = [
    (1350, -4, -3, -5, -6),
    (4350, -4, -3, -5, -6),
    (1350, 6003, 6002, 6004, 6005),
    (4350, 6003, 6002, 6004, 6005),
]
_DROP_ROWS = (43, 44, 45)

# South-wall watch towers (wall_battlement_moat.py) that also get a
# drop-hole grid; outer face z=-10, lamp embedded at z=-9.
_WATCH_DROP_POS = (900, 1800, 3300, 4800)

# Flag stations on the wall-top decks (south deck z~20, north deck z~5975).
_FLAG_SOUTH_X = (600, 1400, 2200, 3400, 5000)
_FLAG_NORTH_X = (1000, 2600, 4600)

# The five gate passages of each south gate (gate_*.py passage loops).
_ZHUQUE_PASSAGES = (2968, 2984, 3000, 3016, 3032)
_MINGDE_PASSAGES = (2952, 2976, 3000, 3024, 3048)

# Corner watch towers (wall_corner_tower.py).
_CORNER_TOWERS = ((80, 80), (80, 5920), (5920, 80), (5920, 5920))

# Stele spots beside the two south-wall horse-way ramp feet.
_STELAE = ((1491, -22), (4509, -22))


# ---------------------------------------------------------------------------
# Build sections.
# ---------------------------------------------------------------------------
def _gate_plaques_and_inscription(fills: list[Fill]) -> None:
    """城门石匾 + 长安堡铭: pixel murals over the two gate arches and on
    the bastion west of the East Market."""
    # Zhuque Men: bed one block proud of the outer face z=-42, right
    # above the central arch crown (y=45).
    add_fill(fills, "gatewall zhuque plaque bed", (2992, 46, -43), (3007, 51, -43), M.DARK)
    add_pixel_mural(
        fills, "gatewall zhuque plaque",
        _seal_frame(_ZHU, _QUE, _MEN), _PLAQUE_PALETTE,
        2992, 51, -43, axis="x",
    )
    # Mingde Men: bed one block proud of the outer face z=-145, tucked
    # below the existing gold board (y 58..64).
    add_fill(fills, "gatewall mingde plaque bed", (2992, 44, -146), (3007, 49, -146), M.DARK)
    add_pixel_mural(
        fills, "gatewall mingde plaque",
        _seal_frame(_MING, _DE, _MEN), _PLAQUE_PALETTE,
        2992, 49, -146, axis="x",
    )
    # Bastion inscription on the x=4200 south-wall watch tower.
    add_fill(fills, "gatewall changan inscription bed", (4190, 37, -11), (4209, 44, -11), M.DARK)
    add_pixel_mural(
        fills, "gatewall changan inscription",
        _changan_rows(), _PLAQUE_PALETTE,
        4190, 44, -11, axis="x",
    )


def _enemy_tower_drop_holes(fills: list[Fill]) -> None:
    """马面礌石孔: 2x3 iron-bar drop grids with an embedded sea lantern
    plus a two-step smooth-stone drip eave on every enemy-tower face."""
    for cx, fz, lz, ez1, ez2 in _DILOU_FACES:
        for col in (cx - 3, cx + 2):
            for row in _DROP_ROWS:
                add_fill(
                    fills, f"gatewall dilou drop bar {col},{row}",
                    (col, row, fz), (col, row, fz), M.IRON_BARS,
                )
        add_fill(fills, f"gatewall dilou drop lamp {cx}", (cx, 44, lz), (cx, 44, lz), M.SEA_LANTERN)
        add_fill(fills, f"gatewall dilou drip eave 1 {cx}", (cx - 5, 42, ez1), (cx + 4, 42, ez1), M.SMOOTH)
        add_fill(fills, f"gatewall dilou drip eave 2 {cx}", (cx - 4, 41, ez2), (cx + 3, 41, ez2), M.SMOOTH)
    for pos in _WATCH_DROP_POS:
        for col in (pos - 3, pos + 2):
            for row in (44, 45, 46):
                add_fill(
                    fills, f"gatewall watch drop bar {col},{row}",
                    (col, row, -10), (col, row, -10), M.IRON_BARS,
                )
        add_fill(fills, f"gatewall watch drop lamp {pos}", (pos, 45, -9), (pos, 45, -9), M.SEA_LANTERN)
        add_fill(fills, f"gatewall watch drip eave 1 {pos}", (pos - 5, 43, -11), (pos + 4, 43, -11), M.SMOOTH)
        add_fill(fills, f"gatewall watch drip eave 2 {pos}", (pos - 4, 42, -12), (pos + 3, 42, -12), M.SMOOTH)


def _flag_station(fills: list[Fill], x: int, z: int) -> None:
    """One flag station: stone pier, 10-tall log pole, three-segment
    red banner."""
    add_fill(fills, f"gatewall flag pier {x}", (x, 40, z - 1), (x + 1, 40, z), M.SMOOTH)
    add_fill(fills, f"gatewall flag pole {x}", (x + 1, 41, z), (x + 1, 50, z), M.LOG)
    for seg, fy in enumerate((50, 49, 48)):
        add_fill(fills, f"gatewall flag banner {x} seg {seg}", (x + 2, fy, z), (x + 4, fy, z), M.RED_WOOL)


def _battlement_flag_stations(fills: list[Fill]) -> None:
    """垛口旗台: eight flag stations along the wall-top decks."""
    for x in _FLAG_SOUTH_X:
        _flag_station(fills, x, 20)
    for x in _FLAG_NORTH_X:
        _flag_station(fills, x, 5975)


def _passage_niche_lamps(fills: list[Fill]) -> None:
    """门洞壁龛灯: three flush sea-lantern niches with a dark stone
    lintel on both side walls of every gate passage."""
    for gx in _ZHUQUE_PASSAGES:
        for wx in (gx - 5, gx + 5):
            add_fill(fills, f"gatewall zhuque niche lamps {gx},{wx}", (wx, 6, 41), (wx, 8, 41), M.SEA_LANTERN)
            add_fill(fills, f"gatewall zhuque niche lintel {gx},{wx}", (wx, 9, 41), (wx, 9, 41), M.DARK)
    for gx in _MINGDE_PASSAGES:
        for wx in (gx - 6, gx + 6):
            add_fill(fills, f"gatewall mingde niche lamps {gx},{wx}", (wx, 6, -34), (wx, 8, -34), M.SEA_LANTERN)
            add_fill(fills, f"gatewall mingde niche lintel {gx},{wx}", (wx, 9, -34), (wx, 9, -34), M.DARK)


def _corner_tower_bells_and_rails(fills: list[Fill]) -> None:
    """角楼风铃 + 望柱栏板: four bells under each eave corner and a
    balustrade ring around the beacon platform on the tower top."""
    for cx, cz in _CORNER_TOWERS:
        add_eave_bells(
            fills, f"gatewall corner bells {cx},{cz}",
            [
                (cx - 35, 56, cz - 35),
                (cx + 35, 56, cz - 35),
                (cx - 35, 56, cz + 35),
                (cx + 35, 56, cz + 35),
            ],
        )
        # Beacon platform spans y 67..72; rail rests on its rim at y=73.
        add_balustrade(
            fills, f"gatewall corner rail {cx},{cz}",
            cx - 3, cz - 3, cx + 3, cz + 3, 73,
            post_block=M.RED_WALL, head_block=M.WHITE_TERRACOTTA,
            post_every=6,
        )


def _horse_way_stelae(fills: list[Fill]) -> None:
    """登城马道碑: quartz stele with gold cap on a dark stone base beside
    each south-wall ramp entrance."""
    for sx, sz in _STELAE:
        add_fill(fills, f"gatewall horseway stele base {sx}", (sx, 1, sz), (sx, 1, sz), M.DARK)
        add_fill(fills, f"gatewall horseway stele shaft {sx}", (sx, 2, sz), (sx, 4, sz), QUARTZ_PILLAR)
        add_fill(fills, f"gatewall horseway stele cap {sx}", (sx, 5, sz), (sx, 5, sz), M.GOLD)


def build_gate_wall_detail_3d(fills: list[Fill]) -> None:
    _gate_plaques_and_inscription(fills)
    _enemy_tower_drop_holes(fills)
    _battlement_flag_stations(fills)
    _passage_niche_lamps(fills)
    _corner_tower_bells_and_rails(fills)
    _horse_way_stelae(fills)


def main() -> None:
    run_builder(build_gate_wall_detail_3d, "gate_wall_detail_3d")


if __name__ == "__main__":
    main()
