from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.main import _is_busy_status, _should_repair


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

    print({"auto_repair_gate": "ok"})


if __name__ == "__main__":
    main()
