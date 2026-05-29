from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.dsl.schema import BuildPlan
from backend.schematic.generator import generate_outputs


def main() -> None:
    plan = BuildPlan.model_validate(
        {
            "name": "preview_lod_smoke",
            "size": [5, 5, 5],
            "origin": [0, 64, 0],
            "palette": {"stone": "stone"},
            "parts": [
                {
                    "type": "box",
                    "from": [0, 0, 0],
                    "to": [4, 4, 4],
                    "block": "stone",
                }
            ],
        }
    )

    with tempfile.TemporaryDirectory() as tmp:
        output_dir = Path(tmp)
        _, preview_path, surface_preview_path, _ = generate_outputs(plan, output_dir, output_dir)
        full = json.loads(preview_path.read_text(encoding="utf-8"))
        surface = json.loads(surface_preview_path.read_text(encoding="utf-8"))

    assert full["mode"] == "full", full
    assert surface["mode"] == "surface", surface
    assert full["block_count"] == 125, full
    assert full["preview_count"] == 125, full
    assert surface["block_count"] == 125, surface
    assert surface["preview_source_count"] == 98, surface
    assert surface["preview_count"] == 98, surface
    assert surface["preview_count"] < full["preview_count"], (surface, full)

    print({"full": full["preview_count"], "surface": surface["preview_count"]})


if __name__ == "__main__":
    main()
