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

Detener base:

```bash
./scripts/db_down.sh
```
