#!/usr/bin/env bash
set -euo pipefail

if command -v podman >/dev/null 2>&1; then
  if command -v podman-compose >/dev/null 2>&1; then
    podman-compose -f podman-compose.yml up -d
  else
    podman compose -f podman-compose.yml up -d
  fi
elif command -v distrobox-host-exec >/dev/null 2>&1; then
  distrobox-host-exec podman-compose -f podman-compose.yml up -d
else
  printf "No podman runtime available\n" >&2
  exit 1
fi
