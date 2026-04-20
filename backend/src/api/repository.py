from __future__ import annotations

import json
from datetime import date

from src.api.db import get_connection


def fetch_routes_geojson(limit: int = 500) -> dict:
    # ST_Simplify reduce la cantidad de puntos por ruta para mejorar el render en Leaflet.
    # La tolerancia 0.0003 grados equivale a ~33 metros, suficiente para rutas nacionales.
    # preserve_collapsed=true conserva geometrias muy cortas que de otro modo desaparecerian.
    query = """
        SELECT
            route_code,
            MIN(name) AS name,
            ST_AsGeoJSON(
                ST_Multi(
                    ST_SimplifyPreserveTopology(
                        ST_LineMerge(
                            ST_UnaryUnion(
                                ST_Collect(geom)
                            )
                        ),
                        0.0003
                    )
                )
            ) AS geom_json,
            ROUND(SUM(ST_Length(geom::geography)) / 1000)::int AS length_km
        FROM road_segments
        GROUP BY route_code
        ORDER BY route_code
        LIMIT %s
    """
    features: list[dict] = []
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            rows = cur.fetchall()

    for row in rows:
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "route_code": row["route_code"],
                    "name": row["name"],
                    "length_km": row["length_km"],
                },
                "geometry": json.loads(row["geom_json"]),
            }
        )

    return {"type": "FeatureCollection", "features": features}


def fetch_route_catalog(limit: int = 500) -> list[dict]:
    query = """
        SELECT
            route_code,
            MIN(name) AS name,
            COUNT(*) AS segment_count,
            ROUND(SUM(ST_Length(geom::geography)) / 1000)::int AS length_km
        FROM road_segments
        GROUP BY route_code
        ORDER BY route_code
        LIMIT %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            rows = cur.fetchall()
    return rows


def fetch_departments_geojson(limit: int = 500) -> dict:
    query = """
        SELECT
            id,
            code,
            name,
            ST_AsGeoJSON(geom) AS geom_json
        FROM departments
        ORDER BY id
        LIMIT %s
    """
    features: list[dict] = []
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            rows = cur.fetchall()

    for row in rows:
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "id": row["id"],
                    "code": row["code"],
                    "name": row["name"],
                },
                "geometry": json.loads(row["geom_json"]),
            }
        )

    return {"type": "FeatureCollection", "features": features}


def fetch_route_departments(route_code: str) -> list[dict]:
    query = """
        SELECT DISTINCT
            rs.route_code,
            rs.name AS route_name,
            d.code AS department_code,
            d.name AS department_name
        FROM road_segments rs
        INNER JOIN departments d ON ST_Intersects(rs.geom, d.geom)
        WHERE rs.route_code = %s
        ORDER BY d.name
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (route_code,))
            rows = cur.fetchall()
    return rows


def fetch_route_summary(route_code: str) -> dict:
    query = """
        SELECT
            rs.route_code,
            MIN(rs.name) AS route_name,
            COALESCE(ROUND(AVG(tha.total_count))::int, 0) AS normal_flow,
            COALESCE(MAX(tha.total_count), 0) AS peak_flow,
            (
                ARRAY_AGG(tha.hour ORDER BY tha.total_count DESC NULLS LAST)
            )[1] AS peak_hour
        FROM road_segments rs
        LEFT JOIN count_points cp ON cp.road_segment_id = rs.id
        LEFT JOIN traffic_hourly_agg tha ON tha.count_point_id = cp.id
        WHERE rs.route_code = %s
        GROUP BY rs.route_code
        LIMIT 1
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (route_code,))
            row = cur.fetchone()

    if not row:
        return {
            "route_code": route_code,
            "route_name": route_code,
            "normal_flow": 0,
            "peak_flow": 0,
            "peak_hour": None,
        }
    return row


def fetch_route_probe_points(route_code: str) -> list[dict]:
    query = """
        WITH segments AS (
            SELECT (ST_Dump(ST_CollectionExtract(geom, 2))).geom AS line
            FROM road_segments
            WHERE route_code = %s
        ),
        ranked AS (
            SELECT line
            FROM segments
            WHERE line IS NOT NULL AND ST_NPoints(line) > 1
            ORDER BY ST_Length(line::geography) DESC
            LIMIT 40
        ),
        fractions AS (
            SELECT unnest(ARRAY[0.08, 0.2, 0.35, 0.5, 0.65, 0.8, 0.92]) AS fraction
        ),
        sampled AS (
            SELECT
                fraction,
                ST_LineInterpolatePoint(line, fraction) AS pt,
                ST_Length(line::geography) AS line_len
            FROM ranked
            CROSS JOIN fractions
        )
        SELECT
            fraction,
            ST_Y(pt) AS latitude,
            ST_X(pt) AS longitude
        FROM sampled
        ORDER BY line_len DESC, fraction
        LIMIT 120
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (route_code,))
            rows = cur.fetchall()
    return rows


