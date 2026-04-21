from __future__ import annotations

import time
from typing import Any

import requests

from src.api.repository import (
    fetch_route_probe_points,
    fetch_saved_live_probe,
    upsert_saved_live_probe,
)
from src.api.settings import settings

_cache: dict[str, tuple[float, dict[str, Any]]] = {}


def _cached(route_code: str) -> dict[str, Any] | None:
    ttl = settings.tomtom_cache_ttl_sec
    if ttl <= 0:
        return None
    item = _cache.get(route_code)
    if item is None:
        return None
    expires_at, payload = item
    if time.time() > expires_at:
        _cache.pop(route_code, None)
        return None
    return payload


def _set_cache(route_code: str, payload: dict[str, Any]) -> None:
    ttl = settings.tomtom_cache_ttl_sec
    if ttl <= 0:
        return
    _cache[route_code] = (time.time() + ttl, payload)


def _call_tomtom(latitude: float, longitude: float) -> dict[str, Any]:
    endpoint = (
        f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/"
        f"{settings.tomtom_zoom}/json"
    )
    point = f"{latitude:.8f},{longitude:.8f}"
    response = requests.get(
        endpoint,
        params={"key": settings.tomtom_api_key, "point": point},
        timeout=settings.tomtom_timeout_sec,
    )

    if response.status_code == 400:
        data = response.json()
        message = str(data.get("error") or "")
        if "Point too far" in message:
            return {"ok": False, "retryable_point": True, "message": message}

    response.raise_for_status()
    body = response.json()
    flow = body.get("flowSegmentData") or {}
    return {
        "ok": True,
        "live_current_speed_kph": flow.get("currentSpeed"),
        "live_free_flow_speed_kph": flow.get("freeFlowSpeed"),
        "live_current_travel_time_sec": flow.get("currentTravelTime"),
        "live_free_flow_travel_time_sec": flow.get("freeFlowTravelTime"),
        "live_confidence": flow.get("confidence"),
        "live_road_closure": flow.get("roadClosure"),
        "live_source": "tomtom",
    }


def probe_tomtom_point(latitude: float, longitude: float) -> dict[str, Any]:
    """Public probe helper for calibration scripts."""
    return _call_tomtom(latitude=latitude, longitude=longitude)


def get_live_traffic_for_route(route_code: str, use_cache: bool = True) -> dict[str, Any]:
    if not settings.tomtom_enabled:
        return {"live_status": "disabled", "live_message": "TomTom disabled"}
    if not settings.tomtom_api_key:
        return {"live_status": "disabled", "live_message": "TomTom key missing"}

    if use_cache:
        cached = _cached(route_code)
        if cached is not None:
            return cached

    saved = fetch_saved_live_probe(route_code)
    if saved and saved.get("status") == "ok" and saved.get("latitude") is not None:
        try:
            result = _call_tomtom(float(saved["latitude"]), float(saved["longitude"]))
            if result.get("ok", False):
                payload = {
                    "live_status": "ok",
                    "live_message": "Live traffic from TomTom",
                    "live_probe_point": {
                        "latitude": float(saved["latitude"]),
                        "longitude": float(saved["longitude"]),
                    },
                }
                payload.update({k: v for k, v in result.items() if k != "ok"})
                _set_cache(route_code, payload)
                return payload
        except requests.RequestException:
            pass

    points = fetch_route_probe_points(route_code)[: max(1, settings.tomtom_probe_max_points)]
    if not points:
        payload = {
            "live_status": "unavailable",
            "live_message": "No geometry points for route",
        }
        upsert_saved_live_probe(
            route_code=route_code,
            status="unavailable",
            message=payload["live_message"],
            latitude=None,
            longitude=None,
        )
        _set_cache(route_code, payload)
        return payload

    last_error = "No valid traffic segment found"
    for point in points:
        latitude = float(point["latitude"])
        longitude = float(point["longitude"])
        try:
            result = _call_tomtom(latitude=latitude, longitude=longitude)
            if not result.get("ok", False):
                if result.get("retryable_point", False):
                    last_error = str(result.get("message", last_error))
                    continue
                payload = {
                    "live_status": "error",
                    "live_message": str(result.get("message", "TomTom request failed")),
                }
                _set_cache(route_code, payload)
                return payload

            payload = {
                "live_status": "ok",
                "live_message": "Live traffic from TomTom",
                "live_probe_point": {
                    "latitude": latitude,
                    "longitude": longitude,
                },
            }
            payload.update({k: v for k, v in result.items() if k != "ok"})
            upsert_saved_live_probe(
                route_code=route_code,
                status="ok",
                message="Live traffic point calibrated",
                latitude=latitude,
                longitude=longitude,
            )
            _set_cache(route_code, payload)
            return payload
        except requests.RequestException as exc:
            last_error = str(exc)
            continue

    payload = {
        "live_status": "unavailable",
        "live_message": last_error,
    }
    upsert_saved_live_probe(
        route_code=route_code,
        status="unavailable",
        message=last_error,
        latitude=None,
        longitude=None,
    )
    _set_cache(route_code, payload)
    return payload
