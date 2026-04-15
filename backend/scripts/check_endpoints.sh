#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"

printf "Checking %s\n" "$BASE_URL"
curl -s "$BASE_URL/health"
printf "\n"
curl -s "$BASE_URL/routes/main?limit=3"
printf "\n"
curl -s "$BASE_URL/departments?limit=3"
printf "\n"
curl -s "$BASE_URL/routes/CA-2/summary?include_live=true"
printf "\n"
curl -s "$BASE_URL/monitor/worker/status"
printf "\n"
curl -s "$BASE_URL/monitor/routes"
printf "\n"
