from __future__ import annotations

import argparse

from src.api.repository import fetch_route_codes
from src.api.tomtom import get_live_traffic_for_route


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Calibrate TomTom probe points by route")
    parser.add_argument("--limit", type=int, default=200, help="Max routes to calibrate")
    parser.add_argument(
        "--only-route",
        default="",
        help="Optional single route code",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.only_route:
        route_codes = [args.only_route]
    else:
        route_codes = fetch_route_codes(limit=args.limit)

    ok = 0
    unavailable = 0
    for route_code in route_codes:
        payload = get_live_traffic_for_route(route_code)
        status = str(payload.get("live_status", "unknown"))
        message = str(payload.get("live_message", ""))
        if status == "ok":
            ok += 1
        else:
            unavailable += 1
        print(f"{route_code}: {status} - {message}")

    print(f"Calibration complete. ok={ok} unavailable={unavailable}")


if __name__ == "__main__":
    main()
