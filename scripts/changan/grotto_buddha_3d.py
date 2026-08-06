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
Cliff Grottoes 3D (崖壁佛龛) - Longmen-style Buddhist niches carved into a
rock face at the foot of the Zhongnan mountains, south of the city.

A vertical composition you only get by thinking in 3D: a rock massif,
three stacked levels of arched niches cut into it, seated Buddha figures
inside each niche, and a bracket-hung wooden plank walkway (栈道) with
stone stairs threading the levels together.

Location in Chang'an city local coordinates:
    rock face: x 3100..3300, z -680..-640 (south suburbs, facing the
    city across the farm band; near the Zhongnan ridge at z=-800..-400)

3D features:
    - Stepped rock massif with weathered stone texture
    - 15 niches on three levels (arched openings carved back 6 deep)
    - Seated Buddha in every niche (quartz body, gold halo)
    - Cantilevered plank walkway on wooden brackets at level two
    - Stone stair flights connecting ground -> walkway -> top level
    - Protective tile eaves over the top-level niches
"""

FX1, FX2 = 3100, 3300   # rock face x extent
FZ_BACK = -680          # rock back
FZ_FACE = -640          # rock face (toward the city, +z)

LEVELS = [6, 18, 30]    # niche floor heights
NICHE_W = 9
NICHE_H = 9
NICHE_D = 7


def _buddha(fills: list[Fill], label: str, bx: int, by: int, bz: int) -> None:
    """Simple seated Buddha: crossed legs, body, head, halo."""
    add_fill(fills, f"{label} base", (bx - 2, by, bz - 1), (bx + 2, by + 1, bz + 1), M.GOLD_ACCENT)
    add_fill(fills, f"{label} legs", (bx - 2, by + 2, bz - 1), (bx + 2, by + 2, bz + 1), M.QUARTZ)
    add_fill(fills, f"{label} body", (bx - 1, by + 3, bz - 1), (bx + 1, by + 5, bz + 1), M.QUARTZ)
    add_fill(fills, f"{label} head", (bx - 1, by + 6, bz - 1), (bx + 1, by + 7, bz + 1), M.QUARTZ)
    # Halo slab behind the head
    add_fill(fills, f"{label} halo", (bx - 2, by + 5, bz + 1), (bx + 2, by + 8, bz + 1), M.GOLD)


def _niche(fills: list[Fill], label: str, nx: int, level_y: int) -> None:
    """Carve one arched niche into the face and place a Buddha inside."""
    z_face = FZ_FACE
    # Carve the opening (face back NICHE_D blocks)
    add_fill(
        fills, f"{label} carve",
        (nx - NICHE_W // 2, level_y, z_face - NICHE_D),
        (nx + NICHE_W // 2, level_y + NICHE_H, z_face),
        M.AIR,
    )
    # Arch lintel: round the top of the opening with an extra shallow carve
    add_fill(
        fills, f"{label} arch",
        (nx - NICHE_W // 2 + 1, level_y + NICHE_H + 1, z_face - 2),
        (nx + NICHE_W // 2 - 1, level_y + NICHE_H + 1, z_face),
        M.AIR,
    )
    # Niche floor
    add_fill(
        fills, f"{label} sill",
        (nx - NICHE_W // 2, level_y - 1, z_face - NICHE_D),
        (nx + NICHE_W // 2, level_y - 1, z_face),
        M.SMOOTH,
    )
    _buddha(fills, f"{label} buddha", nx, level_y, z_face - NICHE_D + 3)


def build_grotto_buddha_3d(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # 0. Rock massif: stepped, slightly tapering, weathered texture.
    # ------------------------------------------------------------------
    add_fill(fills, "grotto clear", (FX1 - 10, 1, FZ_BACK - 10), (FX2 + 10, 60, FZ_FACE + 16), M.AIR)
    add_fill(fills, "grotto rock low", (FX1, 1, FZ_BACK), (FX2, 20, FZ_FACE), M.STONE)
    add_fill(fills, "grotto rock mid", (FX1 + 6, 20, FZ_BACK + 4), (FX2 - 6, 34, FZ_FACE), M.ANDESITE)
    add_fill(fills, "grotto rock top", (FX1 + 14, 34, FZ_BACK + 8), (FX2 - 14, 44, FZ_FACE - 4), M.STONE)
    # Weathering patches
    for i, (wx, wy) in enumerate([(3120, 8), (3160, 14), (3240, 10), (3280, 16), (3180, 24), (3230, 28)]):
        add_fill(fills, f"grotto moss {i}", (wx, wy, FZ_FACE), (wx + 12, wy + 4, FZ_FACE), M.MOSS_STONE)

    # ------------------------------------------------------------------
    # 1. Three levels of niches.
    # ------------------------------------------------------------------
    niche_xs = [3140, 3170, 3200, 3230, 3260]
    for lv, level_y in enumerate(LEVELS):
        for j, nx in enumerate(niche_xs):
            _niche(fills, f"grotto l{lv} n{j}", nx, level_y)

    # Protective eaves above each top-level niche
    for j, nx in enumerate(niche_xs):
        add_fill(fills, f"grotto eave {j}", (nx - 7, LEVELS[2] + NICHE_H + 3, FZ_FACE - 2), (nx + 7, LEVELS[2] + NICHE_H + 4, FZ_FACE + 4), M.ROOF_GREEN)

    # ------------------------------------------------------------------
    # 2. Cantilevered plank walkway (栈道) at level two.
    # ------------------------------------------------------------------
    wy = LEVELS[1] - 1  # walkway deck just below the level-2 niche floors
    add_fill(fills, "grotto walkway deck", (FX1 - 4, wy, FZ_FACE + 1), (FX2 + 4, wy, FZ_FACE + 5), M.WOOD)
    add_outline(fills, "grotto walkway rail", FX1 - 4, FZ_FACE + 5, FX2 + 4, FZ_FACE + 5, wy + 1, wy + 1, M.FENCE, thickness=1)
    # Wooden brackets under the deck every 10 blocks
    for x in range(FX1 - 2, FX2 + 3, 10):
        add_fill(fills, f"grotto bracket {x}", (x, wy - 4, FZ_FACE), (x + 1, wy - 1, FZ_FACE + 3), M.LOG)

    # ------------------------------------------------------------------
    # 3. Stone stairs: ground -> walkway -> top level.
    # ------------------------------------------------------------------
    # Flight A: from ground at the west end up to the walkway
    for i in range(15):
        add_fill(fills, f"grotto stairA {i}", (FX1 - 12 + i, 1 + i, FZ_FACE + 2), (FX1 - 11 + i, 1 + i, FZ_FACE + 5), M.SMOOTH)
    # Flight B: from walkway east end up to the top level ledge
    for i in range(12):
        add_fill(fills, f"grotto stairB {i}", (FX2 + 4 - i, wy + 1 + i, FZ_FACE + 1), (FX2 + 4 - i, wy + 1 + i, FZ_FACE + 4), M.SMOOTH)
    # Top level ledge connecting the top niches
    add_fill(fills, "grotto top ledge", (FX1 + 8, LEVELS[2] - 1, FZ_FACE + 1), (FX2 - 8, LEVELS[2] - 1, FZ_FACE + 4), M.SMOOTH)
    add_outline(fills, "grotto top rail", FX1 + 8, FZ_FACE + 4, FX2 - 8, FZ_FACE + 4, LEVELS[2], LEVELS[2], M.FENCE, thickness=1)

    # ------------------------------------------------------------------
    # 4. Forecourt: offering terrace, incense burner, lanterns.
    # ------------------------------------------------------------------
    add_fill(fills, "grotto forecourt", (3170, 0, FZ_FACE + 6), (3230, 1, FZ_FACE + 24), M.SMOOTH)
    add_fill(fills, "grotto incense base", (3196, 1, FZ_FACE + 12), (3204, 3, FZ_FACE + 20), M.DARK_BRICKS)
    add_fill(fills, "grotto incense bowl", (3197, 4, FZ_FACE + 14), (3203, 6, FZ_FACE + 18), M.GOLD_ACCENT)
    for i, x in enumerate(range(3176, 3230, 12)):
        add_fill(fills, f"grotto lantern post {i}", (x, 1, FZ_FACE + 8), (x, 6, FZ_FACE + 8), M.LOG)
        add_fill(fills, f"grotto lantern {i}", (x, 7, FZ_FACE + 8), (x, 7, FZ_FACE + 8), M.LANTERN)


def main() -> None:
    run_builder(build_grotto_buddha_3d, "grotto_buddha_3d")


if __name__ == "__main__":
    main()
