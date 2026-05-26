from __future__ import annotations

import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.ai import analyze_image, plan_build
from backend.ai.planner import plan_from_conversation
from backend.config import ROOT_DIR, settings
from backend.dsl.schema import BuildPlan
from backend.library import load_components, load_materials
from backend.minecraft import FaweController
from backend.minecraft.rcon import MinecraftRcon, RconConfig
from backend.schematic.generator import generate_outputs


app = FastAPI(title="Minecraft AI Builder")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TaskState = dict[str, Any]
tasks: dict[str, TaskState] = {}


class ChatRequest(BaseModel):
    message: str
    paste: bool = False


class PlacementRequest(BaseModel):
    x: int | None = None
    y: int | None = None
    z: int | None = None
    spawn_x: int | None = None
    spawn_y: int | None = None
    spawn_z: int | None = None


@app.on_event("startup")
def startup() -> None:
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.schematic_dir.mkdir(parents=True, exist_ok=True)
    settings.generated_plan_dir.mkdir(parents=True, exist_ok=True)
    settings.project_dir.mkdir(parents=True, exist_ok=True)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/library")
def get_library() -> dict[str, Any]:
    return {
        "materials": load_materials().get("palettes", {}),
        "components": load_components().get("components", {}),
    }


@app.post("/api/builds")
async def create_build(background_tasks: BackgroundTasks, image: UploadFile = File(...)) -> dict[str, str]:
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="only image uploads are supported")

    task_id = uuid.uuid4().hex[:12]
    suffix = Path(image.filename or "upload.png").suffix or ".png"
    image_path = settings.upload_dir / f"{task_id}{suffix}"

    with image_path.open("wb") as target:
        shutil.copyfileobj(image.file, target)

    tasks[task_id] = {
        "id": task_id,
        "status": "queued",
        "created_at": _now(),
        "image_path": str(image_path),
        "schematic_path": None,
        "preview_path": None,
        "materials_path": None,
        "placement": None,
        "plan_path": None,
        "plan": None,
        "rcon": [],
        "error": None,
    }

    background_tasks.add_task(_run_build_task, task_id, image_path)
    return {"task_id": task_id}


@app.get("/api/builds/{task_id}")
def get_build(task_id: str) -> TaskState:
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@app.get("/api/builds/{task_id}/schematic")
def download_schematic(task_id: str) -> FileResponse:
    task = tasks.get(task_id)
    if not task or not task.get("schematic_path"):
        raise HTTPException(status_code=404, detail="schematic not found")
    return FileResponse(task["schematic_path"], filename=Path(task["schematic_path"]).name)


@app.get("/api/builds/{task_id}/preview")
def get_build_preview(task_id: str) -> FileResponse:
    task = tasks.get(task_id)
    if not task or not task.get("preview_path"):
        raise HTTPException(status_code=404, detail="preview not found")
    return FileResponse(task["preview_path"], media_type="application/json")


@app.post("/api/projects")
async def create_project(
    background_tasks: BackgroundTasks,
    image: UploadFile | None = File(default=None),
    prompt: str = Form(default=""),
) -> dict[str, str]:
    project_id = uuid.uuid4().hex[:12]
    project_path = _project_path(project_id)
    project_path.mkdir(parents=True, exist_ok=True)

    image_path: Path | None = None
    if image and image.filename:
        if image.content_type and not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="only image uploads are supported")
        suffix = Path(image.filename).suffix or ".png"
        image_path = project_path / f"source{suffix}"
        with image_path.open("wb") as target:
            shutil.copyfileobj(image.file, target)

    state = {
        "id": project_id,
        "status": "queued",
        "created_at": _now(),
        "updated_at": _now(),
        "image_path": str(image_path) if image_path else None,
        "analysis": None,
        "messages": [],
        "plan": None,
        "plan_path": None,
        "schematic_path": None,
        "preview_path": None,
        "materials_path": None,
        "placement": None,
        "rcon": [],
        "error": None,
    }
    if prompt.strip():
        state["messages"].append({"role": "user", "content": prompt.strip(), "created_at": _now()})
    _save_project(project_id, state)

    background_tasks.add_task(_run_project_generation, project_id)
    return {"project_id": project_id}


