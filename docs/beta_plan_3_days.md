# Beta plan (3 days)

## Day 1 - MVP pipeline

- Run inference from test video.
- Add tracking IDs (ByteTrack).
- Count motorcycle and vehicles by line crossing.
- Save event-level records to `outputs/csv/events.csv`.

## Day 2 - Accuracy and analytics

- Reduce double counting with `track_id` guard.
- Calibrate `conf`, `iou`, `imgsz` and counting line.
- Build daily aggregation with pandas into `outputs/csv/daily_counts.csv`.
- Generate matplotlib daily chart.

## Day 3 - Web beta and validation

- Publish Streamlit dashboard for events and daily chart.
- Validate with multiple videos and log errors.
- Document known limits and next training tasks.
