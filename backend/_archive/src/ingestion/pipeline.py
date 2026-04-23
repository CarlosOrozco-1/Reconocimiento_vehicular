from __future__ import annotations

from dataclasses import dataclass

from src.ingestion.adapters.base import SourceAdapter
from src.ingestion.repository import (
    finish_run,
    insert_raw_records,
    start_run,
    upsert_hourly_agg_from_raw,
)


@dataclass(frozen=True)
class IngestionResult:
    source_name: str
    records_read: int
    raw_loaded: int
    hourly_upserts: int


def run_ingestion(adapter: SourceAdapter) -> IngestionResult:
    run_id = start_run(adapter.source_name)
    records_read = 0
    raw_loaded = 0
    hourly_upserts = 0

    try:
        records = list(adapter.read_records())
        records_read = len(records)
        raw_loaded = insert_raw_records(records)
        hourly_upserts = upsert_hourly_agg_from_raw(records)
        finish_run(
            run_id=run_id,
            records_read=records_read,
            records_loaded=raw_loaded,
            error_message=None,
        )
    except Exception as exc:
        finish_run(
            run_id=run_id,
            records_read=records_read,
            records_loaded=raw_loaded,
            error_message=str(exc),
        )
        raise

    return IngestionResult(
        source_name=adapter.source_name,
        records_read=records_read,
        raw_loaded=raw_loaded,
        hourly_upserts=hourly_upserts,
    )
