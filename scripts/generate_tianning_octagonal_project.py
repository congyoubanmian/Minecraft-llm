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


PROJECT_ID = "tianning_oct_v2"
NAME = f"project_{PROJECT_ID}"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def box(parts: list[dict], a: tuple[int, int, int], b: tuple[int, int, int], block: str, hollow: bool = False) -> None:
    parts.append({"type": "box", "from": list(a), "to": list(b), "block": block, "hollow": hollow})


def window(parts: list[dict], a: tuple[int, int, int], b: tuple[int, int, int]) -> None:
    parts.append({"type": "window", "from": list(a), "to": list(b), "glass": "glass", "frame": "bronze", "sill": "jade"})


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
    cx = 52
    cz = 52
    y = 0

    # Broad octagonal temple base and front stair.
    parts.append(
        {
            "type": "octagonal_tower",
            "center": [cx, y, cz],
            "radius": 43,
            "height": 4,
            "block": "base",
            "hollow": False,
            "thickness": 1,
            "floor_block": "base",
        }
    )
    parts.append({"type": "octagonal_roof", "center": [cx, 4, cz], "radius": 45, "layers": 2, "block": "stone_slab", "fill": "stone"})
    box(parts, (cx - 11, 0, 0), (cx + 11, 1, 16), "base")
    for step in range(5):
        box(parts, (cx - 14 + step, step, 9 + step * 2), (cx + 14 - step, step, 18 + step * 2), "base")

    floor_y = 6
    radii = [31, 30, 29, 28, 27, 25, 24, 23, 21, 20, 18, 17, 15]
    floor_height = 7
    for index, radius in enumerate(radii, start=1):
        wall = "jade" if index % 2 else "light_jade"
        parts.append(
            {
                "type": "octagonal_tower",
                "center": [cx, floor_y, cz],
                "radius": radius,
                "height": floor_height,
                "block": wall,
                "hollow": True,
                "thickness": 2,
                "floor_block": "dark_wood",
                "floor_interval": floor_height,
                "trim_block": "bronze",
            }
        )
        parts.append(
            {
                "type": "octagonal_roof",
                "center": [cx, floor_y + floor_height, cz],
                "radius": radius + 7,
                "layers": 4,
                "block": "copper_roof",
                "fill": "dark_wood",
                "cap": "bronze",
            }
        )

        # Eight-corner vertical bronze ribs.
        for dx, dz in oct_points(radius):
            box(parts, (cx + dx, floor_y, cz + dz), (cx + dx, floor_y + floor_height + 1, cz + dz), "bronze")

        # Four cardinal large windows and four diagonal jade/bronze plaques.
        w = max(2, min(4, radius // 6))
        wy1 = floor_y + 2
        wy2 = floor_y + 4
        window(parts, (cx - w, wy1, cz - radius), (cx + w, wy2, cz - radius))
        window(parts, (cx - w, wy1, cz + radius), (cx + w, wy2, cz + radius))
        window(parts, (cx - radius, wy1, cz - w), (cx - radius, wy2, cz + w))
        window(parts, (cx + radius, wy1, cz - w), (cx + radius, wy2, cz + w))
        for dx, dz in oct_points(radius - 1)[1::2]:
            box(parts, (cx + dx, floor_y + 2, cz + dz), (cx + dx, floor_y + 4, cz + dz), "bronze")

        # Hanging lanterns under every other eave.
        lanterns = []
        if index % 2 == 1:
            for dx, dz in [(0, -radius - 5), (radius + 5, 0), (0, radius + 5), (-radius - 5, 0)]:
                lanterns.append({"pos": [cx + dx, floor_y + floor_height + 1, cz + dz], "block": "lantern"})
        if lanterns:
            parts.append({"type": "blocks", "blocks": lanterns})

        floor_y += 8

    # Gold Vajra-seat inspired spire.
    parts.append({"type": "octagonal_tower", "center": [cx, floor_y + 2, cz], "radius": 10, "height": 3, "block": "gold", "hollow": False})
    parts.append({"type": "octagonal_roof", "center": [cx, floor_y + 5, cz], "radius": 12, "layers": 3, "block": "gold", "fill": "gold"})
    parts.append({"type": "octagonal_tower", "center": [cx, floor_y + 9, cz], "radius": 5, "height": 6, "block": "gold", "hollow": False})
    parts.append({"type": "octagonal_tower", "center": [cx, floor_y + 15, cz], "radius": 2, "height": 8, "block": "gold", "hollow": False})
    parts.append({"type": "blocks", "blocks": [{"pos": [cx, floor_y + 24, cz], "block": "lightning_rod"}]})

    # Four plaza incense/guardian markers around the base.
    for px, pz in [(cx - 30, cz - 30), (cx + 30, cz - 30), (cx - 30, cz + 30), (cx + 30, cz + 30)]:
        parts.append({"type": "cylinder", "center": [px, 6, pz], "radius": 3, "height": 2, "block": "bronze", "hollow": False})
        parts.append({"type": "cylinder", "center": [px, 8, pz], "radius": 2, "height": 3, "block": "gold", "hollow": False})

    plan = {
        "name": NAME,
        "size": [104, 140, 104],
        "origin": [0, 64, 0],
        "palette": {
            "base": "stone_bricks",
            "stone": "polished_andesite",
            "stone_slab": "stone_brick_slab",
            "jade": "smooth_quartz",
            "light_jade": "quartz_bricks",
            "bronze": "cut_copper",
            "copper_roof": "oxidized_cut_copper",
            "dark_wood": "dark_oak_planks",
            "glass": "cyan_stained_glass_pane",
            "gold": "gold_block",
            "lantern": "lantern",
            "lightning_rod": "lightning_rod",
        },
        "analysis": {
            "source": "code_generated_octagonal_tianning_v2",
            "massing": ["13 tier octagonal pagoda", "large octagonal base", "gold spire"],
            "geometry": ["octagonal_tower parts force the footprint", "each floor has an octagonal eave"],
            "materials": ["jade white body", "bronze/copper roof tiles", "golden finial"],
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
        max_preview_blocks=180_000,
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
                "content": "代码生成八角形天宁宝塔 V2：13层、八角平面、铜瓦玉身金顶。",
                "created_at": now(),
            },
            {"role": "assistant", "content": "已生成八角约束版 schematic 和网页预览。", "created_at": now()},
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
