# Bootstrap desde cero (nuevo equipo)

Este flujo te permite levantar el proyecto con un solo comando (`bootstrap.sh`) y evitar ejecutar todos los pasos manuales.

## 1) Preparación recomendada (Fedora + Distrobox)

En host Fedora:

```bash
distrobox create --name vehicle-counter-dev --image docker.io/library/ubuntu:22.04
distrobox enter vehicle-counter-dev
```

Dentro de Distrobox:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl
```

## 2) Clonar proyecto

```bash
git clone <URL_DEL_REPO> Proyecto-Reconocimiento-Vehicular
cd Proyecto-Reconocimiento-Vehicular
git checkout desa
```

## 3) Ejecutar bootstrap

```bash
./bootstrap.sh
```

Qué hace automáticamente:

1. crea/repara `.venv` e instala dependencias backend,
2. crea `backend/.env` desde `backend/.env.example` si no existe,
3. levanta PostGIS (`backend/scripts/db_up.sh`),
4. aplica scripts SQL (`002` a `011`),
5. carga capas SEGEPLAN (departamentos/rutas),
6. instala dependencias frontend (`npm install`) si hay npm.

## 4) Variables opcionales de bootstrap

Puedes controlar comportamiento sin editar el script:

- `INSTALL_FRONTEND=false` -> no ejecuta `npm install`.
- `RUN_DB_SETUP=false` -> no levanta DB ni aplica SQL.
- `RUN_SEGEPLAN_LOAD=false` -> no carga capas WFS.
- `RUN_TOMTOM_SCAN=true` -> ejecuta escaneo expandido TomTom al final.
- `DB_CONTAINER=<nombre>` -> cambia nombre del contenedor DB (default `traffic_gt_db`).

Ejemplo:

```bash
RUN_TOMTOM_SCAN=true INSTALL_FRONTEND=false ./bootstrap.sh
```

## 5) Levantar servicios después del bootstrap

Backend:

```bash
cd backend
./scripts/run_api.sh
```

Frontend (otra terminal):

```bash
cd frontend
npm run start
```

## 6) Verificación rápida

```bash
cd backend
./scripts/check_endpoints.sh http://127.0.0.1:8000
```

## Nota importante

El script asume acceso a `podman` para la base de datos.
Si estás en un entorno donde `podman` no está disponible, usa `RUN_DB_SETUP=false` y configura la DB por separado.
