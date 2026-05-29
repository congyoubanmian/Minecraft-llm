from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.main import _module_preview_payload


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        preview_path = Path(tmp) / "preview.json"
        preview_path.write_text(
            json.dumps(
                {
                    "name": "module_api_smoke",
                    "mode": "surface",
                    "size": [8, 8, 8],
                    "blocks": [
                        [0, 0, 0, "stone"],
                        [2, 2, 2, "stone"],
                        [6, 6, 6, "glass"],
                    ],
                    "block_count": 3,
                    "preview_count": 3,
                }
            ),
            encoding="utf-8",
        )
        state = {
            "analysis_report": {
                "design_blueprint": {
                    "modules": [
                        {
                            "name": "core",
                            "role": "mass",
                            "bbox": [[0, 0, 0], [3, 3, 3]],
                            "size": [4, 4, 4],
                        }
                    ]
                }
            }
        }
        payload = _module_preview_payload(state, str(preview_path), "core")

    assert payload["module_filtered"] is True
    assert payload["module"]["name"] == "core"
    assert payload["preview_count"] == 2
    assert payload["module_source_count"] == 3
    assert payload["blocks"] == [[0, 0, 0, "stone"], [2, 2, 2, "stone"]]
    print({"preview_module_api": "ok"})


if __name__ == "__main__":
    main()
