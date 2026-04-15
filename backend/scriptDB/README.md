# scriptDB

Esta carpeta contiene los scripts SQL y utilitarios usados para crear, migrar y poblar la base de datos del proyecto.

Sugerencia de organizacion:

- `001_init.sql`
- `002_postgis_extensions.sql`
- `003_tables_traffic.sql`
- `004_indexes.sql`
- `005_seed_routes.sql`
- `006_seed_departments.sql`
- `007_ingestion_tables.sql`
- `008_ingestion_indexes.sql`
- `009_alter_road_segments_geom.sql`
- `010_tomtom_probe_cache.sql`
- `011_worker_monitoring.sql`

Orden de ejecucion recomendado:

1. `002_postgis_extensions.sql`
2. `003_tables_traffic.sql`
3. `004_indexes.sql`
4. `005_seed_routes.sql`
5. `006_seed_departments.sql`
6. `007_ingestion_tables.sql`
7. `008_ingestion_indexes.sql`
8. `009_alter_road_segments_geom.sql`
9. `010_tomtom_probe_cache.sql`
10. `011_worker_monitoring.sql`

Si la base ya fue creada antes de agregar nuevos scripts, ejecútalos manualmente con psql o DBeaver.
