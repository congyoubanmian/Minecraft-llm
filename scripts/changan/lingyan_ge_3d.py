from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.changan.lib import (
    Fill,
    Materials as M,
    add_cantilevered_floor,
    add_column_grid,
    add_fill,
    add_hip_roof,
    add_hollow_box,
    add_outline,
    add_platform_with_steps,
    add_pyramid_roof,
    add_spiral_stair,
    add_staircase,
    run_builder,
)


"""
Lingyan Pavilion (凌烟阁) — the Tang portrait gallery of the Twenty-Four
Meritorious Officials (二十四功臣), on the east side of the Taiji Palace
(太极宫) grounds (palace spans local x 2400-3600, z 4800-5800).

Local city coordinates:
    platform        x: 3300 .. 3440, z: 5300 .. 5450 (ground level y ~ 2)
    pavilion        three inset storeys above the platform
    stele pavilion  碑亭 south-west of the stair approach
    approach        three-flight south staircase with lantern posts

3D features:
- Three-tier stone platform (add_platform_with_steps) with a three-flight
  south staircase (add_staircase) climbing one flight per tier
- Three-storey wooden pavilion, each storey inset from the one below;
  red terracotta walls (M.RED_WALL) with dark-oak columns (M.LOG) at the
  corners and an interior column grid (add_column_grid); storey height 10
- Cantilevered balcony gallery (add_cantilevered_floor) with a fence
  railing ring (M.FENCE) on every storey
- Portrait mural panels (二十四功臣壁画): framed wool panels in distinct
  colours on two to three wall faces per storey, each face a different
  arrangement
- Interior square spiral stair (add_spiral_stair) linking all three storeys
- Hip roof (庑殿顶, add_hip_roof) with the golden ridge running along the
  footprint's long (north-south) axis
- Stone stele pavilion (碑亭): stone stele slab on a tortoise base under a
  small 攒尖顶 (add_pyramid_roof) carried on four posts
"""

X1, Z1 = 3300, 5300          # platform SW corner
X2, Z2 = 3440, 5450          # platform NE corner
CX, CZ = 3370, 5375          # platform centre
GROUND_Y = 2
STOREY_H = 10

# Per-storey wall footprints; each storey inset 6 from the one below.
# Walls rise STOREY_H blocks from the listed base y; a balcony slab caps each.
STOREYS = [
    (3330, 5330, 3410, 5420, 12),   # ground storey, walls y 12..21
    (3336, 5336, 3404, 5414, 23),   # second storey, walls y 23..32
    (3342, 5342, 3398, 5408, 34),   # third storey,  walls y 34..43
]
ROOF_Y = 45

# Spiral stair centre; the ring threads between the interior column grids.
STAIR_CX, STAIR_CZ = 3371, 5376


def add_mural_panel(
    fills: list[Fill],
    label: str,
    face: str,
    fixed: int,
    start: int,
    y1: int,
    width: int,
    height: int,
    color: str,
) -> None:
    """One framed portrait panel (功臣壁画) replacing a stretch of wall.

    face 'south'/'north': wall plane z == fixed, panel runs along x.
    face 'west'/'east':   wall plane x == fixed, panel runs along z.
    The panel is a colored wool canvas with a dark-oak frame on all sides.
    """
    y2 = y1 + height - 1
    end = start + width - 1
    if face in ("south", "north"):
        add_fill(fills, f"{label} canvas", (start, y1, fixed), (end, y2, fixed), color)
        add_fill(fills, f"{label} frame t", (start - 1, y2 + 1, fixed), (end + 1, y2 + 1, fixed), M.LOG)
        add_fill(fills, f"{label} frame b", (start - 1, y1 - 1, fixed), (end + 1, y1 - 1, fixed), M.LOG)
        add_fill(fills, f"{label} frame l", (start - 1, y1, fixed), (start - 1, y2, fixed), M.LOG)
        add_fill(fills, f"{label} frame r", (end + 1, y1, fixed), (end + 1, y2, fixed), M.LOG)
    else:
        add_fill(fills, f"{label} canvas", (fixed, y1, start), (fixed, y2, end), color)
        add_fill(fills, f"{label} frame t", (fixed, y2 + 1, start - 1), (fixed, y2 + 1, end + 1), M.LOG)
        add_fill(fills, f"{label} frame b", (fixed, y1 - 1, start - 1), (fixed, y1 - 1, end + 1), M.LOG)
        add_fill(fills, f"{label} frame l", (fixed, y1, start - 1), (fixed, y2, start - 1), M.LOG)
        add_fill(fills, f"{label} frame r", (fixed, y1, end + 1), (fixed, y2, end + 1), M.LOG)


