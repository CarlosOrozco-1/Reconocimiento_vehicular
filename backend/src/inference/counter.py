from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Counts:
    motorcycles: int = 0
    vehicles: int = 0
    seen_track_ids: set[int] = field(default_factory=set)


class LineCounter:
    def __init__(self) -> None:
        self.counts = Counts()

    def update_from_tracks(self, tracks: list[dict]) -> Counts:
        for track in tracks:
            track_id = int(track.get("track_id", -1))
            class_name = str(track.get("class_name", ""))
            crossed = bool(track.get("crossed_line", False))
            if track_id < 0 or not crossed or track_id in self.counts.seen_track_ids:
                continue
            self.counts.seen_track_ids.add(track_id)
            if class_name == "motorcycle":
                self.counts.motorcycles += 1
            elif class_name in {"car", "bus", "truck"}:
                self.counts.vehicles += 1
        return self.counts