@app.get("/api/projects")
def list_projects() -> dict[str, Any]:
    projects = []
    for state in _iter_project_states():
        plan = state.get("plan") or {}
        preview = None
        if state.get("preview_path"):
            try:
                import json

                preview_path = Path(state["preview_path"])
                if preview_path.exists():
                    preview_data = json.loads(preview_path.read_text(encoding="utf-8"))
                    preview = {
                        "size": preview_data.get("size"),
                        "block_count": preview_data.get("block_count"),
                        "preview_count": preview_data.get("preview_count"),
                        "sampled": preview_data.get("sampled"),
                    }
            except Exception:
                preview = None

        projects.append(
            {
                "id": state.get("id"),
                "status": state.get("status"),
                "created_at": state.get("created_at"),
                "updated_at": state.get("updated_at"),
                "completed_at": state.get("completed_at"),
                "name": plan.get("name") or f"project_{state.get('id', '')}",
                "has_image": bool(state.get("image_path")),
                "has_plan": bool(state.get("plan")),
                "has_preview": bool(state.get("preview_path")),
                "has_schematic": bool(state.get("schematic_path")),
                "placement": state.get("placement"),
                "preview": preview,
                "last_message": _last_user_message(state.get("messages", [])),
                "error": state.get("error"),
            }
        )

    projects.sort(key=lambda item: item.get("updated_at") or item.get("created_at") or "", reverse=True)
    return {"projects": projects}


@app.get("/api/projects/{project_id}")
def get_project(project_id: str) -> dict[str, Any]:
    return _load_project(project_id)


@app.post("/api/projects/{project_id}/chat")
def chat_project(project_id: str, request: ChatRequest, background_tasks: BackgroundTasks) -> dict[str, str]:
    state = _load_project(project_id)
    if state["status"] in {"analyzing", "planning", "generating_schematic", "pasting"}:
        raise HTTPException(status_code=409, detail="project is already generating")
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="message is required")

    state["messages"].append({"role": "user", "content": message, "created_at": _now()})
    state["status"] = "queued"
    state["error"] = None
    state["updated_at"] = _now()
    state["paste_requested"] = request.paste
    _save_project(project_id, state)

    background_tasks.add_task(_run_project_generation, project_id)
    return {"project_id": project_id}


@app.post("/api/projects/{project_id}/paste")
def paste_project(project_id: str) -> dict[str, Any]:
    state = _load_project(project_id)
    schematic_path = state.get("schematic_path")
    if not schematic_path:
        raise HTTPException(status_code=404, detail="schematic not found")
    controller = FaweController()
    state["status"] = "pasting"
    _save_project(project_id, state)
    placement = _ensure_project_placement(project_id, state)
    state["rcon"] = controller.paste_schematic(
        schematic_path=Path(schematic_path),
        x=placement["paste"]["x"],
        y=placement["paste"]["y"],
        z=placement["paste"]["z"],
    )
    state["rcon"].extend(_set_spawnpoint(placement))
    state["status"] = "done"
    state["updated_at"] = _now()
    _save_project(project_id, state)
    return {"project_id": project_id, "rcon": state["rcon"]}


@app.post("/api/projects/{project_id}/placement")
def update_project_placement(project_id: str, request: PlacementRequest) -> dict[str, Any]:
    state = _load_project(project_id)
    plan = state.get("plan")
    if not plan:
        raise HTTPException(status_code=409, detail="project has no generated plan")

    placement = state.get("placement") or _allocate_placement(project_id, BuildPlan.model_validate(plan))
    paste = placement["paste"]
    spawn = placement["spawn"]
    if request.x is not None:
        paste["x"] = request.x
    if request.y is not None:
        paste["y"] = request.y
    if request.z is not None:
        paste["z"] = request.z
    if request.spawn_x is not None:
        spawn["x"] = request.spawn_x
    if request.spawn_y is not None:
        spawn["y"] = request.spawn_y
    if request.spawn_z is not None:
        spawn["z"] = request.spawn_z
    placement = _placement_from_paste(project_id, BuildPlan.model_validate(plan), paste, spawn)
    _assert_no_overlap(project_id, placement)
    state["placement"] = placement
    state["updated_at"] = _now()
    _save_project(project_id, state)
    return {"project_id": project_id, "placement": placement}


@app.get("/api/projects/{project_id}/schematic")
def download_project_schematic(project_id: str) -> FileResponse:
    state = _load_project(project_id)
    if not state.get("schematic_path"):
        raise HTTPException(status_code=404, detail="schematic not found")
    return FileResponse(state["schematic_path"], filename=Path(state["schematic_path"]).name)


@app.get("/api/projects/{project_id}/preview")
def get_project_preview(project_id: str) -> FileResponse:
    state = _load_project(project_id)
    if not state.get("preview_path"):
        raise HTTPException(status_code=404, detail="preview not found")
    return FileResponse(state["preview_path"], media_type="application/json")


@app.get("/api/projects/{project_id}/materials")
def get_project_materials(project_id: str) -> FileResponse:
    state = _load_project(project_id)
    if not state.get("materials_path"):
        raise HTTPException(status_code=404, detail="materials not found")
    return FileResponse(state["materials_path"], media_type="application/json")


