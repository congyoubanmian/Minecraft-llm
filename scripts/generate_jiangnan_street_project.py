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
from backend.main import _placement_from_paste
from backend.schematic.generator import generate_outputs, render_plan_to_blocks


PROJECT_ID = "77c2895e7810"
NAME = f"project_{PROJECT_ID}"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def box(parts: list[dict], a: tuple[int, int, int], b: tuple[int, int, int], block: str, hollow: bool = False) -> None:
    parts.append({"type": "box", "from": list(a), "to": list(b), "block": block, "hollow": hollow})


def slab(parts: list[dict], a: tuple[int, int, int], b: tuple[int, int, int], block: str, slab_type: str = "bottom") -> None:
    parts.append({"type": "slab", "from": list(a), "to": list(b), "block": block, "slab_type": slab_type})


def stairs(
    parts: list[dict],
    a: tuple[int, int, int],
    b: tuple[int, int, int],
    block: str,
    facing: str,
    half: str = "bottom",
) -> None:
    parts.append({"type": "stairs", "from": list(a), "to": list(b), "block": block, "facing": facing, "half": half})


def window(parts: list[dict], a: tuple[int, int, int], b: tuple[int, int, int], glass: str = "window") -> None:
    parts.append({"type": "window", "from": list(a), "to": list(b), "glass": glass, "frame": "frame", "sill": "sill", "shutter": "shutter"})


def door(parts: list[dict], wall: str, x: int | None, z: int | None, width: int = 2, height: int = 4) -> None:
    parts.append({"type": "door", "wall": wall, "x": x, "z": z, "width": width, "height": height, "block": "door"})


def blocks(parts: list[dict], points: list[tuple[int, int, int, str]]) -> None:
    parts.append({"type": "blocks", "blocks": [{"pos": [x, y, z], "block": block} for x, y, z, block in points]})


