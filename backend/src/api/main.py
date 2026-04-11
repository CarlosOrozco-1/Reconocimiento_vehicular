from __future__ import annotations

from datetime import date

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from src.api.db import healthcheck_db
from src.api.mock_data import mock_peak_hours, mock_routes_geojson
from src.api.repository import fetch_peak_hours, fetch_routes_geojson
from src.api.settings import settings

app = FastAPI(title="Traffic Map Guatemala API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    db_ok = healthcheck_db()
    return {
        "status": "ok",
        "db_connected": db_ok,
        "mock_enabled": settings.api_allow_mock,
    }


@app.get("/routes/main")
def get_main_routes(limit: int = Query(default=500, ge=1, le=5000)) -> dict:
    try:
        geojson = fetch_routes_geojson(limit=limit)
        return {"source": "db", "data": geojson}
    except Exception:
        if not settings.api_allow_mock:
            raise
        return {"source": "mock", "data": mock_routes_geojson()}


@app.get("/peak-hours")
def get_peak_hours(
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
) -> dict:
    try:
        rows = fetch_peak_hours(from_date=from_date, to_date=to_date)
        return {"source": "db", "data": rows}
    except Exception:
        if not settings.api_allow_mock:
            raise
        return {"source": "mock", "data": mock_peak_hours()}
