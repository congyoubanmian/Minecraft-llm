from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.dsl.schema import BuildPlan
from backend.schematic.generator import generate_outputs, render_plan_to_blocks


def main() -> None:
    plan = BuildPlan.model_validate(
        {
            "name": "component_library_smoke",
            "size": [128, 64, 64],
            "origin": [0, 64, 0],
            "palette": {},
            "analysis": {"source": "component library smoke test"},
            "parts": [
                {
                    "type": "component",
                    "name": "stone_arch_bridge",
                    "at": [0, 0, 0],
                    "scale": 1.0,
                    "materials": {"stone": "deepslate_bricks", "deck": "smooth_stone"},
                },
                {
                    "type": "component",
                    "name": "suspension_bridge_segment",
                    "at": [0, 20, 24],
                    "scale": 1.0,
                    "materials": {"tower": "light_gray_concrete", "cable": "iron_bars"},
                },
                {
                    "type": "component",
                    "name": "pagoda_tier",
                    "at": [72, 0, 0],
                    "scale": 0.75,
                    "parameters": {"radius": 14, "height": 7, "eave_overhang": 5},
                },
            ],
        }
    )
    blocks = render_plan_to_blocks(plan)
    output_dir = ROOT / "backend" / "generated_plans"
    schematic_path, preview_path, surface_preview_path, material_path = generate_outputs(plan, output_dir, output_dir)
    print(
        {
            "blocks": len(blocks),
            "schematic": str(schematic_path),
            "preview": str(preview_path),
                "surface_preview": str(surface_preview_path),
            "materials": str(material_path),
            "top_materials": list(blocks.material_counts().items())[:8],
        }
    )


if __name__ == "__main__":
    main()
