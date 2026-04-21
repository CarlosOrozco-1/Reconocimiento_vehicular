#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
VENV_DIR="$ROOT_DIR/.venv"

PYTHON_BIN="${PYTHON_BIN:-python3}"
INSTALL_FRONTEND="${INSTALL_FRONTEND:-true}"
RUN_DB_SETUP="${RUN_DB_SETUP:-true}"
RUN_SEGEPLAN_LOAD="${RUN_SEGEPLAN_LOAD:-true}"
RUN_TOMTOM_SCAN="${RUN_TOMTOM_SCAN:-false}"
DB_CONTAINER="${DB_CONTAINER:-traffic_gt_db}"

log() {
  printf "[bootstrap] %s\n" "$1"
}

fail() {
  printf "[bootstrap][error] %s\n" "$1" >&2
  exit 1
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    fail "Missing command: $1"
  fi
}

run_db_migrations() {
  local -a scripts=(
    "002_postgis_extensions.sql"
    "003_tables_traffic.sql"
    "004_indexes.sql"
    "005_seed_routes.sql"
    "006_seed_departments.sql"
    "007_ingestion_tables.sql"
    "008_ingestion_indexes.sql"
    "009_alter_road_segments_geom.sql"
    "010_tomtom_probe_cache.sql"
    "011_worker_monitoring.sql"
  )

  log "Starting PostGIS service"
  (cd "$BACKEND_DIR" && ./scripts/db_up.sh)

  log "Waiting for database readiness"
  local retries=30
  local ready=false
  for _ in $(seq 1 "$retries"); do
    if podman exec "$DB_CONTAINER" pg_isready -U traffic_user -d traffic_gt >/dev/null 2>&1; then
      ready=true
      break
    fi
    sleep 2
  done

  if [ "$ready" != "true" ]; then
    fail "Database container '$DB_CONTAINER' did not become ready"
  fi

  log "Applying SQL migrations"
  for sql in "${scripts[@]}"; do
    podman exec "$DB_CONTAINER" psql -U traffic_user -d traffic_gt -f "/docker-entrypoint-initdb.d/$sql" >/dev/null
  done
}

install_backend() {
  log "Preparing Python virtual environment"
  if [ ! -d "$VENV_DIR" ]; then
    "$PYTHON_BIN" -m venv "$VENV_DIR"
  fi

  "$VENV_DIR/bin/python3" -m ensurepip --upgrade >/dev/null
  "$VENV_DIR/bin/python3" -m pip install --upgrade pip >/dev/null

  log "Installing backend dependencies"
  "$VENV_DIR/bin/pip" install -r "$BACKEND_DIR/requirements.txt"
}

ensure_backend_env() {
  if [ ! -f "$BACKEND_DIR/.env" ]; then
    log "Creating backend/.env from template"
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
  fi
}

load_segeplan_layers() {
  log "Loading SEGEPLAN layers (departments/routes)"
  (cd "$BACKEND_DIR" && ./scripts/load_segeplan_data.sh all)
}

run_tomtom_scan() {
  log "Running expanded TomTom coverage scan"
  (cd "$BACKEND_DIR" && ./scripts/scan_tomtom_coverage.sh 50)
}

install_frontend() {
  if [ "$INSTALL_FRONTEND" != "true" ]; then
    log "Skipping frontend installation (INSTALL_FRONTEND=false)"
    return
  fi

  if ! command -v npm >/dev/null 2>&1; then
    log "npm not found, skipping frontend install"
    return
  fi

  log "Installing frontend dependencies"
  (cd "$FRONTEND_DIR" && npm install)
}

main() {
  [ -d "$BACKEND_DIR" ] || fail "backend directory not found"
  [ -d "$FRONTEND_DIR" ] || fail "frontend directory not found"

  require_cmd "$PYTHON_BIN"

  install_backend
  ensure_backend_env

  if [ "$RUN_DB_SETUP" = "true" ]; then
    require_cmd podman
    run_db_migrations
  else
    log "Skipping DB setup (RUN_DB_SETUP=false)"
  fi

  if [ "$RUN_SEGEPLAN_LOAD" = "true" ]; then
    load_segeplan_layers
  else
    log "Skipping SEGEPLAN load (RUN_SEGEPLAN_LOAD=false)"
  fi

  if [ "$RUN_TOMTOM_SCAN" = "true" ]; then
    run_tomtom_scan
  else
    log "Skipping TomTom scan (RUN_TOMTOM_SCAN=false)"
  fi

  install_frontend

  log "Bootstrap completed"
  printf "\nNext steps:\n"
  printf "1) Backend: cd %s && ./scripts/run_api.sh\n" "$BACKEND_DIR"
  printf "2) Frontend: cd %s && npm run start\n" "$FRONTEND_DIR"
}

main "$@"
