# scriptDB

Esta carpeta contiene los scripts SQL y utilitarios usados para crear, migrar y poblar la base de datos del proyecto.

Sugerencia de organizacion:

- `001_init.sql`
- `002_postgis_extensions.sql`
- `003_tables_traffic.sql`
- `004_indexes.sql`
- `005_seed_routes.sql`

Orden de ejecucion recomendado:

1. `002_postgis_extensions.sql`
2. `003_tables_traffic.sql`
3. `004_indexes.sql`
4. `005_seed_routes.sql`
