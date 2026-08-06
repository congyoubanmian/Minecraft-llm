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
    add_staircase,
    run_builder,
)


"""
Round Altar 3D (圜丘) - the Tang heaven-worship altar south of Mingde Gate.

A three-tier circular altar built with scanline disk rows, so it reads as a
true circle rather than a stepped square - the kind of curved geometry that
only exists when you exploit vertical + radial layering.

Location in Chang'an city local coordinates:
    center: (3000, -1300)  (south suburbs, on the Zhuque Avenue axis,
    beyond the farm band that ends at z=-900)

3D features:
    - Self-levelling square base platform (raw terrain outside the city plate)
    - Three circular tiers (scanline disks), white marble balustrade rings
    - Four grand staircases (N/S/E/W) climbing all three tiers
    - Central spirit tablet + southeast offering furnace (燔柴炉)
    - Double enclosure walls (壝墙) with four Lingxing gates (棂星门)
    - Ring of lantern posts for night ceremonies
"""

CX = 3000
CZ = -1300


def _disk(fills: list[Fill], label: str, cx: int, cz: int, r: int, y1: int, y2: int, block: str, step: int = 2) -> None:
    """Approximate a filled circle with horizontal scanline rows."""
    for dz in range(-r, r + 1, step):
        half = int((r * r - dz * dz) ** 0.5)
        add_fill(fills, f"{label} row {dz}", (cx - half, y1, cz + dz), (cx + half, y2, cz + dz + step - 1), block)


def _ring(fills: list[Fill], label: str, cx: int, cz: int, r: int, y: int, block: str, width: int = 2) -> None:
    """Approximate a circular balustrade ring with scanline outline rows."""
    inner = r - width
    for dz in range(-r, r + 1, 2):
        outer_half = int((r * r - dz * dz) ** 0.5)
        inner_half = int(max(0, inner * inner - dz * dz) ** 0.5) if abs(dz) <= inner else 0
        z = cz + dz
        # west and east arcs of the ring
        add_fill(fills, f"{label} w {dz}", (cx - outer_half, y, z), (cx - inner_half, y, z + 1), block)
        add_fill(fills, f"{label} e {dz}", (cx + inner_half, y, z), (cx + outer_half, y, z + 1), block)


def _gate(fills: list[Fill], label: str, gx: int, gz: int, axis: str) -> None:
    """Lingxing gate: two red pillars, lintel, and a small tiled roof."""
    if axis == "x":  # gate opening faces east-west travel, pillars along z
        p1 = (gx, 1, gz - 6)
        p2 = (gx, 1, gz + 6)
        roof = ((gx - 3, 13, gz - 9), (gx + 3, 14, gz + 9))
        lintel = ((gx - 1, 10, gz - 6), (gx + 1, 11, gz + 6))
    else:
        p1 = (gx - 6, 1, gz)
        p2 = (gx + 6, 1, gz)
        roof = ((gx - 9, 13, gz - 3), (gx + 9, 14, gz + 3))
        lintel = ((gx - 6, 10, gz - 1), (gx + 6, 11, gz + 1))
    add_fill(fills, f"{label} pillar a", (p1[0], p1[1], p1[2]), (p1[0] + 1, 12, p1[2] + 1), M.RED_WALL_ALT)
    add_fill(fills, f"{label} pillar b", (p2[0] - 1, p2[1], p2[2] - 1), (p2[0], 12, p2[2]), M.RED_WALL_ALT)
    add_fill(fills, f"{label} lintel", lintel[0], lintel[1], M.GOLD_ACCENT)
    add_fill(fills, f"{label} roof", roof[0], roof[1], M.ROOF_GREEN)
    # Carve the gateway through the wall
    if axis == "x":
        add_fill(fills, f"{label} opening", (gx, 2, gz - 4), (gx, 9, gz + 4), M.AIR)
    else:
        add_fill(fills, f"{label} opening", (gx - 4, 2, gz), (gx + 4, 9, gz), M.AIR)