def fetch_route_probe_points_expanded(
    route_code: str,
    max_segments: int = 120,
    points_per_segment: int = 12,
) -> list[dict]:
    query = """
        WITH segments AS (
            SELECT (ST_Dump(ST_CollectionExtract(geom, 2))).geom AS line
            FROM road_segments
            WHERE route_code = %s
        ),
        ranked AS (
            SELECT
                line,
                ST_Length(line::geography) AS line_len,
                ROW_NUMBER() OVER (ORDER BY ST_Length(line::geography) DESC) AS rn
            FROM segments
            WHERE line IS NOT NULL AND ST_NPoints(line) > 1
        ),
        selected AS (
            SELECT line, line_len
            FROM ranked
            WHERE rn <= %s
        ),
        fractions AS (
            SELECT (g::double precision / (%s + 1)::double precision) AS fraction
            FROM generate_series(1, %s) AS g
            UNION ALL SELECT 0.01
            UNION ALL SELECT 0.99
        ),
        sampled AS (
            SELECT
                fraction,
                ST_LineInterpolatePoint(line, fraction) AS pt,
                line_len
            FROM selected
            CROSS JOIN fractions
        )
        SELECT
            fraction,
            ST_Y(pt) AS latitude,
            ST_X(pt) AS longitude,
            line_len
        FROM sampled
        ORDER BY line_len DESC, fraction
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (route_code, max_segments, points_per_segment, points_per_segment))
            rows = cur.fetchall()
    return rows


def fetch_route_codes(limit: int = 500) -> list[str]:
    query = """
        SELECT route_code
        FROM road_segments
        GROUP BY route_code
        ORDER BY route_code
        LIMIT %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            rows = cur.fetchall()
    return [str(row["route_code"]) for row in rows]


def fetch_saved_live_probe(route_code: str) -> dict | None:
    query = """
        SELECT route_code, latitude, longitude, status, message, updated_at, successful_at
        FROM route_live_probe_points
        WHERE route_code = %s
        LIMIT 1
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (route_code,))
            row = cur.fetchone()
    return row


def upsert_saved_live_probe(
    route_code: str,
    status: str,
    message: str,
    latitude: float | None,
    longitude: float | None,
) -> None:
    query = """
        INSERT INTO route_live_probe_points (
            route_code,
            latitude,
            longitude,
            status,
            message,
            updated_at,
            successful_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            NOW(),
            CASE WHEN %s = 'ok' THEN NOW() ELSE NULL END
        )
        ON CONFLICT (route_code)
        DO UPDATE SET
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude,
            status = EXCLUDED.status,
            message = EXCLUDED.message,
            updated_at = NOW(),
            successful_at = CASE
                WHEN EXCLUDED.status = 'ok' THEN NOW()
                ELSE route_live_probe_points.successful_at
            END
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (route_code, latitude, longitude, status, message, status))
        conn.commit()


def fetch_live_probe_status(limit: int = 500) -> list[dict]:
    query = """
        SELECT route_code, status, message, latitude, longitude, updated_at, successful_at
        FROM route_live_probe_points
        ORDER BY route_code
        LIMIT %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            rows = cur.fetchall()
    return rows


def ensure_monitored_routes_seed(limit: int = 10) -> int:
    route_codes = fetch_route_codes(limit=limit)
    query = """
        INSERT INTO monitored_routes (route_code, enabled)
        VALUES (%s, TRUE)
        ON CONFLICT (route_code) DO NOTHING
    """
    inserted = 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            for route_code in route_codes:
                cur.execute(query, (route_code,))
                inserted += 1
        conn.commit()
    return inserted


def fetch_monitored_routes(only_enabled: bool = False) -> list[dict]:
    where_clause = "WHERE enabled = TRUE" if only_enabled else ""
    query = f"""
        SELECT route_code, enabled, created_at, updated_at
        FROM monitored_routes
        {where_clause}
        ORDER BY route_code
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    return rows


def add_monitored_route(route_code: str) -> None:
    query = """
        INSERT INTO monitored_routes (route_code, enabled, created_at, updated_at)
        VALUES (%s, TRUE, NOW(), NOW())
        ON CONFLICT (route_code)
        DO UPDATE SET enabled = TRUE, updated_at = NOW()
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (route_code,))
        conn.commit()


def remove_monitored_route(route_code: str) -> None:
    query = "DELETE FROM monitored_routes WHERE route_code = %s"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (route_code,))
        conn.commit()


def set_worker_state(worker_name: str, status: str, message: str) -> None:
    query = """
        INSERT INTO worker_status (worker_name, status, message, updated_at)
        VALUES (%s, %s, %s, NOW())
        ON CONFLICT (worker_name)
        DO UPDATE SET status = EXCLUDED.status, message = EXCLUDED.message, updated_at = NOW()
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (worker_name, status, message))
        conn.commit()


