from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import mcschematic


Vec3 = tuple[int, int, int]
BlockItem = tuple[Vec3, str]


@dataclass(frozen=True)
class BlockBounds:
    min_x: int
    min_y: int
    min_z: int
    max_x: int
    max_y: int
    max_z: int

    @property
    def size(self) -> tuple[int, int, int]:
        return (
            self.max_x - self.min_x + 1,
            self.max_y - self.min_y + 1,
            self.max_z - self.min_z + 1,
        )

    def model_dump(self) -> dict[str, int]:
        return {
            "min_x": self.min_x,
            "min_y": self.min_y,
            "min_z": self.min_z,
            "max_x": self.max_x,
            "max_y": self.max_y,
            "max_z": self.max_z,
        }


class BlockList:
    """Unified in-memory schematic data used by schem export and web preview."""

    def __init__(self) -> None:
        self._blocks: dict[Vec3, str] = {}

    def __len__(self) -> int:
        return len(self._blocks)

    def set_block(self, pos: Vec3, block: str) -> None:
        self._blocks[pos] = _normalize_block(block)

    def setBlock(self, pos: Vec3, block: str) -> None:  # noqa: N802 - mirrors mcschematic API
        self.set_block(pos, block)

    def items_sorted(self) -> list[BlockItem]:
        return sorted(self._blocks.items(), key=lambda item: (item[0][1], item[0][2], item[0][0]))

    def bounds(self) -> BlockBounds | None:
        if not self._blocks:
            return None
        xs = [pos[0] for pos in self._blocks]
        ys = [pos[1] for pos in self._blocks]
        zs = [pos[2] for pos in self._blocks]
        return BlockBounds(
            min_x=min(xs),
            min_y=min(ys),
            min_z=min(zs),
            max_x=max(xs),
            max_y=max(ys),
            max_z=max(zs),
        )

    def material_counts(self, base_only: bool = True) -> dict[str, int]:
        counts = Counter(
            _base_block(block) if base_only else block
            for block in self._blocks.values()
            if not _is_air(block)
        )
        return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))

    def write_schematic(self, output_dir: Path, name: str) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        schem = mcschematic.MCSchematic()
        for pos, block in self.items_sorted():
            schem.setBlock(pos, block)
        schem.save(str(output_dir), name, mcschematic.Version.JE_1_20_1)
        return output_dir / f"{name}.schem"

    def write_preview(
        self,
        output_dir: Path,
        name: str,
        size: tuple[int, int, int],
        origin: tuple[int, int, int],
        palette: dict[str, str],
        max_blocks: int = 120_000,
    ) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        payload = self.preview_payload(name=name, size=size, origin=origin, palette=palette, max_blocks=max_blocks)
        preview_path = output_dir / f"{name}.preview.json"
        preview_path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        return preview_path

    def preview_payload(
        self,
        name: str,
        size: tuple[int, int, int],
        origin: tuple[int, int, int],
        palette: dict[str, str],
        max_blocks: int = 120_000,
    ) -> dict:
        blocks = [(pos, _base_block(block)) for pos, block in self.items_sorted() if not _is_air(block)]
        full_count = len(blocks)
        sampled = False
        if full_count > max_blocks:
            sampled = True
            blocks = _sample_blocks(blocks, max_blocks)

        bounds = self.bounds()
        return {
            "name": name,
            "size": list(size),
            "origin": list(origin),
            "bounds": bounds.model_dump() if bounds else None,
            "palette": palette,
            "blocks": [[x, y, z, block] for (x, y, z), block in blocks],
            "block_count": full_count,
            "preview_count": len(blocks),
            "sampled": sampled,
            "materials": self.material_counts(),
        }

    def write_material_report(self, output_dir: Path, name: str) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "name": name,
            "block_count": sum(1 for block in self._blocks.values() if not _is_air(block)),
            "bounds": self.bounds().model_dump() if self.bounds() else None,
            "materials": self.material_counts(),
        }
        report_path = output_dir / f"{name}.materials.json"
        report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return report_path


def _sample_blocks(blocks: list[BlockItem], max_blocks: int) -> list[BlockItem]:
    if max_blocks <= 0:
        return []
    step = max(1, len(blocks) // max_blocks)
    sampled = blocks[::step][:max_blocks]
    if len(sampled) > max_blocks:
        return sampled[:max_blocks]
    return sampled


def _normalize_block(block: str) -> str:
    if ":" not in block:
        return f"minecraft:{block}"
    return block


def _base_block(block: str) -> str:
    base = block.split("[", 1)[0]
    return base.removeprefix("minecraft:")


def _is_air(block: str) -> bool:
    return _base_block(block) == "air"
