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


PROJECT_ID = "suzhou_gate_v3"
NAME = f"project_{PROJECT_ID}"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def box(parts: list[dict], a: tuple[int, int, int], b: tuple[int, int, int], block: str, hollow: bool = False) -> None:
    parts.append({"type": "box", "from": list(a), "to": list(b), "block": block, "hollow": hollow})


def add_segmented_tower(
    parts: list[dict],
    *,
    side: str,
    x_outer: int,
    x_inner_base: int,
    x_inner_top: int,
    z1: int,
    z2: int,
    y1: int,
    y2: int,
    segments: int,
) -> None:
    height = y2 - y1 + 1
    for idx in range(segments):
        sy1 = y1 + idx * height // segments
        sy2 = y1 + (idx + 1) * height // segments - 1
        t0 = idx / max(1, segments - 1)
        x_inner = round(x_inner_base + (x_inner_top - x_inner_base) * t0)
        if side == "left":
            x1, x2 = x_outer, x_inner
            core1, core2 = x_outer + 2, x_inner - 2
        else:
            x1, x2 = x_inner, x_outer
            core1, core2 = x_inner + 2, x_outer - 2

        box(parts, (x1, sy1, z1), (x2, sy2, z2), "glass_main", hollow=True)
        box(parts, (core1, sy1, z1 + 2), (core2, sy2, z2 - 2), "glass_light", hollow=True)

        # Silver structural edges, with sparse dark curtain-wall seams.
        for x in [x1, x2]:
            box(parts, (x, sy1, z1), (x, sy2, z2), "frame")
        for z in [z1, z2]:
            box(parts, (x1, sy1, z), (x2, sy2, z), "frame")

        for x in range(min(x1, x2) + 8, max(x1, x2), 12):
            box(parts, (x, sy1, z1), (x, sy2, z2), "mullion")
        if idx % 2 == 0:
            mid_y = (sy1 + sy2) // 2
            box(parts, (x1, mid_y, z1), (x2, mid_y, z2), "mullion")


def build_plan() -> BuildPlan:
    parts: list[dict] = []

    box(parts, (0, 0, 0), (143, 0, 95), "plaza")
    box(parts, (10, 1, 10), (133, 3, 85), "podium_dark")
    box(parts, (22, 4, 18), (121, 10, 77), "podium", hollow=True)
    box(parts, (40, 4, 17), (103, 9, 17), "entry")

    add_segmented_tower(
        parts,
        side="left",
        x_outer=12,
        x_inner_base=53,
        x_inner_top=66,
        z1=14,
        z2=82,
        y1=5,
        y2=162,
        segments=28,
    )
    add_segmented_tower(
        parts,
        side="right",
        x_outer=131,
        x_inner_base=90,
        x_inner_top=77,
        z1=14,
        z2=82,
        y1=5,
        y2=162,
        segments=28,
    )

    # Top connected head: glass-dominant with silver frame instead of black mass.
    box(parts, (60, 140, 14), (84, 170, 82), "glass_main", hollow=True)
    box(parts, (62, 143, 16), (82, 166, 80), "glass_light", hollow=True)
    box(parts, (54, 136, 12), (90, 141, 84), "frame_bright")
    box(parts, (56, 169, 12), (88, 176, 84), "frame_bright")
    box(parts, (62, 177, 22), (82, 184, 74), "roof_mech")

    # Larger clean void makes the "big trouser" silhouette read from the ground.
    box(parts, (45, 8, 22), (98, 132, 74), "air")

    # Four main skyline edges are silver; dark seams only one block thick.
    for x in [10, 53, 90, 132]:
        box(parts, (x, 8, 12), (x + 1, 172, 84), "frame_bright")
    for z in [12, 84]:
        box(parts, (10, 8, z), (54, 172, z), "frame")
        box(parts, (89, 8, z), (133, 172, z), "frame")

    for y in range(18, 162, 12):
        box(parts, (13, y, 13), (54, y, 83), "mullion")
        box(parts, (89, y, 13), (130, y, 83), "mullion")
    for y in range(146, 174, 8):
        box(parts, (55, y, 13), (89, y, 83), "mullion")

    # Front road axis, water feature, and restrained night lighting.
    box(parts, (66, 1, 0), (78, 1, 26), "road")
    box(parts, (71, 2, 0), (73, 2, 26), "lane")
    box(parts, (18, 1, 4), (54, 1, 8), "water")
    box(parts, (90, 1, 4), (126, 1, 8), "water")

    lights = []
    for z in range(8, 88, 14):
        lights.append({"pos": [6, 2, z], "block": "light"})
        lights.append({"pos": [137, 2, z], "block": "light"})
    for x in range(34, 112, 16):
        lights.append({"pos": [x, 12, 18], "block": "night_line"})
        lights.append({"pos": [x, 12, 78], "block": "night_line"})
    parts.append({"type": "blocks", "blocks": lights})

    plan = {
        "name": NAME,
        "size": [144, 188, 96],
        "origin": [0, 64, 0],
        "palette": {
            "air": "air",
            "plaza": "smooth_stone",
            "podium": "light_gray_concrete",
            "podium_dark": "gray_concrete",
            "glass_main": "light_blue_stained_glass",
            "glass_light": "white_stained_glass",
            "glass_shadow": "cyan_stained_glass",
            "frame": "light_gray_concrete",
            "frame_bright": "iron_block",
            "mullion": "gray_concrete",
            "mullion_dark": "black_concrete",
            "entry": "cyan_stained_glass",
            "road": "black_concrete",
            "lane": "white_concrete",
            "water": "water",
            "light": "sea_lantern",
            "night_line": "end_rod",
            "roof_mech": "iron_block",
        },
        "analysis": {
            "source": "code_generated_suzhou_gate_v3",
            "intent": ["Suzhou Oriental Gate / big trouser silhouette"],
            "massing": ["taller 188 block gate", "wider central void", "28 segment inward leaning legs"],
            "facade": ["silver-blue glass curtain wall", "thin gray mullions", "bright metal frame"],
            "changes": ["reduced blackstone mass", "increased glass ratio", "larger bottom opening", "smoother lean"],
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
                "content": "生成苏州东方之门/大裤衩 V3：银蓝玻璃幕墙、更大门洞、更高比例、更少黑色龙骨。",
                "created_at": now(),
            },
            {"role": "assistant", "content": "已生成银蓝玻璃修正版 schematic 和网页预览。", "created_at": now()},
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
