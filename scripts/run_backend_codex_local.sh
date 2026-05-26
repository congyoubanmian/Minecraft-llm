#!/usr/bin/env bash
set -euo pipefail

export PLANNER_MODE="${PLANNER_MODE:-codex}"
export BOT_URL="${BOT_URL:-http://localhost:3001}"
export SCHEMATIC_DIR="${SCHEMATIC_DIR:-$(pwd)/server/plugins/FastAsyncWorldEdit/schematics}"
export UPLOAD_DIR="${UPLOAD_DIR:-$(pwd)/backend/uploads}"
export GENERATED_PLAN_DIR="${GENERATED_PLAN_DIR:-$(pwd)/backend/generated_plans}"
export PASTE_ENABLED="${PASTE_ENABLED:-true}"

. .venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000
