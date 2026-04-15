from __future__ import annotations

import argparse
import csv
from pathlib import Path

import requests

from src.api.repository import (
    fetch_route_codes,
    fetch_route_probe_points_expanded,
    upsert_saved_live_probe,
)
from src.api.tomtom import probe_tomtom_point


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Expanded scan to find TomTom-valid points by route")
    parser.add_argument("--limit", type=int, default=200, help="Max routes to scan")
    parser.add_argument("--only-route", default="", help="Optional single route code")
    parser.add_argument("--max-segments", type=int, default=120, help="Max segments per route")
    parser.add_argument("--points-per-segment", type=int, default=12, help="Interpolated points per segment")
    parser.add_argument(
        "--max-probes-per-route",
        type=int,
        default=400,
        help="Safety cap of point probes per route",
    )
    parser.add_argument(
        "--output",
        default="outputs/csv/tomtom_route_scan.csv",
        help="CSV report output path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.only_route:
        route_codes = [args.only_route.strip().upper()]
    else:
        route_codes = fetch_route_codes(limit=args.limit)

    report_rows: list[dict[str, object]] = []
    ok_count = 0
    unavailable_count = 0

    for route_code in route_codes:
        candidates = fetch_route_probe_points_expanded(
            route_code=route_code,
            max_segments=args.max_segments,
            points_per_segment=args.points_per_segment,
        )

        attempts = 0
        found = False
        last_error = "No valid segment found"

        for point in candidates:
            attempts += 1
            if attempts > args.max_probes_per_route:
                break

            latitude = float(point["latitude"])
            longitude = float(point["longitude"])
            try:
                result = probe_tomtom_point(latitude=latitude, longitude=longitude)
                if not result.get("ok", False):
                    if result.get("retryable_point", False):
                        last_error = str(result.get("message", last_error))
                        continue
                    last_error = str(result.get("message", "TomTom error"))
                    continue

                upsert_saved_live_probe(
                    route_code=route_code,
                    status="ok",
                    message="Expanded scan matched a valid TomTom segment",
                    latitude=latitude,
                    longitude=longitude,
                )

                report_rows.append(
                    {
                        "route_code": route_code,
                        "status": "ok",
                        "attempts": attempts,
                        "latitude": latitude,
                        "longitude": longitude,
                        "message": "valid segment found",
                    }
                )
                print(f"{route_code}: ok after {attempts} probes ({latitude:.6f}, {longitude:.6f})")
                ok_count += 1
                found = True
                break
            except requests.RequestException as exc:
                last_error = str(exc)
                continue

        if not found:
            upsert_saved_live_probe(
                route_code=route_code,
                status="unavailable",
                message=last_error,
                latitude=None,
                longitude=None,
            )
            report_rows.append(
                {
                    "route_code": route_code,
                    "status": "unavailable",
                    "attempts": attempts,
                    "latitude": "",
                    "longitude": "",
                    "message": last_error,
                }
            )
            print(f"{route_code}: unavailable after {attempts} probes ({last_error})")
            unavailable_count += 1

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["route_code", "status", "attempts", "latitude", "longitude", "message"],
        )
        writer.writeheader()
        writer.writerows(report_rows)

    print(
        f"Expanded scan complete. ok={ok_count} unavailable={unavailable_count} report={output_path}"
    )


if __name__ == "__main__":
    main()
