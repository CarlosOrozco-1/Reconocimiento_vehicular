from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests

CKAN_SEARCH_URL = "https://datos.ine.gob.gt/api/3/action/package_search"


def _get_with_retry(url: str, *, params: dict[str, str] | None = None, timeout: int = 30) -> requests.Response:
    last_exc: Exception | None = None
    for attempt in range(1, 4):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt < 3:
                time.sleep(2 * attempt)
                continue
            raise
    if last_exc:
        raise last_exc
    raise RuntimeError("Request failed")


def _find_dataset() -> dict[str, Any]:
    response = _get_with_retry(CKAN_SEARCH_URL, params={"q": "vehiculos transito"}, timeout=45)
    body = response.json()
    results = (body.get("result") or {}).get("results") or []

    for dataset in results:
        title = str(dataset.get("title", "")).lower()
        if "vehiculos" in title and "transito" in title:
            return dataset
    if results:
        return results[0]
    raise RuntimeError("No vehicle dataset found in INE CKAN search")


def _pick_latest_resource(dataset: dict[str, Any]) -> dict[str, Any]:
    resources = dataset.get("resources") or []
    xlsx_resources = [res for res in resources if str(res.get("format", "")).upper() == "XLSX"]
    if not xlsx_resources:
        raise RuntimeError("No XLSX resources available in dataset")

    def key(res: dict[str, Any]) -> str:
        return str(res.get("name") or "")

    xlsx_resources.sort(key=key, reverse=True)
    return xlsx_resources[0]


def _detect_vehicle_type_column(df: pd.DataFrame) -> str:
    candidates = [
        col
        for col in df.columns
        if any(token in str(col).lower() for token in ["tipo", "vehiculo", "clase", "categoria"])
    ]
    if not candidates:
        raise RuntimeError("Could not detect vehicle-type column in INE file")
    return candidates[0]


def build_vehicle_mix(output_csv: Path) -> Path:
    dataset = _find_dataset()
    resource = _pick_latest_resource(dataset)
    file_url = str(resource.get("url"))
    if not file_url:
        raise RuntimeError("Missing resource URL")

    df = pd.read_excel(file_url)
    vehicle_col = _detect_vehicle_type_column(df)

    series = df[vehicle_col].astype(str).str.strip()
    series = series[series != ""]

    counts = series.value_counts(dropna=True).reset_index()
    counts.columns = ["vehicle_type", "count"]
    total = int(counts["count"].sum())
    counts["percentage"] = (counts["count"] / total * 100).round(2)
    counts["source_dataset"] = str(dataset.get("title", ""))
    counts["source_resource"] = str(resource.get("name", ""))
    counts["source_url"] = file_url

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    counts.to_csv(output_csv, index=False)
    return output_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch INE vehicle mix and export percentages")
    parser.add_argument(
        "--output",
        default="outputs/csv/ine_vehicle_type_mix.csv",
        help="Output CSV path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = Path(args.output)
    result = build_vehicle_mix(output)
    print(f"Vehicle type mix exported: {result}")


if __name__ == "__main__":
    main()
