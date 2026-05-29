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
from backend.config import settings
from backend.dsl.schema import BuildPlan
from backend.main import _allocate_placement
from backend.schematic.generator import generate_outputs, render_plan_to_blocks


PROJECT_ID = "canton_tower_superheight_v1"
NAME = f"project_{PROJECT_ID}"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def box(parts: list[dict], a: tuple[int, int, int], b: tuple[int, int, int], block: str, hollow: bool = False) -> None:
    parts.append({"type": "box", "from": list(a), "to": list(b), "block": block, "hollow": hollow})


def blocks(parts: list[dict], points: list[tuple[int, int, int, str]]) -> None:
    parts.append({"type": "blocks", "blocks": [{"pos": [x, y, z], "block": block} for x, y, z, block in points]})


def _twisted_radius(t: float, base: int, waist: int, top: int, waist_t: float) -> float:
    if t <= waist_t:
        local = t / max(0.01, waist_t)
        eased = local * local * (3 - 2 * local)
        return base + (waist - base) * eased
    local = (t - waist_t) / max(0.01, 1 - waist_t)
    eased = local * local * (3 - 2 * local)
    return waist + (top - waist) * eased


RAINBOW_GLASS = [
    "rainbow_red",
    "rainbow_orange",
    "rainbow_yellow",
    "rainbow_green",
    "rainbow_cyan",
    "rainbow_blue",
    "rainbow_purple",
]

RAINBOW_BACKLIGHT = [
    "red_light",
    "orange_light",
    "yellow_light",
    "green_light",
    "cyan_light",
    "blue_light",
    "purple_light",
]


def _rainbow_pair(t: float, index: int, y: int, layer_struts: int) -> tuple[str, str]:
    vertical_band = int(t * len(RAINBOW_GLASS) * 1.35)
    spiral_band = int((index / max(1, layer_struts)) * len(RAINBOW_GLASS) + y / 21)
    color_index = (vertical_band + spiral_band) % len(RAINBOW_GLASS)
    return RAINBOW_GLASS[color_index], RAINBOW_BACKLIGHT[color_index]


def add_twisted_shell_skin(
    parts: list[dict],
    *,
    center: tuple[int, int, int],
    body_y1: int,
    body_height: int,
    y1: int,
    y2: int,
    base_radius: int,
    waist_radius: int,
    top_radius: int,
    waist_y_ratio: float,
    z_radius_scale: float,
    twist_degrees: float,
    struts: int,
) -> None:
    cx, _, cz = center
    twist = math.radians(twist_degrees)
    for y in range(y1, y2 + 1, 3):
        t = (y - body_y1) / max(1, body_height)
        t = max(0.0, min(1.0, t))
        rx = _twisted_radius(t, base_radius, waist_radius, top_radius, waist_y_ratio)
        rz = max(2.0, rx * z_radius_scale)
        angle_offset = twist * t
        layer_struts = max(24, struts + (10 if y >= y1 + 140 else 0))
        for index in range(layer_struts):
            angle = math.tau * index / layer_struts + angle_offset
            x = cx + round(math.cos(angle) * rx)
            z = cz + round(math.sin(angle) * rz)
            glass_block, light_block = _rainbow_pair(t, index, y, layer_struts)
            inner_x = cx + round(math.cos(angle) * max(2.0, rx - 1.5))
            inner_z = cz + round(math.sin(angle) * max(2.0, rz - 1.5))
            box(parts, (inner_x, y, inner_z), (inner_x, y, inner_z), light_block)
            box(parts, (x, y, z), (x, y, z), glass_block)
            if y % 12 in (0, 1, 2) and index % 2 == 0:
                box(parts, (inner_x, y + 1, inner_z), (inner_x, y + 1, inner_z), light_block)
            if y >= y1 + 128 and index % 4 == 0:
                box(parts, (x, y + 1, z), (x, y + 1, z), glass_block)


