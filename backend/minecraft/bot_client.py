from __future__ import annotations

from pathlib import Path

import httpx

from backend.config import settings


class BotClient:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or settings.bot_url).rstrip("/")

    def paste_schematic(self, schematic_path: Path, x: int, y: int, z: int) -> list[str]:
        response = httpx.post(
            f"{self.base_url}/paste",
            json={"schematic": schematic_path.stem, "x": x, "y": y, "z": z},
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        return payload.get("commands", [])

    def save_region(self, schematic_path: Path, bounds: dict[str, int]) -> list[str]:
        response = httpx.post(
            f"{self.base_url}/save-region",
            json={
                "schematic": schematic_path.stem,
                "min_x": bounds["min_x"],
                "min_y": bounds["min_y"],
                "min_z": bounds["min_z"],
                "max_x": bounds["max_x"],
                "max_y": bounds["max_y"],
                "max_z": bounds["max_z"],
            },
            timeout=90,
        )
        response.raise_for_status()
        payload = response.json()
        return payload.get("commands", [])
