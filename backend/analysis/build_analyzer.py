from __future__ import annotations

from collections import Counter
from typing import Any

from backend.blocks import BlockList
from backend.dsl.schema import BuildPlan, ComponentPart
from backend.library import load_components, load_templates


def analyze_build(plan: BuildPlan, blocks: BlockList) -> dict[str, Any]:
    """Return lightweight design diagnostics for UI and prompt feedback."""
    materials = blocks.material_counts()
    total = sum(materials.values())
    component_counts = Counter(part.name for part in plan.parts if isinstance(part, ComponentPart))
    categories = _component_categories(component_counts)
    template = _infer_template(plan, materials, categories)
    ratios = _material_ratios(materials, total)
    warnings = _warnings(plan, materials, ratios, component_counts, template)

    return {
        "template_guess": template,
        "size": list(plan.size),
        "aspect": _aspect(plan.size),
        "part_count": len(plan.parts),
        "design_spec": _design_spec_summary(plan.analysis or {}),
        "component_counts": dict(component_counts),
        "component_categories": categories,
        "material_ratios": ratios,
        "warnings": warnings,
    }


def _component_categories(component_counts: Counter[str]) -> dict[str, int]:
    components = load_components().get("components", {})
    categories: Counter[str] = Counter()
    for name, count in component_counts.items():
        category = components.get(name, {}).get("category", "unknown")
        categories[category] += count
    return dict(categories)


def _infer_template(plan: BuildPlan, materials: dict[str, int], categories: dict[str, int]) -> str | None:
    analysis_text = " ".join(_flatten_text(plan.analysis or {})).lower()
    templates = load_templates().get("templates", {})

    keyword_scores: dict[str, int] = {
        "pagoda_stack": _score(analysis_text, ["pagoda", "tower", "octagonal", "temple", "spire", "宝塔", "寺", "塔"]),
        "temple_hall": _score(analysis_text, ["temple", "hall", "gatehouse", "courtyard", "寺", "殿", "牌楼"]),
        "jiangnan_water_town": _score(analysis_text, ["jiangnan", "canal", "water", "old street", "江南", "水乡", "古镇"]),
        "modern_glass_gate": _score(analysis_text, ["gate", "void", "skybridge", "suzhou", "cctv", "大裤衩", "东方之门"]),
        "office_tower": _score(analysis_text, ["office", "curtain wall", "tower", "hotel", "办公", "玻璃幕墙"]),
        "stone_arch_bridge": _score(analysis_text, ["stone arch", "garden bridge", "canal bridge", "拱桥", "石桥"]),
        "suspension_bridge": _score(analysis_text, ["suspension", "cable", "highway bridge", "悬索桥", "斜拉桥"]),
    }

    if categories.get("tower") and _has_octagonal_or_copper(materials):
        keyword_scores["pagoda_stack"] += 4
    if categories.get("bridge"):
        keyword_scores["stone_arch_bridge"] += 2
        keyword_scores["suspension_bridge"] += 2
    if _ratio(materials, "glass") > 0.25 and plan.size[1] >= 48:
        keyword_scores["office_tower"] += 2
    if _ratio(materials, "glass") > 0.3 and ("void" in analysis_text or "gate" in analysis_text):
        keyword_scores["modern_glass_gate"] += 4

    best, score = max(keyword_scores.items(), key=lambda item: item[1])
    return best if score > 0 and best in templates else None


def _material_ratios(materials: dict[str, int], total: int) -> dict[str, float]:
    if total <= 0:
        return {"glass": 0.0, "light": 0.0, "wood": 0.0, "stone": 0.0, "roof": 0.0}
    return {
        "glass": round(sum(count for block, count in materials.items() if "glass" in block) / total, 4),
        "light": round(sum(count for block, count in materials.items() if block in {"lantern", "sea_lantern", "redstone_lamp", "glowstone"} or "light" in block) / total, 4),
        "wood": round(sum(count for block, count in materials.items() if any(token in block for token in ("oak", "spruce", "wood", "log", "planks"))) / total, 4),
        "stone": round(sum(count for block, count in materials.items() if any(token in block for token in ("stone", "deepslate", "andesite", "quartz"))) / total, 4),
        "roof": round(sum(count for block, count in materials.items() if any(token in block for token in ("tile", "copper", "stairs", "slab"))) / total, 4),
    }


