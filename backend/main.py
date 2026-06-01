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
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.ai import analyze_image, plan_build
from backend.ai.planner import plan_from_conversation, repair_plan_from_diagnostics
from backend.analysis import analyze_build
from backend.config import ROOT_DIR, settings
from backend.dsl.schema import BuildPlan
from backend.library import load_components, load_design_contract, load_materials, load_templates
from backend.minecraft import FaweController
from backend.minecraft.rcon import MinecraftRcon, RconConfig
from backend.minecraft.world_manager import backup_worlds, reset_worlds, world_status
from backend.placement import (
    archive_project_placement,
    get_project_placement,
    list_placements,
    mark_project_placement_cleared,
    rebuild_placement_registry,
    upsert_project_placement,
)
from backend.schematic.generator import generate_outputs, render_plan_to_blocks


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.schematic_dir.mkdir(parents=True, exist_ok=True)
    settings.generated_plan_dir.mkdir(parents=True, exist_ok=True)
    settings.project_dir.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="Minecraft AI Builder", lifespan=_lifespan)
MODULE_CLEAR_BLOCK_LIMIT = 1_000_000

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


class ResetWorldRequest(BaseModel):
    confirm: str


class PlacementActionRequest(BaseModel):
    player: str | None = None
    confirm: str | None = None
    snapshot_id: str | None = None
    snapshot_path: str | None = None


class ModuleSnapshotDeleteRequest(BaseModel):
    confirm: str
    snapshot_id: str | None = None
    snapshot_path: str | None = None


class ModuleSnapshotCleanupRequest(BaseModel):
    confirm: str
    module: str | None = None


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


@app.get("/api/world/status")
def get_world_status() -> dict[str, Any]:
    return world_status()


@app.post("/api/world/backup", dependencies=[Depends(_require_api_key)])
def backup_world() -> dict[str, Any]:
    return backup_worlds()


@app.post("/api/world/reset", dependencies=[Depends(_require_api_key)])
def reset_world(request: ResetWorldRequest) -> dict[str, Any]:
    if request.confirm != "RESET_WORLD":
        raise HTTPException(status_code=400, detail='confirm must be "RESET_WORLD"')
    result = reset_worlds()
    for placement in list_placements(active_only=True):
        archive_project_placement(placement["project_id"], reason="world_reset")
    return result


@app.get("/api/placements")
def get_placements(active_only: bool = False) -> dict[str, Any]:
    return {"placements": list_placements(active_only=active_only)}


@app.post("/api/placements/rebuild", dependencies=[Depends(_require_api_key)])
def rebuild_placements() -> dict[str, Any]:
    return rebuild_placement_registry(_iter_project_states())


@app.post("/api/placements/{project_id}/teleport", dependencies=[Depends(_require_api_key)])
def teleport_to_placement(project_id: str, request: PlacementActionRequest) -> dict[str, Any]:
    placement = _require_registry_placement(project_id)
    spawn = placement.get("spawn") or placement.get("paste")
    if not spawn:
        raise HTTPException(status_code=409, detail="placement has no spawn or paste coordinate")
    player = request.player or "@p"
    command = f"tp {player} {spawn['x']} {spawn['y']} {spawn['z']}"
    return {"project_id": project_id, "command": f"/{command}", "response": _rcon_command(command)}


@app.post("/api/projects/{project_id}/modules/{module_name}/teleport", dependencies=[Depends(_require_api_key)])
def teleport_to_project_module(project_id: str, module_name: str, request: PlacementActionRequest) -> dict[str, Any]:
    state = _load_project(project_id)
    placement = state.get("placement") or get_project_placement(project_id)
    if not placement:
        raise HTTPException(status_code=409, detail="project has no placement")
    module = _blueprint_module_by_name(state, module_name)
    if not module:
        raise HTTPException(status_code=404, detail="blueprint module not found")
    target = _module_world_target(placement, module)
    player = request.player or "@p"
    command = f"tp {player} {target['teleport']['x']} {target['teleport']['y']} {target['teleport']['z']}"
    return {
        "project_id": project_id,
        "module": target,
        "command": f"/{command}",
        "response": _rcon_command(command),
    }


@app.get("/api/projects/{project_id}/modules/{module_name}/operation-plan")
def get_project_module_operation_plan(project_id: str, module_name: str) -> dict[str, Any]:
    state, target = _module_operation_context(project_id, module_name)
    return _module_operation_plan(project_id, state, module_name, target)


@app.post("/api/projects/{project_id}/modules/{module_name}/paste", dependencies=[Depends(_require_api_key)])
def paste_project_module(project_id: str, module_name: str, request: PlacementActionRequest) -> dict[str, Any]:
    if request.confirm != "PASTE_MODULE":
        raise HTTPException(status_code=400, detail='confirm must be "PASTE_MODULE"')
    state, target = _module_operation_context(project_id, module_name)
    schematic_path = _module_schematic_path(project_id, state, module_name, output_dir=settings.schematic_dir)
    snapshot = _snapshot_module_schematic(project_id, state, module_name, target, prefer_world=False)
    commands = _paste_module_schematic(schematic_path, target)
    state["updated_at"] = _now()
    state.setdefault("module_rcon", {})[module_name] = commands
    _record_module_operation(state, module_name, "paste", target, commands, schematic_path=schematic_path, snapshot=snapshot)
    _save_project(project_id, state)
    return {
        "project_id": project_id,
        "module": target,
        "schematic_path": str(schematic_path),
        "snapshot": snapshot,
        "rcon": commands,
    }


