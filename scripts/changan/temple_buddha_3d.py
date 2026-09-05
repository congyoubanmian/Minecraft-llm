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
    add_pixel_mural,
    run_builder,
)


"""
Temple Buddha 3D (三大寺大雄宝殿造像深化) - interior statuary overlay pass
that furnishes the Mahavira halls (大雄宝殿) of the three great Tang
monasteries: 大兴善寺 Daxingshan, 大慈恩寺 Da Ci'en and 青龙寺 Qinglong.

Halls deepened (geometry derived from the source builders; interior air =
hollow-box bounds shrunk by the 2-block wall thickness, floor slab top y=2
so the first free block inside is y=3):
    Daxingshan  temple_daxingshan.py: mahavira hall hollow box
        (hx2-45, 1, hz2-35)..(hx2+45, 30, hz2+35), mid_x=1450, hz2=2480
        -> interior x 1407..1493, z 2447..2513, air y 3..28
    Da Ci'en    temple_daci.py: mahavira hall
        (hx2-48, 1, hz2-38)..(hx2+48, 28, hz2+38), mid_x=4600, hz2=3850
        -> interior x 4554..4646, z 3814..3886, air y 3..26
    Qinglong    temple_qinglong.py: buddha hall (大雄宝殿)
        (hx-45, 1, hz-35)..(hx+45, 28, hz+35), mid_x=5050, hz=1050
        -> interior x 5007..5093, z 1017..1083, air y 3..26
    None of the three source halls carve door openings (only the freestanding
    mountain gates sit on the south axis), so the central south corridor is
    kept clear as the ceremonial entry path. This pass is strictly additive:
    statues stand on the hall floor / altar platform and the halos and mural
    lean flat against the wall faces - nothing is carved, no niches.

Deepening checklist (one full set per hall, shared helpers):
    1. 佛坛 + 三世佛: stone altar platform with three seated Buddhas -
       Sakyamuni (h5, centre), Bhaisajyaguru / Amitabha (h4, flanking) -
       quartz lotus thrones, gold ushnisha curls, double-ring halos
    2. 十八罗汉: 9 standing arhats along each gable-wall inner edge,
       holding khakkhara staffs (LOG), sutra boxes (WOOD) or prayer beads
       (RED_WOOL), mirrored hand-to-hand poses
    3. 胁侍菩萨: one attendant bodhisattva flanking the main Buddha
       (quartz body, gold crown, pink silk shawl)
    4. 供桌供品: three long offering tables before the Buddhas, each with
       a gold incense burner, white offering mound and red fruit plate
    5. 幡幔: two rows of four LOG banner poles with 3-segment hanging
       banners alternating red / gold wool
    6. 千手观音壁: 16x12 thousand-hand Guanyin pixel mural (GOLD body +
       fan of slim gold arms + SEA_LANTERN aureole) on the east gable wall
       over a DARK backing slab - painted proud of the wall face
    7. 拜垫: two rows of six pink rush cushions (蒲团) for the congregation

Distinctive features:
    - Triad Buddha altar (三世佛) whose halo ellipses (GOLD outer ring,
      SEA_LANTERN inner ring) rise flat against the north wall behind the
      heads - visible the moment one enters through the south axis
    - 18-arhat processions along both gable walls with three rotating hand
      attributes and left/right mirrored poses
    - Thousand-hand Guanyin pixel mural glowing (sea lantern) against a
      deepslate dark field on the gable wall
    - Complete ritual furniture set: altar platform, offering tables,
      banner rows and a meditation-cushion grid that leave the central
      door axis and the passage between the tables walkable
"""

# ---------------------------------------------------------------------------
# Hall interiors derived from the source builders (see module docstring).
# tag must keep the "buddha " label prefix required for this overlay.
# ---------------------------------------------------------------------------
HALLS = [
    # tag, centre x, centre z, west/east interior air x, south/north air z
    ("buddha daxingshan", 1450, 2480, 1407, 1493, 2447, 2513),
    ("buddha daci", 4600, 3850, 4554, 4646, 3814, 3886),
    ("buddha qinglong", 5050, 1050, 5007, 5093, 1017, 1083),
]

# 16x12 thousand-hand Guanyin mural art (top row first). '.' leaves the dark
# backing slab visible; G = gold body/arms/lotus, S = sea lantern aureole.
_GUANYIN_ART = [
    "....G......G....",
    ".......SS.......",
    ".G....S..S....G.",
    ".....S.GG.S.....",
    ".......GG.......",
    ".......GG.......",
    "..G....GG....G..",
    ".......GG.......",
    "......GGGG......",
    "................",
    "................",
    "................",
]
_GUANYIN_PALETTE = {"G": M.GOLD, "S": M.SEA_LANTERN}


