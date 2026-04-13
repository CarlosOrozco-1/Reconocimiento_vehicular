from __future__ import annotations

import json
from datetime import datetime

from src.api.db import get_connection
from src.ingestion.models import FlowRecord


def start_run(source_name: str) -> int:
    query = """
        INSERT INTO ingestion_runs (source_name, status)
        VALUES (%s, 'running')
        RETURNING id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (source_name,))
            run_id = int(cur.fetchone()["id"])
        conn.commit()
    return run_id


def finish_run(run_id: int, records_read: int, records_loaded: int, error_message: str | None) -> None:
    status = "success" if error_message is None else "failed"
    query = """
        UPDATE ingestion_runs
        SET
            status = %s,
            records_read = %s,
            records_loaded = %s,
            error_message = %s,
            finished_at = NOW()
        WHERE id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (status, records_read, records_loaded, error_message, run_id))
        conn.commit()


def insert_raw_records(records: list[FlowRecord]) -> int:
    query = """
        INSERT INTO traffic_flow_raw (
            source_name,
            route_code,
            observed_at,
            interval_min,
            motorcycle_count,
            light_vehicle_count,
            heavy_vehicle_count,
            total_count,
            payload
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
        ON CONFLICT (source_name, route_code, observed_at) DO UPDATE SET
            interval_min = EXCLUDED.interval_min,
            motorcycle_count = EXCLUDED.motorcycle_count,
            light_vehicle_count = EXCLUDED.light_vehicle_count,
            heavy_vehicle_count = EXCLUDED.heavy_vehicle_count,
            total_count = EXCLUDED.total_count,
            payload = EXCLUDED.payload
    """

    loaded = 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            for record in records:
                cur.execute(
                    query,
                    (
                        record.source_name,
                        record.route_code,
                        record.observed_at,
                        record.interval_min,
                        record.motorcycle_count,
                        record.light_vehicle_count,
                        record.heavy_vehicle_count,
                        record.total_count,
                        json.dumps(record.payload or {}),
                    ),
                )
                loaded += 1
        conn.commit()
    return loaded


def _ensure_count_point(route_code: str) -> int | None:
    select_query = """
        SELECT cp.id
        FROM count_points cp
        INNER JOIN road_segments rs ON rs.id = cp.road_segment_id
        WHERE rs.route_code = %s
        ORDER BY cp.id
        LIMIT 1
    """
    insert_query = """
        INSERT INTO count_points (name, road_segment_id, direction, status, geom)
        SELECT
            CONCAT('auto_', rs.route_code),
            rs.id,
            'bidirectional',
            'active',
            ST_LineInterpolatePoint(rs.geom, 0.5)
        FROM road_segments rs
        WHERE rs.route_code = %s
        RETURNING id
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(select_query, (route_code,))
            row = cur.fetchone()
            if row:
                return int(row["id"])

            cur.execute(insert_query, (route_code,))
            inserted = cur.fetchone()
        conn.commit()

    if inserted is None:
        return None
    return int(inserted["id"])


def _hour_bucket(value: datetime) -> tuple[str, int]:
    return value.date().isoformat(), value.hour


def upsert_hourly_agg_from_raw(records: list[FlowRecord]) -> int:
    upsert_query = """
        INSERT INTO traffic_hourly_agg (
            count_point_id,
            date,
            hour,
            motorcycle_count,
            light_vehicle_count,
            heavy_vehicle_count,
            total_count,
            updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (count_point_id, date, hour)
        DO UPDATE SET
            motorcycle_count = EXCLUDED.motorcycle_count,
            light_vehicle_count = EXCLUDED.light_vehicle_count,
            heavy_vehicle_count = EXCLUDED.heavy_vehicle_count,
            total_count = EXCLUDED.total_count,
            updated_at = NOW()
    """

    grouped: dict[tuple[int, str, int], dict[str, int]] = {}
    for record in records:
        count_point_id = _ensure_count_point(record.route_code)
        if count_point_id is None:
            continue
        date_str, hour = _hour_bucket(record.observed_at)
        key = (count_point_id, date_str, hour)
        if key not in grouped:
            grouped[key] = {
                "motorcycle": 0,
                "light": 0,
                "heavy": 0,
                "total": 0,
            }
        grouped[key]["motorcycle"] += record.motorcycle_count
        grouped[key]["light"] += record.light_vehicle_count
        grouped[key]["heavy"] += record.heavy_vehicle_count
        grouped[key]["total"] += record.total_count

    written = 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            for (count_point_id, date_str, hour), values in grouped.items():
                cur.execute(
                    upsert_query,
                    (
                        count_point_id,
                        date_str,
                        hour,
                        values["motorcycle"],
                        values["light"],
                        values["heavy"],
                        values["total"],
                    ),
                )
                written += 1
        conn.commit()
    return written
