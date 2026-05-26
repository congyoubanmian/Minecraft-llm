from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import mcschematic


SCHEM_DIR = Path("server/plugins/FastAsyncWorldEdit/schematics")


@dataclass(frozen=True)
class ScaleJob:
    source: str
    target: str
    scale_x: float
    scale_y: float
    scale_z: float
    note: str


JOBS = [
    # Tianning pagoda is the baseline: 131 blocks tall for the real 153.79 m tower.
    ScaleJob("tianning_pagoda_13_story", "real_tianning_pagoda_13_story", 1.0, 1.0, 1.0, "baseline 153.79 m tower"),
    # Qingguo Lane is a street district, so scale footprint more than height.
    ScaleJob("qingguo_alley_historic_block", "real_qingguo_alley_historic_block", 1.65, 1.05, 1.55, "larger historic street footprint"),
    # Wenbi Tower should be much lower than Tianning Pagoda: about 48.38 m, near 41 blocks at this scale.
    ScaleJob("hongmei_park_wenbi_tower", "real_hongmei_park_wenbi_tower", 1.35, 0.78, 1.35, "Wenbi tower height corrected against Tianning scale"),
    # Dinosaur Park and cultural plazas are large sites; scale footprint aggressively.
    ScaleJob("china_dinosaur_park_gate", "real_china_dinosaur_park_gate", 1.75, 1.25, 1.55, "theme park entrance/museum enlarged by footprint"),
    ScaleJob("yancheng_spring_autumn_city", "real_yancheng_spring_autumn_city", 1.85, 1.20, 1.85, "Yancheng walls/moats enlarged by footprint"),
    ScaleJob("changzhou_grand_theatre_culture_plaza", "real_changzhou_grand_theatre_culture_plaza", 1.70, 1.35, 1.55, "modern plaza/theatre enlarged"),
    ScaleJob("dongpo_park_ancient_ferry", "real_dongpo_park_ancient_ferry", 1.55, 1.10, 1.50, "park and ferry enlarged by site footprint"),
]


def dims(struct: mcschematic.MCStructure) -> tuple[int, int, int]:
    lo, hi = struct.getBounds()
    return hi[0] - lo[0] + 1, hi[1] - lo[1] + 1, hi[2] - lo[2] + 1


def main() -> None:
    for job in JOBS:
        source = SCHEM_DIR / f"{job.source}.schem"
        if not source.exists():
            raise FileNotFoundError(source)

        schem = mcschematic.MCSchematic(str(source))
        struct = schem.getStructure().makeCopy()
        before = dims(struct)
        struct.scaleXYZ((0, 0, 0), job.scale_x, job.scale_y, job.scale_z)
        after = dims(struct)

        out = mcschematic.MCSchematic(struct)
        out.save(str(SCHEM_DIR), job.target, mcschematic.Version.JE_1_20_1)
        print(
            f"{job.target}.schem {before} -> {after} "
            f"scale=({job.scale_x},{job.scale_y},{job.scale_z}) note={job.note}"
        )


if __name__ == "__main__":
    main()
