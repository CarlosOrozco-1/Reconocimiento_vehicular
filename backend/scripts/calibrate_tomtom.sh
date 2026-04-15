#!/usr/bin/env bash
set -euo pipefail

LIMIT="${1:-200}"
ONLY_ROUTE="${2:-}"

if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if [ -x "../.venv/bin/python3" ]; then
  PYTHON_CMD="../.venv/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
else
  printf "python3 not found.\n" >&2
  exit 1
fi

if [ -n "$ONLY_ROUTE" ]; then
  "$PYTHON_CMD" -m src.data.calibrate_tomtom --limit "$LIMIT" --only-route "$ONLY_ROUTE"
else
  "$PYTHON_CMD" -m src.data.calibrate_tomtom --limit "$LIMIT"
fi
