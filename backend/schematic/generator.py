from __future__ import annotations

from pathlib import Path
import math
from typing import Any

from backend.blocks import BlockList
from backend.dsl.schema import (
    BlocksPart,
    BuildPlan,
    BoxPart,
    ComponentPart,
    CylinderPart,
    DoorPart,
    GableRoofPart,
    FacadePanelRingPart,
    MiniPagodaRingPart,
    OctagonalEavePart,
    OctagonalRoofPart,
    OctagonalTowerPart,
    SlabPart,
    StairPart,
    VajraSpirePart,
    WindowGridPart,
    WindowPart,
)
from backend.library import get_component


def generate_outputs(
    plan: BuildPlan,
    schematic_dir: Path,
    preview_dir: Path,
    max_preview_blocks: int = 120_000,
    blocks: BlockList | None = None,
) -> tuple[Path, Path, Path]:
    blocks = blocks or render_plan_to_blocks(plan)
    schematic_path = blocks.write_schematic(schematic_dir, plan.name)
    preview_path = blocks.write_preview(
        output_dir=preview_dir,
        name=plan.name,
        size=plan.size,
        origin=plan.origin,
        palette=_preview_palette(plan),
        max_blocks=max_preview_blocks,
    )
    material_path = blocks.write_material_report(preview_dir, plan.name)
    return schematic_path, preview_path, material_path


def generate_schematic(plan: BuildPlan, output_dir: Path) -> Path:
    return render_plan_to_blocks(plan).write_schematic(output_dir, plan.name)


def generate_preview(plan: BuildPlan, output_dir: Path, max_blocks: int = 120_000) -> Path:
    return render_plan_to_blocks(plan).write_preview(
        output_dir=output_dir,
        name=plan.name,
        size=plan.size,
        origin=plan.origin,
        palette=_preview_palette(plan),
        max_blocks=max_blocks,
    )


def generate_material_report(plan: BuildPlan, output_dir: Path) -> Path:
    return render_plan_to_blocks(plan).write_material_report(output_dir, plan.name)


def render_plan_to_blocks(plan: BuildPlan) -> BlockList:
    blocks = BlockList()
    _render_plan(blocks, plan)
    return blocks


def _render_plan(target: Any, plan: BuildPlan) -> None:
    _render_plan_parts(target, plan, list(plan.parts))


def _set(target: Any, pos: tuple[int, int, int], block: str) -> None:
    target.setBlock(pos, block)


def _base_block(block: str) -> str:
    base = block.split("[", 1)[0]
    return base.removeprefix("minecraft:")


def _preview_palette(plan: BuildPlan) -> dict[str, str]:
    palette: dict[str, str] = {}
    for value in plan.palette.values():
        block = _base_block(plan.block_id(value))
        palette[block] = _block_color(block)
    return palette


def _block_color(block: str) -> str:
    block = _base_block(block)
    exact = {
        "air": "#000000",
        "glass": "#9bd7e8",
        "glass_pane": "#9bd7e8",
        "white_stained_glass": "#d8eef4",
        "white_stained_glass_pane": "#d8eef4",
        "lantern": "#f0b94d",
        "soul_lantern": "#53b9c8",
    }
    if block in exact:
        return exact[block]

    rules = [
        ("dark_oak", "#3f2a1a"),
        ("spruce", "#6b4728"),
        ("oak", "#a87946"),
        ("birch", "#d7c99b"),
        ("mangrove", "#8a3a34"),
        ("cherry", "#d79aaa"),
        ("stone_brick", "#777b7d"),
        ("stone", "#85898b"),
        ("andesite", "#8b8f8f"),
        ("diorite", "#c7c7c1"),
        ("granite", "#9b6a5b"),
        ("deepslate", "#3d4248"),
        ("blackstone", "#25262b"),
        ("brick", "#9b4635"),
        ("sandstone", "#d7c083"),
        ("red_sandstone", "#b86d45"),
        ("quartz", "#d9d4c6"),
        ("concrete", "#d6d6d6"),
        ("terracotta", "#a86045"),
        ("copper", "#b87351"),
        ("prismarine", "#4f908b"),
        ("warped", "#2c7773"),
        ("crimson", "#79364f"),
        ("gold", "#d6a737"),
        ("iron", "#c5c7c8"),
        ("red", "#9f3030"),
        ("blue", "#345f9f"),
        ("green", "#4d7a3a"),
        ("black", "#1f2328"),
        ("white", "#e8e4d8"),
    ]
    for needle, color in rules:
        if needle in block:
            return color
    return "#9b9f94"


