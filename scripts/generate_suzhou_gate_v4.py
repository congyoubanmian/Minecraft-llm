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


PROJECT_ID = "suzhou_gate_v4"
NAME = f"project_{PROJECT_ID}"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def box(parts: list[dict], a: tuple[int, int, int], b: tuple[int, int, int], block: str, hollow: bool = False) -> None:
    parts.append({"type": "box", "from": list(a), "to": list(b), "block": block, "hollow": hollow})


def add_light_bar(parts: list[dict], a: tuple[int, int, int], b: tuple[int, int, int]) -> None:
    box(parts, a, b, "light")


def add_office_floors(
    parts: list[dict],
    *,
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    y1: int,
    y2: int,
    floor_height: int = 6,
) -> None:
    for y in range(y1, y2 + 1, floor_height):
        box(parts, (x1, y, z1), (x2, y, z2), "floor")
        if y + 1 > y2:
            continue
        for z in range(z1 + 8, z2, 10):
            box(parts, (x1 + 2, y + 1, z), (x2 - 2, min(y + 4, y2), z), "partition")
        for x in range(x1 + 8, x2, 12):
            box(parts, (x, y + 1, z1 + 2), (x, min(y + 4, y2), z2 - 2), "partition")
        for x in range(x1 + 5, x2, 12):
            for z in range(z1 + 5, z2, 10):
                box(parts, (x, min(y + 3, y2), z), (x, min(y + 3, y2), z), "office_light")


