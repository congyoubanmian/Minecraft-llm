from __future__ import annotations

import argparse
import json
import subprocess
import time
from dataclasses import dataclass


BASE_X = 9000
BASE_Y = 64
BASE_Z = 9000
MAX_FILL_VOLUME = 32768

STONE = "minecraft:stone_bricks"
SMOOTH = "minecraft:smooth_stone"
ANDESITE = "minecraft:polished_andesite"
RED = "minecraft:red_terracotta"
WHITE = "minecraft:white_concrete"
WOOD = "minecraft:dark_oak_planks"
LOG = "minecraft:dark_oak_log"
SPRUCE = "minecraft:spruce_planks"
ROOF = "minecraft:dark_prismarine"
DARK = "minecraft:deepslate_tiles"
GOLD = "minecraft:gold_block"
LANTERN = "minecraft:lantern"
SEA_LANTERN = "minecraft:sea_lantern"
YELLOW = "minecraft:yellow_terracotta"
BLACK = "minecraft:black_concrete"
RED_WOOL = "minecraft:red_wool"
BLUE_WOOL = "minecraft:blue_wool"
YELLOW_WOOL = "minecraft:yellow_wool"
GREEN_WOOL = "minecraft:green_wool"


@dataclass(frozen=True)
class Fill:
    label: str
    x1: int
    y1: int
    z1: int
    x2: int
    y2: int
    z2: int
    block: str


def w(x: int, y: int, z: int) -> tuple[int, int, int]:
    return BASE_X + x, BASE_Y + y, BASE_Z + z


