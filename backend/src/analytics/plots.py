from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_daily_counts(daily_csv: Path, output_image: Path) -> None:
    df = pd.read_csv(daily_csv)
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["date"], df["motorcycles"], label="motorcycles", marker="o")
    ax.plot(df["date"], df["vehicles"], label="vehicles", marker="o")
    ax.set_title("Daily vehicle counts")
    ax.set_xlabel("date")
    ax.set_ylabel("count")
    ax.legend()
    fig.autofmt_xdate(rotation=45)
    output_image.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_image, bbox_inches="tight")
    plt.close(fig)
