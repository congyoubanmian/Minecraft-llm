from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass

import httpx


BOT_URL = "http://127.0.0.1:3001"

# Includes the generated Chang'an city footprint plus the 90-block outer moat.
MIN_X = 8910
MAX_X = 15089
MIN_Z = 8910
MAX_Z = 15089

DEFAULT_TILE = 125
DEFAULT_CLEAR_Y1 = 65
DEFAULT_CLEAR_Y2 = 319
DEFAULT_FILL_Y1 = 40
DEFAULT_FILL_Y2 = 63
DEFAULT_SURFACE_Y = 64

FILL_BLOCK = "minecraft:stone"
SURFACE_BLOCK = "minecraft:grass_block"
EDGE_BLOCK = "minecraft:smooth_stone"


@dataclass(frozen=True)
class Bounds:
    x1: int
    x2: int
    z1: int
    z2: int


def iter_tiles(tile_size: int, start: int = 0, limit: int | None = None) -> list[Bounds]:
    tiles: list[Bounds] = []
    seen = 0
    for x in range(MIN_X, MAX_X + 1, tile_size):
        for z in range(MIN_Z, MAX_Z + 1, tile_size):
            if seen < start:
                seen += 1
                continue
            tiles.append(Bounds(x, min(MAX_X, x + tile_size - 1), z, min(MAX_Z, z + tile_size - 1)))
            if limit is not None and len(tiles) >= limit:
                return tiles
            seen += 1
    return tiles


def worldedit_set(bounds: Bounds, y1: int, y2: int, block: str) -> list[str]:
    return [
        f"//pos1 {bounds.x1},{y1},{bounds.z1}",
        f"//pos2 {bounds.x2},{y2},{bounds.z2}",
        f"//set {block}",
    ]


def tile_commands(bounds: Bounds, phase: str, clear_y1: int, clear_y2: int, fill_y1: int, fill_y2: int, surface_y: int) -> list[str]:
    commands: list[str] = []
    if phase in {"all", "clear"}:
        commands.extend(worldedit_set(bounds, clear_y1, clear_y2, "minecraft:air"))
    if phase in {"all", "fill"}:
        commands.extend(worldedit_set(bounds, fill_y1, fill_y2, FILL_BLOCK))
    if phase in {"all", "surface"}:
        commands.extend(worldedit_set(bounds, surface_y, surface_y, SURFACE_BLOCK))
    return commands


def border_commands(surface_y: int) -> list[str]:
    """Add a hard, visible construction edge around the flattened city plate."""
    y1 = surface_y
    y2 = surface_y + 2
    return [
        f"//pos1 {MIN_X},{y1},{MIN_Z}",
        f"//pos2 {MAX_X},{y2},{MIN_Z}",
        f"//set {EDGE_BLOCK}",
        f"//pos1 {MIN_X},{y1},{MAX_Z}",
        f"//pos2 {MAX_X},{y2},{MAX_Z}",
        f"//set {EDGE_BLOCK}",
        f"//pos1 {MIN_X},{y1},{MIN_Z}",
        f"//pos2 {MIN_X},{y2},{MAX_Z}",
        f"//set {EDGE_BLOCK}",
        f"//pos1 {MAX_X},{y1},{MIN_Z}",
        f"//pos2 {MAX_X},{y2},{MAX_Z}",
        f"//set {EDGE_BLOCK}",
    ]


def post_commands(commands: list[str], delay_ms: int, timeout: int) -> dict:
    with httpx.Client(timeout=timeout) as client:
        response = client.post(f"{BOT_URL}/commands", json={"commands": commands, "delay_ms": delay_ms})
        response.raise_for_status()
        return response.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a true flat Chang'an city foundation with FAWE.")
    parser.add_argument("--phase", choices=["all", "clear", "fill", "surface"], default="all")
    parser.add_argument("--tile", type=int, default=DEFAULT_TILE, help="Tile width/depth in blocks.")
    parser.add_argument("--start", type=int, default=0, help="Skip the first N tiles.")
    parser.add_argument("--limit", type=int, default=None, help="Only process N tiles from --start.")
    parser.add_argument("--execute", action="store_true", help="Send commands to BuilderBot.")
    parser.add_argument("--batch-tiles", type=int, default=1, help="Tiles per bot request.")
    parser.add_argument("--delay-ms", type=int, default=300, help="Delay between commands inside one bot request.")
    parser.add_argument("--timeout", type=int, default=600, help="HTTP timeout for one bot request.")
    parser.add_argument("--clear-y1", type=int, default=DEFAULT_CLEAR_Y1)
    parser.add_argument("--clear-y2", type=int, default=DEFAULT_CLEAR_Y2)
    parser.add_argument("--fill-y1", type=int, default=DEFAULT_FILL_Y1)
    parser.add_argument("--fill-y2", type=int, default=DEFAULT_FILL_Y2)
    parser.add_argument("--surface-y", type=int, default=DEFAULT_SURFACE_Y)
    parser.add_argument("--border", action="store_true", help="Add a low smooth-stone edge around the construction plate.")
    args = parser.parse_args()

    tiles = iter_tiles(args.tile, args.start, args.limit)
    sample = Bounds(MIN_X, min(MAX_X, MIN_X + args.tile - 1), MIN_Z, min(MAX_Z, MIN_Z + args.tile - 1))
    commands_per_tile = len(
        tile_commands(sample, args.phase, args.clear_y1, args.clear_y2, args.fill_y1, args.fill_y2, args.surface_y)
    )
    total_tiles = len(iter_tiles(args.tile))
    summary = {
        "bounds": {"min_x": MIN_X, "max_x": MAX_X, "min_z": MIN_Z, "max_z": MAX_Z},
        "phase": args.phase,
        "tile": args.tile,
        "selected_tiles": len(tiles),
        "total_tiles": total_tiles,
        "start": args.start,
        "commands": len(tiles) * commands_per_tile + 4 + (len(border_commands(args.surface_y)) if args.border else 0),
        "clear_y": [args.clear_y1, args.clear_y2],
        "fill_y": [args.fill_y1, args.fill_y2],
        "surface_y": args.surface_y,
        "fill_block": FILL_BLOCK,
        "surface_block": SURFACE_BLOCK,
        "edge_block": EDGE_BLOCK if args.border else None,
        "execute": args.execute,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    if not args.execute:
        return

    initial = [
        "/gamerule randomTickSpeed 0",
        "/weather clear",
        "/time set day",
        "/tp BuilderBot 12000 128 12000",
    ]
    print(json.dumps({"initial": post_commands(initial, args.delay_ms, args.timeout)}, ensure_ascii=False), flush=True)

    for index in range(0, len(tiles), args.batch_tiles):
        batch_tiles = tiles[index : index + args.batch_tiles]
        commands: list[str] = []
        for tile in batch_tiles:
            commands.extend(
                tile_commands(tile, args.phase, args.clear_y1, args.clear_y2, args.fill_y1, args.fill_y2, args.surface_y)
            )
        result = post_commands(commands, args.delay_ms, args.timeout)
        done = min(len(tiles), index + len(batch_tiles))
        print(
            json.dumps(
                {
                    "batch": index // args.batch_tiles + 1,
                    "tiles_done": done,
                    "tiles_total": len(tiles),
                    "absolute_tile": args.start + done,
                    "commands": len(commands),
                    "ok": result.get("ok"),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        time.sleep(0.5)

    if args.border:
        result = post_commands(border_commands(args.surface_y), args.delay_ms, args.timeout)
        print(json.dumps({"border": True, "commands": len(border_commands(args.surface_y)), "ok": result.get("ok")}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
