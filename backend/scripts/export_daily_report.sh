#!/usr/bin/env bash
set -euo pipefail

python -c "from pathlib import Path; from src.analytics.daily_report import generate_daily_counts; generate_daily_counts(Path('outputs/csv/events.csv'), Path('outputs/csv/daily_counts.csv'))"
