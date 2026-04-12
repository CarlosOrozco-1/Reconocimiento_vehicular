# Conexion a PostgreSQL (DBeaver)

Guia rapida para conectarte a la base del proyecto desde DBeaver.

## Requisitos

- Base levantada con:

```bash
distrobox enter vehicle-counter-dev
cd /home/ceorozcom/Documents/Proyecto-Reconocimiento-Vehicular/backend
./scripts/db_up.sh
```

- Archivo `backend/.env` creado desde `backend/.env.example`.

## Parametros de conexion (DBeaver)

Usa una nueva conexion tipo `PostgreSQL` con estos valores:

- Host: `localhost`
- Port: `55432`
- Database: `traffic_gt`
- Username: `traffic_user`
- Password: `traffic_pass`

Para el backend, usa en `backend/.env`:

- `POSTGRES_HOST=localhost`

## Paso a paso en DBeaver

1. `Database` -> `New Database Connection`.
2. Selecciona `PostgreSQL`.
3. Ingresa los parametros anteriores.
4. Clic en `Test Connection`.
5. Si todo esta correcto, `Finish`.

## Verificacion rapida

Ejecuta en el SQL Editor:

```sql
SELECT NOW();
SELECT route_code, name FROM road_segments ORDER BY id;
```

Deberias ver al menos:

- `CA-1 | CA-1 Occidente`
- `CA-9 | CA-9 Sur`

## Notas

- Si cambiaste credenciales o puerto en `backend/.env`, usa esos valores en DBeaver.
- Si falla la conexion, valida que el contenedor este arriba:

```bash
podman ps --filter name=traffic_gt_db
```
