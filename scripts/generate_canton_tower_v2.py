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


PROJECT_ID = "canton_tower_v2"
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
    box(parts, (0, 0, 0), (87, 1, 87), "plaza")
    box(parts, (22, 2, 22), (65, 5, 65), "podium", hollow=True)
    box(parts, (30, 6, 30), (57, 10, 57), "observation", hollow=True)

    parts.append(
        {
            "type": "twisted_lattice_tower",
            "center": [44, 6, 44],
            "body_height": 192,
            "antenna_height": 48,
            "base_radius": 28,
            "waist_radius": 9,
            "top_radius": 18,
            "waist_y_ratio": 0.56,
            "z_radius_scale": 0.78,
            "ring_interval": 7,
            "struts": 32,
            "twist_degrees": 150,
            "lattice": "lattice",
            "ring": "ring",
            "glass": "glass",
            "core": "core",
            "light": "night_light",
        }
    )

    # Observation decks and top cap emphasize the real tower's upper functional zone.
    box(parts, (27, 145, 27), (61, 151, 61), "observation", hollow=True)
    box(parts, (29, 152, 29), (59, 156, 59), "ring", hollow=True)
    box(parts, (32, 178, 32), (56, 184, 56), "observation", hollow=True)
    box(parts, (34, 185, 34), (54, 188, 54), "ring", hollow=True)

    # Thin red night lights on plaza axes and around observation decks.
    points: list[tuple[int, int, int, str]] = []
    for y in range(18, 196, 14):
        points.extend(
            [
                (44, y, 18, "night_light"),
                (44, y, 70, "night_light"),
                (18, y, 44, "night_light"),
                (70, y, 44, "night_light"),
            ]
        )
    for x in range(18, 71, 8):
        points.append((x, 2, 12, "night_light"))
        points.append((x, 2, 76, "night_light"))
    for z in range(18, 71, 8):
        points.append((12, 2, z, "night_light"))
        points.append((76, 2, z, "night_light"))
    blocks(parts, points)

    plan = {
        "name": NAME,
        "size": [88, 248, 88],
        "origin": [0, 64, 0],
        "palette": {
            "lattice": "iron_block",
            "ring": "light_gray_concrete",
            "glass": "light_blue_stained_glass",
            "core": "white_concrete",
            "observation": "cyan_stained_glass",
            "night_light": "redstone_lamp",
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
                "scale_intent": "88w x 248h x 88d; height is 2.82x width/depth to avoid the previous short and fat result.",
                "grid": [
                    "center at [44, y, 44]",
                    "body height 192 blocks from y=6 to y=198",
                    "antenna extends 48 blocks above body",
                    "base radius 28, waist radius 9 at 56% height, top radius 18",
                    "32 rotating lattice struts, ring every 7 blocks",
                ],
                "modules": [
                    {
                        "name": "plaza_podium",
                        "role": "foundation",
                        "bbox": [[0, 0, 0], [87, 10, 87]],
                        "materials": ["plaza", "podium", "observation"],
                    },
                    {
                        "name": "hyperboloid_lattice_body",
                        "role": "structure",
                        "bbox": [[16, 6, 22], [72, 198, 66]],
                        "materials": ["lattice", "ring", "glass", "core", "night_light"],
                    },
                    {
                        "name": "observation_decks",
                        "role": "facade",
                        "bbox": [[27, 145, 27], [61, 188, 61]],
                        "materials": ["observation", "ring"],
                    },
                    {
                        "name": "antenna_mast",
                        "role": "detail",
                        "bbox": [[43, 199, 43], [45, 246, 45]],
                        "materials": ["lattice", "ring", "night_light"],
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
                    "night_light=redstone_lamp for red night points",
                ],
                "quality_checks": [
                    "height_to_width > 2.5",
                    "waist radius much smaller than base radius",
                    "twisted diagonal lattice visible",
                    "no pagoda eaves or ancient spire",
                ],
            },
            "massing": ["slender hyperboloid", "narrow waist", "upper observation decks", "antenna mast"],
            "facade": ["rotating silver lattice", "cyan glass decks", "red night light points"],
            "changes": ["replaces previous short pagoda-like 96x96x96 plan"],
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
                "content": "广州塔/小蛮腰重做：要高很多，不要矮胖；保留细腰、旋转格构、观景层和天线。",
                "created_at": now(),
            },
            {"role": "assistant", "content": "已生成广州塔 V2：高瘦双曲面格构塔。", "created_at": now()},
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
