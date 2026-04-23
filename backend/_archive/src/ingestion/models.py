from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class FlowRecord:
    source_name: str
    route_code: str
    observed_at: datetime
    interval_min: int
    motorcycle_count: int
    light_vehicle_count: int
    heavy_vehicle_count: int
    total_count: int
    payload: dict[str, Any] | None = None
