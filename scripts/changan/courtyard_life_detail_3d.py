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
    add_outline,
    run_builder,
)


"""
Courtyard Life Detail 3D (长安院落生活气息·生活小品叠加) - add-only overlay
that scatters Tang daily-life props through the courtyards of five major
compounds (太极宫 / 国子监 / 都亭驿 / 太医署 / 王府官邸), turning the bare
architectural model into a city where people live. Strictly additive: every
fill places new props into verified empty courtyard ground, door forecourts
or wall corners; nothing is cleared.

Prop distribution (小品分布清单, coordinate provenance per source file):
    - Taiji Palace (imperial_taiji_palace.py, plot x 2400..3600 / z 4800..5800,
      mid_x=3000, ground top y0 so props base y1): huabiao pair flanking the
      axis at z 4770 in the empty band between Chengtian Gate (z 4715..4725)
      and the Danfeng arch (z 4792..4808, street_facilities.py); sundial at
      (3120, 4940) east of the axis and north of the Taiji Hall terrace
      (z 5020); censer on axis (3000, 5005) standing directly on the zhuque
      median paving (street_facilities.py, x 2994..3006 at y3, so base y4),
      clear of the median lamps (z 4980/5080); fire vats (2860 / 3140, 5040)
      beside the hall platform (x 2890..3110); well at (2600, 5200), clear of
      the rockery/garden belts that start at z 5500 (garden_rockery.py).
    - Guozijian (academy_guozijian.py, x 1600..2200 / z 4200..4700, mid_x=1900,
      props base y1): sundial at (1745, 4240) west of the x=1800 avenue paving
      (road body x 1772..1828, road_paving.py); censer inside Lingxing Gate at
      (1900, 4218) between the gate (z <= 4206) and Biyong pond (z 4280); fire
      vats (1845 / 1980, 4390) north of the Confucius hall (z 4400); well at
      (2070, 4440) east of the avenue, clear of the plum garden
      (x 1630..1720, z 4400..4520, flowers_gardens.py) and lecture hall 1
      (x 1965..2035).
    - Douting Post (douting_post_3d.py, x 3450..3750 / z 1500..1800, graded
      grass top y3 so props base y4): censer on the entrance axis (3600, 1676)
      in the strip between the cross path (z 1658) and the Document Hall
      terrace (z 1692); fire vat (3670, 1678); lantern strings hung under the
      guest-room eaves at x 3489 / 3711 (roof lines y9), z 1545..1569 step 6,
      offset off the door bays (z 1548..1550 etc.); hitching-stone +
      mounting-block pairs outside the gate at (3530 / 3670, 1505), clear of
      the existing hitch posts (x 3550..3650).
    - Taiyiyuan (taiyiyuan_3d.py, x 3550..3850 / z 900..1250, props base y4):
      censer on the axis path (3690, 1075) south of the lecture-hall terrace
      (z 1092); two lantern gates beams across the axis at z 980 / 1060
      between the west and east herb-garden fences (x <= 3653 / x >= 3726).
    - Official residences (official_residence.py RESIDENCES list - the task's
      "OFFICES"; ground top y0, props base y1): Qin Wang Fu (2200, 3600):
      censer inside the gate (2200, 3532) between gate (z 3524) and screen
      (z 3540), fire vat (2160, 3552) west of the screen, hitching pair
      (2150 / 2250, 3505) outside the gate. Brick-carved screen-wall carvings
      (砖雕影壁) overlaid onto the existing plain screen slabs of Qi Wang Fu
      (cx 3800) and Wei Guo Gong (cx 2600) on their gate-facing faces
      (z 3539 / z 3139).

Distinctive features:
    - Pair of quartz huabiao columns (12 tall) flanking the Taiji Palace
      axis, each with two pairs of projecting wood cloud boards, a smooth
      stone cap and a crouching gold lion on top
    - Two stone sundials: two-tier smooth-stone pedestals, tilted dial plates
      made of two opposed quartz stairs, iron-bar gnomons with leaning tips
      and quartz hour markers
    - Five bronze tripod censers: iron-bar legs, smooth-stone ding bodies,
      gold twin ears and three staggered white-wool smoke puffs
    - Eave-hung lantern strings (fence drop chain + red-wool shade +
      sea-lantern light) in the Douting lanes plus two beam lantern gates
      strung across the Taiyiyuan axis path
    - Six mossy-stone ring fire vats (太平缸) with water and fence lid racks
      standing on smooth-stone aprons
    - Two brick-carved yingbi screens: deepslate frames and medallion grounds
      carrying a quartz flying-crane relief on the white residence walls
    - Four smooth-stone hitching posts paired with two-tier quartz mounting
      blocks at the residence and post-station gates
    - Two stone wells with windlass posts, log crossbar, fence crank handle,
      iron-bar rope and a quartz bucket
"""

