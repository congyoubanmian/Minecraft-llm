from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.minecraft.world_manager import WORLD_DIRS, world_status


def main() -> None:
    status = world_status()
    assert {item["name"] for item in status["worlds"]} == set(WORLD_DIRS)
    assert "backups" in status
    assert "rcon" in status
    for item in status["worlds"]:
        assert isinstance(item["exists"], bool)
        assert isinstance(item["bytes"], int)
    print(
        {
            "worlds": [(item["name"], item["exists"], item["bytes"]) for item in status["worlds"]],
            "rcon_ok": status["rcon"].get("ok"),
            "backup_count": status["backups"].get("count"),
        }
    )


if __name__ == "__main__":
    main()
