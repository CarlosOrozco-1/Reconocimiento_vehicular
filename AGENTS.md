# AGENTS

Reglas de desarrollo para el proyecto Vehicle Counter YOLO.

## Reglas generales

1. Mantener el alcance del MVP: detectar, trackear, contar y exportar CSV.
2. No hardcodear rutas ni umbrales; usar `configs/*.yaml`.
3. Guardar salidas solo en `outputs/`.
4. No mezclar logica de inferencia con capa de dashboard.
5. Validar con videos de prueba antes de cambios de entrenamiento.

## Reglas basicas de Python

1. Usar Python 3.10+ (3.11 recomendado).
2. Usar type hints en funciones nuevas.
3. Mantener funciones pequenas y con una responsabilidad clara.
4. Seguir `snake_case` para funciones y variables.
5. Manejar errores con mensajes claros y logs minimos.
6. Escribir codigo modular dentro de `src/`.
7. Agregar pruebas basicas para logica critica (conteo y CSV).

## Tecnologias oficiales

- Python
- Ultralytics YOLO
- OpenCV
- NumPy
- Pandas
- Matplotlib
- Streamlit
- Distrobox + Podman (Fedora)

## Regla de documentacion

Toda documentacion del proyecto debe crearse dentro de `docs/`.

## Regla para endpoints y pruebas API

Cada vez que se agregue, modifique o elimine un endpoint del backend, se debe actualizar la coleccion de Postman en `docs/postman/traffic_map_guatemala.postman_collection.json`.

## Entorno de trabajo (Distrobox)

1. Crear entorno Ubuntu 22.04:

```bash
distrobox create --name vehicle-counter-dev --image docker.io/library/ubuntu:22.04
```

2. Entrar al entorno:

```bash
distrobox enter vehicle-counter-dev
```

3. Instalar dependencias base:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv ffmpeg libgl1 libglib2.0-0
```

4. Crear entorno virtual Python dentro del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

5. Ejecutar app base:

```bash
python -m src.main --source data/raw/videos/test.mp4 --output outputs/csv/events.csv
```
