from __future__ import annotations

import json
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
            "night_light": "redstone_lamp",
            "media_blue": "blue_stained_glass",
            "media_purple": "purple_stained_glass",
            "media_green": "lime_stained_glass",
            "media_red": "red_stained_glass",
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
                    "LED nodes every 12 blocks and media bands every 24 blocks",
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
                        "name": "led_media_skin",
                        "role": "lighting",
                        "bbox": [[12, 24, 12], [84, 360, 84]],
                        "materials": ["night_light", "media_blue", "media_purple", "media_green", "media_red"],
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
                    "night_light=redstone_lamp for red lattice nodes",
                    "blue/purple/lime/red stained glass for large LED screen color bands",
                ],
                "quality_checks": [
                    "height_to_width > 2.5",
                    "waist radius much smaller than base radius",
                    "twisted diagonal lattice visible",
                    "night facade has dense LED nodes and colored media bands",
                    "no pagoda eaves or ancient spire",
                ],
            },
            "massing": ["slender hyperboloid", "narrow waist", "upper observation decks", "antenna mast"],
            "facade": ["rotating silver lattice", "cyan glass decks", "red night light points", "colored LED media bands"],
            "changes": ["superheight version for Bedrock-safe y<=511 world", "adds dense night lighting and screen-like colored LED bands"],
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
        "analysis": plan.analysis,
        "messages": [
            {
                "role": "user",
                "content": "广州塔/小蛮腰超高版：在 superheight 世界里做 460 格左右，夜景要有大量灯光设备和屏幕灯带。",
                "created_at": now(),
            },
            {"role": "assistant", "content": "已生成广州塔超高版：高瘦双曲面格构塔，带密集夜景灯光和媒体屏带。", "created_at": now()},
        ],
        "plan": plan.model_dump(by_alias=True),
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
