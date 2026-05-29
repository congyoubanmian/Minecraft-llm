from __future__ import annotations

import json
import subprocess
from pathlib import Path

from backend.ai.vision import VisionSummary
from backend.config import ROOT_DIR, settings
from backend.dsl.schema import BuildPlan
from backend.library import get_library_context


def plan_build(summary: VisionSummary, name: str, image_path: Path | None = None) -> BuildPlan:
    if settings.planner_mode.lower() == "static":
        return _static_plan(name)
    return _codex_plan(summary, name, image_path)


def plan_from_conversation(
    *,
    name: str,
    analysis: dict | None,
    messages: list[dict[str, str]],
    current_plan: dict | None = None,
    image_path: Path | None = None,
) -> BuildPlan:
    if settings.planner_mode.lower() == "static":
        return _static_plan(name)

    settings.generated_plan_dir.mkdir(parents=True, exist_ok=True)
    output_path = settings.generated_plan_dir / f"{name}.json"
    prompt = _build_conversation_prompt(
        name=name,
        output_path=output_path,
        analysis=analysis or {},
        messages=messages,
        current_plan=current_plan,
    )

    return _run_codex(prompt, name, output_path, image_path, error_label="Codex conversation planner failed")


def repair_plan_from_diagnostics(
    *,
    name: str,
    analysis: dict | None,
    messages: list[dict[str, str]],
    current_plan: dict,
    diagnostics: dict,
    image_path: Path | None = None,
    attempt: int = 1,
) -> BuildPlan:
    if settings.planner_mode.lower() == "static":
        return BuildPlan.model_validate(current_plan)

    settings.generated_plan_dir.mkdir(parents=True, exist_ok=True)
    output_path = settings.generated_plan_dir / f"{name}.repair{attempt}.json"
    prompt = _build_repair_prompt(
        name=name,
        output_path=output_path,
        analysis=analysis or {},
        messages=messages,
        current_plan=current_plan,
        diagnostics=diagnostics,
    )
    return _run_codex(prompt, name, output_path, image_path, error_label="Codex repair planner failed")


def _codex_plan(summary: VisionSummary, name: str, image_path: Path | None) -> BuildPlan:
    settings.generated_plan_dir.mkdir(parents=True, exist_ok=True)
    output_path = settings.generated_plan_dir / f"{name}.json"
    prompt = _build_codex_prompt(summary, name, output_path)
    return _run_codex(prompt, name, output_path, image_path, error_label="Codex planner failed")


def _run_codex(
    prompt: str,
    name: str,
    output_path: Path,
    image_path: Path | None = None,
    *,
    error_label: str = "Codex planner failed",
) -> BuildPlan:
    command = [
        settings.codex_command,
        "--dangerously-bypass-approvals-and-sandbox",
        "exec",
        "--skip-git-repo-check",
        "-C",
        str(ROOT_DIR),
    ]
    if settings.codex_model:
        command.extend(["--model", settings.codex_model])
    if image_path:
        command.extend(["--image", str(image_path)])
    command.append("-")

    completed = subprocess.run(
        command,
        cwd=ROOT_DIR,
        input=prompt,
        text=True,
        capture_output=True,
        timeout=settings.codex_timeout_seconds,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"{error_label} "
            f"(exit={completed.returncode}): stdout={completed.stdout[-2000:]!r} "
            f"stderr={completed.stderr[-2000:]!r}"
        )

    if not output_path.exists():
        raise FileNotFoundError(f"Codex did not create DSL file: {output_path}")

    data = json.loads(output_path.read_text(encoding="utf-8"))
    data["name"] = name
    return BuildPlan.model_validate(data)


