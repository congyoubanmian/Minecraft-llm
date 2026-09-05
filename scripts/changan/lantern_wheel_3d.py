from __future__ import annotations

import math
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
Lantern Wheel 3D (安福门灯轮·上元灯轮) - the giant festival lantern wheel of
the Shangyuan night, raised on the plaza outside the West Market north gate.
In Tang records (Emperor Ruizong's reign) a lantern wheel stood outside the
palace gate "twenty zhang tall, burning fifty thousand lamps" - this module
builds that legendary vertical landmark: a true-circle vertical wheel of
coloured lanterns turning on a great central mast above a stone terraced
base, ringed by radial fields of ground lights, flanked by two viewing
pavilions (彩楼看棚) and entered through a gilded memorial arch (牌坊).

Location in Chang'an city local coordinates:
    West Market north-gate plaza: x 1850..2050, z 1950..2150 (ground y 0-4).
    Wheel / plaza centre: (1950, 2050). Strictly inside the plot bounds;
    the West Market gate tower (1785..1795, 2019..2021) and all West Market
    buildings (x <= 1800) are well clear to the west.

Distinctive features (English):
    - Giant vertical lantern wheel, diameter 21 (radius 10): a TRUE circle
      assembled row-by-row with the vertical scanline-ring algorithm (the
      mingtang_altar_3d disk algorithm rotated upright) - every y-row gets
      one west arc and one east arc whose widths follow sqrt(r^2 - dy^2)
    - Double rim (双圈轮辋): outer GOLD band (r=10) plus inner RED_WOOL band
      (r=8), an open gap between them letting the light spill through
    - 20 evenly spaced five-colour lamp clusters (RED/YELLOW/BLUE/GREEN/
      WHITE_WOOL shades) capping the rim, each with an embedded SEA_LANTERN
      glowing just inside
    - 8 dark-oak spokes from hub to rim (4 straight runs + 4 block-stepped
      diagonals), a 3x3 LOG axle piercing the mast horizontally, gold hub
      collars and gilded axle end caps
    - Central lantern mast: 3x3 LOG rising 26 blocks off the terrace to
      y34, crowned with a GOLD orb plate, bead and a two-tone banner
    - Stone terraced base: two scanline disks (r=14 at y4..6, r=12 at
      y7..8) with four directional three-step staircases
    - Radial ground-light field: three concentric flush SEA_LANTERN rings
      (r=18 x 12 lamps, r=24 x 16, r=30 x 24) plus gold radial markers
    - Two two-storey viewing pavilions (彩楼看棚) east and west: open
      ground-floor sheds under a ring beam, cantilevered upper decks with
      fence railings, alternating RED/YELLOW woollen drapes and green-glaze
      pavilion roofs with crossed gold ridges
    - Entrance pailou (灯轮牌坊) on the plaza's north edge: red pillars,
      double lintels, green-glaze crown and a gilded "安福门灯轮" plaque
    - Four palace lantern posts marking the plaza corners and two spruce
      pines softening the hardscape

Note on algorithm: the wheel is a VERTICAL circle, so the scanline runs
over y (one fill per row per side) instead of over z as in the flat
mingtang altar disks; row widths follow the circle equation exactly.
"""


# ---------------------------------------------------------------------------
# Constants - site and wheel geometry.
# ---------------------------------------------------------------------------
PLAZA_X1, PLAZA_X2 = 1850, 2050     # hard plot bounds (never cross)
PLAZA_Z1, PLAZA_Z2 = 1950, 2150

CX, CZ = 1950, 2050                 # plaza / wheel centre
GROUND_Y = 4                        # plaza surface level

WHEEL_R = 10                        # rim radius -> 21-block diameter
WHEEL_CY = 20                       # hub height (rim spans y10..y30)
MAST_TOP_Y = 33                     # 3x3 LOG mast y9..y33 (26 tall)
FLAG_X_SPAN = 6                     # banner reach east of the mast

# Radial ground-light rings: (radius, lamp count).
GROUND_RINGS = ((18, 12), (24, 16), (30, 24))

# Wheel lamp palette cycles RED/YELLOW/BLUE/GREEN/WHITE around the rim.
LAMP_COLORS = (M.RED_WOOL, M.YELLOW_WOOL, M.BLUE_WOOL, M.GREEN_WOOL, M.WHITE_WOOL)

# Viewing pavilion centres (both flanks), pines and corner posts.
PAVILION_W_CX, PAVILION_E_CX, PAVILION_CZ = 1884, 2016, 2050
PINE_SPOTS = ((1890, 1980), (2010, 2120))
CORNER_POSTS = ((1862, 1962), (2038, 1962), (1862, 2138), (2038, 2138))


# ---------------------------------------------------------------------------
# Scanline circle primitives (flat disks + the vertical ring variant).
# ---------------------------------------------------------------------------
def _disk_rows(
    fills: list[Fill],
    label: str,
    cx: int, cz: int,
    r: int,
    y1: int, y2: int,
    block: str,
    step: int = 2,
) -> None:
    """Flat scanline disk (mingtang_altar_3d algorithm): z-rows of width
    sqrt(r^2 - dz^2), each row `step` deep."""
    for dz in range(-r, r + 1, step):
        half = int((r * r - dz * dz) ** 0.5)
        add_fill(
            fills, f"{label} row {dz}",
            (cx - half, y1, cz + dz), (cx + half, y2, cz + dz + step - 1),
            block,
        )


def _vertical_ring(
    fills: list[Fill],
    label: str,
    cx: int, cy: int, cz: int,
    r: int,
    block: str,
) -> None:
    """VERTICAL scanline ring in the x-y plane (the lantern wheel rim).

    One row per y offset dy in -r..r; each row is a west arc and an east
    arc between the outer circle (radius r) and the inner circle (r-1),
    3 blocks thick in z (cz-1..cz+1) to match the central mast.
    """
    inner = r - 1
    for dy in range(-r, r + 1):
        outer_half = int((r * r - dy * dy) ** 0.5)
        inner_half = int((inner * inner - dy * dy) ** 0.5) if abs(dy) <= inner else 0
        add_fill(
            fills, f"{label} w {dy}",
            (cx - outer_half, cy + dy, cz - 1), (cx - inner_half, cy + dy, cz + 1),
            block,
        )
        add_fill(
            fills, f"{label} e {dy}",
            (cx + inner_half, cy + dy, cz - 1), (cx + outer_half, cy + dy, cz + 1),
            block,
        )


# ---------------------------------------------------------------------------
# Section builders.
# ---------------------------------------------------------------------------
def _build_plaza_paving(fills: list[Fill]) -> None:
    """Smooth-stone plaza disk under the whole lamp field (r=32, flush y4)."""
    _disk_rows(fills, "wheel plaza", CX, CZ, 32, GROUND_Y, GROUND_Y, M.SMOOTH)


def _build_base_platform(fills: list[Fill]) -> None:
    """Two-tier stone terrace (scanline disks r=14 / r=12) + 4 stair runs."""
    _disk_rows(fills, "wheel base tier1", CX, CZ, 14, GROUND_Y, 6, M.STONE)
    _disk_rows(fills, "wheel base tier2", CX, CZ, 12, 7, 8, M.STONE)
    # Three steps per direction: y5 (off 15..16), y6 (14..15), y7 (13).
    for name, (dx, dz) in {"s": (0, 1), "n": (0, -1), "e": (1, 0), "w": (-1, 0)}.items():
        for i, (base_off, step_y) in enumerate([(15, 5), (14, 6), (13, 7)]):
            width = 2 if i < 2 else 1
            o1 = base_off if (dx + dz) > 0 else -(base_off + width - 1)
            o2 = o1 + width - 1
            if dz:
                add_fill(
                    fills, f"wheel step {name} {i}",
                    (CX - 2, step_y, CZ + o1), (CX + 2, step_y, CZ + o2), M.SMOOTH,
                )
            else:
                add_fill(
                    fills, f"wheel step {name} {i}",
                    (CX + o1, step_y, CZ - 2), (CX + o2, step_y, CZ + 2), M.SMOOTH,
                )


def _build_wheel(fills: list[Fill]) -> None:
    """The giant vertical lantern wheel: mast, axle, spokes, double rim, lamps."""
    # Central lantern mast: 3x3 LOG from the terrace up to y33, 26 tall.
    add_fill(fills, "wheel mast", (CX - 1, 9, CZ - 1), (CX + 1, MAST_TOP_Y, CZ + 1), M.LOG)
    add_fill(fills, "wheel mast cap", (CX - 1, 34, CZ - 1), (CX + 1, 34, CZ + 1), M.GOLD)
    add_fill(fills, "wheel orb bead", (CX, 35, CZ), (CX, 36, CZ), M.GOLD)
    # Two-tone banner flying from the orb.
    add_fill(fills, "wheel flag cloth", (CX + 1, 35, CZ), (CX + FLAG_X_SPAN, 37, CZ), M.RED_WOOL)
    add_fill(fills, "wheel flag tail", (CX + FLAG_X_SPAN - 1, 35, CZ), (CX + FLAG_X_SPAN, 37, CZ), M.YELLOW_WOOL)

    # Axle: 3x3 LOG piercing the mast horizontally at hub height, gilded caps.
    add_fill(
        fills, "wheel axle",
        (CX - 1, WHEEL_CY - 1, CZ - 6), (CX + 1, WHEEL_CY + 1, CZ + 6), M.LOG,
    )
    add_fill(
        fills, "wheel axle cap n",
        (CX - 1, WHEEL_CY - 1, CZ - 7), (CX + 1, WHEEL_CY + 1, CZ - 7), M.GOLD,
    )
    add_fill(
        fills, "wheel axle cap s",
        (CX - 1, WHEEL_CY - 1, CZ + 7), (CX + 1, WHEEL_CY + 1, CZ + 7), M.GOLD,
    )
    # Gold hub collars where the spokes meet the mast.
    add_fill(fills, "wheel hub w", (CX - 2, WHEEL_CY - 1, CZ - 1), (CX - 2, WHEEL_CY + 1, CZ + 1), M.GOLD)
    add_fill(fills, "wheel hub e", (CX + 2, WHEEL_CY - 1, CZ - 1), (CX + 2, WHEEL_CY + 1, CZ + 1), M.GOLD)

    # Eight spokes (轮辐) from hub to rim: 4 straight runs + 4 stepped diagonals.
    for k in range(8):
        ang = k * math.pi / 4
        ux, uy = math.cos(ang), math.sin(ang)
        if k % 2 == 0:
            if ux > 0:
                add_fill(fills, f"wheel spoke {k}", (CX + 2, WHEEL_CY, CZ - 1), (CX + 9, WHEEL_CY, CZ + 1), M.LOG)
            elif ux < 0:
                add_fill(fills, f"wheel spoke {k}", (CX - 9, WHEEL_CY, CZ - 1), (CX - 2, WHEEL_CY, CZ + 1), M.LOG)
            elif uy > 0:
                add_fill(fills, f"wheel spoke {k}", (CX, WHEEL_CY + 2, CZ - 1), (CX, WHEEL_CY + 9, CZ + 1), M.LOG)
            else:
                add_fill(fills, f"wheel spoke {k}", (CX, WHEEL_CY - 9, CZ - 1), (CX, WHEEL_CY - 2, CZ + 1), M.LOG)
        else:
            for t in range(2, 10):
                px = CX + int(round(t * ux))
                py = WHEEL_CY + int(round(t * uy))
                add_fill(fills, f"wheel spoke {k} t{t}", (px, py, CZ - 1), (px, py, CZ + 1), M.LOG)

    # Double rim (双圈轮辋): GOLD outer band r=10, RED_WOOL inner band r=8.
    _vertical_ring(fills, "wheel rim gold", CX, WHEEL_CY, CZ, 10, M.GOLD)
    _vertical_ring(fills, "wheel rim red", CX, WHEEL_CY, CZ, 8, M.RED_WOOL)

    # 20 evenly spaced five-colour lamps capping the rim, SEA_LANTERN inside.
    for i in range(20):
        ang = i * math.pi / 10
        sx = CX + int(round(9.5 * math.cos(ang)))
        sy = WHEEL_CY + int(round(9.5 * math.sin(ang)))
        lx = CX + int(round(7.5 * math.cos(ang)))
        ly = WHEEL_CY + int(round(7.5 * math.sin(ang)))
        add_fill(
            fills, f"wheel lamp {i} shade",
            (sx, sy, CZ - 1), (sx, sy, CZ + 1), LAMP_COLORS[i % 5],
        )
        add_fill(
            fills, f"wheel lamp {i} light",
            (lx, ly, CZ - 1), (lx, ly, CZ + 1), M.SEA_LANTERN,
        )


def _build_ground_lamp_array(fills: list[Fill]) -> None:
    """Radial field of flush ground lights: rings r18/24/30 with 12/16/24
    lamps, plus gold radial markers between the terrace and the first ring."""
    for ri, (radius, count) in enumerate(GROUND_RINGS):
        for i in range(count):
            ang = 2 * math.pi * i / count
            x = CX + int(round(radius * math.cos(ang)))
            z = CZ + int(round(radius * math.sin(ang)))
            add_fill(
                fills, f"wheel ground ring{ri} lamp {i}",
                (x, GROUND_Y, z), (x, GROUND_Y, z), M.SEA_LANTERN,
            )
    # Gold markers on the 12-spoke radial grid, skipping the 4 stair axes.
    for i in range(12):
        if i % 3 == 0:
            continue
        ang = i * math.pi / 6
        x = CX + int(round(16 * math.cos(ang)))
        z = CZ + int(round(16 * math.sin(ang)))
        add_fill(fills, f"wheel radial marker {i}", (x, GROUND_Y, z), (x, GROUND_Y, z), M.GOLD)


def _viewing_pavilion(fills: list[Fill], name: str, cx: int, cz: int) -> None:
    """One two-storey colour tower (彩楼看棚): open ground shed, railed upper
    deck with RED/YELLOW drapes, and a green-glaze roof with crossed ridges."""
    x1, x2 = cx - 9, cx + 9
    z1, z2 = cz - 7, cz + 7
    # Ground-floor timber sill.
    add_fill(fills, f"wheel {name} sill", (x1, GROUND_Y, z1), (x2, GROUND_Y, z2), M.WOOD)
    # Open shed columns (4 corners + 4 edge midpoints).
    posts = [(x1, z1), (x2, z1), (x1, z2), (x2, z2), (cx, z1), (cx, z2), (x1, cz), (x2, cz)]
    for i, (px, pz) in enumerate(posts):
        add_fill(fills, f"wheel {name} col {i}", (px, 5, pz), (px, 12, pz), M.LOG)
    # Ring beam capping the shed.
    add_outline(fills, f"wheel {name} beam", x1, z1, x2, z2, 12, 12, M.WOOD, thickness=1)
    # Cantilevered upper deck + fence railing.
    add_fill(fills, f"wheel {name} deck", (x1 - 2, 13, z1 - 2), (x2 + 2, 13, z2 + 2), M.WOOD)
    add_outline(fills, f"wheel {name} rail", x1 - 2, z1 - 2, x2 + 2, z2 + 2, 14, 14, M.FENCE, thickness=1)
    # Alternating RED/YELLOW woollen drapes on the north and south faces.
    for fi, off in enumerate((z1 - 2, z2 + 2)):
        for pi in range(5):
            px1 = cx - 9 + pi * 4
            color = M.RED_WOOL if pi % 2 == 0 else M.YELLOW_WOOL
            add_fill(
                fills, f"wheel {name} drape {fi} {pi}",
                (px1, 14, off), (px1 + 2, 16, off), color,
            )
    # Upper hall columns.
    uposts = [(cx - 6, cz - 5), (cx + 6, cz - 5), (cx - 6, cz + 5), (cx + 6, cz + 5), (cx, cz - 5), (cx, cz + 5)]
    for i, (px, pz) in enumerate(uposts):
        add_fill(fills, f"wheel {name} ucol {i}", (px, 14, pz), (px, 19, pz), M.RED_WALL)
    # Green-glaze roof: slab eave, cap, crossed gold ridges, corner upturns.
    add_fill(
        fills, f"wheel {name} roof eave",
        (x1 - 3, 20, z1 - 3), (x2 + 3, 20, z2 + 3),
        "minecraft:dark_prismarine_slab[type=bottom,waterlogged=false]",
    )
    add_fill(fills, f"wheel {name} roof cap", (x1, 21, z1), (x2, 21, z2), M.ROOF_GREEN)
    add_fill(fills, f"wheel {name} roof ridge x", (x1, 22, cz), (x2, 22, cz), M.GOLD)
    add_fill(fills, f"wheel {name} roof ridge z", (cx, 22, z1), (cx, 22, z2), M.GOLD)
    for i, (sx, sz) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        ex = cx + sx * (x2 - cx + 3)
        ez = cz + sz * (z2 - cz + 3)
        add_fill(fills, f"wheel {name} roof corner {i}", (ex, 20, ez), (ex, 22, ez), M.GOLD_ACCENT)


def _build_paifang(fills: list[Fill]) -> None:
    """Entrance pailou on the plaza's north edge with the gilded plaque."""
    pz1, pz2 = 1963, 1964
    add_fill(fills, "wheel paifang base w", (CX - 15, GROUND_Y, pz1 - 1), (CX - 12, GROUND_Y, pz2 + 1), M.STONE)
    add_fill(fills, "wheel paifang base e", (CX + 12, GROUND_Y, pz1 - 1), (CX + 15, GROUND_Y, pz2 + 1), M.STONE)
    add_fill(fills, "wheel paifang pillar w", (CX - 14, 5, pz1), (CX - 13, 16, pz2), M.RED_WALL_ALT)
    add_fill(fills, "wheel paifang pillar e", (CX + 13, 5, pz1), (CX + 14, 16, pz2), M.RED_WALL_ALT)
    add_fill(fills, "wheel paifang lintel", (CX - 15, 17, pz1), (CX + 15, 18, pz2), M.LOG)
    add_fill(fills, "wheel paifang crown", (CX - 17, 19, pz1 - 1), (CX + 17, 19, pz2 + 1), M.ROOF_GREEN)
    # Gilded "安福门灯轮" plaque panel hung off the lintel.
    add_fill(fills, "wheel paifang plaque", (CX - 6, 12, pz1), (CX + 6, 16, pz2), M.GOLD)
    add_fill(fills, "wheel paifang finial", (CX - 1, 20, pz1), (CX + 1, 21, pz2), M.GOLD)


def _build_corner_posts(fills: list[Fill]) -> None:
    """Four palace lantern posts marking the plaza corners."""
    for i, (x, z) in enumerate(CORNER_POSTS):
        add_fill(fills, f"wheel corner post {i} base", (x - 1, GROUND_Y, z - 1), (x + 1, GROUND_Y, z + 1), M.STONE)
        add_fill(fills, f"wheel corner post {i} shaft", (x, 5, z), (x, 11, z), M.RED_WALL)
        add_fill(fills, f"wheel corner post {i} collar", (x, 12, z), (x, 12, z), M.GOLD)
        add_fill(fills, f"wheel corner post {i} lamp", (x, 13, z), (x, 14, z), M.SEA_LANTERN)
        add_fill(fills, f"wheel corner post {i} cap", (x, 15, z), (x, 15, z), M.GOLD_ACCENT)


def _build_pines(fills: list[Fill]) -> None:
    """Two conical spruce pines softening the plaza corners."""
    for i, (x, z) in enumerate(PINE_SPOTS):
        add_fill(fills, f"wheel pine {i} trunk", (x, GROUND_Y, z), (x, 13, z), "minecraft:spruce_log")
        add_fill(fills, f"wheel pine {i} foliage low", (x - 2, 9, z - 2), (x + 2, 10, z + 2), "minecraft:spruce_leaves")
        add_fill(fills, f"wheel pine {i} foliage mid", (x - 1, 11, z - 1), (x + 1, 12, z + 1), "minecraft:spruce_leaves")
        add_fill(fills, f"wheel pine {i} foliage top", (x, 13, z), (x, 14, z), "minecraft:spruce_leaves")


# ---------------------------------------------------------------------------
# Main builder.
# ---------------------------------------------------------------------------
def build_lantern_wheel_3d(fills: list[Fill]) -> None:
    """Anfu Gate lantern wheel on the West Market north-gate plaza."""
    # 1. Plaza paving and the stone terraced base with four stair runs.
    _build_plaza_paving(fills)
    _build_base_platform(fills)
    # 2. The giant vertical lantern wheel (true-circle scanline rim).
    _build_wheel(fills)
    # 3. Radial ground-light field around the wheel.
    _build_ground_lamp_array(fills)
    # 4. East and west viewing pavilions (彩楼看棚).
    _viewing_pavilion(fills, "pavilion w", PAVILION_W_CX, PAVILION_CZ)
    _viewing_pavilion(fills, "pavilion e", PAVILION_E_CX, PAVILION_CZ)
    # 5. Entrance pailou with the gilded plaque.
    _build_paifang(fills)
    # 6. Corner palace lantern posts and pines.
    _build_corner_posts(fills)
    _build_pines(fills)


def main() -> None:
    run_builder(build_lantern_wheel_3d, "lantern_wheel_3d")


if __name__ == "__main__":
    main()