def add_rainbow_show_bands(parts: list[dict], *, center: tuple[int, int, int]) -> None:
    cx, _, cz = center
    # Broad horizontal media bands, matching the way night photos read as stacked colored light zones.
    band_specs = [
        (46, 58, 31, 24, "rainbow_red", "red_light"),
        (82, 94, 25, 20, "rainbow_orange", "orange_light"),
        (118, 130, 19, 15, "rainbow_yellow", "yellow_light"),
        (154, 166, 13, 10, "rainbow_green", "green_light"),
        (196, 208, 11, 9, "rainbow_cyan", "cyan_light"),
        (238, 250, 14, 11, "rainbow_blue", "blue_light"),
        (286, 300, 19, 15, "rainbow_purple", "purple_light"),
        (330, 344, 23, 18, "rainbow_red", "red_light"),
    ]
    for y1, y2, rx, rz, glass_block, light_block in band_specs:
        for y in range(y1, y2 + 1, 2):
            for index in range(56):
                angle = math.tau * index / 56 + y * 0.025
                x = cx + round(math.cos(angle) * rx)
                z = cz + round(math.sin(angle) * rz)
                inner_x = cx + round(math.cos(angle) * max(2, rx - 1))
                inner_z = cz + round(math.sin(angle) * max(2, rz - 1))
                box(parts, (inner_x, y, inner_z), (inner_x, y, inner_z), light_block)
                box(parts, (x, y, z), (x, y, z), glass_block)

    # Vertical ribbon strips make the facade read as an LED media screen, not only colored rings.
    for ribbon in range(7):
        glass_block = RAINBOW_GLASS[ribbon]
        light_block = RAINBOW_BACKLIGHT[ribbon]
        angle_base = math.tau * ribbon / 7
        for y in range(32, 354, 4):
            t = (y - 8) / 360
            rx = _twisted_radius(max(0.0, min(1.0, t)), 32, 10, 22, 0.56)
            rz = max(2.0, rx * 0.78)
            angle = angle_base + math.radians(170) * t + y * 0.011
            x = cx + round(math.cos(angle) * rx)
            z = cz + round(math.sin(angle) * rz)
            inner_x = cx + round(math.cos(angle) * max(2.0, rx - 1.5))
            inner_z = cz + round(math.sin(angle) * max(2.0, rz - 1.5))
            box(parts, (inner_x, y, inner_z), (inner_x, y, inner_z), light_block)
            box(parts, (x, y, z), (x, y + 1, z), glass_block)


