from __future__ import annotations

import json
from datetime import date

from src.api.db import get_connection


def fetch_routes_geojson(limit: int = 500) -> dict:
    query = """
        SELECT
            id,
            route_code,
            name,
            ST_AsGeoJSON(geom) AS geom_json
        FROM road_segments
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
                    "route_code": row["route_code"],
                    "name": row["name"],
                },
                "geometry": json.loads(row["geom_json"]),
            }
        )

    return {"type": "FeatureCollection", "features": features}


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