def house(
    parts: list[dict],
    *,
    x: int,
    z: int,
    w: int,
    d: int,
    floors: int,
    street_side: str,
    accent: str,
) -> None:
    h = floors * 6 + 2
    roof_y = h + 2
    box(parts, (x, 0, z), (x + w - 1, 1, z + d - 1), "foundation")
    box(parts, (x + 1, 2, z + 1), (x + w - 2, h, z + d - 2), "wall", hollow=True)

    for floor in range(1, floors):
        y = 2 + floor * 6
        box(parts, (x + 2, y, z + 2), (x + w - 3, y, z + d - 3), "floor")
        slab(parts, (x, y + 1, z), (x + w - 1, y + 1, z + d - 1), "trim", "top")

    # Timber corner posts and horizontal bands.
    for px in (x, x + w - 1):
        for pz in (z, z + d - 1):
            box(parts, (px, 2, pz), (px, h + 1, pz), "beam")
    for y in range(4, h + 1, 6):
        box(parts, (x, y, z), (x + w - 1, y, z), "frame")
        box(parts, (x, y, z + d - 1), (x + w - 1, y, z + d - 1), "frame")

    front_z = z + d - 1 if street_side == "south" else z
    back_z = z if street_side == "south" else z + d - 1
    front_wall = "back" if street_side == "south" else "front"
    door_x = x + w // 2 - 1
    door(parts, front_wall, door_x, None)

    porch_z = front_z + (1 if street_side == "south" else -1)
    step_z = front_z + (2 if street_side == "south" else -2)
    box(parts, (door_x - 1, 1, porch_z), (door_x + 2, 1, porch_z), "porch")
    stairs(parts, (door_x - 1, 1, step_z), (door_x + 2, 1, step_z), "stair", "south" if street_side == "south" else "north")
    slab(parts, (door_x - 3, 6, porch_z), (door_x + 4, 6, porch_z), "awning", "top")

    for floor in range(floors):
        y1 = 4 + floor * 6
        y2 = y1 + 2
        for wx in (x + 3, x + w - 5):
            window(parts, (wx, y1, front_z), (wx + 2, y2, front_z))
            window(parts, (wx, y1, back_z), (wx + 2, y2, back_z))
        if w >= 16:
            window(parts, (x + w // 2 - 1, y1, back_z), (x + w // 2 + 1, y2, back_z))

    # Black tiled gable roof with deep eaves and ridge accents.
    parts.append({"type": "roof_gable", "from": [x - 2, roof_y, z - 2], "to": [x + w + 1, roof_y + 6, z + d + 1], "block": "roof", "ridge_axis": "x"})
    slab(parts, (x - 3, roof_y, z - 3), (x + w + 2, roof_y, z - 3), "roof_edge", "bottom")
    slab(parts, (x - 3, roof_y, z + d + 2), (x + w + 2, roof_y, z + d + 2), "roof_edge", "bottom")
    box(parts, (x + 2, roof_y + 7, z + d // 2), (x + w - 3, roof_y + 7, z + d // 2), accent)

    detail: list[tuple[int, int, int, str]] = []
    for lx in (door_x - 3, door_x + 4):
        detail.append((lx, 5, porch_z, "lantern"))
    detail.append((door_x, 7, front_z, "sign"))
    for rail_x in range(x + 2, x + w - 2, 3):
        detail.append((rail_x, 8, front_z, "rail"))
    blocks(parts, detail)


def build_plan() -> BuildPlan:
    parts: list[dict] = []

    # Full block stone street and canal-town paving.
    box(parts, (0, 0, 0), (95, 0, 71), "ground")
    box(parts, (0, 1, 30), (95, 1, 41), "street")
    box(parts, (0, 1, 42), (95, 1, 45), "canal")
    box(parts, (0, 2, 29), (95, 2, 29), "curb")
    box(parts, (0, 2, 42), (95, 2, 42), "curb")

    north_specs = [(4, 4, 18, 20, 3), (28, 5, 16, 18, 2), (50, 4, 19, 20, 3), (74, 6, 17, 18, 2)]
    south_specs = [(8, 48, 16, 18, 2), (30, 49, 19, 19, 3), (55, 48, 17, 20, 2), (77, 50, 15, 17, 2)]
    for i, spec in enumerate(north_specs):
        x, z, w, d, floors = spec
        house(parts, x=x, z=z, w=w, d=d, floors=floors, street_side="south", accent="ridge_gold" if i % 2 == 0 else "ridge")
    for i, spec in enumerate(south_specs):
        x, z, w, d, floors = spec
        house(parts, x=x, z=z, w=w, d=d, floors=floors, street_side="north", accent="ridge")

    # Street details: lamps, market posts, benches, paving rhythm, canal rails.
    detail: list[tuple[int, int, int, str]] = []
    for x in range(6, 92, 8):
        detail.append((x, 2, 35, "paver_alt"))
        detail.append((x + 2, 2, 37, "paver_alt"))
    for x in range(10, 90, 16):
        detail.append((x, 3, 29, "lantern_post"))
        detail.append((x, 4, 29, "lantern_post"))
        detail.append((x, 5, 29, "lantern"))
        detail.append((x + 8, 3, 42, "lantern_post"))
        detail.append((x + 8, 4, 42, "lantern_post"))
        detail.append((x + 8, 5, 42, "lantern"))
    for x in range(0, 96, 4):
        detail.append((x, 3, 43, "rail"))
    blocks(parts, detail)

    plan = {
        "name": NAME,
        "size": [96, 36, 72],
        "origin": [0, 64, 0],
        "palette": {
            "ground": "mossy_stone_bricks",
            "street": "smooth_stone",
            "paver_alt": "andesite",
            "curb": "stone_bricks",
            "canal": "water",
            "foundation": "stone_bricks",
            "floor": "spruce_planks",
            "wall": "white_concrete",
            "beam": "dark_oak_log",
            "frame": "dark_oak_planks",
            "roof": "deepslate_tile_stairs",
            "roof_fill": "deepslate_tiles",
            "roof_edge": "deepslate_tile_slab",
            "window": "glass_pane",
            "sill": "smooth_stone_slab",
            "shutter": "spruce_trapdoor",
            "door": "dark_oak_door",
            "porch": "spruce_planks",
            "stair": "stone_brick_stairs",
            "trim": "dark_oak_slab",
            "awning": "spruce_slab",
            "lantern": "lantern",
            "lantern_post": "dark_oak_fence",
            "sign": "oak_sign",
            "rail": "dark_oak_fence",
            "ridge": "blackstone",
            "ridge_gold": "gilded_blackstone",
        },
        "analysis": {
            "source": "deterministic_rebuild_after_static_planner",
            "selected_template": "jiangnan_water_town",
            "component_strategy": [
                "Static planner had produced one 28x16x22 generic house; rebuild as a Jiangnan street block.",
                "Use repeated explicit house modules instead of one shell so each building has its own door and facade.",
            ],
            "design_spec": {
                "building_type": "jiangnan_water_town_street",
                "scale_intent": "96w x 36h x 72d street block with at least 8 independent houses around a walkable center street.",
                "grid": ["street z=30..41", "north houses face south", "south houses face north", "floor height 6", "2-3 floors per house"],
                "modules": [
                    {"name": "center_street", "role": "circulation", "bbox": [[0, 1, 30], [95, 2, 45]], "materials": ["street", "canal", "curb"]},
                    {"name": "north_house_row", "role": "architecture", "bbox": [[4, 0, 4], [92, 35, 26]], "materials": ["wall", "roof", "frame", "door"]},
                    {"name": "south_house_row", "role": "architecture", "bbox": [[8, 0, 48], [92, 35, 69]], "materials": ["wall", "roof", "frame", "door"]},
                    {"name": "street_details", "role": "detail", "bbox": [[0, 2, 29], [95, 8, 45]], "materials": ["lantern", "rail", "paver_alt"]},
                ],
                "interfaces": [
                    {"module_a": "north_house_row", "face_a": "south", "module_b": "center_street", "face_b": "north", "kind": "entry", "note": "north row porches open onto street"},
                    {"module_a": "south_house_row", "face_a": "north", "module_b": "center_street", "face_b": "south", "kind": "entry", "note": "south row porches open onto street"},
                ],
                "material_schedule": [
                    "wall=white_concrete for Jiangnan white walls",
                    "roof=deepslate_tile_stairs for black tiled roofs",
                    "frame/dark_oak for timber windows and beams",
                    "lantern/sign/rail for street detail",
                ],
                "quality_checks": [
                    "at least 6 independent houses",
                    "each house has a door facing the street",
                    "center street remains walkable",
                    "2-3 floors and more detail than static fallback",
                    "block_count comfortably above 15000",
                ],
            },
            "intent": ["replace tiny fallback house with detailed street block"],
            "massing": ["two rows of small Jiangnan buildings", "central walkable street", "canal edge"],
            "facade": ["white walls", "wood frames", "individual doors", "windows on every floor", "porches and signs"],
            "roof": ["black gable tiled roofs", "deep eaves", "ridge accents"],
            "materials": ["white concrete", "deepslate tiles", "dark oak", "stone paving"],
            "changes": ["expanded from 28x16x22/11 parts to 96x36x72/large multi-building street"],
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
    schematic_path, preview_path, material_path = generate_outputs(plan, settings.schematic_dir, project_dir, blocks=rendered)
    analysis_report = analyze_build(plan, rendered)
    analysis_report_path = project_dir / f"{NAME}.analysis.json"
    analysis_report_path.write_text(json.dumps(analysis_report, ensure_ascii=False, indent=2), encoding="utf-8")

    paste = {"x": 3500, "y": 82, "z": 460}
    spawn = {"x": 3548, "y": 118, "z": 420}
    placement = _placement_from_paste(PROJECT_ID, plan, paste, spawn)

    state_path = project_dir / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    state.update(
        {
            "id": PROJECT_ID,
            "status": "done",
            "updated_at": now(),
            "completed_at": now(),
            "error": None,
            "plan": plan.model_dump(by_alias=True),
            "plan_path": str(project_dir / "plan.json"),
            "schematic_path": str(schematic_path),
            "preview_path": str(preview_path),
            "materials_path": str(material_path),
            "analysis_report_path": str(analysis_report_path),
            "analysis_report": analysis_report,
            "placement": placement,
            "rcon": [],
        }
    )
    messages = state.setdefault("messages", [])
    messages.append({"role": "assistant", "content": "已修正为江南水乡街区：8 栋独立房屋、中间街道、每栋都有门和更多细节。", "created_at": now()})

    (project_dir / "plan.json").write_text(plan.model_dump_json(by_alias=True, indent=2), encoding="utf-8")
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "project_id": PROJECT_ID,
                "size": plan.size,
                "part_count": len(plan.parts),
                "block_count": len(rendered),
                "materials": rendered.material_counts(),
                "analysis_report": analysis_report,
                "placement": placement,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
