from __future__ import annotations

from pathlib import Path

from backend.config import settings
from backend.minecraft.bot_client import BotClient


class FaweController:
    def __init__(self) -> None:
        self.bot = BotClient()

    def paste_schematic(self, schematic_path: Path, x: int, y: int, z: int) -> list[str]:
        return self.bot.paste_schematic(schematic_path, x, y, z)
