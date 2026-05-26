from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from backend.config import ROOT_DIR


LIBRARY_DIR = ROOT_DIR / "backend" / "library"


@lru_cache(maxsize=1)
def load_materials() -> dict[str, Any]:
    return json.loads((LIBRARY_DIR / "materials.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_components() -> dict[str, Any]:
    return json.loads((LIBRARY_DIR / "components.json").read_text(encoding="utf-8"))


def get_component(name: str) -> dict[str, Any]:
    components = load_components().get("components", {})
    if name not in components:
        raise KeyError(f"unknown component: {name}")
    return components[name]


def get_library_context() -> dict[str, Any]:
    materials = load_materials().get("palettes", {})
    components = load_components().get("components", {})
    return {
        "materials": {
            key: {
                "description": value.get("description"),
                "blocks": value.get("blocks"),
            }
            for key, value in materials.items()
        },
        "components": {
            key: {
                "description": value.get("description"),
                "size": value.get("size"),
                "parameters": value.get("parameters", {}),
                "default_materials": value.get("default_materials", {}),
            }
            for key, value in components.items()
        },
    }
