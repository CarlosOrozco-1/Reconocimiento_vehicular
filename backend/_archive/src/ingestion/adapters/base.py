from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from src.ingestion.models import FlowRecord


class SourceAdapter(Protocol):
    source_name: str

    def read_records(self) -> Iterable[FlowRecord]:
        ...
