#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env.docker}"

if [ ! -f "$ENV_FILE" ]; then
  echo "Env file not found: $ENV_FILE" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

BACKUP_DIR="${BACKUP_DIR:-$ROOT_DIR/backups}"
mkdir -p "$BACKUP_DIR"

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_FILE="${BACKUP_DIR}/traffic_gt_${STAMP}.dump"

docker compose --env-file "$ENV_FILE" exec -T db \
  pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -Fc > "$OUT_FILE"

echo "Backup created: $OUT_FILE"
