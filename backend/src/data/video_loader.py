from __future__ import annotations

from pathlib import Path


def validate_video_path(source_video: Path) -> None:
    if not source_video.exists():
        raise FileNotFoundError(f"Video not found: {source_video}")
