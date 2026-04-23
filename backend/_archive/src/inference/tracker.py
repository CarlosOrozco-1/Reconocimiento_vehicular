from __future__ import annotations


class Tracker:
    def __init__(self, tracker_config: str = "bytetrack.yaml") -> None:
        self.tracker_config = tracker_config

    def update(self, detections: list[dict]) -> list[dict]:
        _ = self.tracker_config
        return detections