def build_lingyan_ge_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 1. Three-tier stone platform
    # ------------------------------------------------------------------
    add_platform_with_steps(
        fills, "lingyan platform",
        X1, Z1, X2, Z2,
        GROUND_Y,
        tiers=[
            (4, 0, M.STONE),      # y 2..5
            (3, 6, M.STONE),      # y 6..8
            (3, 12, M.SMOOTH),    # y 9..11, top surface y 11
        ],
    )

    # ------------------------------------------------------------------
    # 2. South stair approach: one flight per tier face
    # ------------------------------------------------------------------
    stair_x1, stair_x2 = 3350, 3390
    add_staircase(fills, "lingyan stair flight 1", stair_x1, 5297, stair_x2, 5301, 2, 5, "north", block=M.SMOOTH)
    add_staircase(fills, "lingyan stair flight 2", stair_x1, 5302, stair_x2, 5306, 5, 8, "north", block=M.SMOOTH)
    add_staircase(fills, "lingyan stair flight 3", stair_x1, 5308, stair_x2, 5312, 8, 11, "north", block=M.SMOOTH)

    # ------------------------------------------------------------------
    # 3. Three storeys: walls, columns, murals, balcony galleries
    # ------------------------------------------------------------------
    for index, (sx1, sz1, sx2, sz2, wy) in enumerate(STOREYS):
        top = wy + STOREY_H - 1
        # Red terracotta walls, hollow interior
        add_hollow_box(fills, f"lingyan storey {index}", sx1, wy, sz1, sx2, top, sz2, M.RED_WALL)
        # Dark-oak corner columns (2x2, full storey height)
        add_fill(fills, f"lingyan storey {index} corner nw", (sx1, wy, sz1), (sx1 + 1, top, sz1 + 1), M.LOG)
        add_fill(fills, f"lingyan storey {index} corner ne", (sx2 - 1, wy, sz1), (sx2, top, sz1 + 1), M.LOG)
        add_fill(fills, f"lingyan storey {index} corner sw", (sx1, wy, sz2 - 1), (sx1 + 1, top, sz2), M.LOG)
        add_fill(fills, f"lingyan storey {index} corner se", (sx2 - 1, wy, sz2 - 1), (sx2, top, sz2), M.LOG)
        # Interior column grid (top storey keeps clear of the stairwell)
        if index < 2:
            add_column_grid(fills, f"lingyan storey {index} grid", sx1, sz1, sx2, sz2, wy, top, spacing=16)
        # Cantilevered balcony gallery + fence railing ring
        slab_y = top + 1
        add_cantilevered_floor(
            fills, f"lingyan balcony {index}",
            sx1, sz1, sx2, sz2,
            slab_y,
            overhang=3,
            block=M.WOOD,
            support_block=M.LOG,
        )
        add_outline(
            fills, f"lingyan railing {index}",
            sx1 - 3, sz1 - 3, sx2 + 3, sz2 + 3,
            slab_y + 1, slab_y + 1,
            M.FENCE,
        )

    # Entrance door on the ground-storey south face, with a gilt plaque
    add_fill(fills, "lingyan door", (3366, 12, 5330), (3374, 20, 5330), M.AIR)
    add_fill(fills, "lingyan door frame w", (3365, 12, 5330), (3365, 20, 5330), M.LOG)
    add_fill(fills, "lingyan door frame e", (3375, 12, 5330), (3375, 20, 5330), M.LOG)
    add_fill(fills, "lingyan plaque", (3367, 21, 5330), (3373, 21, 5330), M.GOLD)
    add_fill(fills, "lingyan plaque text", (3369, 21, 5330), (3371, 21, 5330), M.BLACK_WOOL)

    # ------------------------------------------------------------------
    # 4. Portrait murals (二十四功臣壁画) — different arrangement per face
    # ------------------------------------------------------------------
    # Ground storey (walls y 12..21), panel band y 14..19
    add_mural_panel(fills, "lingyan mural s0 south 1", "south", 5330, 3342, 14, 12, 6, M.YELLOW_WOOL)
    add_mural_panel(fills, "lingyan mural s0 south 2", "south", 5330, 3387, 14, 12, 6, M.BLUE_WOOL)
    add_mural_panel(fills, "lingyan mural s0 east 1", "east", 3410, 5342, 14, 12, 6, M.GREEN_WOOL)
    add_mural_panel(fills, "lingyan mural s0 east 2", "east", 3410, 5369, 14, 12, 6, M.RED_WOOL)
    add_mural_panel(fills, "lingyan mural s0 east 3", "east", 3410, 5396, 14, 12, 6, M.YELLOW_WOOL)
    add_mural_panel(fills, "lingyan mural s0 west 1", "west", 3330, 5348, 14, 12, 6, M.BLUE_WOOL)
    add_mural_panel(fills, "lingyan mural s0 west 2", "west", 3330, 5390, 14, 12, 6, M.GREEN_WOOL)
    # Second storey (walls y 23..32), panel band y 25..30
    add_mural_panel(fills, "lingyan mural s1 north 1", "north", 5414, 3346, 25, 11, 6, M.RED_WOOL)
    add_mural_panel(fills, "lingyan mural s1 north 2", "north", 5414, 3365, 25, 11, 6, M.YELLOW_WOOL)
    add_mural_panel(fills, "lingyan mural s1 north 3", "north", 5414, 3384, 25, 11, 6, M.GREEN_WOOL)
    add_mural_panel(fills, "lingyan mural s1 east 1", "east", 3404, 5350, 25, 11, 6, M.BLUE_WOOL)
    add_mural_panel(fills, "lingyan mural s1 east 2", "east", 3404, 5388, 25, 11, 6, M.YELLOW_WOOL)
    add_mural_panel(fills, "lingyan mural s1 west 1", "west", 3336, 5356, 25, 11, 6, M.RED_WOOL)
    add_mural_panel(fills, "lingyan mural s1 west 2", "west", 3336, 5384, 25, 11, 6, M.GREEN_WOOL)
    # Third storey (walls y 34..43), smaller panel band y 36..40
    add_mural_panel(fills, "lingyan mural s2 south 1", "south", 5342, 3350, 36, 10, 5, M.YELLOW_WOOL)
    add_mural_panel(fills, "lingyan mural s2 south 2", "south", 5342, 3381, 36, 10, 5, M.BLUE_WOOL)
    add_mural_panel(fills, "lingyan mural s2 north 1", "north", 5408, 3350, 36, 10, 5, M.GREEN_WOOL)
    add_mural_panel(fills, "lingyan mural s2 north 2", "north", 5408, 3381, 36, 10, 5, M.RED_WOOL)

    # ------------------------------------------------------------------
    # 5. Interior spiral stair linking all three storeys
    # ------------------------------------------------------------------
    # Stairwell openings through the two intermediate balcony slabs
    add_fill(fills, "lingyan stairwell 1", (STAIR_CX - 6, 22, STAIR_CZ - 6), (STAIR_CX + 6, 22, STAIR_CZ + 6), M.AIR)
    add_fill(fills, "lingyan stairwell 2", (STAIR_CX - 6, 33, STAIR_CZ - 6), (STAIR_CX + 6, 33, STAIR_CZ + 6), M.AIR)
    add_spiral_stair(
        fills, "lingyan spiral",
        STAIR_CX, STAIR_CZ,
        radius=6,
        y1=13, y2=43,
        block=M.WOOD,
    )

    # ------------------------------------------------------------------
    # 6. Hip roof (庑殿顶) with golden ridge along the long (z) axis
    # ------------------------------------------------------------------
    add_hip_roof(
        fills, "lingyan hip roof",
        3340, 5340, 3400, 5410,
        ROOF_Y,
        layers=30,
        ridge_axis="z",
    )

    # ------------------------------------------------------------------
    # 7. Stele pavilion (碑亭) south-west of the stair
    # ------------------------------------------------------------------
    stele_cx, stele_cz = 3320, 5286
    add_fill(fills, "lingyan stele base", (3309, 2, 5275), (3331, 3, 5297), M.STONE)
    # Four roof posts
    for px in (3313, 3327):
        for pz in (5279, 5293):
            add_fill(fills, f"lingyan stele post {px},{pz}", (px, 4, pz), (px, 11, pz), M.LOG)
    # Tortoise base, stele slab, inscription inlay, and cap
    add_fill(fills, "lingyan stele tortoise", (3316, 4, 5282), (3324, 5, 5290), M.DARK_BRICKS)
    add_fill(fills, "lingyan stele slab", (3318, 6, 5284), (3322, 14, 5288), M.QUARTZ)
    add_fill(fills, "lingyan stele inscription", (3319, 8, 5284), (3321, 12, 5284), M.DARK)
    add_fill(fills, "lingyan stele cap", (3317, 15, 5283), (3323, 16, 5289), M.DARK)
    # Small pyramidal cover (攒尖顶)
    add_pyramid_roof(
        fills, "lingyan stele roof",
        stele_cx, stele_cz,
        radius=9,
        y=12,
    )

    # ------------------------------------------------------------------
    # 8. Lantern posts along the approach
    # ------------------------------------------------------------------
    for lx, lz in ((3346, 5288), (3394, 5288), (3346, 5294), (3394, 5294)):
        add_fill(fills, f"lingyan lantern post {lx},{lz}", (lx, 2, lz), (lx, 5, lz), M.LOG)
        add_fill(fills, f"lingyan lantern lamp {lx},{lz}", (lx, 6, lz), (lx, 6, lz), M.LANTERN)


def main() -> None:
    run_builder(build_lingyan_ge_3d, "lingyan_ge_3d")


if __name__ == "__main__":
    main()
