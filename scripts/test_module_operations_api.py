from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import backend.main as main_module
from backend.main import (
    ModuleSnapshotDeleteRequest,
    clear_project_module_operations,
    delete_project_module_snapshot,
    get_project_module_operations,
    get_project_module_snapshots,
)


def main() -> None:
    project_id = "module_ops_api_smoke"
    project_dir = ROOT / "backend" / "projects" / project_id
    if project_dir.exists():
        raise RuntimeError(f"test project directory already exists: {project_dir}")
    original_schematic_dir = main_module.settings.schematic_dir
    try:
        project_dir.mkdir(parents=True)
        main_module.settings.schematic_dir = project_dir / "schematics"
        main_module.settings.schematic_dir.mkdir(parents=True)
        snapshot_file = main_module.settings.schematic_dir / "core_snapshot.schem"
        snapshot_file.write_bytes(b"snapshot")
        state = {
            "id": project_id,
            "updated_at": "2026-01-01T00:00:00+00:00",
            "module_operations": [{"module": "core", "action": "replace", "commands": ["a"]}],
            "module_rcon": {"core:replace": ["a"]},
            "module_snapshots": [
                {
                    "module": "core",
                    "created_at": "2026-01-01T00:00:00+00:00",
                    "source": "generated",
                    "path": str(snapshot_file),
                },
                {"module": "roof", "created_at": "2026-01-01T00:01:00+00:00", "source": "world"},
                {"module": "core", "created_at": "2026-01-01T00:02:00+00:00", "source": "world"},
            ],
        }
        (project_dir / "state.json").write_text(json.dumps(state), encoding="utf-8")

        payload = get_project_module_operations(project_id)
        assert payload["project_id"] == project_id
        assert len(payload["module_operations"]) == 1
        assert payload["module_rcon"]["core:replace"] == ["a"]

        snapshots = get_project_module_snapshots(project_id)
        assert snapshots["project_id"] == project_id
        assert snapshots["snapshot_count"] == 3
        assert snapshots["snapshots"][0]["module"] == "core"
        assert snapshots["snapshots"][0]["created_at"].endswith("00:02:00+00:00")

        core_snapshots = get_project_module_snapshots(project_id, module="core")
        assert core_snapshots["module"] == "core"
        assert core_snapshots["snapshot_count"] == 2
        assert core_snapshots["snapshots"][0]["source"] == "world"
        assert core_snapshots["snapshots"][1]["source"] == "generated"

        deleted = delete_project_module_snapshot(
            project_id,
            ModuleSnapshotDeleteRequest(confirm="DELETE_MODULE_SNAPSHOT", snapshot_path=str(snapshot_file)),
        )
        assert deleted["file_removed"] is True
        assert not snapshot_file.exists()

        after_delete = get_project_module_snapshots(project_id)
        assert after_delete["snapshot_count"] == 2

        cleared = clear_project_module_operations(project_id)
        assert cleared["removed_operations"] == 1
        assert cleared["removed_rcon"] == 1

        new_state = json.loads((project_dir / "state.json").read_text(encoding="utf-8"))
        assert new_state["module_operations"] == []
        assert new_state["module_rcon"] == {}
    finally:
        main_module.settings.schematic_dir = original_schematic_dir
        shutil.rmtree(project_dir, ignore_errors=True)

    print({"module_operations_api": "ok"})


if __name__ == "__main__":
    main()
