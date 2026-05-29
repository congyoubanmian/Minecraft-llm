from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import backend.placement.registry as registry_module
from backend.placement.registry import PlacementRegistry, archive_project_placement, rebuild_placement_registry, upsert_project_placement


def sample_placement(x: int = 10) -> dict:
    return {
        "project_id": "demo",
        "paste": {"x": x, "y": 80, "z": 20},
        "spawn": {"x": x + 8, "y": 100, "z": -20},
        "size": {"x": 16, "y": 20, "z": 16},
        "bounds": {"min_x": x, "min_y": 80, "min_z": 20, "max_x": x + 15, "max_y": 99, "max_z": 35},
        "margin": 48,
    }


def main() -> None:
    with TemporaryDirectory() as tmp:
        registry_path = Path(tmp) / "registry.json"
        original = registry_module.REGISTRY_PATH
        registry_module.REGISTRY_PATH = registry_path
        try:
            record = upsert_project_placement(project_id="demo", placement=sample_placement(), project_name="Demo", pasted=True)
            assert record["active"] is True
            assert record["pasted"] is True
            payload = PlacementRegistry(path=registry_path).load()
            assert len(payload["placements"]) == 1

            upsert_project_placement(project_id="demo", placement=sample_placement(40), project_name="Demo 2", pasted=False)
            payload = PlacementRegistry(path=registry_path).load()
            assert len(payload["placements"]) == 1
            assert payload["placements"][0]["paste"]["x"] == 40
            assert payload["placements"][0]["pasted"] is True

            archive_project_placement("demo", reason="test")
            payload = PlacementRegistry(path=registry_path).load()
            assert payload["placements"][0]["active"] is False
            assert payload["placements"][0]["archive_reason"] == "test"

            rebuilt = rebuild_placement_registry(
                [
                    {
                        "id": "from_state",
                        "created_at": "2026-01-01T00:00:00+00:00",
                        "updated_at": "2026-01-01T00:00:00+00:00",
                        "plan": {"name": "project_from_state"},
                        "placement": sample_placement(90),
                        "rcon": ["/paste"],
                    }
                ]
            )
            assert len(rebuilt["placements"]) == 1
            assert rebuilt["placements"][0]["project_id"] == "from_state"
            assert rebuilt["placements"][0]["pasted"] is True
        finally:
            registry_module.REGISTRY_PATH = original

    print({"placement_registry": "ok"})


if __name__ == "__main__":
    main()