def touch_worker_run(worker_name: str) -> None:
    query = """
        UPDATE worker_status
        SET last_run_at = NOW(), updated_at = NOW()
        WHERE worker_name = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (worker_name,))
        conn.commit()


def mark_worker_request_result(worker_name: str, ok: bool) -> None:
    if ok:
        query = """
            UPDATE worker_status
            SET requests_ok = requests_ok + 1, last_success_at = NOW(), updated_at = NOW()
            WHERE worker_name = %s
        """
    else:
        query = """
            UPDATE worker_status
            SET requests_error = requests_error + 1, updated_at = NOW()
            WHERE worker_name = %s
        """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (worker_name,))
        conn.commit()


def fetch_worker_status(worker_name: str) -> dict:
    query = """
        SELECT worker_name, status, last_run_at, last_success_at, requests_ok, requests_error, message, updated_at
        FROM worker_status
        WHERE worker_name = %s
        LIMIT 1
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (worker_name,))
            row = cur.fetchone()
    if row:
        return row
    return {
        "worker_name": worker_name,
        "status": "unknown",
        "last_run_at": None,
        "last_success_at": None,
        "requests_ok": 0,
        "requests_error": 0,
        "message": "Worker status row not found",
        "updated_at": None,
    }


def insert_worker_request_log(
    worker_name: str,
    route_code: str,
    request_url: str,
    status_code: int | None,
    duration_ms: int,
    result: str,
    error_message: str | None,
) -> None:
    query = """
        INSERT INTO worker_request_log (
            worker_name,
            route_code,
            request_url,
            status_code,
            duration_ms,
            result,
            error_message
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (worker_name, route_code, request_url, status_code, duration_ms, result, error_message),
            )
        conn.commit()


def fetch_worker_request_logs(minutes: int = 60, limit: int = 200) -> list[dict]:
    query = """
        SELECT
            id,
            worker_name,
            route_code,
            request_url,
            status_code,
            duration_ms,
            result,
            error_message,
            created_at
        FROM worker_request_log
        WHERE created_at >= NOW() - (%s::text || ' minutes')::interval
        ORDER BY created_at DESC
        LIMIT %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (minutes, limit))
            rows = cur.fetchall()
    return rows


def insert_route_live_history(
    route_code: str,
    current_speed_kph: int | None,
    free_flow_speed_kph: int | None,
    current_travel_time_sec: int | None,
    free_flow_travel_time_sec: int | None,
    confidence: float | None,
    road_closure: bool | None,
    afluencia_pct: float | None,
) -> None:
    query = """
        INSERT INTO route_live_history (
            route_code,
            current_speed_kph,
            free_flow_speed_kph,
            current_travel_time_sec,
            free_flow_travel_time_sec,
            confidence,
            road_closure,
            afluencia_pct,
            source
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'tomtom')
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (
                    route_code,
                    current_speed_kph,
                    free_flow_speed_kph,
                    current_travel_time_sec,
                    free_flow_travel_time_sec,
                    confidence,
                    road_closure,
                    afluencia_pct,
                ),
            )
        conn.commit()


def fetch_route_live_history(route_code: str, hours: int = 24, limit: int = 500) -> list[dict]:
    query = """
        SELECT
            route_code,
            observed_at,
            current_speed_kph,
            free_flow_speed_kph,
            afluencia_pct,
            road_closure,
            confidence
        FROM route_live_history
        WHERE route_code = %s
          AND observed_at >= NOW() - (%s::text || ' hours')::interval
        ORDER BY observed_at ASC
        LIMIT %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (route_code, hours, limit))
            rows = cur.fetchall()
    return rows


def fetch_peak_hours(from_date: date | None, to_date: date | None) -> list[dict]:
    date_filters = []
    params: list[object] = []

    if from_date:
        date_filters.append("tha.date >= %s")
        params.append(from_date)
    if to_date:
        date_filters.append("tha.date <= %s")
        params.append(to_date)

    where_clause = f"WHERE {' AND '.join(date_filters)}" if date_filters else ""

    query = f"""
        WITH route_hourly AS (
            SELECT
                rs.route_code,
                rs.name AS route_name,
                tha.hour,
                AVG(tha.total_count) AS avg_flow,
                ROW_NUMBER() OVER (
                    PARTITION BY rs.route_code
                    ORDER BY AVG(tha.total_count) DESC
                ) AS rn
            FROM traffic_hourly_agg tha
            INNER JOIN count_points cp ON cp.id = tha.count_point_id
            INNER JOIN road_segments rs ON rs.id = cp.road_segment_id
            {where_clause}
            GROUP BY rs.route_code, rs.name, tha.hour
        )
        SELECT route_code, route_name, hour AS peak_hour, ROUND(avg_flow)::int AS avg_flow
        FROM route_hourly
        WHERE rn = 1
        ORDER BY avg_flow DESC
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
    return rows
