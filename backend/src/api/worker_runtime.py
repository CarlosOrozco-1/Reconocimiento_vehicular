from __future__ import annotations

import threading
import time

from src.api.repository import (
    fetch_monitored_routes,
    insert_route_live_history,
    insert_worker_request_log,
    mark_worker_request_result,
    set_worker_state,
    touch_worker_run,
)
from src.api.settings import settings
from src.api.tomtom import get_live_traffic_for_route


class TomTomWorkerController:
    def __init__(self) -> None:
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def is_running(self) -> bool:
        with self._lock:
            return self._thread is not None and self._thread.is_alive()

    def start(self) -> dict:
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return {"status": "already_running", "message": "Worker is already running"}

            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_loop, daemon=True, name=settings.worker_name)
            self._thread.start()

        set_worker_state(settings.worker_name, "running", "Worker started")
        return {"status": "started", "message": "Worker started"}

    def stop(self) -> dict:
        with self._lock:
            if self._thread is None or not self._thread.is_alive():
                set_worker_state(settings.worker_name, "stopped", "Worker was not running")
                return {"status": "already_stopped", "message": "Worker is not running"}

            self._stop_event.set()
            thread = self._thread

        thread.join(timeout=5)
        set_worker_state(settings.worker_name, "stopped", "Worker stopped by user")
        return {"status": "stopped", "message": "Worker stopped"}

    def _run_loop(self) -> None:
        set_worker_state(settings.worker_name, "running", "Worker loop active")

        while not self._stop_event.is_set():
            touch_worker_run(settings.worker_name)
            routes = fetch_monitored_routes(only_enabled=True)

            for item in routes:
                if self._stop_event.is_set():
                    break

                route_code = str(item.get("route_code", "")).strip()
                if not route_code:
                    continue

                started = time.perf_counter()
                status_code: int | None = None
                result = "error"
                error_message: str | None = None

                try:
                    live = get_live_traffic_for_route(route_code, use_cache=False)
                    live_status = str(live.get("live_status", "unknown"))
                    if live_status == "ok":
                        result = "ok"
                        mark_worker_request_result(settings.worker_name, ok=True)

                        current_speed = live.get("live_current_speed_kph")
                        free_speed = live.get("live_free_flow_speed_kph")
                        current_time = live.get("live_current_travel_time_sec")
                        free_time = live.get("live_free_flow_travel_time_sec")
                        confidence = live.get("live_confidence")
                        road_closure = live.get("live_road_closure")

                        afluencia_pct: float | None = None
                        if isinstance(current_speed, (int, float)) and isinstance(free_speed, (int, float)):
                            if float(free_speed) > 0:
                                afluencia_pct = round(100 - ((float(current_speed) / float(free_speed)) * 100), 2)

                        insert_route_live_history(
                            route_code=route_code,
                            current_speed_kph=int(current_speed) if isinstance(current_speed, (int, float)) else None,
                            free_flow_speed_kph=int(free_speed) if isinstance(free_speed, (int, float)) else None,
                            current_travel_time_sec=int(current_time)
                            if isinstance(current_time, (int, float))
                            else None,
                            free_flow_travel_time_sec=int(free_time)
                            if isinstance(free_time, (int, float))
                            else None,
                            confidence=float(confidence) if isinstance(confidence, (int, float)) else None,
                            road_closure=bool(road_closure) if road_closure is not None else None,
                            afluencia_pct=afluencia_pct,
                        )
                    else:
                        result = live_status
                        error_message = str(live.get("live_message", "No live data"))
                        mark_worker_request_result(settings.worker_name, ok=False)
                except Exception as exc:  # noqa: BLE001
                    result = "error"
                    error_message = str(exc)
                    mark_worker_request_result(settings.worker_name, ok=False)

                duration_ms = int((time.perf_counter() - started) * 1000)
                insert_worker_request_log(
                    worker_name=settings.worker_name,
                    route_code=route_code,
                    request_url="tomtom:flowSegmentData",
                    status_code=status_code,
                    duration_ms=duration_ms,
                    result=result,
                    error_message=error_message,
                )

            sleep_seconds = max(5, settings.worker_interval_sec)
            for _ in range(sleep_seconds):
                if self._stop_event.is_set():
                    break
                time.sleep(1)

        set_worker_state(settings.worker_name, "stopped", "Worker loop exited")


worker_controller = TomTomWorkerController()
