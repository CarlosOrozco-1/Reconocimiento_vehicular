from __future__ import annotations

import argparse
from pathlib import Path

# Importar solo las funciones de carga de datos necesarias.
# La funcion ensure_monitored_routes_seed fue eliminada junto con el modulo worker.
from src.data.load_segeplan import load_departments, load_routes
from src.data.load_vehicle_mix import load_vehicle_mix_to_db
from src.data.run_sql_migrations import run_sql_migrations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize database schema and baseline data")
    parser.add_argument(
        "--load-segeplan",
        action="store_true",
        help="Load SEGEPLAN routes and departments after running SQL migrations",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    # Ruta al directorio scriptDB relativa a este archivo
    root = Path(__file__).resolve().parents[2]
    script_dir = root / "scriptDB"

    # Ejecutar migraciones SQL en orden (001_init.sql, 002_..., etc.)
    applied = run_sql_migrations(script_dir)
    print(f"Applied SQL scripts: {', '.join(applied) if applied else 'none (all already applied)'}")

    if args.load_segeplan:
        # Carga de datos cartograficos desde la API de SEGEPLAN/IDE Guatemala
        dep_count = load_departments()
        route_count = load_routes()
        # La carga del mix vehicular requiere un archivo externo del INE.
        # Si no esta disponible, se omite sin interrumpir el proceso.
        try:
            veh_mix_count = load_vehicle_mix_to_db()
            print(f"SEGEPLAN loaded: departments={dep_count} routes={route_count} vehicle_mix={veh_mix_count}")
        except Exception as exc:
            print(f"SEGEPLAN loaded: departments={dep_count} routes={route_count} vehicle_mix=skipped ({exc})")
    else:
        print("Skipping SEGEPLAN data load (use --load-segeplan to include geographic data)")



if __name__ == "__main__":
    main()