def _build_codex_prompt(summary: VisionSummary, name: str, output_path: Path) -> str:
    library_context = get_library_context()
    return f"""
You are generating a high-detail Minecraft building DSL file for an automated schematic generator.

Write exactly one JSON file at:
{output_path}

Do not modify any other file.

	Use the attached image as the primary source. The vision summary is only a rough hint.
	First reason about the building from multiple dimensions, then encode that reasoning in
	the JSON "analysis" field. The final schematic should be recognizable from the most
	visible facade, not just a generic house.

	Work like an architect before you work like a Minecraft builder:
	1. Create a concise design specification in analysis.design_spec.
	2. Define the selected template, scale intent, structural grid, modules, module
	   bounding boxes, interface faces, material schedule, and quality checks.
	3. Translate that design specification into BuildPlan parts.
	For large or complex buildings, think in modules such as foundation, core mass,
	voids, facade, roof, interior, lighting, and details. All modules must share the
	same local coordinate system so split generation can later be joined without
	cut-face mismatches.

The JSON must match this shape:
{{
  "name": "{name}",
  "size": [x, y, z],
  "origin": [0, 64, 0],
  "palette": {{
    "foundation": "stone_bricks",
    "floor": "spruce_planks",
    "wall": "white_concrete",
    "beam": "dark_oak_log",
    "roof": "dark_oak_stairs",
    "roof_fill": "dark_oak_planks",
    "window": "glass_pane",
    "frame": "dark_oak_planks",
    "sill": "smooth_stone_slab",
    "trim": "polished_andesite",
    "accent": "spruce_trapdoor",
    "door": "dark_oak_door",
    "stair": "stone_brick_stairs",
    "slab": "stone_brick_slab"
	  }},
	  "analysis": {{
	    "viewpoint": "front/three-quarter/side/etc",
	    "selected_template": "template key or custom",
	    "component_strategy": ["why each component is suitable or avoided"],
	    "design_spec": {{
	      "building_type": "template building type",
	      "scale_intent": "target block dimensions and proportions",
	      "grid": ["bay width, floor height, tier height, span, symmetry axis"],
	      "modules": [
	        {{
	          "name": "module id",
	          "role": "foundation/mass/structure/void/facade/roof/interior/lighting/detail/landscape/circulation/services/architecture/entry",
	          "bbox": [[0, 0, 0], [10, 10, 10]],
	          "materials": ["role=palette_key"],
	          "interfaces": {{"top": "expected connection"}},
	          "notes": ["short construction note"]
	        }}
	      ],
	      "interfaces": [
	        {{
	          "module_a": "left_tower",
	          "face_a": "top",
	          "module_b": "skybridge",
	          "face_b": "bottom",
	          "kind": "support",
	          "note": "shared support face or one-block overlap"
	        }}
	      ],
	      "material_schedule": ["role=block with reason"],
	      "quality_checks": ["checks to verify recognizability"],
	      "performance_budget": {{
	        "max_blocks": 120000,
	        "max_preview_blocks": 120000,
	        "max_tick_commands": 0,
	        "animated": false,
	        "suggested_view_distance": 12,
	        "min_server_memory_mb": 2048,
	        "notes": ["prefer static lights unless animation is explicitly requested"]
	      }}
	    }},
	    "massing": ["major volumes and proportions"],
    "facade": ["symmetry, bays, floors, entrances, balconies"],
    "roof": ["shape, pitch, ridges, dormers, parapets"],
    "materials": ["dominant blocks and accent materials"],
    "details": ["trim, columns, windows, railings, steps, overhangs"],
    "assumptions": ["what you inferred where the image was ambiguous"]
  }},
  "parts": []
}}

	Allowed part types include primitive parts and reusable library components.
	Before writing parts, choose the closest library template by style/building type.
	Use that template's recommended palettes, component sequence, avoid_components,
	checks, and scale_guidance as hard planning guidance. Do not reuse a component
	only because it worked in a previous project: ancient buildings, bridges, modern
	office towers, and gate-shaped landmarks need different component families.

Primitive parts:
- box
- roof_gable
- window_grid
- window
- door
- stairs
- slab
- cylinder
- blocks
- octagonal_tower
- octagonal_roof
- octagonal_eave
- vajra_spire
- mini_pagoda_ring
- facade_panel_ring
- twisted_lattice_tower

Reusable component part:
{{
  "type": "component",
  "name": "pagoda_tier",
  "at": [0, 0, 0],
  "scale": 1.0,
  "parameters": {{"radius": 18, "height": 8}},
  "materials": {{"body": "smooth_quartz", "roof": "oxidized_cut_copper"}}
}}

	Use components when the target contains matching reusable structures such as
	pagoda tiers, bridge segments, concrete podiums, small pagoda clusters, or other
	systems listed by the selected template. Components can be stacked, shifted,
	scaled, and material-overridden.

	Component selection rules:
	- For pagodas/temples/ancient Chinese landmarks, prefer pagoda_tier,
	  mini_pagoda_cluster, octagonal_* primitives, timber/stone/roof detail; avoid
	  glass office and concrete podium components unless the prompt asks for fusion.
	- For Jiangnan water-town scenes, prefer low houses, dark roofs, stone_arch_bridge,
	  canal/path details; avoid tall modern towers.
		- For modern glass office landmarks, prefer curtain wall, office floors,
		  structural frame, central void/skybridge when applicable, and repeated lights.
		- For Canton Tower / Guangzhou Tower / Xiaomanyao / TV observation towers,
		  choose twisted_lattice_tower. Keep it very tall and slender, with a narrow
		  waist, rotating diagonal lattice, observation decks, antenna mast, and no
		  pagoda eaves.
		- For bridges, choose stone_arch_bridge for historic arches and
	  suspension_bridge_segment for cable/suspension bridges; do not mix them unless
	  the prompt explicitly asks.
	- If the target proportions differ from a named landmark, adapt the template and
	  component parameters instead of forcing a fixed shape.

	Available material palettes, component blueprints, and architecture templates:
	{json.dumps(library_context, ensure_ascii=False, indent=2)}

Primitive part examples:

1. box
{{
  "type": "box",
  "from": [x1, y1, z1],
  "to": [x2, y2, z2],
  "block": "palette_key_or_minecraft_block",
  "hollow": false
}}

2. roof_gable
{{
  "type": "roof_gable",
  "from": [x1, y1, z1],
  "to": [x2, y2, z2],
  "block": "roof",
  "ridge_axis": "x"
}}

3. window_grid - quick repeated plain glass openings on a wall
{{
  "type": "window_grid",
  "wall": "front",
  "count": 4,
  "y": 4,
  "width": 2,
  "height": 3,
  "block": "window"
}}

4. window - explicit detailed window with frame/sill/shutters
{{
  "type": "window",
  "from": [x1, y1, z1],
  "to": [x2, y2, z2],
  "glass": "window",
  "frame": "frame",
  "sill": "sill",
  "shutter": "accent"
}}

5. door
{{
  "type": "door",
  "wall": "front",
  "width": 2,
  "height": 3,
  "block": "door"
}}

6. stairs - rows of oriented stair blocks for steps, roof lips, cornices, angled trim
{{
  "type": "stairs",
  "from": [x1, y1, z1],
  "to": [x2, y2, z2],
  "block": "stair",
  "facing": "north",
  "half": "bottom",
  "shape": "straight"
}}

7. slab - thin trim, floors, ledges, caps, balconies, paths
{{
  "type": "slab",
  "from": [x1, y1, z1],
  "to": [x2, y2, z2],
  "block": "slab",
  "slab_type": "bottom"
}}

8. cylinder - round/curved towers, columns, chimneys, turrets
{{
  "type": "cylinder",
  "center": [x, y, z],
  "radius": 2,
  "height": 8,
  "block": "wall",
  "hollow": true
}}

9. blocks - precise single-block accents when a box would be too coarse
{{
  "type": "blocks",
  "blocks": [
    {{"pos": [x, y, z], "block": "accent"}}
  ]
}}

10. twisted_lattice_tower - Canton Tower / Xiaomanyao style hyperboloid lattice tower
{{
  "type": "twisted_lattice_tower",
  "center": [48, 4, 48],
  "body_height": 184,
  "antenna_height": 44,
  "base_radius": 26,
  "waist_radius": 10,
  "top_radius": 18,
  "waist_y_ratio": 0.56,
  "z_radius_scale": 0.78,
  "ring_interval": 7,
  "struts": 28,
  "twist_degrees": 140,
  "lattice": "lattice",
  "ring": "ring",
  "glass": "glass",
  "core": "core",
  "light": "night_light"
}}

Rules:
- Return no prose in the file, JSON only.
- Keep the JSON compact. Do not include long narrative text in analysis; use short bullet-like strings.
- Keep size within [16..64, 10..32, 16..64].
- Coordinates are relative to the schematic origin.
- Use non-negative coordinates except roof overhang may start at -2.
- Include a foundation, floor, hollow wall shell, explicit facade details, windows, door, roof, and structural accents.
- Use at least 28 parts for normal buildings and 45+ parts for visually rich buildings.
- Prefer explicit "window" parts over "window_grid" when the facade has visible individual windows.
- Add facade depth: trim bands, recessed/raised central bay, columns, steps, overhangs, balcony rails, sill lines, roof edge details, and material changes.
- For symmetrical facades, keep windows/columns aligned across floors.
- Use "blocks" sparingly for icons, small ornaments, rail posts, lantern-like accents, and roof finials.
- Do not make a flat rectangular box unless the image is actually flat and rectangular.
- If the picture shows only one facade, still give the building shallow side/back volume so it is usable in Minecraft.
- Prefer valid Java Edition block ids, without the "minecraft:" prefix.
	- Use palette keys in parts where possible.
	- Prefer component parts for repeated architectural systems, then add primitive
	  parts for custom details.
	- If a component is not suitable for the selected style, do not use it. Build the
	  needed form from primitives or another better component.
	- Include "selected_template" and "component_strategy" in analysis so later turns
	  can understand why the design used or avoided specific components.
	- Include analysis.design_spec with module bboxes, interfaces, material_schedule,
	  quality_checks, and performance_budget before parts. Treat this as the
	  construction drawing: parts must follow those dimensions.
	- For every important module connection, include a design_spec.interfaces entry
	  using module_a, face_a, module_b, face_b, kind, and note. Interface module
	  names must exactly match design_spec.modules names.
	- The output must pass the existing Pydantic BuildPlan schema in backend/dsl/schema.py.

Vision summary:
{json.dumps(dict(summary), ensure_ascii=False, indent=2)}
""".strip()


