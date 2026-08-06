from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import settings


PROJECT_ID = "changan_city_v1"
NAME = f"project_{PROJECT_ID}"
CITY_SIZE = 6000
BASE_Y = 64
PASTE = {"x": 9000, "y": BASE_Y, "z": 9000}
SPAWN = {"x": 12000, "y": 96, "z": 8720}
MAX_FILL_SPAN = 500

STONE = "minecraft:stone_bricks"
MOSS = "minecraft:mossy_stone_bricks"
DARK = "minecraft:deepslate_tiles"
ROAD = "minecraft:smooth_stone"
ROAD_EDGE = "minecraft:polished_andesite"
GROUND = "minecraft:grass_block"
WATER = "minecraft:water"
RED = "minecraft:red_terracotta"
WOOD = "minecraft:dark_oak_planks"
LOG = "minecraft:dark_oak_log"
ROOF = "minecraft:dark_prismarine"
GOLD = "minecraft:gold_block"
LANTERN = "minecraft:sea_lantern"
MARKET_RED = "minecraft:red_wool"
MARKET_BLUE = "minecraft:blue_wool"
MARKET_YELLOW = "minecraft:yellow_wool"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def app_path(path: Path) -> str:
    if path.is_relative_to(ROOT):
        return str(Path("/app") / path.relative_to(ROOT))
    return str(path)


def fill_cmds(a: tuple[int, int, int], b: tuple[int, int, int], block: str) -> list[str]:
    x1, y1, z1 = a
    x2, y2, z2 = b
    min_x, max_x = sorted((x1, x2))
    min_y, max_y = sorted((y1, y2))
    min_z, max_z = sorted((z1, z2))
    commands: list[str] = []
    for sx in range(min_x, max_x + 1, MAX_FILL_SPAN):
        ex = min(max_x, sx + MAX_FILL_SPAN - 1)
        for sz in range(min_z, max_z + 1, MAX_FILL_SPAN):
            ez = min(max_z, sz + MAX_FILL_SPAN - 1)
            commands.extend(
                [
                    f"//pos1 {sx},{min_y},{sz}",
                    f"//pos2 {ex},{max_y},{ez}",
                    f"//set {block}",
                ]
            )
    return commands


def w(local: tuple[int, int, int]) -> tuple[int, int, int]:
    return (PASTE["x"] + local[0], PASTE["y"] + local[1], PASTE["z"] + local[2])


def add_fill(commands: list[str], label: str, a: tuple[int, int, int], b: tuple[int, int, int], block: str) -> None:
    commands.append(f"# {label}")
    commands.extend(fill_cmds(w(a), w(b), block))


def add_outline(
    commands: list[str],
    label: str,
    x1: int,
    z1: int,
    x2: int,
    z2: int,
    y1: int,
    y2: int,
    block: str,
    *,
    thickness: int = 1,
) -> None:
    add_fill(commands, f"{label} north", (x1, y1, z1), (x2, y2, z1 + thickness - 1), block)
    add_fill(commands, f"{label} south", (x1, y1, z2 - thickness + 1), (x2, y2, z2), block)
    add_fill(commands, f"{label} west", (x1, y1, z1), (x1 + thickness - 1, y2, z2), block)
    add_fill(commands, f"{label} east", (x2 - thickness + 1, y1, z1), (x2, y2, z2), block)


def add_tower(commands: list[str], label: str, cx: int, cz: int, radius: int = 28, height: int = 46) -> None:
    add_fill(commands, f"{label} base", (cx - radius, 1, cz - radius), (cx + radius, height, cz + radius), STONE)
    add_fill(commands, f"{label} hollow", (cx - radius + 7, 3, cz - radius + 7), (cx + radius - 7, height - 8, cz + radius - 7), "minecraft:air")
    add_fill(commands, f"{label} roof lower", (cx - radius - 6, height + 1, cz - radius - 6), (cx + radius + 6, height + 3, cz + radius + 6), ROOF)
    add_fill(commands, f"{label} roof upper", (cx - radius + 3, height + 4, cz - radius + 3), (cx + radius - 3, height + 7, cz + radius - 3), ROOF)
    add_fill(commands, f"{label} beacon", (cx - 2, height + 8, cz - 2), (cx + 2, height + 12, cz + 2), GOLD)