# ---------------------------------------------------------------------------
# Direct-string blocks / states used by this module.
# ---------------------------------------------------------------------------
LOG_X = "minecraft:dark_oak_log[axis=x]"
QUARTZ_PILLAR_Y = "minecraft:quartz_pillar[axis=y]"

# Flying-crane relief (鹤纹) for the carved screens; '.' leaves the ground.
_CRANE_ART = (
    ".Q...Q.",
    ".QQ.QQ.",
    "..QQQ..",
    "...Q...",
    "..Q.Q..",
)


# ---------------------------------------------------------------------------
# Prop helpers.
# ---------------------------------------------------------------------------
def _quartz_stair(facing: str) -> str:
    """Directional bottom quartz stair used for tilted dial plates."""
    return (
        "minecraft:quartz_stairs"
        f"[facing={facing},half=bottom,shape=straight,waterlogged=false]"
    )


def _censer(fills: list[Fill], label: str, cx: int, cz: int, y: int) -> None:
    """Bronze tripod censer (三足香炉): pad, plinth, legs, ding, ears, smoke."""
    add_fill(fills, f"{label} pad", (cx - 2, y, cz - 2), (cx + 2, y, cz + 2), M.SMOOTH)
    add_fill(fills, f"{label} plinth", (cx - 1, y + 1, cz - 1), (cx + 1, y + 1, cz + 1), M.ANDESITE)
    for lx, lz in ((cx - 1, cz - 1), (cx + 1, cz - 1), (cx, cz + 1)):
        add_fill(fills, f"{label} leg {lx},{lz}", (lx, y + 2, lz), (lx, y + 3, lz), M.IRON_BARS)
    add_fill(fills, f"{label} body", (cx - 1, y + 4, cz - 1), (cx + 1, y + 5, cz + 1), M.SMOOTH)
    add_fill(fills, f"{label} ear w", (cx - 1, y + 6, cz), (cx - 1, y + 6, cz), M.GOLD)
    add_fill(fills, f"{label} ear e", (cx + 1, y + 6, cz), (cx + 1, y + 6, cz), M.GOLD)
    # Three staggered smoke puffs drifting off the mouth.
    add_fill(fills, f"{label} smoke 1", (cx, y + 6, cz), (cx, y + 7, cz), M.WHITE_WOOL)
    add_fill(fills, f"{label} smoke 2", (cx, y + 8, cz), (cx, y + 8, cz), M.WHITE_WOOL)
    add_fill(fills, f"{label} smoke 3", (cx + 1, y + 9, cz), (cx + 1, y + 9, cz), M.WHITE_WOOL)


def _sundial(fills: list[Fill], label: str, cx: int, cz: int, y: int) -> None:
    """Stone sundial (日晷): two-tier pedestal, tilted quartz dial, bar gnomon."""
    add_fill(fills, f"{label} apron", (cx - 3, y, cz - 3), (cx + 3, y, cz + 3), M.SMOOTH)
    add_fill(fills, f"{label} pedestal base", (cx - 2, y + 1, cz - 2), (cx + 2, y + 1, cz + 2), M.SMOOTH)
    add_fill(fills, f"{label} pedestal top", (cx - 1, y + 2, cz - 1), (cx + 1, y + 2, cz + 1), M.SMOOTH)
    # Dial plate: two quartz stairs stepping up toward the north edge.
    add_fill(fills, f"{label} dial south", (cx, y + 3, cz), (cx, y + 3, cz), _quartz_stair("north"))
    add_fill(fills, f"{label} dial north", (cx, y + 4, cz - 1), (cx, y + 4, cz - 1), _quartz_stair("north"))
    # Gnomon: iron bars rising from the high edge, tip leaning north.
    add_fill(fills, f"{label} gnomon", (cx, y + 5, cz - 1), (cx, y + 6, cz - 1), M.IRON_BARS)
    add_fill(fills, f"{label} gnomon tip", (cx, y + 7, cz - 2), (cx, y + 7, cz - 2), M.IRON_BARS)
    # Hour markers on the apron.
    add_fill(fills, f"{label} marker n", (cx, y + 1, cz - 3), (cx, y + 1, cz - 3), M.QUARTZ)
    add_fill(fills, f"{label} marker s", (cx, y + 1, cz + 3), (cx, y + 1, cz + 3), M.QUARTZ)


