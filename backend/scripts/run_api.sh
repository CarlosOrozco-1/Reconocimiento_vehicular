#!/usr/bin/env bash
set -euo pipefail

if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

HOST="${API_HOST:-0.0.0.0}"
PORT="${API_PORT:-8000}"

if [ -x "../.venv/bin/uvicorn" ]; then
  UVICORN_CMD="../.venv/bin/uvicorn"
elif command -v uvicorn >/dev/null 2>&1; then
  UVICORN_CMD="uvicorn"
else
  printf "uvicorn not found. Activate virtualenv or install dependencies.\n" >&2
  exit 1
fi

"$UVICORN_CMD" src.api.main:app --host "$HOST" --port "$PORT" --reload
