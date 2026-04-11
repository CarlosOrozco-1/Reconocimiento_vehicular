# Arquitectura backend - Fase 1

## Objetivo de la fase

Levantar la base geoespacial del sistema:

- API en FastAPI
- Esquema inicial PostgreSQL + PostGIS
- Endpoints base para mapa y horas pico

## Componentes

1. API

- `backend/src/api/main.py`
- Endpoints:
  - `GET /health`
  - `GET /routes/main`
  - `GET /peak-hours`

2. Configuracion

- `backend/src/api/settings.py`
- Variables en `backend/.env.example`

3. Acceso a base de datos

- `backend/src/api/db.py`
- Conexion psycopg a PostgreSQL

4. Capa de consulta

- `backend/src/api/repository.py`
- Consultas SQL para GeoJSON de rutas y horas pico

5. Datos fallback

- `backend/src/api/mock_data.py`
- Permite responder con datos mock si la base aun no esta disponible (`API_ALLOW_MOCK=true`)

6. Orquestacion local DB

- `backend/podman-compose.yml`
- Puerto host por defecto del proyecto: `55432` (evita conflicto con `5432`/`5433`)

## Modelo de datos inicial

Scripts en `backend/scriptDB/`:

- `001_init.sql`
- `002_postgis_extensions.sql`
- `003_tables_traffic.sql`
- `004_indexes.sql`
- `005_seed_routes.sql`

Tablas iniciales:

- `road_segments`
- `count_points`
- `traffic_counts`
- `traffic_hourly_agg`

## Como ejecutar API en entorno aislado

```bash
distrobox enter vehicle-counter-dev
cd /home/ceorozcom/Documents/Proyecto-Reconocimiento-Vehicular/backend
source /home/ceorozcom/Documents/Proyecto-Reconocimiento-Vehicular/.venv/bin/activate
pip install -r requirements.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Validacion rapida

- `GET http://localhost:8000/health`
- `GET http://localhost:8000/routes/main`
- `GET http://localhost:8000/peak-hours`

## Estado Fase 1

- API base: implementada
- Scripts SQL iniciales: implementados
- Documento de arquitectura: implementado
