CREATE INDEX IF NOT EXISTS idx_road_segments_geom ON road_segments USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_road_segments_route_code ON road_segments (route_code);

CREATE INDEX IF NOT EXISTS idx_departments_geom ON departments USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_departments_code ON departments (code);

CREATE INDEX IF NOT EXISTS idx_count_points_geom ON count_points USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_count_points_segment ON count_points (road_segment_id);

CREATE INDEX IF NOT EXISTS idx_traffic_counts_ts ON traffic_counts (timestamp);
CREATE INDEX IF NOT EXISTS idx_traffic_counts_point_ts ON traffic_counts (count_point_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_hourly_route_time ON traffic_hourly_agg (date, hour);
