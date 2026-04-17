# Plan de Containerizacion con Docker

Objetivo: ejecutar la plataforma completa en Linux/Windows de forma consistente, con despliegue simple y ruta a produccion.

## Aclaracion de termino

El termino mas usado es **containerizar** (tambien se entiende "encapsular").

## Problema clave de datos (tu observacion es correcta)

Al construir imagenes Docker **no** se conserva automaticamente la data viva de PostgreSQL.

- La imagen lleva codigo/configuracion.
- La data vive en un **volumen**.
- Si recreas contenedores sin volumen persistente o sin restore, la BD queda vacia.

Por eso la estrategia debe incluir:

1. volumen persistente para `postgres`,
2. scripts de migracion,
3. carga inicial de geodatos (SEGEPLAN/OSM) automatizada,
4. backup/restore versionado.

---

## Arquitectura objetivo (Docker)

Servicios:

1. `db` -> Postgres + PostGIS
2. `backend` -> FastAPI + worker TomTom
3. `frontend` -> Angular build servido estatico
4. `caddy` -> reverse proxy TLS/certificados
5. (opcional) `db-init` -> job one-shot para migraciones + carga geo inicial

Red interna Docker:

- todos en la misma red privada (`app-net`)
- solo `caddy` expone 80/443 al host

Persistencia:

- volumen `pg_data` para base de datos
- volumen opcional para backups `pg_backups`

---

## Fases de implementacion

## Fase 1 - Base Docker local

Objetivo:

- Levantar `db`, `backend`, `frontend` con `docker compose`.

Entregables:

- `docker-compose.yml`
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `.env.docker.example`

Validacion:

- `docker compose up -d`
- `GET /health` responde ok
- frontend visible por puerto local

## Fase 2 - Persistencia y datos iniciales

Objetivo:

- evitar BD vacia en reinstalaciones.

Entregables:

- volumen persistente `pg_data`
- job `db-init` para:
  - aplicar SQL `002..011`,
  - cargar capas SEGEPLAN,
  - seed de rutas monitoreadas
- script `make restore` (o shell) para restaurar dump

Validacion:

- bajar/subir contenedores sin perder datos
- restaurar dump en entorno limpio

## Fase 3 - Caddy y TLS

Objetivo:

- exponer aplicacion con HTTPS y proxy limpio.

Entregables:

- `deploy/Caddyfile.local`
- `deploy/Caddyfile.prod`
- rutas:
  - `app.tudominio.com` -> frontend
  - `api.tudominio.com` -> backend

Validacion:

- certificado emitido automaticamente
- rutas HTTPS funcionales

## Fase 4 - Worker operacional

Objetivo:

- correr worker TomTom de manera controlada en Docker.

Entregables:

- modo worker en `backend` (comando alterno o mismo contenedor)
- healthcheck del worker
- logs persistentes

Validacion:

- start/stop via API operativo
- tablas `worker_status`, `worker_request_log`, `route_live_history` actualizan

## Fase 5 - Backup y recuperacion

Objetivo:

- garantizar continuidad al mover entorno (Linux/Windows/servidor).

Entregables:

- script `backup_db.sh` (`pg_dump`)
- script `restore_db.sh`
- politica de backup (diario, retencion)

Validacion:

- restauracion completa en maquina nueva
- app funcional tras restore

## Fase 6 - Preparacion produccion

Objetivo:

- hardening para servidor real.

Entregables:

- variables sensibles fuera de repo
- CORS restringido
- usuarios/roles DB
- monitoreo basico (CPU/RAM/errores)

Validacion:

- checklist pre-produccion aprobada

---

## Estrategia de datos recomendada (resumen)

Para tu preocupacion principal (datos geo no se trasladan):

1. En desarrollo: usa volumen persistente + carga automatica inicial.
2. Para mover entorno: exporta dump (`pg_dump`) e importa (`psql`/`pg_restore`).
3. Para servidor: primer despliegue con `db-init`; siguientes despliegues solo migran, no reinicializan.

Asi no dependes de "reconstruir" la BD desde cero cada vez.

---

## Orden recomendado para empezar ya

1. Fase 1
2. Fase 2
3. Fase 3

Con esas 3 fases ya tendras una beta desplegable y portable entre equipos.
