# Docker Fase 2 (persistencia + init + backup/restore)

Esta fase asegura que la base no quede en blanco y que puedas mover datos entre equipos/servidor.

## Sobre `.env.example`

Sí, `*.example` es solo plantilla.

- No debe contener secretos reales en producción.
- Se usa para crear tu archivo real (`.env` o `.env.docker`).
- En este proyecto, la key de TomTom en ejemplos quedó como `replace_me` para evitar confusión.

## 1) Crear archivo real de Docker env

```bash
cp .env.docker.example .env.docker
```

Edita `TOMTOM_API_KEY` en `.env.docker`.

## 2) Levantar servicios base

```bash
docker compose --env-file .env.docker up -d --build db backend frontend
```

## 3) Ejecutar job de inicialización (`db-init`)

```bash
docker compose --env-file .env.docker --profile init up db-init
```

Qué hace:

1. aplica scripts SQL `002..011`,
2. carga rutas/departamentos desde SEGEPLAN,
3. siembra rutas monitoreadas iniciales.

## 4) Persistencia

- La data vive en volumen `pg_data`.
- Si no eliminas el volumen, los datos persisten aunque recrees contenedores.
- Si borras volumen (`docker compose down -v`), la BD se reinicializa.

## 5) Backup de base

```bash
./scripts/docker/backup_db.sh
```

Genera un archivo `.dump` en `backups/`.

## 6) Restore de base

```bash
./scripts/docker/restore_db.sh backups/traffic_gt_YYYYMMDD_HHMMSS.dump
```

## 7) Verificación rápida

```bash
curl http://localhost:8000/health
curl "http://localhost:8000/routes/main?limit=5"
curl "http://localhost:8000/departments?limit=5"
```
