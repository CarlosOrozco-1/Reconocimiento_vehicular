#!/usr/bin/env bash
set -euo pipefail

python -m src.main --source data/raw/videos/test.mp4 --output outputs/csv/events.csv --video-output outputs/videos/annotated.mp4
