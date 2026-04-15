CREATE TABLE IF NOT EXISTS monitored_routes (
    route_code VARCHAR(40) PRIMARY KEY,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS worker_request_log (
    id BIGSERIAL PRIMARY KEY,
    worker_name VARCHAR(80) NOT NULL,
    route_code VARCHAR(40) NOT NULL,
    request_url TEXT,
    status_code INTEGER,
    duration_ms INTEGER,
    result VARCHAR(30) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS worker_status (
    worker_name VARCHAR(80) PRIMARY KEY,
    status VARCHAR(30) NOT NULL DEFAULT 'stopped',
    last_run_at TIMESTAMPTZ,
    last_success_at TIMESTAMPTZ,
    requests_ok INTEGER NOT NULL DEFAULT 0,
    requests_error INTEGER NOT NULL DEFAULT 0,
    message TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS route_live_history (
    id BIGSERIAL PRIMARY KEY,
    route_code VARCHAR(40) NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    current_speed_kph INTEGER,
    free_flow_speed_kph INTEGER,
    current_travel_time_sec INTEGER,
    free_flow_travel_time_sec INTEGER,
    confidence NUMERIC(6,2),
    road_closure BOOLEAN,
    afluencia_pct NUMERIC(6,2),
    source VARCHAR(40) NOT NULL DEFAULT 'tomtom'
);

INSERT INTO worker_status (worker_name, status, message)
VALUES ('tomtom_worker', 'stopped', 'Worker not started')
ON CONFLICT (worker_name) DO NOTHING;
