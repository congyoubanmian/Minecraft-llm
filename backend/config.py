from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    upload_dir: Path = ROOT_DIR / "backend" / "uploads"
    schematic_dir: Path = ROOT_DIR / "server" / "plugins" / "FastAsyncWorldEdit" / "schematics"
    project_dir: Path = ROOT_DIR / "backend" / "projects"

    rcon_host: str = "localhost"
    rcon_port: int = 25575
    rcon_password: str = "minecraft-ai-builder"
    bot_url: str = "http://localhost:3001"

    paste_x: int = 0
    paste_y: int = 80
    paste_z: int = 0
    paste_base_x: int = 3200
    paste_base_y: int = 82
    paste_base_z: int = 40
    paste_margin: int = 48
    paste_row_width: int = 900
    spawn_offset_z: int = -40
    spawn_y_offset: int = 24

    paste_enabled: bool = True

    planner_mode: str = "codex"
    generated_plan_dir: Path = ROOT_DIR / "backend" / "generated_plans"
    codex_command: str = "codex"
    codex_model: str | None = None
    codex_timeout_seconds: int = 420

    cors_origins: str = "http://localhost:8000,http://localhost:5173,http://localhost:3000"

    rate_limit_per_minute: int = 10

    api_key: str = ""


settings = Settings()
