from __future__ import annotations

from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from backend.ai.planner import _static_plan
from backend.schematic.generator import generate_schematic


def main() -> None:
    plan = _static_plan("local_test_build")
    path = generate_schematic(plan, Path("server/plugins/FastAsyncWorldEdit/schematics"))
    print(path)


if __name__ == "__main__":
    main()