def _range(a: int, b: int) -> range:
    return range(min(a, b), max(a, b) + 1)


def _box(schem: Any, plan: BuildPlan, part: BoxPart) -> None:
    x1, y1, z1 = part.from_pos
    x2, y2, z2 = part.to
    block = plan.block_id(part.block)

    for x in _range(x1, x2):
        for y in _range(y1, y2):
            for z in _range(z1, z2):
                if part.hollow and x not in (x1, x2) and y not in (y1, y2) and z not in (z1, z2):
                    continue
                _set(schem, (x, y, z), block)


def _fill(
    schem: Any,
    plan: BuildPlan,
    from_pos: tuple[int, int, int],
    to_pos: tuple[int, int, int],
    block: str,
) -> None:
    resolved = plan.block_id(block)
    x1, y1, z1 = from_pos
    x2, y2, z2 = to_pos
    for x in _range(x1, x2):
        for y in _range(y1, y2):
            for z in _range(z1, z2):
                _set(schem, (x, y, z), resolved)


def _gable_roof(schem: Any, plan: BuildPlan, part: GableRoofPart) -> None:
    x1, y1, z1 = part.from_pos
    x2, y2, z2 = part.to
    block = plan.block_id(part.block)
    fill = plan.block_id("roof_fill")

    if part.ridge_axis == "x":
        width = z2 - z1
        layers = width // 2 + 1
        for layer in range(layers):
            z_left = z1 + layer
            z_right = z2 - layer
            y = y1 + layer
            for x in _range(x1, x2):
                _set(schem, (x, y, z_left), block)
                _set(schem, (x, y, z_right), block)
            for z in _range(z_left + 1, z_right - 1):
                _set(schem, (x1, y, z), fill)
                _set(schem, (x2, y, z), fill)
    else:
        width = x2 - x1
        layers = width // 2 + 1
        for layer in range(layers):
            x_left = x1 + layer
            x_right = x2 - layer
            y = y1 + layer
            for z in _range(z1, z2):
                _set(schem, (x_left, y, z), block)
                _set(schem, (x_right, y, z), block)
            for x in _range(x_left + 1, x_right - 1):
                _set(schem, (x, y, z1), fill)
                _set(schem, (x, y, z2), fill)


