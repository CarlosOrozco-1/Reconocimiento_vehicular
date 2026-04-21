from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Configuracion central de la API. Todos los valores se leen de variables de entorno."""

    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    # Si es true, los endpoints retornan datos mock cuando la DB no responde.
    # En produccion debe ser false para detectar errores reales.
    api_allow_mock: bool = os.getenv("API_ALLOW_MOCK", "false").lower() == "true"

    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "traffic_gt")
    postgres_user: str = os.getenv("POSTGRES_USER", "traffic_user")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "traffic_pass")

    @property
    def dsn(self) -> str:
        """Cadena de conexion DSN para psycopg."""
        return (
            f"host={self.postgres_host} port={self.postgres_port} "
            f"dbname={self.postgres_db} user={self.postgres_user} "
            f"password={self.postgres_password}"
        )


settings = Settings()