def _buddha(
    fills: list[Fill],
    label: str,
    x: int,
    z: int,
    y: int,
    halo: bool = True,
    height: int = 5,
) -> None:
    """One seated Buddha in full lotus pose (结跏趺坐).

    (x, z) is the statue centre, y the first free floor block. Stacked
    throne (2) + lap (1) + 2-wide quartz body (height-2 tall, head at top)
    + gold ushnisha curl = `height` blocks of statue. The optional halo is
    a vertical double ellipse mounted flat on the wall face behind the
    statue: gold outer ring + sea lantern inner ring.
    """
    add_fill(fills, f"{label} throne", (x - 3, y, z - 2), (x + 2, y, z + 1), M.STONE)
    add_fill(fills, f"{label} throne lotus", (x - 2, y + 1, z - 1), (x + 1, y + 1, z), M.QUARTZ)
    add_fill(fills, f"{label} lap", (x - 2, y + 2, z - 1), (x + 1, y + 2, z), M.QUARTZ)
    add_fill(fills, f"{label} body", (x - 1, y + 3, z - 1), (x, y + height, z), M.QUARTZ)
    add_fill(fills, f"{label} ushnisha", (x - 1, y + height + 1, z - 1), (x, y + height + 1, z), M.GOLD)
    if halo:
        cy = y + height
        hz = z + 2  # one block behind the body, against the north wall face
        add_fill(fills, f"{label} halo w", (x - 2, cy - 3, hz), (x - 2, cy + 3, hz), M.GOLD)
        add_fill(fills, f"{label} halo e", (x + 2, cy - 3, hz), (x + 2, cy + 3, hz), M.GOLD)
        add_fill(fills, f"{label} halo top", (x - 1, cy + 4, hz), (x + 1, cy + 4, hz), M.GOLD)
        add_fill(fills, f"{label} halo base", (x - 1, cy - 4, hz), (x + 1, cy - 4, hz), M.GOLD)
        add_fill(fills, f"{label} halo inner w", (x - 1, cy - 2, hz), (x - 1, cy + 2, hz), M.SEA_LANTERN)
        add_fill(fills, f"{label} halo inner e", (x + 1, cy - 2, hz), (x + 1, cy + 2, hz), M.SEA_LANTERN)


def _attendant(fills: list[Fill], label: str, x: int, z: int, y: int) -> None:
    """Standing attendant bodhisattva (胁侍菩萨): quartz body, gold crown,
    pink silk shawl (披帛) draped across the shoulders."""
    add_fill(fills, f"{label} body", (x, y, z), (x, y + 2, z), M.QUARTZ)
    add_fill(fills, f"{label} crown", (x, y + 3, z), (x, y + 3, z), M.GOLD)
    add_fill(fills, f"{label} shawl", (x - 1, y + 1, z), (x + 1, y + 1, z), M.PINK_WOOL)


def _arhat(fills: list[Fill], label: str, x: int, z: int, y: int, item: int, side: int) -> None:
    """Standing arhat (罗汉): 1x2 quartz figure with one hand attribute.

    item cycles 0 khakkhara staff (禅杖, held high), 1 sutra box (经匣),
    2 prayer beads (念珠); `side` (-1/+1) mirrors which hand holds it, so
    neighbours alternate pose down the wall.
    """
    add_fill(fills, f"{label} body", (x, y, z), (x, y + 1, z), M.QUARTZ)
    ix = x + side
    if item == 0:
        add_fill(fills, f"{label} staff", (ix, y, z), (ix, y + 2, z), M.LOG)
    elif item == 1:
        add_fill(fills, f"{label} sutra box", (ix, y + 1, z), (ix, y + 1, z), M.WOOD)
    else:
        add_fill(fills, f"{label} beads", (ix, y + 1, z), (ix, y + 1, z), M.RED_WOOL)


def _altar_table(fills: list[Fill], label: str, tcx: int, z1: int, z2: int, y: int) -> None:
    """Long offering table (供案): wood slab + gold incense burner + white
    offering mound + red fruit plate."""
    add_fill(fills, f"{label} slab", (tcx - 6, y, z1), (tcx + 6, y, z2), M.WOOD)
    add_fill(fills, f"{label} burner", (tcx, y + 1, z1), (tcx, y + 1, z1), M.GOLD)
    add_fill(fills, f"{label} offering mound", (tcx - 3, y + 1, z1), (tcx - 2, y + 1, z1), M.WHITE_WOOL)
    add_fill(fills, f"{label} fruit plate", (tcx + 2, y + 1, z1), (tcx + 3, y + 1, z1), M.RED_WOOL)