@app.post("/api/projects/{project_id}/modules/{module_name}/clear", dependencies=[Depends(_require_api_key)])
def clear_project_module(project_id: str, module_name: str, request: PlacementActionRequest) -> dict[str, Any]:
    if request.confirm != "CLEAR_MODULE":
        raise HTTPException(status_code=400, detail='confirm must be "CLEAR_MODULE"')
    state, target = _module_operation_context(project_id, module_name)
    clear_result = _clear_module_area(target)
    state["updated_at"] = _now()
    state.setdefault("module_rcon", {})[f"{module_name}:clear"] = [clear_result["command"], clear_result["response"]]
    _record_module_operation(
        state,
        module_name,
        "clear",
        target,
        [clear_result["command"], clear_result["response"]],
        blocks=clear_result["blocks"],
    )
    _save_project(project_id, state)
    return {
        "project_id": project_id,
        "module": target,
        **clear_result,
    }


@app.post("/api/projects/{project_id}/modules/{module_name}/replace", dependencies=[Depends(_require_api_key)])
def replace_project_module(project_id: str, module_name: str, request: PlacementActionRequest) -> dict[str, Any]:
    if request.confirm != "REPLACE_MODULE":
        raise HTTPException(status_code=400, detail='confirm must be "REPLACE_MODULE"')
    state, target = _module_operation_context(project_id, module_name)
    schematic_path = _module_schematic_path(project_id, state, module_name, output_dir=settings.schematic_dir)
    snapshot = _snapshot_module_schematic(project_id, state, module_name, target, prefer_world=True)
    clear_result = _clear_module_area(target)
    paste_commands = _paste_module_schematic(schematic_path, target)
    rcon = [clear_result["command"], clear_result["response"], *paste_commands]
    state["updated_at"] = _now()
    state.setdefault("module_rcon", {})[f"{module_name}:replace"] = rcon
    _record_module_operation(
        state,
        module_name,
        "replace",
        target,
        rcon,
        schematic_path=schematic_path,
        blocks=clear_result["blocks"],
        snapshot=snapshot,
    )
    _save_project(project_id, state)
    return {
        "project_id": project_id,
        "module": target,
        "schematic_path": str(schematic_path),
        "snapshot": snapshot,
        "clear": clear_result,
        "rcon": rcon,
    }


@app.post("/api/projects/{project_id}/modules/{module_name}/rollback", dependencies=[Depends(_require_api_key)])
def rollback_project_module(project_id: str, module_name: str, request: PlacementActionRequest) -> dict[str, Any]:
    if request.confirm != "ROLLBACK_MODULE":
        raise HTTPException(status_code=400, detail='confirm must be "ROLLBACK_MODULE"')
    state, target = _module_operation_context(project_id, module_name)
    snapshot = _module_snapshot_by_ref(state, module_name, request.snapshot_id, request.snapshot_path)
    if not snapshot:
        raise HTTPException(status_code=404, detail="module snapshot not found")
    snapshot_path = Path(snapshot["path"])
    if not snapshot_path.exists():
        raise HTTPException(status_code=404, detail="module snapshot file not found")
    commands = _paste_module_schematic(snapshot_path, target)
    state["updated_at"] = _now()
    state.setdefault("module_rcon", {})[f"{module_name}:rollback"] = commands
    _record_module_operation(state, module_name, "rollback", target, commands, schematic_path=snapshot_path)
    _save_project(project_id, state)
    return {
        "project_id": project_id,
        "module": target,
        "snapshot": snapshot,
        "rcon": commands,
    }


@app.post("/api/placements/{project_id}/archive", dependencies=[Depends(_require_api_key)])
def archive_placement(project_id: str) -> dict[str, Any]:
    archived = archive_project_placement(project_id, reason="manual_archive")
    if not archived:
        raise HTTPException(status_code=404, detail="active placement not found")
    return {"project_id": project_id, "placement": archived}


@app.post("/api/placements/{project_id}/clear", dependencies=[Depends(_require_api_key)])
def clear_placement(project_id: str, request: PlacementActionRequest) -> dict[str, Any]:
    if request.confirm != "CLEAR_AREA":
        raise HTTPException(status_code=400, detail='confirm must be "CLEAR_AREA"')
    placement = _require_registry_placement(project_id)
    bounds = placement.get("bounds")
    if not bounds:
        raise HTTPException(status_code=409, detail="placement has no bounds")
    volume = _bounds_volume(bounds)
    if volume > 5_000_000:
        raise HTTPException(status_code=409, detail=f"area too large to clear safely: {volume} blocks")
    command = (
        f"fill {bounds['min_x']} {bounds['min_y']} {bounds['min_z']} "
        f"{bounds['max_x']} {bounds['max_y']} {bounds['max_z']} air replace"
    )
    response = _rcon_command(command)
    cleared = mark_project_placement_cleared(project_id)
    return {"project_id": project_id, "blocks": volume, "command": f"/{command}", "response": response, "placement": cleared}


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
        "surface_preview_path": None,
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
def get_build_preview(task_id: str, mode: str = "surface") -> FileResponse:
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="preview not found")
    preview_path = _preview_path_for_mode(task, mode)
    if not preview_path:
        raise HTTPException(status_code=404, detail="preview not found")
    return FileResponse(preview_path, media_type="application/json")


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
        "surface_preview_path": None,
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
        summary_preview_path = state.get("surface_preview_path") or state.get("preview_path")
        if summary_preview_path:
            try:
                preview_path = Path(summary_preview_path)
                if preview_path.exists():
                    preview_data = json.loads(preview_path.read_text(encoding="utf-8"))
                    preview = {
                        "mode": preview_data.get("mode"),
                        "size": preview_data.get("size"),
                        "block_count": preview_data.get("block_count"),
                        "preview_source_count": preview_data.get("preview_source_count"),
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
                "has_preview": bool(summary_preview_path),
                "has_schematic": bool(state.get("schematic_path")),
                "placement": state.get("placement"),
                "analysis_report": state.get("analysis_report"),
                "preview": preview,
                "snapshot_summary": _snapshot_summary(state),
                "last_message": _last_user_message(state.get("messages", [])),
                "error": state.get("error"),
            }
        )

    projects.sort(key=lambda item: item.get("updated_at") or item.get("created_at") or "", reverse=True)
    return {"projects": projects}


