from __future__ import annotations

import argparse
import json
from typing import Any

import requests

from src.api.db import get_connection

WFS_URL = "https://ideg.segeplan.gob.gt/geoserver/ows"


def fetch_wfs_geojson(type_name: str, count: int = 200000) -> dict[str, Any]:
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeName": type_name,
        "outputFormat": "application/json",
        "srsName": "EPSG:4326",
        "count": str(count),
    }
    response = requests.get(WFS_URL, params=params, timeout=120)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict) or data.get("type") != "FeatureCollection":
        raise ValueError(f"Invalid GeoJSON response for {type_name}")
    return data


def load_departments() -> int:
    data = fetch_wfs_geojson("agrip:03_Limites_departamentales", count=200)
    features = data.get("features", [])
    if not isinstance(features, list):
        return 0

    query = """
        INSERT INTO departments (code, name, geom)
        VALUES (
            %s,
            %s,
            ST_Multi(ST_Force2D(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)))
        )
        ON CONFLICT (code)
        DO UPDATE SET
            name = EXCLUDED.name,
            geom = EXCLUDED.geom
    """

    inserted = 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            for feature in features:
                if not isinstance(feature, dict):
                    continue
                geometry = feature.get("geometry")
                props = feature.get("properties") or {}
                if geometry is None or not isinstance(props, dict):
                    continue

                cod_dep = props.get("cod_dep")
                dept_name = str(props.get("departamen") or "").strip()
                if cod_dep is None or not dept_name:
                    continue

                try:
                    code = f"GT-{int(cod_dep):02d}"
                except (TypeError, ValueError):
                    continue

                cur.execute(query, (code, dept_name, json.dumps(geometry)))
                inserted += 1
        conn.commit()
    return inserted


def load_routes() -> int:
    data = fetch_wfs_geojson("infraestructura:carretera_centroamericana", count=200000)
    features = data.get("features", [])
    if not isinstance(features, list):
        return 0

    query = """
        INSERT INTO road_segments (route_code, name, department, geom)
        VALUES (
            %s,
            %s,
            NULL,
            ST_Multi(ST_LineMerge(ST_Force2D(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))))
        )
        ON CONFLICT (route_code, name)
        DO UPDATE SET
            geom = ST_Multi(
                ST_LineMerge(
                    ST_UnaryUnion(
                        ST_Collect(road_segments.geom, EXCLUDED.geom)
                    )
                )
            )
    """

    inserted = 0

    def normalize_route_code(raw_code: str, categoria: str) -> str:
        code = raw_code.strip().upper().replace(" ", "")
        cat = categoria.strip().upper()

        if not code:
            return ""

        if code.isdigit() and "CENTROAMERIC" in cat:
            return f"CA-{code}"

        if code.startswith("CA"):
            tail = code[2:].lstrip("-")
            if tail:
                return f"CA-{tail}"

        if code.startswith("RN"):
            tail = code[2:].lstrip("-")
            if tail:
                return f"RN-{tail}"

        return code

    with get_connection() as conn:
        with conn.cursor() as cur:
            for feature in features:
                if not isinstance(feature, dict):
                    continue
                geometry = feature.get("geometry")
                props = feature.get("properties") or {}
                if geometry is None or not isinstance(props, dict):
                    continue

                raw_route = str(props.get("no_ruta") or props.get("no_ruta_2") or "")
                categoria = str(props.get("categoria") or "")
                route_code = normalize_route_code(raw_route, categoria)
                if not route_code:
                    continue

                route_name = f"Ruta {route_code}"
                cur.execute(query, (route_code, route_name, json.dumps(geometry)))
                inserted += 1
        conn.commit()
    return inserted


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load SEGEPLAN WFS layers into PostGIS")
    parser.add_argument(
        "--mode",
        choices=["departments", "routes", "all"],
        default="all",
        help="Which layers to load",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    loaded_departments = 0
    loaded_routes = 0

    if args.mode in {"departments", "all"}:
        loaded_departments = load_departments()
    if args.mode in {"routes", "all"}:
        loaded_routes = load_routes()

    print(
        "SEGEPLAN load complete:",
        f"departments={loaded_departments}",
        f"routes={loaded_routes}",
    )


if __name__ == "__main__":
    main()
