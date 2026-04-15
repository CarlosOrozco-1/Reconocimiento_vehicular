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
  - `GET /routes/{route_code}/summary`

### Ingestion de datos

- Pipeline multi-fuente inicial implementado (`src/ingestion/`).
- Adaptadores iniciales: CSV y HTTP JSON.
- Persistencia en crudo `traffic_flow_raw` y consolidacion a `traffic_hourly_agg`.
- Scripts SQL agregados: `007_ingestion_tables.sql`, `008_ingestion_indexes.sql`.
- Script de ejecucion: `backend/scripts/run_ingestion_csv.sh`.

### Carga de capas oficiales (SEGEPLAN)

- Script nuevo: `backend/scripts/load_segeplan_data.sh`.
- Carga departamentos desde `agrip:03_Limites_departamentales`.
- Carga rutas desde `infraestructura:carretera_centroamericana`.
- Normalizacion de codigos de ruta aplicada (formato `CA-xx`).

### Integracion de trafico en tiempo real

- Endpoint `GET /routes/{route_code}/summary` ahora soporta `include_live=true`.
- Integracion TomTom con fallback de puntos sobre la ruta y cache por ruta.
- Variables de entorno TomTom agregadas en `backend/.env.example`.
- Documento tecnico: `docs/tomtom_integracion.md`.
- Endpoint `GET /routes/live-status` agregado para monitorear cobertura live por ruta.
- Tabla `route_live_probe_points` para guardar puntos calibrados con exito.
- Script de calibracion: `backend/scripts/calibrate_tomtom.sh`.
- Script de escaneo expandido: `backend/scripts/scan_tomtom_coverage.sh`.

### Worker en tiempo real y observabilidad

- Endpoints de control: start/stop/status/requests.
- Endpoints de gestión de rutas monitoreadas (listar/agregar/eliminar).
- Dashboard Angular con botones para iniciar/detener worker y tabla de solicitudes en vivo.
- Endpoint `GET /routes/{route_code}/live-history` para curva temporal en dashboard.
- Dashboard ahora grafica afluencia por ruta con datos de `route_live_history`.
- Tablas de soporte: `monitored_routes`, `worker_request_log`, `worker_status`, `route_live_history`.
- Documento operativo: `docs/worker_monitoreo_operacion.md`.

### Fuentes externas de vehiculos

- Fuente CKAN INE validada para vehiculos involucrados por tipo.
- Script inicial para mezcla porcentual por tipo: `backend/scripts/fetch_ine_vehicle_mix.sh`.
- Documento de fuentes: `docs/fuentes_externas_vehiculos.md`.
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
- Decision de stack (Leaflet + OSMnx/GeoPandas): `docs/decision_stack_mapa.md`.
- Guia de datos espaciales y fuentes: `docs/datos_espaciales_y_fuentes.md`.
- Matriz de fuentes y endpoints candidatos: `docs/matriz_fuentes_trafico.md`.

### Frontend mapa

- Migracion de componente de mapa a Leaflet completada.
- Hover por ruta con popup de flujo normal, flujo hora pico y departamentos.

### Git

- Seguimiento iniciado con Git.
- Ramas creadas: `desa`, `pre`, `pro`.
- Rama activa de trabajo: `desa`.
