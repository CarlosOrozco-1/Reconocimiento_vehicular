CREATE TABLE IF NOT EXISTS route_live_probe_points (
    route_code VARCHAR(40) PRIMARY KEY,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    status VARCHAR(20) NOT NULL DEFAULT 'unknown',
    message TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    successful_at TIMESTAMPTZ
);
