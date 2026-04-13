CREATE TABLE IF NOT EXISTS traffic_flow_raw (
    id BIGSERIAL PRIMARY KEY,
    source_name VARCHAR(80) NOT NULL,
    route_code VARCHAR(40) NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    interval_min INTEGER NOT NULL DEFAULT 60 CHECK (interval_min > 0),
    motorcycle_count INTEGER NOT NULL DEFAULT 0,
    light_vehicle_count INTEGER NOT NULL DEFAULT 0,
    heavy_vehicle_count INTEGER NOT NULL DEFAULT 0,
    total_count INTEGER NOT NULL DEFAULT 0,
    payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_traffic_flow_raw UNIQUE (source_name, route_code, observed_at)
);

CREATE TABLE IF NOT EXISTS ingestion_runs (
    id BIGSERIAL PRIMARY KEY,
    source_name VARCHAR(80) NOT NULL,
    status VARCHAR(20) NOT NULL,
    records_read INTEGER NOT NULL DEFAULT 0,
    records_loaded INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ
);
