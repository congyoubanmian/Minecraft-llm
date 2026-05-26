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


@lru_cache(maxsize=1)
def load_templates() -> dict[str, Any]:
    return json.loads((LIBRARY_DIR / "templates.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_design_contract() -> dict[str, Any]:
    return json.loads((LIBRARY_DIR / "design_contract.json").read_text(encoding="utf-8"))


def get_component(name: str) -> dict[str, Any]:
    components = load_components().get("components", {})
    if name not in components:
        raise KeyError(f"unknown component: {name}")
    return components[name]


def get_library_context() -> dict[str, Any]:
    materials = load_materials().get("palettes", {})
    components = load_components().get("components", {})
    templates = load_templates().get("templates", {})
    design_contract = load_design_contract().get("design_contract", {})
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
                "category": value.get("category"),
                "styles": value.get("styles", []),
                "building_types": value.get("building_types", []),
                "stages": value.get("stages", []),
                "size": value.get("size"),
                "parameters": value.get("parameters", {}),
                "parameter_ranges": value.get("parameter_ranges", {}),
                "scale_range": value.get("scale_range"),
                "default_materials": value.get("default_materials", {}),
                "applicability": value.get("applicability"),
                "avoid_when": value.get("avoid_when"),
            }
            for key, value in components.items()
        },
        "templates": {
            key: {
                "description": value.get("description"),
                "style": value.get("style"),
                "building_types": value.get("building_types", []),
                "recommended_palettes": value.get("recommended_palettes", []),
                "component_sequence": value.get("component_sequence", []),
                "primitive_needs": value.get("primitive_needs", []),
                "avoid_components": value.get("avoid_components", []),
                "checks": value.get("checks", []),
                "scale_guidance": value.get("scale_guidance"),
            }
            for key, value in templates.items()
        },
        "design_contract": design_contract,
    }
