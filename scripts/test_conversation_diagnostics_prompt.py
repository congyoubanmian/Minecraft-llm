from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.ai.planner import _build_conversation_prompt, _conversation_diagnostic_context


def main() -> None:
    diagnostics = {
        "template_guess": "modern_glass_gate",
        "warnings": ["接口 left_tower.east 与 skybridge.west 的 bbox 没有按声明面接触或一格重叠。"],
        "material_ratios": {"glass": 0.18, "light": 0.001},
        "design_spec": {
            "present": True,
            "stitch_ready": False,
            "module_count": 3,
            "missing_bbox": [],
            "duplicate_names": [],
            "coverage": {"module_volume_to_plan": 0.35},
        },
        "design_blueprint": {
            "interface_checks": [
                {
                    "ok": False,
                    "from": "left_tower",
                    "from_face": "east",
                    "to": "skybridge",
                    "to_face": "west",
                    "status": "gap",
                    "message": "bbox 没有按声明面接触或一格重叠。",
                },
                {
                    "ok": True,
                    "from": "podium",
                    "from_face": "top",
                    "to": "left_tower",
                    "to_face": "bottom",
                    "status": "ok",
                },
            ],
            "stage_checks": [
                {
                    "executable": False,
                    "role": "facade",
                    "message": "阶段 facade 有模块缺少 bbox。",
                }
            ],
            "risks": ["现代高层灯光比例偏低。"],
        },
    }

    context = _conversation_diagnostic_context(diagnostics)
    assert context["template_guess"] == "modern_glass_gate"
    assert len(context["interface_issues"]) == 1
    assert context["interface_issues"][0]["from"] == "left_tower"
    assert len(context["stage_issues"]) == 1
    assert "podium" not in str(context["interface_issues"])

    prompt = _build_conversation_prompt(
        name="project_prompt_smoke",
        output_path=ROOT / "backend" / "generated_plans" / "prompt_smoke.json",
        analysis={},
        messages=[{"role": "user", "content": "请修复当前诊断问题"}],
        current_plan={"name": "project_prompt_smoke", "parts": []},
        diagnostics=diagnostics,
    )
    for expected in [
        "Current diagnostics to consider",
        "modern_glass_gate",
        "left_tower",
        "skybridge",
        "stage_issues",
        "阶段 facade 有模块缺少 bbox",
    ]:
        assert expected in prompt
    print({"conversation_diagnostics_prompt": "ok"})


if __name__ == "__main__":
    main()