def _huabiao(fills: list[Fill], label: str, cx: int, cz: int, y: int) -> None:
    """Ornamental column (华表): base, quartz shaft, cloud boards, lion cap."""
    add_fill(fills, f"{label} base", (cx - 1, y, cz - 1), (cx + 1, y, cz + 1), M.ANDESITE)
    add_fill(fills, f"{label} shaft", (cx, y + 1, cz), (cx, y + 12, cz), QUARTZ_PILLAR_Y)
    # Two pairs of short wood cloud boards crossing the shaft.
    add_fill(fills, f"{label} cloud board w1", (cx - 2, y + 5, cz), (cx - 1, y + 5, cz), M.WOOD)
    add_fill(fills, f"{label} cloud board e1", (cx + 1, y + 5, cz), (cx + 2, y + 5, cz), M.WOOD)
    add_fill(fills, f"{label} cloud board w2", (cx - 2, y + 8, cz), (cx - 1, y + 8, cz), M.WOOD)
    add_fill(fills, f"{label} cloud board e2", (cx + 1, y + 8, cz), (cx + 2, y + 8, cz), M.WOOD)
    add_fill(fills, f"{label} cap", (cx - 1, y + 13, cz), (cx + 1, y + 13, cz), M.SMOOTH)
    # Crouching gold lion on the cap.
    add_fill(fills, f"{label} lion", (cx, y + 14, cz), (cx, y + 15, cz), M.GOLD)


def _lantern_string(fills: list[Fill], label: str, x: int, z: int, y_top: int) -> None:
    """One hanging lantern: fence chain, red-wool shade, sea-lantern light."""
    add_fill(fills, f"{label} chain", (x, y_top, z), (x, y_top, z), M.FENCE)
    add_fill(fills, f"{label} shade", (x, y_top - 1, z), (x, y_top - 1, z), M.RED_WOOL)
    add_fill(fills, f"{label} light", (x, y_top - 2, z), (x, y_top - 2, z), M.SEA_LANTERN)


