from src.inference.counter import LineCounter


def test_counter_counts_motorcycle_and_vehicle_once() -> None:
    counter = LineCounter()
    tracks = [
        {"track_id": 1, "class_name": "motorcycle", "crossed_line": True},
        {"track_id": 2, "class_name": "car", "crossed_line": True},
        {"track_id": 2, "class_name": "car", "crossed_line": True},
    ]
    counts = counter.update_from_tracks(tracks)
    assert counts.motorcycles == 1
    assert counts.vehicles == 1
