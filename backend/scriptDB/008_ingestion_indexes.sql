CREATE INDEX IF NOT EXISTS idx_traffic_flow_raw_route_time
    ON traffic_flow_raw (route_code, observed_at);

CREATE INDEX IF NOT EXISTS idx_traffic_flow_raw_source_time
    ON traffic_flow_raw (source_name, observed_at);

CREATE INDEX IF NOT EXISTS idx_ingestion_runs_source
    ON ingestion_runs (source_name, started_at);
