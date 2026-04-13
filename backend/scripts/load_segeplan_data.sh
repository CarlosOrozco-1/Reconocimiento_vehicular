#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-all}"

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

"$PYTHON_CMD" -m src.data.load_segeplan --mode "$MODE"
