from __future__ import annotations

import argparse
from pathlib import Path

from src.inference.pipeline import run_video_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Vehicle counter pipeline")
    parser.add_argument("--source", required=True, help="Path to input video")
    parser.add_argument("--output", required=True, help="Path to events CSV output")
    parser.add_argument(
        "--video-output",
        default="outputs/videos/annotated.mp4",
        help="Path to annotated video output",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Optional max frames for quick testing",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = Path(args.source)
    events_output = Path(args.output)
    video_output = Path(args.video_output)
    counts = run_video_pipeline(
        source_video=source,
        events_csv=events_output,
        output_video=video_output,
        max_frames=args.max_frames,
    )
    print(
        f"Done. motorcycles={counts['motorcycles']} vehicles={counts['vehicles']} total={counts['total']}"
    )
    print(f"Events CSV: {events_output}")
    print(f"Annotated video: {video_output}")


if __name__ == "__main__":
    main()
