# Cambios recientes

Registro rapido de cambios para no perder contexto.

## 2026-04-11

### Estructura y arquitectura

- Proyecto separado por capas: `backend/`, `frontend/`, `docs/`.
- Se agrego carpeta `backend/scriptDB/` para scripts de base de datos.

### Frontend

- Scaffold Angular base funcional.
- Mapa inicial con MapLibre en `frontend/src/app/pages/map/map-page.component.ts`.
- Servicio API en `frontend/src/app/services/api/traffic-api.service.ts`.

### Backend Fase 1

- API FastAPI base en `backend/src/api/main.py`.
- Endpoints implementados:
  - `GET /health`
  - `GET /routes/main`
  - `GET /peak-hours`
- Config de entorno en `backend/.env.example`.
- Conexion DB y repositorio SQL en `backend/src/api/db.py` y `backend/src/api/repository.py`.
- Datos mock para desarrollo sin DB en `backend/src/api/mock_data.py`.

### Base de datos

- Scripts SQL iniciales en `backend/scriptDB/001..005`.
- Puerto por defecto del proyecto cambiado a `55432` para evitar conflicto con `5432` y `5433`.
- Orquestacion local con Podman Compose en `backend/podman-compose.yml`.
- Scripts de ayuda:
  - `backend/scripts/db_up.sh`
  - `backend/scripts/db_down.sh`

### Documentacion

- `docs/fases_desarrollo.md` (plan oficial por fases).
- `docs/maplibre_como_funciona.md` (explicacion de MapLibre y flujo de carga).
- `docs/arquitectura_backend_fase1.md` (arquitectura y alcance de Fase 1).