@app.get("/api/projects/{project_id}")
def get_project(project_id: str) -> dict[str, Any]:
    return _project_response(_load_project(project_id))


@app.get("/api/projects/{project_id}/module-operations")
def get_project_module_operations(project_id: str) -> dict[str, Any]:
    state = _load_project(project_id)
    return {
        "project_id": project_id,
        "module_operations": state.get("module_operations") or [],
        "module_rcon": state.get("module_rcon") or {},
    }


@app.post("/api/projects/{project_id}/analysis-report/refresh", dependencies=[Depends(_require_api_key)])
def refresh_project_analysis_report(project_id: str) -> dict[str, Any]:
    state = _load_project(project_id)
    plan_data = state.get("plan")
    if not plan_data:
        raise HTTPException(status_code=409, detail="project has no generated plan")
    plan = BuildPlan.model_validate(plan_data)
    analysis_report_path, analysis_report = _refresh_analysis_report(plan, _project_path(project_id))
    state["analysis_report_path"] = str(analysis_report_path)
    state["analysis_report"] = analysis_report
    state["updated_at"] = _now()
    _save_project(project_id, state)
    return {
        "project_id": project_id,
        "analysis_report_path": str(analysis_report_path),
        "analysis_report": analysis_report,
    }


@app.get("/api/projects/{project_id}/module-snapshots")
def get_project_module_snapshots(project_id: str, module: str | None = None) -> dict[str, Any]:
    state = _load_project(project_id)
    snapshots = _module_snapshots(state, module)
    return {
        "project_id": project_id,
        "module": module,
        "snapshot_count": len(snapshots),
        "snapshots": snapshots,
    }


