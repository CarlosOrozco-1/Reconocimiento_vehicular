# Backend

Contiene la capa de backend del proyecto:

- API y servicios (FastAPI/servicios Python)
- Pipeline de deteccion y conteo
- Analytics y exportaciones
- Configuracion de modelo
- Scripts de base de datos en `scriptDB/`

## Estructura

- `src/`
- `configs/`
- `data/`
- `models/`
- `outputs/`
- `scriptDB/`
- `tests/`

## API Fase 1

Endpoints base:

- `GET /health`
- `GET /routes/main`
- `GET /peak-hours`

Ejecucion (dentro del entorno aislado):

```bash
distrobox enter vehicle-counter-dev
cd /home/ceorozcom/Documents/Proyecto-Reconocimiento-Vehicular/backend
source /home/ceorozcom/Documents/Proyecto-Reconocimiento-Vehicular/.venv/bin/activate
./scripts/run_api.sh
```

Nota importante: el backend no usa `npm`. Se levanta con Python/FastAPI (`uvicorn`).

Configuracion recomendada en `backend/.env`:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=55432
```

Configuracion TomTom (pruebas):

```env
TOMTOM_ENABLED=true
TOMTOM_API_KEY=<tu_key>
TOMTOM_ZOOM=10
TOMTOM_TIMEOUT_SEC=12
TOMTOM_CACHE_TTL_SEC=60
TOMTOM_PROBE_MAX_POINTS=120
```

Calibrar rutas para tiempo real:

```bash
./scripts/calibrate_tomtom.sh 50
```

Ver cobertura live calibrada:

```bash
curl "http://localhost:8000/routes/live-status?limit=200"
```

## Worker en tiempo real

Control desde API:

- `POST /monitor/worker/start`
- `POST /monitor/worker/stop`
- `GET /monitor/worker/status`
- `GET /monitor/worker/requests?minutes=60&limit=100`

Gestión de rutas monitoreadas:

- `GET /monitor/routes`
- `POST /monitor/routes/{route_code}`
- `DELETE /monitor/routes/{route_code}`

## Troubleshooting rapido

Si ejecutas `npm start` dentro de `backend/`, fallara porque no existe `package.json`.

- Backend se levanta con `./scripts/run_api.sh`
- Frontend se levanta desde `frontend/` con `npm run start`

Si el mapa solo muestra color base:

1. Verifica API: `curl http://localhost:8000/health`
2. Verifica rutas: `curl http://localhost:8000/routes/main`
3. Verifica departamentos: `curl http://localhost:8000/departments`

Checklist rapido automatizado:

```bash
./scripts/check_endpoints.sh
```

Si aparece `ERR_CONNECTION_REFUSED` en el frontend:

- el backend no esta levantado en `:8000`,
- inicia con `./scripts/run_api.sh` en una terminal separada,
- confirma con `curl http://localhost:8000/health`.

## Base de datos

Scripts SQL en `scriptDB/` para Postgres + PostGIS.

Si ya tenías la base creada, aplica nuevos scripts manualmente (ej. `011_worker_monitoring.sql`).

Si tienes conflicto de puertos con otras bases, usa un puerto alterno en `.env`:

```env
POSTGRES_PORT=55432
```

El backend lee este valor con `POSTGRES_PORT`.

Levantar base local con Podman Compose:

```bash
cd /home/ceorozcom/Documents/Proyecto-Reconocimiento-Vehicular/backend
cp .env.example .env
./scripts/db_up.sh
```

Nota: si ejecutas desde Distrobox, el script usa `distrobox-host-exec` para invocar Podman del host.

Conexion con DBeaver:

- Ver `docs/conexion_dbeaver.md`

Detener base:

```bash
./scripts/db_down.sh
```

## Ingestion de datos reales (multi-fuente)

Flujo recomendado:

1. Capturar de fuentes externas (CSV/API).
2. Guardar en tabla cruda `traffic_flow_raw`.
3. Procesar y consolidar en `traffic_hourly_agg`.
4. Exponer por API para dashboard/mapa.

Ejemplo de ingestion desde CSV:

```bash
cd /home/ceorozcom/Documents/Proyecto-Reconocimiento-Vehicular/backend
./scripts/run_ingestion_csv.sh fuente_demo ../docs/ejemplo_fuente_trafico.csv
```

Después puedes consultar:

- `GET /routes/{route_code}/summary`
- `GET /peak-hours`

### Carga geoespacial desde SEGEPLAN WFS

Este proyecto ya incluye carga automatizada de capas oficiales (WFS):

- Departamentos: `agrip:03_Limites_departamentales`
- Rutas centroamericanas: `infraestructura:carretera_centroamericana`

Ejecutar:

```bash
cd /home/ceorozcom/Documents/Proyecto-Reconocimiento-Vehicular/backend
./scripts/load_segeplan_data.sh all
```

Opciones:

- `./scripts/load_segeplan_data.sh departments`
- `./scripts/load_segeplan_data.sh routes`
