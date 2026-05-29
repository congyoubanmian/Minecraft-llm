from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import backend.main as main_module
from backend.main import _bounds_volume, _clear_module_area, _module_world_target


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
    original_rcon = main_module._rcon_command
    try:
        main_module._rcon_command = lambda command: f"ran:{command}"
        cleared = _clear_module_area(target)
    finally:
        main_module._rcon_command = original_rcon
    assert cleared["blocks"] == 4059
    assert cleared["command"] == "/fill 110 104 220 150 112 230 air replace"
    assert cleared["response"] == "ran:fill 110 104 220 150 112 230 air replace"
    print({"module_teleport_target": "ok"})


if __name__ == "__main__":
    main()
