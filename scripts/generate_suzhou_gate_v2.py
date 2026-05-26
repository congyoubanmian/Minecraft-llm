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


PROJECT_ID = "suzhou_gate_v2"
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

        box(parts, (x1, sy1, z1), (x2, sy2, z2), "glass", hollow=True)
        box(parts, (core1, sy1, z1 + 2), (core2, sy2, z2 - 2), "glass_light", hollow=True)

        # Strong outer and inner dark structural ribs.
        for x in [x1, x2]:
            box(parts, (x, sy1, z1), (x + 1, sy2, z2), "mullion_dark")
        for z in [z1, z2]:
            box(parts, (x1, sy1, z), (x2, sy2, z + 1), "mullion")

        # Curtain-wall grid bands.
        for x in range(min(x1, x2) + 5, max(x1, x2), 7):
            box(parts, (x, sy1, z1), (x, sy2, z2), "mullion")
        for y in range(sy1 + 6, sy2, 9):
            box(parts, (x1, y, z1), (x2, y + 1, z2), "mullion_dark")


def build_plan() -> BuildPlan:
    parts: list[dict] = []

    # Plaza and low podium.
    box(parts, (0, 0, 0), (127, 0, 87), "plaza")
    box(parts, (12, 1, 10), (115, 3, 77), "concrete_dark")
    box(parts, (22, 4, 18), (105, 10, 69), "concrete", hollow=True)
    box(parts, (36, 4, 17), (91, 9, 17), "entry")

    # Two leaning tower legs. Their inner faces move inward with height, making
    # the big-trouser silhouette instead of two vertical boxes.
    add_segmented_tower(
        parts,
        side="left",
        x_outer=12,
        x_inner_base=47,
        x_inner_top=58,
        z1=16,
        z2=72,
        y1=4,
        y2=132,
        segments=13,
    )
    add_segmented_tower(
        parts,
        side="right",
        x_outer=115,
        x_inner_base=80,
        x_inner_top=69,
        z1=16,
        z2=72,
        y1=4,
        y2=132,
        segments=13,
    )

    # Top bridge and crown: wide rounded-looking gate head, thick enough to read
    # as the Oriental Gate's connected roof mass.
    box(parts, (46, 118, 16), (82, 136, 72), "glass", hollow=True)
    box(parts, (49, 121, 18), (79, 133, 70), "glass_light", hollow=True)
    box(parts, (42, 114, 14), (86, 119, 74), "mullion_dark")
    box(parts, (44, 135, 14), (84, 142, 74), "mullion_dark")
    box(parts, (50, 143, 20), (78, 149, 68), "roof_mech")

    # The visible hollow opening should remain clean and very tall.
    box(parts, (50, 11, 22), (78, 112, 66), "air")

    # Vertical skyline emphasis on the two outside edges and inner arch edges.
    for x in [10, 46, 81, 116]:
        box(parts, (x, 8, 14), (x + 2, 138, 74), "mullion_dark")
    for z in [14, 74]:
        box(parts, (10, 8, z), (48, 138, z + 1), "mullion")
        box(parts, (80, 8, z), (118, 138, z + 1), "mullion")

    # Horizontal floor bands across both legs.
    for y in range(14, 132, 9):
        box(parts, (13, y, 15), (48, y + 1, 73), "mullion_dark")
        box(parts, (80, y, 15), (115, y + 1, 73), "mullion_dark")
    for y in range(123, 140, 6):
        box(parts, (43, y, 15), (85, y + 1, 73), "mullion_dark")

    # Road/axis and entry lights.
    box(parts, (58, 1, 0), (70, 1, 24), "road")
    box(parts, (63, 2, 0), (65, 2, 24), "lane")
    lights = []
    for z in range(6, 78, 10):
        lights.append({"pos": [6, 2, z], "block": "light"})
        lights.append({"pos": [121, 2, z], "block": "light"})
    for x in range(28, 102, 12):
        lights.append({"pos": [x, 12, 18], "block": "light"})
        lights.append({"pos": [x, 12, 70], "block": "light"})
    parts.append({"type": "blocks", "blocks": lights})

    plan = {
        "name": NAME,
        "size": [128, 152, 88],
        "origin": [0, 64, 0],
        "palette": {
            "air": "air",
            "plaza": "polished_andesite",
            "concrete": "light_gray_concrete",
            "concrete_dark": "gray_concrete",
            "glass": "blue_stained_glass",
            "glass_light": "light_blue_stained_glass",
            "mullion": "blackstone",
            "mullion_dark": "polished_blackstone",
            "entry": "cyan_stained_glass",
            "road": "black_concrete",
            "lane": "white_concrete",
            "light": "sea_lantern",
            "roof_mech": "iron_block",
        },
        "analysis": {
            "source": "code_generated_suzhou_gate_v2",
            "intent": ["Suzhou Oriental Gate / big-trouser silhouette"],
            "massing": ["two tall legs lean inward", "large open void at bottom", "top bridge connects both towers"],
            "facade": ["blue glass curtain wall", "black mullion grid", "strong inner/outer edge ribs"],
            "changes": ["avoid vertical twin towers", "increase height and top crown", "clear central opening"],
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
    schematic_path, preview_path, material_path = generate_outputs(
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
        "analysis": plan.analysis,
        "messages": [
            {
                "role": "user",
                "content": "生成苏州东方之门/大裤衩 V2：更高更瘦，两条塔腿向内收，顶部连桥，底部保持巨大门洞。",
                "created_at": now(),
            },
            {"role": "assistant", "content": "已生成比例修正版 schematic 和网页预览。", "created_at": now()},
        ],
        "plan": plan.model_dump(by_alias=True),
        "plan_path": str(project_dir / "plan.json"),
        "schematic_path": str(schematic_path),
        "preview_path": str(preview_path),
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
                "materials": str(material_path),
                "placement": placement,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