def _run_build_task(task_id: str, image_path: Path) -> None:
    task = tasks[task_id]
    try:
        task["status"] = "analyzing"
        summary = analyze_image(image_path)

        task["status"] = "planning"
        plan = plan_build(summary, name=f"build_{task_id}", image_path=image_path)
        task["plan"] = plan.model_dump(by_alias=True)
        task["plan_path"] = str(settings.generated_plan_dir / f"build_{task_id}.json")

        task["status"] = "generating_schematic"
        schematic_path, preview_path, material_path = _write_outputs(plan, settings.schematic_dir)
        task["schematic_path"] = str(schematic_path)
        task["preview_path"] = str(preview_path)
        task["materials_path"] = str(material_path)

        if settings.paste_enabled:
            task["status"] = "pasting"
            controller = FaweController()
            task["rcon"] = controller.paste_schematic(
                schematic_path=schematic_path,
                x=settings.paste_x,
                y=settings.paste_y,
                z=settings.paste_z,
            )
        else:
            task["rcon"] = ["paste disabled by PASTE_ENABLED=false"]

        task["status"] = "done"
        task["completed_at"] = _now()
    except Exception as exc:  # noqa: BLE001
        task["status"] = "failed"
        task["error"] = repr(exc)
        task["completed_at"] = _now()


def _run_project_generation(project_id: str) -> None:
    state = _load_project(project_id)
    project_path = _project_path(project_id)
    try:
        image_path = Path(state["image_path"]) if state.get("image_path") else None
        if image_path and not state.get("analysis"):
            state["status"] = "analyzing"
            state["updated_at"] = _now()
            _save_project(project_id, state)
            state["analysis"] = dict(analyze_image(image_path))

        state["status"] = "planning"
        state["updated_at"] = _now()
        _save_project(project_id, state)

        plan = plan_from_conversation(
            name=f"project_{project_id}",
            analysis=state.get("analysis"),
            messages=state.get("messages", []),
            current_plan=state.get("plan"),
            image_path=image_path,
        )
        state["plan"] = plan.model_dump(by_alias=True)
        if not state.get("placement"):
            state["placement"] = _allocate_placement(project_id, plan)
        plan_path = project_path / "plan.json"
        plan_path.write_text(plan.model_dump_json(by_alias=True, indent=2), encoding="utf-8")
        state["plan_path"] = str(plan_path)

        state["status"] = "generating_schematic"
        state["updated_at"] = _now()
        _save_project(project_id, state)

        schematic_path, preview_path, material_path = _write_outputs(plan, settings.schematic_dir, project_path)
        state["schematic_path"] = str(schematic_path)
        state["preview_path"] = str(preview_path)
        state["materials_path"] = str(material_path)

        if state.pop("paste_requested", False):
            state["status"] = "pasting"
            state["updated_at"] = _now()
            _save_project(project_id, state)
            controller = FaweController()
            placement = _ensure_project_placement(project_id, state)
            state["rcon"] = controller.paste_schematic(
                schematic_path=schematic_path,
                x=placement["paste"]["x"],
                y=placement["paste"]["y"],
                z=placement["paste"]["z"],
            )
            state["rcon"].extend(_set_spawnpoint(placement))

        state["messages"].append(
            {
                "role": "assistant",
                "content": "已生成新的 schematic 和网页预览。",
                "created_at": _now(),
            }
        )
        state["status"] = "done"
        state["error"] = None
        state["updated_at"] = _now()
        state["completed_at"] = _now()
        _save_project(project_id, state)
    except Exception as exc:  # noqa: BLE001
        state["status"] = "failed"
        state["error"] = repr(exc)
        state["updated_at"] = _now()
        state["completed_at"] = _now()
        _save_project(project_id, state)


def _write_outputs(plan: BuildPlan, schematic_dir: Path, preview_dir: Path | None = None) -> tuple[Path, Path, Path]:
    return generate_outputs(plan, schematic_dir, preview_dir or schematic_dir)


def _ensure_project_placement(project_id: str, state: dict[str, Any]) -> dict[str, Any]:
    if state.get("placement"):
        return state["placement"]
    if not state.get("plan"):
        raise HTTPException(status_code=409, detail="project has no generated plan")
    placement = _allocate_placement(project_id, BuildPlan.model_validate(state["plan"]))
    state["placement"] = placement
    state["updated_at"] = _now()
    _save_project(project_id, state)
    return placement


def _allocate_placement(project_id: str, plan: BuildPlan) -> dict[str, Any]:
    sx, sy, sz = plan.size
    x = settings.paste_base_x
    z = settings.paste_base_z
    row_height = sz + settings.paste_margin

    for _ in range(10_000):
        paste = {"x": x, "y": settings.paste_base_y, "z": z}
        spawn = _default_spawn_for(plan, paste)
        placement = _placement_from_paste(project_id, plan, paste, spawn)
        if not _overlaps_existing(project_id, placement):
            return placement

        x = placement["bounds"]["max_x"] + settings.paste_margin
        if x - settings.paste_base_x > settings.paste_row_width:
            x = settings.paste_base_x
            z += row_height

    raise RuntimeError("could not allocate a non-overlapping Minecraft placement")


