from __future__ import annotations

from pathlib import Path


class Detector:
    def __init__(self, weights_path: str = "yolo11n.pt") -> None:
        self.weights_path = weights_path

    def warmup(self) -> None:
        _ = self.weights_path

    def detect(self, frame: object) -> list[dict]:
        _ = frame
        return []
