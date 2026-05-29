from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.config import ROOT_DIR


REGISTRY_PATH = ROOT_DIR / "backend" / "placement" / "registry.json"


@dataclass(frozen=True)
class PlacementRegistry:
    path: Path = REGISTRY_PATH

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"version": 1, "updated_at": None, "placements": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, payload: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload["version"] = 1
        payload["updated_at"] = _now()
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def list_placements(active_only: bool = False) -> list[dict[str, Any]]:
    placements = _registry().load().get("placements", [])
    if active_only:
        placements = [item for item in placements if item.get("active", True)]
    return sorted(placements, key=lambda item: item.get("updated_at") or item.get("created_at") or "", reverse=True)


def upsert_project_placement(
    *,
    project_id: str,
    placement: dict[str, Any],
    project_name: str | None = None,
    pasted: bool = False,
) -> dict[str, Any]:
    registry = _registry()
    payload = registry.load()
    items = [item for item in payload.get("placements", []) if item.get("project_id") != project_id]
    existing = next((item for item in payload.get("placements", []) if item.get("project_id") == project_id), {})
    now = _now()
    record = {
        "project_id": project_id,
        "project_name": project_name or existing.get("project_name") or f"project_{project_id}",
        "paste": placement.get("paste"),
        "spawn": placement.get("spawn"),
        "size": placement.get("size"),
        "bounds": placement.get("bounds"),
        "margin": placement.get("margin"),
        "active": True,
        "pasted": pasted or bool(existing.get("pasted")),
        "created_at": existing.get("created_at") or now,
        "updated_at": now,
    }
    items.append(record)
    payload["placements"] = items
    registry.save(payload)
    return record


def archive_project_placement(project_id: str, *, reason: str = "archived") -> None:
    registry = _registry()
    payload = registry.load()
    changed = False
    for item in payload.get("placements", []):
        if item.get("project_id") == project_id and item.get("active", True):
            item["active"] = False
            item["archived_at"] = _now()
            item["archive_reason"] = reason
            item["updated_at"] = _now()
            changed = True
    if changed:
        registry.save(payload)


def rebuild_placement_registry(project_states: list[dict[str, Any]]) -> dict[str, Any]:
    registry = _registry()
    placements = []
    now = _now()
    for state in project_states:
        placement = state.get("placement")
        if not placement:
            continue
        plan = state.get("plan") or {}
        placements.append(
            {
                "project_id": state.get("id"),
                "project_name": plan.get("name") or f"project_{state.get('id', '')}",
                "paste": placement.get("paste"),
                "spawn": placement.get("spawn"),
                "size": placement.get("size"),
                "bounds": placement.get("bounds"),
                "margin": placement.get("margin"),
                "active": True,
                "pasted": bool(state.get("rcon")),
                "created_at": state.get("created_at") or now,
                "updated_at": state.get("updated_at") or now,
            }
        )
    payload = {"version": 1, "updated_at": now, "placements": placements}
    registry.save(payload)
    return payload


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _registry() -> PlacementRegistry:
    return PlacementRegistry(path=REGISTRY_PATH)