def split_fill(label: str, a: tuple[int, int, int], b: tuple[int, int, int], block: str) -> list[Fill]:
    x1, y1, z1 = w(*a)
    x2, y2, z2 = w(*b)
    min_x, max_x = sorted((x1, x2))
    min_y, max_y = sorted((y1, y2))
    min_z, max_z = sorted((z1, z2))
    height = max_y - min_y + 1
    fills: list[Fill] = []
    max_width = min(max_x - min_x + 1, max(1, MAX_FILL_VOLUME // height))
    for sx in range(min_x, max_x + 1, max_width):
        ex = min(max_x, sx + max_width - 1)
        width = ex - sx + 1
        max_depth = max(1, MAX_FILL_VOLUME // (width * height))
        for sz in range(min_z, max_z + 1, max_depth):
            ez = min(max_z, sz + max_depth - 1)
            fills.append(Fill(label, sx, min_y, sz, ex, max_y, ez, block))
    return fills


def add_fill(fills: list[Fill], label: str, a: tuple[int, int, int], b: tuple[int, int, int], block: str) -> None:
    fills.extend(split_fill(label, a, b, block))


def add_outline(
    fills: list[Fill],
    label: str,
    x1: int,
    z1: int,
    x2: int,
    z2: int,
    y1: int,
    y2: int,
    block: str,
    thickness: int,
) -> None:
    add_fill(fills, f"{label} north", (x1, y1, z1), (x2, y2, z1 + thickness - 1), block)
    add_fill(fills, f"{label} south", (x1, y1, z2 - thickness + 1), (x2, y2, z2), block)
    add_fill(fills, f"{label} west", (x1, y1, z1), (x1 + thickness - 1, y2, z2), block)
    add_fill(fills, f"{label} east", (x2 - thickness + 1, y1, z1), (x2, y2, z2), block)


def add_stair_run(fills: list[Fill], label: str, x1: int, z1: int, x2: int, z2: int, start_y: int, steps: int, direction: str) -> None:
    for i in range(steps):
        if direction == "south":
            add_fill(fills, f"{label} step {i}", (x1 - i * 3, start_y + i, z1 - i * 6), (x2 + i * 3, start_y + i, z1 - i * 6 + 4), SMOOTH)
        elif direction == "north":
            add_fill(fills, f"{label} step {i}", (x1 - i * 3, start_y + i, z2 + i * 6 - 4), (x2 + i * 3, start_y + i, z2 + i * 6), SMOOTH)


def add_pillar_grid(fills: list[Fill], label: str, x1: int, z1: int, x2: int, z2: int, y1: int, y2: int, spacing: int = 28) -> None:
    xs = list(range(x1, x2 + 1, spacing))
    zs = list(range(z1, z2 + 1, spacing))
    for x in xs:
        for z in (z1, z2):
            add_fill(fills, f"{label} outer pillar", (x - 2, y1, z - 2), (x + 2, y2, z + 2), LOG)
    for z in zs:
        for x in (x1, x2):
            add_fill(fills, f"{label} side pillar", (x - 2, y1, z - 2), (x + 2, y2, z + 2), LOG)
    for x in range(x1 + spacing, x2, spacing * 2):
        for z in range(z1 + spacing, z2, spacing * 2):
            add_fill(fills, f"{label} inner pillar", (x - 1, y1, z - 1), (x + 1, y2 - 4, z + 1), LOG)


def add_roof_layers(fills: list[Fill], label: str, x1: int, z1: int, x2: int, z2: int, y: int, layers: int) -> None:
    for i in range(layers):
        inset = i * 12
        add_fill(fills, f"{label} roof layer {i}", (x1 + inset, y + i * 3, z1 + inset), (x2 - inset, y + i * 3 + 1, z2 - inset), ROOF)
    ridge_x = (x1 + x2) // 2
    add_fill(fills, f"{label} central ridge", (ridge_x - 4, y + layers * 3, z1 + 18), (ridge_x + 4, y + layers * 3 + 4, z2 - 18), GOLD)
    add_fill(fills, f"{label} ridge dark cap", (ridge_x - 8, y + layers * 3 + 5, z1 + 36), (ridge_x + 8, y + layers * 3 + 6, z2 - 36), DARK)


def add_lantern_line(fills: list[Fill], label: str, x1: int, z1: int, x2: int, z2: int, y: int, every: int) -> None:
    if x1 == x2:
        for z in range(min(z1, z2), max(z1, z2) + 1, every):
            add_fill(fills, f"{label} lamp post", (x1 - 1, y, z - 1), (x1 + 1, y + 5, z + 1), LOG)
            add_fill(fills, f"{label} lamp", (x1 - 1, y + 6, z - 1), (x1 + 1, y + 6, z + 1), SEA_LANTERN)
    elif z1 == z2:
        for x in range(min(x1, x2), max(x1, x2) + 1, every):
            add_fill(fills, f"{label} lamp post", (x - 1, y, z1 - 1), (x + 1, y + 5, z1 + 1), LOG)
            add_fill(fills, f"{label} lamp", (x - 1, y + 6, z1 - 1), (x + 1, y + 6, z1 + 1), SEA_LANTERN)


def add_palace_detail(fills: list[Fill]) -> None:
    halls = [
        ("hanyuan", 2660, 5180, 3340, 5480, 56),
        ("xuanzheng", 2740, 4880, 3260, 5080, 44),
        ("taiji", 2360, 5200, 2620, 5480, 40),
    ]
    for label, x1, z1, x2, z2, height in halls:
        add_stair_run(fills, f"{label} south stairs", x1 + 80, z1, x2 - 80, z2, 1, 8, "south")
        add_stair_run(fills, f"{label} north stairs", x1 + 120, z1, x2 - 120, z2, 1, 5, "north")
        add_pillar_grid(fills, f"{label} colonnade", x1 + 18, z1 + 18, x2 - 18, z2 - 18, 5, min(height - 4, 42), spacing=34)
        add_roof_layers(fills, f"{label} double eave", x1 - 38, z1 - 38, x2 + 38, z2 + 38, height + 9, 4)
        add_outline(fills, f"{label} stone railing", x1 - 28, z1 - 28, x2 + 28, z2 + 28, 5, 7, ANDESITE, 2)

    # Processional lamps and red carpet along the palace axis.
    add_fill(fills, "palace axis carpet", (2978, 2, 4100), (3022, 2, 5480), RED_WOOL)
    add_lantern_line(fills, "palace axis west", 2958, 4140, 2958, 5440, 3, 70)
    add_lantern_line(fills, "palace axis east", 3042, 4140, 3042, 5440, 3, 70)

    # Chengtian/Danfeng gate detail.
    for label, z in [("chengtian", 4100), ("danfeng", 4750)]:
        add_fill(fills, f"{label} plaque", (2960, 28, z - 34), (3040, 35, z - 32), GOLD)
        add_fill(fills, f"{label} plaque text bar", (2980, 30, z - 35), (3020, 32, z - 35), BLACK)
        add_roof_layers(fills, f"{label} gate layered roof", 2850, z - 56, 3150, z + 56, 45, 3)


def add_shop_unit(fills: list[Fill], label: str, x: int, z: int, width: int, depth: int, color: str, facing: str) -> None:
    add_fill(fills, f"{label} floor", (x, 2, z), (x + width, 2, z + depth), SPRUCE)
    add_fill(fills, f"{label} back wall", (x, 3, z + depth - 2), (x + width, 12, z + depth), WOOD)
    add_fill(fills, f"{label} left wall", (x, 3, z), (x + 2, 12, z + depth), WOOD)
    add_fill(fills, f"{label} right wall", (x + width - 2, 3, z), (x + width, 12, z + depth), WOOD)
    add_fill(fills, f"{label} awning", (x - 3, 13, z - 4), (x + width + 3, 15, z + depth + 4), color)
    add_fill(fills, f"{label} roof cap", (x - 5, 16, z - 6), (x + width + 5, 18, z + depth + 6), ROOF)
    add_fill(fills, f"{label} counter", (x + 6, 3, z + 4), (x + width - 6, 5, z + 8), ANDESITE)
    add_fill(fills, f"{label} lantern", (x + width // 2 - 1, 12, z + 2), (x + width // 2 + 1, 12, z + 4), SEA_LANTERN)
    if facing == "south":
        add_fill(fills, f"{label} sign", (x + 8, 10, z - 1), (x + width - 8, 13, z - 1), YELLOW)
    else:
        add_fill(fills, f"{label} sign", (x + 8, 10, z + depth + 1), (x + width - 8, 13, z + depth + 1), YELLOW)


def add_market_detail(fills: list[Fill], label: str, x1: int, z1: int, x2: int, z2: int) -> None:
    mid_x = (x1 + x2) // 2
    mid_z = (z1 + z2) // 2
    add_lantern_line(fills, f"{label} main street lamps x north", x1 + 80, mid_z - 34, x2 - 80, mid_z - 34, 3, 80)
    add_lantern_line(fills, f"{label} main street lamps x south", x1 + 80, mid_z + 34, x2 - 80, mid_z + 34, 3, 80)
    add_lantern_line(fills, f"{label} main street lamps z west", mid_x - 34, z1 + 80, mid_x - 34, z2 - 80, 3, 80)
    add_lantern_line(fills, f"{label} main street lamps z east", mid_x + 34, z1 + 80, mid_x + 34, z2 - 80, 3, 80)

    colors = [RED_WOOL, BLUE_WOOL, YELLOW_WOOL, GREEN_WOOL]
    idx = 0
    for x in range(x1 + 90, x2 - 130, 120):
        add_shop_unit(fills, f"{label} north shop {idx}", x, z1 + 85, 72, 42, colors[idx % len(colors)], "south")
        add_shop_unit(fills, f"{label} south shop {idx}", x, z2 - 130, 72, 42, colors[(idx + 1) % len(colors)], "north")
        idx += 1
    for z in range(z1 + 170, z2 - 190, 120):
        add_shop_unit(fills, f"{label} west shop {idx}", x1 + 90, z, 42, 72, colors[idx % len(colors)], "south")
        add_shop_unit(fills, f"{label} east shop {idx}", x2 - 135, z, 42, 72, colors[(idx + 2) % len(colors)], "south")
        idx += 1

    # Trading square with wells and flag poles.
    add_fill(fills, f"{label} central stone square", (mid_x - 90, 2, mid_z - 90), (mid_x + 90, 2, mid_z + 90), SMOOTH)
    add_outline(fills, f"{label} central well", mid_x - 18, mid_z - 18, mid_x + 18, mid_z + 18, 3, 7, STONE, 3)
    add_fill(fills, f"{label} well water", (mid_x - 12, 3, mid_z - 12), (mid_x + 12, 3, mid_z + 12), "minecraft:water")
    for dx, dz in [(-70, -70), (70, -70), (-70, 70), (70, 70)]:
        add_fill(fills, f"{label} banner pole", (mid_x + dx - 1, 3, mid_z + dz - 1), (mid_x + dx + 1, 18, mid_z + dz + 1), LOG)
        add_fill(fills, f"{label} banner cloth", (mid_x + dx + 2, 12, mid_z + dz - 5), (mid_x + dx + 2, 18, mid_z + dz + 5), RED_WOOL)


def add_ward_gates(fills: list[Fill]) -> None:
    x_lines = [520, 900, 1280, 1660, 2040, 2420, 3420, 3800, 4180, 4560, 4940, 5320]
    z_lines = [620, 1020, 1420, 1820, 2220, 2620, 3020, 3420, 3820]
    idx = 0
    for x in x_lines:
        for z in z_lines:
            if 1800 <= x <= 4200 and z >= 4100:
                continue
            if 700 <= x <= 1800 and 2000 <= z <= 3100:
                continue
            if 4200 <= x <= 5300 and 2000 <= z <= 3100:
                continue
            gate_x = x + 130
            add_fill(fills, f"ward gate {idx} posts", (gate_x - 18, 2, z - 3), (gate_x - 13, 15, z + 3), LOG)
            add_fill(fills, f"ward gate {idx} posts", (gate_x + 13, 2, z - 3), (gate_x + 18, 15, z + 3), LOG)
            add_fill(fills, f"ward gate {idx} lintel", (gate_x - 28, 15, z - 4), (gate_x + 28, 18, z + 4), ROOF)
            add_fill(fills, f"ward gate {idx} plaque", (gate_x - 10, 11, z - 5), (gate_x + 10, 13, z - 5), GOLD)
            idx += 1


def build_fills(section: str) -> list[Fill]:
    fills: list[Fill] = []
    if section in {"all", "palace"}:
        add_palace_detail(fills)
    if section in {"all", "markets"}:
        add_market_detail(fills, "west market", 760, 2060, 1760, 3060)
        add_market_detail(fills, "east market", 4240, 2060, 5240, 3060)
    if section in {"all", "wards"}:
        add_ward_gates(fills)
    return fills


def rcon(command: str, timeout: int) -> str:
    return subprocess.check_output(["docker", "exec", "mc-ai-paper", "rcon-cli", command], text=True, timeout=timeout).strip()


def chunk_coords(x: int, z: int) -> tuple[int, int]:
    return x >> 4, z >> 4


def execute_fill(fill: Fill, timeout: int, use_forceload: bool) -> str:
    if use_forceload:
        corners = sorted(
            {
                chunk_coords(fill.x1, fill.z1),
                chunk_coords(fill.x1, fill.z2),
                chunk_coords(fill.x2, fill.z1),
                chunk_coords(fill.x2, fill.z2),
            }
        )
        for cx, cz in corners:
            rcon(f"forceload add {cx * 16} {cz * 16}", timeout)
    else:
        corners = []
    try:
        return rcon(f"fill {fill.x1} {fill.y1} {fill.z1} {fill.x2} {fill.y2} {fill.z2} {fill.block}", timeout)
    finally:
        for cx, cz in corners:
            rcon(f"forceload remove {cx * 16} {cz * 16}", timeout)


def main() -> None:
    parser = argparse.ArgumentParser(description="Add Tang-style detail components to Chang'an city v2.")
    parser.add_argument("--section", choices=["all", "palace", "markets", "wards"], default="all")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--delay-ms", type=int, default=60)
    parser.add_argument("--report-every", type=int, default=100)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--no-forceload", action="store_true")
    args = parser.parse_args()

    fills = build_fills(args.section)
    selected = fills[args.start :]
    if args.limit is not None:
        selected = selected[: args.limit]
    print(
        json.dumps(
            {
                "section": args.section,
                "total_fills": len(fills),
                "selected_fills": len(selected),
                "start": args.start,
                "execute": args.execute,
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )
    if not args.execute:
        return

    rcon("gamerule randomTickSpeed 0", args.timeout)
    rcon("weather clear", args.timeout)
    for index, fill in enumerate(selected, start=1):
        output = execute_fill(fill, args.timeout, not args.no_forceload)
        if args.delay_ms:
            time.sleep(args.delay_ms / 1000)
        if index % args.report_every == 0 or index == len(selected):
            print(
                json.dumps(
                    {
                        "done": index,
                        "total": len(selected),
                        "absolute_fill": args.start + index,
                        "label": fill.label,
                        "sample": f"{fill.x1} {fill.y1} {fill.z1} {fill.x2} {fill.y2} {fill.z2} {fill.block}",
                        "result": output[:160],
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )


if __name__ == "__main__":
    main()
