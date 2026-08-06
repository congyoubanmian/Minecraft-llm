from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parents[1]
BOT_URL = "http://127.0.0.1:3001"

MIN_X = 9000
MAX_X = 14999
MIN_Z = 9000
MAX_Z = 14999
FOUNDATION_Y1 = 60
FOUNDATION_Y2 = 63
CLEAR_Y1 = 65
CLEAR_Y2 = 130
TILE = 250

FOUNDATION_BLOCK = "minecraft:stone"
ENABLE_FOUNDATION_FILL = False

# Only natural terrain/vegetation/liquid blocks are removed above the city plane.
# Generated city blocks such as stone_bricks, concrete, wool, prismarine, lanterns,
# red_terracotta, roads, and roofs are deliberately not listed here.
NATURAL_CLEAR_MASK = ",".join(
    [
        "minecraft:grass_block",
        "minecraft:dirt",
        "minecraft:coarse_dirt",
        "minecraft:rooted_dirt",
        "minecraft:podzol",
        "minecraft:mycelium",
        "minecraft:stone",
        "minecraft:granite",
        "minecraft:diorite",
        "minecraft:andesite",
        "minecraft:tuff",
        "minecraft:calcite",
        "minecraft:gravel",
        "minecraft:sand",
        "minecraft:red_sand",
        "minecraft:clay",
        "minecraft:mud",
        "minecraft:water",
        "minecraft:lava",
        "minecraft:snow",
        "minecraft:snow_block",
        "minecraft:ice",
        "minecraft:packed_ice",
        "minecraft:oak_log",
        "minecraft:birch_log",
        "minecraft:spruce_log",
        "minecraft:jungle_log",
        "minecraft:acacia_log",
        "minecraft:dark_oak_log",
        "minecraft:mangrove_log",
        "minecraft:cherry_log",
        "minecraft:oak_leaves",
        "minecraft:birch_leaves",
        "minecraft:spruce_leaves",
        "minecraft:jungle_leaves",
        "minecraft:acacia_leaves",
        "minecraft:dark_oak_leaves",
        "minecraft:mangrove_leaves",
        "minecraft:cherry_leaves",
        "minecraft:azalea_leaves",
        "minecraft:flowering_azalea_leaves",
        "minecraft:grass",
        "minecraft:tall_grass",
        "minecraft:fern",
        "minecraft:large_fern",
        "minecraft:dead_bush",
        "minecraft:short_grass",
        "minecraft:seagrass",
        "minecraft:tall_seagrass",
        "minecraft:sugar_cane",
        "minecraft:vine",
        "minecraft:cave_vines",
        "minecraft:cave_vines_plant",
        "minecraft:kelp",
        "minecraft:kelp_plant",
        "minecraft:moss_block",
        "minecraft:moss_carpet",
    ]
)


def iter_tiles(limit: int | None = None, start: int = 0) -> list[tuple[int, int, int, int]]:
    tiles: list[tuple[int, int, int, int]] = []
    seen = 0
    for x in range(MIN_X, MAX_X + 1, TILE):
        for z in range(MIN_Z, MAX_Z + 1, TILE):
            if seen < start:
                seen += 1
                continue
            tiles.append((x, min(MAX_X, x + TILE - 1), z, min(MAX_Z, z + TILE - 1)))
            if limit is not None and len(tiles) >= limit:
                return tiles
    return tiles


def tile_commands(tile: tuple[int, int, int, int]) -> list[str]:
    x1, x2, z1, z2 = tile
    commands = []
    if ENABLE_FOUNDATION_FILL:
        commands.extend(
            [
                f"//pos1 {x1},{FOUNDATION_Y1},{z1}",
                f"//pos2 {x2},{FOUNDATION_Y2},{z2}",
                f"//set {FOUNDATION_BLOCK}",
            ]
        )
    commands.extend(
        [
        f"//pos1 {x1},{CLEAR_Y1},{z1}",
        f"//pos2 {x2},{CLEAR_Y2},{z2}",
        f"//replace {NATURAL_CLEAR_MASK} minecraft:air",
        ]
    )
    return commands


def build_commands(limit: int | None = None) -> list[str]:
    commands = [
        "/gamerule randomTickSpeed 0",
        "/weather clear",
        "/time set day",
    ]
    for tile in iter_tiles(limit):
        commands.extend(tile_commands(tile))
    return commands


def post_commands(commands: list[str], delay_ms: int) -> dict:
    with httpx.Client(timeout=300) as client:
        response = client.post(f"{BOT_URL}/commands", json={"commands": commands, "delay_ms": delay_ms})
        response.raise_for_status()
        return response.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a flat foundation under Chang'an city v1.")
    parser.add_argument("--limit", type=int, default=None, help="Only process the first N 250x250 tiles.")
    parser.add_argument("--start", type=int, default=0, help="Skip the first N 250x250 tiles.")
    parser.add_argument("--execute", action="store_true", help="Send commands to BuilderBot.")
    parser.add_argument("--batch-tiles", type=int, default=4, help="Tiles per bot request when executing.")
    parser.add_argument("--delay-ms", type=int, default=120, help="Delay between commands inside bot request.")
    args = parser.parse_args()

    tiles = iter_tiles(args.limit, args.start)
    commands_per_tile = len(tile_commands((MIN_X, min(MAX_X, MIN_X + TILE - 1), MIN_Z, min(MAX_Z, MIN_Z + TILE - 1))))
    total_commands = 3 + len(tiles) * commands_per_tile
    summary = {
        "bounds": {"min_x": MIN_X, "max_x": MAX_X, "min_z": MIN_Z, "max_z": MAX_Z},
        "tile_size": TILE,
        "tiles": len(tiles),
        "start": args.start,
        "commands": total_commands,
        "foundation_y": [FOUNDATION_Y1, FOUNDATION_Y2],
        "foundation_fill": ENABLE_FOUNDATION_FILL,
        "clear_y": [CLEAR_Y1, CLEAR_Y2],
        "execute": args.execute,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if not args.execute:
        return

    initial = ["/gamerule randomTickSpeed 0", "/weather clear", "/time set day"]
    print(json.dumps({"initial": post_commands(initial, args.delay_ms)}, ensure_ascii=False))

    for index in range(0, len(tiles), args.batch_tiles):
        batch_tiles = tiles[index : index + args.batch_tiles]
        batch: list[str] = []
        for tile in batch_tiles:
            batch.extend(tile_commands(tile))
        result = post_commands(batch, args.delay_ms)
        print(
            json.dumps(
                {
                    "batch": index // args.batch_tiles + 1,
                    "tiles_done": min(len(tiles), index + len(batch_tiles)),
                    "tiles_total": len(tiles),
                    "commands": len(batch),
                    "ok": result.get("ok"),
                },
                ensure_ascii=False,
            )
        )
        time.sleep(0.5)


if __name__ == "__main__":
    main()
