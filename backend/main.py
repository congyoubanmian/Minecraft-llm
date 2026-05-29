from __future__ import annotations

import asyncio
import json
import shutil
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.ai import analyze_image, plan_build
from backend.ai.planner import plan_from_conversation
from backend.analysis import analyze_build
from backend.config import ROOT_DIR, settings
from backend.dsl.schema import BuildPlan
from backend.library import load_components, load_design_contract, load_materials, load_templates
from backend.minecraft import FaweController
from backend.minecraft.rcon import MinecraftRcon, RconConfig
from backend.schematic.generator import generate_outputs, render_plan_to_blocks


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.schematic_dir.mkdir(parents=True, exist_ok=True)
    settings.generated_plan_dir.mkdir(parents=True, exist_ok=True)
    settings.project_dir.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="Minecraft AI Builder", lifespan=_lifespan)

_cors_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_rate_limit_store: dict[str, list[float]] = defaultdict(list)
_rate_limit_last_sweep: float = 0.0


@app.middleware("http")
async def rate_limit_middleware(request: Any, call_next: Any) -> Any:
    global _rate_limit_last_sweep
    if request.url.path.startswith("/api/") and request.method == "POST":
        now = time.monotonic()
        cutoff = now - 60.0
        if now - _rate_limit_last_sweep > 60.0:
            _rate_limit_last_sweep = now
            stale = [k for k, v in _rate_limit_store.items() if not v or v[-1] < cutoff]
            for k in stale:
                del _rate_limit_store[k]
        client_ip = request.client.host if request.client else "unknown"
        key = f"{client_ip}:{request.url.path}"
        window = _rate_limit_store[key]
        window[:] = [t for t in window if t > cutoff]
        if len(window) >= settings.rate_limit_per_minute:
            return JSONResponse(status_code=429, content={"detail": "too many requests, please try again later"})
        window.append(now)
    return await call_next(request)


BUSY_STATUSES = frozenset({"queued", "analyzing", "planning", "generating_schematic", "pasting"})
TERMINAL_STATUSES = frozenset({"done", "failed", "cancelled"})


def _require_api_key(request: Request) -> None:
    if not settings.api_key:
        return
    auth = request.headers.get("Authorization", "")
    token = auth.removeprefix("Bearer ").strip()
    if token != settings.api_key:
        raise HTTPException(status_code=401, detail="invalid or missing API key")


TaskState = dict[str, Any]
tasks: dict[str, TaskState] = {}


class _WSManager:
    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = {}

    def connect(self, project_id: str, ws: WebSocket) -> None:
        self._connections.setdefault(project_id, []).append(ws)

    def disconnect(self, project_id: str, ws: WebSocket) -> None:
        conns = self._connections.get(project_id, [])
        if ws in conns:
            conns.remove(ws)
        if not conns:
            self._connections.pop(project_id, None)

    async def broadcast(self, project_id: str, data: dict[str, Any]) -> None:
        dead: list[WebSocket] = []
        for ws in self._connections.get(project_id, []):
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(project_id, ws)


_ws_manager = _WSManager()


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


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/library")
def get_library() -> dict[str, Any]:
    return {
        "materials": load_materials().get("palettes", {}),
        "components": load_components().get("components", {}),
        "templates": load_templates().get("templates", {}),
        "design_contract": load_design_contract().get("design_contract", {}),
    }


@app.websocket("/ws/projects/{project_id}")
async def ws_project_status(websocket: WebSocket, project_id: str) -> None:
    await websocket.accept()
    _ws_manager.connect(project_id, websocket)
    try:
        state = _load_project(project_id)
        await websocket.send_json({"type": "state", **state})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        _ws_manager.disconnect(project_id, websocket)


@app.post("/api/builds", dependencies=[Depends(_require_api_key)])
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
        "analysis_report_path": None,
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


@app.post("/api/projects", dependencies=[Depends(_require_api_key)])
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
        "analysis_report_path": None,
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
                "analysis_report": state.get("analysis_report"),
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


@app.post("/api/projects/{project_id}/chat", dependencies=[Depends(_require_api_key)])
def chat_project(project_id: str, request: ChatRequest, background_tasks: BackgroundTasks) -> dict[str, str]:
    state = _load_project(project_id)
    if state["status"] in BUSY_STATUSES:
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


@app.post("/api/projects/{project_id}/paste", dependencies=[Depends(_require_api_key)])
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


@app.post("/api/projects/{project_id}/cancel", dependencies=[Depends(_require_api_key)])
def cancel_project(project_id: str) -> dict[str, str]:
    state = _load_project(project_id)
    if state["status"] not in BUSY_STATUSES:
        raise HTTPException(status_code=409, detail="project is not in a cancellable state")
    state["status"] = "cancelled"
    state["error"] = "cancelled by user"
    state["updated_at"] = _now()
    state["completed_at"] = _now()
    _save_project(project_id, state)
    return {"project_id": project_id, "status": "cancelled"}


@app.post("/api/projects/{project_id}/placement", dependencies=[Depends(_require_api_key)])
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


