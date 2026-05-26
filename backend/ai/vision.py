from __future__ import annotations

from pathlib import Path


class VisionSummary(dict):
    """Small placeholder object for the image-to-design stage."""


def analyze_image(image_path: Path) -> VisionSummary:
    """
    MVP placeholder.

    Replace this function with GPT-4o / Qwen-VL later. The rest of the system
    should not care which vision model produced the summary.
    """
    return VisionSummary(
        source=str(image_path),
        style="compact japanese-inspired house",
        floors=1,
        notable_features=["white walls", "dark wood beams", "gable roof", "front windows"],
    )