@app.get("/api/projects/{project_id}/module-snapshots/download")
def download_project_module_snapshot(
    project_id: str,
    snapshot_id: str | None = None,
    snapshot_path: str | None = None,
) -> FileResponse:
    state = _load_project(project_id)
    snapshot = _snapshot_by_ref(state, snapshot_id, snapshot_path)
    if not snapshot:
        raise HTTPException(status_code=404, detail="module snapshot not found")
    path = Path(snapshot["path"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="module snapshot file not found")
    return FileResponse(path, filename=path.name)


@app.delete("/api/projects/{project_id}/module-snapshots", dependencies=[Depends(_require_api_key)])
def delete_project_module_snapshot(project_id: str, request: ModuleSnapshotDeleteRequest) -> dict[str, Any]:
    if request.confirm != "DELETE_MODULE_SNAPSHOT":
        raise HTTPException(status_code=400, detail='confirm must be "DELETE_MODULE_SNAPSHOT"')
    state = _load_project(project_id)
    removed = _delete_module_snapshot(state, request.snapshot_id, request.snapshot_path)
    if not removed:
        raise HTTPException(status_code=404, detail="module snapshot not found")
    state["updated_at"] = _now()
    _save_project(project_id, state)
    return {
        "project_id": project_id,
        "snapshot": removed["snapshot"],
        "removed_snapshots": [removed["snapshot"]],
        "file_removed": removed["file_removed"],
        "snapshot_summary": _snapshot_summary(state),
    }


@app.post("/api/projects/{project_id}/module-snapshots/cleanup", dependencies=[Depends(_require_api_key)])
def cleanup_project_module_snapshots(project_id: str, request: ModuleSnapshotCleanupRequest) -> dict[str, Any]:
    if request.confirm != "CLEANUP_MISSING_MODULE_SNAPSHOTS":
        raise HTTPException(status_code=400, detail='confirm must be "CLEANUP_MISSING_MODULE_SNAPSHOTS"')
    state = _load_project(project_id)
    snapshots = state.get("module_snapshots") or []
    kept: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    for snapshot in snapshots:
        if request.module and snapshot.get("module") != request.module:
            kept.append(snapshot)
            continue
        file_status = _snapshot_with_file_status(snapshot).get("file", {})
        if snapshot.get("path") and not file_status.get("exists"):
            removed.append(snapshot)
        else:
            kept.append(snapshot)
    state["module_snapshots"] = kept
    if removed:
        state["updated_at"] = _now()
        _save_project(project_id, state)
    return {
        "project_id": project_id,
        "module": request.module,
        "removed_count": len(removed),
        "remaining_count": len(kept),
        "removed_snapshots": removed,
        "snapshot_summary": _snapshot_summary(state),
    }


@app.delete("/api/projects/{project_id}/module-operations", dependencies=[Depends(_require_api_key)])
def clear_project_module_operations(project_id: str) -> dict[str, Any]:
    state = _load_project(project_id)
    removed_operations = len(state.get("module_operations") or [])
    removed_rcon = len(state.get("module_rcon") or {})
    state["module_operations"] = []
    state["module_rcon"] = {}
    state["updated_at"] = _now()
    _save_project(project_id, state)
    return {
        "project_id": project_id,
        "removed_operations": removed_operations,
        "removed_rcon": removed_rcon,
    }


@app.post("/api/projects/{project_id}/chat", dependencies=[Depends(_require_api_key)])
def chat_project(project_id: str, request: ChatRequest, background_tasks: BackgroundTasks) -> dict[str, str]:
    state = _load_project(project_id)
    if _is_busy_status(state["status"]):
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
    upsert_project_placement(
        project_id=project_id,
        placement=placement,
        project_name=(state.get("plan") or {}).get("name"),
        pasted=True,
    )
    state["status"] = "done"
    state["updated_at"] = _now()
    _save_project(project_id, state)
    return {"project_id": project_id, "rcon": state["rcon"]}


@app.post("/api/projects/{project_id}/cancel", dependencies=[Depends(_require_api_key)])
def cancel_project(project_id: str) -> dict[str, str]:
    state = _load_project(project_id)
    if not _is_busy_status(state["status"]):
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
    upsert_project_placement(
        project_id=project_id,
        placement=placement,
        project_name=(state.get("plan") or {}).get("name"),
        pasted=bool(state.get("rcon")),
    )
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
    if _is_busy_status(state.get("status")):
        raise HTTPException(status_code=409, detail="cannot delete project while generating")

    shutil.rmtree(project_path, ignore_errors=True)
    archive_project_placement(project_id, reason="project_deleted")
    _invalidate_project_cache()
    return {"project_id": project_id, "deleted": True}


@app.get("/api/projects/{project_id}/schematic")
def download_project_schematic(project_id: str) -> FileResponse:
    state = _load_project(project_id)
    if not state.get("schematic_path"):
        raise HTTPException(status_code=404, detail="schematic not found")
    return FileResponse(state["schematic_path"], filename=Path(state["schematic_path"]).name)


@app.get("/api/projects/{project_id}/modules/{module_name}/schematic")
def download_project_module_schematic(project_id: str, module_name: str) -> FileResponse:
    state = _load_project(project_id)
    path = _module_schematic_path(project_id, state, module_name)
    return FileResponse(path, filename=path.name)


@app.get("/api/projects/{project_id}/preview")
def get_project_preview(project_id: str, mode: str = "surface", module: str | None = None) -> Response:
    state = _load_project(project_id)
    preview_path = _preview_path_for_mode(state, mode)
    if not preview_path:
        raise HTTPException(status_code=404, detail="preview not found")
    if module:
        payload = _module_preview_payload(state, preview_path, module)
        return Response(
            content=json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            media_type="application/json",
        )
    return FileResponse(preview_path, media_type="application/json")


def _preview_path_for_mode(state: dict[str, Any], mode: str) -> str | None:
    if mode not in {"surface", "full"}:
        raise HTTPException(status_code=400, detail="preview mode must be surface or full")

    if mode == "full":
        path = state.get("preview_path")
        return path if path and Path(path).exists() else None

    surface_path = state.get("surface_preview_path")
    if surface_path and Path(surface_path).exists():
        return surface_path
    fallback_path = state.get("preview_path")
    return fallback_path if fallback_path and Path(fallback_path).exists() else None


def _module_preview_payload(state: dict[str, Any], preview_path: str, module_name: str) -> dict[str, Any]:
    preview = json.loads(Path(preview_path).read_text(encoding="utf-8"))
    module = _blueprint_module_by_name(state, module_name)
    if not module:
        raise HTTPException(status_code=404, detail="blueprint module not found")
    bbox = module.get("bbox")
    if not bbox:
        raise HTTPException(status_code=409, detail="blueprint module has no bbox")

    filtered = _blocks_in_bbox(preview.get("blocks") or [], bbox)
    payload = dict(preview)
    payload["blocks"] = filtered
    payload["preview_count"] = len(filtered)
    payload["module"] = {
        "name": module.get("name"),
        "role": module.get("role"),
        "bbox": bbox,
        "size": module.get("size"),
    }
    payload["module_filtered"] = True
    payload["module_source_count"] = len(preview.get("blocks") or [])
    return payload


def _blueprint_module_by_name(state: dict[str, Any], module_name: str) -> dict[str, Any] | None:
    blueprint = (state.get("analysis_report") or {}).get("design_blueprint") or {}
    for module in blueprint.get("modules") or []:
        if module.get("name") == module_name:
            return module
    return None


def _blocks_in_bbox(blocks: list[list[Any]], bbox: list[list[int]]) -> list[list[Any]]:
    (min_x, min_y, min_z), (max_x, max_y, max_z) = bbox
    return [
        block
        for block in blocks
        if (
            len(block) >= 4
            and min_x <= block[0] <= max_x
            and min_y <= block[1] <= max_y
            and min_z <= block[2] <= max_z
        )
    ]


def _module_operation_context(project_id: str, module_name: str) -> tuple[dict[str, Any], dict[str, Any]]:
    state = _load_project(project_id)
    placement = state.get("placement") or get_project_placement(project_id)
    if not placement:
        raise HTTPException(status_code=409, detail="project has no placement")
    module = _blueprint_module_by_name(state, module_name)
    if not module:
        raise HTTPException(status_code=404, detail="blueprint module not found")
    return state, _module_world_target(placement, module)


def _clear_module_plan(target: dict[str, Any]) -> dict[str, Any]:
    bounds = target["world_bounds"]
    volume = _bounds_volume(bounds)
    command = (
        f"fill {bounds['min_x']} {bounds['min_y']} {bounds['min_z']} "
        f"{bounds['max_x']} {bounds['max_y']} {bounds['max_z']} air replace"
    )
    return {
        "blocks": volume,
        "command": f"/{command}",
        "limit": MODULE_CLEAR_BLOCK_LIMIT,
        "safe": volume <= MODULE_CLEAR_BLOCK_LIMIT,
    }


def _module_operation_plan(
    project_id: str,
    state: dict[str, Any],
    module_name: str,
    target: dict[str, Any],
) -> dict[str, Any]:
    clear = _clear_module_plan(target)
    paste = {
        "x": target["world_bounds"]["min_x"],
        "y": target["world_bounds"]["min_y"],
        "z": target["world_bounds"]["min_z"],
    }
    schematic_path: str | None = None
    try:
        schematic_path = str(_module_schematic_path(project_id, state, module_name, output_dir=settings.schematic_dir))
    except HTTPException:
        schematic_path = None
    return {
        "project_id": project_id,
        "module": target,
        "schematic_path": schematic_path,
        "latest_snapshot": _latest_module_snapshot(state, module_name),
        "snapshots": _module_snapshots(state, module_name)[:5],
        "world_bounds": target["world_bounds"],
        "teleport": target["teleport"],
        "clear": clear,
        "paste": paste,
        "replace": {
            "steps": ["clear", "paste"],
            "safe": clear["safe"],
        },
    }


def _clear_module_area(target: dict[str, Any]) -> dict[str, Any]:
    plan = _clear_module_plan(target)
    if not plan["safe"]:
        raise HTTPException(status_code=409, detail=f"module area too large to clear safely: {plan['blocks']} blocks")
    response = _rcon_command(plan["command"].lstrip("/"))
    return {"blocks": plan["blocks"], "command": plan["command"], "response": response}


def _paste_module_schematic(schematic_path: Path, target: dict[str, Any]) -> list[str]:
    paste = target["world_bounds"]
    controller = FaweController()
    return controller.paste_schematic(
        schematic_path=schematic_path,
        x=paste["min_x"],
        y=paste["min_y"],
        z=paste["min_z"],
    )


def _snapshot_module_schematic(
    project_id: str,
    state: dict[str, Any],
    module_name: str,
    target: dict[str, Any],
    *,
    prefer_world: bool = True,
) -> dict[str, Any] | None:
    snapshot_dir = settings.schematic_dir
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    safe_name = _safe_filename(module_name)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snapshot_path = snapshot_dir / f"snapshot_{_safe_filename(project_id)}_{timestamp}_{safe_name}_{uuid.uuid4().hex[:8]}.schem"

    commands: list[str] = []
    source = "generated"
    error: str | None = None
    if prefer_world:
        try:
            controller = FaweController()
            commands = controller.save_region(snapshot_path, target["world_bounds"])
            source = "world"
        except Exception as exc:
            error = str(exc)

    source_path = state.get("schematic_path")
    if source != "world":
        if not source_path or not Path(source_path).exists():
            if error:
                return {
                    "id": uuid.uuid4().hex,
                    "module": module_name,
                    "created_at": _now(),
                    "source": "failed",
                    "error": error,
                    "world_bounds": target.get("world_bounds"),
                }
            return None
        shutil.copy2(source_path, snapshot_path)

    snapshot = {
        "id": uuid.uuid4().hex,
        "module": module_name,
        "created_at": _now(),
        "source": source,
        "path": str(snapshot_path),
        "world_bounds": target.get("world_bounds"),
    }
    if commands:
        snapshot["commands"] = commands
    if source_path:
        snapshot["source_path"] = str(source_path)
    if error:
        snapshot["fallback_error"] = error
    snapshots = state.setdefault("module_snapshots", [])
    snapshots.append(snapshot)
    _trim_module_snapshots(state)
    return snapshot


def _latest_module_snapshot(state: dict[str, Any], module_name: str) -> dict[str, Any] | None:
    snapshots = _module_snapshots(state, module_name)
    return snapshots[0] if snapshots else None


def _module_snapshot_by_ref(
    state: dict[str, Any],
    module_name: str,
    snapshot_id: str | None = None,
    snapshot_path: str | None = None,
) -> dict[str, Any] | None:
    if not snapshot_id and not snapshot_path:
        return _latest_module_snapshot(state, module_name)
    for snapshot in _module_snapshots(state, module_name):
        if _snapshot_ref_matches(snapshot, snapshot_id, snapshot_path):
            return snapshot
    return None


def _snapshot_by_ref(
    state: dict[str, Any],
    snapshot_id: str | None = None,
    snapshot_path: str | None = None,
) -> dict[str, Any] | None:
    if not snapshot_id and not snapshot_path:
        return None
    for snapshot in state.get("module_snapshots") or []:
        if _snapshot_ref_matches(snapshot, snapshot_id, snapshot_path):
            return snapshot
    return None


def _snapshot_ref_matches(
    snapshot: dict[str, Any],
    snapshot_id: str | None = None,
    snapshot_path: str | None = None,
) -> bool:
    if snapshot_id and snapshot.get("id") == snapshot_id:
        return True
    if snapshot_path and snapshot.get("path") == snapshot_path:
        return True
    return False


def _delete_module_snapshot(
    state: dict[str, Any],
    snapshot_id: str | None = None,
    snapshot_path: str | None = None,
) -> dict[str, Any] | None:
    if not snapshot_id and not snapshot_path:
        return None
    snapshots = state.get("module_snapshots") or []
    for index, snapshot in enumerate(snapshots):
        if not _snapshot_ref_matches(snapshot, snapshot_id, snapshot_path):
            continue
        removed_snapshot = snapshots.pop(index)
        state["module_snapshots"] = snapshots
        file_removed = _remove_snapshot_file(snapshot)
        return {"snapshot": removed_snapshot, "file_removed": file_removed}
    return None


def _trim_module_snapshots(state: dict[str, Any], keep: int = 50) -> list[dict[str, Any]]:
    snapshots = state.get("module_snapshots") or []
    if keep < 1 or len(snapshots) <= keep:
        state["module_snapshots"] = snapshots
        return []
    removed = snapshots[:-keep]
    state["module_snapshots"] = snapshots[-keep:]
    for snapshot in removed:
        _remove_snapshot_file(snapshot)
    return removed


def _remove_snapshot_file(snapshot: dict[str, Any]) -> bool:
    path_value = snapshot.get("path")
    if not path_value:
        return False
    path = Path(path_value)
    if path.exists() and _is_path_inside(path, settings.schematic_dir):
        path.unlink()
        return True
    return False


def _is_path_inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _module_snapshots(state: dict[str, Any], module_name: str | None = None) -> list[dict[str, Any]]:
    snapshots = [
        _snapshot_with_file_status(snapshot)
        for snapshot in state.get("module_snapshots") or []
        if module_name is None or snapshot.get("module") == module_name
    ]
    return list(reversed(snapshots))


def _snapshot_with_file_status(snapshot: dict[str, Any]) -> dict[str, Any]:
    payload = dict(snapshot)
    path_value = snapshot.get("path")
    file_status = {
        "exists": False,
        "name": Path(path_value).name if path_value else None,
        "size": None,
        "managed": False,
    }
    if path_value:
        path = Path(path_value)
        file_status["managed"] = _is_path_inside(path, settings.schematic_dir)
        if path.exists():
            file_status["exists"] = True
            file_status["size"] = path.stat().st_size
    payload["file"] = file_status
    return payload


def _project_response(state: dict[str, Any]) -> dict[str, Any]:
    payload = dict(state)
    if "module_snapshots" in payload:
        payload["module_snapshots"] = [_snapshot_with_file_status(snapshot) for snapshot in payload.get("module_snapshots") or []]
    payload["snapshot_summary"] = _snapshot_summary(state)
    return payload


def _snapshot_summary(state: dict[str, Any]) -> dict[str, Any]:
    snapshots = [_snapshot_with_file_status(snapshot) for snapshot in state.get("module_snapshots") or []]
    modules = {snapshot.get("module") for snapshot in snapshots if snapshot.get("module")}
    available = [snapshot for snapshot in snapshots if snapshot.get("file", {}).get("exists")]
    missing = [snapshot for snapshot in snapshots if snapshot.get("path") and not snapshot.get("file", {}).get("exists")]
    bytes_total = sum(int(snapshot.get("file", {}).get("size") or 0) for snapshot in available)
    latest = max((snapshot.get("created_at") or "" for snapshot in snapshots), default="")
    return {
        "count": len(snapshots),
        "available_count": len(available),
        "missing_count": len(missing),
        "bytes": bytes_total,
        "module_count": len(modules),
        "latest_created_at": latest or None,
    }


def _record_module_operation(
    state: dict[str, Any],
    module_name: str,
    action: str,
    target: dict[str, Any],
    commands: list[str],
    *,
    schematic_path: Path | None = None,
    blocks: int | None = None,
    snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    operation = {
        "module": module_name,
        "action": action,
        "created_at": _now(),
        "command_count": len(commands),
        "commands": commands,
        "world_bounds": target.get("world_bounds"),
        "teleport": target.get("teleport"),
    }
    if schematic_path is not None:
        operation["schematic_path"] = str(schematic_path)
    if blocks is not None:
        operation["blocks"] = blocks
    if snapshot:
        operation["snapshot"] = snapshot
    operations = state.setdefault("module_operations", [])
    operations.append(operation)
    del operations[:-50]
    return operation


def _module_schematic_path(project_id: str, state: dict[str, Any], module_name: str, output_dir: Path | None = None) -> Path:
    if not state.get("plan"):
        raise HTTPException(status_code=409, detail="project has no generated plan")
    module = _blueprint_module_by_name(state, module_name)
    if not module:
        raise HTTPException(status_code=404, detail="blueprint module not found")
    bbox = module.get("bbox")
    if not bbox:
        raise HTTPException(status_code=409, detail="blueprint module has no bbox")

    plan = BuildPlan.model_validate(state["plan"])
    blocks = render_plan_to_blocks(plan)
    cropped = blocks.crop(_bbox_tuple(bbox), rebase=True)
    if len(cropped) == 0:
        raise HTTPException(status_code=409, detail="blueprint module contains no blocks")

    module_dir = output_dir or (_project_path(project_id) / "modules")
    safe_module = _safe_filename(module_name)
    return cropped.write_schematic(module_dir, f"{plan.name}.{safe_module}")


def _bbox_tuple(bbox: list[list[int]]) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    return (
        (int(bbox[0][0]), int(bbox[0][1]), int(bbox[0][2])),
        (int(bbox[1][0]), int(bbox[1][1]), int(bbox[1][2])),
    )


def _safe_filename(value: str) -> str:
    safe = "".join(char if char.isalnum() or char in {"_", "-"} else "_" for char in value.strip())
    return safe or "module"


def _module_world_target(placement: dict[str, Any], module: dict[str, Any]) -> dict[str, Any]:
    bbox = module.get("bbox")
    if not bbox:
        raise HTTPException(status_code=409, detail="blueprint module has no bbox")
    paste = placement.get("paste")
    if not paste:
        raise HTTPException(status_code=409, detail="placement has no paste coordinate")
    (min_x, min_y, min_z), (max_x, max_y, max_z) = bbox
    world_bounds = {
        "min_x": paste["x"] + min_x,
        "min_y": paste["y"] + min_y,
        "min_z": paste["z"] + min_z,
        "max_x": paste["x"] + max_x,
        "max_y": paste["y"] + max_y,
        "max_z": paste["z"] + max_z,
    }
    width = max_x - min_x + 1
    depth = max_z - min_z + 1
    height = max_y - min_y + 1
    stand_off = max(8, min(48, max(width, depth) // 2 + 8))
    teleport = {
        "x": (world_bounds["min_x"] + world_bounds["max_x"]) // 2,
        "y": min(world_bounds["max_y"] + 6, world_bounds["min_y"] + max(4, height // 2)),
        "z": world_bounds["min_z"] - stand_off,
    }
    return {
        "name": module.get("name"),
        "role": module.get("role"),
        "local_bbox": bbox,
        "world_bounds": world_bounds,
        "teleport": teleport,
        "stand_off": stand_off,
    }


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
        schematic_path, preview_path, surface_preview_path, material_path, analysis_report_path, analysis_report = _write_outputs(plan, settings.schematic_dir)
        task["schematic_path"] = str(schematic_path)
        task["preview_path"] = str(preview_path)
        task["surface_preview_path"] = str(surface_preview_path)
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
            diagnostics=state.get("analysis_report") or state.get("preflight_analysis_report"),
            image_path=image_path,
        )
        plan, preflight_report = _repair_plan_if_needed(project_id, state, plan, image_path)
        state["preflight_analysis_report"] = preflight_report
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

        schematic_path, preview_path, surface_preview_path, material_path, analysis_report_path, analysis_report = _write_outputs(plan, settings.schematic_dir, project_path)
        state["schematic_path"] = str(schematic_path)
        state["preview_path"] = str(preview_path)
        state["surface_preview_path"] = str(surface_preview_path)
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
            upsert_project_placement(
                project_id=project_id,
                placement=placement,
                project_name=(state.get("plan") or {}).get("name"),
                pasted=True,
            )

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


def _is_busy_status(status: Any) -> bool:
    return status in BUSY_STATUSES or (isinstance(status, str) and status.startswith("repairing_plan_"))


def _write_outputs(plan: BuildPlan, schematic_dir: Path, preview_dir: Path | None = None) -> tuple[Path, Path, Path, Path, Path, dict[str, Any]]:
    output_dir = preview_dir or schematic_dir
    blocks = render_plan_to_blocks(plan)
    schematic_path, preview_path, surface_preview_path, material_path = generate_outputs(plan, schematic_dir, output_dir, blocks=blocks)
    analysis_report_path, analysis_report = _refresh_analysis_report(plan, output_dir, blocks=blocks)
    return schematic_path, preview_path, surface_preview_path, material_path, analysis_report_path, analysis_report


def _refresh_analysis_report(plan: BuildPlan, output_dir: Path, blocks: Any | None = None) -> tuple[Path, dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered_blocks = blocks if blocks is not None else render_plan_to_blocks(plan)
    analysis_report = analyze_build(plan, rendered_blocks)
    analysis_report_path = output_dir / f"{plan.name}.analysis.json"
    analysis_report_path.write_text(json.dumps(analysis_report, ensure_ascii=False, indent=2), encoding="utf-8")
    return analysis_report_path, analysis_report


def _repair_plan_if_needed(
    project_id: str,
    state: dict[str, Any],
    plan: BuildPlan,
    image_path: Path | None,
) -> tuple[BuildPlan, dict[str, Any]]:
    blocks = render_plan_to_blocks(plan)
    report = analyze_build(plan, blocks)
    warnings = report.get("warnings") or []
    state["repair_history"] = []
    if not _should_repair(warnings):
        return plan, report
    if not settings.planner_auto_repair or settings.planner_repair_attempts <= 0:
        return plan, report

    current = plan
    current_report = report
    for attempt in range(1, settings.planner_repair_attempts + 1):
        if _check_cancelled(project_id):
            return current, current_report
        state["status"] = f"repairing_plan_{attempt}"
        state["updated_at"] = _now()
        state["repair_history"].append(
            {
                "attempt": attempt,
                "input_warnings": current_report.get("warnings", []),
                "started_at": _now(),
            }
        )
        _save_project(project_id, state)

        repaired = repair_plan_from_diagnostics(
            name=f"project_{project_id}",
            analysis=state.get("analysis"),
            messages=state.get("messages", []),
            current_plan=current.model_dump(by_alias=True, mode="json"),
            diagnostics=current_report,
            image_path=image_path,
            attempt=attempt,
        )
        repaired_blocks = render_plan_to_blocks(repaired)
        repaired_report = analyze_build(repaired, repaired_blocks)
        accepted, reason = _repair_acceptance(current_report, repaired_report)
        state["repair_history"][-1].update(
            {
                "completed_at": _now(),
                "output_warnings": repaired_report.get("warnings", []),
                "input_score": _diagnostic_score(current_report),
                "output_score": _diagnostic_score(repaired_report),
                "accepted": accepted,
                "reason": reason,
            }
        )
        if not accepted:
            break
        current = repaired
        current_report = repaired_report
        if not _should_repair(current_report.get("warnings", [])):
            break

    return current, current_report


def _should_repair(warnings: list[str]) -> bool:
    if not warnings:
        return False
    repair_tokens = (
        "缺少设计规约",
        "模块",
        "接口",
        "广州塔",
        "比例",
        "玻璃比例偏高",
        "灯光比例偏低",
        "parts 数偏少",
        "performance_budget",
        "完整预览方块数超过",
        "动态效果",
        "标记为 animated",
        "中央空洞",
    )
    return any(any(token in warning for token in repair_tokens) for warning in warnings)


def _repair_acceptance(before: dict[str, Any], after: dict[str, Any]) -> tuple[bool, str]:
    before_score = _diagnostic_score(before)
    after_score = _diagnostic_score(after)
    if after_score["blocking"] > before_score["blocking"]:
        return False, "rejected: blocking diagnostics increased"
    if after_score["score"] > before_score["score"]:
        return False, "rejected: diagnostic score worsened"
    if after_score["score"] < before_score["score"]:
        return True, "accepted: diagnostics improved"
    return True, "accepted: diagnostics did not worsen"


def _diagnostic_score(report: dict[str, Any]) -> dict[str, int]:
    warnings = report.get("warnings") or []
    module_report = report.get("design_spec") or {}
    blueprint = report.get("design_blueprint") or {}
    interface_checks = blueprint.get("interface_checks") or module_report.get("interface_checks") or []
    stage_checks = blueprint.get("stage_checks") or module_report.get("stage_checks") or []

    warning_count = len(warnings)
    blocking = 0
    blocking += 0 if module_report.get("stitch_ready") else 1
    blocking += len(module_report.get("missing_bbox") or [])
    blocking += len(module_report.get("duplicate_names") or [])
    blocking += sum(1 for check in interface_checks if not check.get("ok"))
    blocking += sum(1 for check in stage_checks if not check.get("executable"))

    repair_warning_count = sum(1 for warning in warnings if _should_repair([warning]))
    return {
        "score": blocking * 10 + repair_warning_count * 3 + warning_count,
        "blocking": blocking,
        "repair_warnings": repair_warning_count,
        "warnings": warning_count,
    }


def _ensure_project_placement(project_id: str, state: dict[str, Any]) -> dict[str, Any]:
    if state.get("placement"):
        return state["placement"]
    if not state.get("plan"):
        raise HTTPException(status_code=409, detail="project has no generated plan")
    placement = _allocate_placement(project_id, BuildPlan.model_validate(state["plan"]))
    state["placement"] = placement
    upsert_project_placement(
        project_id=project_id,
        placement=placement,
        project_name=(state.get("plan") or {}).get("name"),
        pasted=bool(state.get("rcon")),
    )
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
    for other in list_placements(active_only=True):
        if other.get("project_id") == project_id or not other.get("bounds"):
            continue
        other_bounds = _expanded_bounds(other["bounds"], other.get("margin", 0))
        if _bounds_overlap(current, other_bounds):
            return True
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


def _rcon_command(command: str) -> str:
    rcon = MinecraftRcon(
        RconConfig(
            host=settings.rcon_host,
            port=settings.rcon_port,
            password=settings.rcon_password,
        )
    )
    return rcon.command(command)


def _require_registry_placement(project_id: str) -> dict[str, Any]:
    placement = get_project_placement(project_id)
    if not placement:
        raise HTTPException(status_code=404, detail="placement not found")
    if placement.get("active") is False:
        raise HTTPException(status_code=409, detail="placement is archived")
    return placement


def _bounds_volume(bounds: dict[str, int]) -> int:
    return (
        max(0, bounds["max_x"] - bounds["min_x"] + 1)
        * max(0, bounds["max_y"] - bounds["min_y"] + 1)
        * max(0, bounds["max_z"] - bounds["min_z"] + 1)
    )


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
