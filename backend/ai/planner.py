from __future__ import annotations

import json
import subprocess
from pathlib import Path

from backend.ai.vision import VisionSummary
from backend.config import ROOT_DIR, settings
from backend.dsl.schema import BuildPlan


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
            "Codex conversation planner failed "
            f"(exit={completed.returncode}): stdout={completed.stdout[-2000:]!r} "
            f"stderr={completed.stderr[-2000:]!r}"
        )

    if not output_path.exists():
        raise FileNotFoundError(f"Codex did not create DSL file: {output_path}")

    data = json.loads(output_path.read_text(encoding="utf-8"))
    data["name"] = name
    return BuildPlan.model_validate(data)


def _codex_plan(summary: VisionSummary, name: str, image_path: Path | None) -> BuildPlan:
    settings.generated_plan_dir.mkdir(parents=True, exist_ok=True)
    output_path = settings.generated_plan_dir / f"{name}.json"
    prompt = _build_codex_prompt(summary, name, output_path)

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
            "Codex planner failed "
            f"(exit={completed.returncode}): stdout={completed.stdout[-2000:]!r} "
            f"stderr={completed.stderr[-2000:]!r}"
        )

    if not output_path.exists():
        raise FileNotFoundError(f"Codex did not create DSL file: {output_path}")

    data = json.loads(output_path.read_text(encoding="utf-8"))
    data["name"] = name
    return BuildPlan.model_validate(data)


def _build_codex_prompt(summary: VisionSummary, name: str, output_path: Path) -> str:
    return f"""
You are generating a high-detail Minecraft building DSL file for an automated schematic generator.

Write exactly one JSON file at:
{output_path}

Do not modify any other file.

Use the attached image as the primary source. The vision summary is only a rough hint.
First reason about the building from multiple dimensions, then encode that reasoning in
the JSON "analysis" field. The final schematic should be recognizable from the most
visible facade, not just a generic house.

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
    "massing": ["major volumes and proportions"],
    "facade": ["symmetry, bays, floors, entrances, balconies"],
    "roof": ["shape, pitch, ridges, dormers, parapets"],
    "materials": ["dominant blocks and accent materials"],
    "details": ["trim, columns, windows, railings, steps, overhangs"],
    "assumptions": ["what you inferred where the image was ambiguous"]
  }},
  "parts": []
}}

Allowed part types:

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
    return f"""
You are modifying a Minecraft building plan through a multi-turn design chat.

Write exactly one JSON file at:
{output_path}

Do not modify any other file. Return no prose outside that file.

The JSON must validate against backend/dsl/schema.py and use the same part types
as the existing image-to-DSL planner:
- box
- roof_gable
- window_grid
- window
- door
- stairs
- slab
- cylinder
- blocks

Keep size within [16..96, 10..96, 16..96] unless the user explicitly asks for a
larger landmark. Prefer valid vanilla Java Edition block ids without the
"minecraft:" prefix. Use palette keys in parts where possible.

Important design rules:
- Treat the image analysis as reference material, not as a finished build.
- Treat the latest user message as the strongest instruction.
- Preserve useful details from the current plan unless the user asks to replace them.
- Output a coherent, buildable Minecraft structure, not a raw coordinate dump.
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
