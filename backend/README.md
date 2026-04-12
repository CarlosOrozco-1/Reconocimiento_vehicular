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

## Troubleshooting rapido

Si ejecutas `npm start` dentro de `backend/`, fallara porque no existe `package.json`.

- Backend se levanta con `./scripts/run_api.sh`
- Frontend se levanta desde `frontend/` con `npm run start`

Si el mapa solo muestra color base:

1. Verifica API: `curl http://localhost:8000/health`
2. Verifica rutas: `curl http://localhost:8000/routes/main`
3. Verifica departamentos: `curl http://localhost:8000/departments`

## Base de datos

Scripts SQL en `scriptDB/` para Postgres + PostGIS.

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
