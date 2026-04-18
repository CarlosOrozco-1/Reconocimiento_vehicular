CREATE TABLE IF NOT EXISTS vehicle_type_mix (
    id SERIAL PRIMARY KEY,
    vehicle_type VARCHAR(100) NOT NULL,
    vehicle_count NUMERIC NOT NULL,
    percentage NUMERIC NOT NULL,
    source_dataset VARCHAR(255),
    source_resource VARCHAR(255),
    source_url VARCHAR(1024),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_vehicle_type_mix_type ON vehicle_type_mix(vehicle_type);
