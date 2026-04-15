from __future__ import annotations

from datetime import date

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
    add_monitored_route,
    ensure_monitored_routes_seed,
    fetch_departments_geojson,
    fetch_live_probe_status,
    fetch_monitored_routes,
    fetch_peak_hours,
    fetch_route_departments,
    fetch_route_live_history,
    fetch_route_summary,
    fetch_routes_geojson,
    fetch_worker_request_logs,
    fetch_worker_status,
    remove_monitored_route,
)
from src.api.settings import settings
from src.api.tomtom import get_live_traffic_for_route
from src.api.worker_runtime import worker_controller

app = FastAPI(title="Traffic Map Guatemala API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_seed_monitored_routes() -> None:
    try:
        ensure_monitored_routes_seed(limit=10)
    except Exception:
        return


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


@app.get("/departments")
def get_departments(limit: int = Query(default=500, ge=1, le=5000)) -> dict:
    try:
        geojson = fetch_departments_geojson(limit=limit)
        return {"source": "db", "data": geojson}
    except Exception:
        if not settings.api_allow_mock:
            raise
        return {"source": "mock", "data": mock_departments_geojson()}


@app.get("/routes/{route_code}/departments")
def get_route_departments(route_code: str) -> dict:
    try:
        rows = fetch_route_departments(route_code=route_code)
        return {"source": "db", "data": rows}
    except Exception:
        if not settings.api_allow_mock:
            raise
        return {"source": "mock", "data": mock_route_departments(route_code=route_code)}


@app.get("/routes/{route_code}/summary")
def get_route_summary(route_code: str, include_live: bool = Query(default=True)) -> dict:
    try:
        row = fetch_route_summary(route_code=route_code)
        if include_live:
            row.update(get_live_traffic_for_route(route_code=route_code))
        return {"source": "db", "data": row}
    except Exception:
        if not settings.api_allow_mock:
            raise
        row = mock_route_summary(route_code=route_code)
        if include_live:
            row.update(get_live_traffic_for_route(route_code=route_code))
        return {"source": "mock", "data": row}


@app.get("/routes/live-status")
def get_routes_live_status(limit: int = Query(default=500, ge=1, le=5000)) -> dict:
    try:
        rows = fetch_live_probe_status(limit=limit)
        return {"source": "db", "data": rows}
    except Exception:
        if not settings.api_allow_mock:
            raise
        return {"source": "mock", "data": []}


@app.get("/routes/{route_code}/live-history")
def get_route_live_history(
    route_code: str,
    hours: int = Query(default=24, ge=1, le=168),
    limit: int = Query(default=500, ge=1, le=5000),
) -> dict:
    try:
        rows = fetch_route_live_history(route_code=route_code, hours=hours, limit=limit)
        return {"source": "db", "data": rows}
    except Exception:
        if not settings.api_allow_mock:
            raise
        return {"source": "mock", "data": []}


@app.get("/monitor/worker/status")
def get_worker_status() -> dict:
    row = fetch_worker_status(settings.worker_name)
    row["runtime_running"] = worker_controller.is_running()
    return {"source": "db", "data": row}


@app.get("/monitor/worker/requests")
def get_worker_requests(
    minutes: int = Query(default=60, ge=1, le=1440),
    limit: int = Query(default=200, ge=1, le=1000),
) -> dict:
    rows = fetch_worker_request_logs(minutes=minutes, limit=limit)
    return {"source": "db", "data": rows}


@app.post("/monitor/worker/start")
def start_worker() -> dict:
    data = worker_controller.start()
    return {"source": "runtime", "data": data}


@app.post("/monitor/worker/stop")
def stop_worker() -> dict:
    data = worker_controller.stop()
    return {"source": "runtime", "data": data}


@app.get("/monitor/routes")
def get_monitored_routes(only_enabled: bool = Query(default=False)) -> dict:
    rows = fetch_monitored_routes(only_enabled=only_enabled)
    return {"source": "db", "data": rows}


@app.post("/monitor/routes/{route_code}")
def post_monitored_route(route_code: str) -> dict:
    add_monitored_route(route_code=route_code.upper())
    return {"source": "db", "data": {"route_code": route_code.upper(), "status": "enabled"}}


@app.delete("/monitor/routes/{route_code}")
def delete_monitored_route(route_code: str) -> dict:
    remove_monitored_route(route_code=route_code.upper())
    return {"source": "db", "data": {"route_code": route_code.upper(), "status": "removed"}}