def add_bridge_offices(
    parts: list[dict],
    *,
    x1: int,
    x2: int,
    z1: int,
    z2: int,
    y1: int,
    y2: int,
    corridor_z1: int,
    corridor_z2: int,
) -> None:
    for y in range(y1, y2 + 1, 6):
        box(parts, (x1, y, z1), (x2, y, z2), "floor")
        if y + 1 > y2:
            continue

        # Corridor boundaries: middle is walkable, both sides are offices.
        box(parts, (x1 + 1, y + 1, corridor_z1 - 1), (x2 - 1, min(y + 4, y2), corridor_z1 - 1), "partition")
        box(parts, (x1 + 1, y + 1, corridor_z2 + 1), (x2 - 1, min(y + 4, y2), corridor_z2 + 1), "partition")

        # Office partitions along the bridge length, on both sides of corridor.
        for x in range(x1 + 8, x2, 10):
            box(parts, (x, y + 1, z1 + 2), (x, min(y + 4, y2), corridor_z1 - 2), "partition")
            box(parts, (x, y + 1, corridor_z2 + 2), (x, min(y + 4, y2), z2 - 2), "partition")

        # Corridor lights and room lights.
        add_light_bar(parts, (x1 + 2, min(y + 3, y2), (corridor_z1 + corridor_z2) // 2), (x2 - 2, min(y + 3, y2), (corridor_z1 + corridor_z2) // 2))
        for x in range(x1 + 5, x2, 10):
            box(parts, (x, min(y + 3, y2), z1 + 6), (x, min(y + 3, y2), z1 + 6), "office_light")
            box(parts, (x, min(y + 3, y2), z2 - 6), (x, min(y + 3, y2), z2 - 6), "office_light")


def add_glass_tower(
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
        t = idx / max(1, segments - 1)
        x_inner = round(x_inner_base + (x_inner_top - x_inner_base) * t)
        if side == "left":
            x1, x2 = x_outer, x_inner
            light_x = x_inner - 2
        else:
            x1, x2 = x_inner, x_outer
            light_x = x_inner + 2

        box(parts, (x1, sy1, z1), (x2, sy2, z2), "glass_main", hollow=True)
        box(parts, (x1 + 1, sy1, z1 + 1), (x2 - 1, sy2, z2 - 1), "glass_light", hollow=True)

        # Thin exterior seams only. The building should read as a glass object.
        for x in [x1, x2]:
            box(parts, (x, sy1, z1), (x, sy2, z2), "glass_shadow")
        for z in [z1, z2]:
            box(parts, (x1, sy1, z), (x2, sy2, z), "glass_shadow")
        for x in range(min(x1, x2) + 12, max(x1, x2), 18):
            box(parts, (x, sy1, z1), (x, sy2, z2), "mullion")

        # Interior luminous floors hidden behind glass.
        if idx % 2 == 0:
            y = (sy1 + sy2) // 2
            add_light_bar(parts, (x1 + 2, y, z1 + 3), (x2 - 2, y, z1 + 3))
            add_light_bar(parts, (x1 + 2, y, z2 - 3), (x2 - 2, y, z2 - 3))
            add_light_bar(parts, (light_x, y, z1 + 6), (light_x, y, z2 - 6))

        if idx % 2 == 0:
            add_office_floors(parts, x1=x1 + 3, x2=x2 - 3, z1=z1 + 4, z2=z2 - 4, y1=sy1 + 1, y2=sy2 - 1)


def build_plan() -> BuildPlan:
    parts: list[dict] = []

    box(parts, (0, 0, 0), (143, 0, 95), "plaza")
    box(parts, (10, 1, 10), (133, 2, 85), "podium")
    box(parts, (22, 3, 18), (121, 8, 77), "glass_shadow", hollow=True)
    box(parts, (40, 3, 17), (103, 8, 17), "entry")

    add_glass_tower(
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
    add_glass_tower(
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

    # Glass top bridge with lighting inside instead of solid metal cap.
    box(parts, (58, 140, 14), (86, 170, 82), "glass_main", hollow=True)
    box(parts, (60, 143, 16), (84, 166, 80), "glass_light", hollow=True)
    box(parts, (56, 136, 12), (88, 139, 84), "glass_shadow")
    box(parts, (56, 170, 12), (88, 174, 84), "glass_shadow")
    box(parts, (62, 175, 22), (82, 182, 74), "glass_light", hollow=True)

    for y in range(145, 168, 6):
        add_light_bar(parts, (60, y, 19), (84, y, 19))
        add_light_bar(parts, (60, y, 77), (84, y, 77))
        add_light_bar(parts, (62, y, 48), (82, y, 48))
    add_bridge_offices(
        parts,
        x1=61,
        x2=83,
        z1=18,
        z2=78,
        y1=144,
        y2=166,
        corridor_z1=43,
        corridor_z2=53,
    )

    # Clear the iconic central opening and add luminous inner outline.
    box(parts, (43, 8, 22), (100, 134, 74), "air")
    for x in [43, 100]:
        add_light_bar(parts, (x, 10, 24), (x, 132, 24))
        add_light_bar(parts, (x, 10, 72), (x, 132, 72))
    add_light_bar(parts, (45, 134, 24), (98, 134, 24))
    add_light_bar(parts, (45, 134, 72), (98, 134, 72))

    # Very thin silhouette edges.
    for x in [10, 53, 90, 132]:
        box(parts, (x, 8, 12), (x, 172, 84), "frame_glass")
    for z in [12, 84]:
        box(parts, (10, 8, z), (54, 172, z), "frame_glass")
        box(parts, (89, 8, z), (133, 172, z), "frame_glass")

    # Plaza, water, and approach.
    box(parts, (66, 1, 0), (78, 1, 26), "road")
    box(parts, (71, 2, 0), (73, 2, 26), "lane")
    box(parts, (18, 1, 4), (54, 1, 8), "water")
    box(parts, (90, 1, 4), (126, 1, 8), "water")

    lights = []
    for z in range(8, 88, 14):
        lights.append({"pos": [6, 2, z], "block": "light"})
        lights.append({"pos": [137, 2, z], "block": "light"})
    for x in range(36, 110, 14):
        lights.append({"pos": [x, 10, 18], "block": "night_line"})
        lights.append({"pos": [x, 10, 78], "block": "night_line"})
    parts.append({"type": "blocks", "blocks": lights})

    plan = {
        "name": NAME,
        "size": [144, 188, 96],
        "origin": [0, 64, 0],
        "palette": {
            "air": "air",
            "plaza": "smooth_stone",
            "podium": "light_gray_concrete",
            "glass_main": "light_blue_stained_glass",
            "glass_light": "white_stained_glass",
            "glass_shadow": "cyan_stained_glass",
            "frame_glass": "gray_stained_glass",
            "mullion": "light_gray_stained_glass",
            "entry": "cyan_stained_glass",
            "road": "black_concrete",
            "lane": "white_concrete",
            "water": "water",
            "floor": "smooth_quartz",
            "partition": "light_gray_stained_glass_pane",
            "office_light": "sea_lantern",
            "light": "sea_lantern",
            "night_line": "end_rod",
        },
        "analysis": {
            "source": "code_generated_suzhou_gate_v4",
            "intent": ["glass-shell Suzhou Oriental Gate with interior lighting"],
            "massing": ["same high gate silhouette", "large central opening", "thin glass frame"],
            "facade": ["mostly light-blue and white glass", "office floors visible through facade", "luminous opening outline"],
            "interior": ["tower floors have office partitions", "top bridge has central walk corridor", "bridge offices sit on both sides of corridor"],
            "changes": ["removed most concrete/iron mass", "added room divisions and office lights", "top bridge corridor stays walkable"],
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
        "analysis": plan.analysis_dict(),
        "messages": [
            {
                "role": "user",
                "content": "生成苏州东方之门/大裤衩 V4：外层几乎全玻璃，内部每层是办公室，有房间分割和灯光；顶部连桥中间是可走人的走廊，两侧是办公室。",
                "created_at": now(),
            },
            {"role": "assistant", "content": "已生成玻璃外壳和内部灯光版 schematic。", "created_at": now()},
        ],
        "plan": plan.model_dump(by_alias=True, mode="json"),
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
