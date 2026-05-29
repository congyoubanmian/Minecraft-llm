from __future__ import annotations

import shutil
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from backend.config import ROOT_DIR, settings
from backend.minecraft.rcon import MinecraftRcon, RconConfig


WORLD_DIRS = ("world", "world_nether", "world_the_end")


def world_status() -> dict[str, Any]:
    return {
        "worlds": [_world_dir_status(name) for name in WORLD_DIRS],
        "backups": _backup_status(),
        "rcon": _rcon_status(),
    }


def backup_worlds() -> dict[str, Any]:
    backup_root = _backup_root()
    backup_root.mkdir(parents=True, exist_ok=True)
    backup_dir = backup_root / f"world_backup_{_timestamp()}"
    backup_dir.mkdir(parents=True, exist_ok=False)
    copied: list[dict[str, Any]] = []
    for name in WORLD_DIRS:
        source = _server_dir() / name
        if not source.exists():
            continue
        target = backup_dir / name
        shutil.copytree(source, target)
        copied.append({"name": name, "bytes": _path_size(target)})
    return {
        "backup": str(backup_dir.relative_to(ROOT_DIR)),
        "copied": copied,
        "bytes": _path_size(backup_dir),
    }


def reset_worlds() -> dict[str, Any]:
    backup = backup_worlds()
    _compose("stop", "bot", "minecraft")
    reset_dir = _backup_root() / f"world_reset_{_timestamp()}"
    reset_dir.mkdir(parents=True, exist_ok=False)
    moved: list[str] = []
    for name in WORLD_DIRS:
        source = _server_dir() / name
        if not source.exists():
            continue
        shutil.move(str(source), str(reset_dir / name))
        moved.append(name)
    _compose("up", "-d", "minecraft", "bot")
    return {
        "backup_before_reset": backup,
        "reset_backup": str(reset_dir.relative_to(ROOT_DIR)),
        "moved": moved,
    }


def _rcon_status() -> dict[str, Any]:
    try:
        rcon = MinecraftRcon(
            RconConfig(
                host=settings.rcon_host,
                port=settings.rcon_port,
                password=settings.rcon_password,
            )
        )
        tps = rcon.command("tps")
        players = rcon.command("list")
        return {"ok": True, "tps": _strip_minecraft_codes(tps), "players": _strip_minecraft_codes(players)}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": repr(exc)}


def _world_dir_status(name: str) -> dict[str, Any]:
    path = _server_dir() / name
    return {
        "name": name,
        "exists": path.exists(),
        "bytes": _path_size(path) if path.exists() else 0,
        "path": str(path.relative_to(ROOT_DIR)) if path.exists() else str(path),
    }


def _backup_status() -> dict[str, Any]:
    root = _backup_root()
    if not root.exists():
        return {"count": 0, "bytes": 0, "latest": None}
    entries = [path for path in root.iterdir() if path.is_dir() or path.is_file()]
    entries.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return {
        "count": len(entries),
        "bytes": _path_size(root),
        "latest": str(entries[0].relative_to(ROOT_DIR)) if entries else None,
    }


def _compose(*args: str) -> None:
    result = subprocess.run(
        ["docker-compose", *args],
        cwd=ROOT_DIR,
        text=True,
        capture_output=True,
        timeout=180,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"docker-compose {' '.join(args)} failed: {result.stderr[-2000:] or result.stdout[-2000:]}")


def _path_size(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    total = 0
    for item in path.rglob("*"):
        if item.is_file():
            try:
                total += item.stat().st_size
            except OSError:
                continue
    return total


def _server_dir() -> Path:
    return ROOT_DIR / "server"


def _backup_root() -> Path:
    return ROOT_DIR / "backups"


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _strip_minecraft_codes(value: str) -> str:
    value = re.sub(r"\x1b\[[0-9;]*m", "", value)
    value = re.sub(r"\u00a7.", "", value)
    return value.strip()