def _build_conversation_prompt(
    *,
    name: str,
    output_path: Path,
    analysis: dict,
    messages: list[dict[str, str]],
    current_plan: dict | None,
) -> str:
    library_context = get_library_context()
    return f"""
You are modifying a Minecraft building plan through a multi-turn design chat.

Write exactly one JSON file at:
{output_path}

Do not modify any other file. Return no prose outside that file.

	The JSON must validate against backend/dsl/schema.py. You may use primitive parts
	or reusable component parts. First choose an architecture template from the
	library by style/building type. Prefer components only when they match that
	template's applicability; use primitive parts for custom transitions/details.
		Do not force a modern glass office component into ancient buildings, or a pagoda
		component into bridges/office towers, unless the user explicitly asks for fusion.
		If the user asks for Guangzhou Tower, Canton Tower, 广州塔, or 小蛮腰,
		select twisted_lattice_tower and do not select pagoda_stack.

	Available material palettes, component blueprints, and architecture templates:
	{json.dumps(library_context, ensure_ascii=False, indent=2)}

Component example:
{{
  "type": "component",
  "name": "stone_arch_bridge",
  "at": [0, 0, 0],
  "scale": 1.25,
  "parameters": {{}},
  "materials": {{"stone": "deepslate_bricks", "deck": "smooth_stone"}}
}}

Keep size within [16..96, 10..96, 16..96] unless the user explicitly asks for a
larger landmark. Prefer valid vanilla Java Edition block ids without the
"minecraft:" prefix. Use palette keys in parts where possible.
For Canton Tower / Guangzhou Tower / Xiaomanyao, use a much taller landmark size
such as [72..96, 180..260, 72..96], with height at least 2.5x max(width, depth).

	Important design rules:
	- Treat the image analysis as reference material, not as a finished build.
	- Treat the latest user message as the strongest instruction.
	- Preserve useful details from the current plan unless the user asks to replace them.
	- Output a coherent, buildable Minecraft structure, not a raw coordinate dump.
	- Work in two stages inside analysis: first update analysis.design_spec with
	  building_type, scale_intent, grid, modules, bboxes, interfaces,
	  material_schedule, quality_checks, and performance_budget; then generate
	  parts from that design spec.
	- For complex or large projects, split conceptually by modules but keep one
	  final BuildPlan JSON. Every module must share the same coordinates and exact
	  interface faces so future split-LLM generation can be stitched safely.
	- For every important module connection, include a design_spec.interfaces entry
	  using module_a, face_a, module_b, face_b, kind, and note. Interface module
	  names must exactly match design_spec.modules names.
	- If the previous plan used a too-specific component family, switch templates and
	  explain that in analysis.changes.
	- Use enough explicit parts for recognizable massing, facade, roof, entrances,
  windows, trim, columns, steps, and ornaments.
- Do not use more than 4096 entries in any single "blocks" part.
- Include/update "analysis" with short structured notes about what changed.

Required output shape:
{{
  "name": "{name}",
  "size": [x, y, z],
  "origin": [0, 64, 0],
	  "palette": {{}},
	  "analysis": {{
	    "source": "image/text/current_plan",
	    "selected_template": "template key or custom",
	    "component_strategy": [],
	    "design_spec": {{
	      "building_type": "template building type",
	      "scale_intent": "target block dimensions and proportions",
	      "grid": [],
	      "modules": [],
	      "interfaces": [],
	      "material_schedule": [],
	      "quality_checks": [],
	      "performance_budget": {{
	        "max_blocks": 120000,
	        "max_preview_blocks": 120000,
	        "max_tick_commands": 0,
	        "animated": false,
	        "suggested_view_distance": 12,
	        "min_server_memory_mb": 2048,
	        "notes": []
	      }}
	    }},
	    "intent": [],
    "massing": [],
    "facade": [],
    "roof": [],
    "materials": [],
    "changes": []
  }},
  "parts": []
}}

Image/vision analysis:
{json.dumps(analysis, ensure_ascii=False, indent=2)}

Conversation messages:
{json.dumps(messages, ensure_ascii=False, indent=2)}

Current plan, if any:
{json.dumps(current_plan or {}, ensure_ascii=False, indent=2)}
""".strip()


