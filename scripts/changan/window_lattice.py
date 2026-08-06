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
    run_builder,
)


"""
Window lattice and door details for palace, temple, gate, and office halls.

Replaces large blank wall faces with traditional grid patterns:
- Vertical mullions and horizontal transoms
- Central door opening with frame
- Lattice blocks alternating with air gaps
"""


def add_wall_grid(
    fills: list[Fill],
    label: str,
    x1: int, y1: int, z1: int,
    x2: int, y2: int, z2: int,
    face: str,
    frame_block: str = M.WOOD,
    lattice_block: str = M.GLASS,
) -> None:
    """
    Add a window lattice grid on a wall face using batched fills.
    face: 'north', 'south', 'west', 'east' - which side of the box gets the grid.
    """
    min_x, max_x = sorted((x1, x2))
    min_y, max_y = sorted((y1, y2))
    min_z, max_z = sorted((z1, z2))

    if face in ("south", "north"):
        z = min_z if face == "south" else max_z
        width_start, width_end = min_x, max_x
        depth_start, depth_end = z, z
        is_x_width = True
    else:
        x = min_x if face == "west" else max_x
        width_start, width_end = min_z, max_z
        depth_start, depth_end = x, x
        is_x_width = False

    cell_w, cell_h = 4, 5

    for w in range(width_start, width_end + 1, cell_w):
        if is_x_width:
            add_fill(fills, f"{label} mullion {w}", (w, min_y, depth_start), (w, max_y, depth_end), frame_block)
        else:
            add_fill(fills, f"{label} mullion {w}", (depth_start, min_y, w), (depth_end, max_y, w), frame_block)

    for h in range(min_y, max_y + 1, cell_h):
        if is_x_width:
            add_fill(fills, f"{label} transom {h}", (width_start, h, depth_start), (width_end, h, depth_end), frame_block)
        else:
            add_fill(fills, f"{label} transom {h}", (depth_start, h, width_start), (depth_end, h, width_end), frame_block)

    for w in range(width_start + cell_w // 2, width_end, cell_w):
        for h in range(min_y + cell_h // 2, max_y, cell_h):
            if is_x_width:
                add_fill(fills, f"{label} glass {w},{h}", (w - 1, h, depth_start), (w, h + 1, depth_end), lattice_block)
            else:
                add_fill(fills, f"{label} glass {w},{h}", (depth_start, h, w - 1), (depth_end, h + 1, w), lattice_block)


def build_window_lattices(fills: list[Fill]) -> None:
    # ------------------------------------------------------------------
    # Daming Palace main halls
    # ------------------------------------------------------------------
    add_wall_grid(fills, "hanyuan_s", 2660, 12, 5179, 3340, 60, 5180, "north")
    add_wall_grid(fills, "hanyuan_w", 2660, 12, 5180, 2660, 60, 5480, "east")
    add_wall_grid(fills, "hanyuan_e", 3340, 12, 5180, 3340, 60, 5480, "west")
    add_wall_grid(fills, "xuanzheng_s", 2740, 10, 4879, 3260, 42, 4880, "north")
    add_wall_grid(fills, "zichen_s", 2360, 8, 5199, 2620, 32, 5200, "north")
    # Danfeng Gate south facade
    add_wall_grid(fills, "danfeng_s", 2945, 24, 4050, 3055, 58, 4050, "south")
    # Penglai Pavilion
    add_wall_grid(fills, "penglai_s", 2976, 5, 5596, 3024, 28, 5596, "south")

    # ------------------------------------------------------------------
    # Taiji Palace
    # ------------------------------------------------------------------
    add_wall_grid(fills, "taiji_chengtian_s", 2980, 2, 4715, 3020, 20, 4715, "south")
    add_wall_grid(fills, "taiji_hall_s", 2920, 8, 5050, 3080, 44, 5050, "south")
    add_wall_grid(fills, "taiji_liangyi_s", 2940, 7, 5360, 3060, 33, 5360, "south")
    add_wall_grid(fills, "taiji_office_w", 2300, 2, 4900, 2300, 22, 5700, "west")
    add_wall_grid(fills, "taiji_office_e", 3700, 2, 4900, 3700, 22, 5700, "east")

    # ------------------------------------------------------------------
    # Xingqing Palace
    # ------------------------------------------------------------------
    add_wall_grid(fills, "xingqing_flower_s", 992, 2, 1452, 1048, 42, 1452, "south")
    add_wall_grid(fills, "xingqing_chenxiang_s", 1284, 5, 1184, 1316, 22, 1184, "south")

    # ------------------------------------------------------------------
    # City gates - main tower south/north facades
    # ------------------------------------------------------------------
    gate_north_south = [
        ("zhuque", 2950, 40, -42, 3050, 66, -42),
        ("mingde", 2930, 36, -145, 3070, 70, -145),
        ("anhua", 1164, 28, -28, 1236, 53, -28),
        ("qixia", 4764, 28, -28, 4836, 53, -28),
        ("zhide", 1164, 28, 5972, 1236, 53, 5972),
        ("xuanwu", 2964, 28, 5972, 3036, 53, 5972),
        ("anli", 4764, 28, 5972, 4836, 53, 5972),
    ]
    for name, x1, y1, z1, x2, y2, z2 in gate_north_south:
        add_wall_grid(fills, f"{name}_s", x1, y1, z1, x2, y2, z2, "south")
        north_z = 42 if name == "zhuque" else (-35 if name == "mingde" else z2 + 56)
        add_wall_grid(fills, f"{name}_n", x1, y1, north_z, x2, y2, north_z, "north")

    gate_east_west = [
        ("kaiyuan", -28, 28, 1464, -28, 53, 1536),
        ("jinguang", -28, 28, 2964, -28, 53, 3036),
        ("yanping", -28, 28, 4464, -28, 53, 4536),
        ("tonghua", 5972, 28, 1464, 5972, 53, 1536),
        ("chunming", 5972, 28, 2964, 5972, 53, 3036),
        ("yanxing", 5972, 28, 4464, 5972, 53, 4536),
    ]
    for name, x1, y1, z1, x2, y2, z2 in gate_east_west:
        add_wall_grid(fills, f"{name}_w", x1, y1, z1, x2, y2, z2, "west")
        east_x = 28 if name in {"kaiyuan", "jinguang", "yanping"} else 6028
        add_wall_grid(fills, f"{name}_e", east_x, y1, z1, east_x, y2, z2, "east")

    # ------------------------------------------------------------------
    # Temple main halls
    # ------------------------------------------------------------------
    add_wall_grid(fills, "daci_mahavira_s", 4552, 5, 3811, 4648, 27, 3812, "north")
    add_wall_grid(fills, "jianfu_buddha_s", 1290, 5, 3574, 1360, 19, 3575, "north")
    add_wall_grid(fills, "qinglong_buddha_s", 5005, 5, 1014, 5095, 27, 1015, "north")
    add_wall_grid(fills, "daxingshan_mahavira_s", 1405, 5, 2444, 1495, 29, 2445, "north")
    add_wall_grid(fills, "dayan_mahavira_s", 1105, 5, 3764, 1195, 29, 3765, "north")
    add_wall_grid(fills, "xuandu_sanqing_s", 4810, 5, 3629, 4890, 25, 3630, "north")

    # ------------------------------------------------------------------
    # Bell / Drum towers
    # ------------------------------------------------------------------
    add_wall_grid(fills, "bell_daming_s", 2212, 2, 4191, 2228, 44, 4192, "south")
    add_wall_grid(fills, "drum_daming_s", 3772, 2, 4191, 3788, 44, 4192, "south")
    add_wall_grid(fills, "bell_taiji_s", 2512, 2, 4891, 2528, 44, 4892, "south")
    add_wall_grid(fills, "drum_taiji_s", 3472, 2, 4891, 3488, 44, 4892, "south")

    # ------------------------------------------------------------------
    # Government offices and ritual buildings
    # ------------------------------------------------------------------
    add_wall_grid(fills, "government_hall_s", 2940, 3, 2459, 3060, 25, 2460, "south")
    add_wall_grid(fills, "ancestral_hall_s", 1920, 3, 5229, 1980, 21, 5230, "south")
    add_wall_grid(fills, "academy_hall_s", 1740, 3, 4469, 1810, 19, 4470, "south")


def main() -> None:
    run_builder(build_window_lattices, "window_lattice")


if __name__ == "__main__":
    main()
