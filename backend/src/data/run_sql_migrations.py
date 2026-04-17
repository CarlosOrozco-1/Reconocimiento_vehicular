from __future__ import annotations

from pathlib import Path

from src.api.db import get_connection


def discover_sql_scripts(script_dir: Path) -> list[Path]:
    scripts: list[Path] = []
    for path in sorted(script_dir.glob("*.sql")):
        name = path.name
        if not name[:3].isdigit():
            continue
        number = int(name[:3])
        if number < 2:
            continue
        scripts.append(path)
    return scripts


def run_sql_migrations(script_dir: Path) -> list[str]:
    scripts = discover_sql_scripts(script_dir)
    applied: list[str] = []

    with get_connection() as conn:
        with conn.cursor() as cur:
            for script in scripts:
                sql = script.read_text(encoding="utf-8")
                if not sql.strip():
                    continue
                cur.execute(sql)
                applied.append(script.name)
        conn.commit()

    return applied
