from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from src.ingestion.models import FlowRecord


class CsvSourceAdapter:
    def __init__(self, source_name: str, file_path: Path) -> None:
        self.source_name = source_name
        self.file_path = file_path

    def read_records(self) -> list[FlowRecord]:
        if not self.file_path.exists():
            raise FileNotFoundError(f"CSV source not found: {self.file_path}")

        records: list[FlowRecord] = []
        with self.file_path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                route_code = str(row.get("route_code", "")).strip()
                if not route_code:
                    continue

                observed_at = datetime.fromisoformat(str(row.get("observed_at", "")).strip())
                interval_min = int(row.get("interval_min", 60) or 60)
                motorcycle_count = int(row.get("motorcycle_count", 0) or 0)
                light_vehicle_count = int(row.get("light_vehicle_count", 0) or 0)
                heavy_vehicle_count = int(row.get("heavy_vehicle_count", 0) or 0)
                total_count = int(
                    row.get(
                        "total_count",
                        motorcycle_count + light_vehicle_count + heavy_vehicle_count,
                    )
                    or 0
                )

                payload = {k: v for k, v in row.items()}
                records.append(
                    FlowRecord(
                        source_name=self.source_name,
                        route_code=route_code,
                        observed_at=observed_at,
                        interval_min=interval_min,
                        motorcycle_count=motorcycle_count,
                        light_vehicle_count=light_vehicle_count,
                        heavy_vehicle_count=heavy_vehicle_count,
                        total_count=total_count,
                        payload=payload,
                    )
                )
        return records
