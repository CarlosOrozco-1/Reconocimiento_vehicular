#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env.docker}"

if [ ! -f "$ENV_FILE" ]; then
  echo "Env file not found: $ENV_FILE" >&2
  exit 1
fi

if [ $# -lt 1 ]; then
  echo "Usage: $0 <dump_file>" >&2
  exit 1
fi

DUMP_FILE="$1"
if [ ! -f "$DUMP_FILE" ]; then
  echo "Dump file not found: $DUMP_FILE" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

docker compose --env-file "$ENV_FILE" exec -T db \
  pg_restore -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" --clean --if-exists < "$DUMP_FILE"

echo "Restore completed from: $DUMP_FILE"
