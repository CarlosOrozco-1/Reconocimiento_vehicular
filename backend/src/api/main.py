from __future__ import annotations

from datetime import date

import logging

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from src.api.db import healthcheck_db
from src.api.mock_data import (
    mock_departments_geojson,
    mock_peak_hours,
    mock_route_departments,
    mock_route_summary,
    mock_routes_geojson,
)
from src.api.repository import (
    fetch_departments_geojson,
    fetch_peak_hours,
    fetch_route_catalog,
    fetch_route_departments,
    fetch_route_summary,
    fetch_routes_geojson,
    fetch_vehicle_mix,
)
from src.api.settings import settings

# Aplicacion principal de la API de trafico Guatemala
app = FastAPI(title="Traffic Map Guatemala API", version="0.2.0")
logger = logging.getLogger(__name__)

# Configuracion CORS: permite peticiones desde el frontend Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    """Verifica el estado de la API y la conexion a la base de datos."""
    db_ok = healthcheck_db()
    return {
        "status": "ok",
        "db_connected": db_ok,
        "mock_enabled": settings.api_allow_mock,
    }


@app.get("/routes/main")
def get_main_routes(limit: int = Query(default=500, ge=1, le=5000)) -> dict:
    """
    Retorna el GeoJSON de las rutas principales de Guatemala.
    Cada feature es un MultiLineString que representa la geometria real de la ruta.
    Usa ST_Simplify para reducir puntos y mejorar el rendimiento del mapa.
    """
    try:
        geojson = fetch_routes_geojson(limit=limit)
        return {"source": "db", "data": geojson}
    except Exception:
        logger.warning("Falling back to mock routes for /routes/main", exc_info=True)
        if not settings.api_allow_mock:
            raise
        return {"source": "mock", "data": mock_routes_geojson()}


@app.get("/routes/catalog")
def get_route_catalog(limit: int = Query(default=500, ge=1, le=5000)) -> dict:
    """
    Retorna el catalogo de rutas: codigo, nombre, cantidad de segmentos y longitud en km.
    Se usa para poblar el selector de rutas en el frontend.
    """
    try:
        rows = fetch_route_catalog(limit=limit)
        return {"source": "db", "data": rows}
    except Exception:
        logger.warning("Falling back to mock route catalog for /routes/catalog", exc_info=True)
        if not settings.api_allow_mock:
            raise
        return {"source": "mock", "data": []}


@app.get("/peak-hours")
def get_peak_hours(
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
) -> dict:
    """Retorna la hora pico de mayor flujo por ruta, con filtro opcional por rango de fechas."""
    try:
        rows = fetch_peak_hours(from_date=from_date, to_date=to_date)
        return {"source": "db", "data": rows}
    except Exception:
        if not settings.api_allow_mock:
            raise
        return {"source": "mock", "data": mock_peak_hours()}


@app.get("/departments")
def get_departments(limit: int = Query(default=500, ge=1, le=5000)) -> dict:
    """
    Retorna el GeoJSON de los departamentos de Guatemala.
    Se usa como capa de fondo informativa en el mapa.
    """
    try:
        geojson = fetch_departments_geojson(limit=limit)
        return {"source": "db", "data": geojson}
    except Exception:
        if not settings.api_allow_mock:
            raise
        return {"source": "mock", "data": mock_departments_geojson()}


@app.get("/routes/{route_code}/departments")
def get_route_departments(route_code: str) -> dict:
    """Retorna los departamentos que atraviesa una ruta especifica usando interseccion espacial."""
    try:
        rows = fetch_route_departments(route_code=route_code)
        return {"source": "db", "data": rows}
    except Exception:
        if not settings.api_allow_mock:
            raise
        return {"source": "mock", "data": mock_route_departments(route_code=route_code)}


@app.get("/routes/{route_code}/summary")
def get_route_summary(route_code: str) -> dict:
    """
    Retorna el resumen de una ruta: flujo normal, flujo pico y hora pico.
    Los datos provienen de traffic_hourly_agg.
    """
    try:
        row = fetch_route_summary(route_code=route_code)
        return {"source": "db", "data": row}
    except Exception:
        if not settings.api_allow_mock:
            raise
        return {"source": "mock", "data": mock_route_summary(route_code=route_code)}


@app.get("/sandbox/tomtom-flow")
def sandbox_tomtom_flow(lat: float, lon: float) -> dict:
    """
    Endpoint de Sandbox: Consulta la API de TomTom Traffic Flow para una coordenada.
    Retorna los datos en crudo para validacion en el frontend.
    """
    from src.api.tomtom_client import get_flow_segment_data
    return get_flow_segment_data(lat, lon)


@app.get("/peak-hours")
def get_peak_hours(
    from_date: date | None = Query(None), to_date: date | None = Query(None)
):
    """Hora pico por ruta basada en promedios historicos."""
    try:
        data = fetch_peak_hours(from_date, to_date)
        return {"source": "db", "data": data}
    except Exception:
        if not settings.api_allow_mock:
            raise
        return {"source": "mock", "data": mock_peak_hours()}


@app.get("/vehicle-mix")
def get_vehicle_mix():
    """Estadisticas reales del parque vehicular de Guatemala (SAT/INE)."""
    try:
        data = fetch_vehicle_mix()
        return {"source": "db", "data": data}
    except Exception:
        if not settings.api_allow_mock:
            raise
        return {
            "source": "mock",
            "data": [
                {"vehicle_type": "MOTO", "vehicle_count": 2500000, "percentage": 45.0},
                {"vehicle_type": "AUTOMOVIL", "vehicle_count": 2000000, "percentage": 36.0},
                {"vehicle_type": "PICK UP", "vehicle_count": 1000000, "percentage": 18.0},
            ],
        }
