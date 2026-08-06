from __future__ import annotations

import argparse
import json
import subprocess
import time

MIN_X = 9000
MAX_X = 14999
MIN_Z = 9000
MAX_Z = 14999

MOAT_MIN_X = 8910
MOAT_MAX_X = 15089
MOAT_MIN_Z = 8910
MOAT_MAX_Z = 15089

BASE_Y = 64
MAX_FILL_VOLUME = 32768

MOSS = "minecraft:mossy_stone_bricks"
STONE = "minecraft:stone_bricks"
DARK = "minecraft:deepslate_tiles"
ROAD_EDGE = "minecraft:polished_andesite"
WATER = "minecraft:water"


def fill_volume(x1: int, y1: int, z1: int, x2: int, y2: int, z2: int) -> int:
    return (abs(x2 - x1) + 1) * (abs(y2 - y1) + 1) * (abs(z2 - z1) + 1)


def split_fill(x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, block: str) -> list[tuple[int, int, int, int, int, int, str]]:
    min_x, max_x = sorted((x1, x2))
    min_y, max_y = sorted((y1, y2))
    min_z, max_z = sorted((z1, z2))
    height = max_y - min_y + 1
    commands: list[tuple[int, int, int, int, int, int, str]] = []
    max_width = min(max_x - min_x + 1, max(1, MAX_FILL_VOLUME // height))
    for sx in range(min_x, max_x + 1, max_width):
        ex = min(max_x, sx + max_width - 1)
        width = ex - sx + 1
        max_depth = max(1, MAX_FILL_VOLUME // (width * height))
        for sz in range(min_z, max_z + 1, max_depth):
            ez = min(max_z, sz + max_depth - 1)
            if fill_volume(sx, min_y, sz, ex, max_y, ez) > MAX_FILL_VOLUME:
                raise ValueError("split_fill produced an oversized command")
            commands.append((sx, min_y, sz, ex, max_y, ez, block))
    return commands


def add_fill(commands: list[tuple[int, int, int, int, int, int, str]], x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, block: str) -> None:
    commands.extend(split_fill(x1, y1, z1, x2, y2, z2, block))


def add_outline(commands: list[tuple[int, int, int, int, int, int, str]], x1: int, z1: int, x2: int, z2: int, y1: int, y2: int, block: str, thickness: int) -> None:
    add_fill(commands, x1, y1, z1, x2, y2, z1 + thickness - 1, block)
    add_fill(commands, x1, y1, z2 - thickness + 1, x2, y2, z2, block)
    add_fill(commands, x1, y1, z1, x1 + thickness - 1, y2, z2, block)
    add_fill(commands, x2 - thickness + 1, y1, z1, x2, y2, z2, block)


def build_commands() -> list[tuple[int, int, int, int, int, int, str]]:
    commands: list[tuple[int, int, int, int, int, int, str]] = []
    add_outline(commands, MOAT_MIN_X, MOAT_MIN_Z, MOAT_MAX_X, MOAT_MAX_Z, BASE_Y, BASE_Y, WATER, 48)
    add_outline(commands, MIN_X, MIN_Z, MAX_X, MAX_Z, BASE_Y + 1, BASE_Y + 26, MOSS, 30)
    add_outline(commands, MIN_X, MIN_Z, MAX_X, MAX_Z, BASE_Y + 27, BASE_Y + 34, STONE, 34)
    add_outline(commands, MIN_X, MIN_Z, MAX_X, MAX_Z, BASE_Y + 35, BASE_Y + 39, DARK, 10)
    add_outline(commands, MIN_X + 34, MIN_Z + 34, MAX_X - 34, MAX_Z - 34, BASE_Y + 35, BASE_Y + 35, ROAD_EDGE, 12)
    return commands


def rcon(command: str, timeout: int) -> str:
    return subprocess.check_output(["docker", "exec", "mc-ai-paper", "rcon-cli", command], text=True, timeout=timeout).strip()


def chunk_coords(x: int, z: int) -> tuple[int, int]:
    return x >> 4, z >> 4


def execute_fill(command: tuple[int, int, int, int, int, int, str], timeout: int) -> str:
    x1, y1, z1, x2, y2, z2, block = command
    corners = sorted({chunk_coords(x1, z1), chunk_coords(x1, z2), chunk_coords(x2, z1), chunk_coords(x2, z2)})
    for cx, cz in corners:
        rcon(f"forceload add {cx * 16} {cz * 16}", timeout)
    try:
        return rcon(f"fill {x1} {y1} {z1} {x2} {y2} {z2} {block}", timeout)
    finally:
        for cx, cz in corners:
            rcon(f"forceload remove {cx * 16} {cz * 16}", timeout)


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair Chang'an outer wall and moat using vanilla /fill chunks.")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--batch", type=int, default=20)
    parser.add_argument("--delay-ms", type=int, default=120)
    parser.add_argument("--timeout", type=int, default=240)
    args = parser.parse_args()

    commands = build_commands()
    selected = commands[args.start :]
    if args.limit is not None:
        selected = selected[: args.limit]
    print(
        json.dumps(
            {
                "total_commands": len(commands),
                "selected_commands": len(selected),
                "start": args.start,
                "execute": args.execute,
                "max_fill_volume": MAX_FILL_VOLUME,
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
    rcon("time set day", args.timeout)
    for index, command in enumerate(selected, start=1):
        output = execute_fill(command, args.timeout)
        if args.delay_ms:
            time.sleep(args.delay_ms / 1000)
        if index % args.batch == 0 or index == len(selected):
            absolute = args.start + index
            sample = " ".join(map(str, command[:6])) + f" {command[6]}"
            print(
                json.dumps(
                    {
                        "batch": (index + args.batch - 1) // args.batch,
                        "done": index,
                        "total": len(selected),
                        "absolute_command": absolute,
                        "sample": sample,
                        "result": output[:160],
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )


if __name__ == "__main__":
    main()
