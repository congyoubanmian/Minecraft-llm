from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.analysis import analyze_build
from backend.blocks import BlockList
from backend.config import settings
from backend.dsl.schema import BuildPlan
from backend.schematic.generator import generate_outputs


PROJECT_ID = "canton_tower_superheight_v3"
NAME = f"project_{PROJECT_ID}"

SIZE = (112, 472, 112)
CX = 56
CZ = 56
BODY_BASE_Y = 10
BODY_HEIGHT = 365
ANTENNA_HEIGHT = 88
PASTE = {"x": 3600, "y": 36, "z": 900}
SPAWN = {"x": 3656, "y": 118, "z": 820}

LED_GLASS = [
    "minecraft:red_stained_glass",
    "minecraft:orange_stained_glass",
    "minecraft:yellow_stained_glass",
    "minecraft:lime_stained_glass",
    "minecraft:cyan_stained_glass",
    "minecraft:blue_stained_glass",
    "minecraft:purple_stained_glass",
]
LED_LIGHTS = [
    "minecraft:redstone_lamp[lit=true]",
    "minecraft:shroomlight",
    "minecraft:glowstone",
    "minecraft:sea_lantern",
    "minecraft:sea_lantern",
    "minecraft:sea_lantern",
    "minecraft:sea_lantern",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def app_path(path: Path) -> str:
    if path.is_relative_to(ROOT):
        return str(Path("/app") / path.relative_to(ROOT))
    return str(path)


def radius_at(t: float) -> float:
    """Canton Tower-like hyperboloid: broad lower bowl, narrow waist, flared head."""
    t = max(0.0, min(1.0, t))
    waist_t = 0.58
    if t <= waist_t:
        local = t / waist_t
        eased = local * local * (3 - 2 * local)
        return 37 + (8.5 - 37) * eased
    local = (t - waist_t) / (1 - waist_t)
    eased = local * local * (3 - 2 * local)
    return 8.5 + (24 - 8.5) * eased


def z_radius_at(t: float) -> float:
    return max(4.0, radius_at(t) * 0.76)


def set_block(blocks: BlockList, x: int, y: int, z: int, block: str) -> None:
    if 0 <= x < SIZE[0] and 0 <= y < SIZE[1] and 0 <= z < SIZE[2]:
        blocks.set_block((x, y, z), block)


def fill(blocks: BlockList, a: tuple[int, int, int], b: tuple[int, int, int], block: str, *, hollow: bool = False) -> None:
    x1, y1, z1 = a
    x2, y2, z2 = b
    min_x, max_x = sorted((x1, x2))
    min_y, max_y = sorted((y1, y2))
    min_z, max_z = sorted((z1, z2))
    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            for z in range(min_z, max_z + 1):
                if hollow and min_x < x < max_x and min_y < y < max_y and min_z < z < max_z:
                    continue
                set_block(blocks, x, y, z, block)


def line(blocks: BlockList, start: tuple[int, int, int], end: tuple[int, int, int], block: str) -> None:
    x1, y1, z1 = start
    x2, y2, z2 = end
    steps = max(abs(x2 - x1), abs(y2 - y1), abs(z2 - z1), 1)
    for step in range(steps + 1):
        t = step / steps
        set_block(
            blocks,
            round(x1 + (x2 - x1) * t),
            round(y1 + (y2 - y1) * t),
            round(z1 + (z2 - z1) * t),
            block,
        )


def ring_points(y: int, count: int, *, offset: float = 0.0, inset: float = 0.0) -> list[tuple[int, int, int]]:
    t = (y - BODY_BASE_Y) / BODY_HEIGHT
    rx = max(2.0, radius_at(t) - inset)
    rz = max(2.0, z_radius_at(t) - inset * 0.76)
    points: list[tuple[int, int, int]] = []
    for index in range(count):
        angle = math.tau * index / count + offset
        points.append((CX + round(math.cos(angle) * rx), y, CZ + round(math.sin(angle) * rz)))
    return points


def draw_ellipse_ring(
    blocks: BlockList,
    y: int,
    rx: float,
    rz: float,
    block: str,
    *,
    count: int = 112,
    offset: float = 0.0,
    thickness: int = 1,
) -> None:
    for layer in range(thickness):
        local_rx = max(1, rx - layer)
        local_rz = max(1, rz - layer * 0.76)
        previous: tuple[int, int, int] | None = None
        first: tuple[int, int, int] | None = None
        for index in range(count + 1):
            angle = math.tau * (index % count) / count + offset
            point = (CX + round(math.cos(angle) * local_rx), y, CZ + round(math.sin(angle) * local_rz))
            if first is None:
                first = point
            if previous:
                line(blocks, previous, point, block)
            previous = point
        if previous and first:
            line(blocks, previous, first, block)


def build_plaza(blocks: BlockList) -> None:
    fill(blocks, (0, 0, 0), (111, 1, 111), "minecraft:smooth_stone")
    for radius, block in [
        (50, "minecraft:red_stained_glass"),
        (45, "minecraft:orange_stained_glass"),
        (40, "minecraft:yellow_stained_glass"),
        (35, "minecraft:lime_stained_glass"),
        (30, "minecraft:cyan_stained_glass"),
    ]:
        draw_ellipse_ring(blocks, 2, radius, radius * 0.76, block, count=144)

    fill(blocks, (24, 2, 24), (88, 8, 88), "minecraft:smooth_quartz", hollow=True)
    fill(blocks, (32, 9, 32), (80, 16, 80), "minecraft:cyan_stained_glass", hollow=True)
    for x in range(20, 93, 8):
        set_block(blocks, x, 3, 14, "minecraft:sea_lantern")
        set_block(blocks, x, 3, 98, "minecraft:sea_lantern")
    for z in range(20, 93, 8):
        set_block(blocks, 14, 3, z, "minecraft:sea_lantern")
        set_block(blocks, 98, 3, z, "minecraft:sea_lantern")


def build_lattice(blocks: BlockList) -> None:
    levels = list(range(BODY_BASE_Y, BODY_BASE_Y + BODY_HEIGHT + 1, 7))
    if levels[-1] != BODY_BASE_Y + BODY_HEIGHT:
        levels.append(BODY_BASE_Y + BODY_HEIGHT)

    rings: list[list[tuple[int, int, int]]] = []
    for y in levels:
        t = (y - BODY_BASE_Y) / BODY_HEIGHT
        offset = math.radians(205) * t
        count = 48
        points = ring_points(y, count, offset=offset)
        rings.append(points)
        draw_ellipse_ring(blocks, y, radius_at(t), z_radius_at(t), "minecraft:light_gray_concrete", count=144, offset=offset)

    for lower, upper in zip(rings, rings[1:]):
        count = len(lower)
        for index in range(count):
            if index % 2 == 0:
                line(blocks, lower[index], upper[(index + 3) % count], "minecraft:iron_block")
            if index % 2 == 1:
                line(blocks, lower[index], upper[(index - 3) % count], "minecraft:iron_block")

    # Thin white service core keeps the tower readable from below without filling the outer waist.
    for y in range(BODY_BASE_Y, BODY_BASE_Y + BODY_HEIGHT + 1):
        core_radius = 2 if y % 14 else 3
        for x in range(CX - core_radius, CX + core_radius + 1):
            for z in range(CZ - core_radius, CZ + core_radius + 1):
                if (x - CX) ** 2 + (z - CZ) ** 2 <= core_radius**2:
                    set_block(blocks, x, y, z, "minecraft:white_concrete")


def build_led_skin(blocks: BlockList) -> None:
    for y in range(24, 369, 3):
        t = (y - BODY_BASE_Y) / BODY_HEIGHT
        rx = radius_at(t)
        rz = z_radius_at(t)
        offset = math.radians(205) * t
        count = 112 if y < 260 else 128
        for index in range(count):
            angle = math.tau * index / count + offset
            color_index = (int(t * 10) + int(index / 8) + y // 24) % len(LED_GLASS)
            outer = (
                CX + round(math.cos(angle) * rx),
                y,
                CZ + round(math.sin(angle) * rz),
            )
            inner = (
                CX + round(math.cos(angle) * max(2, rx - 1.7)),
                y,
                CZ + round(math.sin(angle) * max(2, rz - 1.3)),
            )
            if index % 2 == 0:
                set_block(blocks, *inner, LED_LIGHTS[color_index])
            set_block(blocks, *outer, LED_GLASS[color_index])
            if y % 12 == 0 and index % 5 == 0:
                set_block(blocks, outer[0], y + 1, outer[2], LED_GLASS[color_index])

    # Wide horizontal LED belts based on night photos: the tower reads as stacked glowing bands.
    bands = [
        (38, 54, 36, "minecraft:red_stained_glass", "minecraft:redstone_lamp[lit=true]"),
        (80, 98, 30, "minecraft:orange_stained_glass", "minecraft:shroomlight"),
        (122, 140, 23, "minecraft:yellow_stained_glass", "minecraft:glowstone"),
        (164, 182, 15, "minecraft:lime_stained_glass", "minecraft:sea_lantern"),
        (210, 226, 9, "minecraft:cyan_stained_glass", "minecraft:sea_lantern"),
        (258, 276, 14, "minecraft:blue_stained_glass", "minecraft:sea_lantern"),
        (308, 328, 21, "minecraft:purple_stained_glass", "minecraft:sea_lantern"),
        (346, 362, 24, "minecraft:red_stained_glass", "minecraft:redstone_lamp[lit=true]"),
    ]
    for y1, y2, nominal_radius, glass, light in bands:
        for y in range(y1, y2 + 1, 2):
            t = (y - BODY_BASE_Y) / BODY_HEIGHT
            rx = max(nominal_radius, radius_at(t))
            rz = max(nominal_radius * 0.72, z_radius_at(t))
            for index in range(160):
                angle = math.tau * index / 160 + y * 0.018
                x = CX + round(math.cos(angle) * rx)
                z = CZ + round(math.sin(angle) * rz)
                set_block(blocks, CX + round(math.cos(angle) * (rx - 1)), y, CZ + round(math.sin(angle) * (rz - 1)), light)
                set_block(blocks, x, y, z, glass)

    # Spiral ribbons are deliberately thicker than real life so they survive phone render distance.
    for ribbon in range(9):
        glass = LED_GLASS[ribbon % len(LED_GLASS)]
        light = LED_LIGHTS[ribbon % len(LED_LIGHTS)]
        base_angle = math.tau * ribbon / 9
        for y in range(30, 366, 2):
            t = (y - BODY_BASE_Y) / BODY_HEIGHT
            angle = base_angle + math.radians(300) * t
            rx = radius_at(t) + 1
            rz = z_radius_at(t) + 1
            x = CX + round(math.cos(angle) * rx)
            z = CZ + round(math.sin(angle) * rz)
            set_block(blocks, x, y, z, glass)
            if y % 4 == 0:
                set_block(blocks, CX + round(math.cos(angle) * (rx - 1)), y, CZ + round(math.sin(angle) * (rz - 1)), light)


def build_observation_decks(blocks: BlockList) -> None:
    decks = [
        (278, 292, 29, 21, "minecraft:cyan_stained_glass", "minecraft:light_gray_concrete"),
        (324, 340, 27, 20, "minecraft:blue_stained_glass", "minecraft:light_gray_concrete"),
        (348, 363, 24, 18, "minecraft:purple_stained_glass", "minecraft:light_gray_concrete"),
    ]
    for y1, y2, rx, rz, glass, frame in decks:
        for y in range(y1, y2 + 1):
            draw_ellipse_ring(blocks, y, rx, rz, glass, count=144)
        draw_ellipse_ring(blocks, y1 - 1, rx + 1, rz + 1, frame, count=144, thickness=2)
        draw_ellipse_ring(blocks, y2 + 1, rx + 1, rz + 1, frame, count=144, thickness=2)
        for angle_index in range(0, 144, 8):
            angle = math.tau * angle_index / 144
            x = CX + round(math.cos(angle) * (rx + 1))
            z = CZ + round(math.sin(angle) * (rz + 1))
            for y in range(y1, y2 + 2, 5):
                set_block(blocks, x, y, z, "minecraft:sea_lantern")


def build_antenna(blocks: BlockList) -> None:
    body_top = BODY_BASE_Y + BODY_HEIGHT
    for y in range(body_top + 1, body_top + ANTENNA_HEIGHT + 1):
        set_block(blocks, CX, y, CZ, "minecraft:iron_block")
        if y < body_top + 38:
            set_block(blocks, CX + 1, y, CZ, "minecraft:iron_block")
            set_block(blocks, CX - 1, y, CZ, "minecraft:iron_block")
            set_block(blocks, CX, y, CZ + 1, "minecraft:iron_block")
            set_block(blocks, CX, y, CZ - 1, "minecraft:iron_block")
        if y % 10 == 0:
            set_block(blocks, CX, y, CZ, "minecraft:redstone_lamp[lit=true]")
            set_block(blocks, CX + 1, y, CZ, "minecraft:beacon")
            set_block(blocks, CX - 1, y, CZ, "minecraft:beacon")
            set_block(blocks, CX, y, CZ + 1, "minecraft:beacon")
            set_block(blocks, CX, y, CZ - 1, "minecraft:beacon")


def make_blocks() -> BlockList:
    blocks = BlockList()
    build_plaza(blocks)
    build_lattice(blocks)
    build_led_skin(blocks)
    build_observation_decks(blocks)
    build_antenna(blocks)
    return blocks


def make_preview_plan() -> BuildPlan:
    return BuildPlan.model_validate(
        {
            "name": NAME,
            "size": list(SIZE),
            "origin": [0, 64, 0],
            "palette": {
                "steel": "iron_block",
                "ring": "light_gray_concrete",
                "core": "white_concrete",
                "glass": "cyan_stained_glass",
                "red": "red_stained_glass",
                "orange": "orange_stained_glass",
                "yellow": "yellow_stained_glass",
                "green": "lime_stained_glass",
                "cyan": "cyan_stained_glass",
                "blue": "blue_stained_glass",
                "purple": "purple_stained_glass",
                "light": "sea_lantern",
                "plaza": "smooth_stone",
                "podium": "smooth_quartz",
            },
            "analysis": {
                "source": "code_generated_canton_tower_v3",
                "selected_template": "twisted_lattice_tower",
                "component_strategy": [
                    "Use the twisted_lattice_tower design template with a direct block renderer for a denser double-curved Canton Tower profile.",
                    "Separate plaza, hyperboloid lattice, LED skin, observation decks, and antenna so later LLM planning can revise modules independently.",
                ],
                "design_spec": {
                    "building_type": "guangzhou_tower",
                    "scale_intent": "112w x 472h x 112d superheight static night version; paste y=36 reaches top y=507.",
                    "modules": [
                        {"name": "plaza_podium", "bbox": [[0, 0, 0], [111, 16, 111]], "role": "foundation"},
                        {"name": "hyperboloid_lattice_body", "bbox": [[19, 10, 28], [93, 375, 84]], "role": "structure"},
                        {"name": "rainbow_led_media_skin", "bbox": [[18, 24, 27], [94, 369, 85]], "role": "lighting"},
                        {"name": "observation_decks", "bbox": [[26, 277, 35], [86, 364, 77]], "role": "facade"},
                        {"name": "antenna_mast", "bbox": [[55, 376, 55], [57, 463, 57]], "role": "detail"},
                    ],
                    "quality_checks": [
                        "very narrow waist is clearly smaller than base and head",
                        "outer LED points follow the curved shell, not a square tower",
                        "observation decks sit around the upper third",
                        "static lights are used instead of redstone animation to reduce lag",
                    ],
                },
            },
            "parts": [
                {"type": "box", "from": [0, 0, 0], "to": [111, 1, 111], "block": "plaza"},
                {"type": "box", "from": [24, 2, 24], "to": [88, 8, 88], "block": "podium", "hollow": True},
                {
                    "type": "twisted_lattice_tower",
                    "center": [CX, BODY_BASE_Y, CZ],
                    "body_height": BODY_HEIGHT,
                    "antenna_height": ANTENNA_HEIGHT,
                    "base_radius": 37,
                    "waist_radius": 9,
                    "top_radius": 24,
                    "waist_y_ratio": 0.58,
                    "z_radius_scale": 0.76,
                    "ring_interval": 7,
                    "struts": 48,
                    "twist_degrees": 205,
                    "lattice": "steel",
                    "ring": "ring",
                    "glass": "glass",
                    "core": "core",
                    "light": "light",
                },
            ],
        }
    )


def main() -> None:
    settings.project_dir.mkdir(parents=True, exist_ok=True)
    settings.schematic_dir.mkdir(parents=True, exist_ok=True)
    project_dir = settings.project_dir / PROJECT_ID
    project_dir.mkdir(parents=True, exist_ok=True)

    plan = make_preview_plan()
    blocks = make_blocks()
    schematic_path, preview_path, surface_preview_path, material_path = generate_outputs(
        plan,
        schematic_dir=settings.schematic_dir,
        preview_dir=project_dir,
        max_preview_blocks=240_000,
        blocks=blocks,
    )
    analysis_report = analyze_build(plan, blocks)
    analysis_report_path = project_dir / f"{NAME}.analysis.json"
    analysis_report_path.write_text(json.dumps(analysis_report, ensure_ascii=False, indent=2), encoding="utf-8")

    placement = {
        "paste": PASTE,
        "spawn": SPAWN,
        "bounds": {
            "min_x": PASTE["x"],
            "min_y": PASTE["y"],
            "min_z": PASTE["z"],
            "max_x": PASTE["x"] + SIZE[0] - 1,
            "max_y": PASTE["y"] + SIZE[1] - 1,
            "max_z": PASTE["z"] + SIZE[2] - 1,
        },
    }
    state = {
        "id": PROJECT_ID,
        "status": "done",
        "created_at": now(),
        "updated_at": now(),
        "image_path": None,
        "analysis": plan.analysis_dict(),
        "messages": [
            {
                "role": "user",
                "content": "重新做一个广州塔：更瘦、更高、腰部更细，夜景整塔彩虹 LED，手机可见距离下也要看得出小蛮腰。",
                "created_at": now(),
            },
            {
                "role": "assistant",
                "content": "已生成广州塔 v3：双曲格构塔身、静态彩虹 LED 外壳、上部观光舱和红色航空灯天线。",
                "created_at": now(),
            },
        ],
        "plan": plan.model_dump(by_alias=True, mode="json"),
        "plan_path": app_path(project_dir / "plan.json"),
        "schematic_path": app_path(schematic_path),
        "preview_path": app_path(preview_path),
        "surface_preview_path": app_path(surface_preview_path),
        "materials_path": app_path(material_path),
        "analysis_report_path": app_path(analysis_report_path),
        "analysis_report": analysis_report,
        "placement": placement,
        "rcon": [],
        "error": None,
        "completed_at": now(),
    }
    (project_dir / "plan.json").write_text(plan.model_dump_json(by_alias=True, indent=2), encoding="utf-8")
    (project_dir / "state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "project_id": PROJECT_ID,
                "size": SIZE,
                "block_count": len(blocks),
                "schematic": str(schematic_path),
                "preview": str(preview_path),
                "surface_preview": str(surface_preview_path),
                "materials": str(material_path),
                "placement": placement,
                "analysis_report": analysis_report,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
