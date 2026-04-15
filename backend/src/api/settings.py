from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_allow_mock: bool = os.getenv("API_ALLOW_MOCK", "true").lower() == "true"

    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "55432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "traffic_gt")
    postgres_user: str = os.getenv("POSTGRES_USER", "traffic_user")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "traffic_pass")

    tomtom_enabled: bool = os.getenv("TOMTOM_ENABLED", "true").lower() == "true"
    tomtom_api_key: str = os.getenv("TOMTOM_API_KEY", "")
    tomtom_zoom: int = int(os.getenv("TOMTOM_ZOOM", "10"))
    tomtom_timeout_sec: int = int(os.getenv("TOMTOM_TIMEOUT_SEC", "12"))
    tomtom_cache_ttl_sec: int = int(os.getenv("TOMTOM_CACHE_TTL_SEC", "60"))
    tomtom_probe_max_points: int = int(os.getenv("TOMTOM_PROBE_MAX_POINTS", "120"))

    worker_interval_sec: int = int(os.getenv("WORKER_INTERVAL_SEC", "60"))
    worker_name: str = os.getenv("WORKER_NAME", "tomtom_worker")

    @property
    def dsn(self) -> str:
        return (
            f"host={self.postgres_host} port={self.postgres_port} "
            f"dbname={self.postgres_db} user={self.postgres_user} "
            f"password={self.postgres_password}"
        )


settings = Settings()