def add_minecraft_view_details(parts: list[dict]) -> None:
    # Ground-level details make the tower readable from mobile view distance.
    for radius, block in [(42, "rainbow_red"), (38, "rainbow_orange"), (34, "rainbow_yellow"), (30, "rainbow_green")]:
        for index in range(80):
            angle = math.tau * index / 80
            x = 48 + round(math.cos(angle) * radius)
            z = 48 + round(math.sin(angle) * radius)
            box(parts, (x, 2, z), (x, 2, z), block)
    for radius, block in [(26, "cyan_light"), (22, "blue_light"), (18, "purple_light")]:
        for index in range(64):
            angle = math.tau * index / 64
            x = 48 + round(math.cos(angle) * radius)
            z = 48 + round(math.sin(angle) * radius)
            box(parts, (x, 3, z), (x, 3, z), block)

    # Observation deck rims and balcony lights.
    for y, radius, glass_block, light_block in [
        (274, 27, "rainbow_cyan", "cyan_light"),
        (286, 25, "rainbow_blue", "blue_light"),
        (330, 23, "rainbow_purple", "purple_light"),
        (342, 21, "rainbow_red", "red_light"),
    ]:
        for index in range(72):
            angle = math.tau * index / 72
            x = 48 + round(math.cos(angle) * radius)
            z = 48 + round(math.sin(angle) * max(3, radius * 0.78))
            box(parts, (x, y, z), (x, y, z), glass_block)
            if index % 2 == 0:
                box(parts, (x, y + 1, z), (x, y + 1, z), light_block)

    # Antenna aircraft warning lights and beacon-like top markers.
    for y in range(374, 456, 10):
        block = "red_light" if (y // 10) % 2 == 0 else "white_beacon"
        box(parts, (48, y, 48), (48, y, 48), block)
        box(parts, (47, y, 48), (49, y, 48), block)
        box(parts, (48, y, 47), (48, y, 49), block)

    # Simple pixel glyphs on four faces so the light show reads as a media screen.
    glyph_points: list[tuple[int, int, int, str]] = []
    for y in range(104, 188, 8):
        color = RAINBOW_GLASS[((y - 104) // 8) % len(RAINBOW_GLASS)]
        glyph_points.extend([(48, y, 20, color), (48, y, 76, color), (20, y, 48, color), (76, y, 48, color)])
        if y % 16 == 0:
            glyph_points.extend([(44, y, 20, "yellow_light"), (52, y, 20, "yellow_light"), (44, y, 76, "yellow_light"), (52, y, 76, "yellow_light")])
    blocks(parts, glyph_points)


def build_plan() -> BuildPlan:
    parts: list[dict] = []

    # Low plaza and podium. The tower itself is deliberately slender and tall.
    box(parts, (0, 0, 0), (95, 1, 95), "plaza")
    box(parts, (22, 2, 22), (73, 6, 73), "podium", hollow=True)
    box(parts, (30, 7, 30), (65, 13, 65), "observation", hollow=True)

    parts.append(
        {
            "type": "twisted_lattice_tower",
            "center": [48, 8, 48],
            "body_height": 360,
            "antenna_height": 88,
            "base_radius": 32,
            "waist_radius": 10,
            "top_radius": 22,
            "waist_y_ratio": 0.56,
            "z_radius_scale": 0.78,
            "ring_interval": 8,
            "struts": 36,
            "twist_degrees": 170,
            "lattice": "lattice",
            "ring": "ring",
            "glass": "glass",
            "core": "core",
            "light": "night_light",
        }
    )

    # Observation decks and top cap emphasize the real tower's upper functional zone.
    box(parts, (25, 272, 25), (71, 282, 71), "observation", hollow=True)
    box(parts, (27, 283, 27), (69, 290, 69), "media_blue", hollow=True)
    box(parts, (30, 328, 30), (66, 338, 66), "observation", hollow=True)
    box(parts, (32, 339, 32), (64, 346, 64), "media_purple", hollow=True)
    box(parts, (35, 356, 35), (61, 364, 61), "ring", hollow=True)
    add_twisted_shell_skin(
        parts,
        center=(48, 8, 48),
        body_y1=8,
        body_height=360,
        y1=24,
        y2=360,
        base_radius=32,
        waist_radius=10,
        top_radius=22,
        waist_y_ratio=0.56,
        z_radius_scale=0.78,
        twist_degrees=170,
        struts=36,
    )
    add_twisted_shell_skin(
        parts,
        center=(48, 8, 48),
        body_y1=8,
        body_height=360,
        y1=364,
        y2=456,
        base_radius=22,
        waist_radius=16,
        top_radius=11,
        waist_y_ratio=0.56,
        z_radius_scale=0.76,
        twist_degrees=170,
        struts=30,
    )
    add_rainbow_show_bands(parts, center=(48, 8, 48))
    add_minecraft_view_details(parts)

    # Dense LED nodes and media bands. Canton Tower reads as a self-lit screen at night.
    points: list[tuple[int, int, int, str]] = []
    for y in range(24, 360, 12):
        points.extend(
            [
                (48, y, 17, "night_light"),
                (48, y, 79, "night_light"),
                (17, y, 48, "night_light"),
                (79, y, 48, "night_light"),
            ]
        )
    for y in range(64, 352, 24):
        for x in range(30, 67, 6):
            points.append((x, y, 22, "media_blue"))
            points.append((x, y + 2, 74, "media_purple"))
        for z in range(30, 67, 6):
            points.append((22, y + 4, z, "media_green"))
            points.append((74, y + 6, z, "media_red"))
    for x in range(18, 79, 6):
        points.append((x, 2, 12, "night_light"))
        points.append((x, 2, 84, "night_light"))
    for z in range(18, 79, 6):
        points.append((12, 2, z, "night_light"))
        points.append((84, 2, z, "night_light"))
    blocks(parts, points)

    plan = {
        "name": NAME,
        "size": [96, 464, 96],
        "origin": [0, 64, 0],
        "palette": {
            "lattice": "iron_block",
            "ring": "light_gray_concrete",
            "glass": "light_blue_stained_glass",
            "core": "white_concrete",
            "observation": "cyan_stained_glass",
            "night_light": "sea_lantern",
            "screen_light": "sea_lantern",
            "media_blue": "blue_stained_glass",
            "media_purple": "purple_stained_glass",
            "media_green": "lime_stained_glass",
            "media_red": "red_stained_glass",
            "rainbow_red": "red_stained_glass",
            "rainbow_orange": "orange_stained_glass",
            "rainbow_yellow": "yellow_stained_glass",
            "rainbow_green": "lime_stained_glass",
            "rainbow_cyan": "cyan_stained_glass",
            "rainbow_blue": "blue_stained_glass",
            "rainbow_purple": "purple_stained_glass",
            "red_light": "redstone_lamp",
            "orange_light": "shroomlight",
            "yellow_light": "glowstone",
            "green_light": "sea_lantern",
            "cyan_light": "sea_lantern",
            "blue_light": "sea_lantern",
            "purple_light": "sea_lantern",
            "white_beacon": "beacon",
            "podium": "smooth_quartz",
            "plaza": "smooth_stone",
        },
        "analysis": {
            "source": "code_generated_canton_tower_v2",
            "selected_template": "twisted_lattice_tower",
            "component_strategy": [
                "Use twisted_lattice_tower instead of pagoda_stack because Guangzhou Tower is a modern hyperboloid lattice TV tower.",
                "Avoid pagoda_tier, eaves, copper roofs, and gold spires.",
            ],
            "design_spec": {
                "building_type": "guangzhou_tower",
                "scale_intent": "96w x 464h x 96d in the superheight world; paste y=40 reaches top y=503, below Bedrock-safe top y=511.",
                "grid": [
                    "center at [48, y, 48]",
                    "body height 360 blocks from y=8 to y=368",
                    "antenna extends 88 blocks above body",
                    "base radius 32, waist radius 10 at 56% height, top radius 22",
                    "36 rotating lattice struts, ring every 8 blocks",
                    "rainbow LED skin follows the tower curvature from base to top",
                    "broad horizontal rainbow media bands and spiral vertical ribbons",
                ],
                "modules": [
                    {
                        "name": "plaza_podium",
                        "role": "foundation",
                        "bbox": [[0, 0, 0], [95, 13, 95]],
                        "materials": ["plaza", "podium", "observation"],
                    },
                    {
                        "name": "hyperboloid_lattice_body",
                        "role": "structure",
                        "bbox": [[16, 8, 23], [80, 368, 73]],
                        "materials": ["lattice", "ring", "glass", "core", "night_light"],
                    },
                    {
                        "name": "observation_decks",
                        "role": "facade",
                        "bbox": [[25, 272, 25], [71, 364, 71]],
                        "materials": ["observation", "ring", "media_blue", "media_purple"],
                    },
                    {
                        "name": "antenna_mast",
                        "role": "detail",
                        "bbox": [[47, 369, 47], [49, 456, 49]],
                        "materials": ["lattice", "ring", "night_light"],
                    },
                    {
                        "name": "rainbow_led_media_skin",
                        "role": "lighting",
                        "bbox": [[12, 24, 12], [84, 360, 84]],
                        "materials": ["red_light", "orange_light", "yellow_light", "green_light", "cyan_light", "blue_light", "purple_light", "rainbow_red", "rainbow_orange", "rainbow_yellow", "rainbow_green", "rainbow_cyan", "rainbow_blue", "rainbow_purple"],
                    },
                ],
                "interfaces": [
                    {
                        "module_a": "plaza_podium",
                        "face_a": "top",
                        "module_b": "hyperboloid_lattice_body",
                        "face_b": "bottom",
                        "kind": "support",
                        "note": "lattice starts from the podium center",
                    },
                    {
                        "module_a": "hyperboloid_lattice_body",
                        "face_a": "top",
                        "module_b": "antenna_mast",
                        "face_b": "bottom",
                        "kind": "touch",
                        "note": "antenna continues from body top",
                    },
                ],
                "material_schedule": [
                    "lattice=iron_block for silver structural mesh",
                    "ring=light_gray_concrete for horizontal deck bands",
                    "glass/light_blue_stained_glass for observation skin",
                    "night_light=sea_lantern for visible luminous nodes",
                    "colored stained glass plus hidden light blocks for a rainbow LED facade",
                    "red/orange/yellow/green/cyan/blue/purple bands for night light-show effect",
                    "rainbow screen skin follows the tower curvature instead of a rectangular box",
                ],
                "quality_checks": [
                    "height_to_width > 2.5",
                    "waist radius much smaller than base radius",
                    "twisted diagonal lattice visible",
                    "night facade reads as rainbow LED light show with colored horizontal and vertical bands",
                    "no pagoda eaves or ancient spire",
                ],
            },
            "massing": ["slender hyperboloid", "narrow waist", "upper observation decks", "antenna mast"],
            "facade": ["rotating silver lattice", "cyan glass decks", "rainbow LED pixel skin", "horizontal rainbow media bands", "spiral vertical light ribbons"],
            "changes": ["superheight version for Bedrock-safe y<=511 world", "switches from mostly white LED skin to rainbow night light-show facade", "adds colored glass pixels backed by light blocks"],
        },
        "parts": parts,
    }
    return BuildPlan.model_validate(plan)


def main() -> None:
    settings.project_dir.mkdir(parents=True, exist_ok=True)
    settings.schematic_dir.mkdir(parents=True, exist_ok=True)
    project_dir = settings.project_dir / PROJECT_ID
    project_dir.mkdir(parents=True, exist_ok=True)

    plan = build_plan()
    rendered = render_plan_to_blocks(plan)
    schematic_path, preview_path, material_path = generate_outputs(
        plan,
        schematic_dir=settings.schematic_dir,
        preview_dir=project_dir,
        max_preview_blocks=220_000,
        blocks=rendered,
    )
    analysis_report = analyze_build(plan, rendered)
    analysis_report_path = project_dir / f"{NAME}.analysis.json"
    analysis_report_path.write_text(json.dumps(analysis_report, ensure_ascii=False, indent=2), encoding="utf-8")
    placement = _allocate_placement(PROJECT_ID, plan)
    placement = {
        **placement,
        "paste": {"x": 3400, "y": 40, "z": 900},
        "spawn": {"x": 3448, "y": 120, "z": 850},
        "bounds": {
            "min_x": 3400,
            "min_y": 40,
            "min_z": 900,
            "max_x": 3495,
            "max_y": 503,
            "max_z": 995,
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
                "content": "广州塔/小蛮腰超高版：在 superheight 世界里做 460 格左右，夜景要复刻彩虹 LED 灯光秀，整塔有多色屏幕和灯带。",
                "created_at": now(),
            },
            {"role": "assistant", "content": "已生成广州塔彩虹夜景版：高瘦双曲面格构塔，带彩虹 LED 外壳、横向媒体屏带和螺旋竖向灯带。", "created_at": now()},
        ],
        "plan": plan.model_dump(by_alias=True, mode="json"),
        "plan_path": str(project_dir / "plan.json"),
        "schematic_path": str(schematic_path),
        "preview_path": str(preview_path),
        "materials_path": str(material_path),
        "analysis_report_path": str(analysis_report_path),
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
                "size": plan.size,
                "analysis_report": analysis_report,
                "schematic": str(schematic_path),
                "preview": str(preview_path),
                "materials": str(material_path),
                "placement": placement,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
