from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import backend.main as main_module
from backend.main import (
    MODULE_CLEAR_BLOCK_LIMIT,
    _bounds_volume,
    _clear_module_area,
    _clear_module_plan,
    _delete_module_snapshot,
    _latest_module_snapshot,
    _module_snapshot_by_ref,
    _snapshot_by_ref,
    _module_operation_plan,
    _module_world_target,
    _record_module_operation,
    _snapshot_module_schematic,
)


def main() -> None:
    placement = {
        "paste": {"x": 100, "y": 64, "z": 200},
    }
    module = {
        "name": "skybridge",
        "role": "circulation",
        "bbox": [[10, 40, 20], [50, 48, 30]],
    }
    target = _module_world_target(placement, module)

    assert target["name"] == "skybridge"
    assert target["world_bounds"] == {
        "min_x": 110,
        "min_y": 104,
        "min_z": 220,
        "max_x": 150,
        "max_y": 112,
        "max_z": 230,
    }
    assert target["teleport"]["x"] == 130
    assert target["teleport"]["y"] == 108
    assert target["teleport"]["z"] == 192
    assert _bounds_volume(target["world_bounds"]) == 4059
    clear_plan = _clear_module_plan(target)
    assert clear_plan["blocks"] == 4059
    assert clear_plan["command"] == "/fill 110 104 220 150 112 230 air replace"
    assert clear_plan["safe"] is True
    assert clear_plan["limit"] == MODULE_CLEAR_BLOCK_LIMIT

    operation_plan = _module_operation_plan("project-1", {"block_count": 4059}, "skybridge", target)
    assert operation_plan["project_id"] == "project-1"
    assert operation_plan["module"]["name"] == "skybridge"
    assert operation_plan["world_bounds"] == target["world_bounds"]
    assert operation_plan["paste"] == {"x": 110, "y": 104, "z": 220}
    assert operation_plan["replace"]["steps"] == ["clear", "paste"]
    assert operation_plan["replace"]["safe"] is True
    assert operation_plan["schematic_path"] is None

    original_rcon = main_module._rcon_command
    try:
        main_module._rcon_command = lambda command: f"ran:{command}"
        cleared = _clear_module_area(target)
    finally:
        main_module._rcon_command = original_rcon
    assert cleared["blocks"] == 4059
    assert cleared["command"] == "/fill 110 104 220 150 112 230 air replace"
    assert cleared["response"] == "ran:fill 110 104 220 150 112 230 air replace"

    huge_target = {
        **target,
        "world_bounds": {"min_x": 0, "min_y": 0, "min_z": 0, "max_x": 100, "max_y": 100, "max_z": 100},
    }
    huge_plan = _clear_module_plan(huge_target)
    assert huge_plan["blocks"] == 1030301
    assert huge_plan["safe"] is False

    original_project_dir = main_module.settings.project_dir
    original_schematic_dir = main_module.settings.schematic_dir
    original_fawe_controller = main_module.FaweController
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            main_module.settings.project_dir = Path(tmp_dir)
            main_module.settings.schematic_dir = Path(tmp_dir) / "schematics"
            source_path = Path(tmp_dir) / "source.schem"
            source_path.write_bytes(b"schem-data")
            snapshot_state = {"schematic_path": str(source_path)}
            snapshot = _snapshot_module_schematic("project-1", snapshot_state, "skybridge", target, prefer_world=False)
            assert snapshot is not None
            assert snapshot["id"]
            assert snapshot["module"] == "skybridge"
            assert snapshot["source"] == "generated"
            assert Path(snapshot["path"]).exists()
            assert Path(snapshot["path"]).parent == main_module.settings.schematic_dir
            assert Path(snapshot["path"]).read_bytes() == b"schem-data"
            assert _latest_module_snapshot(snapshot_state, "skybridge") == snapshot
            assert _module_snapshot_by_ref(snapshot_state, "skybridge") == snapshot
            assert _module_snapshot_by_ref(snapshot_state, "skybridge", snapshot_id=snapshot["id"]) == snapshot
            assert _module_snapshot_by_ref(snapshot_state, "skybridge", snapshot_path=snapshot["path"]) == snapshot
            assert _module_snapshot_by_ref(snapshot_state, "skybridge", snapshot_path="/tmp/missing.schem") is None
            assert _snapshot_by_ref(snapshot_state, snapshot_id=snapshot["id"]) == snapshot
            assert _snapshot_by_ref(snapshot_state, snapshot_path=snapshot["path"]) == snapshot
            assert _snapshot_by_ref(snapshot_state, snapshot_path="/tmp/missing.schem") is None
            delete_state = {"module_snapshots": [snapshot]}
            deleted = _delete_module_snapshot(delete_state, snapshot_id=snapshot["id"])
            assert deleted is not None
            assert deleted["snapshot"] == snapshot
            assert deleted["file_removed"] is True
            assert delete_state["module_snapshots"] == []
            assert not Path(snapshot["path"]).exists()
            assert _delete_module_snapshot(delete_state, snapshot_id=snapshot["id"]) is None

            class FakeFaweController:
                def save_region(self, schematic_path, bounds):
                    schematic_path.write_bytes(b"world-data")
                    assert bounds == target["world_bounds"]
                    return ["//pos1", "//pos2", "//copy", "/schem save"]

            main_module.FaweController = FakeFaweController
            world_state = {"schematic_path": str(source_path)}
            world_snapshot = _snapshot_module_schematic("project-1", world_state, "skybridge", target)
            assert world_snapshot is not None
            assert world_snapshot["source"] == "world"
            assert world_snapshot["commands"][-1] == "/schem save"
            assert Path(world_snapshot["path"]).read_bytes() == b"world-data"

            class FailingFaweController:
                def save_region(self, schematic_path, bounds):
                    raise RuntimeError("bot unavailable")

            main_module.FaweController = FailingFaweController
            fallback_state = {"schematic_path": str(source_path)}
            fallback_snapshot = _snapshot_module_schematic("project-1", fallback_state, "skybridge", target)
            assert fallback_snapshot is not None
            assert fallback_snapshot["source"] == "generated"
            assert fallback_snapshot["fallback_error"] == "bot unavailable"
            assert Path(fallback_snapshot["path"]).read_bytes() == b"schem-data"

            failed_snapshot = _snapshot_module_schematic("project-1", {}, "skybridge", target)
            assert failed_snapshot is not None
            assert failed_snapshot["source"] == "failed"
            assert failed_snapshot["error"] == "bot unavailable"

            main_module.FaweController = original_fawe_controller
            missing_snapshot = _snapshot_module_schematic("project-1", {}, "skybridge", target, prefer_world=False)
            assert missing_snapshot is None
    finally:
        main_module.settings.project_dir = original_project_dir
        main_module.settings.schematic_dir = original_schematic_dir
        main_module.FaweController = original_fawe_controller

    state = {}
    operation = _record_module_operation(
        state,
        "skybridge",
        "replace",
        target,
        ["clear", "paste"],
        blocks=4059,
        snapshot={"module": "skybridge", "path": "/tmp/skybridge.schem"},
    )
    assert operation["module"] == "skybridge"
    assert operation["action"] == "replace"
    assert operation["command_count"] == 2
    assert operation["blocks"] == 4059
    assert operation["snapshot"]["module"] == "skybridge"
    assert len(state["module_operations"]) == 1
    for index in range(60):
        _record_module_operation(state, f"m{index}", "paste", target, ["paste"])
    assert len(state["module_operations"]) == 50
    assert state["module_operations"][0]["module"] == "m10"
    print({"module_teleport_target": "ok"})


if __name__ == "__main__":
    main()
