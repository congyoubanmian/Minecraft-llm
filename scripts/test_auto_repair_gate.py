from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.main import _diagnostic_score, _is_busy_status, _repair_acceptance, _should_repair


def main() -> None:
    assert _should_repair(["缺少设计规约模块列表，复杂建筑建议先定义 grid。"])
    assert _should_repair(["广州塔比例偏矮胖，高度应至少是最大宽度/深度的 2.5 倍。"])
    assert _should_repair(["方块数 960 超过 performance_budget.max_blocks=20，建议降低细节密度或拆分项目。"])
    assert not _should_repair([])
    assert not _should_repair(["普通提示：材料统计已生成。"])

    assert _is_busy_status("planning")
    assert _is_busy_status("repairing_plan_1")
    assert _is_busy_status("repairing_plan_2")
    assert not _is_busy_status("done")

    broken = {
        "warnings": ["接口 left.east 与 right.west 的 bbox 没有按声明面接触或一格重叠。"],
        "design_spec": {
            "stitch_ready": False,
            "missing_bbox": [],
            "duplicate_names": [],
            "interface_checks": [{"ok": False}],
            "stage_checks": [{"executable": True}],
        },
    }
    fixed = {
        "warnings": [],
        "design_spec": {
            "stitch_ready": True,
            "missing_bbox": [],
            "duplicate_names": [],
            "interface_checks": [{"ok": True}],
            "stage_checks": [{"executable": True}],
        },
    }
    worse = {
        "warnings": [
            "接口 left.east 与 right.west 的 bbox 没有按声明面接触或一格重叠。",
            "阶段 mass 有模块缺少 bbox，无法稳定单独清空/粘贴。",
        ],
        "design_spec": {
            "stitch_ready": False,
            "missing_bbox": ["mass"],
            "duplicate_names": [],
            "interface_checks": [{"ok": False}],
            "stage_checks": [{"executable": False}],
        },
    }
    assert _diagnostic_score(broken)["blocking"] == 2
    assert _repair_acceptance(broken, fixed) == (True, "accepted: diagnostics improved")
    accepted, reason = _repair_acceptance(broken, worse)
    assert accepted is False
    assert reason == "rejected: blocking diagnostics increased"

    print({"auto_repair_gate": "ok"})


if __name__ == "__main__":
    main()
