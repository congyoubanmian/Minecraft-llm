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
    download_project_module_snapshot,
    get_project,
    get_project_module_operations,
    get_project_module_snapshots,
    cleanup_project_module_snapshots,
    list_projects,
    ModuleSnapshotCleanupRequest,
    _save_project,
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
                    "id": "snapshot-core-generated",
                    "module": "core",
                    "created_at": "2026-01-01T00:00:00+00:00",
                    "source": "generated",
                    "path": str(snapshot_file),
                },
                {"module": "roof", "created_at": "2026-01-01T00:01:00+00:00", "source": "world"},
                {"module": "core", "created_at": "2026-01-01T00:02:00+00:00", "source": "world"},
            ],
        }
        _save_project(project_id, state)

        payload = get_project_module_operations(project_id)
        assert payload["project_id"] == project_id
        assert len(payload["module_operations"]) == 1
        assert payload["module_rcon"]["core:replace"] == ["a"]

        project_payload = get_project(project_id)
        assert project_payload["module_snapshots"][0]["file"]["exists"] is True
        disk_state = json.loads((project_dir / "state.json").read_text(encoding="utf-8"))
        assert "file" not in disk_state["module_snapshots"][0]

        projects_payload = list_projects()
        project_summary = next(item for item in projects_payload["projects"] if item["id"] == project_id)
        assert project_summary["snapshot_summary"]["count"] == 3
        assert project_summary["snapshot_summary"]["available_count"] == 1
        assert project_summary["snapshot_summary"]["missing_count"] == 0
        assert project_summary["snapshot_summary"]["module_count"] == 2
        assert project_summary["snapshot_summary"]["bytes"] == len(b"snapshot")

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
        assert core_snapshots["snapshots"][0]["file"]["exists"] is False
        assert core_snapshots["snapshots"][1]["file"]["exists"] is True
        assert core_snapshots["snapshots"][1]["file"]["name"] == snapshot_file.name
        assert core_snapshots["snapshots"][1]["file"]["size"] == len(b"snapshot")
        assert core_snapshots["snapshots"][1]["file"]["managed"] is True

        cleanup = cleanup_project_module_snapshots(
            project_id,
            ModuleSnapshotCleanupRequest(confirm="CLEANUP_MISSING_MODULE_SNAPSHOTS", module="core"),
        )
        assert cleanup["removed_count"] == 0
        assert cleanup["remaining_count"] == 3

        missing_snapshot_file = main_module.settings.schematic_dir / "missing_snapshot.schem"
        state["module_snapshots"].append(
            {
                "id": "snapshot-core-missing",
                "module": "core",
                "created_at": "2026-01-01T00:03:00+00:00",
                "source": "generated",
                "path": str(missing_snapshot_file),
            }
        )
        _save_project(project_id, state)
        projects_payload = list_projects()
        project_summary = next(item for item in projects_payload["projects"] if item["id"] == project_id)
        assert project_summary["snapshot_summary"]["missing_count"] == 1

        cleanup = cleanup_project_module_snapshots(
            project_id,
            ModuleSnapshotCleanupRequest(confirm="CLEANUP_MISSING_MODULE_SNAPSHOTS", module="core"),
        )
        assert cleanup["removed_count"] == 1
        assert cleanup["remaining_count"] == 3
        assert cleanup["removed_snapshots"][0]["id"] == "snapshot-core-missing"
        assert cleanup["snapshot_summary"]["missing_count"] == 0

        download = download_project_module_snapshot(project_id, snapshot_id="snapshot-core-generated")
        assert Path(download.path) == snapshot_file
        assert download.filename == snapshot_file.name

        deleted = delete_project_module_snapshot(
            project_id,
            ModuleSnapshotDeleteRequest(confirm="DELETE_MODULE_SNAPSHOT", snapshot_id="snapshot-core-generated"),
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
