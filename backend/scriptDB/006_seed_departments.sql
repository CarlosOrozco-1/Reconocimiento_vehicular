INSERT INTO departments (code, name, geom)
VALUES
(
    'GT-01',
    'Guatemala',
    ST_Multi(ST_GeomFromText('POLYGON((-90.75 14.45, -90.30 14.45, -90.30 14.85, -90.75 14.85, -90.75 14.45))', 4326))
),
(
    'GT-03',
    'Sacatepequez',
    ST_Multi(ST_GeomFromText('POLYGON((-90.88 14.40, -90.58 14.40, -90.58 14.67, -90.88 14.67, -90.88 14.40))', 4326))
),
(
    'GT-05',
    'Escuintla',
    ST_Multi(ST_GeomFromText('POLYGON((-90.65 13.90, -90.15 13.90, -90.15 14.45, -90.65 14.45, -90.65 13.90))', 4326))
)
ON CONFLICT (code) DO NOTHING;
