from __future__ import annotations

import csv
from pathlib import Path

EVENT_HEADERS = [
    "timestamp",
    "track_id",
    "class_name",
    "direction",
    "crossing_line_id",
    "confidence",
]


def ensure_events_csv(events_csv: Path) -> None:
    events_csv.parent.mkdir(parents=True, exist_ok=True)
    if events_csv.exists():
        return
    with events_csv.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(EVENT_HEADERS)


def append_event(
    events_csv: Path,
    timestamp: str,
    track_id: int,
    class_name: str,
    direction: str,
    crossing_line_id: str,
    confidence: float,
) -> None:
    with events_csv.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                timestamp,
                track_id,
                class_name,
                direction,
                crossing_line_id,
                f"{confidence:.4f}",
            ]
        )