def _window_grid(schem: Any, plan: BuildPlan, part: WindowGridPart) -> None:
    block = plan.block_id(part.block)
    sx, _, sz = plan.size
    y1 = part.y
    y2 = part.y + part.height - 1

    horizontal_span = sx if part.wall in ("front", "back") else sz
    spacing = max(2, horizontal_span // (part.count + 1))

    for idx in range(1, part.count + 1):
        center = spacing * idx
        start = center - part.width // 2
        for offset in range(part.width):
            coord = start + offset
            for y in _range(y1, y2):
                if part.wall == "front":
                    _set(schem, (coord, y, 0), block)
                elif part.wall == "back":
                    _set(schem, (coord, y, sz - 1), block)
                elif part.wall == "left":
                    _set(schem, (0, y, coord), block)
                else:
                    _set(schem, (sx - 1, y, coord), block)


def _window(schem: Any, plan: BuildPlan, part: WindowPart) -> None:
    x1, y1, z1 = part.from_pos
    x2, y2, z2 = part.to
    glass = plan.block_id(part.glass)

    for x in _range(x1, x2):
        for y in _range(y1, y2):
            for z in _range(z1, z2):
                _set(schem, (x, y, z), glass)

    if part.frame:
        frame = plan.block_id(part.frame)
        for x in _range(x1 - 1, x2 + 1):
            for z in _range(z1 - 1, z2 + 1):
                _set(schem, (x, y1 - 1, z), frame)
                _set(schem, (x, y2 + 1, z), frame)
        for y in _range(y1 - 1, y2 + 1):
            for z in _range(z1 - 1, z2 + 1):
                _set(schem, (x1 - 1, y, z), frame)
                _set(schem, (x2 + 1, y, z), frame)
            for x in _range(x1 - 1, x2 + 1):
                _set(schem, (x, y, z1 - 1), frame)
                _set(schem, (x, y, z2 + 1), frame)

    if part.sill:
        _fill(schem, plan, (x1 - 1, y1 - 1, z1 - 1), (x2 + 1, y1 - 1, z2 + 1), part.sill)

    if part.shutter:
        shutter = plan.block_id(part.shutter)
        if z1 == z2:
            for y in _range(y1, y2):
                _set(schem, (x1 - 2, y, z1), shutter)
                _set(schem, (x2 + 2, y, z1), shutter)
        elif x1 == x2:
            for y in _range(y1, y2):
                _set(schem, (x1, y, z1 - 2), shutter)
                _set(schem, (x1, y, z2 + 2), shutter)


def _door(schem: Any, plan: BuildPlan, part: DoorPart) -> None:
    sx, _, sz = plan.size
    block = plan.block_id(part.block)
    x = part.x if part.x is not None else sx // 2 - part.width // 2
    z = part.z if part.z is not None else sz // 2 - part.width // 2

    for w in range(part.width):
        for y in range(2, 2 + part.height):
            if part.wall == "front":
                _set(schem, (x + w, y, 0), block)
            elif part.wall == "back":
                _set(schem, (x + w, y, sz - 1), block)
            elif part.wall == "left":
                _set(schem, (0, y, z + w), block)
            else:
                _set(schem, (sx - 1, y, z + w), block)


def _stairs(schem: Any, plan: BuildPlan, part: StairPart) -> None:
    base = plan.block_id(part.block)
    block = f"{base}[facing={part.facing},half={part.half},shape={part.shape},waterlogged=false]"
    _fill(schem, plan, part.from_pos, part.to, block)


def _slab(schem: Any, plan: BuildPlan, part: SlabPart) -> None:
    base = plan.block_id(part.block)
    block = f"{base}[type={part.slab_type},waterlogged=false]"
    _fill(schem, plan, part.from_pos, part.to, block)


def _cylinder(schem: Any, plan: BuildPlan, part: CylinderPart) -> None:
    cx, y1, cz = part.center
    block = plan.block_id(part.block)
    radius_sq = part.radius * part.radius
    inner_sq = max(0, part.radius - 1) * max(0, part.radius - 1)
    for y in range(y1, y1 + part.height):
        for x in range(cx - part.radius, cx + part.radius + 1):
            for z in range(cz - part.radius, cz + part.radius + 1):
                dist_sq = (x - cx) * (x - cx) + (z - cz) * (z - cz)
                if dist_sq > radius_sq:
                    continue
                if part.hollow and dist_sq < inner_sq:
                    continue
                _set(schem, (x, y, z), block)


def _oct_limit(radius: int) -> int:
    return radius + max(2, int(radius * 0.42))


def _inside_octagon(dx: int, dz: int, radius: int) -> bool:
    return abs(dx) <= radius and abs(dz) <= radius and abs(dx) + abs(dz) <= _oct_limit(radius)


def _octagonal_tower(schem: Any, plan: BuildPlan, part: OctagonalTowerPart) -> None:
    cx, y1, cz = part.center
    block = plan.block_id(part.block)
    floor_block = plan.block_id(part.floor_block) if part.floor_block else block
    trim_block = plan.block_id(part.trim_block) if part.trim_block else None
    inner = max(0, part.radius - part.thickness)
    y2 = y1 + part.height - 1

    for y in range(y1, y2 + 1):
        is_floor = part.floor_interval > 0 and (y - y1) % part.floor_interval == 0
        for x in range(cx - part.radius, cx + part.radius + 1):
            for z in range(cz - part.radius, cz + part.radius + 1):
                dx, dz = x - cx, z - cz
                if not _inside_octagon(dx, dz, part.radius):
                    continue
                if is_floor and _inside_octagon(dx, dz, max(0, part.radius - 2)):
                    _set(schem, (x, y, z), floor_block)
                    continue
                if part.hollow and _inside_octagon(dx, dz, inner):
                    continue
                _set(schem, (x, y, z), block)

        if trim_block and (y == y1 or y == y2 or (part.floor_interval > 0 and (y - y1) % part.floor_interval == part.floor_interval - 1)):
            _octagonal_ring(schem, plan, cx, y, cz, part.radius + 1, part.radius - 1, trim_block)


def _octagonal_roof(schem: Any, plan: BuildPlan, part: OctagonalRoofPart) -> None:
    cx, y1, cz = part.center
    block = plan.block_id(part.block)
    fill = plan.block_id(part.fill) if part.fill else block
    cap = plan.block_id(part.cap) if part.cap else block

    for layer in range(part.layers):
        radius = max(1, part.radius - layer)
        y = y1 + layer
        edge_inner = max(0, radius - 2)
        _octagonal_ring(schem, plan, cx, y, cz, radius, edge_inner, block)
        if fill and radius > 3:
            _octagonal_fill(schem, plan, cx, y, cz, radius - 2, fill)

    _octagonal_fill(schem, plan, cx, y1 + part.layers, cz, max(1, part.radius - part.layers), cap)


def _octagonal_eave(schem: Any, plan: BuildPlan, part: OctagonalEavePart) -> None:
    cx, y1, cz = part.center
    roof = plan.block_id(part.block)
    underside = plan.block_id(part.underside) if part.underside else roof
    corner = plan.block_id(part.corner_block) if part.corner_block else roof
    outer = part.radius + part.overhang
    inner = max(0, part.radius - 1)

    for layer in range(part.thickness):
        y = y1 + layer
        radius = outer - layer
        _octagonal_ring(schem, plan, cx, y, cz, radius, inner - layer, roof)
        if layer == 0 and underside:
            _octagonal_ring(schem, plan, cx, y - 1, cz, max(inner + 1, radius - 2), max(0, inner - 2), underside)

    tip_radius = max(1, outer - 1)
    for dx, dz in _octagonal_points(tip_radius):
        _set(schem, (cx + dx, y1 + part.thickness, cz + dz), corner)
        _set(schem, (cx + dx, y1 + part.thickness + 1, cz + dz), corner)

    if part.lantern:
        lantern = plan.block_id(part.lantern)
        for dx, dz in _octagonal_points(max(1, outer - 2))[::2]:
            _set(schem, (cx + dx, y1 - 2, cz + dz), lantern)


def _vajra_spire(schem: Any, plan: BuildPlan, part: VajraSpirePart) -> None:
    cx, y1, cz = part.center
    block = plan.block_id(part.block)
    accent = plan.block_id(part.accent) if part.accent else block
    base = part.base_radius

    _octagonal_fill(schem, plan, cx, y1, cz, base, block)
    _octagonal_fill(schem, plan, cx, y1 + 1, cz, max(1, base - 1), block)
    for dx, dz in [(base - 2, base - 2), (-(base - 2), base - 2), (base - 2, -(base - 2)), (-(base - 2), -(base - 2))]:
        _small_spire(schem, plan, cx + dx, y1 + 2, cz + dz, max(1, base // 4), max(5, part.height // 3), block, accent)

    current_y = y1 + 2
    tiers = [
        (max(2, base - 3), 2),
        (max(2, base - 5), 2),
        (max(1, base - 7), 3),
        (max(1, base - 9), 4),
    ]
    for radius, height in tiers:
        for offset in range(height):
            _octagonal_fill(schem, plan, cx, current_y + offset, cz, radius, block)
        _octagonal_ring(schem, plan, cx, current_y + height, cz, radius + 1, max(0, radius - 1), accent)
        current_y += height + 1

    needle_top = y1 + part.height - 1
    for y in range(current_y, needle_top + 1):
        radius = 2 if y < needle_top - 5 else 1
        _octagonal_fill(schem, plan, cx, y, cz, radius, block)
    _set(schem, (cx, needle_top + 1, cz), accent)


def _mini_pagoda_ring(schem: Any, plan: BuildPlan, part: MiniPagodaRingPart) -> None:
    cx, y1, cz = part.center
    for index in range(part.count):
        angle = math.tau * index / part.count
        px = cx + round(math.cos(angle) * part.ring_radius)
        pz = cz + round(math.sin(angle) * part.ring_radius)
        _small_spire(
            schem,
            plan,
            px,
            y1,
            pz,
            part.pagoda_radius,
            part.height,
            plan.block_id(part.block),
            plan.block_id(part.roof),
            plan.block_id(part.accent) if part.accent else None,
        )


def _facade_panel_ring(schem: Any, plan: BuildPlan, part: FacadePanelRingPart) -> None:
    cx, _, cz = part.center
    glass = plan.block_id(part.glass)
    frame = plan.block_id(part.frame)
    plaque = plan.block_id(part.plaque) if part.plaque else None
    half = part.width // 2
    y1 = part.y
    y2 = part.y + part.height - 1

    for dx, dz in _octagonal_points(part.radius):
        if abs(dz) >= abs(dx):
            z = cz + dz
            for x in range(cx - half, cx + half + 1):
                for y in range(y1, y2 + 1):
                    _set(schem, (x, y, z), glass)
            _fill(schem, plan, (cx - half - 1, y1 - 1, z), (cx + half + 1, y1 - 1, z), frame)
            _fill(schem, plan, (cx - half - 1, y2 + 1, z), (cx + half + 1, y2 + 1, z), frame)
            _fill(schem, plan, (cx - half - 1, y1 - 1, z), (cx - half - 1, y2 + 1, z), frame)
            _fill(schem, plan, (cx + half + 1, y1 - 1, z), (cx + half + 1, y2 + 1, z), frame)
            if plaque:
                _set(schem, (cx, y2 + 2, z), plaque)
        else:
            x = cx + dx
            for z in range(cz - half, cz + half + 1):
                for y in range(y1, y2 + 1):
                    _set(schem, (x, y, z), glass)
            _fill(schem, plan, (x, y1 - 1, cz - half - 1), (x, y1 - 1, cz + half + 1), frame)
            _fill(schem, plan, (x, y2 + 1, cz - half - 1), (x, y2 + 1, cz + half + 1), frame)
            _fill(schem, plan, (x, y1 - 1, cz - half - 1), (x, y2 + 1, cz - half - 1), frame)
            _fill(schem, plan, (x, y1 - 1, cz + half + 1), (x, y2 + 1, cz + half + 1), frame)
            if plaque:
                _set(schem, (x, y2 + 2, cz), plaque)


def _component(schem: Any, plan: BuildPlan, part: ComponentPart) -> None:
    component = get_component(part.name)
    parameters = dict(component.get("parameters", {}))
    parameters.update(part.parameters)
    materials = dict(component.get("default_materials", {}))
    materials.update(part.materials)
    scale = part.scale
    ax, ay, az = part.at

    for raw_part in component.get("parts", []):
        expanded = _expand_component_value(raw_part, parameters, materials, scale, (ax, ay, az))
        nested = _component_part_model(expanded)
        _render_plan_parts(schem, plan, [nested])


def _render_plan_parts(target: Any, plan: BuildPlan, parts: list[Any]) -> None:
    for part in parts:
        if isinstance(part, BoxPart):
            _box(target, plan, part)
        elif isinstance(part, GableRoofPart):
            _gable_roof(target, plan, part)
        elif isinstance(part, WindowGridPart):
            _window_grid(target, plan, part)
        elif isinstance(part, WindowPart):
            _window(target, plan, part)
        elif isinstance(part, DoorPart):
            _door(target, plan, part)
        elif isinstance(part, StairPart):
            _stairs(target, plan, part)
        elif isinstance(part, SlabPart):
            _slab(target, plan, part)
        elif isinstance(part, CylinderPart):
            _cylinder(target, plan, part)
        elif isinstance(part, OctagonalTowerPart):
            _octagonal_tower(target, plan, part)
        elif isinstance(part, OctagonalRoofPart):
            _octagonal_roof(target, plan, part)
        elif isinstance(part, OctagonalEavePart):
            _octagonal_eave(target, plan, part)
        elif isinstance(part, VajraSpirePart):
            _vajra_spire(target, plan, part)
        elif isinstance(part, MiniPagodaRingPart):
            _mini_pagoda_ring(target, plan, part)
        elif isinstance(part, FacadePanelRingPart):
            _facade_panel_ring(target, plan, part)
        elif isinstance(part, ComponentPart):
            _component(target, plan, part)
        elif isinstance(part, BlocksPart):
            _blocks(target, plan, part)
        else:
            raise ValueError(f"unsupported component part: {part}")


def _component_part_model(data: dict[str, Any]) -> Any:
    part_type = data.get("type")
    models = {
        "box": BoxPart,
        "roof_gable": GableRoofPart,
        "window_grid": WindowGridPart,
        "window": WindowPart,
        "door": DoorPart,
        "stairs": StairPart,
        "slab": SlabPart,
        "cylinder": CylinderPart,
        "octagonal_tower": OctagonalTowerPart,
        "octagonal_roof": OctagonalRoofPart,
        "octagonal_eave": OctagonalEavePart,
        "vajra_spire": VajraSpirePart,
        "mini_pagoda_ring": MiniPagodaRingPart,
        "facade_panel_ring": FacadePanelRingPart,
        "component": ComponentPart,
        "blocks": BlocksPart,
    }
    if part_type not in models:
        raise ValueError(f"unsupported component part type: {part_type}")
    return models[part_type].model_validate(data)


def _expand_component_value(value: Any, parameters: dict[str, Any], materials: dict[str, str], scale: float, offset: tuple[int, int, int]) -> Any:
    if isinstance(value, str):
        if value.startswith("$"):
            key = value[1:]
            return parameters.get(key, value)
        return materials.get(value, value)
    if isinstance(value, list):
        expanded = [_expand_component_value(item, parameters, materials, scale, offset) for item in value]
        if len(expanded) == 3 and all(isinstance(item, (int, float)) for item in expanded):
            return _scale_pos(expanded, scale, offset)
        return expanded
    if isinstance(value, dict):
        return {key: _expand_component_value(item, parameters, materials, scale, offset) for key, item in value.items()}
    if isinstance(value, (int, float)) and scale != 1.0:
        return max(1, round(value * scale))
    return value


def _scale_pos(pos: list[int | float], scale: float, offset: tuple[int, int, int]) -> list[int]:
    return [round(pos[0] * scale) + offset[0], round(pos[1] * scale) + offset[1], round(pos[2] * scale) + offset[2]]


def _small_spire(
    schem: Any,
    plan: BuildPlan,
    cx: int,
    y1: int,
    cz: int,
    radius: int,
    height: int,
    body_block: str,
    roof_block: str,
    accent_block: str | None = None,
) -> None:
    body_height = max(2, height // 2)
    for y in range(y1, y1 + body_height):
        _octagonal_fill(schem, plan, cx, y, cz, radius, body_block)
    _octagonal_ring(schem, plan, cx, y1 + body_height, cz, radius + 1, max(0, radius - 1), roof_block)
    for y in range(y1 + body_height + 1, y1 + height):
        r = max(1, radius - (y - y1 - body_height))
        _octagonal_fill(schem, plan, cx, y, cz, r, roof_block)
    _set(schem, (cx, y1 + height, cz), accent_block or roof_block)


def _octagonal_fill(
    schem: Any,
    plan: BuildPlan,
    cx: int,
    y: int,
    cz: int,
    radius: int,
    block: str,
) -> None:
    for x in range(cx - radius, cx + radius + 1):
        for z in range(cz - radius, cz + radius + 1):
            if _inside_octagon(x - cx, z - cz, radius):
                _set(schem, (x, y, z), block)


def _octagonal_ring(
    schem: Any,
    plan: BuildPlan,
    cx: int,
    y: int,
    cz: int,
    outer: int,
    inner: int,
    block: str,
) -> None:
    for x in range(cx - outer, cx + outer + 1):
        for z in range(cz - outer, cz + outer + 1):
            dx, dz = x - cx, z - cz
            if _inside_octagon(dx, dz, outer) and not _inside_octagon(dx, dz, max(0, inner)):
                _set(schem, (x, y, z), block)


def _octagonal_points(radius: int) -> list[tuple[int, int]]:
    cut = max(2, int(radius * 0.42))
    return [
        (-cut, -radius),
        (cut, -radius),
        (radius, -cut),
        (radius, cut),
        (cut, radius),
        (-cut, radius),
        (-radius, cut),
        (-radius, -cut),
    ]


def _blocks(schem: Any, plan: BuildPlan, part: BlocksPart) -> None:
    for placement in part.blocks:
        _set(schem, placement.pos, plan.block_id(placement.block))
