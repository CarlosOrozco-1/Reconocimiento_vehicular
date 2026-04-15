#!/usr/bin/env bash
set -euo pipefail

OUTPUT_PATH="${1:-outputs/csv/ine_vehicle_type_mix.csv}"

if [ -x "../.venv/bin/python3" ]; then
  PYTHON_CMD="../.venv/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
else
  printf "python3 not found.\n" >&2
  exit 1
fi

"$PYTHON_CMD" -m src.data.fetch_ine_vehicle_mix --output "$OUTPUT_PATH"
