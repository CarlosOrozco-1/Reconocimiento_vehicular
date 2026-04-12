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
  - `GET /departments`
  - `GET /routes/{route_code}/departments`
- Config de entorno en `backend/.env.example`.
- Conexion DB y repositorio SQL en `backend/src/api/db.py` y `backend/src/api/repository.py`.
- Datos mock para desarrollo sin DB en `backend/src/api/mock_data.py`.

### Base de datos

- Scripts SQL iniciales en `backend/scriptDB/001..005`.
- Script adicional: `backend/scriptDB/006_seed_departments.sql`.
- Puerto por defecto del proyecto cambiado a `55432` para evitar conflicto con `5432` y `5433`.
- Orquestacion local con Podman Compose en `backend/podman-compose.yml`.
- Scripts de ayuda:
  - `backend/scripts/db_up.sh`
  - `backend/scripts/db_down.sh`
- Ajuste SELinux en compose para montar scripts SQL: `:ro,z`.

### Documentacion

- `docs/fases_desarrollo.md` (plan oficial por fases).
- `docs/maplibre_como_funciona.md` (explicacion de MapLibre y flujo de carga).
- `docs/arquitectura_backend_fase1.md` (arquitectura y alcance de Fase 1).
- `docs/git_workflow.md` (flujo de ramas `desa`, `pre`, `pro`).
- Coleccion Postman inicial: `docs/postman/traffic_map_guatemala.postman_collection.json`.
- Flujo de mapa rutas/departamentos: `docs/rutas_departamentos_mapa.md`.

### Git

- Seguimiento iniciado con Git.
- Ramas creadas: `desa`, `pre`, `pro`.
- Rama activa de trabajo: `desa`.
