from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMANDS_PATH = ROOT / "backend/projects/changan_city_v1/commands.json"
MAX_FILL_VOLUME = 32768


@dataclass(frozen=True)
class Region:
    name: str
    x1: int
    y1: int
    z1: int
    x2: int
    y2: int
    z2: int
    block: str


@dataclass(frozen=True)
class Fill:
    name: str
    x1: int
    y1: int
    z1: int
    x2: int
    y2: int
    z2: int
    block: str


def parse_coord(command: str, prefix: str) -> tuple[int, int, int]:
    raw = command.removeprefix(prefix).strip()
    match = re.fullmatch(r"(-?\d+),(-?\d+),(-?\d+)", raw)
    if not match:
        raise ValueError(f"Bad coordinate command: {command}")
    return tuple(map(int, match.groups()))


def parse_regions(commands: list[str]) -> tuple[list[str], list[Region]]:
    passthrough: list[str] = []
    regions: list[Region] = []
    pos1: tuple[int, int, int] | None = None
    pos2: tuple[int, int, int] | None = None
    label = "region"

    for command in commands:
        stripped = command.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            label = stripped.lstrip("#").strip() or "region"
            continue
        if stripped.startswith("//pos1 "):
            pos1 = parse_coord(stripped, "//pos1")
            continue
        if stripped.startswith("//pos2 "):
            pos2 = parse_coord(stripped, "//pos2")
            continue
        if stripped.startswith("//set "):
            if pos1 is None or pos2 is None:
                raise ValueError(f"//set without both positions: {stripped}")
            block = stripped.removeprefix("//set").strip()
            regions.append(Region(label, *pos1, *pos2, block))
            pos1 = None
            pos2 = None
            continue
        if stripped.startswith("/"):
            passthrough.append(stripped)
            continue
        raise ValueError(f"Unsupported command: {stripped}")

    return passthrough, regions


def split_region(region: Region) -> list[Fill]:
    min_x, max_x = sorted((region.x1, region.x2))
    min_y, max_y = sorted((region.y1, region.y2))
    min_z, max_z = sorted((region.z1, region.z2))
    height = max_y - min_y + 1
    fills: list[Fill] = []

    max_width = min(max_x - min_x + 1, max(1, MAX_FILL_VOLUME // height))
    for sx in range(min_x, max_x + 1, max_width):
        ex = min(max_x, sx + max_width - 1)
        width = ex - sx + 1
        max_depth = max(1, MAX_FILL_VOLUME // (width * height))
        for sz in range(min_z, max_z + 1, max_depth):
            ez = min(max_z, sz + max_depth - 1)
            volume = (ex - sx + 1) * height * (ez - sz + 1)
            if volume > MAX_FILL_VOLUME:
                raise ValueError(f"oversized fill produced: {volume}")
            fills.append(Fill(region.name, sx, min_y, sz, ex, max_y, ez, region.block))
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
        return rcon(
            f"fill {fill.x1} {fill.y1} {fill.z1} {fill.x2} {fill.y2} {fill.z2} {fill.block}",
            timeout,
        )
    finally:
        for cx, cz in corners:
            rcon(f"forceload remove {cx * 16} {cz * 16}", timeout)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Chang'an city using only vanilla /fill commands.")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--start", type=int, default=0, help="0-based split fill command offset.")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--delay-ms", type=int, default=80)
    parser.add_argument("--report-every", type=int, default=100)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--no-forceload", action="store_true")
    parser.add_argument("--skip-ground", action="store_true", help="Skip large grass ground tiles already provided by the foundation.")
    parser.add_argument("--skip-outer-wall", action="store_true", help="Skip wall/moat pieces already repaired by repair_changan_outer_wall_v1.py.")
    args = parser.parse_args()

    payload = json.loads(COMMANDS_PATH.read_text(encoding="utf-8"))
    passthrough, regions = parse_regions(payload["commands"])
    selected_regions: list[Region] = []
    for region in regions:
        name = region.name.lower()
        if args.skip_ground and "city ground tile" in name:
            continue
        if args.skip_outer_wall and (
            "outer wall" in name
            or "outer moat" in name
            or "moat" in name
            or (region.x1 in {9000, 14970, 14990} and region.y1 >= 65 and region.y2 <= 103)
        ):
            continue
        selected_regions.append(region)

    fills = [fill for region in selected_regions for fill in split_region(region)]
    selected_fills = fills[args.start :]
    if args.limit is not None:
        selected_fills = selected_fills[: args.limit]

    print(
        json.dumps(
            {
                "passthrough_commands": len(passthrough),
                "regions": len(regions),
                "selected_regions": len(selected_regions),
                "split_fills": len(fills),
                "selected_fills": len(selected_fills),
                "start": args.start,
                "execute": args.execute,
                "skip_ground": args.skip_ground,
                "skip_outer_wall": args.skip_outer_wall,
                "max_fill_volume": MAX_FILL_VOLUME,
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )
    if not args.execute:
        return

    for command in passthrough[:5]:
        if command.startswith("/tp "):
            continue
        rcon(command, args.timeout)

    for index, fill in enumerate(selected_fills, start=1):
        output = execute_fill(fill, args.timeout, not args.no_forceload)
        if args.delay_ms:
            time.sleep(args.delay_ms / 1000)
        absolute = args.start + index
        if index % args.report_every == 0 or index == len(selected_fills):
            print(
                json.dumps(
                    {
                        "done": index,
                        "total": len(selected_fills),
                        "absolute_fill": absolute,
                        "name": fill.name,
                        "sample": f"{fill.x1} {fill.y1} {fill.z1} {fill.x2} {fill.y2} {fill.z2} {fill.block}",
                        "result": output[:160],
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )

    for command in passthrough[5:]:
        rcon(command, args.timeout)


if __name__ == "__main__":
    main()
