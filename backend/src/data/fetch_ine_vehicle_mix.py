from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests

def build_vehicle_mix(output_csv: Path) -> Path:
    local_txt = Path("data/external/INE_PARQUE_VEHICULAR_080426.txt")
    if not local_txt.exists():
        raise RuntimeError(f"No se encontro el archivo del parque vehicular proporcionado: {local_txt}")

    # El archivo txt esta delimitado por pipes '|'
    try:
        df = pd.read_csv(local_txt, sep="|", encoding="utf-8", on_bad_lines="skip")
    except Exception as e:
        df = pd.read_csv(local_txt, sep="|", encoding="latin-1", on_bad_lines="skip")
        
    vehicle_col = "TIPO_VEHICULO"
    qty_col = "CANTIDAD"

    if vehicle_col not in df.columns or qty_col not in df.columns:
        raise RuntimeError("El formato del TXT no coincide con TIPO_VEHICULO y CANTIDAD.")

    df[vehicle_col] = df[vehicle_col].astype(str).str.strip()
    df[qty_col] = pd.to_numeric(df[qty_col], errors="coerce").fillna(0)

    # Agrupar y sumar
    counts = df.groupby(vehicle_col)[qty_col].sum().reset_index()
    counts.columns = ["vehicle_type", "count"]
    
    # Filtrar vacios o 0
    counts = counts[(counts["count"] > 0) & (counts["vehicle_type"] != "") & (counts["vehicle_type"] != "nan")]

    total = float(counts["count"].sum())
    counts["percentage"] = (counts["count"] / total * 100).round(2)
    
    # Ordenar por mayor flujo
    counts = counts.sort_values(by="count", ascending=False)
    
    counts["source_dataset"] = "SAT Parque Vehicular Guatemala"
    counts["source_resource"] = local_txt.name
    counts["source_url"] = "LOCAL (Provisto por usuario)"

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