def build_mingtang_altar_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 0. Self-levelling base platform (terrain outside the city plate).
    # ------------------------------------------------------------------
    add_fill(fills, "yuanqiu base clear", (CX - 150, 1, CZ - 150), (CX + 150, 60, CZ + 150), M.AIR)
    add_fill(fills, "yuanqiu base platform", (CX - 150, 0, CZ - 150), (CX + 150, 1, CZ + 150), M.GRASS)

    # ------------------------------------------------------------------
    # 1. Three circular tiers.
    # ------------------------------------------------------------------
    _disk(fills, "yuanqiu tier1", CX, CZ, 62, 1, 3, M.STONE)
    _disk(fills, "yuanqiu tier2", CX, CZ, 46, 3, 6, M.STONE)
    _disk(fills, "yuanqiu tier3", CX, CZ, 30, 6, 9, M.STONE)
    # White marble balustrade ring on each tier edge
    _ring(fills, "yuanqiu rail1", CX, CZ, 62, 4, M.QUARTZ)
    _ring(fills, "yuanqiu rail2", CX, CZ, 46, 7, M.QUARTZ)
    _ring(fills, "yuanqiu rail3", CX, CZ, 30, 10, M.QUARTZ)

    # ------------------------------------------------------------------
    # 2. Four grand staircases climbing all tiers.
    # ------------------------------------------------------------------
    for name, (dx, dz, direction) in {
        "south": (0, 1, "south"),
        "north": (0, -1, "north"),
        "east": (1, 0, "east"),
        "west": (-1, 0, "west"),
    }.items():
        # Each staircase runs radially inward from r=78 to r=30.
        for seg, (r_out, r_in, y1, y2) in enumerate([(78, 62, 1, 3), (60, 46, 3, 6), (44, 30, 6, 9)]):
            steps = r_out - r_in
            if direction in ("north", "south"):
                z_from = CZ + dz * r_out
                z_to = CZ + dz * r_in
                add_staircase(fills, f"yuanqiu stair {name} s{seg}", CX - 5, z_from, CX + 5, z_to, y1=y1, y2=y2, direction=direction, block=M.SMOOTH)
            else:
                x_from = CX + dx * r_out
                x_to = CX + dx * r_in
                add_staircase(fills, f"yuanqiu stair {name} s{seg}", x_from, CZ - 5, x_to, CZ + 5, y1=y1, y2=y2, direction=direction, block=M.SMOOTH)

    # ------------------------------------------------------------------
    # 3. Altar top: central spirit tablet + offering furnace.
    # ------------------------------------------------------------------
    add_fill(fills, "yuanqiu tablet base", (CX - 3, 9, CZ - 2), (CX + 3, 10, CZ + 2), M.DARK)
    add_fill(fills, "yuanqiu tablet", (CX - 2, 11, CZ - 1), (CX + 2, 18, CZ + 1), M.DARK_BRICKS)
    add_fill(fills, "yuanqiu tablet cap", (CX - 3, 19, CZ - 2), (CX + 3, 20, CZ + 2), M.GOLD)
    # Offering furnace (燔柴炉) southeast of the tablet
    fx, fz = CX + 18, CZ + 18
    add_fill(fills, "yuanqiu furnace base", (fx - 4, 9, fz - 4), (fx + 4, 10, fz + 4), M.GOLD_ACCENT)
    add_fill(fills, "yuanqiu furnace bowl", (fx - 3, 11, fz - 3), (fx + 3, 13, fz + 3), M.DARK_BRICKS)
    add_fill(fills, "yuanqiu furnace fire", (fx - 1, 14, fz - 1), (fx + 1, 14, fz + 1), M.SEA_LANTERN)

    # ------------------------------------------------------------------
    # 4. Double enclosure walls (壝墙) with four Lingxing gates.
    # ------------------------------------------------------------------
    for r, label in [(96, "inner"), (132, "outer")]:
        add_outline(fills, f"yuanqiu wall {label} n", CX - r, CZ - r, CX + r, CZ - r, 1, 7, M.RED_WALL, thickness=2)
        add_outline(fills, f"yuanqiu wall {label} s", CX - r, CZ + r, CX + r, CZ + r, 1, 7, M.RED_WALL, thickness=2)
        add_outline(fills, f"yuanqiu wall {label} w", CX - r, CZ - r, CX - r, CZ + r, 1, 7, M.RED_WALL, thickness=2)
        add_outline(fills, f"yuanqiu wall {label} e", CX + r, CZ - r, CX + r, CZ + r, 1, 7, M.RED_WALL, thickness=2)
    for r in (96, 132):
        _gate(fills, f"yuanqiu gate s {r}", CX, CZ + r, "z")
        _gate(fills, f"yuanqiu gate n {r}", CX, CZ - r, "z")
        _gate(fills, f"yuanqiu gate e {r}", CX + r, CZ, "x")
        _gate(fills, f"yuanqiu gate w {r}", CX - r, CZ, "x")

    # ------------------------------------------------------------------
    # 5. Lantern ring between the enclosures.
    # ------------------------------------------------------------------
    for i in range(16):
        ang = i * math.pi / 8
        lx = CX + int(114 * math.cos(ang))
        lz = CZ + int(114 * math.sin(ang))
        add_fill(fills, f"yuanqiu lantern post {i}", (lx, 1, lz), (lx, 6, lz), M.LOG)
        add_fill(fills, f"yuanqiu lantern {i}", (lx, 7, lz), (lx, 7, lz), M.LANTERN)


def main() -> None:
    run_builder(build_mingtang_altar_3d, "mingtang_altar_3d")


if __name__ == "__main__":
    main()