@app.delete("/api/projects/{project_id}", dependencies=[Depends(_require_api_key)])
def delete_project(project_id: str) -> dict[str, Any]:
    project_path = _project_path(project_id)
    state_path = project_path / "state.json"
    if not state_path.exists():
        raise HTTPException(status_code=404, detail="project not found")

    state = _load_project(project_id)
    if state.get("status") in BUSY_STATUSES:
        raise HTTPException(status_code=409, detail="cannot delete project while generating")

    shutil.rmtree(project_path, ignore_errors=True)
    _invalidate_project_cache()
    return {"project_id": project_id, "deleted": True}


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


@app.get("/api/projects/{project_id}/analysis-report")
def get_project_analysis_report(project_id: str) -> FileResponse:
    state = _load_project(project_id)
    if not state.get("analysis_report_path"):
        raise HTTPException(status_code=404, detail="analysis report not found")
    return FileResponse(state["analysis_report_path"], media_type="application/json")


def _run_build_task(task_id: str, image_path: Path) -> None:
    task = tasks[task_id]
    try:
        task["status"] = "analyzing"
        summary = analyze_image(image_path)

        task["status"] = "planning"
        plan = plan_build(summary, name=f"build_{task_id}", image_path=image_path)
        task["plan"] = plan.model_dump(by_alias=True, mode="json")
        task["plan_path"] = str(settings.generated_plan_dir / f"build_{task_id}.json")

        task["status"] = "generating_schematic"
        schematic_path, preview_path, material_path, analysis_report_path, analysis_report = _write_outputs(plan, settings.schematic_dir)
        task["schematic_path"] = str(schematic_path)
        task["preview_path"] = str(preview_path)
        task["materials_path"] = str(material_path)
        task["analysis_report_path"] = str(analysis_report_path)
        task["analysis_report"] = analysis_report

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
            if _check_cancelled(project_id):
                return
            state["status"] = "analyzing"
            state["updated_at"] = _now()
            _save_project(project_id, state)
            state["analysis"] = dict(analyze_image(image_path))

        if _check_cancelled(project_id):
            return
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
        state["plan"] = plan.model_dump(by_alias=True, mode="json")
        if not state.get("placement"):
            state["placement"] = _allocate_placement(project_id, plan)
        plan_path = project_path / "plan.json"
        plan_path.write_text(plan.model_dump_json(by_alias=True, indent=2), encoding="utf-8")
        state["plan_path"] = str(plan_path)

        if _check_cancelled(project_id):
            return
        state["status"] = "generating_schematic"
        state["updated_at"] = _now()
        _save_project(project_id, state)

        schematic_path, preview_path, material_path, analysis_report_path, analysis_report = _write_outputs(plan, settings.schematic_dir, project_path)
        state["schematic_path"] = str(schematic_path)
        state["preview_path"] = str(preview_path)
        state["materials_path"] = str(material_path)
        state["analysis_report_path"] = str(analysis_report_path)
        state["analysis_report"] = analysis_report

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


def _check_cancelled(project_id: str) -> bool:
    try:
        return _load_project(project_id).get("status") == "cancelled"
    except HTTPException:
        return True


def _write_outputs(plan: BuildPlan, schematic_dir: Path, preview_dir: Path | None = None) -> tuple[Path, Path, Path, Path, dict[str, Any]]:
    output_dir = preview_dir or schematic_dir
    blocks = render_plan_to_blocks(plan)
    schematic_path, preview_path, material_path = generate_outputs(plan, schematic_dir, output_dir, blocks=blocks)
    analysis_report = analyze_build(plan, blocks)
    analysis_report_path = output_dir / f"{plan.name}.analysis.json"
    analysis_report_path.write_text(json.dumps(analysis_report, ensure_ascii=False, indent=2), encoding="utf-8")
    return schematic_path, preview_path, material_path, analysis_report_path, analysis_report


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


_project_states_cache: list[dict[str, Any]] = []
_project_states_cache_ts: float = 0.0
_PROJECT_STATES_TTL = 2.0


def _invalidate_project_cache() -> None:
    global _project_states_cache, _project_states_cache_ts
    _project_states_cache = []
    _project_states_cache_ts = 0.0


def _iter_project_states() -> list[dict[str, Any]]:
    global _project_states_cache, _project_states_cache_ts
    if _project_states_cache and time.monotonic() - _project_states_cache_ts < _PROJECT_STATES_TTL:
        return _project_states_cache
    states: list[dict[str, Any]] = []
    if settings.project_dir.exists():
        for state_path in settings.project_dir.glob("*/state.json"):
            try:
                states.append(json.loads(state_path.read_text(encoding="utf-8")))
            except Exception:
                continue
    _project_states_cache = states
    _project_states_cache_ts = time.monotonic()
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
    return json.loads(state_path.read_text(encoding="utf-8"))


def _save_project(project_id: str, state: dict[str, Any]) -> None:
    project_path = _project_path(project_id)
    project_path.mkdir(parents=True, exist_ok=True)
    state_path = project_path / "state.json"
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    _invalidate_project_cache()
    _ws_notify(project_id, state)


def _ws_notify(project_id: str, state: dict[str, Any]) -> None:
    if not _ws_manager._connections.get(project_id):
        return
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_ws_manager.broadcast(project_id, {"type": "state", **state}))
    except RuntimeError:
        pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


frontend_dir = ROOT_DIR / "frontend"
app.mount("/assets", StaticFiles(directory=frontend_dir), name="assets")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(frontend_dir / "index.html")
