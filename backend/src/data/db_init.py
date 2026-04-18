from __future__ import annotations

import argparse
from pathlib import Path

from src.api.repository import ensure_monitored_routes_seed
from src.data.load_segeplan import load_departments, load_routes
from src.data.load_vehicle_mix import load_vehicle_mix_to_db
from src.data.run_sql_migrations import run_sql_migrations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize database schema and baseline data")
    parser.add_argument(
        "--load-segeplan",
        action="store_true",
        help="Load SEGEPLAN routes, departments, and vehicle mix after migrations",
    )
    parser.add_argument(
        "--seed-monitored-routes",
        type=int,
        default=10,
        help="Seed first N routes in monitored_routes",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[2]
    script_dir = root / "scriptDB"

    applied = run_sql_migrations(script_dir)
    print(f"Applied SQL scripts: {', '.join(applied)}")

    if args.load_segeplan:
        dep_count = load_departments()
        route_count = load_routes()
        veh_mix_count = load_vehicle_mix_to_db()
        print(f"SEGEPLAN loaded: departments={dep_count} routes={route_count} vehicle_mix={veh_mix_count}")

    seeded = ensure_monitored_routes_seed(limit=args.seed_monitored_routes)
    print(f"Monitored routes seeded: attempted={seeded}")


if __name__ == "__main__":
    main()
