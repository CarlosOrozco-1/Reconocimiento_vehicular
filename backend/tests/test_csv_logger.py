from pathlib import Path

from src.data.csv_logger import append_event, ensure_events_csv


def test_csv_logger_writes_file(tmp_path: Path) -> None:
    out = tmp_path / "events.csv"
    ensure_events_csv(out)
    append_event(out, "2026-01-01T00:00:00Z", 1, "motorcycle", "in", "line_1", 0.95)
    assert out.exists()
