from __future__ import annotations

from pathlib import Path

import pandas as pd


def generate_daily_counts(events_csv: Path, daily_csv: Path) -> None:
    if not events_csv.exists():
        raise FileNotFoundError(f"events CSV not found: {events_csv}")

    df = pd.read_csv(events_csv)
    if df.empty:
        out = pd.DataFrame(columns=["date", "motorcycles", "vehicles", "total"])
        out.to_csv(daily_csv, index=False)
        return

    filtered = df[df["class_name"].isin(["motorcycle", "car", "bus", "truck"])].copy()
    filtered["timestamp"] = pd.to_datetime(filtered["timestamp"], errors="coerce")
    filtered["date"] = filtered["timestamp"].dt.date.astype(str)

    motorcycles = (
        filtered[filtered["class_name"] == "motorcycle"]
        .groupby("date")
        .size()
        .rename("motorcycles")
    )
    vehicles = (
        filtered[filtered["class_name"].isin(["car", "bus", "truck"])]
        .groupby("date")
        .size()
        .rename("vehicles")
    )

    daily = pd.concat([motorcycles, vehicles], axis=1).fillna(0).astype(int).reset_index()
    daily["total"] = daily["motorcycles"] + daily["vehicles"]
    daily_csv.parent.mkdir(parents=True, exist_ok=True)
    daily.to_csv(daily_csv, index=False)
