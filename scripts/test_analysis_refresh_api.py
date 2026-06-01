from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import backend.main as main_module
from backend.main import _save_project, get_project, refresh_project_analysis_report


def main() -> None:
    original_project_dir = main_module.settings.project_dir
    with tempfile.TemporaryDirectory() as tmp:
        main_module.settings.project_dir = Path(tmp)
        project_id = "analysis_refresh_smoke"
        try:
            state = {
                "id": project_id,
                "updated_at": "2026-01-01T00:00:00+00:00",
                "analysis_report": {"legacy": True},
                "plan": {
                    "name": "analysis_refresh_smoke",
                    "size": [12, 8, 8],
                    "origin": [0, 64, 0],
                    "palette": {"wall": "white_concrete"},
                    "analysis": {
                        "design_spec": {
                            "building_type": "custom",
                            "scale_intent": "refresh old diagnostics",
                            "modules": [
                                {
                                    "name": "left",
                                    "role": "mass",
                                    "bbox": [[0, 0, 0], [3, 4, 3]],
                                },
                                {
                                    "name": "right",
                                    "role": "mass",
                                    "bbox": [[8, 0, 0], [11, 4, 3]],
                                },
                            ],
                            "interfaces": [
                                {
                                    "module_a": "left",
                                    "face_a": "east",
                                    "module_b": "right",
                                    "face_b": "west",
                                    "kind": "touch",
                                }
                            ],
                        }
                    },
                    "parts": [
                        {"type": "box", "from": [0, 0, 0], "to": [3, 4, 3], "block": "wall"},
                        {"type": "box", "from": [8, 0, 0], "to": [11, 4, 3], "block": "wall"},
                    ],
                },
            }
            _save_project(project_id, state)
            result = refresh_project_analysis_report(project_id)
            report = result["analysis_report"]
            assert report["design_blueprint"]["interface_checks"][0]["status"] == "gap"
            assert result["analysis_report_path"].endswith("analysis_refresh_smoke.analysis.json")

            path = Path(result["analysis_report_path"])
            assert path.exists()
            assert json.loads(path.read_text(encoding="utf-8"))["design_blueprint"]["interface_checks"][0]["status"] == "gap"

            project = get_project(project_id)
            assert project["analysis_report"]["design_blueprint"]["interface_checks"][0]["status"] == "gap"
            assert project["analysis_report_path"] == str(path)
        finally:
            shutil.rmtree(Path(tmp) / project_id, ignore_errors=True)
            main_module.settings.project_dir = original_project_dir

    print({"analysis_refresh_api": "ok"})


if __name__ == "__main__":
    main()