def _build_repair_prompt(
    *,
    name: str,
    output_path: Path,
    analysis: dict,
    messages: list[dict[str, str]],
    current_plan: dict,
    diagnostics: dict,
) -> str:
    library_context = get_library_context()
    severe_warnings = diagnostics.get("warnings", [])
    return f"""
You are repairing a Minecraft BuildPlan JSON after automatic diagnostics.

Write exactly one complete replacement JSON file at:
{output_path}

Do not modify any other file. Return no prose outside that file.

Repair objective:
- Keep the same project name: {name}
- Preserve the user's latest intent and the useful parts of the current plan.
- Fix every relevant diagnostic warning, especially template mismatch, bad
  proportions, missing module bboxes, broken interfaces, missing lighting, overly
  high glass ratio for ancient buildings, or performance budget violations.
- Update analysis.design_spec first, then update parts so they match the repaired
  design_spec. Do not leave analysis claiming a design that parts do not implement.
- If a warning is intentionally not fixable in Minecraft, add a short note in
  analysis.assumptions and keep performance_budget conservative.

Hard requirements:
- The output must validate against backend/dsl/schema.py.
- Include analysis.selected_template, analysis.component_strategy, and
  analysis.design_spec with modules, interfaces, material_schedule,
  quality_checks, and performance_budget.
- Keep every module bbox inside BuildPlan size.
- Do not use more than 4096 entries in any single blocks part.
- Prefer reusable components only when they match the selected template.
- Prefer static lighting unless the user explicitly asked for animation.
- Use valid vanilla Java Edition block ids without the minecraft: prefix, or use
  palette keys that resolve to valid block ids.

Available material palettes, component blueprints, and architecture templates:
{json.dumps(library_context, ensure_ascii=False, indent=2)}

Diagnostics to fix:
{json.dumps(severe_warnings, ensure_ascii=False, indent=2)}

Full diagnostics:
{json.dumps(diagnostics, ensure_ascii=False, indent=2)}

Image/vision analysis:
{json.dumps(analysis, ensure_ascii=False, indent=2)}

Conversation messages:
{json.dumps(messages, ensure_ascii=False, indent=2)}

Current plan to repair:
{json.dumps(current_plan, ensure_ascii=False, indent=2)}
""".strip()