def _banner(fills: list[Fill], label: str, x: int, z: int, y: int, idx: int, dx: int) -> None:
    """Hall banner pole (幡杆): slim dark-oak post with a 3-segment hanging
    banner alternating red / gold wool; dx hangs the cloth toward the
    central axis and idx alternates the starting colour per pole."""
    add_fill(fills, f"{label} pole", (x, y, z), (x, y + 5, z), M.LOG)
    colors = (M.RED_WOOL, M.GOLD) if idx % 2 == 0 else (M.GOLD, M.RED_WOOL)
    for k in range(3):
        add_fill(fills, f"{label} banner {k}", (x + dx, y + 5 - k, z), (x + dx, y + 5 - k, z), colors[k % 2])


def _guanyin_mural(fills: list[Fill], label: str, x: int, y_top: int, z1: int, z2: int) -> None:
    """Thousand-hand Guanyin wall (千手观音壁): a DARK backing slab standing
    one block proud of the gable wall face, then the 16x12 pixel mural
    painted over it (gold figure + arm fan, sea lantern aureole; unpainted
    cells keep the dark field)."""
    add_fill(fills, f"{label} dark base", (x, y_top - 11, z1), (x, y_top, z2), M.DARK)
    add_pixel_mural(fills, f"{label} art", _GUANYIN_ART, _GUANYIN_PALETTE, x, y_top, z1 + 2, axis="z")


def _furnish_mahavira_hall(
    fills: list[Fill],
    tag: str,
    cx: int,
    cz: int,
    x_west: int,
    x_east: int,
    z_south: int,
    z_north: int,
) -> None:
    """One full statue set inside one Mahavira hall.

    (cx, cz) hall centre; x_west/x_east and z_south/z_north are the
    interior air boundaries taken from the source hollow box. y=3 is the
    first free block above the hall floor slab. Everything flanks the
    central south-north axis, leaving the entry path clear.
    """
    y = 3

    # 1. Altar platform (佛坛) against the north wall.
    add_fill(fills, f"{tag} altar platform", (cx - 28, y, z_north - 10), (cx + 28, y, z_north - 1), M.STONE)

    # 2. Triad of seated Buddhas (三世佛) on the platform, halos on the wall.
    _buddha(fills, f"{tag} sakyamuni", cx, z_north - 3, y + 1, halo=True, height=5)
    _buddha(fills, f"{tag} bhaisajyaguru", cx - 20, z_north - 3, y + 1, halo=True, height=4)
    _buddha(fills, f"{tag} amitabha", cx + 20, z_north - 3, y + 1, halo=True, height=4)

    # 3. Attendant bodhisattvas flanking the main Buddha.
    _attendant(fills, f"{tag} attendant w", cx - 7, z_north - 5, y + 1)
    _attendant(fills, f"{tag} attendant e", cx + 7, z_north - 5, y + 1)

    # 4. Eighteen arhats (十八罗汉), 9 along each gable-wall inner edge.
    z_start, z_end = z_south + 13, z_north - 13
    step = max(3, (z_end - z_start) // 8)
    for side_name, ax, item_side in (("w", x_west, 1), ("e", x_east, -1)):
        for i in range(9):
            _arhat(
                fills,
                f"{tag} arhat {side_name}{i}",
                ax,
                z_start + i * step,
                y,
                item=i % 3,
                side=item_side,
            )

    # 5. Three long offering tables before the Buddhas (gaps between them
    #    keep the side passages walkable).
    tz1, tz2 = z_north - 15, z_north - 14
    for name, tcx in (("w", cx - 20), ("c", cx), ("e", cx + 20)):
        _altar_table(fills, f"{tag} table {name}", tcx, tz1, tz2, y)

    # 6. Two rows of four banner poles flanking the central axis.
    for col, (bx, bdx) in enumerate(((cx - 14, 1), (cx + 14, -1))):
        for i in range(4):
            _banner(fills, f"{tag} banner {col}{i}", bx, z_south + 11 + i * 12, y, col * 4 + i, bdx)

    # 7. Thousand-hand Guanyin mural on the east gable wall.
    mural_z1 = cz - 8  # 16-wide art centred on the hall, 2-block dark frame
    _guanyin_mural(fills, f"{tag} guanyin wall", x_east, 19, mural_z1 - 2, mural_z1 + 17)

    # 8. Meditation cushions (拜垫蒲团), two rows of six.
    for i in range(6):
        czz = z_south + 7 + i * 6
        add_fill(fills, f"{tag} cushion w{i}", (cx - 8, y, czz), (cx - 8, y, czz), M.PINK_WOOL)
        add_fill(fills, f"{tag} cushion e{i}", (cx + 8, y, czz), (cx + 8, y, czz), M.PINK_WOOL)


def build_temple_buddha_3d(fills: list[Fill]) -> None:
    """Furnish the Mahavira halls of all three great temples."""
    for tag, cx, cz, x_west, x_east, z_south, z_north in HALLS:
        _furnish_mahavira_hall(fills, tag, cx, cz, x_west, x_east, z_south, z_north)


def main() -> None:
    run_builder(build_temple_buddha_3d, "temple_buddha_3d")


if __name__ == "__main__":
    main()