def add_gate(commands: list[str], name: str, cx: int, cz: int, orientation: str) -> None:
    if orientation == "north_south":
        add_fill(commands, f"{name} gatehouse", (cx - 120, 1, cz - 26), (cx + 120, 38, cz + 26), RED)
        add_fill(commands, f"{name} gate opening", (cx - 34, 1, cz - 30), (cx + 34, 24, cz + 30), "minecraft:air")
        add_fill(commands, f"{name} roof", (cx - 135, 39, cz - 38), (cx + 135, 44, cz + 38), ROOF)
        add_tower(commands, f"{name} west tower", cx - 150, cz, 26, 42)
        add_tower(commands, f"{name} east tower", cx + 150, cz, 26, 42)
    else:
        add_fill(commands, f"{name} gatehouse", (cx - 26, 1, cz - 120), (cx + 26, 38, cz + 120), RED)
        add_fill(commands, f"{name} gate opening", (cx - 30, 1, cz - 34), (cx + 30, 24, cz + 34), "minecraft:air")
        add_fill(commands, f"{name} roof", (cx - 38, 39, cz - 135), (cx + 38, 44, cz + 135), ROOF)
        add_tower(commands, f"{name} north tower", cx, cz - 150, 26, 42)
        add_tower(commands, f"{name} south tower", cx, cz + 150, 26, 42)


