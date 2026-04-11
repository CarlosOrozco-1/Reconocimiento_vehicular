#!/usr/bin/env bash
set -euo pipefail

podman-compose -f podman-compose.yml up -d
