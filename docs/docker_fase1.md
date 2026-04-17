# Docker Fase 1 (db + backend + frontend)

Esta fase levanta la aplicacion base con Docker Compose.

## Archivos creados

- `docker-compose.yml`
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `frontend/nginx.conf`
- `.env.docker.example`

## 1) Preparar variables de entorno

```bash
cp .env.docker.example .env.docker
```

Edita `TOMTOM_API_KEY` en `.env.docker`.

## 2) Levantar servicios

```bash
docker compose --env-file .env.docker up -d --build
```

## 3) Verificar

- Backend: `http://localhost:8000/health`
- Frontend: `http://localhost:4200`

## 4) Datos de base

- En primer arranque, Postgres ejecuta scripts de `backend/scriptDB/`.
- La data queda en volumen `pg_data`.
- Si eliminas el volumen, la base se reinicializa desde scripts.

## 5) Apagar

```bash
docker compose --env-file .env.docker down
```

## Nota

En Fase 1 no se incluye Caddy. Caddy se integra en Fase 3.
