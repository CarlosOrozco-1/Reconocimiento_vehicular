INSERT INTO road_segments (route_code, name, department, geom)
VALUES
(
    'CA-1',
    'CA-1 Occidente',
    'Guatemala',
    ST_GeomFromText('LINESTRING(-90.733 14.620, -91.480 14.780)', 4326)
),
(
    'CA-9',
    'CA-9 Sur',
    'Guatemala',
    ST_GeomFromText('LINESTRING(-90.506 14.634, -90.330 14.280)', 4326)
)
ON CONFLICT DO NOTHING;
