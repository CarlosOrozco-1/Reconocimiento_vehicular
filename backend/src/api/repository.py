from __future__ import annotations

import json
from datetime import date

from src.api.db import get_connection


def fetch_routes_geojson(limit: int = 500) -> dict:
    """
    Obtiene el GeoJSON de rutas principales desde road_segments.
    ST_Simplify reduce puntos por ruta para mejor rendimiento en Leaflet.
    Tolerancia 0.0003 grados (~33m), suficiente para rutas nacionales.
    ST_LineMerge une segmentos contiguos de la misma ruta en una sola linea.
    """
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
    """
    Retorna el catalogo de rutas con codigo, nombre, cantidad de segmentos y longitud total.
    Se usa para el selector de rutas del frontend.
    """
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
    """
    Obtiene el GeoJSON de los departamentos de Guatemala desde la tabla departments.
    Se usa como capa cartografica de fondo en el mapa.
    """
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
    """
    Retorna los departamentos que intersectan con una ruta dada.
    Usa ST_Intersects para el join espacial entre road_segments y departments.
    """
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
    """
    Retorna el resumen de trafico de una ruta: flujo promedio, flujo pico y hora pico.
    Los datos provienen de la tabla traffic_hourly_agg con joins a count_points y road_segments.
    Si no hay datos de conteo, retorna valores en cero.
    """
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


def fetch_peak_hours(from_date: date | None, to_date: date | None) -> list[dict]:
    """
    Retorna la hora de mayor flujo promedio por ruta.
    Soporta filtro opcional por rango de fechas (from_date, to_date).
    Usa ROW_NUMBER para seleccionar solo la hora pico de cada ruta.
    """
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
