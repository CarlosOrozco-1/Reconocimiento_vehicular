from pathlib import Path

import pytest

from src.inference.pipeline import run_video_pipeline


def test_pipeline_raises_when_video_missing(tmp_path: Path) -> None:
    missing_video = tmp_path / "missing.mp4"
    output_csv = tmp_path / "events.csv"
    with pytest.raises(FileNotFoundError):
        run_video_pipeline(missing_video, output_csv)
