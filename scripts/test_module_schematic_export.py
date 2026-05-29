from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.blocks import BlockList
from backend.main import _module_schematic_path


def test_block_crop() -> None:
    blocks = BlockList()
    blocks.set_block((0, 0, 0), "stone")
    blocks.set_block((3, 2, 3), "glass")
    blocks.set_block((8, 8, 8), "gold_block")

    cropped = blocks.crop(((2, 1, 2), (4, 3, 4)))
    assert len(cropped) == 1
    assert cropped.items_sorted() == [((1, 1, 1), "minecraft:glass")]


def test_module_schematic_path() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        project_id = "module_export_smoke"
        project_dir = ROOT / "backend" / "projects" / project_id
        original_exists = project_dir.exists()
        if original_exists:
            raise RuntimeError(f"test project directory already exists: {project_dir}")
        try:
            state = {
                "plan": {
                    "name": "module_export_smoke",
                    "size": [8, 8, 8],
                    "origin": [0, 64, 0],
                    "palette": {"stone": "stone", "glass": "glass"},
                    "parts": [
                        {"type": "box", "from": [0, 0, 0], "to": [3, 3, 3], "block": "stone"},
                        {"type": "box", "from": [4, 4, 4], "to": [7, 7, 7], "block": "glass"},
                    ],
                },
                "analysis_report": {
                    "design_blueprint": {
                        "modules": [
                            {
                                "name": "stone core",
                                "role": "mass",
                                "bbox": [[0, 0, 0], [3, 3, 3]],
                            }
                        ]
                    }
                },
            }
            path = _module_schematic_path(project_id, state, "stone core")
            assert path.exists()
            assert path.name == "module_export_smoke.stone_core.schem"
            with tempfile.TemporaryDirectory() as schematic_tmp:
                fawe_path = _module_schematic_path(project_id, state, "stone core", output_dir=Path(schematic_tmp))
                assert fawe_path.exists()
                assert fawe_path.parent == Path(schematic_tmp)
        finally:
            if project_dir.exists():
                for child in sorted(project_dir.rglob("*"), reverse=True):
                    if child.is_file():
                        child.unlink()
                    else:
                        child.rmdir()
                project_dir.rmdir()


def main() -> None:
    test_block_crop()
    test_module_schematic_path()
    print({"module_schematic_export": "ok"})


if __name__ == "__main__":
    main()
