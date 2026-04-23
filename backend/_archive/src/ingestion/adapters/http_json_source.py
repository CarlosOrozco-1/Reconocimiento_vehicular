from __future__ import annotations

from datetime import datetime
from typing import Any

import requests

from src.ingestion.models import FlowRecord


class HttpJsonSourceAdapter:
    def __init__(self, source_name: str, endpoint: str, timeout_sec: int = 20) -> None:
        self.source_name = source_name
        self.endpoint = endpoint
        self.timeout_sec = timeout_sec

    def read_records(self) -> list[FlowRecord]:
        response = requests.get(self.endpoint, timeout=self.timeout_sec)
        response.raise_for_status()
        data: Any = response.json()

        if not isinstance(data, list):
            raise ValueError("Expected JSON array for traffic source")

        records: list[FlowRecord] = []
        for item in data:
            if not isinstance(item, dict):
                continue

            route_code = str(item.get("route_code", "")).strip()
            observed_at_raw = str(item.get("observed_at", "")).strip()
            if not route_code or not observed_at_raw:
                continue

            observed_at = datetime.fromisoformat(observed_at_raw)
            interval_min = int(item.get("interval_min", 60) or 60)
            motorcycle_count = int(item.get("motorcycle_count", 0) or 0)
            light_vehicle_count = int(item.get("light_vehicle_count", 0) or 0)
            heavy_vehicle_count = int(item.get("heavy_vehicle_count", 0) or 0)
            total_count = int(
                item.get(
                    "total_count",
                    motorcycle_count + light_vehicle_count + heavy_vehicle_count,
                )
                or 0
            )

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
                    payload=item,
                )
            )
        return records
