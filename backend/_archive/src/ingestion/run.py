from __future__ import annotations

import argparse
from pathlib import Path

from src.ingestion.adapters.csv_source import CsvSourceAdapter
from src.ingestion.adapters.http_json_source import HttpJsonSourceAdapter
from src.ingestion.pipeline import run_ingestion


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run traffic data ingestion")
    parser.add_argument("--source-name", required=True, help="Source name identifier")
    parser.add_argument(
        "--mode",
        required=True,
        choices=["csv", "http"],
        help="Input mode",
    )
    parser.add_argument("--csv-path", default="", help="CSV path when mode=csv")
    parser.add_argument("--http-endpoint", default="", help="HTTP endpoint when mode=http")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.mode == "csv":
        if not args.csv_path:
            raise ValueError("--csv-path is required when mode=csv")
        adapter = CsvSourceAdapter(source_name=args.source_name, file_path=Path(args.csv_path))
    else:
        if not args.http_endpoint:
            raise ValueError("--http-endpoint is required when mode=http")
        adapter = HttpJsonSourceAdapter(source_name=args.source_name, endpoint=args.http_endpoint)

    result = run_ingestion(adapter)
    print(
        "Ingestion completed:",
        f"source={result.source_name}",
        f"records_read={result.records_read}",
        f"raw_loaded={result.raw_loaded}",
        f"hourly_upserts={result.hourly_upserts}",
    )


if __name__ == "__main__":
    main()