def _placement_from_paste(
    project_id: str,
    plan: BuildPlan,
    paste: dict[str, int],
    spawn: dict[str, int],
) -> dict[str, Any]:
    sx, sy, sz = plan.size
    bounds = {
        "min_x": paste["x"],
        "min_y": paste["y"],
        "min_z": paste["z"],
        "max_x": paste["x"] + sx - 1,
        "max_y": paste["y"] + sy - 1,
        "max_z": paste["z"] + sz - 1,
    }
    return {
        "project_id": project_id,
        "paste": paste,
        "spawn": spawn,
        "size": {"x": sx, "y": sy, "z": sz},
        "bounds": bounds,
        "margin": settings.paste_margin,
    }


def _default_spawn_for(plan: BuildPlan, paste: dict[str, int]) -> dict[str, int]:
    sx, sy, _ = plan.size
    return {
        "x": paste["x"] + sx // 2,
        "y": paste["y"] + min(settings.spawn_y_offset, max(12, sy + 6)),
        "z": paste["z"] + settings.spawn_offset_z,
    }


def _assert_no_overlap(project_id: str, placement: dict[str, Any]) -> None:
    if _overlaps_existing(project_id, placement):
        raise HTTPException(status_code=409, detail="placement overlaps another project")


def _overlaps_existing(project_id: str, placement: dict[str, Any]) -> bool:
    current = _expanded_bounds(placement["bounds"], placement.get("margin", settings.paste_margin))
    for other in _iter_project_states():
        if other.get("id") == project_id or not other.get("placement"):
            continue
        other_bounds = _expanded_bounds(other["placement"]["bounds"], other["placement"].get("margin", 0))
        if _bounds_overlap(current, other_bounds):
            return True
    return False


def _expanded_bounds(bounds: dict[str, int], margin: int) -> dict[str, int]:
    return {
        "min_x": bounds["min_x"] - margin,
        "min_y": bounds["min_y"],
        "min_z": bounds["min_z"] - margin,
        "max_x": bounds["max_x"] + margin,
        "max_y": bounds["max_y"],
        "max_z": bounds["max_z"] + margin,
    }


def _bounds_overlap(a: dict[str, int], b: dict[str, int]) -> bool:
    return (
        a["min_x"] <= b["max_x"]
        and a["max_x"] >= b["min_x"]
        and a["min_z"] <= b["max_z"]
        and a["max_z"] >= b["min_z"]
    )


def _iter_project_states() -> list[dict[str, Any]]:
    states = []
    if not settings.project_dir.exists():
        return states
    for state_path in settings.project_dir.glob("*/state.json"):
        try:
            import json

            states.append(json.loads(state_path.read_text(encoding="utf-8")))
        except Exception:
            continue
    return states


def _set_spawnpoint(placement: dict[str, Any]) -> list[str]:
    spawn = placement["spawn"]
    command = f"setworldspawn {spawn['x']} {spawn['y']} {spawn['z']}"
    try:
        rcon = MinecraftRcon(
            RconConfig(
                host=settings.rcon_host,
                port=settings.rcon_port,
                password=settings.rcon_password,
            )
        )
        response = rcon.command(command)
        return [f"/{command}", response]
    except Exception as exc:  # noqa: BLE001
        return [f"/{command}", f"setworldspawn failed: {exc!r}"]


def _last_user_message(messages: list[dict[str, Any]]) -> str | None:
    for message in reversed(messages):
        if message.get("role") == "user" and message.get("content"):
            return str(message["content"])
    return None


def _project_path(project_id: str) -> Path:
    if not project_id.replace("_", "").replace("-", "").isalnum():
        raise HTTPException(status_code=400, detail="invalid project id")
    return settings.project_dir / project_id


def _load_project(project_id: str) -> dict[str, Any]:
    state_path = _project_path(project_id) / "state.json"
    if not state_path.exists():
        raise HTTPException(status_code=404, detail="project not found")
    import json

    return json.loads(state_path.read_text(encoding="utf-8"))


def _save_project(project_id: str, state: dict[str, Any]) -> None:
    import json

    project_path = _project_path(project_id)
    project_path.mkdir(parents=True, exist_ok=True)
    state_path = project_path / "state.json"
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


frontend_dir = ROOT_DIR / "frontend"
app.mount("/assets", StaticFiles(directory=frontend_dir), name="assets")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(frontend_dir / "index.html")
