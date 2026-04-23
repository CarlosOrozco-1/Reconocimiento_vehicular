from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2
import yaml
from ultralytics import YOLO

from src.analytics.daily_report import generate_daily_counts
from src.data.csv_logger import append_event, ensure_events_csv


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML structure in {path}")
    return data


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _count_direction(prev_y: float, curr_y: float, line_y: int) -> str | None:
    if prev_y < line_y <= curr_y:
        return "down"
    if prev_y > line_y >= curr_y:
        return "up"
    return None


def run_video_pipeline(
    source_video: Path,
    events_csv: Path,
    output_video: Path,
    max_frames: int | None = None,
) -> dict[str, int]:
    if not source_video.exists():
        raise FileNotFoundError(f"Input video not found: {source_video}")

    project_root = Path(__file__).resolve().parents[2]
    app_config = _load_yaml(project_root / "configs" / "app.yaml")
    infer_config = _load_yaml(project_root / "configs" / "yolo_infer.yaml")

    model_weights = str(infer_config.get("model", {}).get("weights", "yolo11n.pt"))
    conf = float(infer_config.get("inference", {}).get("conf", 0.35))
    iou = float(infer_config.get("inference", {}).get("iou", 0.45))
    classes = infer_config.get("inference", {}).get("classes", [2, 3, 5, 7])
    imgsz = int(infer_config.get("model", {}).get("imgsz", 960))
    device = str(infer_config.get("inference", {}).get("device", "cpu"))
    tracker = str(infer_config.get("tracking", {}).get("tracker", "bytetrack.yaml"))
    persist = bool(infer_config.get("tracking", {}).get("persist", True))

    allowed_classes = set(app_config.get("counting", {}).get("allowed_classes", []))
    vehicle_group = set(app_config.get("counting", {}).get("vehicle_group", []))
    line_cfg = app_config.get("counting", {}).get("line", {})

    capture = cv2.VideoCapture(str(source_video))
    if not capture.isOpened():
        raise RuntimeError(f"Could not open video: {source_video}")

    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 1280)
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 720)
    fps = float(capture.get(cv2.CAP_PROP_FPS) or 30.0)
    capture.release()

    x1 = int(line_cfg.get("x1", 0))
    y1 = int(line_cfg.get("y1", height // 2))
    x2 = int(line_cfg.get("x2", width))
    y2 = int(line_cfg.get("y2", height // 2))
    if x1 >= width or x2 <= 0 or y1 >= height or y2 >= height:
        x1, y1, x2, y2 = 0, height // 2, width, height // 2
    line_y = int((y1 + y2) / 2)

    model = YOLO(model_weights)

    output_video.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(output_video),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    if events_csv.exists():
        events_csv.unlink()
    ensure_events_csv(events_csv)

    prev_y_by_track: dict[int, float] = {}
    counted_track_ids: set[int] = set()
    motorcycles = 0
    vehicles = 0
    processed = 0

    results = model.track(
        source=str(source_video),
        stream=True,
        conf=conf,
        iou=iou,
        classes=classes,
        imgsz=imgsz,
        tracker=tracker,
        persist=persist,
        device=device,
        verbose=False,
    )

    for result in results:
        processed += 1
        annotated = result.plot()

        boxes = result.boxes
        if boxes is not None and boxes.id is not None and boxes.xyxy is not None:
            ids = boxes.id.int().cpu().tolist()
            xyxy = boxes.xyxy.cpu().tolist()
            cls_list = boxes.cls.int().cpu().tolist()
            conf_list = boxes.conf.cpu().tolist()

            for track_id, box, class_id, score in zip(ids, xyxy, cls_list, conf_list):
                class_name = str(result.names.get(class_id, str(class_id)))
                if allowed_classes and class_name not in allowed_classes:
                    continue

                center_y = float((box[1] + box[3]) / 2.0)
                previous_y = prev_y_by_track.get(track_id)
                prev_y_by_track[track_id] = center_y

                if previous_y is None or track_id in counted_track_ids:
                    continue

                direction = _count_direction(previous_y, center_y, line_y)
                if direction is None:
                    continue

                counted_track_ids.add(track_id)
                if class_name == "motorcycle":
                    motorcycles += 1
                elif class_name in vehicle_group:
                    vehicles += 1
                else:
                    continue

                append_event(
                    events_csv=events_csv,
                    timestamp=_utc_now_iso(),
                    track_id=track_id,
                    class_name=class_name,
                    direction=direction,
                    crossing_line_id="line_1",
                    confidence=float(score),
                )

        cv2.line(annotated, (x1, y1), (x2, y2), (0, 200, 255), 2)
        cv2.putText(
            annotated,
            f"Motorcycles: {motorcycles}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            annotated,
            f"Vehicles: {vehicles}",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 0),
            2,
            cv2.LINE_AA,
        )
        writer.write(annotated)

        if max_frames is not None and processed >= max_frames:
            break

    writer.release()

    daily_csv = Path(app_config.get("paths", {}).get("daily_csv", "outputs/csv/daily_counts.csv"))
    generate_daily_counts(events_csv=events_csv, daily_csv=daily_csv)

    return {
        "motorcycles": motorcycles,
        "vehicles": vehicles,
        "total": motorcycles + vehicles,
    }