def _warnings(
    plan: BuildPlan,
    materials: dict[str, int],
    ratios: dict[str, float],
    component_counts: Counter[str],
    template: str | None,
) -> list[str]:
    warnings: list[str] = []
    sx, sy, sz = plan.size

    if template in {"pagoda_stack", "temple_hall", "jiangnan_water_town"} and ratios["glass"] > 0.18:
        warnings.append("古建/水乡模板玻璃比例偏高，建议减少幕墙玻璃，改用小窗、木框、瓦面。")
    if template in {"modern_glass_gate", "office_tower"} and ratios["light"] < 0.005 and sy >= 48:
        warnings.append("现代高层灯光比例偏低，建议给办公楼层、连桥、入口重复布置 sea_lantern 或 redstone_lamp。")
    if template == "pagoda_stack" and not component_counts.get("pagoda_tier"):
        warnings.append("疑似宝塔但没有使用 pagoda_tier，八角层级可能不稳定。")
    if template == "modern_glass_gate" and "air" not in (plan.palette or {}) and ratios["glass"] < 0.25:
        warnings.append("门形地标需要清晰中央空洞和高玻璃比例；可用 air 清空中部，再加两侧办公层。")
    if sy > 96 and len(plan.parts) < 40:
        warnings.append("大型建筑 parts 数偏少，容易变成粗体量；建议增加 facade/interior/lighting/detail 分层部件。")
    if max(sx, sz) / max(1, min(sx, sz)) > 4 and template not in {"suspension_bridge", "stone_arch_bridge"}:
        warnings.append("平面长宽比很极端，如果不是桥梁，可能需要检查比例尺。")
    if not component_counts and len(plan.parts) >= 80:
        warnings.append("当前主要依赖 primitive parts，可考虑抽出重复窗格、楼层、屋檐或桥段组件复用。")
    design_spec = (plan.analysis or {}).get("design_spec") if isinstance(plan.analysis, dict) else None
    if not isinstance(design_spec, dict) or not design_spec.get("modules"):
        warnings.append("缺少设计规约模块列表，复杂建筑建议先定义 grid、modules、bbox、interfaces，再转 Minecraft parts。")
    return warnings


def _design_spec_summary(analysis: dict[str, Any]) -> dict[str, Any]:
    design_spec = analysis.get("design_spec") if isinstance(analysis, dict) else None
    if not isinstance(design_spec, dict):
        return {"present": False, "module_count": 0, "interface_count": 0}
    modules = design_spec.get("modules") if isinstance(design_spec.get("modules"), list) else []
    interfaces = design_spec.get("interfaces") if isinstance(design_spec.get("interfaces"), list) else []
    missing_bbox = [
        module.get("name", f"module_{index}")
        for index, module in enumerate(modules)
        if isinstance(module, dict) and not module.get("bbox")
    ]
    return {
        "present": True,
        "building_type": design_spec.get("building_type"),
        "module_count": len(modules),
        "interface_count": len(interfaces),
        "missing_bbox": missing_bbox,
    }


def _aspect(size: tuple[int, int, int]) -> dict[str, float]:
    sx, sy, sz = size
    return {
        "height_to_width": round(sy / max(1, sx), 3),
        "height_to_depth": round(sy / max(1, sz), 3),
        "width_to_depth": round(sx / max(1, sz), 3),
    }


def _flatten_text(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        output: list[str] = []
        for item in value.values():
            output.extend(_flatten_text(item))
        return output
    if isinstance(value, list):
        output = []
        for item in value:
            output.extend(_flatten_text(item))
        return output
    return [str(value)]


def _score(text: str, needles: list[str]) -> int:
    return sum(1 for needle in needles if needle.lower() in text)


def _ratio(materials: dict[str, int], token: str) -> float:
    total = sum(materials.values())
    if total <= 0:
        return 0.0
    return sum(count for block, count in materials.items() if token in block) / total


def _has_octagonal_or_copper(materials: dict[str, int]) -> bool:
    return any("copper" in block for block in materials)
