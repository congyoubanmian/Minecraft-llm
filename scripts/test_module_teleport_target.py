from __future__ import annotations

import sys
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
    _module_operation_plan,
    _module_world_target,
    _record_module_operation,
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

    state = {}
    operation = _record_module_operation(state, "skybridge", "replace", target, ["clear", "paste"], blocks=4059)
    assert operation["module"] == "skybridge"
    assert operation["action"] == "replace"
    assert operation["command_count"] == 2
    assert operation["blocks"] == 4059
    assert len(state["module_operations"]) == 1
    for index in range(60):
        _record_module_operation(state, f"m{index}", "paste", target, ["paste"])
    assert len(state["module_operations"]) == 50
    assert state["module_operations"][0]["module"] == "m10"
    print({"module_teleport_target": "ok"})


if __name__ == "__main__":
    main()
