from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field


Vec3 = tuple[int, int, int]


class BoxPart(BaseModel):
    type: Literal["box"]
    from_pos: Annotated[Vec3, Field(alias="from")]
    to: Vec3
    block: str
    hollow: bool = False


class GableRoofPart(BaseModel):
    type: Literal["roof_gable"]
    from_pos: Annotated[Vec3, Field(alias="from")]
    to: Vec3
    block: str
    ridge_axis: Literal["x", "z"] = "x"


class WindowGridPart(BaseModel):
    type: Literal["window_grid"]
    wall: Literal["front", "back", "left", "right"]
    count: int = Field(ge=1, le=12)
    y: int = 3
    width: int = Field(default=2, ge=1, le=5)
    height: int = Field(default=3, ge=1, le=6)
    block: str


class WindowPart(BaseModel):
    type: Literal["window"]
    from_pos: Annotated[Vec3, Field(alias="from")]
    to: Vec3
    glass: str = "window"
    frame: str | None = "frame"
    sill: str | None = "sill"
    shutter: str | None = None


class DoorPart(BaseModel):
    type: Literal["door"]
    wall: Literal["front", "back", "left", "right"] = "front"
    x: int | None = None
    z: int | None = None
    width: int = Field(default=2, ge=1, le=4)
    height: int = Field(default=3, ge=2, le=5)
    block: str


class StairPart(BaseModel):
    type: Literal["stairs"]
    from_pos: Annotated[Vec3, Field(alias="from")]
    to: Vec3
    block: str
    facing: Literal["north", "south", "east", "west"]
    half: Literal["bottom", "top"] = "bottom"
    shape: Literal["straight", "inner_left", "inner_right", "outer_left", "outer_right"] = "straight"


class SlabPart(BaseModel):
    type: Literal["slab"]
    from_pos: Annotated[Vec3, Field(alias="from")]
    to: Vec3
    block: str
    slab_type: Literal["bottom", "top", "double"] = "bottom"


class CylinderPart(BaseModel):
    type: Literal["cylinder"]
    center: Vec3
    radius: int = Field(ge=1, le=16)
    height: int = Field(ge=1, le=32)
    block: str
    hollow: bool = False


class OctagonalTowerPart(BaseModel):
    type: Literal["octagonal_tower"]
    center: Vec3
    radius: int = Field(ge=2, le=64)
    height: int = Field(ge=1, le=192)
    block: str
    hollow: bool = True
    thickness: int = Field(default=1, ge=1, le=8)
    floor_block: str | None = None
    floor_interval: int = Field(default=0, ge=0, le=32)
    trim_block: str | None = None


class OctagonalRoofPart(BaseModel):
    type: Literal["octagonal_roof"]
    center: Vec3
    radius: int = Field(ge=2, le=72)
    layers: int = Field(default=3, ge=1, le=16)
    block: str
    fill: str | None = None
    cap: str | None = None


class OctagonalEavePart(BaseModel):
    type: Literal["octagonal_eave"]
    center: Vec3
    radius: int = Field(ge=3, le=80)
    overhang: int = Field(default=4, ge=1, le=12)
    thickness: int = Field(default=2, ge=1, le=6)
    block: str
    underside: str | None = None
    corner_block: str | None = None
    lantern: str | None = None


class VajraSpirePart(BaseModel):
    type: Literal["vajra_spire"]
    center: Vec3
    base_radius: int = Field(ge=3, le=32)
    height: int = Field(ge=8, le=80)
    block: str
    accent: str | None = None


class MiniPagodaRingPart(BaseModel):
    type: Literal["mini_pagoda_ring"]
    center: Vec3
    ring_radius: int = Field(ge=8, le=96)
    count: int = Field(default=16, ge=4, le=64)
    pagoda_radius: int = Field(default=2, ge=1, le=8)
    height: int = Field(default=8, ge=4, le=24)
    block: str
    roof: str
    accent: str | None = None


class FacadePanelRingPart(BaseModel):
    type: Literal["facade_panel_ring"]
    center: Vec3
    radius: int = Field(ge=3, le=72)
    y: int
    height: int = Field(default=4, ge=1, le=16)
    width: int = Field(default=4, ge=1, le=12)
    glass: str
    frame: str
    plaque: str | None = None


class TwistedLatticeTowerPart(BaseModel):
    type: Literal["twisted_lattice_tower"]
    center: Vec3
    body_height: int = Field(ge=32, le=260)
    antenna_height: int = Field(default=0, ge=0, le=96)
    base_radius: int = Field(ge=6, le=48)
    waist_radius: int = Field(ge=3, le=32)
    top_radius: int = Field(ge=4, le=40)
    waist_y_ratio: float = Field(default=0.56, ge=0.25, le=0.8)
    z_radius_scale: float = Field(default=0.82, ge=0.35, le=1.0)
    ring_interval: int = Field(default=8, ge=3, le=18)
    struts: int = Field(default=24, ge=8, le=48)
    twist_degrees: float = Field(default=130.0, ge=-360.0, le=360.0)
    lattice: str
    ring: str | None = None
    glass: str | None = None
    core: str | None = None
    light: str | None = None


class ComponentPart(BaseModel):
    type: Literal["component"]
    name: str = Field(pattern=r"^[a-zA-Z0-9_-]+$")
    at: Vec3 = (0, 0, 0)
    scale: float = Field(default=1.0, ge=0.25, le=8.0)
    parameters: dict[str, int | float | str | bool] = Field(default_factory=dict)
    materials: dict[str, str] = Field(default_factory=dict)


class BlockPlacement(BaseModel):
    pos: Vec3
    block: str


class BlocksPart(BaseModel):
    type: Literal["blocks"]
    blocks: list[BlockPlacement] = Field(default_factory=list, max_length=4096)


BuildPart = (
    BoxPart
    | GableRoofPart
    | WindowGridPart
    | WindowPart
    | DoorPart
    | StairPart
    | SlabPart
    | CylinderPart
    | OctagonalTowerPart
    | OctagonalRoofPart
    | OctagonalEavePart
    | VajraSpirePart
    | MiniPagodaRingPart
    | FacadePanelRingPart
    | TwistedLatticeTowerPart
    | ComponentPart
    | BlocksPart
)


class BuildPlan(BaseModel):
    name: str = Field(pattern=r"^[a-zA-Z0-9_-]+$")
    size: Vec3
    origin: Vec3 = (0, 64, 0)
    palette: dict[str, str]
    parts: list[BuildPart] = Field(default_factory=list)
    analysis: dict[str, Any] | None = None

    def block_id(self, key_or_block: str) -> str:
        block = self.palette.get(key_or_block, key_or_block)
        if ":" not in block:
            block = f"minecraft:{block}"
        return block