def add_hall(commands: list[str], label: str, x1: int, z1: int, x2: int, z2: int, height: int, *, block: str = RED) -> None:
    add_fill(commands, f"{label} platform", (x1 - 18, 1, z1 - 18), (x2 + 18, 4, z2 + 18), STONE)
    add_fill(commands, f"{label} body", (x1, 5, z1), (x2, height, z2), block)
    add_fill(commands, f"{label} interior void", (x1 + 8, 7, z1 + 8), (x2 - 8, height - 2, z2 - 8), "minecraft:air")
    add_fill(commands, f"{label} roof eave", (x1 - 24, height + 1, z1 - 24), (x2 + 24, height + 4, z2 + 24), ROOF)
    add_fill(commands, f"{label} roof ridge", (x1 - 8, height + 5, z1 - 8), (x2 + 8, height + 8, z2 + 8), ROOF)
    add_fill(commands, f"{label} gold ridge", ((x1 + x2) // 2 - 5, height + 9, z1 - 12), ((x1 + x2) // 2 + 5, height + 12, z2 + 12), GOLD)


def add_market(commands: list[str], label: str, x1: int, z1: int, x2: int, z2: int) -> None:
    add_outline(commands, f"{label} market wall", x1, z1, x2, z2, 1, 8, STONE, thickness=5)
    add_fill(commands, f"{label} market plaza", (x1 + 20, 1, z1 + 20), (x2 - 20, 1, z2 - 20), ROAD)
    mid_x = (x1 + x2) // 2
    mid_z = (z1 + z2) // 2
    add_fill(commands, f"{label} cross road x", (x1 + 20, 2, mid_z - 16), (x2 - 20, 2, mid_z + 16), ROAD_EDGE)
    add_fill(commands, f"{label} cross road z", (mid_x - 16, 2, z1 + 20), (mid_x + 16, 2, z2 - 20), ROAD_EDGE)
    colors = [MARKET_RED, MARKET_BLUE, MARKET_YELLOW, WOOD]
    index = 0
    for x in range(x1 + 70, x2 - 80, 110):
        for z in range(z1 + 70, z2 - 80, 90):
            color = colors[index % len(colors)]
            add_fill(commands, f"{label} booth {index}", (x, 2, z), (x + 42, 8, z + 28), color)
            add_fill(commands, f"{label} booth roof {index}", (x - 5, 9, z - 5), (x + 47, 11, z + 33), ROOF)
            index += 1


def build_commands() -> list[str]:
    commands: list[str] = []
    commands.append(f"/tp BuilderBot {PASTE['x']} {PASTE['y'] + 90} {PASTE['z']}")
    commands.append("/gamerule doMobSpawning false")
    commands.append("/gamerule randomTickSpeed 0")
    commands.append("/weather clear")
    commands.append("/time set day")

    # Ground is tiled instead of one giant fill, keeping every command below vanilla fill limits.
    tile = 250
    for x in range(0, CITY_SIZE, tile):
        for z in range(0, CITY_SIZE, tile):
            add_fill(commands, "city ground tile", (x, 0, z), (min(CITY_SIZE - 1, x + tile - 1), 0, min(CITY_SIZE - 1, z + tile - 1)), GROUND)

    # Outer moat and wall.
    add_outline(commands, "outer moat", -90, -90, CITY_SIZE + 89, CITY_SIZE + 89, 0, 0, WATER, thickness=48)
    add_outline(commands, "outer rammed-earth wall core", 0, 0, CITY_SIZE - 1, CITY_SIZE - 1, 1, 26, MOSS, thickness=30)
    add_outline(commands, "outer wall stone facing", 0, 0, CITY_SIZE - 1, CITY_SIZE - 1, 27, 34, STONE, thickness=34)
    add_outline(commands, "outer wall battlement", 0, 0, CITY_SIZE - 1, CITY_SIZE - 1, 35, 39, DARK, thickness=10)
    add_outline(commands, "wall walk", 34, 34, CITY_SIZE - 35, CITY_SIZE - 35, 35, 35, ROAD_EDGE, thickness=12)

    # Twelve symbolic gates.
    for x, name in [(1200, "south-west yanping"), (3000, "south zhuque"), (4800, "south-east qixia")]:
        add_gate(commands, name, x, 0, "north_south")
        add_gate(commands, name.replace("south", "north"), x, CITY_SIZE - 1, "north_south")
    for z, name in [(1500, "west kaiyuan"), (3000, "west jinguang"), (4500, "west yanshou")]:
        add_gate(commands, name, 0, z, "east_west")
        add_gate(commands, name.replace("west", "east"), CITY_SIZE - 1, z, "east_west")

    # Corner towers.
    add_tower(commands, "north-west corner tower", 80, CITY_SIZE - 81, 34, 54)
    add_tower(commands, "north-east corner tower", CITY_SIZE - 81, CITY_SIZE - 81, 34, 54)
    add_tower(commands, "south-west corner tower", 80, 80, 34, 54)
    add_tower(commands, "south-east corner tower", CITY_SIZE - 81, 80, 34, 54)

    # Chang'an axial roads and grid.
    add_fill(commands, "zhuque avenue", (2928, 1, 0), (3072, 2, CITY_SIZE - 1), ROAD)
    add_fill(commands, "zhuque avenue center lamps", (2996, 3, 0), (3004, 4, CITY_SIZE - 1), LANTERN)
    for x in [900, 1800, 3000, 4200, 5100]:
        add_fill(commands, f"north-south avenue {x}", (x - 32, 1, 80), (x + 32, 2, CITY_SIZE - 81), ROAD)
    for z in [900, 1700, 2500, 3300, 4100, 5000]:
        add_fill(commands, f"east-west avenue {z}", (80, 1, z - 32), (CITY_SIZE - 81, 2, z + 32), ROAD)

    # Palace city and imperial city.
    add_outline(commands, "imperial city wall", 1800, 4100, 4200, 5820, 1, 22, STONE, thickness=24)
    add_outline(commands, "palace city wall", 2140, 4750, 3860, 5780, 1, 30, RED, thickness=26)
    add_gate(commands, "chengtian gate", 3000, 4100, "north_south")
    add_gate(commands, "danfeng gate", 3000, 4750, "north_south")
    add_hall(commands, "hanyuan hall", 2660, 5180, 3340, 5480, 56)
    add_hall(commands, "xuanzheng hall", 2740, 4880, 3260, 5080, 44)
    add_hall(commands, "taiji palace", 2360, 5200, 2620, 5480, 40)
    add_hall(commands, "east palace office", 3380, 4930, 3700, 5200, 34, block="minecraft:white_concrete")
    add_hall(commands, "west palace office", 2300, 4930, 2620, 5200, 34, block="minecraft:white_concrete")

    # East and West markets.
    add_market(commands, "west market", 760, 2060, 1760, 3060)
    add_market(commands, "east market", 4240, 2060, 5240, 3060)

    # Representative wards. Full 6000 layout uses visible walls around large blocks, not filled housing.
    ward_index = 0
    x_lines = [520, 900, 1280, 1660, 2040, 2420, 3420, 3800, 4180, 4560, 4940, 5320]
    z_lines = [620, 1020, 1420, 1820, 2220, 2620, 3020, 3420, 3820]
    for x in x_lines:
        for z in z_lines:
            if 1800 <= x <= 4200 and z >= 4100:
                continue
            if 700 <= x <= 1800 and 2000 <= z <= 3100:
                continue
            if 4200 <= x <= 5300 and 2000 <= z <= 3100:
                continue
            add_outline(commands, f"ward wall {ward_index}", x, z, x + 260, z + 260, 1, 7, STONE, thickness=5)
            add_fill(commands, f"ward gate road {ward_index}", (x + 112, 1, z), (x + 148, 1, z + 260), ROAD_EDGE)
            if ward_index % 5 == 0:
                add_hall(commands, f"ward temple {ward_index}", x + 74, z + 82, x + 186, z + 166, 22, block="minecraft:yellow_terracotta")
            elif ward_index % 3 == 0:
                add_fill(commands, f"ward courtyard {ward_index}", (x + 65, 2, z + 70), (x + 195, 8, z + 160), WOOD)
                add_fill(commands, f"ward courtyard roof {ward_index}", (x + 55, 9, z + 60), (x + 205, 12, z + 170), ROOF)
            ward_index += 1

    # Landmark religious/civic accents.
    add_tower(commands, "giant wild goose pagoda symbol", 4580, 3860, 44, 92)
    add_tower(commands, "small wild goose pagoda symbol", 1320, 3700, 34, 70)
    add_hall(commands, "ancestral temple", 920, 4480, 1280, 4720, 34, block="minecraft:yellow_terracotta")
    add_hall(commands, "state altar", 4720, 4480, 5080, 4720, 28, block="minecraft:quartz_bricks")

    commands.append(f"/setworldspawn {SPAWN['x']} {SPAWN['y']} {SPAWN['z']}")
    commands.append(f"/tp @a {SPAWN['x']} {SPAWN['y']} {SPAWN['z']}")
    return commands


def write_project(commands: list[str]) -> dict:
    project_dir = settings.project_dir / PROJECT_ID
    project_dir.mkdir(parents=True, exist_ok=True)
    commands_path = project_dir / "commands.json"
    design_path = project_dir / "design.json"
    commands_path.write_text(json.dumps({"commands": commands}, ensure_ascii=False, indent=2), encoding="utf-8")

    placement = {
        "paste": PASTE,
        "spawn": SPAWN,
        "bounds": {
            "min_x": PASTE["x"] - 90,
            "min_y": PASTE["y"],
            "min_z": PASTE["z"] - 90,
            "max_x": PASTE["x"] + CITY_SIZE + 89,
            "max_y": PASTE["y"] + 110,
            "max_z": PASTE["z"] + CITY_SIZE + 89,
        },
    }
    design = {
        "id": PROJECT_ID,
        "name": NAME,
        "city_size": [CITY_SIZE, CITY_SIZE],
        "style": "Tang Chang'an inspired imperial grid city",
        "placement": placement,
        "modules": [
            {"name": "outer_city_wall_and_moat", "role": "structure", "bbox": [[-90, 0, -90], [6089, 39, 6089]]},
            {"name": "zhuque_avenue_axis", "role": "circulation", "bbox": [[2928, 1, 0], [3072, 4, 5999]]},
            {"name": "imperial_city", "role": "architecture", "bbox": [[1800, 1, 4100], [4200, 64, 5820]]},
            {"name": "palace_city", "role": "architecture", "bbox": [[2140, 1, 4750], [3860, 100, 5780]]},
            {"name": "east_market", "role": "architecture", "bbox": [[4240, 1, 2060], [5240, 16, 3060]]},
            {"name": "west_market", "role": "architecture", "bbox": [[760, 1, 2060], [1760, 16, 3060]]},
            {"name": "ward_grid", "role": "architecture", "bbox": [[520, 1, 620], [5580, 24, 4080]]},
        ],
        "quality_checks": [
            "6000x6000 overall planning footprint",
            "north palace and south gate align on Zhuque Avenue",
            "east/west markets sit symmetrically around the central axis",
            "ward walls form a readable chessboard city",
            "all large fills are split into safe command segments",
        ],
        "performance_budget": {
            "animated": False,
            "max_tick_commands": 0,
            "suggested_view_distance": 8,
            "min_server_memory_mb": 2048,
            "notes": ["Use low view-distance during construction; add ward interiors in later batches."],
        },
        "command_count": len(commands),
    }
    design_path.write_text(json.dumps(design, ensure_ascii=False, indent=2), encoding="utf-8")

    state = {
        "id": PROJECT_ID,
        "status": "ready_to_build",
        "created_at": now(),
        "updated_at": now(),
        "image_path": None,
        "analysis": {
            "source": "code_generated_changan_city_v1",
            "selected_template": "custom_city_grid",
            "design_spec": {
                "building_type": "custom_city",
                "scale_intent": "6000x6000 Tang Chang'an inspired city skeleton built by segmented bot commands.",
                "grid": ["city footprint 6000x6000", "central axis x=3000", "major avenues every 800-1200 blocks", "ward cells about 260x260"],
                "modules": design["modules"],
                "quality_checks": design["quality_checks"],
                "performance_budget": design["performance_budget"],
            },
        },
        "messages": [
            {
                "role": "user",
                "content": "设计一座 6000x6000 的长安城，不用网页，直接让 bot 建造。",
                "created_at": now(),
            },
            {
                "role": "assistant",
                "content": "已生成长安城一期施工设计：外郭城、护城河、十二城门、朱雀大街、宫城皇城、东西市、坊市网格和代表建筑。",
                "created_at": now(),
            },
        ],
        "plan": None,
        "plan_path": app_path(design_path),
        "schematic_path": None,
        "preview_path": None,
        "surface_preview_path": None,
        "materials_path": None,
        "analysis_report_path": None,
        "commands_path": app_path(commands_path),
        "placement": placement,
        "rcon": [],
        "error": None,
    }
    (project_dir / "state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"project_id": PROJECT_ID, "command_count": len(commands), "commands_path": str(commands_path), "design_path": str(design_path), "placement": placement}


def main() -> None:
    settings.project_dir.mkdir(parents=True, exist_ok=True)
    commands = build_commands()
    print(json.dumps(write_project(commands), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
