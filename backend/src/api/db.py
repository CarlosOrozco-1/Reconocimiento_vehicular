from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

import psycopg
from psycopg.rows import dict_row

from src.api.settings import settings


@contextmanager
def get_connection() -> Iterator[psycopg.Connection[Any]]:
    conn = psycopg.connect(settings.dsn, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()


def healthcheck_db() -> bool:
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 AS ok")
                _ = cur.fetchone()
        return True
    except Exception:
        return False