def _lantern_gate(fills: list[Fill], label: str, z: int, x1: int, x2: int) -> None:
    """Beam gate across a path with three lantern strings hung beneath."""
    add_fill(fills, f"{label} post w", (x1, 4, z), (x1, 10, z), M.LOG)
    add_fill(fills, f"{label} post e", (x2, 4, z), (x2, 10, z), M.LOG)
    add_fill(fills, f"{label} beam", (x1, 10, z), (x2, 10, z), LOG_X)
    for sx in (x1 + 8, (x1 + x2) // 2, x2 - 8):
        _lantern_string(fills, f"{label} string {sx}", sx, z, 9)


def _fire_vat(fills: list[Fill], label: str, cx: int, cz: int, y: int) -> None:
    """Fire-fighting vat (太平缸): apron, mossy ring, water, fence lid rack."""
    add_fill(fills, f"{label} apron", (cx - 1, y, cz - 1), (cx + 1, y, cz + 1), M.SMOOTH)
    add_outline(fills, f"{label} ring", cx - 1, cz - 1, cx + 1, cz + 1, y + 1, y + 2, M.MOSS_STONE)
    add_fill(fills, f"{label} water", (cx, y + 2, cz), (cx, y + 2, cz), M.WATER)
    add_fill(fills, f"{label} rack x", (cx - 1, y + 3, cz), (cx + 1, y + 3, cz), M.FENCE)
    add_fill(fills, f"{label} rack z", (cx, y + 3, cz - 1), (cx, y + 3, cz + 1), M.FENCE)


def _hitch_set(fills: list[Fill], label: str, x: int, z: int, y: int, side: int) -> None:
    """Hitching stone (拴马石) post + two-tier quartz mounting block (上马石)."""
    add_fill(fills, f"{label} post", (x, y, z), (x, y + 3, z), M.SMOOTH)
    add_fill(fills, f"{label} block low", (x + 2 * side, y, z - 1), (x + 3 * side, y, z + 1), M.QUARTZ)
    add_fill(fills, f"{label} block top", (x + 2 * side, y + 1, z), (x + 3 * side, y + 1, z), M.QUARTZ)


def _well(fills: list[Fill], label: str, cx: int, cz: int, y: int) -> None:
    """Well with windlass (水井·辘轳): curb, water, posts, bar, crank, rope."""
    add_fill(fills, f"{label} apron", (cx - 2, y, cz - 2), (cx + 2, y, cz + 2), M.SMOOTH)
    add_outline(fills, f"{label} curb", cx - 1, cz - 1, cx + 1, cz + 1, y + 1, y + 2, M.STONE)
    add_fill(fills, f"{label} water", (cx, y + 1, cz), (cx, y + 1, cz), M.WATER)
    add_fill(fills, f"{label} post w", (cx - 2, y + 1, cz), (cx - 2, y + 4, cz), M.LOG)
    add_fill(fills, f"{label} post e", (cx + 2, y + 1, cz), (cx + 2, y + 4, cz), M.LOG)
    add_fill(fills, f"{label} bar", (cx - 2, y + 4, cz), (cx + 2, y + 4, cz), LOG_X)
    add_fill(fills, f"{label} crank", (cx + 3, y + 4, cz), (cx + 3, y + 5, cz), M.FENCE)
    add_fill(fills, f"{label} rope", (cx, y + 2, cz), (cx, y + 3, cz), M.IRON_BARS)
    add_fill(fills, f"{label} bucket", (cx - 2, y + 1, cz + 1), (cx - 2, y + 1, cz + 1), M.QUARTZ)


def _screen_carving(fills: list[Fill], label: str, cx: int, face_z: int, base_y: int) -> None:
    """Brick-carved yingbi relief on a gate-facing screen wall plane.

    Deepslate frame + dark medallion ground with a quartz flying-crane
    pattern, all one block proud of the existing white screen face.
    """
    add_fill(fills, f"{label} frame top", (cx - 5, base_y + 7, face_z), (cx + 5, base_y + 7, face_z), M.DARK)
    add_fill(fills, f"{label} frame bottom", (cx - 5, base_y, face_z), (cx + 5, base_y, face_z), M.DARK)
    add_fill(fills, f"{label} frame w", (cx - 5, base_y + 1, face_z), (cx - 5, base_y + 6, face_z), M.DARK)
    add_fill(fills, f"{label} frame e", (cx + 5, base_y + 1, face_z), (cx + 5, base_y + 6, face_z), M.DARK)
    add_fill(fills, f"{label} medallion", (cx - 3, base_y + 2, face_z), (cx + 3, base_y + 6, face_z), M.DARK)
    # Quartz crane relief, drawn row by row as contiguous runs.
    for r, row in enumerate(_CRANE_ART):
        yy = base_y + 6 - r
        run_start = None
        for c, ch in enumerate(row):
            if ch == "Q" and run_start is None:
                run_start = c
            if ch != "Q" and run_start is not None:
                add_fill(
                    fills, f"{label} crane r{r} c{run_start}",
                    (cx - 3 + run_start, yy, face_z), (cx - 3 + c - 1, yy, face_z), M.QUARTZ,
                )
                run_start = None
        if run_start is not None:
            add_fill(
                fills, f"{label} crane r{r} c{run_start}",
                (cx - 3 + run_start, yy, face_z), (cx - 3 + len(row) - 1, yy, face_z), M.QUARTZ,
            )


# ---------------------------------------------------------------------------
# Main builder.
# ---------------------------------------------------------------------------
def build_courtyard_life_detail_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Sundials (日晷): Guozijian courtyard west of the avenue, and the
    #    Taiji Palace east court.
    # ------------------------------------------------------------------
    _sundial(fills, "courtlife sundial guozijian", 1745, 4240, 1)
    _sundial(fills, "courtlife sundial taiji", 3120, 4940, 1)

    # ------------------------------------------------------------------
    # 2. Bronze censers (香炉): one inside the gate of each compound,
    #    on the entrance axis in front of the main hall.
    # ------------------------------------------------------------------
    _censer(fills, "courtlife censer guozijian", 1900, 4218, 1)
    _censer(fills, "courtlife censer taiji", 3000, 5005, 4)
    _censer(fills, "courtlife censer douting", 3600, 1676, 4)
    _censer(fills, "courtlife censer taiyi", 3690, 1075, 4)
    _censer(fills, "courtlife censer qinfu", 2200, 3532, 1)

    # ------------------------------------------------------------------
    # 3. Huabiao pair (华表) flanking the axis inside Chengtian Gate.
    # ------------------------------------------------------------------
    _huabiao(fills, "courtlife huabiao taiji w", 2930, 4770, 1)
    _huabiao(fills, "courtlife huabiao taiji e", 3070, 4770, 1)

    # ------------------------------------------------------------------
    # 4. Lantern strings (灯笼串): guest-room eaves in the Douting lanes,
    #    beam gates across the Taiyiyuan axis path.
    # ------------------------------------------------------------------
    for lz in (1545, 1551, 1557, 1563, 1569):
        _lantern_string(fills, f"courtlife lantern douting w {lz}", 3489, lz, 8)
        _lantern_string(fills, f"courtlife lantern douting e {lz}", 3711, lz, 8)
    _lantern_gate(fills, "courtlife lantern gate taiyi s", 980, 3676, 3704)
    _lantern_gate(fills, "courtlife lantern gate taiyi n", 1060, 3676, 3704)

    # ------------------------------------------------------------------
    # 5. Fire vats (太平缸): hall corners and gate courts of four yards.
    # ------------------------------------------------------------------
    _fire_vat(fills, "courtlife vat taiji w", 2860, 5040, 1)
    _fire_vat(fills, "courtlife vat taiji e", 3140, 5040, 1)
    _fire_vat(fills, "courtlife vat guozijian w", 1845, 4390, 1)
    _fire_vat(fills, "courtlife vat guozijian e", 1980, 4390, 1)
    _fire_vat(fills, "courtlife vat douting", 3670, 1678, 4)
    _fire_vat(fills, "courtlife vat qinfu", 2160, 3552, 1)

    # ------------------------------------------------------------------
    # 6. Carved screen walls (影壁): overlays on the Qi Wang Fu and Wei
    #    Guo Gong screen slabs, gate-facing faces.
    # ------------------------------------------------------------------
    _screen_carving(fills, "courtlife yingbi qiwangfu", 3800, 3539, 1)
    _screen_carving(fills, "courtlife yingbi weiguogong", 2600, 3139, 1)

    # ------------------------------------------------------------------
    # 7. Hitching stones + mounting blocks (拴马石·上马石): paired sets
    #    outside the residence and post-station gates.
    # ------------------------------------------------------------------
    _hitch_set(fills, "courtlife hitch qinfu w", 2150, 3505, 1, 1)
    _hitch_set(fills, "courtlife hitch qinfu e", 2250, 3505, 1, -1)
    _hitch_set(fills, "courtlife hitch douting w", 3530, 1505, 4, 1)
    _hitch_set(fills, "courtlife hitch douting e", 3670, 1505, 4, -1)

    # ------------------------------------------------------------------
    # 8. Wells with windlass (水井·辘轳) for the well-less courtyards.
    # ------------------------------------------------------------------
    _well(fills, "courtlife well guozijian", 2070, 4440, 1)
    _well(fills, "courtlife well taiji", 2600, 5200, 1)


def main() -> None:
    run_builder(build_courtyard_life_detail_3d, "courtyard_life_detail_3d")


if __name__ == "__main__":
    main()
