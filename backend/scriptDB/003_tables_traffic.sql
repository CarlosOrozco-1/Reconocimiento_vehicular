CREATE TABLE IF NOT EXISTS road_segments (
    id BIGSERIAL PRIMARY KEY,
    route_code VARCHAR(40) NOT NULL,
    name VARCHAR(200) NOT NULL,
    department VARCHAR(100),
    geom geometry(LINESTRING, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_road_segments_route_name UNIQUE (route_code, name)
);

CREATE TABLE IF NOT EXISTS departments (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    geom geometry(MULTIPOLYGON, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS count_points (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    road_segment_id BIGINT NOT NULL REFERENCES road_segments(id) ON DELETE CASCADE,
    direction VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    geom geometry(POINT, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS traffic_counts (
    id BIGSERIAL PRIMARY KEY,
    count_point_id BIGINT NOT NULL REFERENCES count_points(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    interval_min INTEGER NOT NULL CHECK (interval_min > 0),
    motorcycle_count INTEGER NOT NULL DEFAULT 0,
    light_vehicle_count INTEGER NOT NULL DEFAULT 0,
    heavy_vehicle_count INTEGER NOT NULL DEFAULT 0,
    total_count INTEGER GENERATED ALWAYS AS (
        motorcycle_count + light_vehicle_count + heavy_vehicle_count
    ) STORED,
    source VARCHAR(30) NOT NULL DEFAULT 'vision',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS traffic_hourly_agg (
    count_point_id BIGINT NOT NULL REFERENCES count_points(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    hour SMALLINT NOT NULL CHECK (hour BETWEEN 0 AND 23),
    motorcycle_count INTEGER NOT NULL DEFAULT 0,
    light_vehicle_count INTEGER NOT NULL DEFAULT 0,
    heavy_vehicle_count INTEGER NOT NULL DEFAULT 0,
    total_count INTEGER NOT NULL DEFAULT 0,
    avg_speed NUMERIC(6,2),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (count_point_id, date, hour)
);