def _static_plan(name: str) -> BuildPlan:
    """
    Deterministic fallback planner.

    Use PLANNER_MODE=static when Codex CLI is unavailable or when a predictable
    test build is needed.
    """
    return BuildPlan.model_validate(
        {
            "name": name,
            "size": [28, 16, 22],
            "origin": [0, 64, 0],
            "palette": {
                "foundation": "stone_bricks",
                "floor": "spruce_planks",
                "wall": "white_concrete",
                "beam": "dark_oak_log",
                "roof": "dark_oak_stairs",
                "roof_fill": "dark_oak_planks",
                "window": "glass_pane",
                "door": "dark_oak_door",
            },
            "parts": [
                {
                    "type": "box",
                    "from": [0, 0, 0],
                    "to": [27, 0, 21],
                    "block": "foundation",
                },
                {
                    "type": "box",
                    "from": [1, 1, 1],
                    "to": [26, 1, 20],
                    "block": "floor",
                },
                {
                    "type": "box",
                    "from": [1, 2, 1],
                    "to": [26, 8, 20],
                    "block": "wall",
                    "hollow": True,
                },
                {
                    "type": "box",
                    "from": [0, 2, 0],
                    "to": [0, 9, 0],
                    "block": "beam",
                },
                {
                    "type": "box",
                    "from": [27, 2, 0],
                    "to": [27, 9, 0],
                    "block": "beam",
                },
                {
                    "type": "box",
                    "from": [0, 2, 21],
                    "to": [0, 9, 21],
                    "block": "beam",
                },
                {
                    "type": "box",
                    "from": [27, 2, 21],
                    "to": [27, 9, 21],
                    "block": "beam",
                },
                {
                    "type": "window_grid",
                    "wall": "front",
                    "count": 4,
                    "y": 4,
                    "width": 2,
                    "height": 3,
                    "block": "window",
                },
                {
                    "type": "window_grid",
                    "wall": "back",
                    "count": 4,
                    "y": 4,
                    "width": 2,
                    "height": 3,
                    "block": "window",
                },
                {
                    "type": "door",
                    "wall": "front",
                    "width": 2,
                    "height": 3,
                    "block": "door",
                },
                {
                    "type": "roof_gable",
                    "from": [-2, 9, -2],
                    "to": [29, 15, 23],
                    "block": "roof",
                    "ridge_axis": "x",
                },
            ],
        }
    )
