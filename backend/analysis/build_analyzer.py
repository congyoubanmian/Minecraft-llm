from __future__ import annotations

from collections import Counter
from typing import Any

from backend.blocks import BlockList
from backend.dsl.schema import BuildPlan, ComponentPart, DesignInterface, DesignModule, DesignSpec
from backend.library import load_components, load_templates


def analyze_build(plan: BuildPlan, blocks: BlockList) -> dict[str, Any]:
    """Return lightweight design diagnostics for UI and prompt feedback."""
    materials = blocks.material_counts()
    total = sum(materials.values())
    component_counts = Counter(part.name for part in plan.parts if isinstance(part, ComponentPart))
    categories = _component_categories(component_counts)
    template = _infer_template(plan, materials, categories)
    ratios = _material_ratios(materials, total)
    module_report = _module_report(plan)
    warnings = _warnings(plan, materials, ratios, component_counts, template, module_report)
    blueprint = _design_blueprint(plan, module_report, materials, warnings)

    return {
        "template_guess": template,
        "size": list(plan.size),
        "aspect": _aspect(plan.size),
        "part_count": len(plan.parts),
        "design_spec": module_report,
        "design_blueprint": blueprint,
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
    analysis_text = " ".join(_flatten_text(plan.analysis_dict())).lower()
    templates = load_templates().get("templates", {})

    keyword_scores: dict[str, int] = {
        "pagoda_stack": _score(analysis_text, ["pagoda", "tower", "octagonal", "temple", "spire", "宝塔", "寺", "塔"]),
        "temple_hall": _score(analysis_text, ["temple", "hall", "gatehouse", "courtyard", "寺", "殿", "牌楼"]),
        "jiangnan_water_town": _score(analysis_text, ["jiangnan", "canal", "water", "old street", "江南", "水乡", "古镇"]),
        "modern_glass_gate": _score(analysis_text, ["gate", "void", "skybridge", "suzhou", "cctv", "大裤衩", "东方之门"]),
        "office_tower": _score(analysis_text, ["office", "curtain wall", "tower", "hotel", "办公", "玻璃幕墙"]),
        "stone_arch_bridge": _score(analysis_text, ["stone arch", "garden bridge", "canal bridge", "拱桥", "石桥"]),
        "suspension_bridge": _score(analysis_text, ["suspension", "cable", "highway bridge", "悬索桥", "斜拉桥"]),
        "twisted_lattice_tower": _score(analysis_text, ["canton tower", "guangzhou tower", "xiaomanyao", "tv tower", "hyperboloid", "广州塔", "小蛮腰", "电视塔"]),
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
    if "twisted_lattice_tower" in analysis_text:
        keyword_scores["twisted_lattice_tower"] += 5

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
    module_report: dict[str, Any],
) -> list[str]:
    warnings: list[str] = []
    sx, sy, sz = plan.size
    total_blocks = sum(materials.values())

    if template in {"pagoda_stack", "temple_hall", "jiangnan_water_town"} and ratios["glass"] > 0.18:
        warnings.append("古建/水乡模板玻璃比例偏高，建议减少幕墙玻璃，改用小窗、木框、瓦面。")
    if template in {"modern_glass_gate", "office_tower"} and ratios["light"] < 0.005 and sy >= 48:
        warnings.append("现代高层灯光比例偏低，建议给办公楼层、连桥、入口重复布置 sea_lantern 或 redstone_lamp。")
    if template == "pagoda_stack" and not component_counts.get("pagoda_tier"):
        warnings.append("疑似宝塔但没有使用 pagoda_tier，八角层级可能不稳定。")
    if any(token in " ".join(_flatten_text(plan.analysis_dict())).lower() for token in ("广州塔", "小蛮腰", "canton tower", "guangzhou tower")):
        if template != "twisted_lattice_tower":
            warnings.append("广州塔/小蛮腰应使用 twisted_lattice_tower 模板，当前模板可能会跑成宝塔或普通高楼。")
        if sy / max(1, max(sx, sz)) < 2.5:
            warnings.append("广州塔比例偏矮胖，高度应至少是最大宽度/深度的 2.5 倍。")
    if template == "modern_glass_gate" and "air" not in (plan.palette or {}) and ratios["glass"] < 0.25:
        warnings.append("门形地标需要清晰中央空洞和高玻璃比例；可用 air 清空中部，再加两侧办公层。")
    if sy > 96 and len(plan.parts) < 40 and not _has_part_type(plan, "twisted_lattice_tower"):
        warnings.append("大型建筑 parts 数偏少，容易变成粗体量；建议增加 facade/interior/lighting/detail 分层部件。")
    if max(sx, sz) / max(1, min(sx, sz)) > 4 and template not in {"suspension_bridge", "stone_arch_bridge"}:
        warnings.append("平面长宽比很极端，如果不是桥梁，可能需要检查比例尺。")
    if not component_counts and len(plan.parts) >= 80:
        warnings.append("当前主要依赖 primitive parts，可考虑抽出重复窗格、楼层、屋檐或桥段组件复用。")
    if not module_report.get("present") or not module_report.get("module_count"):
        warnings.append("缺少设计规约模块列表，复杂建筑建议先定义 grid、modules、bbox、interfaces，再转 Minecraft parts。")
    warnings.extend(_performance_warnings(total_blocks, module_report.get("performance_budget")))
    warnings.extend(module_report.get("warnings", []))
    return warnings


def _performance_warnings(total_blocks: int, performance_budget: dict[str, Any] | None) -> list[str]:
    if not performance_budget:
        return []
    warnings: list[str] = []
    max_blocks = performance_budget.get("max_blocks")
    if isinstance(max_blocks, int) and total_blocks > max_blocks:
        warnings.append(f"方块数 {total_blocks} 超过 performance_budget.max_blocks={max_blocks}，建议降低细节密度或拆分项目。")
    max_preview_blocks = performance_budget.get("max_preview_blocks")
    if isinstance(max_preview_blocks, int) and total_blocks > max_preview_blocks:
        warnings.append(f"完整预览方块数超过 {max_preview_blocks}，前端应使用抽样或外表面 LOD。")
    max_tick_commands = performance_budget.get("max_tick_commands")
    animated = bool(performance_budget.get("animated"))
    if animated and isinstance(max_tick_commands, int) and max_tick_commands > 600:
        warnings.append("动态效果 tick 命令预算偏高，低配电脑或手机端可能卡顿，建议改静态灯光或局部动画。")
    if animated and max_tick_commands in (None, 0):
        warnings.append("标记为 animated 但没有设置 max_tick_commands，无法评估动态灯光性能。")
    return warnings


def _module_report(plan: BuildPlan) -> dict[str, Any]:
    design_spec = plan.analysis.design_spec if plan.analysis else None
    if design_spec is None:
        return {
            "present": False,
            "module_count": 0,
            "interface_count": 0,
            "modules": [],
            "performance_budget": None,
            "warnings": [],
            "stitch_ready": False,
        }

    modules = design_spec.modules
    interfaces = design_spec.interfaces
    module_items = [_normalize_module(module, index) for index, module in enumerate(modules)]
    module_names = [module["name"] for module in module_items]
    interface_checks = _interface_checks(module_items, interfaces)
    stage_checks = _stage_checks(module_items)
    warnings = _module_warnings(plan.size, module_items, interfaces, interface_checks, stage_checks)
    missing_bbox = [
        module["name"]
        for module in module_items
        if module["bbox"] is None
    ]

    return {
        "present": True,
        "building_type": design_spec.building_type,
        "scale_intent": design_spec.scale_intent,
        "grid": design_spec.grid,
        "module_count": len(module_items),
        "interface_count": len(interfaces),
        "missing_bbox": missing_bbox,
        "duplicate_names": _duplicates(module_names),
        "modules": module_items,
        "interfaces": [_interface_dump(interface) for interface in interfaces],
        "interface_checks": interface_checks,
        "material_schedule": design_spec.material_schedule,
        "quality_checks": design_spec.quality_checks,
        "performance_budget": _performance_budget_dump(design_spec),
        "stage_order": _stage_order(module_items),
        "stage_checks": stage_checks,
        "coverage": _module_coverage(plan.size, module_items),
        "warnings": warnings,
        "stitch_ready": bool(module_items) and not missing_bbox and not warnings,
    }


def _normalize_module(module: DesignModule, index: int) -> dict[str, Any]:
    name = module.name or f"module_{index}"
    role = module.role
    bbox = _parse_bbox(module.bbox)
    return {
        "name": name,
        "role": role,
        "bbox": bbox,
        "materials": module.materials,
        "interfaces": module.interfaces,
        "notes": module.notes,
        "volume": _bbox_volume(bbox) if bbox else 0,
    }


def _parse_bbox(value: Any) -> list[list[int]] | None:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        return None
    first, second = value
    if not (
        isinstance(first, (list, tuple))
        and isinstance(second, (list, tuple))
        and len(first) == 3
        and len(second) == 3
        and all(isinstance(item, int) for item in first + second)
    ):
        return None
    x1, y1, z1 = first
    x2, y2, z2 = second
    return [[min(x1, x2), min(y1, y2), min(z1, z2)], [max(x1, x2), max(y1, y2), max(z1, z2)]]


def _module_warnings(
    size: tuple[int, int, int],
    modules: list[dict[str, Any]],
    interfaces: list[DesignInterface],
    interface_checks: list[dict[str, Any]],
    stage_checks: list[dict[str, Any]],
) -> list[str]:
    warnings: list[str] = []
    duplicate_names = _duplicates([module["name"] for module in modules])
    if duplicate_names:
        warnings.append(f"模块名称重复：{', '.join(duplicate_names)}。分部生成时模块名必须稳定唯一。")

    for module in modules:
        bbox = module["bbox"]
        if bbox is None:
            warnings.append(f"模块 {module['name']} 缺少有效 bbox。")
            continue
        if _bbox_outside(size, bbox):
            warnings.append(f"模块 {module['name']} 的 bbox 超出 BuildPlan size。")
        if module["role"] == "void" and _bbox_volume(bbox) == 0:
            warnings.append(f"void 模块 {module['name']} 体积为 0，无法稳定清空空间。")

    structural = [module for module in modules if module["bbox"] and module["role"] not in {"void", "detail", "lighting", "landscape"}]
    if len(structural) >= 2 and not _has_touching_pair(structural) and not interfaces:
        warnings.append("结构模块之间没有接触/接口声明，分部生成后可能断开。")

    stage_order = _stage_order(modules)
    if "void" in stage_order:
        void_index = stage_order.index("void")
        for later_role in ("facade", "interior", "lighting", "detail"):
            if later_role in stage_order and stage_order.index(later_role) < void_index:
                warnings.append("void/air 清空阶段应早于 facade/interior/lighting/detail，避免清掉后续细节。")
                break

    for check in interface_checks:
        if not check.get("ok"):
            warnings.append(check["message"])
    for check in stage_checks:
        if not check.get("executable"):
            warnings.append(check["message"])
    return warnings


def _interface_dump(interface: DesignInterface) -> dict[str, Any]:
    return interface.model_dump(mode="json")


def _performance_budget_dump(design_spec: DesignSpec) -> dict[str, Any] | None:
    if design_spec.performance_budget is None:
        return None
    return design_spec.performance_budget.model_dump(mode="json")


def _design_blueprint(
    plan: BuildPlan,
    module_report: dict[str, Any],
    materials: dict[str, int],
    warnings: list[str],
) -> dict[str, Any]:
    modules = module_report.get("modules") or []
    interfaces = module_report.get("interfaces") or []
    stages = _blueprint_stages(modules)
    unresolved = list(module_report.get("missing_bbox") or [])
    unresolved.extend(module_report.get("duplicate_names") or [])

    return {
        "present": bool(module_report.get("present")),
        "name": plan.name,
        "size": list(plan.size),
        "building_type": module_report.get("building_type"),
        "scale_intent": module_report.get("scale_intent"),
        "grid": module_report.get("grid") or [],
        "stitch_ready": bool(module_report.get("stitch_ready")),
        "stage_count": len(stages),
        "stages": stages,
        "modules": [_blueprint_module(module) for module in modules],
        "interfaces": [_blueprint_interface(interface) for interface in interfaces],
        "interface_checks": module_report.get("interface_checks") or [],
        "material_schedule": module_report.get("material_schedule") or [],
        "quality_checks": module_report.get("quality_checks") or [],
        "performance_budget": module_report.get("performance_budget"),
        "stage_checks": module_report.get("stage_checks") or [],
        "coverage": module_report.get("coverage") or {},
        "top_materials": list(materials.items())[:12],
        "risks": warnings[:12],
        "unresolved": unresolved,
    }


def _blueprint_stages(modules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stage_order = [
        "foundation",
        "void",
        "mass",
        "structure",
        "circulation",
        "facade",
        "roof",
        "interior",
        "lighting",
        "detail",
        "landscape",
        "services",
        "architecture",
        "entry",
        "unknown",
    ]
    grouped: dict[str, list[dict[str, Any]]] = {}
    for module in modules:
        grouped.setdefault(module.get("role") or "unknown", []).append(module)

    ordered_roles = [role for role in stage_order if role in grouped]
    ordered_roles.extend(sorted(role for role in grouped if role not in stage_order))

    stages: list[dict[str, Any]] = []
    for index, role in enumerate(ordered_roles, start=1):
        items = grouped[role]
        stages.append(
            {
                "index": index,
                "role": role,
                "module_count": len(items),
                "modules": [item["name"] for item in items],
                "bbox": _combined_bbox([item["bbox"] for item in items if item.get("bbox")]),
                "volume": sum(item.get("volume", 0) for item in items),
            }
        )
    return stages


def _stage_checks(modules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stages = _blueprint_stages(modules)
    checks: list[dict[str, Any]] = []
    for stage in stages:
        missing = [
            module["name"]
            for module in modules
            if module.get("role") == stage["role"] and not module.get("bbox")
        ]
        executable = not missing and stage.get("bbox") is not None
        message = (
            f"阶段 {stage['role']} 可按模块 bbox 单独施工。"
            if executable
            else f"阶段 {stage['role']} 有模块缺少 bbox，无法稳定单独清空/粘贴。"
        )
        checks.append(
            {
                "role": stage["role"],
                "module_count": stage["module_count"],
                "modules": stage["modules"],
                "bbox": stage["bbox"],
                "volume": stage["volume"],
                "executable": executable,
                "missing_bbox": missing,
                "message": message,
            }
        )
    return checks


def _blueprint_module(module: dict[str, Any]) -> dict[str, Any]:
    bbox = module.get("bbox")
    return {
        "name": module.get("name"),
        "role": module.get("role"),
        "bbox": bbox,
        "size": _bbox_size(bbox) if bbox else None,
        "volume": module.get("volume", 0),
        "materials": module.get("materials") or [],
        "interfaces": module.get("interfaces") or {},
        "notes": module.get("notes") or [],
    }


def _blueprint_interface(interface: dict[str, Any]) -> dict[str, Any]:
    return {
        "from": interface.get("module_a"),
        "from_face": interface.get("face_a"),
        "to": interface.get("module_b"),
        "to_face": interface.get("face_b"),
        "kind": interface.get("kind"),
        "note": interface.get("note", ""),
    }


def _interface_checks(modules: list[dict[str, Any]], interfaces: list[DesignInterface]) -> list[dict[str, Any]]:
    by_name = {module["name"]: module for module in modules}
    checks: list[dict[str, Any]] = []
    for index, interface in enumerate(interfaces):
        left = by_name.get(interface.module_a)
        right = by_name.get(interface.module_b)
        left_bbox = left.get("bbox") if left else None
        right_bbox = right.get("bbox") if right else None
        status = "ok"
        message = f"接口 {interface.module_a}.{interface.face_a} -> {interface.module_b}.{interface.face_b} 可对齐。"

        if interface.module_a.startswith("legacy_interface_") and interface.module_b.startswith("legacy_interface_"):
            status = "legacy"
            message = "旧版文本接口无法做 bbox 对齐检查。"
        elif left is None or right is None:
            status = "missing_module"
            missing = interface.module_a if left is None else interface.module_b
            message = f"接口 #{index + 1} 引用了不存在的模块 {missing}。"
        elif left_bbox is None or right_bbox is None:
            status = "missing_bbox"
            missing = interface.module_a if left_bbox is None else interface.module_b
            message = f"接口 #{index + 1} 的模块 {missing} 缺少 bbox，无法检查切口。"
        elif not _interface_faces_align(left_bbox, interface.face_a, right_bbox, interface.face_b):
            status = "gap"
            message = f"接口 {interface.module_a}.{interface.face_a} 与 {interface.module_b}.{interface.face_b} 的 bbox 没有按声明面接触或一格重叠。"

        checks.append(
            {
                "index": index + 1,
                "from": interface.module_a,
                "from_face": interface.face_a,
                "to": interface.module_b,
                "to_face": interface.face_b,
                "kind": interface.kind,
                "status": status,
                "ok": status in {"ok", "legacy"},
                "message": message,
            }
        )
    return checks


def _interface_faces_align(
    left_bbox: list[list[int]],
    left_face: str,
    right_bbox: list[list[int]],
    right_face: str,
) -> bool:
    if left_face in {"any", "inside", "outside", "center"} or right_face in {"any", "inside", "outside", "center"}:
        return _bboxes_touch_or_overlap(left_bbox, right_bbox)

    axis_by_face = {
        "west": 0,
        "east": 0,
        "bottom": 1,
        "top": 1,
        "north": 2,
        "south": 2,
    }
    left_axis = axis_by_face.get(left_face)
    right_axis = axis_by_face.get(right_face)
    if left_axis is None or right_axis is None or left_axis != right_axis:
        return _bboxes_touch_or_overlap(left_bbox, right_bbox)

    left_coord = _face_coordinate(left_bbox, left_face)
    right_coord = _face_coordinate(right_bbox, right_face)
    if left_coord is None or right_coord is None or abs(left_coord - right_coord) > 1:
        return False

    other_axes = [axis for axis in (0, 1, 2) if axis != left_axis]
    return all(_ranges_touch_or_overlap(_bbox_axis_range(left_bbox, axis), _bbox_axis_range(right_bbox, axis)) for axis in other_axes)


def _face_coordinate(bbox: list[list[int]], face: str) -> int | None:
    low, high = bbox
    if face in {"west", "bottom", "north"}:
        axis = {"west": 0, "bottom": 1, "north": 2}[face]
        return low[axis]
    if face in {"east", "top", "south"}:
        axis = {"east": 0, "top": 1, "south": 2}[face]
        return high[axis]
    return None


def _bbox_axis_range(bbox: list[list[int]], axis: int) -> tuple[int, int]:
    return bbox[0][axis], bbox[1][axis]


def _ranges_touch_or_overlap(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] <= right[1] + 1 and left[1] + 1 >= right[0]


def _combined_bbox(boxes: list[list[list[int]]]) -> list[list[int]] | None:
    if not boxes:
        return None
    min_x = min(box[0][0] for box in boxes)
    min_y = min(box[0][1] for box in boxes)
    min_z = min(box[0][2] for box in boxes)
    max_x = max(box[1][0] for box in boxes)
    max_y = max(box[1][1] for box in boxes)
    max_z = max(box[1][2] for box in boxes)
    return [[min_x, min_y, min_z], [max_x, max_y, max_z]]


def _bbox_size(bbox: list[list[int]]) -> list[int]:
    (x1, y1, z1), (x2, y2, z2) = bbox
    return [x2 - x1 + 1, y2 - y1 + 1, z2 - z1 + 1]


def _module_coverage(size: tuple[int, int, int], modules: list[dict[str, Any]]) -> dict[str, float]:
    sx, sy, sz = size
    plan_volume = max(1, sx * sy * sz)
    total = sum(module["volume"] for module in modules if module["bbox"])
    void = sum(module["volume"] for module in modules if module["bbox"] and module["role"] == "void")
    return {
        "module_volume_to_plan": round(total / plan_volume, 4),
        "void_volume_to_plan": round(void / plan_volume, 4),
    }


def _stage_order(modules: list[dict[str, Any]]) -> list[str]:
    order: list[str] = []
    for module in modules:
        role = module.get("role", "unknown")
        if role not in order:
            order.append(role)
    return order


def _duplicates(values: list[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def _bbox_volume(bbox: list[list[int]]) -> int:
    (x1, y1, z1), (x2, y2, z2) = bbox
    return max(0, x2 - x1 + 1) * max(0, y2 - y1 + 1) * max(0, z2 - z1 + 1)


def _bbox_outside(size: tuple[int, int, int], bbox: list[list[int]]) -> bool:
    (x1, y1, z1), (x2, y2, z2) = bbox
    sx, sy, sz = size
    return x1 < 0 or y1 < 0 or z1 < 0 or x2 >= sx or y2 >= sy or z2 >= sz


def _has_touching_pair(modules: list[dict[str, Any]]) -> bool:
    for left_index, left in enumerate(modules):
        for right in modules[left_index + 1:]:
            if _bboxes_touch_or_overlap(left["bbox"], right["bbox"]):
                return True
    return False


def _bboxes_touch_or_overlap(a: list[list[int]], b: list[list[int]]) -> bool:
    (ax1, ay1, az1), (ax2, ay2, az2) = a
    (bx1, by1, bz1), (bx2, by2, bz2) = b
    return (
        ax1 <= bx2 + 1
        and ax2 + 1 >= bx1
        and ay1 <= by2 + 1
        and ay2 + 1 >= by1
        and az1 <= bz2 + 1
        and az2 + 1 >= bz1
    )


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


def _has_part_type(plan: BuildPlan, part_type: str) -> bool:
    return any(getattr(part, "type", None) == part_type for part in plan.parts)
