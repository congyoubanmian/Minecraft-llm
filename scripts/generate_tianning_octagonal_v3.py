from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import settings
from backend.dsl.schema import BuildPlan
from backend.main import _allocate_placement
from backend.schematic.generator import generate_outputs


PROJECT_ID = "tianning_oct_v3"
NAME = f"project_{PROJECT_ID}"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def box(parts: list[dict], a: tuple[int, int, int], b: tuple[int, int, int], block: str, hollow: bool = False) -> None:
    parts.append({"type": "box", "from": list(a), "to": list(b), "block": block, "hollow": hollow})


def oct_points(radius: int) -> list[tuple[int, int]]:
    cut = max(2, int(radius * 0.42))
    return [
        (-cut, -radius),
        (cut, -radius),
        (radius, -cut),
        (radius, cut),
        (cut, radius),
        (-cut, radius),
        (-radius, cut),
        (-radius, -cut),
    ]


def build_plan() -> BuildPlan:
    parts: list[dict] = []
    cx = 48
    cz = 48

    # Tall octagonal base, front stair, and surrounding white pagoda grove.
    parts.append(
        {
            "type": "octagonal_tower",
            "center": [cx, 0, cz],
            "radius": 41,
            "height": 5,
            "block": "base",
            "hollow": False,
            "floor_block": "base",
        }
    )
    parts.append({"type": "octagonal_eave", "center": [cx, 5, cz], "radius": 40, "overhang": 4, "thickness": 2, "block": "stone_trim", "underside": "stone"})
    box(parts, (cx - 13, 0, 0), (cx + 13, 1, 16), "base")
    for step in range(6):
        box(parts, (cx - 16 + step, step, 10 + step * 2), (cx + 16 - step, step, 20 + step * 2), "base")
    parts.append(
        {
            "type": "mini_pagoda_ring",
            "center": [cx, 6, cz],
            "ring_radius": 42,
            "count": 24,
            "pagoda_radius": 2,
            "height": 9,
            "block": "jade",
            "roof": "bronze",
            "accent": "gold",
        }
    )

    floor_y = 8
    floor_height = 9
    radii = [27, 26, 25, 24, 23, 22, 21, 20, 18, 17, 16, 15, 14]
    for index, radius in enumerate(radii, start=1):
        wall = "jade" if index % 2 else "light_jade"
        trim_y = floor_y + floor_height - 1
        parts.append(
            {
                "type": "octagonal_tower",
                "center": [cx, floor_y, cz],
                "radius": radius,
                "height": floor_height,
                "block": wall,
                "hollow": True,
                "thickness": 2,
                "floor_block": "jade",
                "floor_interval": floor_height,
                "trim_block": "bronze",
            }
        )
        parts.append(
            {
                "type": "facade_panel_ring",
                "center": [cx, floor_y, cz],
                "radius": radius,
                "y": floor_y + 3,
                "height": 3,
                "width": max(3, min(5, radius // 4)),
                "glass": "glass",
                "frame": "bronze",
                "plaque": "gold",
            }
        )
        parts.append(
            {
                "type": "octagonal_eave",
                "center": [cx, trim_y + 1, cz],
                "radius": radius + 1,
                "overhang": 7 if index < 8 else 6,
                "thickness": 3,
                "block": "copper_roof",
                "underside": "bronze_dark",
                "corner_block": "gold",
                "lantern": "lantern" if index % 2 == 1 else None,
            }
        )

        # Bronze vertical ribs emphasize eight-sided geometry.
        for dx, dz in oct_points(radius):
            box(parts, (cx + dx, floor_y, cz + dz), (cx + dx, trim_y + 2, cz + dz), "bronze")

        # Thin dark bracket band under each eave instead of wood-filled roofs.
        parts.append(
            {
                "type": "octagonal_roof",
                "center": [cx, trim_y, cz],
                "radius": radius + 2,
                "layers": 1,
                "block": "bronze_dark",
                "fill": "jade",
                "cap": "jade",
            }
        )

        floor_y += floor_height + 3

    # Multi-part golden vajra-style top: central spire plus four side spires.
    parts.append({"type": "octagonal_tower", "center": [cx, floor_y, cz], "radius": 10, "height": 3, "block": "gold", "hollow": False})
    parts.append({"type": "octagonal_eave", "center": [cx, floor_y + 3, cz], "radius": 10, "overhang": 4, "thickness": 2, "block": "gold", "underside": "bronze"})
    parts.append({"type": "vajra_spire", "center": [cx, floor_y + 5, cz], "base_radius": 10, "height": 31, "block": "gold", "accent": "lightning_rod"})

    plan = {
        "name": NAME,
        "size": [96, 202, 96],
        "origin": [0, 64, 0],
        "palette": {
            "base": "stone_bricks",
            "stone": "polished_andesite",
            "stone_trim": "stone_brick_slab",
            "jade": "smooth_quartz",
            "light_jade": "quartz_bricks",
            "bronze": "cut_copper",
            "bronze_dark": "exposed_cut_copper",
            "copper_roof": "oxidized_cut_copper",
            "glass": "cyan_stained_glass_pane",
            "gold": "gold_block",
            "lantern": "lantern",
            "lightning_rod": "lightning_rod",
        },
        "analysis": {
            "source": "code_generated_tianning_v3",
            "massing": ["slender 13-tier octagonal pagoda", "wide base and white mini-pagoda ring", "vajra-style golden spire"],
            "geometry": ["octagonal_eave adds overhanging upturned corners", "facade_panel_ring repeats windows on eight faces"],
            "materials": ["white jade/quartz tower body", "oxidized copper eaves", "gold vajra spire"],
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
    schematic_path, preview_path, surface_preview_path, material_path = generate_outputs(
        plan,
        schematic_dir=settings.schematic_dir,
        preview_dir=project_dir,
        max_preview_blocks=220_000,
    )
    placement = _allocate_placement(PROJECT_ID, plan)
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
                "content": "生成更像常州天宁宝塔的 V3：更高更瘦、十三层八角飞檐、金顶玉身、塔基小白塔环绕。",
                "created_at": now(),
            },
            {"role": "assistant", "content": "已生成 V3 schematic、网页预览和材料统计。", "created_at": now()},
        ],
        "plan": plan.model_dump(by_alias=True, mode="json"),
        "plan_path": str(project_dir / "plan.json"),
        "schematic_path": str(schematic_path),
        "preview_path": str(preview_path),
            "surface_preview_path": str(surface_preview_path),
        "materials_path": str(material_path),
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
                "schematic": str(schematic_path),
                "preview": str(preview_path),
                "surface_preview": str(surface_preview_path),
                "materials": str(material_path),
                "placement": placement,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
