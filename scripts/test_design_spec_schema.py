from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.analysis import analyze_build
from backend.dsl.schema import BuildPlan
from backend.schematic.generator import render_plan_to_blocks


def main() -> None:
    plan = BuildPlan.model_validate(
        {
            "name": "design_spec_schema_smoke",
            "size": [16, 12, 16],
            "origin": [0, 64, 0],
            "palette": {
                "foundation": "stone_bricks",
                "wall": "white_concrete",
            },
            "analysis": {
                "selected_template": "temple_hall",
                "design_spec": {
                    "building_type": "temple_hall",
                    "scale_intent": "small schema validation hall",
                    "grid": ["bay_width=4", "floor_height=4"],
                    "modules": [
                        {
                            "name": "base",
                            "role": "foundation",
                            "bbox": [[0, 0, 0], [15, 0, 15]],
                            "materials": ["foundation=stone_bricks"],
                            "interfaces": {"top": "hall.bottom"},
                        },
                        {
                            "name": "hall",
                            "role": "mass",
                            "bbox": [[1, 1, 1], [14, 8, 14]],
                            "materials": ["wall=white_concrete"],
                            "interfaces": {"bottom": "base.top"},
                        },
                    ],
                    "interfaces": [
                        {
                            "module_a": "base",
                            "face_a": "top",
                            "module_b": "hall",
                            "face_b": "bottom",
                            "kind": "support",
                            "note": "hall sits on base",
                        }
                    ],
                    "material_schedule": ["foundation=stone_bricks", "wall=white_concrete"],
                    "quality_checks": ["modules have bboxes", "interfaces reference existing modules"],
                    "performance_budget": {
                        "max_blocks": 20,
                        "max_preview_blocks": 20,
                        "max_tick_commands": 0,
                        "animated": False,
                        "suggested_view_distance": 8,
                        "min_server_memory_mb": 2048,
                    },
                },
            },
            "parts": [
                {"type": "box", "from": [0, 0, 0], "to": [15, 0, 15], "block": "foundation"},
                {"type": "box", "from": [1, 1, 1], "to": [14, 8, 14], "block": "wall", "hollow": True},
            ],
        }
    )
    blocks = render_plan_to_blocks(plan)
    report = analyze_build(plan, blocks)
    assert report["design_spec"]["present"] is True
    assert report["design_spec"]["stitch_ready"] is True
    assert report["design_spec"]["performance_budget"]["max_blocks"] == 20
    assert report["design_blueprint"]["present"] is True
    assert report["design_blueprint"]["stitch_ready"] is True
    assert report["design_blueprint"]["stage_count"] == 2
    assert report["design_blueprint"]["modules"][0]["size"] == [16, 1, 16]
    assert report["design_blueprint"]["interfaces"][0]["from"] == "base"
    assert any("performance_budget.max_blocks" in warning for warning in report["warnings"])
    print({"blocks": len(blocks), "warnings": report["warnings"]})


if __name__ == "__main__":
    main()
